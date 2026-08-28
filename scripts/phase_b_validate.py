#!/usr/bin/env python3
"""Phase B.1: validate all 10 frozen interventions on one guest.

No agent. No judge. No rewrite of I. Snapshot /data + Tax_2025 after boot,
restore between tasks so each I is applied to a clean world.

A QEMU/tooling failure is recorded as failed execution, not a reason to
edit the patch.
"""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("AGENT_ROOT", Path(__file__).resolve().parents[1]))
HARNESS = ROOT / "external/MyPCBench-main/agent-harness"
RESULTS = ROOT / "results" / "phase_b_validate"
OUT = ROOT / "out"
SNAP = "/tmp/phase_b_snap"

TASKS = [
    t["task_id"]
    for t in json.loads((ROOT / "cf/phase_b_registry.json").read_text())["tasks"]
]


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
    script = f"""
set -e
rm -rf /data
cp -a {SNAP}/data /data
if [ -d {SNAP}/Tax_2025 ]; then
  rm -rf /home/user/Documents/Tax_2025
  mkdir -p /home/user/Documents
  cp -a {SNAP}/Tax_2025 /home/user/Documents/Tax_2025
fi
"""
    out = guest_text(env, script)
    if out:
        print(out[:500], flush=True)


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
        container_name=f"mypcbench-phaseb-{os.getpid()}",
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


def summarize_record(task_id: str, dest: Path, proc: subprocess.CompletedProcess) -> dict:
    path = dest / f"{task_id}.guest.json"
    row = {
        "task_id": task_id,
        "ok": False,
        "gold_moved": None,
        "fails": "",
        "returncode": proc.returncode,
        "guest_json": str(path) if path.exists() else "",
        "probe_before": "",
        "probe_after": "",
        "error": "",
    }
    if proc.returncode != 0 and not path.exists():
        row["error"] = (proc.stderr or proc.stdout or "")[-1500]
        row["fails"] = "inject_process_failed"
        return row
    if not path.exists():
        row["error"] = "no guest.json"
        row["fails"] = "missing_guest_json"
        return row
    rec = json.loads(path.read_text())
    row["ok"] = bool(rec.get("ok"))
    row["gold_moved"] = rec.get("gold_moved")
    row["fails"] = "; ".join(rec.get("fails") or [])
    row["probe_before"] = str(rec.get("probe_before") or "")[:240]
    row["probe_after"] = str(rec.get("probe_after") or "")[:240]
    if not row["ok"] and not row["fails"]:
        row["fails"] = "ok_false"
        row["error"] = (proc.stderr or proc.stdout or "")[-1500]
    return row


def write_report(rows: list[dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    cols = [
        "task_id",
        "ok",
        "gold_moved",
        "fails",
        "returncode",
        "guest_json",
        "error",
    ]
    csv_path = OUT / "phase_b_validate.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    n_ok = sum(1 for r in rows if r["ok"])
    md = [
        "# Phase B.1 intervention validation",
        "",
        f"Written {datetime.now(timezone.utc).isoformat()}.",
        "Dummy guest. No agent. Frozen I. Snapshot restored between tasks.",
        "",
        f"**{n_ok}/{len(rows)} interventions validated.**",
        "",
        "| task_id | ok | gold_moved | fails |",
        "| --- | --- | --- | --- |",
    ]
    for r in rows:
        fails = (r.get("fails") or "").replace("|", "\\|")
        md.append(
            f"| `{r['task_id']}` | {r['ok']} | {r['gold_moved']} | {fails} |"
        )
    md.append("")
    if n_ok == len(rows):
        md.append("B.2 (Claude / GPT / Qwen 35B × 10) may start. Do not rewrite I.")
    else:
        md.append(
            "Do not start B.2. Failed cells are execution failures; "
            "do not edit I to rescue them. Fix inject/tooling, then re-validate."
        )
        md.append("")
        md.append("A 10/10 here is required before any Phase B trajectory is observed.")
    (OUT / "phase_b_validate.md").write_text("\n".join(md) + "\n")
    print(f"wrote {csv_path}", flush=True)
    print(f"wrote {OUT / 'phase_b_validate.md'}", flush=True)
    print(f"validated {n_ok}/{len(rows)}", flush=True)


def main() -> int:
    os.environ.pop("MYPCBENCH_CF_TASK", None)
    os.environ.pop("MYPCBENCH_CF_SCRIPT", None)
    os.environ.pop("ANTHROPIC_API_KEY", None)
    os.environ.pop("OPENAI_API_KEY", None)
    os.environ.pop("OPENROUTER_API_KEY", None)
    RESULTS.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    print("tasks:", " ".join(TASKS), flush=True)
    env = None
    rows: list[dict] = []
    try:
        env = boot_env()
        snapshot(env)
        for task_id in TASKS:
            dest = RESULTS / task_id
            print(f"----- restore + inject {task_id} -----", flush=True)
            restore(env)
            proc = inject(env, task_id, dest)
            print((proc.stdout or "")[-2000:], flush=True)
            if proc.returncode != 0:
                print((proc.stderr or "")[-2000:], flush=True)
            row = summarize_record(task_id, dest, proc)
            rows.append(row)
            print(
                f"  ok={row['ok']} gold_moved={row['gold_moved']} fails={row['fails']!r}",
                flush=True,
            )
    except Exception as exc:
        print(f"TECHNICAL FAILURE during boot/validate: {exc!r}", flush=True)
        have = {r["task_id"] for r in rows}
        for task_id in TASKS:
            if task_id in have:
                continue
            rows.append({
                "task_id": task_id,
                "ok": False,
                "gold_moved": None,
                "fails": "boot_or_session_failure",
                "returncode": 1,
                "guest_json": "",
                "probe_before": "",
                "probe_after": "",
                "error": repr(exc),
            })
    finally:
        if env is not None:
            try:
                env.close()
            except Exception:
                pass
        write_report(rows)

    return 0 if rows and all(r["ok"] for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
