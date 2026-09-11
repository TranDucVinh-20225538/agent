#!/usr/bin/env python3
"""§6.2 transcription of the sealed corpus, frozen before any instrument touches it.

The authoritative source is `build_final.py::CLASS` (A-1.2), read statically with `ast` so
Paper 1's generator is never executed. §6.2 step 1 allows only values *literally stated* in
the prose, and that is the one place author discretion enters an otherwise sealed corpus.
So it is enforced rather than promised: every transcribed value carries the exact substring
it came from, and the validator fails if that substring is not present in the cell's `gold`
(for gold values) or `mech` (for reported values) string.

Nothing here reads a trajectory, an archive, a guest file, or Paper 1's rubric score. The
answer text the instrument will consume comes from `traj.jsonl` per A-1.3; this table
supplies only ground truth.
"""
from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "out" / "stage4_counterfactual_analysis_final" / "build_final.py"
SRC_SHA = "f00dbcdd33c944bf8429a40ee13d05160cdbac98997a2e9c879ede203b343531"
OUT = ROOT / "paper" / "paper3_observation_grounded" / "P3_1_SEALED_TRANSCRIPTION.json"

# Component ids and kinds. §6.2 step 3: this mapping is written and frozen before any
# instrument is run on this corpus. `kind` drives the extractor, so it is part of the
# mapping and not a later implementation choice.
COMPONENTS = {
    "retrieval-f001": {"loyalty_status": "entity", "loyalty_miles": "int"},
    "aggregation-f003": {"combined_filed_refund": "money"},
    "preference_inference-f018": {"gme_shares": "int", "oddsmarket_yes_shares": "int"},
    "counterfactual-f004": {"nec_1099_amount": "money"},
    "retrieval-f003": {"w2_wages": "money"},
    "retrieval-f016": {"cost_basis_total": "money", "cash": "money"},
    "retrieval-f029": {"w2_wages": "money", "fed_withheld": "money"},
    "retrieval-f030": {"nec_1099_amount": "money", "charitable": "money"},
    "aggregation-f018": {"charitable": "money", "home_office_days": "int"},
    "preference_inference-f004": {"hd_winner": "entity", "hd_winner_count": "int"},
}

# (model, task, leg, component): (gold_value, gold_literal, reported_value,
#                                 reported_literal, human_correct)
# `human_correct` is the hand coder's verdict, transcribed, never inferred by me. Where the
# coder wrote "Both correct" a rounded report is still recorded as correct -- the coder's
# judgement is the ground truth, and disagreement with the instrument is the measurement.
# A `None` reported_literal marks an observation the prose does not state literally: it is
# UNTRANSCRIBABLE and excluded, per §6.2 step 2.
F001 = [("loyalty_status", "Gold", "Gold", "Gold", "Gold", True),
        ("loyalty_miles", "38450", "38450", "38450", "38,450", True)]
F001C = [("loyalty_status", "Silver", "Silver", "Silver", "Silver", True),
         ("loyalty_miles", "8620", "8620", "8620", "8,620", True)]


def f003(base_rep_literal: str) -> tuple[list, list]:
    b = [("combined_filed_refund", "4871.70", "4871.70", base_rep_literal.replace(",", ""),
          base_rep_literal, True)]
    c = [("combined_filed_refund", "400.00", "400.00", "400", "400", True)]
    return b, c


def f016_full() -> tuple[list, list]:
    b = [("cost_basis_total", "8213.25", "8213.25", "8213.25", "8,213.25", True),
         ("cash", "420", "420", "420", "420", True)]
    c = [("cost_basis_total", "7114.20", "7114.20", "7114.20", "7,114.20", True),
         ("cash", "50", "50", "50", "50", True)]
    return b, c


def f029_full() -> tuple[list, list]:
    b = [("w2_wages", "142000", "142000", "142000", "142,000", True),
         ("fed_withheld", "28400", "28400", "28400", "28,400", True)]
    c = [("w2_wages", "90000", "90000", "90000", "90,000", True),
         ("fed_withheld", "18000", "18000", "18000", "18,000", True)]
    return b, c


def f004pref() -> tuple[list, list]:
    b = [("hd_winner", "Cooper's", "Cooper's", "Cooper's", "Cooper's", True),
         ("hd_winner_count", "88", "88", "88", "88", True)]
    c = [("hd_winner", "Backyard Ale House", "Backyard Ale House",
          "Backyard Ale House", "Backyard Ale House", True),
         ("hd_winner_count", "59", "59", "59", "59", True)]
    return b, c


TABLE: dict[tuple[str, str], dict[str, list]] = {}
for _m in ("Claude", "GPT", "Qwen3.5-35B-A3B", "Qwen3.5-9B", "Qwen3.8-Flash"):
    TABLE[(_m, "retrieval-f001")] = {"base": list(F001), "cf": list(F001C)}
