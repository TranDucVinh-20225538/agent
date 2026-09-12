#!/usr/bin/env python3
"""Set-valued reachability on the two singleton-UNREACHABLE calibration components.

§12.8 showed that no single grounded span reproduces the frozen extraction for
`contradiction-f006/credit_headroom` and `preference_inference-f014/designated_booking_total`,
and that each frozen list contains one load-bearing ungrounded synonym. That is not a
proof that no grounded *set* can. This audit asks that question at set size 2 — the
frozen cardinality of both lists, and the smallest step beyond the singleton audit.

Two parts, in order, both read-only:

  1. Decomposition. Per leg: frozen set, each frozen label alone, grounded-only subset.
  2. Pair exhaustion. Every size-2 set of grounded literal spans, as a label set.

Not calibration: declares no parameter, produces no R. A surviving pair may not be
adopted as a label (G1b). Writes nothing.

UNREACHABLE here means unreachable at size ≤ 2. It must not be printed as G2 being
unattainable by any grounded rule.
"""
from __future__ import annotations

import json
import re
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
TASKS = ROOT / "external" / "MyPCBench-main" / "tasks" / "final" / "all_tasks_with_grading.json"
LOCK = ROOT / "out" / "study2_gold_path_lock.json"
A_LEGS = ROOT / "out" / "study2_hatd_legs.jsonl"
P3_LEGS = ROOT / "out" / "p3_0_extracted.jsonl"

TARGETS = [
    ("contradiction-f006", "credit_headroom"),
    ("preference_inference-f014", "designated_booking_total"),
]
MAX_WORDS = 6
TOKEN = re.compile(r"[A-Za-z0-9$][A-Za-z0-9$.,'%/-]*")


def task_side_text(t: dict) -> str:
    g = t.get("grading")
    return " ".join([t.get("instruction") or "",
                     g if isinstance(g, str) else json.dumps(g, ensure_ascii=False)])


def grounded_spans(text: str, max_words: int = MAX_WORDS) -> list[str]:
    toks = list(TOKEN.finditer(text))
    out, seen = [], set()
    for i in range(len(toks)):
        for n in range(1, max_words + 1):
            if i + n > len(toks):
                break
            s = text[toks[i].start():toks[i + n - 1].end()]
            k = s.casefold()
            if k not in seen:
                seen.add(k)
                out.append(s)
    return out


def label_grounded(pat: str, text: str) -> bool:
    try:
        return re.search(pat, text, re.IGNORECASE) is not None and ".*" not in pat
    except re.error:
        return False


def money_hits(ex, text: str, lab: str) -> list:
    found = []
    for m in re.finditer(lab, text, re.IGNORECASE):
        after = text[m.end(): m.end() + 100]
        after = re.split(r"\n\s*Breakdown", after, maxsplit=1, flags=re.I)[0]
        ms = ex.parse_moneys(after)
        if ms:
            found.append(ms[0])
    return found


