#!/usr/bin/env bash
# One-shot resume prep for Paper2 SMALL lane:
# - backfill paper2_leg_finished.json for archived terminal legs (DONE / TERMINAL_FAIL)
# - stash INCOMPLETE_CRASH dirs so they are never counted as completed
# Does NOT start agents.
set -euo pipefail
A="${AGENT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
SLUG="${1:-qwen35-9b}"
H="$A/external/MyPCBench-main/results"
OUT="$A/results/paper2_exec/$SLUG"
STAMP="$(date +%Y%m%dT%H%M%S)"
CKPT="$OUT/CHECKPOINT.jsonl"
PROGRESS="$OUT/PROGRESS.md"
mkdir -p "$OUT"

python3 - "$A" "$SLUG" "$STAMP" "$CKPT" "$PROGRESS" <<'PY'
import json, re, shutil, sys
from datetime import datetime, timezone
from pathlib import Path

root = Path(sys.argv[1])
slug = sys.argv[2]
stamp = sys.argv[3]
ckpt = Path(sys.argv[4])
progress = Path(sys.argv[5])
H = root / "external/MyPCBench-main/results"
OUT = root / "results/paper2_exec" / slug
au = json.loads((root / "out/paper2_analysis_universe.json").read_text())
co = json.loads((root / "out/paper2_cell_order.json").read_text())
order = co["order"]
multi = set(au["multi_i_both_pass"])
legs = []
for task in order:
    legs.append((task, "G0"))
    legs.append((task, "G1"))
    if task in multi:
        legs.append((task, "G2"))

def traj_info(d: Path):
    traj = next(d.rglob("traj.jsonl"), None) if d.exists() else None
    if not traj or not traj.exists():
        return 0, False, None
    t = traj.read_text(errors="ignore")
    steps = t.count('"step_num"')
    done = bool(re.search(r'"action": "DONE"|"done": true', t))
    return steps, done, traj

def write_finished(dirs, payload):
    text = json.dumps(payload, indent=2) + "\n"
    for d in dirs:
        if d is None:
            continue
        d.mkdir(parents=True, exist_ok=True)
        (d / "paper2_leg_finished.json").write_text(text)

records = []
stashed = []
for i, (task, leg) in enumerate(legs, 1):
    h = H / f"paper2-{slug}-{task}" / leg
    a = OUT / task / leg
    steps_h, done_h, _ = traj_info(h)
    steps_a, done_a, _ = traj_info(a)
    steps = max(steps_h, steps_a)
    done = done_h or done_a
    # Complete archive = archived traj with steps. guest.json-only is NOT terminal.
    archived_complete = steps_a > 0
    has_start = (h / "run_started.txt").exists() or (a / "run_started.txt").exists()

    if (h / "paper2_leg_finished.json").exists() or (a / "paper2_leg_finished.json").exists():
        # already marked
        src = h if (h / "paper2_leg_finished.json").exists() else a
        payload = json.loads((src / "paper2_leg_finished.json").read_text())
        records.append(payload)
        print(f"KEEP {i:02d} {task} {leg} {payload.get('status')}")
        continue

    if done:
        status = "DONE"
        payload = {
            "leg_index": i,
            "legs_total": 57,
            "task": task,
            "leg": leg,
            "status": status,
            "steps": steps,
            "has_done_action": True,
            "model": "qwen/qwen3.5-9b",
            "lane": "SMALL",
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "note": "backfilled_on_resume",
            "result_dir": str(h),
            "archive_dir": str(a),
        }
        write_finished([h if h.exists() else None, a if a.exists() else None], payload)
        records.append(payload)
        print(f"BACKFILL_DONE {i:02d} {task} {leg} steps={steps}")
        continue

    # Terminal fail: full archived traj, agent returned, no DONE — do NOT re-run
    if archived_complete and h.exists() and steps_h > 0:
        status = "TERMINAL_FAIL"
        payload = {
            "leg_index": i,
            "legs_total": 57,
            "task": task,
            "leg": leg,
            "status": status,
            "steps": steps,
            "has_done_action": False,
            "model": "qwen/qwen3.5-9b",
            "lane": "SMALL",
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "note": "backfilled_on_resume_terminal_fail",
            "result_dir": str(h),
            "archive_dir": str(a),
        }
        write_finished([h, a], payload)
        records.append(payload)
        print(f"BACKFILL_FAIL {i:02d} {task} {leg} steps={steps}")
        continue

    # Incomplete crash / boot-only / partial archive (e.g. guest.json only)
    if has_start or steps > 0 or (a.exists() and any(a.iterdir())) or (h.exists() and any(h.iterdir())):
        for d, label in ((h, "H"), (a, "A")):
            if not d.exists():
                continue
            bak = Path(str(d) + f"-incomplete-{stamp}")
            print(f"STASH_{label} {d} -> {bak}")
            shutil.move(str(d), str(bak))
            (bak / "paper2_incomplete_marker.json").write_text(
                json.dumps(
                    {
                        "status": "INCOMPLETE_STASHED",
                        "task": task,
                        "leg": leg,
                        "steps_at_stash": steps,
                        "at": datetime.now(timezone.utc).isoformat(),
                        "reason": "resume_prep_crash_or_partial",
                    },
                    indent=2,
                )
                + "\n"
            )
            stashed.append(str(bak))
        print(f"RESUME_POINT {i:02d} {task} {leg} (will re-run clean)")
        break

    # not started — resume point is first missing
    print(f"RESUME_POINT {i:02d} {task} {leg} NOT_STARTED")
    break

# rewrite checkpoint from backfilled records (idempotent snapshot)
# preserve prior ckpt lines then append unique
prior = []
if ckpt.exists():
    for line in ckpt.read_text().splitlines():
        if line.strip():
            prior.append(json.loads(line))
latest = {(o["task"], o["leg"]): o for o in prior}
for o in records:
    latest[(o["task"], o["leg"])] = o
with ckpt.open("w") as f:
    for o in sorted(latest.values(), key=lambda x: x.get("leg_index", 0)):
        f.write(json.dumps(o) + "\n")

done_n = sum(1 for o in latest.values() if o.get("status") == "DONE")
term_n = sum(1 for o in latest.values() if o.get("status") == "TERMINAL_FAIL")
progress.write_text(
    "\n".join(
        [
            f"# Paper2 progress — qwen/qwen3.5-9b (SMALL)",
            "",
            f"- updated: {datetime.now(timezone.utc).isoformat()}",
            f"- checkpointed legs: {len(latest)}/57",
            f"- DONE (real): {done_n}",
            f"- TERMINAL_FAIL: {term_n}",
            f"- stashed incomplete: {len(stashed)}",
            "",
            "Incomplete dirs: `*-incomplete-*` — NOT completed.",
            "",
        ]
    )
    + "\n"
)
print(f"CKPT_WRITTEN {ckpt} n={len(latest)} DONE={done_n} TERMINAL_FAIL={term_n} stashed={len(stashed)}")
PY