for _m, _lit in (("Claude", "4,872"), ("GPT", "4,871.70"),
                 ("Qwen3.5-9B", "4,872"), ("Qwen3.8-Flash", "4,872")):
    _b, _c = f003(_lit)
    TABLE[(_m, "aggregation-f003")] = {"base": _b, "cf": _c}

TABLE[("Claude", "preference_inference-f018")] = {
    # Base values exist only through the stated identity "byte-identical to the base row",
    # which is LENIENT-only. Under STRICT the whole base leg is untranscribable -- exactly
    # the leg A-1.1 named.
    "base": [("gme_shares", "85", "85", None, None, None),
             ("oddsmarket_yes_shares", "200", "200", None, None, None)],
    "cf": [("gme_shares", "0", "85->0", "0", "0 sh", True),
           ("oddsmarket_yes_shares", "0", "->0/settled", "200", "200 sh", False)],
}
TABLE[("GPT", "counterfactual-f004")] = {
    # Gold-side failure: the base-leg pre-image is never literally given, only the
    # post-image "all ->0". The same gold-specification failure mode as VACUOUS_GOLD.
    "base": [("nec_1099_amount", None, None, "1200", "$1,200", None)],
    "cf": [("nec_1099_amount", "0", "all ->0", "1200", "$1,200", False)],
}
for _m, _bl, _cl in (("Claude", "136,320", "80,000"), ("GPT", "136,320", "80,000")):
    TABLE[(_m, "retrieval-f003")] = {
        "base": [("w2_wages", "136320", "136320", "136320", _bl, True)],
        "cf": [("w2_wages", "80000", "80000", "80000", _cl, True)],
    }
for _m in ("Claude", "GPT"):
    _b, _c = f016_full()
    TABLE[(_m, "retrieval-f016")] = {"base": _b, "cf": _c}
TABLE[("Qwen3.5-9B", "retrieval-f016")] = {
    # The coder states the base total and calls it wrong, and states the CF total. Cash is
    # never given for either leg of this cell, so those two observations are excluded.
    "base": [("cost_basis_total", "8213.25", "8213.25", "8788.75", "8,788.75", False),
             ("cash", "420", "420", None, None, None)],
    "cf": [("cost_basis_total", "7114.20", "7114.20", "7114.20", "7,114.20", True),
           ("cash", "50", "50", None, None, None)],
}
for _m in ("Claude", "GPT"):
    _b, _c = f029_full()
    TABLE[(_m, "retrieval-f029")] = {"base": _b, "cf": _c}
TABLE[("Qwen3.8-Flash", "retrieval-f029")] = {
    "base": [("w2_wages", "142000", "142000", "142000", "142,000", True),
             ("fed_withheld", "28400", "28400", "28400", "28,400", True)],
    "cf": [("w2_wages", "90000", "90000", "91200", "91,200", False),
           ("fed_withheld", "18000", "18000", "18000", "18,000", True)],
}
TABLE[("Claude", "retrieval-f030")] = {
    "base": [("nec_1099_amount", "1200", "1,200", "1080", "1,080", False),
             ("charitable", "950", "950", None, None, None)],
    "cf": [("nec_1099_amount", "1200", "1,200", "1200", "1,200", True),
           ("charitable", "100", "100", "100", "100", True)],
}
TABLE[("GPT", "retrieval-f030")] = {
    "base": [("nec_1099_amount", "1200", "1,200", "1200", "1,200", True),
             ("charitable", "950", "950", "950", "950", True)],
    "cf": [("nec_1099_amount", "1200", "1,200", "1200", "1,200", True),
           ("charitable", "100", "100", "100", "100", True)],
}
TABLE[("Claude", "aggregation-f018")] = {
    "base": [("charitable", "950", "950", "950", "950", True),
             ("home_office_days", "104", "104", "104", "104", True)],
    "cf": [("charitable", "0", "950->0", "0", "0.00", True),
           ("home_office_days", "0", "104->0", "0", "0 days", True)],
}
for _m in ("Claude", "GPT"):
    _b, _c = f004pref()
    TABLE[(_m, "preference_inference-f004")] = {"base": _b, "cf": _c}

# Read literally from the prose: the coder states the agent surfaced a file/sqlite
# disagreement on this leg. Whether the answer text actually carries two disagreeing values
# for one quantity is for the instrument to determine from the trajectory, not for me to
# decide here. §6.3's contrast subset is the opposite case, a cross-check that produced the
# same value twice, and the spec names retrieval-f029 Claude as its example.
CHANNEL_FLAGGED = {("Claude", "aggregation-f018", "cf"), ("GPT", "retrieval-f030", "cf")}
SAME_VALUE_CROSSCHECK = {("Claude", "retrieval-f029", "base"), ("Claude", "retrieval-f029", "cf"),
                         ("GPT", "retrieval-f029", "base"), ("GPT", "retrieval-f029", "cf")}


