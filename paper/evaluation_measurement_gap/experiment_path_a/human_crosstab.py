#!/usr/bin/env python3
"""Sensitivity: ARB human trajectory_success × Path A (V, E).

Not gold. Not Table 2. Does not retune extractor or families.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from math import exp, lgamma
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CELLS = ROOT / "out" / "path_a_cells.csv"
ANN = ROOT / "schema" / "annotations.csv"
OUT_CSV = ROOT / "out" / "human_crosstab_fail.csv"
OUT_MD = ROOT / "out" / "human_crosstab.md"


def key(r: dict) -> tuple:
    return (r["benchmark"], r["task_id"], r["model_name"], r["exp_name"])


def logC(n: int, k: int) -> float:
    if k < 0 or k > n:
        return float("-inf")
    return lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)


def fisher_two_sided(a: int, b: int, c: int, d: int) -> float:
    n1, n2 = a + b, c + d
    k = a + c
    lo, hi = max(0, k - n2), min(k, n1)
    p_obs = exp(logC(n1, a) + logC(n2, c) - logC(n1 + n2, a + c))
    s = 0.0
    for x in range(lo, hi + 1):
        px = exp(logC(n1, x) + logC(n2, k - x) - logC(n1 + n2, k))
        if px <= p_obs + 1e-15:
            s += px
    return min(1.0, s)


def main() -> None:
    cells = list(csv.DictReader(CELLS.open()))
    ann = list(csv.DictReader(ANN.open()))
    by: dict[tuple, list[str]] = defaultdict(list)
    for r in ann:
        by[key(r)].append(r["trajectory_success"].strip())

    wavwa = [
        r
        for r in cells
        if r["benchmark"] in ("webarena", "visualwebarena")
        and r["episode"] == "ELIGIBLE"
    ]
    rows = []
    missing = 0
    for r in wavwa:
        labs = by.get(key(r))
        if not labs:
            missing += 1
            continue
        n = len(labs)
        n_succ = sum(1 for x in labs if x == "Successful")
        rows.append(
            {
                **r,
                "n_ann": n,
                "n_succ": n_succ,
                "unan": n_succ == n and n > 0,
                "any": n_succ > 0,
            }
        )

    fail_abs = [r for r in rows if r["V"] == "FAIL" and r["E"] == "ABSTAIN"]
    fail_det = [r for r in rows if r["V"] == "FAIL" and r["E"] == "DETERMINING"]
    a, b = sum(r["unan"] for r in fail_abs), len(fail_abs) - sum(
        r["unan"] for r in fail_abs
    )
    c, d = sum(r["unan"] for r in fail_det), len(fail_det) - sum(
        r["unan"] for r in fail_det
    )
    p = fisher_two_sided(a, b, c, d)

    with OUT_CSV.open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "benchmark",
                "task_id",
                "model_name",
                "exp_name",
                "family",
                "E",
                "V",
                "n_ann",
                "n_succ",
                "unan_successful",
                "any_successful",
            ],
        )
        w.writeheader()
        for r in rows:
            if r["V"] != "FAIL":
                continue
            w.writerow(
                {
                    "benchmark": r["benchmark"],
                    "task_id": r["task_id"],
                    "model_name": r["model_name"],
                    "exp_name": r["exp_name"],
                    "family": r["family"],
                    "E": r["E"],
                    "V": r["V"],
                    "n_ann": r["n_ann"],
                    "n_succ": r["n_succ"],
                    "unan_successful": int(r["unan"]),
                    "any_successful": int(r["any"]),
                }
            )

    n_ann_abs = Counter(r["n_ann"] for r in fail_abs)
    n_ann_det = Counter(r["n_ann"] for r in fail_det)
    pos_abs_n = Counter(r["n_ann"] for r in fail_abs if r["unan"])
    pos_det_n = Counter(r["n_ann"] for r in fail_det if r["unan"])

    md = f"""# Human × FAIL type (sensitivity)

**Not gold. Not Table 2. Not a ledger finding unless copied.**
Join: all 366 WA/VWA ELIGIBLE matched annotations (`missing={missing}`).
`path_a_cells.csv` unchanged. Extractor unchanged.

Most trajectories have **one** ARB annotator (318/366).
"Unanimous Successful" is often a single label.

## FAIL column (licensed contrast)

| FAIL type | n | unan. Successful | any Successful |
|---|---:|---:|---:|
| Empty \(I\) (ABSTAIN) | {len(fail_abs)} | {sum(r['unan'] for r in fail_abs)} ({sum(r['unan'] for r in fail_abs)/len(fail_abs):.3f}) | {sum(r['any'] for r in fail_abs)} |
| Candidate then mismatch (DETERMINING) | {len(fail_det)} | {sum(r['unan'] for r in fail_det)} ({sum(r['unan'] for r in fail_det)/len(fail_det):.3f}) | {sum(r['any'] for r in fail_det)} |

Fisher exact two-sided on unan. Successful: {a}/{len(fail_abs)} vs {c}/{len(fail_det)}, p≈{p:.2e}.

Annotator multiplicity: empty-I FAIL n_ann {dict(n_ann_abs)}; positives {dict(pos_abs_n)}.
Mismatch FAIL n_ann {dict(n_ann_det)}; positives {dict(pos_det_n)}.

## Licensed reading

Human-labeled success among released FAIL is **rarer** on empty \(I\) (4/126)
than on candidate-then-mismatch (50/173). Empty-\(I\) FAIL is not the hidden-success
pocket. Hidden success, if any, sits in the mismatch cell — the surface Lù/Dong
already study (rule-based string fail, human success).

This **does not** license “FAIL unjustified from \(I\).”
It **does** license: the two FAIL kinds are not exchangeable vs human labels.

## Forbidden

- Headline 50/173 as this paper's discovery (Lù already: oracles underreport success)
- Use human as Table 2 gold
- Recode ABSTAIN → FAIL
- Treat 4/126 as an unjustified-FAIL rate
"""
    OUT_MD.write_text(md)
    print(OUT_MD.read_text())


if __name__ == "__main__":
    main()
