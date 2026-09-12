#!/usr/bin/env python3
"""Assemble CQ01–CQ06 authored last-responses in the C dialect.

Uses generate_slate.assemble (no per-id branch). Does not edit Q/V/R.
Does not call generate_slate.main(). $0. No agents.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import generate_slate as gs  # noqa: E402

CQ_IDS = [f"CQ{i:02d}" for i in range(1, 7)]
DEST = ROOT / "slate" / "cq"


def main() -> int:
    params = json.loads((ROOT / "params_cq.json").read_text())
    if list(params) != CQ_IDS:
        raise SystemExit(f"params_cq keys {list(params)} != {CQ_IDS}")
    DEST.mkdir(parents=True, exist_ok=True)
    for cid, row in params.items():
        if row["gold"] in gs.FORBIDDEN_VALUES or row["wrong"] in gs.FORBIDDEN_VALUES:
            raise SystemExit(f"forbidden gold/wrong in {cid}")
        if "observations" in row:
            raise SystemExit(f"{cid}: observations must be generated, not authored in params")
        gs.write_cluster(DEST / f"{cid}.json", gs.assemble(cid, "qualification", row))
    print(f"wrote {len(CQ_IDS)} CQ clusters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
