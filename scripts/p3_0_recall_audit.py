#!/usr/bin/env python3
"""P3-0.6: extractor recall audit over the 57 pre-registered legs.

Host-only, read-only with respect to every archive. Implements P3_0_RECALL_AUDIT_SPEC.md
and nothing beyond it.

The only new thing here is the *search scope*. Candidate enumeration and the equality
relation are the frozen ones, imported rather than reimplemented:

  * candidates come from `study2_hatd_extract` regexes and `parse_moneys`;
  * equality comes from `protocol/matching.py`;
  * `reported` / `matches` are recomputed with the frozen extractor and cross-checked
    against what 0.2 and Study 2 already wrote. Any disagreement aborts.

The frozen extractor searches a +-120 char window around task labels. This asks whether
the gold value is anywhere in the answer at all, which upper-bounds what any label
strategy could have recovered.

Usage:
    p3_0_recall_audit.py [--a-legs out/study2_hatd_legs.jsonl]
                         [--p3-legs out/p3_0_extracted.jsonl]
                         [--jsonl out/p3_0_recall_audit.jsonl]
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

from study2_hatd_extract import (  # noqa: E402
    INT_RE,
    _DATE_RE,
    extract_leg,
    final_answer_from_traj,
    load_lock,
    parse_moneys,
)
from study2_hatd_apply import match_one  # noqa: E402
from matching import Kind, match_categorical, match_integer, match_money_usd  # noqa: E402

EXTRACTOR_SHA = "3242c30a1423f9ef90754809e50cd2698c5560b5"
EXPECTED_LEGS = 57
EXPECTED_STRATA = {"A": 36, "gate0": 16, "dissoc_nondone": 4, "unmatched_nondone": 1}

_MD = str.maketrans({c: None for c in "*_`#"} | {"\u2013": "-", "\u2014": "-"})
_WS = re.compile(r"\s+")


def norm(s) -> str:
    """Rule R1, frozen in P3_0_RECALL_AUDIT_SPEC.md section 4."""
    return _WS.sub(" ", str(s).translate(_MD).casefold()).strip().rstrip(".")


def _is_vacuous(gold) -> bool:
    if gold is None:
        return True
    if isinstance(gold, dict):
        return all(v is None for v in gold.values())
    return False


def candidates(kind: str, component_id: str, answer: str):
    """Frozen candidate enumeration, applied to the whole answer instead of a window.

    Returns (list_or_None, kind_tag). None means the kind is not tokenizable, in which
    case presence falls back to normalized substring containment.
    """
    if kind == "money_usd":
        return parse_moneys(answer), Kind.MONEY_USD
    if kind == "integer":
        return [int(m.group(1)) for m in INT_RE.finditer(answer)], Kind.INTEGER
    if kind == "categorical" and "date" in component_id:
        return _DATE_RE.findall(answer), Kind.CATEGORICAL
    return None, Kind.ENTITY


def present_scalar(kind: str, component_id: str, gold, answer: str):
    """(text_present, n_candidates) for one scalar gold value."""
    cands, tag = candidates(kind, component_id, answer)
    if cands is None:
        g = norm(gold)
        return (bool(g) and g in norm(answer)), None
    eq = {
        Kind.MONEY_USD: match_money_usd,
        Kind.INTEGER: match_integer,
        Kind.CATEGORICAL: match_categorical,
    }[tag]
    hit = False
    for v in cands:
        try:
            if eq(gold, v):
                hit = True
                break
        except Exception:
            continue
    return hit, len(cands)


def present_component(spec: dict, component_id: str, gold, answer: str):
    """(text_present, n_candidates, per_key_detail)."""
    kind = spec["kind"]
    if kind != "state":
        p, n = present_scalar(kind, component_id, gold, answer)
        return p, n, None
    key_kinds = spec.get("key_kinds") or {}
    detail, live = {}, []
    for key, kk in key_kinds.items():
        gv = gold.get(key) if isinstance(gold, dict) else None
        if gv is None:
            detail[key] = {"gold": None, "vacuous": True}
            continue
        p, n = present_scalar(kk, key, gv, answer)
        detail[key] = {"gold": gv, "norm_gold": norm(gv), "text_present": p,
                       "n_candidates": n, "vacuous": False}
        live.append(p)
    if not live:
        return None, None, detail
    return all(live), None, detail


def categorize(extractor_match: bool, text_present: bool, vacuous: bool) -> str:
    if vacuous:
        return "VACUOUS_GOLD"
    if extractor_match and text_present:
        return "MATCH"
    if extractor_match and not text_present:
        return "ANOMALY"
    if text_present:
        return "RECALL_MISS"
    return "ABSENT"


def wilson(k: int, n: int):
    if n == 0:
        return None
    z, p = 1.959963985, k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [max(0.0, c - h), min(1.0, c + h)]


def load_population(a_path: Path, p3_path: Path):
    rows, seen = [], {}
    for path, stratum_of in ((a_path, lambda r: "A"), (p3_path, lambda r: r["stratum"])):
        for line in Path(path).read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            key = (r["lane"], r["task"], r["leg"])
            stratum = stratum_of(r)
            if key in seen:
                raise SystemExit(
                    f"ABORT: leg {key} appears in strata {seen[key]} and {stratum}; "
                    "the four strata are disjoint by construction (spec section 3)"
                )
            seen[key] = stratum
            r["_stratum"] = stratum
            rows.append(r)
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a-legs", default="out/study2_hatd_legs.jsonl")
    ap.add_argument("--p3-legs", default="out/p3_0_extracted.jsonl")
    ap.add_argument("--jsonl", default="out/p3_0_recall_audit.jsonl")
    a = ap.parse_args()

    rows = load_population(Path(a.a_legs), Path(a.p3_legs))
    counts = Counter(r["_stratum"] for r in rows)
    if len(rows) != EXPECTED_LEGS or dict(counts) != EXPECTED_STRATA:
        print("ABORT: population disagrees with spec section 3", file=sys.stderr)
        print(f"  got   {len(rows)} legs {dict(sorted(counts.items()))}", file=sys.stderr)
        print(f"  want  {EXPECTED_LEGS} legs {EXPECTED_STRATA}", file=sys.stderr)
        return 3
    for r in rows:
        if r.get("extractor_sha") not in (None, EXTRACTOR_SHA):
            print(f"ABORT: {r['lane']}/{r['task']}/{r['leg']} carries extractor_sha "
                  f"{r['extractor_sha']}, expected {EXTRACTOR_SHA}", file=sys.stderr)
            return 3
    print(f"population verified: {len(rows)} distinct legs {dict(sorted(counts.items()))}\n")

    lock = load_lock()
    out, drift = [], []

    for r in sorted(rows, key=lambda x: (x["_stratum"], x["lane"], x["task"], x["leg"])):
        task, lane, leg, stratum = r["task"], r["lane"], r["leg"], r["_stratum"]
        specs = lock["components"][task]
        traj = Path(r["traj"]) if r.get("traj") else None
        answer = final_answer_from_traj(traj) if traj and traj.exists() else ""

        # Recompute with the frozen extractor and cross-check the recorded artifact,
        # so a silent change in extractor, lock or archive cannot pass unnoticed.
        # Both artifacts record the guest file; traj is two levels below the leg dir.
        leg_dir = (Path(r["guest"]).parent if r.get("guest")
                   else traj.parents[1] if traj else None)
        rec = extract_leg(task, leg_dir, lock) if leg_dir and leg_dir.exists() else None
        for cid in specs:
            if rec is None:
                drift.append(f"{lane}/{task}/{leg}: leg dir unreadable")
                break
            m = match_one(specs[cid], rec["gold"].get(cid), rec["reported"].get(cid))
            if bool(m) != bool(r["matches"][cid]):
                drift.append(f"{lane}/{task}/{leg}/{cid}: recomputed match {m} "
                             f"!= recorded {r['matches'][cid]}")
            if norm(rec["gold"].get(cid)) != norm(r["gold"].get(cid)):
                drift.append(f"{lane}/{task}/{leg}/{cid}: recomputed gold "
                             f"{rec['gold'].get(cid)!r} != recorded {r['gold'].get(cid)!r}")

        for cid, spec in specs.items():
            gold = (rec["gold"] if rec else r["gold"]).get(cid)
            vac = _is_vacuous(gold)
            if vac:
                tp, nc, detail = None, None, None
            else:
                tp, nc, detail = present_component(spec, cid, gold, answer)
                if tp is None:
                    vac = True
            em = bool(r["matches"][cid])
            out.append({
                "stratum": stratum, "lane": lane, "task": task, "leg": leg,
                "component_id": cid, "kind": spec["kind"],
                "role": spec.get("role", "determining"),
                "gold": gold, "norm_gold": None if vac else norm(gold),
                "reported": (rec["reported"] if rec else r["reported"]).get(cid),
                "extractor_match": em, "text_present": tp,
                "n_candidates": nc, "state_keys": detail,
                "answer_chars": len(answer),
                "score": r.get("score"),
                "valid_done": r.get("valid_done"),
                "category": categorize(em, bool(tp), vac),
            })

    if drift:
        print("ABORT: frozen extractor did not reproduce the recorded artifacts:",
              file=sys.stderr)
        for d in drift[:40]:
            print(f"  - {d}", file=sys.stderr)
        if len(drift) > 40:
            print(f"  ... and {len(drift) - 40} more", file=sys.stderr)
        return 3
    print(f"frozen extractor reproduced all recorded gold/match values on "
          f"{len(rows)} legs\n")

    with open(a.jsonl, "w") as fh:
        for row in out:
            fh.write(json.dumps(row, default=str) + "\n")
    print(f"{len(out)} leg x component rows -> {a.jsonl}\n")

    CATS = ["MATCH", "RECALL_MISS", "ABSENT", "VACUOUS_GOLD", "ANOMALY"]

    def table(title, keyfn, order=None):
        groups = defaultdict(Counter)
        for row in out:
            groups[keyfn(row)][row["category"]] += 1
        keys = order or sorted(groups)
        w = max([len(title)] + [len(str(k)) for k in keys])
        print(f"{title:<{w}} " + " ".join(f"{c:>12s}" for c in CATS) + f"{'n':>6s}")
        print("-" * (w + 13 * len(CATS) + 6))
        for k in keys:
            if k not in groups:
                continue
            g = groups[k]
            print(f"{str(k):<{w}} " + " ".join(f"{g[c]:>12d}" for c in CATS)
                  + f"{sum(g.values()):>6d}")
        print()

    overall = Counter(row["category"] for row in out)
    print("=== category counts, overall")
    for c in CATS:
        print(f"  {c:<14s} {overall[c]:>4d}")
    print()

    print("=== by stratum")
    table("stratum", lambda r: r["stratum"],
          ["A", "gate0", "dissoc_nondone", "unmatched_nondone"])
    print("=== by component kind")
    table("kind", lambda r: r["kind"])
    print("=== by task")
    table("task", lambda r: r["task"])

    if overall["ANOMALY"]:
        NUMERIC = {"money_usd", "integer"}
        anom = [r for r in out if r["category"] == "ANOMALY"]
        print("=== ANOMALY rows: self-check on R1, not findings (spec section 5.1)\n")
        num = [r for r in anom if r["kind"] in NUMERIC]
        ent = [r for r in anom if r["kind"] not in NUMERIC]
        if num:
            print(f"  (a) window-boundary lookbehind, {len(num)} row(s). Expected "
                  "mechanism, kind NOT voided;")
            print("      already outside the recall-miss numerator and denominator.")
            for r in num:
                print(f"      {r['lane']}/{r['task']}/{r['leg']}/{r['component_id']} "
                      f"[{r['kind']}] gold={r['gold']!r} reported={r['reported']!r}")
            print()
        if ent:
            print(f"  (b) RULE FAILURE on entity/categorical, {len(ent)} row(s). R1 is "
                  "inadequate for these")
            print("      kinds and their recall numbers are VOID. R1 must not be patched.")
            for r in ent:
                print(f"      {r['lane']}/{r['task']}/{r['leg']}/{r['component_id']} "
                      f"[{r['kind']}] gold={r['gold']!r} reported={r['reported']!r}")
            print(f"      VOID kinds: {sorted({r['kind'] for r in ent})}")
            print()

    print("=== primary quantity: recall-miss share of non-matches")
    print("    RECALL_MISS / (RECALL_MISS + ABSENT), Wilson 95%\n")
    print(f"{'population':<22s} {'miss':>5s} {'absent':>7s} {'share':>8s}   95% CI")
    print("-" * 62)
    for label, pred in (
        ("A (valid pairs)", lambda r: r["stratum"] == "A"),
        ("outside A (21 legs)", lambda r: r["stratum"] != "A"),
        ("all 57 legs", lambda r: True),
    ):
        sub = [r for r in out if pred(r)]
        k = sum(1 for r in sub if r["category"] == "RECALL_MISS")
        n0 = sum(1 for r in sub if r["category"] == "ABSENT")
        ci = wilson(k, k + n0)
        share = f"{k / (k + n0):.3f}" if k + n0 else "n/a"
        cis = f"[{ci[0]:.3f}, {ci[1]:.3f}]" if ci else "n/a"
        print(f"{label:<22s} {k:>5d} {n0:>7d} {share:>8s}   {cis}")
    print()

    print("=== n_candidates distribution, and category by candidate multiplicity")
    print("    (spec section 2 coincidence hazard: presence among many candidates is weak)\n")
    buckets = defaultdict(Counter)
    for row in out:
        nc = row["n_candidates"]
        b = "not tokenizable" if nc is None else (
            "0" if nc == 0 else "1" if nc == 1 else "2-5" if nc <= 5
            else "6-20" if nc <= 20 else ">20")
        buckets[b][row["category"]] += 1
    order = ["0", "1", "2-5", "6-20", ">20", "not tokenizable"]
    w = max(len("n_candidates"), *(len(o) for o in order))
    print(f"{'n_candidates':<{w}} " + " ".join(f"{c:>12s}" for c in CATS) + f"{'n':>6s}")
    print("-" * (w + 13 * len(CATS) + 6))
    for b in order:
        if b not in buckets:
            continue
        g = buckets[b]
        print(f"{b:<{w}} " + " ".join(f"{g[c]:>12d}" for c in CATS)
              + f"{sum(g.values()):>6d}")
    print()

    print("=== legs where the two explanations diverge (spec section 6.5)")
    print("    high-score or long-answer legs whose frozen match count is zero\n")
    legs = defaultdict(list)
    for row in out:
        legs[(row["stratum"], row["lane"], row["task"], row["leg"])].append(row)
    hdr = (f"{'stratum':<18s} {'lane':<7s} {'task':<26s} {'leg':<4s} {'S':>5s} "
           f"{'ans_ch':>7s} {'match':>6s} {'present':>8s} {'miss':>5s} {'absent':>7s}")
    print(hdr)
    print("-" * len(hdr))
    for key in sorted(legs):
        rs = legs[key]
        nm = sum(1 for r in rs if r["category"] == "MATCH")
        if nm:
            continue
        live = [r for r in rs if r["category"] != "VACUOUS_GOLD"]
        if not live:
            continue
        s, lane, task, leg = key
        sc = rs[0]["score"]
        print(f"{s:<18s} {lane:<7s} {task:<26s} {leg:<4s} "
              f"{('-' if sc is None else int(sc)):>5} {rs[0]['answer_chars']:>7d} "
              f"{nm:>6d} {sum(1 for r in live if r['text_present']):>8d} "
              f"{sum(1 for r in live if r['category'] == 'RECALL_MISS'):>5d} "
              f"{sum(1 for r in live if r['category'] == 'ABSENT'):>7d}")
    print()

    print("=== every RECALL_MISS row (value is in the text, extractor did not reach it)\n")
    miss = [r for r in out if r["category"] == "RECALL_MISS"]
    if not miss:
        print("  none\n")
    else:
        hdr = (f"{'stratum':<18s} {'lane':<7s} {'task':<26s} {'leg':<4s} "
               f"{'component':<28s} {'kind':<11s} {'cand':>5s} gold")
        print(hdr)
        print("-" * len(hdr))
        for r in miss:
            print(f"{r['stratum']:<18s} {r['lane']:<7s} {r['task']:<26s} {r['leg']:<4s} "
                  f"{r['component_id']:<28s} {r['kind']:<11s} "
                  f"{('-' if r['n_candidates'] is None else r['n_candidates']):>5} "
                  f"{r['gold']!r}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
