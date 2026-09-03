#!/usr/bin/env python3
"""Paper 2 §7 inject-probe gate for READY_RELATIVE Tier 1 units.

No agent. No judge. No rewrite of D / sealed registry. One boot, snapshot
`/data` (+ Tax_2025), restore before every unit so patches never chain.

PASS / REJECT mapping follows PAPER2_SPEC.md §7 and the frozen expect
fields already evaluated by cf_inject.py.
"""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("AGENT_ROOT", Path(__file__).resolve().parents[1]))
HARNESS = ROOT / "external/MyPCBench-main/agent-harness"
OUT = ROOT / "out"
SPEC_PATH = ROOT / "cf" / "paper2_interventions.json"

# PAPER2_INVENTORY_TIER=1 (default) or 2 — selects READY_RELATIVE rows + output paths.
INVENTORY_TIER = int(os.environ.get("PAPER2_INVENTORY_TIER", "1"))
RESULTS = ROOT / "results" / (
    "paper2_tier1_probe" if INVENTORY_TIER == 1 else f"paper2_tier{INVENTORY_TIER}_probe"
)
SNAP = f"/tmp/paper2_tier{INVENTORY_TIER}_snap"
REPORT_STEM = f"paper2_tier{INVENTORY_TIER}_probe_gate"
# Expected counts (abort if file disagrees). Tier 1: 18+5; Tier 2: 5+1.
EXPECTED = {
    1: (18, 5),
    2: (5, 1),
}


def load_ready_groups() -> tuple[list[str], list[str]]:
    doc = json.loads(SPEC_PATH.read_text())
    ready = []
    for e in doc.get("interventions") or []:
        if e.get("_sql_status") != "READY_RELATIVE" or not e.get("id"):
            continue
        tier = e.get("_inventory_tier")
        if INVENTORY_TIER == 1:
            # Tier 1 rows predate the _inventory_tier field.
            if tier not in (None, 1):
                continue
        else:
            if tier != INVENTORY_TIER:
                continue
        ready.append(e["id"])
    group1 = sorted(i for i in ready if not str(i).endswith("-I2"))
    group2 = sorted(i for i in ready if str(i).endswith("-I2"))
    return group1, group2


def guest_sh(env, command: str) -> dict:
    return env._execute_shell(command)


def guest_text(env, command: str) -> str:
    result = guest_sh(env, command)
    out = (result.get("output") or "") + (result.get("error") or "")
    return out.strip()


def snapshot(env) -> None:
    script = f"""
set -e
rm -rf {SNAP}
mkdir -p {SNAP}
cp -a /data {SNAP}/data
if [ -d /home/user/Documents/Tax_2025 ]; then
  cp -a /home/user/Documents/Tax_2025 {SNAP}/Tax_2025
fi
ls -ld {SNAP}/data {SNAP}/Tax_2025 2>/dev/null || true
"""
    print(guest_text(env, script), flush=True)


def restore(env) -> None:
    # /data is a mount: wipe contents (retry on busy dirs), then copy snapshot back.
    # Prefer rsync --delete when available; fall back to rm -rf + cp -a.
    script = f"""
set -e
if [ ! -d {SNAP}/data ]; then
  echo "SNAPSHOT_MISSING:{SNAP}/data" >&2
  exit 1
fi
restore_once() {{
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete {SNAP}/data/ /data/
  else
    # Busy guest apps can leave dirs non-empty under find+rm; force wipe.
    for _try in 1 2 3; do
      find /data -mindepth 1 -maxdepth 1 -exec rm -rf {{}} + 2>/dev/null || true
      # leftover mount/busy paths
      rm -rf /data/* /data/.[!.]* /data/..?* 2>/dev/null || true
      if [ -z "$(ls -A /data 2>/dev/null)" ]; then
        break
      fi
      sleep 1
    done
    cp -a {SNAP}/data/. /data/
  fi
  if [ -d {SNAP}/Tax_2025 ]; then
    rm -rf /home/user/Documents/Tax_2025
    mkdir -p /home/user/Documents
    cp -a {SNAP}/Tax_2025 /home/user/Documents/Tax_2025
  fi
  test -f /data/dinoco-airlines.sqlite
  sqlite3 /data/dinoco-airlines.sqlite "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='loyalty';"
}}
out=$(restore_once)
echo "$out"
"""
    out = guest_text(env, script)
    if out:
        print(out[:2000], flush=True)
    last = out.strip().splitlines()[-1] if out.strip() else ""
    if last != "1":
        raise RuntimeError(f"restore did not bring back loyalty table: {out!r}")