def load_class() -> dict:
    if SRC.read_bytes() and hashlib.sha256(SRC.read_bytes()).hexdigest() != SRC_SHA:
        raise SystemExit(f"ABORT: {SRC.name} does not match the hash frozen in A-1.")
    tree = ast.parse(SRC.read_text())
    node = next(n for n in tree.body if isinstance(n, ast.Assign)
                and any(getattr(t, "id", "") == "CLASS" for t in n.targets))
    return {tuple(ast.literal_eval(e) for e in k.elts):
            {kw.arg: ast.literal_eval(kw.value) for kw in v.keywords}
            for k, v in zip(node.value.keys, node.value.values)}


def main() -> int:
    C = load_class()
    if set(TABLE) != set(C):
        raise SystemExit(f"ABORT: table covers {len(TABLE)} cells, CLASS has {len(C)}.")

    rows, problems = [], []
    for (model, task), legs in TABLE.items():
        cell = C[(model, task)]
        for leg, obs in legs.items():
            for cid, gold, gold_lit, rep, rep_lit, ok in obs:
                if cid not in COMPONENTS[task]:
                    problems.append(f"{model}/{task}: {cid} not in the frozen mapping")
                # §6.2 step 1, enforced: gold literals must occur in the cell's gold
                # string, reported literals in its mech string.
                if gold_lit is not None and gold_lit not in cell["gold"]:
                    problems.append(f"{model}/{task}/{leg}/{cid}: gold literal "
                                    f"{gold_lit!r} absent from CLASS gold")
                if rep_lit is not None and rep_lit not in cell["mech"]:
                    problems.append(f"{model}/{task}/{leg}/{cid}: reported literal "
                                    f"{rep_lit!r} absent from CLASS mech")
                rows.append({
                    "model": model, "task": task, "leg": leg, "component": cid,
                    "kind": COMPONENTS[task][cid],
                    "gold": gold, "gold_literal": gold_lit,
                    "reported": rep, "reported_literal": rep_lit,
                    "human_correct": ok,
                    "transcribable": gold is not None and rep is not None,
                    "channel_inconsistency_flagged": (model, task, leg) in CHANNEL_FLAGGED,
                    "same_value_crosscheck": (model, task, leg) in SAME_VALUE_CROSSCHECK,
                })
    if problems:
        print("ABORT: transcription is not literal. §6.2 step 1 is violated.", file=sys.stderr)
        for p in problems:
            print("  !", p, file=sys.stderr)
        return 1

    tr = [r for r in rows if r["transcribable"]]
    legs = {(r["model"], r["task"], r["leg"]) for r in rows}
    dead = sorted(l for l in legs
                  if not any(r["transcribable"] for r in tr
                             if (r["model"], r["task"], r["leg"]) == l))
    print(f"cells {len(TABLE)}  legs {len(legs)}  observations {len(rows)}  "
          f"transcribable {len(tr)}  excluded {len(rows) - len(tr)}")
    print(f"legs with no transcribable observation (STRICT): {len(legs) - len(dead)}"
          f"/{len(legs)} transcribable, {len(dead)} excluded")
    for d in dead:
        print(f"  excluded leg: {'/'.join(d)}")

    # Cross-check against A-1.1's independently counted pre-check. The pre-check ran before
    # this table existed, so agreement is evidence the transcription rule is the one K5 was
    # assessed under -- and disagreement would mean K5's verdict does not cover this table.
    expect = {("Claude", "preference_inference-f018", "base"),
              ("GPT", "counterfactual-f004", "base")}
    if set(dead) != expect:
        print(f"ABORT: STRICT exclusions {set(dead)} != A-1.1's {expect}. K5 was assessed "
              f"on a different rule than this table applies.", file=sys.stderr)
        return 2
    print("matches A-1.1's STRICT pre-check exactly: 46/48 legs, both named exclusions")

    neg = [r for r in tr if r["human_correct"] is False]
    print(f"human-correct positives {sum(1 for r in tr if r['human_correct'])}, "
          f"negatives {len(neg)}  <- precision rests on {len(neg)} observations")
    for r in neg:
        print(f"  negative: {r['model']}/{r['task']}/{r['leg']}/{r['component']} "
              f"gold {r['gold']} reported {r['reported']}")
    if not 50 <= len(tr) <= 80:
        print(f"NOTE: {len(tr)} transcribable observations is outside §6.2 step 5's "
              f"stated 50-80 range.", file=sys.stderr)

    OUT.write_text(json.dumps({
        "source": "out/stage4_counterfactual_analysis_final/build_final.py::CLASS",
        "source_sha256": SRC_SHA, "rule": "STRICT",
        "n_cells": len(TABLE), "n_legs": len(legs), "n_observations": len(rows),
        "n_transcribable": len(tr), "n_negatives": len(neg),
        "excluded_legs": ["/".join(d) for d in dead],
        "components": COMPONENTS, "observations": rows,
    }, indent=1))
    print(f"\nwritten: {OUT}")
    print(f"sha256: {hashlib.sha256(OUT.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
