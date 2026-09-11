#!/usr/bin/env python3
"""P3-0 Gate 1: does a high rubric score come from one observation or from several?

Read-only. Reads `per_step_scores` out of rubric_result.json files that are already on
disk. No judging, no model call, no write to any archive.

Paper 2's score is a max-reduce over frames, S = 100 * sum_i w_i * max_t I(i,t). That
leaves two ways to reach a high S. Either some single step carried every positive-weight
item at once, or each item fired at a different step and the aggregate was assembled
across time from observations that never coexisted. The second case is the one that
matters for P3, so the reported scalar is

    gap = S_maxreduce - max_t (100 * sum_i w_i * I(i,t))

Every cell is self-checked: if the recomputed max-reduce score does not reproduce the
stored `score`, the cell is reported unreadable rather than interpreted.

Usage:
    p3_0_item_timing.py GLOB [GLOB ...]          # globs matching cell or leg dirs
    p3_0_item_timing.py --json out.json GLOB     # also dump per-cell detail
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

TOL = 1e-6


def find_rubrics(roots):
    seen, out = set(), []
    for pat in roots:
        for p in glob.glob(pat):
            if os.path.isfile(p) and os.path.basename(p) == "rubric_result.json":
                cand = [p]
            else:
                cand = glob.glob(os.path.join(p, "**", "rubric_result.json"), recursive=True)
            for c in cand:
                rp = os.path.realpath(c)
                if rp not in seen:
                    seen.add(rp)
                    out.append(c)
    return sorted(out)


def read_cell(path):
    """Return a dict of timing facts for one rubric_result.json, or an error row."""
    with open(path) as fh:
        d = json.load(fh)

    stored = d.get("score")
    steps = d.get("per_step_scores")
    rubrics = d.get("rubrics") or []
    maxes = d.get("per_rubric_max") or []

    if not isinstance(steps, list) or not steps or not rubrics:
        return {"path": path, "readable": False, "why": "no per_step_scores or rubrics"}

    weights = [float(r.get("weight") or 0.0) for r in rubrics]
    n = len(weights)
    if len(maxes) != n:
        maxes = [1] * n

    # Normalised per-item score at each step. A step whose array is the wrong length or
    # which recorded an error contributes nothing; it is counted, not silently dropped.
    grid, skipped = [], 0
    for s in steps:
        sc = s.get("scores")
        if not isinstance(sc, list) or len(sc) != n:
            skipped += 1
            continue
        row = []
        for i, v in enumerate(sc):
            m = float(maxes[i]) or 1.0
            try:
                row.append(max(0.0, min(1.0, float(v) / m)))
            except (TypeError, ValueError):
                row.append(0.0)
        grid.append((s.get("step_num"), s.get("screenshot"), row))
    if not grid:
        return {"path": path, "readable": False, "why": "no usable score rows"}

    # Self-check: reproduce the stored max-reduce score. The stored `score` is the
    # recomputed value rounded to an integer, so compare at that granularity rather than
    # exactly; a genuine disagreement is off by more than rounding.
    recomputed = 100.0 * sum(weights[i] * max(r[2][i] for r in grid) for i in range(n))
    if stored is None or abs(recomputed - float(stored)) >= 0.5:
        return {
            "path": path, "readable": False,
            "why": f"score did not reproduce (stored={stored}, recomputed={recomputed:.4f})",
        }

    pos = [i for i in range(n) if weights[i] > 0]

    # Best single observation, and where it occurs.
    best_val, best_step = -1.0, None
    for step_num, shot, row in grid:
        v = 100.0 * sum(weights[i] * row[i] for i in pos)
        if v > best_val + TOL:
            best_val, best_step = v, step_num

    # Co-firing: a step at which every positive-weight item fires.
    cofire = [sn for sn, _, row in grid if all(row[i] >= 1.0 - TOL for i in pos)]
    last_step = grid[-1][0]

    first_fire = {}
    for i in pos:
        hit = [sn for sn, _, row in grid if row[i] >= 1.0 - TOL]
        first_fire[str(i)] = hit[0] if hit else None

    fired = [i for i in pos if first_fire[str(i)] is not None]
    distinct = len({first_fire[str(i)] for i in fired})

    return {
        "path": path,
        "readable": True,
        "score": float(stored),
        "n_items": n,
        "n_pos_items": len(pos),
        "weights": weights,
        "n_steps_scored": len(grid),
        "n_steps_skipped": skipped,
        "score_maxreduce_unrounded": round(recomputed, 4),
        "best_single_step_score": round(best_val, 4),
        "best_single_step": best_step,
        # Measured against the unrounded max-reduce so the gap is not polluted by the
        # integer rounding that produced the stored `score`.
        "gap": round(recomputed - best_val, 4),
        "cofire_steps": cofire,
        "has_cofire": bool(cofire),
        "cofire_persists_to_last": bool(cofire) and cofire[-1] == last_step,
        "last_step": last_step,
        "first_fire_by_item": first_fire,
        "n_items_ever_fired": len(fired),
        "n_distinct_first_fire_steps": distinct,
        "all_items_fired": len(fired) == len(pos),
        # The composition case: every item fired, but never together.
        "composed_across_time": len(fired) == len(pos) and not cofire,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("globs", nargs="+")
    ap.add_argument("--json", dest="json_out")
    ap.add_argument("--min-score", type=float, default=None,
                    help="only report cells with stored score >= this")
    a = ap.parse_args()

    paths = find_rubrics(a.globs)
    if not paths:
        print("no rubric_result.json found", file=sys.stderr)
        return 2

    rows = [read_cell(p) for p in paths]
    ok = [r for r in rows if r["readable"]]
    bad = [r for r in rows if not r["readable"]]
    if a.min_score is not None:
        ok = [r for r in ok if r["score"] >= a.min_score]

    print(f"cells found            : {len(rows)}")
    print(f"readable (score repro) : {len(rows) - len(bad)}"
          f"{'' if a.min_score is None else f'  (after score filter: {len(ok)})'}")
    print(f"unreadable             : {len(bad)}")
    for r in bad:
        print(f"  ! {r['path']}: {r['why']}")
    if not ok:
        return 0

    composed = [r for r in ok if r["composed_across_time"]]
    cofired = [r for r in ok if r["has_cofire"]]
    persist = [r for r in ok if r["cofire_persists_to_last"]]
    gaps = sorted(r["gap"] for r in ok)

    print()
    print(f"co-firing step exists           : {len(cofired)} / {len(ok)}")
    print(f"  of which persists to last step: {len(persist)}")
    print(f"all items fired but never together (composed across time): {len(composed)} / {len(ok)}")
    print(f"gap = S_maxreduce - best_single_step:")
    print(f"  zero (score attainable in one observation) : {sum(1 for g in gaps if abs(g) < 1e-4)}")
    print(f"  min / median / max                          : "
          f"{gaps[0]:.2f} / {gaps[len(gaps)//2]:.2f} / {gaps[-1]:.2f}")

    print()
    hdr = f"{'cell':58s} {'S':>6s} {'best1':>7s} {'gap':>7s} {'cofire':>7s} {'persist':>8s} {'steps':>6s}"
    print(hdr)
    print("-" * len(hdr))
    for r in sorted(ok, key=lambda x: -x["gap"]):
        cell = r["path"].replace("/rubric_result.json", "")
        print(f"{cell[-58:]:58s} {r['score']:>6.1f} {r['best_single_step_score']:>7.1f} "
              f"{r['gap']:>7.1f} {str(r['has_cofire']):>7s} "
              f"{str(r['cofire_persists_to_last']):>8s} {r['n_steps_scored']:>6d}")

    if a.json_out:
        with open(a.json_out, "w") as fh:
            json.dump({"cells": rows}, fh, indent=1)
        print(f"\nper-cell detail -> {a.json_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