def boot_env():
    sys.path.insert(0, str(HARNESS))
    from env import MyPCBenchEnv

    qcow2 = os.environ.get("MYPCBENCH_QCOW2")
    if not qcow2:
        raise SystemExit("MYPCBENCH_QCOW2 is not set")
    env = MyPCBenchEnv(
        backend="qemu",
        qcow2_path=qcow2,
        headless=True,
        persona="michael_scott",
        container_name=f"mypcbench-paper2-{os.getpid()}",
    )
    print(f"reset() starting; qcow2={qcow2}", flush=True)
    env.reset()
    print(f"guest ready at {env.base_url}", flush=True)
    return env


def inject(env, task_id: str, dest: Path) -> subprocess.CompletedProcess:
    dest.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/cf_inject.py"),
            "--api",
            env.base_url,
            "--task",
            task_id,
            "--out",
            str(dest),
        ],
        capture_output=True,
        text=True,
    )


def _probe_blob_has_infra_error(blobs) -> bool:
    """True if any probe string looks like guest sqlite / control infra failure."""
    text = json.dumps(blobs)
    needles = (
        "ERROR:",
        "database is locked",
        "Connection refused",
        "Connection reset",
        "Timeout",
        "Control API",
    )
    return any(n.lower() in text.lower() for n in needles)


def classify(row_base: dict, rec: dict | None) -> dict:
    """Map cf_inject record → PASS / REJECT_* / technical_failure."""
    out = dict(row_base)
    if rec is None:
        out["verdict"] = "technical_failure"
        out["verdict_detail"] = out.get("fails") or "missing_guest_json"
        return out

    fails = list(rec.get("fails") or [])
    moved = bool(rec.get("gold_moved"))
    out["ok"] = bool(rec.get("ok"))
    out["gold_moved"] = moved
    out["fails"] = "; ".join(fails)
    out["probe_before"] = str(rec.get("probe_before") or "")
    out["probe_after"] = str(rec.get("probe_after") or "")
    out["extra_probes_before"] = rec.get("extra_probes_before") or []
    out["extra_probes_after"] = rec.get("extra_probes_after") or []

    # Infra noise (locked DB, control errors) is technical_failure, not REJECT.
    probe_blobs = [
        out["probe_before"],
        out["probe_after"],
        out["extra_probes_before"],
        out["extra_probes_after"],
    ]
    if _probe_blob_has_infra_error(probe_blobs):
        out["verdict"] = "technical_failure"
        out["verdict_detail"] = "guest_sqlite_or_control_error"
        return out

    if not fails and moved:
        out["verdict"] = "PASS"
        out["verdict_detail"] = ""
        return out

    # Prefer held-leak when the determining probe did move.
    held_leak = any("extra probes moved but must not" in f for f in fails)
    no_move = any(
        f in (
            "the gold did not move inside the guest",
        )
        or "did not move" in f
        for f in fails
    )
    if held_leak and moved:
        out["verdict"] = "REJECT_held_leak"
        out["verdict_detail"] = "; ".join(fails)
        return out
    if no_move or (not moved and fails):
        out["verdict"] = "REJECT_identifiability"
        out["verdict_detail"] = "; ".join(fails) or "probe unchanged"
        return out
    if fails:
        # Unexpected expect failure shape — treat as technical, do not invent D edits.
        out["verdict"] = "technical_failure"
        out["verdict_detail"] = "; ".join(fails)
        return out
    # ok with no move and no fails shouldn't happen under probe_changes=True
    out["verdict"] = "REJECT_identifiability"
    out["verdict_detail"] = "probe unchanged"
    return out


def summarize_record(task_id: str, group: str, dest: Path, proc: subprocess.CompletedProcess) -> dict:
    path = dest / f"{task_id}.guest.json"
    base = {
        "task_id": task_id,
        "group": group,
        "ok": False,
        "gold_moved": None,
        "fails": "",
        "returncode": proc.returncode,
        "guest_json": str(path) if path.exists() else "",
        "probe_before": "",
        "probe_after": "",
        "extra_probes_before": [],
        "extra_probes_after": [],
        "error": "",
        "verdict": "technical_failure",
        "verdict_detail": "",
    }
    if proc.returncode != 0 and not path.exists():
        base["error"] = (proc.stderr or proc.stdout or "")[-1500:]
        base["fails"] = "inject_process_failed"
        base["verdict_detail"] = "inject_process_failed"
        return base
    if not path.exists():
        base["error"] = "no guest.json"
        base["fails"] = "missing_guest_json"
        base["verdict_detail"] = "missing_guest_json"
        return base
    rec = json.loads(path.read_text())
    row = classify(base, rec)
    if not row["ok"] and not row["fails"] and row["verdict"] == "technical_failure":
        row["error"] = (proc.stderr or proc.stdout or "")[-1500:]
    return row


