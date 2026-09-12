#!/usr/bin/env python3
"""Where G2's difficulty concentrates, across all 30 calibration components.

Stage 2 asked whether G1 and G2 contradict on the four components whose frozen labels
are not groundable. They do not. This asks a different question, still before `R`
exists: *where* does G2 actually constrain a grounded rule?

For each of the 30 label-sensitive Study 2 components it reports two numbers:

  constraint weight  — how many calibration legs have a non-None frozen extraction
  selectivity        — how many grounded literal spans reproduce that frozen vector

A component valued on many legs with few surviving spans is where G2's difficulty
concentrates. A component that is None everywhere is VACUOUS. UNREACHABLE on any of
the 30 would be a protocol contradiction stage 2 could not have seen.

Not calibration: declares no parameter, produces no R. A surviving span may not be
adopted as a label — that is G1b. Reads Study 2 only. Writes nothing.
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

MAX_WORDS = 6
TOKEN = re.compile(r"[A-Za-z0-9$][A-Za-z0-9$.,'%/-]*")


def task_side_text(t: dict) -> str:
    g = t.get("grading")
    return " ".join([t.get("instruction") or "",
                     g if isinstance(g, str) else json.dumps(g, ensure_ascii=False)])


def grounded_spans(text: str, max_words: int = MAX_WORDS) -> list[str]:
    """Every literal substring spanning 1..max_words whole tokens, deduplicated."""
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
    live = [(t, c, s["kind"])
            for t, cs in lock["components"].items()
            for c, s in cs.items()
            if s["kind"] != "state"]

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

    rows = []
    for task, cid, kind in live:
        fn = extractors[kind]
        frozen_pats = ex.LABELS.get((task, cid), [])
        answers = []
        for lane, leg, traj in legs.get(task, []):
            if not traj or not Path(traj).exists():
                print(f"  NOTE {task}/{cid}: leg {lane}/{leg} has no readable traj")
                continue
            answers.append((f"{lane}/{leg}", ex.final_answer_from_traj(Path(traj))))
        key = f"{task}/{cid}"
        if not answers:
            print(f"{key}: no readable legs; cannot decide")
            rows.append({"key": key, "kind": kind, "verdict": "UNDECIDED",
                         "n_legs": 0, "n_valued": 0, "n_cands": 0, "n_surv": 0,
                         "examples": []})
            continue

        frozen_vals = {tag: fn(a, frozen_pats) for tag, a in answers}
        n_valued = sum(v is not None for v in frozen_vals.values())
        if n_valued == 0:
            rows.append({"key": key, "kind": kind, "verdict": "VACUOUS",
                         "n_legs": len(answers), "n_valued": 0, "n_cands": 0,
                         "n_surv": 0, "examples": []})
            continue

        if task not in tasks:
            print(f"  NOTE {key}: task absent from task file")
            rows.append({"key": key, "kind": kind, "verdict": "UNDECIDED",
                         "n_legs": len(answers), "n_valued": n_valued,
                         "n_cands": 0, "n_surv": 0, "examples": []})
            continue

        cands = grounded_spans(task_side_text(tasks[task]))
        survivors = []
        for s in cands:
            pat = [re.escape(s)]
            if all(fn(a, pat) == frozen_vals[tag] for tag, a in answers):
                survivors.append(s)
        verdict = "REACHABLE" if survivors else "UNREACHABLE"
        rows.append({"key": key, "kind": kind, "verdict": verdict,
                     "n_legs": len(answers), "n_valued": n_valued,
                     "n_cands": len(cands), "n_surv": len(survivors),
                     "examples": survivors[:2]})

    # Sort so concentration is visible: valued first, then fewest survivors.
    order = {"UNREACHABLE": 0, "REACHABLE": 1, "VACUOUS": 2, "UNDECIDED": 3}
    rows.sort(key=lambda r: (order[r["verdict"]], -r["n_valued"], r["n_surv"], r["key"]))

    print(f"{'component':44s} {'kind':12s} {'verdict':12s} "
          f"{'legs':>4s} {'val':>4s} {'cand':>5s} {'surv':>5s}  examples")
    print("-" * 110)
    for r in rows:
        exs = ", ".join(repr(s) for s in r["examples"])
        print(f"{r['key']:44s} {r['kind']:12s} {r['verdict']:12s} "
              f"{r['n_legs']:4d} {r['n_valued']:4d} {r['n_cands']:5d} {r['n_surv']:5d}  "
              f"{exs}")
        if r["verdict"] == "REACHABLE":
            print("    (reachability only; adopting a survivor as a label is G1b-forbidden)")

    n = {v: sum(1 for r in rows if r["verdict"] == v)
         for v in ("REACHABLE", "VACUOUS", "UNREACHABLE", "UNDECIDED")}
    valued = [r for r in rows if r["n_valued"] > 0]
    print(f"\nreachable {n['REACHABLE']}  vacuous {n['VACUOUS']}  "
          f"unreachable {n['UNREACHABLE']}  undecided {n['UNDECIDED']}")
    print(f"valued-on-at-least-one-leg: {len(valued)}/{len(rows)}")
    if valued:
        tight = sorted(valued, key=lambda r: (r["n_surv"], -r["n_valued"]))
        print("tightest valued (fewest survivors, then most valued legs):")
        for r in tight[:8]:
            rate = (100.0 * r["n_surv"] / r["n_cands"]) if r["n_cands"] else 0.0
            print(f"  {r['key']:44s} valued={r['n_valued']}/{r['n_legs']}  "
                  f"surv={r['n_surv']}/{r['n_cands']} ({rate:.2f}%)")

    if n["UNREACHABLE"]:
        print(f"\nG1 and G2 are genuinely INCOMPATIBLE on {n['UNREACHABLE']} "
              f"component(s). G2 at 30/30 is unattainable by any grounded rule.")
        return 5
    if n["UNDECIDED"]:
        print("\nIncomplete: at least one component could not be decided.")
        return 4
    print("\nNo contradiction across the 30. Concentration is the ranking above, "
          "not a restated gate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
