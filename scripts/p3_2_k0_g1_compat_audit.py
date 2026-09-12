#!/usr/bin/env python3
"""Audit whether G1 and G2 can be satisfied at once, before `R` is designed.

G1 requires every label to occur literally in the task's own `instruction`/`grading`. G2
requires `FROZEN` with `R`'s labels to reproduce the frozen development result exactly. If
a component's evidence-identifying vocabulary appears nowhere in its task-side text, then
no G1-compliant rule can ever emit a label for it, so G2 is unreachable for that component
*by construction* — a contradiction between two invariants rather than a shortcoming of any
algorithm. That has to be found before `R` exists.

The test uses the frozen label patterns themselves as matchers against task-side text, so
it invents no "regex stripping" of its own. A match means there exists a literal span in
the task definition that the frozen label identifies — i.e. a G1-compliant literal label
with the same identifying behaviour is possible in principle.

Read-only. Task definitions and the frozen label table only; no answer text, no trajectory,
no archive.
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTRACT = ROOT / "scripts" / "study2_hatd_extract.py"
LOCK = ROOT / "out" / "study2_gold_path_lock.json"
TASKS = ROOT / "external" / "MyPCBench-main" / "tasks" / "final" / "all_tasks_with_grading.json"


def frozen_labels() -> dict[tuple[str, str], list[str]]:
    tree = ast.parse(EXTRACT.read_text())
    node = next(n for n in tree.body
                if isinstance(n, ast.AnnAssign) and getattr(n.target, "id", "") == "LABELS")
    return {tuple(ast.literal_eval(e) for e in k.elts): ast.literal_eval(v)
            for k, v in zip(node.value.keys, node.value.values)}


def task_side_text(task: dict) -> str:
    g = task.get("grading")
    return " ".join([task.get("instruction") or "",
                     g if isinstance(g, str) else json.dumps(g, ensure_ascii=False)])


def main() -> int:
    labels = frozen_labels()
    lock = json.loads(LOCK.read_text())
    tasks = {t["id"]: t for t in json.loads(TASKS.read_text())}

    comps = [(t, c, s["kind"]) for t, cs in lock["components"].items() for c, s in cs.items()]
    live = [(t, c, k) for t, c, k in comps if k != "state"]
    missing_task = sorted({t for t, _, _ in live if t not in tasks})
    if missing_task:
        print(f"NOTE: {len(missing_task)} calibration tasks absent from the task file: "
              f"{missing_task}")

    rows, feasible, infeasible, no_labels = [], [], [], []
    for task, cid, kind in live:
        pats = labels.get((task, cid))
        text = task_side_text(tasks[task]) if task in tasks else ""
        hits, degenerate = [], []
        for p in (pats or []):
            try:
                m = re.search(p, text, re.IGNORECASE)
            except re.error:
                m = None
            if not m:
                continue
            # A pattern containing `.*` does not correspond to any fixed phrase: its match
            # is whatever lies between two anchors, here up to ~900 characters of rubric
            # text. Such a match cannot license a literal G1 label, so it is recorded as
            # degenerate rather than counted. This is a structural exclusion, not a length
            # threshold chosen to suit the outcome.
            (degenerate if ".*" in p else hits).append((p, m.group(0)))
        row = {"task": task, "component": cid, "kind": kind,
               "n_labels": len(pats or []), "n_grounded": len(hits),
               "n_degenerate": len(degenerate),
               "spans": [h[1] for h in hits],
               "max_span": max((len(h[1]) for h in hits), default=0)}
        rows.append(row)
        if pats is None:
            no_labels.append(row)
        elif hits:
            feasible.append(row)
        else:
            infeasible.append(row)

    print(f"label-sensitive calibration components: {len(live)}\n")
    hdr = (f"{'task':26s} {'component':26s} {'lab':>4s} {'grnd':>5s} {'deg':>4s} "
           f"{'len':>4s}  grounded spans")
    print(hdr)
    print("-" * (len(hdr) + 10))
    for r in rows:
        mark = " " if r["n_grounded"] else "!"
        print(f"{mark}{r['task']:25s} {r['component']:26s} {r['n_labels']:>4d} "
              f"{r['n_grounded']:>5d} {r['n_degenerate']:>4d} {r['max_span']:>4d}  "
              f"{', '.join(repr(s) for s in r['spans'][:3])}")

    print(f"\nG1-feasible   (>=1 frozen label matches task-side text): {len(feasible)}"
          f"/{len(live)}")
    print(f"G1-infeasible (no frozen label matches task-side text)  : {len(infeasible)}"
          f"/{len(live)}")
    if no_labels:
        print(f"without a LABELS entry at all                           : {len(no_labels)}")

    if infeasible:
        print("\nComponents for which no G1-compliant rule can reproduce the frozen "
              "behaviour:")
        for r in infeasible:
            print(f"  {r['task']}/{r['component']}  {r['n_labels']} frozen labels, "
                  f"{r['n_degenerate']} matching only via a `.*` wildcard, none usable "
                  f"as a literal label")
        print("\nverdict: the frozen labels for these components are NOT GROUNDABLE, so G2"
              "\ncannot be met by reproducing them. What this audit does *not* settle: "
              "whether\nsome *other* task-side-grounded phrase selects the same extraction "
              "windows and so\nreproduces the behaviour G2 actually tests. Deciding that "
              "requires reading the\ncalibration answer text, which this audit deliberately "
              "does not do.\n\nSo this is a determinate obstruction to one route to G2 and "
              "a risk flag on the\nother, not yet a proof of contradiction. Resolve before "
              "designing R; do not weaken\neither invariant silently.")
        return 5
    print("\nverdict: every label-sensitive component has at least one groundable frozen "
          "label. A grounded rule is not excluded a priori.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
