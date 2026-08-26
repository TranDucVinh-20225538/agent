#!/usr/bin/env python3
"""Identifiability gate for a dummy-probe dump. Exit 2 = reject at $0."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rows_of(payload: dict) -> list:
    raw = payload.get("probe_before") or payload.get("probe_after") or payload.get("gold")
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return []
    return raw or []


def gate_aggregation_f003(payload: dict) -> str | None:
    rows = rows_of(payload)
    filed = [
        r for r in rows
        if str(r.get("status", "")).lower() == "filed"
    ]
    # gold blob may already be n_filed/combined
    if rows and "n_filed" in rows[0]:
        n = int(rows[0]["n_filed"] or 0)
        if n < 2:
            return f"GATE: n_filed={n}; a one-year sum is point lookup, not aggregation."
        return None
    if len(filed) < 2:
        return f"GATE: {len(filed)} filed prior-year return(s); need >= 2 to identify a multi-record sum."
    return None


GATES = {
    "aggregation-f003": gate_aggregation_f003,
    "aggregation-f003-A": gate_aggregation_f003,
}


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: evidence_gate.py <guest.json> [task_id]", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    payload = json.loads(path.read_text())
    tid = sys.argv[2] if len(sys.argv) > 2 else payload.get("id", "")
    fn = GATES.get(tid)
    dest = ROOT / "results" / f"{tid}_probe.sql.txt"
    dest.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(rows_of(payload), indent=2)
    if fn is None:
        dest.write_text(blob + "\nGATE: no identifiability rule for this id.\n")
        print(dest.read_text())
        return 2
    reason = fn(payload)
    dest.write_text(blob + ("\n" + reason + "\n" if reason else "\nIDENTIFIABLE\n"))
    print(dest.read_text())
    return 2 if reason else 0


if __name__ == "__main__":
    sys.exit(main())
