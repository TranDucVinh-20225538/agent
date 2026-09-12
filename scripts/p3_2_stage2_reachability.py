#!/usr/bin/env python3
"""Stage-2 audit: is the frozen extraction behaviour *reachable* by a grounded label?

Stage 1 showed that for four calibration components no frozen label occurs in the task's
own `instruction`/`grading`, so G2 cannot be met by reproducing those labels. It left open
whether some *other* task-side-grounded phrase selects the same extracted value, which is
what G2 actually compares.

This settles that by exhaustion rather than by cleverness. For each of the four it
enumerates **every** literal substring of the task-side text up to `MAX_WORDS` tokens, and
asks whether any of them, used as the sole label, reproduces the frozen extracted value on
every calibration leg of that task. Being exhaustive is the point: if no grounded span
works, no grounded rule can work, however it is written.

Two things this audit is NOT. It is not calibration: it declares no parameter and produces
no `R`. And a surviving span may **not** then be adopted as a label — that would be
hand-authoring by search, exactly what G1b forbids. The only output is reachability.

Reads Study 2 answer text, which is the calibration corpus and is permitted. Reads no
validation answer text, no gold lock path beyond component kinds, and writes no result
used by any measurement.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
TASKS = ROOT / "external" / "MyPCBench-main" / "tasks" / "final" / "all_tasks_with_grading.json"
LOCK = ROOT / "out" / "study2_gold_path_lock.json"
A_LEGS = ROOT / "out" / "study2_hatd_legs.jsonl"
P3_LEGS = ROOT / "out" / "p3_0_extracted.jsonl"

# The four components stage 1 flagged. Named explicitly because this audit is about exactly
# them; it is a diagnostic, not part of any instrument.
TARGETS = [
    ("aggregation-f037", "top_sender"),
    ("aggregation-f037", "top_sender_count"),
    ("contradiction-f004", "batbucks_gme_shares"),
    ("counterfactual-f005", "gme_avg_cost"),
]
MAX_WORDS = 6  # generous on purpose: a negative result at 6 is stronger than at 2
TOKEN = re.compile(r"[A-Za-z0-9$][A-Za-z0-9$.,'%/-]*")


def task_side_text(t: dict) -> str:
    g = t.get("grading")
    return " ".join([t.get("instruction") or "",
                     g if isinstance(g, str) else json.dumps(g, ensure_ascii=False)])


def grounded_spans(text: str, max_words: int = MAX_WORDS) -> list[str]:
    """Every literal substring spanning 1..max_words whole tokens, deduplicated.

    Taken from the original text by offset so each candidate is a literal substring by
    construction and therefore G1-compliant without further checking.
    """
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

    extractors = {"money_usd": ex.extract_money, "integer": ex.extract_int,
                  "entity": ex.extract_entity, "categorical": ex.extract_date}
    verdicts = {}

    for task, cid in TARGETS:
        kind = lock["components"][task][cid]["kind"]
        fn = extractors[kind]
        frozen_pats = ex.LABELS.get((task, cid), [])
        rows = legs.get(task, [])
        answers = []
        for lane, leg, traj in rows:
            if not traj or not Path(traj).exists():
                print(f"  NOTE {task}/{cid}: leg {lane}/{leg} has no readable traj")
                continue
            answers.append((f"{lane}/{leg}", ex.final_answer_from_traj(Path(traj))))
        if not answers:
            print(f"{task}/{cid}: no readable legs; cannot decide")
            verdicts[f"{task}/{cid}"] = "UNDECIDED"
            continue

        frozen_vals = {tag: fn(a, frozen_pats) for tag, a in answers}
        print(f"\n{task}/{cid}  kind={kind}  legs={len(answers)}")
        print(f"  frozen labels   : {frozen_pats}")
        print(f"  frozen extracts : {[(t, str(v)) for t, v in frozen_vals.items()]}")

        if all(v is None for v in frozen_vals.values()):
            # Then the frozen label contributes nothing to the taxonomy on this corpus and
            # G2 is satisfied for this component by any label that also extracts nothing.
            # The stage-1 obstruction would be vacuous.
            print("  VACUOUS: the frozen label extracts nothing on every leg, so this "
                  "component\n           constrains G2 only to also extract nothing.")
            verdicts[f"{task}/{cid}"] = "VACUOUS"
            continue

        cands = grounded_spans(task_side_text(tasks[task]))
        survivors = []
        for s in cands:
            pat = [re.escape(s)]
            if all(fn(a, pat) == frozen_vals[tag] for tag, a in answers):
                survivors.append(s)
        print(f"  grounded candidates tested: {len(cands)} (<= {MAX_WORDS} tokens)")
        if survivors:
            print(f"  REACHABLE: {len(survivors)} grounded span(s) reproduce the frozen "
                  f"value on every leg")
            print(f"    e.g. {[s for s in survivors[:5]]}")
            print("    (recorded as reachability only; adopting one as a label would be "
                  "hand-authoring by search and is forbidden by G1b)")
            verdicts[f"{task}/{cid}"] = "REACHABLE"
        else:
            print("  UNREACHABLE: no grounded span of the task definition reproduces the "
                  "frozen\n               extracted value. No grounded rule can, however "
                  "written.")
            verdicts[f"{task}/{cid}"] = "UNREACHABLE"

    print("\n" + "=" * 72)
    for k, v in verdicts.items():
        print(f"  {k:44s} {v}")
    unreach = [k for k, v in verdicts.items() if v == "UNREACHABLE"]
    vac = [k for k, v in verdicts.items() if v == "VACUOUS"]
    reach = [k for k, v in verdicts.items() if v == "REACHABLE"]
    print(f"\nreachable {len(reach)}  vacuous {len(vac)}  unreachable {len(unreach)}")
    if unreach:
        print(f"\nG1 and G2 are genuinely INCOMPATIBLE on {len(unreach)} component(s). "
              f"G2 at 30/30 is\nunattainable by any grounded rule, and that is a protocol "
              f"contradiction to be\nresolved by amendment, not by weakening a gate "
              f"quietly.")
        return 5
    print("\nNo contradiction: every flagged component is reachable or vacuous, so G2 at "
          "30/30\nremains attainable in principle by a grounded rule.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
