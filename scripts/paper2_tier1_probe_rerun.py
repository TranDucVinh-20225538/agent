#!/usr/bin/env python3
"""Re-run only Paper 2 Tier 1 units that hit technical failure; merge into gate report.

Does not touch sealed registry / D. No agent / judge.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("AGENT_ROOT", Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(ROOT / "scripts"))

import paper2_tier1_probe_gate as gate  # noqa: E402

RERUN = ["aggregation-f020", "aggregation-f040"]
REPORT = ROOT / "out" / "paper2_tier1_probe_gate.json"


def main() -> int:
    os.environ.pop("MYPCBENCH_CF_TASK", None)
    os.environ.pop("MYPCBENCH_CF_SCRIPT", None)
    os.environ.pop("MYPCBENCH_CF_PROBE_ONLY", None)
    os.environ.pop("ANTHROPIC_API_KEY", None)
    os.environ.pop("OPENAI_API_KEY", None)
    os.environ.pop("OPENROUTER_API_KEY", None)

    if not REPORT.is_file():
        raise SystemExit(f"missing prior report {REPORT}")

    prior = json.loads(REPORT.read_text())
    group1 = list(prior["group1"])
    group2 = list(prior["group2"])
    by_id = {r["task_id"]: r for r in prior["rows"]}

    print(f"rerun units: {RERUN}", flush=True)
    env = None
    try:
        env = gate.boot_env()
        gate.snapshot(env)
        for task_id in RERUN:
            group = "2" if task_id.endswith("-I2") else "1"
            dest = gate.RESULTS / task_id
            row = None
            for attempt in range(1, 4):
                # wipe prior guest json so we don't reuse a stale FAIL
                if dest.exists():
                    for p in dest.glob("*.guest.json"):
                        p.unlink()
                print(
                    f"----- restore + inject {task_id} (rerun attempt {attempt}/3) -----",
                    flush=True,
                )
                try:
                    gate.restore(env)
                except Exception as exc:
                    print(f"TECHNICAL FAILURE on restore before {task_id}: {exc!r}", flush=True)
                    row = {
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
                    }
                    continue
                proc = gate.inject(env, task_id, dest)
                print((proc.stdout or "")[-2500:], flush=True)
                if proc.returncode != 0:
                    print((proc.stderr or "")[-2500:], flush=True)
                row = gate.summarize_record(task_id, group, dest, proc)
                print(
                    f"  verdict={row['verdict']} gold_moved={row['gold_moved']} "
                    f"fails={row['fails']!r}",
                    flush=True,
                )
                if row["verdict"] != "technical_failure":
                    break
            by_id[task_id] = row
    finally:
        if env is not None:
            try:
                env.close()
            except Exception:
                pass

    # Preserve original group order
    ordered_ids = group1 + group2
    rows = [by_id[tid] for tid in ordered_ids if tid in by_id]
    gate.write_report(rows, group1, group2)

    # Annotate merge
    doc = json.loads(REPORT.read_text())
    doc["rerun_at"] = datetime.now(timezone.utc).isoformat()
    doc["rerun_units"] = RERUN
    REPORT.write_text(json.dumps(doc, indent=2) + "\n")
    print(f"merged into {REPORT}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