def write_report(rows: list[dict], group1: list[str], group2: list[str]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)

    json_path = OUT / f"{REPORT_STEM}.json"
    json_path.write_text(
        json.dumps(
            {
                "written_at": datetime.now(timezone.utc).isoformat(),
                "inventory_tier": INVENTORY_TIER,
                "spec": "paper/paper2_counterfactual_eval/PAPER2_SPEC.md §7",
                "interventions": str(SPEC_PATH),
                "group1": group1,
                "group2": group2,
                "rows": rows,
            },
            indent=2,
        )
        + "\n"
    )

    cols = [
        "task_id",
        "group",
        "verdict",
        "gold_moved",
        "fails",
        "returncode",
        "verdict_detail",
        "guest_json",
        "error",
    ]
    csv_path = OUT / f"{REPORT_STEM}.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    def count(pred, group=None):
        return sum(
            1
            for r in rows
            if pred(r) and (group is None or r.get("group") == group)
        )

    n_pass = count(lambda r: r["verdict"] == "PASS")
    n_id = count(lambda r: r["verdict"] == "REJECT_identifiability")
    n_hold = count(lambda r: r["verdict"] == "REJECT_held_leak")
    n_tech = count(lambda r: r["verdict"] == "technical_failure")

    pair_id = "contradiction-f011" if INVENTORY_TIER == 1 else "preference_inference-f014"
    md = [
        f"# Paper 2 — Tier {INVENTORY_TIER} inject-probe gate",
        "",
        f"Written {datetime.now(timezone.utc).isoformat()}.",
        "Live apply via `cf_inject.py` (not `--probe-only`). Snapshot restore between units.",
        "No agent. No judge. Sealed registry / D untouched.",
        "",
        f"Group 1 (non-`-I2`): **{len(group1)}**"
        + (f" `{group1[0]}` … `{group1[-1]}`" if group1 else ""),
        f"Group 2 (`-I2`): **{len(group2)}**"
        + (f" `{group2[0]}` … `{group2[-1]}`" if group2 else ""),
        "",
        f"**Total: {n_pass} PASS / {n_id} REJECT (identifiability) / "
        f"{n_hold} REJECT (held-leak) / {n_tech} technical-failure** "
        f"(of {len(rows)}).",
        "",
        "### By group",
        "",
        "| group | PASS | REJECT_id | REJECT_held | tech |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for gname, glabel in (("1", "group1 non-I2"), ("2", "group2 -I2")):
        md.append(
            f"| {glabel} | {count(lambda r: r['verdict']=='PASS', gname)} | "
            f"{count(lambda r: r['verdict']=='REJECT_identifiability', gname)} | "
            f"{count(lambda r: r['verdict']=='REJECT_held_leak', gname)} | "
            f"{count(lambda r: r['verdict']=='technical_failure', gname)} |"
        )

    i1 = next((r for r in rows if r["task_id"] == pair_id), None)
    i2 = next((r for r in rows if r["task_id"] == f"{pair_id}-I2"), None)
    md.extend(
        [
            "",
            f"### `{pair_id}` pair (partial multi-I failure clause)",
            "",
            f"- I1 (`{pair_id}`): **{(i1 or {}).get('verdict', 'missing')}**",
            f"- I2 (`{pair_id}-I2`): **{(i2 or {}).get('verdict', 'missing')}**",
            "",
            "Each variant is its own unit; a reject does not relabel the task as single-I.",
            "",
            "| task_id | group | verdict | gold_moved | fails |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for r in rows:
        fails = (r.get("fails") or "").replace("|", "\\|")[:120]
        md.append(
            f"| `{r['task_id']}` | {r['group']} | {r['verdict']} | "
            f"{r.get('gold_moved')} | {fails} |"
        )
    md.append("")
    md_path = OUT / f"{REPORT_STEM}.md"
    md_path.write_text("\n".join(md) + "\n")
    print(f"wrote {json_path}", flush=True)
    print(f"wrote {csv_path}", flush=True)
    print(f"wrote {md_path}", flush=True)
    print(
        f"summary PASS={n_pass} REJECT_id={n_id} REJECT_held={n_hold} tech={n_tech}",
        flush=True,
    )


def main() -> int:
    os.environ.pop("MYPCBENCH_CF_TASK", None)
    os.environ.pop("MYPCBENCH_CF_SCRIPT", None)
    os.environ.pop("MYPCBENCH_CF_PROBE_ONLY", None)
    os.environ.pop("ANTHROPIC_API_KEY", None)
    os.environ.pop("OPENAI_API_KEY", None)
    os.environ.pop("OPENROUTER_API_KEY", None)

    if not SPEC_PATH.is_file():
        raise SystemExit(f"missing {SPEC_PATH}; pull abfc00c+ first")

    group1, group2 = load_ready_groups()
    print(f"INVENTORY_TIER={INVENTORY_TIER} RESULTS={RESULTS} SNAP={SNAP}", flush=True)
    print(f"READY_RELATIVE total={len(group1)+len(group2)}", flush=True)
    print(f"group1 count={len(group1)} first={group1[0]!r} last={group1[-1]!r}", flush=True)
    g2_first = group2[0] if group2 else None
    g2_last = group2[-1] if group2 else None
    print(f"group2 count={len(group2)} first={g2_first!r} last={g2_last!r}", flush=True)
    print("group1 ids:", " ".join(group1), flush=True)
    print("group2 ids:", " ".join(group2), flush=True)

    exp1, exp2 = EXPECTED.get(INVENTORY_TIER, (None, None))
    if exp1 is not None and (len(group1) != exp1 or len(group2) != exp2):
        print(
            f"STOP: expected group1={exp1} group2={exp2} for inventory tier "
            f"{INVENTORY_TIER}; got {len(group1)}/{len(group2)}. "
            "Do not guess grouping.",
            flush=True,
        )
        return 2

    ordered = [(tid, "1") for tid in group1] + [(tid, "2") for tid in group2]
    RESULTS.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    env = None
    rows: list[dict] = []
    try:
        env = boot_env()
        snapshot(env)
        for task_id, group in ordered:
            dest = RESULTS / task_id
            print(f"----- restore + inject {task_id} (group {group}) -----", flush=True)
            try:
                restore(env)
            except Exception as exc:
                print(f"TECHNICAL FAILURE on restore before {task_id}: {exc!r}", flush=True)
                traceback.print_exc()
                rows.append({
                    "task_id": task_id,
                    "group": group,
                    "ok": False,
                    "gold_moved": None,
                    "fails": "restore_failed",
                    "returncode": 1,
                    "guest_json": "",
                    "probe_before": "",
                    "probe_after": "",
                    "extra_probes_before": [],
                    "extra_probes_after": [],
                    "error": repr(exc),
                    "verdict": "technical_failure",
                    "verdict_detail": "restore_failed",
                })
                continue
            proc = inject(env, task_id, dest)
            print((proc.stdout or "")[-2500:], flush=True)
            if proc.returncode != 0:
                print((proc.stderr or "")[-2500:], flush=True)
            row = summarize_record(task_id, group, dest, proc)
            rows.append(row)
            print(
                f"  verdict={row['verdict']} gold_moved={row['gold_moved']} "
                f"fails={row['fails']!r}",
                flush=True,
            )
    except Exception as exc:
        print(f"TECHNICAL FAILURE during boot/gate: {exc!r}", flush=True)
        traceback.print_exc()
        have = {r["task_id"] for r in rows}
        for task_id, group in ordered:
            if task_id in have:
                continue
            rows.append({
                "task_id": task_id,
                "group": group,
                "ok": False,
                "gold_moved": None,
                "fails": "boot_or_session_failure",
                "returncode": 1,
                "guest_json": "",
                "probe_before": "",
                "probe_after": "",
                "extra_probes_before": [],
                "extra_probes_after": [],
                "error": repr(exc),
                "verdict": "technical_failure",
                "verdict_detail": "boot_or_session_failure",
            })
    finally:
        if env is not None:
            try:
                env.close()
            except Exception:
                pass
        write_report(rows, group1, group2)

    return 0


if __name__ == "__main__":
    sys.exit(main())
