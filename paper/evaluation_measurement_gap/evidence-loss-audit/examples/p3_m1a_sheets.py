#!/usr/bin/env python3
"""Emit P3-CORE Stage-1 stubs from join.json once PNGs exist.

Does not label. Does not read screenshot bytes as evidence.
See experiment_m1a_location/P3_HUMAN.md.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JOIN = ROOT / "experiment_m1a_location" / "join.json"
OUT = ROOT / "experiment_m1a_location" / "out_p3h"
PNG_ROOT = ROOT / "experiment_m1a_location" / "hpc_import"


def main() -> None:
    if not JOIN.exists():
        raise SystemExit(f"missing {JOIN}")
    data = json.loads(JOIN.read_text())
    rows = data["rows"]
    OUT.mkdir(parents=True, exist_ok=True)
    key_path = OUT / "p3h_stage1_key.csv"
    sheet_path = OUT / "p3h_stage1_sheet.csv"
    missing = [r for r in rows if not PNG_ROOT.exists()]
    if missing:
        (OUT / "STOP-NO-PNG.txt").write_text(
            "hpc_import/ is empty. Do not start annotators.\n"
            "Run HPC_RSYNC_PROMPT.md first.\n"
        )
        print("STOP-NO-PNG", file=sys.stderr)
    fields = ["lane", "task", "leg", "component", "row_id"]
    with key_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for i, r in enumerate(rows, start=1):
            w.writerow(
                {
                    "lane": r["lane"],
                    "task": r["task"],
                    "leg": r["leg"],
                    "component": r["component"],
                    "row_id": f"P3H-{i:02d}",
                }
            )
    with sheet_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["item_id", "task", "leg"])
        w.writeheader()
        for i, r in enumerate(rows, start=1):
            w.writerow(
                {"item_id": f"P3H-{i:02d}", "task": r["task"], "leg": r["leg"]}
            )
    print(f"wrote {key_path} and {sheet_path} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
