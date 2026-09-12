#!/usr/bin/env python3
"""G1, G1b, and synthetic fixtures for R. Reads no answer text.

G1: every label R emits for a Study 2 or sealed (task, component) is a grounded
substring of that task's instruction/grading.

G1b: scripts/p3_2_r.py contains no task id and no component id as a string
literal. Checked against the 184 task ids and the component ids of both corpora.

Synthetics use invented identifiers only, so they are not a G1b vehicle.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import p3_2_r as R  # noqa: E402

TASKS = ROOT / "external" / "MyPCBench-main" / "tasks" / "final" / "all_tasks_with_grading.json"
LOCK = ROOT / "out" / "study2_gold_path_lock.json"
SEALED = ROOT / "paper" / "paper3_observation_grounded" / "P3_1_SEALED_TRANSCRIPTION.json"
R_PATH = ROOT / "scripts" / "p3_2_r.py"


def fixtures() -> list[str]:
    bad = []
    # invented ids only
    got = R.derive_labels("Report the alpha beta figure.", "", "alpha_beta")
    if got != ["alpha", "beta", "alpha beta"]:
        bad.append(f"alpha_beta: {got}")
    got = R.derive_labels("Count open items in the inbox.", "", "n_open_items")
    if got != ["open", "items", "open items"]:
        bad.append(f"n_open_items: {got}")
    got = R.derive_labels("Nothing relevant lives here.", "", "alpha_beta")
    if got != []:
        bad.append(f"ungrounded alpha_beta should be empty, got {got}")
    got = R.derive_labels("The beta score only.", "", "alpha_beta")
    if got != ["beta"]:
        bad.append(f"partial ground: {got}")
    # whitespace / case
    got = R.derive_labels("  ALPHA\nBETA  ", "", "alpha_beta")
    if got != ["alpha", "beta", "alpha beta"]:
        bad.append(f"norm: {got}")
    return bad


def string_literals(path: Path) -> list[str]:
    tree = ast.parse(path.read_text())
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            out.append(n.value)
    return out


def main() -> int:
    fx = fixtures()
    print("synthetics:", "PASS" if not fx else "FAIL")
    for b in fx:
        print(f"  {b}")

    tasks = {t["id"]: t for t in json.loads(TASKS.read_text())}
    lock = json.loads(LOCK.read_text())
    sealed = json.loads(SEALED.read_text())
    live = [(t, c) for t, cs in lock["components"].items()
            for c, s in cs.items() if s["kind"] != "state"]
    sealed_comps = [(t, c) for t, cs in sealed["components"].items() for c in cs]

    # G1b
    forbidden = set(tasks)
    forbidden |= {t for t, _ in live} | {c for _, c in live}
    forbidden |= {t for t, _ in sealed_comps} | {c for _, c in sealed_comps}
    hits = []
    for lit in string_literals(R_PATH):
        if lit in forbidden:
            hits.append(lit)
    print(f"G1b: {'PASS' if not hits else 'FAIL'}  "
          f"(literals scanned against {len(forbidden)} identifiers)")
    for h in hits:
        print(f"  forbidden literal {h!r}")

    # G1 on Study 2 + sealed component index; task text only
    def check(pairs, name):
        n_lab, n_empty, ungrounded = 0, 0, []
        print(f"\n{name}")
        for task, cid in pairs:
            t = tasks.get(task)
            if t is None:
                print(f"  NOTE {task}/{cid}: task absent from the 184-file")
                continue
            labs = R.derive_labels(t.get("instruction"), t.get("grading"), cid)
            n_lab += len(labs)
            if not labs:
                n_empty += 1
            for lab in labs:
                if not R.grounded(lab, R.task_text(t.get("instruction"), t.get("grading"))):
                    ungrounded.append(f"{task}/{cid}: {lab!r}")
            print(f"  {task}/{cid:32s} {labs}")
        print(f"  labels {n_lab}  empty {n_empty}/{len(pairs)}  "
              f"ungrounded {len(ungrounded)}")
        return ungrounded

    u2 = check(live, "Study 2 (calibration, task-side only)")
    us = check(sealed_comps, "sealed component index (ids only, no gold, no answers)")
    g1 = not u2 and not us
    print(f"\nG1: {'PASS' if g1 else 'FAIL'}")
    for u in u2 + us:
        print(f"  {u}")

    if fx or hits or not g1:
        return 5
    print("\nG1 and G1b hold. R is not frozen; G2 has not been run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
