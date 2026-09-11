#!/usr/bin/env python3
"""Audit the frozen extractor's label coverage on a target corpus, before it is run.

`extract_component` identifies evidence by matching hand-written regex labels near a
candidate value. Those labels live in `LABELS`, keyed by `(task, component_id)`. When a key
is absent the function silently falls back to the component id with underscores turned into
spaces. It never raises, so an instrument with no coverage returns no detections and that
output is indistinguishable from an instrument that looked and found nothing.

This audit exists because that distinction cannot be recovered after the fact. It is
read-only: it reads `LABELS` statically and compares key sets. No trajectory, answer text,
archive or guest file is touched, and no instrument is run.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTRACT = ROOT / "scripts" / "study2_hatd_extract.py"
LOCK = ROOT / "out" / "study2_gold_path_lock.json"
SEALED = ROOT / "paper" / "paper3_observation_grounded" / "P3_1_SEALED_TRANSCRIPTION.json"

# The one Study 2 component reached by a bespoke branch instead of LABELS, hardcoded at the
# top of extract_component. Counted as covered because it is, just not via the table.
BESPOKE = {("contradiction-f004", "oddsmarket_gme_yes")}


def labels_keys() -> set[tuple[str, str]]:
    tree = ast.parse(EXTRACT.read_text())
    node = next(n for n in tree.body
                if isinstance(n, ast.AnnAssign) and getattr(n.target, "id", "") == "LABELS")
    return {tuple(ast.literal_eval(e) for e in k.elts) for k in node.value.keys}


def report(name: str, comps: list[tuple[str, str]], keys: set) -> dict:
    table = [c for c in comps if c in keys]
    bespoke = [c for c in comps if c in BESPOKE and c not in keys]
    fallback = [c for c in comps if c not in keys and c not in BESPOKE]
    cov = (len(table) + len(bespoke)) / len(comps) if comps else 0.0
    print(f"{name:26s} components {len(comps):3d} | LABELS {len(table):3d} | "
          f"bespoke {len(bespoke):2d} | fallback {len(fallback):3d} | coverage {cov:6.1%}")
    return {"n": len(comps), "labels": len(table), "bespoke": len(bespoke),
            "fallback": len(fallback), "coverage": cov,
            "uncovered": ["/".join(c) for c in fallback]}


def main() -> int:
    keys = labels_keys()
    lock = json.loads(LOCK.read_text())
    dev = [(t, c) for t, cs in lock["components"].items() for c in cs]
    sealed_doc = json.loads(SEALED.read_text())
    sealed = [(t, c) for t, cs in sealed_doc["components"].items() for c in cs]

    print(f"LABELS: {len(keys)} entries over {len({k[0] for k in keys})} tasks\n")
    d = report("Study 2 (development)", dev, keys)
    s = report("Paper 1 (sealed target)", sealed, keys)

    print(f"\nThe generic fallback is exercised by {d['fallback']} of {d['n']} components in "
          f"every measured result to date\n(0.6, 0.7, A-10, §4), and would be exercised by "
          f"{s['fallback']} of {s['n']} on the sealed target.")
    if s["fallback"]:
        print("\nUncovered sealed components:")
        for c in s["uncovered"]:
            print(f"  {c}")
    verdict = "USABLE" if s["coverage"] > 0 else "NOT EVALUABLE — zero label coverage"
    print(f"\nverdict: {verdict}")
    return 0 if s["coverage"] > 0 else 4


if __name__ == "__main__":
    raise SystemExit(main())