def main() -> int:
    import study2_hatd_extract as ex

    tasks = {t["id"]: t for t in json.loads(TASKS.read_text())}
    lock = json.loads(LOCK.read_text())

    legs: dict[str, list[tuple[str, str, str]]] = {}
    for p in (A_LEGS, P3_LEGS):
        if not p.exists():
            print(f"ABORT: {p} not found; this audit must run where the archive lives.",
                  file=sys.stderr)
            return 3
        for line in p.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            legs.setdefault(r["task"], []).append((r["lane"], r["leg"], r.get("traj")))

    verdicts = {}
    for task, cid in TARGETS:
        kind = lock["components"][task][cid]["kind"]
        if kind != "money_usd":
            print(f"ABORT: {task}/{cid} kind={kind}; this audit is money-only.",
                  file=sys.stderr)
            return 3
        frozen_pats = ex.LABELS[(task, cid)]
        side = task_side_text(tasks[task])
        answers = []
        for lane, leg, traj in legs.get(task, []):
            if not traj or not Path(traj).exists():
                print(f"  NOTE {task}/{cid}: leg {lane}/{leg} has no readable traj")
                continue
            answers.append((f"{lane}/{leg}", ex.final_answer_from_traj(Path(traj))))
        if not answers:
            print(f"{task}/{cid}: no readable legs")
            verdicts[f"{task}/{cid}"] = "UNDECIDED"
            continue

        print(f"\n{'=' * 72}")
        print(f"{task}/{cid}  kind={kind}  legs={len(answers)}")
        print(f"  frozen labels: {frozen_pats}")
        gflags = []
        for p in frozen_pats:
            g = label_grounded(p, side)
            gflags.append(g)
            print(f"    {p!r:24s}  {'GROUNDED' if g else 'NOT IN TASK TEXT'}")
        grounded_subset = [p for p, g in zip(frozen_pats, gflags) if g]

        print("  decomposition (per leg):")
        print(f"    {'leg':16s} {'frozen':>12s}  " +
              "  ".join(f"{p!r:>16s}" for p in frozen_pats) +
              f"  {'grounded-subset':>16s}")
        frozen_vals = {}
        n_subset_match = 0
        for tag, a in answers:
            fv = ex.extract_money(a, frozen_pats)
            frozen_vals[tag] = fv
            alones = [ex.extract_money(a, [p]) for p in frozen_pats]
            sub = ex.extract_money(a, grounded_subset) if grounded_subset else None
            if sub == fv:
                n_subset_match += 1
            def fmt(v):
                return "None" if v is None else str(v)
            print(f"    {tag:16s} {fmt(fv):>12s}  " +
                  "  ".join(f"{fmt(v):>16s}" for v in alones) +
                  f"  {fmt(sub):>16s}")
        subset_ok = n_subset_match == len(answers)
        print(f"  grounded-subset reproduces frozen vector: "
              f"{'YES' if subset_ok else 'NO'} "
              f"({n_subset_match}/{len(answers)} legs)")
        print("    (YES would mean the ungrounded synonym is not load-bearing; "
              "§12.8 inferred NO from the singleton audit)")

        if subset_ok:
            print("  REACHABLE at size ≤ 2 via the grounded-only frozen subset")
            print("    (reachability only; adopting that subset as a label is G1b-forbidden)")
            verdicts[f"{task}/{cid}"] = "REACHABLE"
            continue

        cands = grounded_spans(side)
        # Precompute per-span money hits so a pair is unique_or_none of concatenated hits,
        # which is exactly extract_money on the two-label set.
        hits = {s: [money_hits(ex, a, re.escape(s)) for _, a in answers] for s in cands}
        target = [frozen_vals[tag] for tag, _ in answers]
        survivors = []
        n_pairs = 0
        for s1, s2 in combinations(cands, 2):
            n_pairs += 1
            ok = True
            for i in range(len(answers)):
                if ex._unique_or_none(hits[s1][i] + hits[s2][i]) != target[i]:
                    ok = False
                    break
            if ok:
                survivors.append((s1, s2))
        print(f"  grounded pairs tested: {n_pairs} "
              f"(C({len(cands)},2), spans ≤ {MAX_WORDS} tokens)")
        if survivors:
            print(f"  REACHABLE at size 2: {len(survivors)} pair(s) reproduce the "
                  f"frozen vector on every leg")
            print(f"    e.g. {survivors[:3]}")
            print("    (reachability only; adopting a pair as a label is G1b-forbidden)")
            verdicts[f"{task}/{cid}"] = "REACHABLE"
        else:
            print("  UNREACHABLE at size ≤ 2: no grounded singleton or pair reproduces "
                  "the frozen vector")
            verdicts[f"{task}/{cid}"] = "UNREACHABLE"

    print("\n" + "=" * 72)
    for k, v in verdicts.items():
        print(f"  {k:52s} {v}")
    n_u = sum(1 for v in verdicts.values() if v == "UNREACHABLE")
    n_r = sum(1 for v in verdicts.values() if v == "REACHABLE")
    n_d = sum(1 for v in verdicts.values() if v == "UNDECIDED")
    print(f"\nreachable {n_r}  unreachable-at-2 {n_u}  undecided {n_d}")
    if n_d:
        print("\nIncomplete: at least one component could not be decided.")
        return 4
    if n_u:
        print("\nNo grounded singleton or pair reproduces the frozen vector on "
              f"{n_u} component(s). That is UNREACHABLE at size ≤ 2, not a proof "
              "that no finite grounded set can, and not a restatement of G2.")
        return 5
    print("\nBoth components are reachable by a grounded set of size ≤ 2, so G2 "
          "at 30/30 remains attainable in principle by a multi-label rule.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
