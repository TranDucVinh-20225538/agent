#!/usr/bin/env python3
"""Probe counterfactual-f003-I2 (Files venue_planned) on a clean guest.

No agent. Snapshot optional (single unit). Writes results under
results/paper2_f003_i2_probe/ and a one-row gate summary.
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

TASK = "counterfactual-f003-I2"
OUT_DIR = ROOT / "results" / "paper2_f003_i2_probe"
REPORT = ROOT / "out" / "paper2_f003_i2_probe_gate.json"


def main() -> int:
    os.environ.pop("MYPCBENCH_CF_PROBE_ONLY", None)
    os.environ.pop("ANTHROPIC_API_KEY", None)
    os.environ.pop("OPENAI_API_KEY", None)
    os.environ.pop("OPENROUTER_API_KEY", None)

    env = None
    row = None
    try:
        env = gate.boot_env()
        # Single unit — still snapshot/restore so state is known-clean.
        gate.SNAP = "/tmp/paper2_f003_i2_snap"
        gate.snapshot(env)
        gate.restore(env)
        dest = OUT_DIR
        if dest.exists():
            for p in dest.glob("*.guest.json"):
                p.unlink()
        proc = gate.inject(env, TASK, dest)
        print((proc.stdout or "")[-3000:], flush=True)
        if proc.returncode != 0:
            print((proc.stderr or "")[-2000:], flush=True)
        row = gate.summarize_record(TASK, "2", dest, proc)
        print(
            f"verdict={row['verdict']} gold_moved={row['gold_moved']} "
            f"fails={row['fails']!r}",
            flush=True,
        )
    except Exception as exc:
        print(f"TECHNICAL FAILURE: {exc!r}", flush=True)
        row = {
            "task_id": TASK,
            "group": "2",
            "verdict": "technical_failure",
            "gold_moved": None,
            "fails": "boot_or_inject_failure",
            "error": repr(exc),
            "returncode": 1,
            "guest_json": "",
            "probe_before": "",
            "probe_after": "",
            "verdict_detail": "boot_or_inject_failure",
        }
    finally:
        if env is not None:
            try:
                env.close()
            except Exception:
                pass

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    doc = {
        "written_at": datetime.now(timezone.utc).isoformat(),
        "task_id": TASK,
        "row": row,
        "note": (
            "File-backend I2 for venue_planned. "
            "PASS/REJECT only — no D rewrite, no agent."
        ),
    }
    REPORT.write_text(json.dumps(doc, indent=2) + "\n")
    md = ROOT / "out" / "paper2_f003_i2_probe_gate.md"
    md.write_text(
        "# Paper 2 — counterfactual-f003-I2 file-backend probe\n\n"
        f"Written {doc['written_at']}.\n\n"
        f"- verdict: **{row['verdict']}**\n"
        f"- gold_moved (SQL headroom probe): {row.get('gold_moved')}\n"
        f"- fails: {row.get('fails') or '(none)'}\n"
        f"- guest_json: `{row.get('guest_json') or ''}`\n"
    )
    print(f"wrote {REPORT}", flush=True)
    print(f"wrote {md}", flush=True)
    return 0 if row and row.get("verdict") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
