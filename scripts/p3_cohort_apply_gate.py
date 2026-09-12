#!/usr/bin/env python3
"""Apply the locked 20-cluster gate to Wave A + Wave B ledgers.

Not an experiment. Does not inspect values, agents, or STS.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out" / "p3_cohort_probe"
A_PATH = OUT / "wave_a.json"
B_PATH = OUT / "wave_b.json"


def main() -> int:
    a = json.loads(A_PATH.read_text())
    b = json.loads(B_PATH.read_text())
    if b.get("status") == "TECHNICAL_ABORT" or b.get("n_survive") is None:
        print("REFUSE: Wave B is TECHNICAL_ABORT / not scored. Do not apply the gate.")
        return 2
    if b.get("n_scored") != 16:
        print(f"REFUSE: Wave B n_scored={b.get('n_scored')} != 16")
        return 2
    n_a = int(a["n_survive"])
    n_b = int(b["n_survive"])
    n = n_a + n_b
    passed = n >= 20
    survivors = [r["id"] for r in a["rows"] if r["survive"]] + [
        r["id"] for r in b["rows"] if r["survive"]
    ]
    failed = [r["id"] for r in a["rows"] if not r["survive"]] + [
        r["id"] for r in b["rows"] if not r["survive"]
    ]
    doc = {
        "protocol": "P3_COHORT_PROBE_PROTOCOL.md",
        "n_wave_a": n_a,
        "n_wave_b": n_b,
        "n": n,
        "threshold": 20,
        "gate": "PASS" if passed else "FAIL",
        "survivors": survivors,
        "failed": failed,
        "next": (
            "lock cohort → hash labels → I1 → pre-registration → trajectory 1"
            if passed
            else "comparative branch closed; C7 existence only; write A"
        ),
    }
    (OUT / "gate.json").write_text(json.dumps(doc, indent=2) + "\n")
    md = [
        "# P3 cohort probe gate",
        "",
        f"Wave A: {n_a}/12. Wave B: {n_b}/16. **n = {n}.** Gate: **{doc['gate']}**.",
        "",
        doc["next"] + ".",
        "",
    ]
    (OUT / "gate.md").write_text("\n".join(md) + "\n")
    print(f"n={n} gate={doc['gate']}")
    return 0 if passed else 5


if __name__ == "__main__":
    raise SystemExit(main())
