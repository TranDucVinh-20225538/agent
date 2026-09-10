#!/usr/bin/env python3
"""Audit the per_step judge's frame handling. Read-only; no API calls.

Answers three questions from archived rubric_result.json alone:
  1. Does S reproduce exactly from weights x per-frame max? (instrument sanity)
  2. Do models differ in frames per step, and does deduping frames move S?
  3. Does the max-reduce inflate S for long episodes?

Usage: paper2_judge_frame_audit.py GLOB [GLOB ...]
  e.g. paper2_judge_frame_audit.py 'results/study2-*/*/*/rubric_result.json'
Model label is taken from the segment after the run-prefix in the cell path.
"""
import glob
import json
import re
import statistics as st
import sys
from collections import defaultdict


def score_of(per_frame_rows, weights):
    n = len(weights)
    per_item_max = [
        max((r["scores"][i] if i < len(r["scores"]) else 0) for r in per_frame_rows)
        for i in range(n)
    ]
    return 100.0 * sum(m * w for m, w in zip(per_item_max, weights))


def model_of(path):
    m = re.search(r"results/[a-z0-9]+-([a-z0-9]+)-", path)
    return m.group(1) if m else "unknown"


def main(patterns):
    paths = [p for pat in patterns for p in glob.glob(pat)]
    if not paths:
        print("no rubric_result.json matched", file=sys.stderr)
        return 2

    by_model = defaultdict(lambda: {"cells": 0, "frames": 0, "steps": 0, "S": 0.0,
                                    "S_first": 0.0, "S_last": 0.0, "moved": 0})
    repro_bad, repro_worst, cells = 0, 0.0, []

    for p in sorted(paths):
        try:
            d = json.load(open(p))
        except Exception as exc:
            print(f"SKIP unreadable {p}: {exc}", file=sys.stderr)
            continue
        rows = [r for r in (d.get("per_step_scores") or []) if r.get("scores")]
        rubrics = d.get("rubrics") or []
        if not rows or not rubrics or d.get("score") is None:
            continue
        weights = [r.get("weight", 1.0 / len(rubrics)) for r in rubrics]

        s_full = score_of(rows, weights)
        diff = abs(s_full - float(d["score"]))
        if diff > 0.51:  # stored score is rounded to integer percent
            repro_bad += 1
            repro_worst = max(repro_worst, diff)
            print(f"REPRO MISMATCH {p}: stored={d['score']} recomputed={s_full:.3f}")

        first, last = {}, {}
        for r in rows:
            k = r.get("step_num")
            first.setdefault(k, r)
            last[k] = r
        s_first = score_of(list(first.values()), weights)
        s_last = score_of(list(last.values()), weights)

        m = by_model[model_of(p)]
        m["cells"] += 1
        m["frames"] += len(rows)
        m["steps"] += len(last)
        m["S"] += s_full
        m["S_first"] += s_first
        m["S_last"] += s_last
        if abs(s_full - s_first) > 1e-9 or abs(s_full - s_last) > 1e-9:
            m["moved"] += 1
            print(f"DEDUP MOVES S {p}: as-exec={s_full:.2f} first={s_first:.2f} last={s_last:.2f}")
        cells.append((len(last), s_full))

    print(f"\nreproducibility: {len(cells)} cells, {repro_bad} mismatch, "
          f"max abs diff {repro_worst:.3f}")

    print(f"\n{'model':14}{'cells':>6}{'frames/step':>13}{'S':>8}{'S_1frame':>10}{'cells_moved':>13}")
    for name, m in sorted(by_model.items()):
        c = m["cells"]
        print(f"{name:14}{c:6}{m['frames']/m['steps']:13.3f}{m['S']/c:8.2f}"
              f"{m['S_last']/c:10.2f}{m['moved']:13}")

    xs = [c[0] for c in cells]
    ys = [c[1] for c in cells]
    mx, my = st.mean(xs), st.mean(ys)
    den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
    corr = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den if den else float("nan")
    print(f"\ncorr(steps, S) = {corr:.3f}   (negative => max-reduce does not inflate long episodes)")
    print(f"{'steps':10}{'n':>5}{'mean S':>9}")
    for lo, hi, lab in [(1, 10, "1-10"), (11, 30, "11-30"), (31, 60, "31-60"), (61, 10**6, "61+")]:
        sel = [y for x, y in cells if lo <= x <= hi]
        if sel:
            print(f"{lab:10}{len(sel):5}{st.mean(sel):9.2f}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1:]))
