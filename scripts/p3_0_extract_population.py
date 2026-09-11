#!/usr/bin/env python3
"""P3-0 step 0.2: run the frozen extractor on the pre-registered 21 legs.

Host-only, read-only with respect to every archive. Nothing here is a new instrument:

  * extraction is `study2_hatd_extract.extract_leg` at 3242c30, unchanged;
  * gold comes from `out/study2_gold_path_lock.json`, unchanged;
  * matching is `protocol/matching.py`, unchanged;
  * `match_one` and `components_for` are *imported* from `study2_hatd_apply.py` rather
    than copied, so exactly one implementation of the matching semantics exists.

The population is fixed by P3_0_SPEC.md §5c and hardcoded below, so it cannot drift while
the script is being run. It is also cross-checked against `out/p3_0_legs.jsonl` from 0.1:
any disagreement aborts rather than proceeding on a population nobody registered.

Strata are reported separately and never pooled:

  gate0             16  excluded VALID_DONE legs on keyed tasks
  dissoc_nondone     4  non-DONE partner legs of the 4 matched dissociation cells
  unmatched_nondone  1  claude/retrieval-f002/G0, whose cell has no terminating leg

Usage:
    p3_0_extract_population.py [--legs out/p3_0_legs.jsonl]
                               [--jsonl out/p3_0_extracted.jsonl]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

VINH = Path("/data2/hpcshared/Vinh-/agent")
sys.path.insert(0, str(VINH / "scripts"))
sys.path.insert(0, str(VINH / "paper/paper2_counterfactual_eval/protocol"))

from study2_hatd_extract import (  # noqa: E402
    GOLD_LOCK,
    extract_leg,
    final_answer_from_traj,
    load_lock,
)
from study2_hatd_apply import components_for, match_one  # noqa: E402
from matching import binary_track  # noqa: E402

EXTRACTOR_SHA = "3242c30a1423f9ef90754809e50cd2698c5560b5"

# P3_0_SPEC.md §5c. The four matched dissociation cells: DONE leg first, then the
# non-DONE partner that this step adds.
DISSOCIATION_CELLS = [
    ("flash", "aggregation-f037", "G1", "G0"),
    ("flash", "counterfactual-f005", "G0", "G1"),
    ("gpt", "preference_inference-f010", "G1", "G0"),
    ("gpt", "retrieval-f010", "G0", "G1"),
]
UNMATCHED_NONDONE = [("claude", "retrieval-f002", "G0")]


def load_0_1(path):
    rows = [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
    return {(r["lane"], r["task"], r["leg"]): r for r in rows}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--legs", default="out/p3_0_legs.jsonl")
    ap.add_argument("--jsonl", default="out/p3_0_extracted.jsonl")
    a = ap.parse_args()

    idx = load_0_1(a.legs)
    if len(idx) != 171:
        print(f"ABORT: {a.legs} has {len(idx)} legs, expected 171 from a clean 0.1.",
              file=sys.stderr)
        return 3

    # Stratum membership, derived from 0.1 for gate0 and hardcoded for the rest.
    plan = []
    for key, r in sorted(idx.items()):
        if r.get("gate0_measurable"):
            plan.append((key, "gate0"))
    for lane, task, done_leg, nd_leg in DISSOCIATION_CELLS:
        plan.append(((lane, task, nd_leg), "dissoc_nondone"))
    for key in UNMATCHED_NONDONE:
        plan.append((key, "unmatched_nondone"))

    # Cross-check the registered population against what 0.1 actually saw.
    problems = []
    counts = {"gate0": 0, "dissoc_nondone": 0, "unmatched_nondone": 0}
    for key, stratum in plan:
        counts[stratum] += 1
        r = idx.get(key)
        if r is None:
            problems.append(f"{key} not present in 0.1 output")
            continue
        if not r["task_keyed"]:
            problems.append(f"{key} is on an unkeyed task; extraction would be vacuous")
        if stratum == "gate0" and not r["valid_done"]:
            problems.append(f"{key} in gate0 but not VALID_DONE")
        if stratum != "gate0" and r["valid_done"]:
            problems.append(f"{key} registered as non-DONE but 0.1 says VALID_DONE")
    for lane, task, done_leg, _nd in DISSOCIATION_CELLS:
        r = idx.get((lane, task, done_leg))
        if r is None or not r["valid_done"]:
            problems.append(f"({lane},{task},{done_leg}) should be the terminating partner")
        elif not r.get("gate0_measurable"):
            problems.append(f"({lane},{task},{done_leg}) should already be inside gate0")
    if counts != {"gate0": 16, "dissoc_nondone": 4, "unmatched_nondone": 1}:
        problems.append(f"stratum sizes {counts} != registered 16/4/1")
    if problems:
        print("ABORT: registered population disagrees with 0.1:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 3

    print(f"population verified against 0.1: {counts}, total {len(plan)} legs\n")

    lock = load_lock()
    out = []
    with open(a.jsonl, "w") as fh:
        for (lane, task, leg), stratum in plan:
            r = idx[(lane, task, leg)]
            comps = components_for(task, lock)
            specs = lock["components"][task]
            rec = extract_leg(task, Path(r["dir"]), lock)
            ans = final_answer_from_traj(Path(rec["traj"])) if rec.get("traj") else ""
            matches = {
                cid: match_one(specs[cid], rec["gold"].get(cid), rec["reported"].get(cid))
                for cid in specs
            }
            # Leg-level all-positive-weight match, via the frozen predicate applied to
            # this one leg on both sides rather than a second implementation.
            leg_match = binary_track(comps, matches, matches)
            rec.update({
                "lane": lane, "leg": leg, "stratum": stratum,
                "extractor_sha": EXTRACTOR_SHA, "gold_lock": str(GOLD_LOCK),
                "valid_done": r["valid_done"], "exclusion_cause": r["exclusion_cause"],
                "score": r["score"],
                "answer_chars": len(ans),
                "answer_sha256": hashlib.sha256(ans.encode()).hexdigest() if ans else None,
                "matches": matches,
                "n_components": len(specs),
                "n_matched": sum(1 for v in matches.values() if v),
                "leg_component_match": bool(leg_match),
            })
            fh.write(json.dumps(rec, default=str) + "\n")
            out.append(rec)

    print(f"extracted {len(out)} legs -> {a.jsonl}\n")

    by = {}
    for r in out:
        by.setdefault(r["stratum"], []).append(r)

    hdr = f"{'stratum':18s} {'n':>3s} {'full match':>11s} {'any comp':>9s} {'empty answer':>13s}"
    print(hdr)
    print("-" * len(hdr))
    for s in ("gate0", "dissoc_nondone", "unmatched_nondone"):
        rs = by.get(s, [])
        if not rs:
            continue
        print(f"{s:18s} {len(rs):>3d} "
              f"{sum(1 for r in rs if r['leg_component_match']):>11d} "
              f"{sum(1 for r in rs if r['n_matched'] > 0):>9d} "
              f"{sum(1 for r in rs if not r['answer_chars']):>13d}")

    print("\nper-leg detail")
    h2 = (f"{'lane':7s} {'task':28s} {'leg':4s} {'stratum':18s} {'DONE':5s} "
          f"{'S':>4s} {'matched':>9s} {'full':>5s} {'ans_ch':>7s}")
    print(h2)
    print("-" * len(h2))
    for r in out:
        print(f"{r['lane']:7s} {r['task']:28s} {r['leg']:4s} {r['stratum']:18s} "
              f"{str(r['valid_done']):5s} {str(r['score']):>4s} "
              f"{r['n_matched']}/{r['n_components']:<7} "
              f"{str(r['leg_component_match']):5s} {r['answer_chars']:>7d}")

    # The pre-registered new quantity, reported only for the four registered cells.
    print("\npair-level component match under terminal-independent extraction")
    print("(the four matched dissociation cells; NOT Y on A, which stays 0 on all 18 pairs)")
    h3 = f"{'lane':7s} {'task':28s} {'DONE leg':10s} {'non-DONE leg':13s} {'both match':>11s}"
    print(h3)
    print("-" * len(h3))
    got = {(r["lane"], r["task"], r["leg"]): r for r in out}
    n_both = 0
    for lane, task, done_leg, nd_leg in DISSOCIATION_CELLS:
        d = got.get((lane, task, done_leg))
        n = got.get((lane, task, nd_leg))
        dm = d["leg_component_match"] if d else None
        nm = n["leg_component_match"] if n else None
        both = bool(dm and nm)
        n_both += int(both)
        print(f"{lane:7s} {task:28s} {done_leg}={str(dm):7s} {nd_leg}={str(nm):10s} "
              f"{str(both):>11s}")
    print(f"\ncells with both legs matching: {n_both} / {len(DISSOCIATION_CELLS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
