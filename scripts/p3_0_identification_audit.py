#!/usr/bin/env python3
"""P3-0.7: identification audit over the 134 rows of 0.6.

Host-only, read-only with respect to every archive. Implements
P3_0_IDENTIFICATION_AUDIT_SPEC.md and nothing beyond it.

Tests one mechanistic prediction: a RECALL_MISS occurs because the frozen extractor
accumulated two disagreeing candidates across label windows, so `_unique_or_none`
returned None. The window logic is NOT reimplemented. `_unique_or_none` is wrapped by a
recorder that returns the original value unchanged, and the frozen `extract_component` /
`gold_for_component` are then called exactly as `extract_leg` calls them.

Because `_unique_or_none` returns None iff its filtered input is empty or disagrees, the
two causes are read off the frozen function's own output rather than from a predicate of
ours.

Usage:
    p3_0_identification_audit.py [--audit out/p3_0_recall_audit.jsonl]
                                 [--a-legs out/study2_hatd_legs.jsonl]
                                 [--p3-legs out/p3_0_extracted.jsonl]
                                 [--jsonl out/p3_0_identification_audit.jsonl]
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

VINH = Path("/data2/hpcshared/Vinh-/agent")
sys.path.insert(0, str(VINH / "scripts"))
sys.path.insert(0, str(VINH / "paper/paper2_counterfactual_eval/protocol"))

import study2_hatd_extract as ex  # noqa: E402
from study2_hatd_apply import match_one  # noqa: E402

EXPECTED_ROWS = 134
EXPECTED_LEGS = 57
EXPECTED_CATS = {"MATCH": 20, "RECALL_MISS": 39, "ABSENT": 61, "VACUOUS_GOLD": 14}

# P3_0_IDENTIFICATION_AUDIT_SPEC.md section 1: structurally unreadable, excluded from
# every share. All five are ABSENT, so excluding them raises the miss share.
UNREADABLE = {
    ("flash", "preference_inference-f014", "G1", "designated_booking_property"),
    ("gpt", "preference_inference-f014", "G1", "designated_booking_property"),
    ("claude", "preference_inference-f014", "G1", "designated_booking_property"),
    ("flash", "retrieval-f009", "G0", "nyc_checkin_date"),
    ("flash", "retrieval-f009", "G1", "nyc_checkin_date"),
}
MECHANISM_TASKS = lambda t: t.startswith("counterfactual-") or t == "contradiction-f004"

# ---------------------------------------------------------------- instrumentation

_CALLS: list[dict] = []
_ORIG = ex._unique_or_none


def _filtered(vals):
    """The list `_unique_or_none` builds before comparing. Mirrors its filter only."""
    out = []
    for v in vals:
        if v is None:
            continue
        if isinstance(v, str):
            if v.strip():
                out.append(v.strip())
        else:
            out.append(v)
    return out


def _recording(vals):
    returned = _ORIG(vals)          # frozen behaviour, unchanged
    _CALLS.append({"found": list(vals), "filtered": _filtered(vals), "returned": returned})
    return returned


ex._unique_or_none = _recording


def labels_for(task: str, cid: str) -> list[str]:
    if task == "contradiction-f004" and cid == "oddsmarket_gme_yes":
        return [r"oddsmarket", r"yes", r"position", r"\bshares\b"]
    return ex.LABELS.get((task, cid), [re.escape(cid.replace("_", " "))])


def gold_among(spec: dict, gold, values) -> bool:
    """Is gold among these candidates, under the frozen matcher for this kind?"""
    for v in values:
        try:
            if match_one(spec, gold, v):
                return True
        except Exception:
            continue
    return False


def classify(spec: dict, task: str, cid: str, gold, reported, matched: bool,
             answer: str, calls):
    """Cause per spec section 5. Exactly one applies.

    HIT is the contrast class: the extractor produced a value and it matched gold. It
    cannot occur on a RECALL_MISS row, where `extractor_match` is False by construction.
    """
    disagreeing = [c for c in calls if c["returned"] is None and len(c["filtered"]) >= 1]
    if reported is not None:
        # A discarded sub-channel can coexist with a value from another path, but what
        # reached the output is the pick, so the pick is the cause.
        return ("HIT" if matched else "M4"), disagreeing
    if disagreeing:
        return "M1", disagreeing
    any_label = any(re.search(lab, answer, re.IGNORECASE) for lab in labels_for(task, cid))
    return ("M3" if any_label else "M2"), []


def wilson(k: int, n: int):
    if n == 0:
        return None
    z, p = 1.959963985, k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [max(0.0, c - h), min(1.0, c + h)]


def share(k, n):
    if n == 0:
        return f"{'n/a':>7s}   no rows"
    ci = wilson(k, n)
    return f"{k / n:>7.3f}   [{ci[0]:.3f}, {ci[1]:.3f}]"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", default="out/p3_0_recall_audit.jsonl")
    ap.add_argument("--a-legs", default="out/study2_hatd_legs.jsonl")
    ap.add_argument("--p3-legs", default="out/p3_0_extracted.jsonl")
    ap.add_argument("--jsonl", default="out/p3_0_identification_audit.jsonl")
    a = ap.parse_args()

    rows = [json.loads(l) for l in Path(a.audit).read_text().splitlines() if l.strip()]
    paths = {}
    for p in (a.a_legs, a.p3_legs):
        for line in Path(p).read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                paths[(r["lane"], r["task"], r["leg"])] = (r.get("traj"), r.get("guest"))

    legs = {(r["lane"], r["task"], r["leg"]) for r in rows}
    cats = Counter(r["category"] for r in rows)
    bad = []
    if len(rows) != EXPECTED_ROWS:
        bad.append(f"{len(rows)} rows, expected {EXPECTED_ROWS}")
    if len(legs) != EXPECTED_LEGS:
        bad.append(f"{len(legs)} legs, expected {EXPECTED_LEGS}")
    for c, n in EXPECTED_CATS.items():
        if cats[c] != n:
            bad.append(f"category {c} = {cats[c]}, expected {n}")
    if cats.get("ANOMALY", 0) != 0:
        bad.append(f"category ANOMALY = {cats['ANOMALY']}, expected 0")
    missing = sorted(k for k in legs if k not in paths)
    if missing:
        bad.append(f"no traj/guest path for {len(missing)} leg(s): {missing[:3]}")
    if bad:
        print("ABORT: population disagrees with spec section 3", file=sys.stderr)
        for b in bad:
            print(f"  - {b}", file=sys.stderr)
        return 3
    print(f"population verified: {len(rows)} rows over {len(legs)} legs, "
          f"categories {dict(sorted(cats.items()))}\n")

    lock = ex.load_lock()
    answers, guests, out, drift = {}, {}, [], []

    for r in sorted(rows, key=lambda x: (x["stratum"], x["lane"], x["task"], x["leg"],
                                         x["component_id"])):
        key = (r["lane"], r["task"], r["leg"])
        traj_s, guest_s = paths[key]
        if key not in answers:
            tp = Path(traj_s) if traj_s else None
            answers[key] = ex.final_answer_from_traj(tp) if tp and tp.exists() else ""
            gp = Path(guest_s) if guest_s else None
            guests[key] = ex.load_guest(gp) if gp and gp.exists() else {}
        answer, guest = answers[key], guests[key]
        task, cid = r["task"], r["component_id"]
        spec = lock["components"][task][cid]

        _CALLS.clear()
        gold = ex.gold_for_component(guest, task, cid, lock)
        reported = ex.extract_component(task, cid, spec["kind"], answer)
        calls = [dict(c) for c in _CALLS]

        for c in calls:
            if c["returned"] is not None and not c["filtered"]:
                drift.append(f"{key}/{cid}: _unique_or_none returned "
                             f"{c['returned']!r} from an empty filtered list")
        g, rp = ex._jsonable(gold), ex._jsonable(reported)
        if json.dumps(g, sort_keys=True, default=str) != \
           json.dumps(r["gold"], sort_keys=True, default=str):
            drift.append(f"{key}/{cid}: gold {g!r} != 0.6 recorded {r['gold']!r}")
        if json.dumps(rp, sort_keys=True, default=str) != \
           json.dumps(r["reported"], sort_keys=True, default=str):
            drift.append(f"{key}/{cid}: reported {rp!r} != 0.6 recorded {r['reported']!r}")

        cause, dis = (None, [])
        if r["category"] in ("MATCH", "RECALL_MISS", "ABSENT"):
            cause, dis = classify(spec, task, cid, gold, reported,
                                  bool(r["extractor_match"]), answer, calls)

        found = [ex._jsonable(v) for c in dis for v in c["filtered"]]
        sub = None
        if cause == "M1":
            sub = "M1a" if gold_among(spec, gold, [v for c in dis for v in c["filtered"]]) \
                  else "M1b"
        out.append({**{k: r[k] for k in ("stratum", "lane", "task", "leg",
                                         "component_id", "kind", "category",
                                         "text_present", "n_candidates")},
                    "gold": g, "reported": rp, "cause": cause, "m1_form": sub,
                    "disagreeing_found": found,
                    "n_unique_calls": len(calls),
                    "unreadable": (r["lane"], task, r["leg"], cid) in UNREADABLE})

    if drift:
        print("ABORT: instrumented replay did not reproduce 0.6 (spec section 4):",
              file=sys.stderr)
        for d in drift[:40]:
            print(f"  - {d}", file=sys.stderr)
        if len(drift) > 40:
            print(f"  ... and {len(drift) - 40} more", file=sys.stderr)
        return 3
    print("instrumented replay reproduced every gold and reported value from 0.6, and no "
          "_unique_or_none\ncall returned a value from an empty list: instrumentation did "
          "not alter behaviour\n")

    with open(a.jsonl, "w") as fh:
        for row in out:
            fh.write(json.dumps(row, default=str) + "\n")
    print(f"{len(out)} rows -> {a.jsonl}\n")

    miss = [r for r in out if r["category"] == "RECALL_MISS"]
    CAUSES = ["M1", "M2", "M3", "M4"]
    ALL_CAUSES = ["HIT"] + CAUSES

    print("=== every RECALL_MISS row with its cause\n")
    hdr = (f"{'stratum':<18s} {'lane':<6s} {'task':<26s} {'leg':<4s} "
           f"{'component':<28s} {'kind':<11s} {'cause':<5s} {'form':<4s} gold -> disagreeing found")
    print(hdr)
    print("-" * len(hdr))
    for r in miss:
        f = r["disagreeing_found"]
        print(f"{r['stratum']:<18s} {r['lane']:<6s} {r['task']:<26s} {r['leg']:<4s} "
              f"{r['component_id']:<28s} {r['kind']:<11s} {r['cause']:<5s} "
              f"{(r['m1_form'] or '-'):<4s} {r['gold']!r} -> {f if f else '-'}")
    print()

    def table(title, keyfn, rowset, order=None, cols=None):
        cols = cols or CAUSES
        g = defaultdict(Counter)
        for r in rowset:
            g[keyfn(r)][r["cause"]] += 1
        keys = order or sorted(g)
        w = max([len(title)] + [len(str(k)) for k in keys])
        print(f"{title:<{w}} " + " ".join(f"{c:>6s}" for c in cols) + f"{'n':>6s}")
        print("-" * (w + 7 * len(cols) + 6))
        for k in keys:
            if k not in g:
                continue
            print(f"{str(k):<{w}} " + " ".join(f"{g[k][c]:>6d}" for c in cols)
                  + f"{sum(g[k].values()):>6d}")
        print()

    print("=== RECALL_MISS cause counts, overall")
    cc = Counter(r["cause"] for r in miss)
    for c in CAUSES:
        print(f"  {c:<4s} {cc[c]:>3d}")
    print(f"  M1a {sum(1 for r in miss if r['m1_form']=='M1a'):>3d}"
          f"   (extractor saw gold and discarded it)")
    print(f"  M1b {sum(1 for r in miss if r['m1_form']=='M1b'):>3d}"
          f"   (disagreement between two wrong values)\n")

    print("=== RECALL_MISS by stratum");   table("stratum", lambda r: r["stratum"], miss)
    print("=== RECALL_MISS by kind");      table("kind", lambda r: r["kind"], miss)
    print("=== RECALL_MISS by task");      table("task", lambda r: r["task"], miss)

    print("=== primary quantity: M1 / RECALL_MISS\n")
    print(f"{'population':<26s} {'M1':>4s} {'miss':>5s} {'share':>7s}   95% CI")
    print("-" * 62)
    for lab, pred in (("all RECALL_MISS", lambda r: True),
                      ("A", lambda r: r["stratum"] == "A"),
                      ("outside A", lambda r: r["stratum"] != "A")):
        s = [r for r in miss if pred(r)]
        k = sum(1 for r in s if r["cause"] == "M1")
        print(f"{lab:<26s} {k:>4d} {len(s):>5d} {share(k, len(s))}")
    print()

    print("=== secondary quantity: task-level concentration of M1\n")
    print(f"{'task group':<42s} {'M1':>4s} {'miss':>5s} {'share':>7s}   95% CI")
    print("-" * 78)
    for lab, pred in (("counterfactual-* + contradiction-f004",
                       lambda r: MECHANISM_TASKS(r["task"])),
                      ("all other tasks", lambda r: not MECHANISM_TASKS(r["task"]))):
        s = [r for r in miss if pred(r)]
        k = sum(1 for r in s if r["cause"] == "M1")
        print(f"{lab:<42s} {k:>4d} {len(s):>5d} {share(k, len(s))}")
    print()

    print("=== contrast class: causes on MATCH and ABSENT rows")
    print("    (M1 rate among misses must be read against its rate elsewhere)\n")
    rest = [r for r in out if r["category"] in ("MATCH", "ABSENT")]
    table("category", lambda r: r["category"], rest, ["MATCH", "ABSENT"],
          cols=ALL_CAUSES)

    print("=== spec section 2.1 control: gme_avg_cost in both tasks")
    print("    same component id, same kind, same gold; contradiction-f004 carries a")
    print("    covering second label and counterfactual-f005 does not\n")
    ctrl = sorted((r for r in out if r["component_id"] == "gme_avg_cost"),
                  key=lambda r: (r["task"], r["lane"], r["leg"]))
    hdr = (f"{'task':<22s} {'labels':<34s} {'lane':<6s} {'leg':<4s} "
           f"{'category':<12s} {'cause':<5s} reported")
    print(hdr)
    print("-" * len(hdr))
    for r in ctrl:
        print(f"{r['task']:<22s} {str(labels_for(r['task'], 'gme_avg_cost')):<34s} "
              f"{r['lane']:<6s} {r['leg']:<4s} {r['category']:<12s} "
              f"{str(r['cause']):<5s} {r['reported']!r}")
    print()

    print("=== the 5 structurally unreadable rows, kept visible and out of every share\n")
    for r in out:
        if r["unreadable"]:
            print(f"  {r['stratum']:<18s} {r['lane']:<6s} {r['task']:<26s} {r['leg']:<4s} "
                  f"{r['component_id']:<28s} {r['category']:<12s} cause={r['cause']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
