#!/usr/bin/env python3
"""P3-2 G2: does R reconstruct the frozen FROZEN result on Study 2?

Study 2 only. Does not open the sealed transcription, does not read validation
answer text, does not modify R, does not pick a label from any audit.

    selftest → pre-replay gates → materialise R on Study 2 → escape
            → replace LABELS → FROZEN replay on the 134 → compare → stop

G2 FAIL is a verdict. It is not a reason to edit R.
"""
from __future__ import annotations

import ast
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import p3_2_r as R  # noqa: E402
import p3_1_repair as p31  # noqa: E402
import study2_hatd_extract as ex  # noqa: E402

TASKS = ROOT / "external" / "MyPCBench-main" / "tasks" / "final" / "all_tasks_with_grading.json"
LOCK = ROOT / "out" / "study2_gold_path_lock.json"
R_PATH = ROOT / "scripts" / "p3_2_r.py"
SELF_PATH = Path(__file__).resolve()

# Published FROZEN row of A-10 (P3-1). Counts, not intervals.
A10_FROZEN = {"sensitivity": (20, 59), "abstention": (89, 134), "confident_wrong": (25, 45)}

# Ban the on-disk name of the other corpus, constructed so the check does not
# trip over itself.
def _other_corpus_file() -> str:
    return "P3_1_" + "SEALED_TRANSCRIPTION.json"


def r_blob() -> str:
    return p31.git_blob(R_PATH)


def string_literals(path: Path) -> list[str]:
    tree = ast.parse(path.read_text())
    return [n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def g1b_hits() -> list[str]:
    tasks = {t["id"] for t in json.loads(TASKS.read_text())}
    lock = json.loads(LOCK.read_text())
    ids = set(tasks)
    ids |= set(lock["components"])
    ids |= {c for cs in lock["components"].values() for c in cs}
    return [lit for lit in string_literals(R_PATH) if lit in ids]


def live_components(lock: dict) -> list[tuple[str, str]]:
    return [(t, c) for t, cs in lock["components"].items()
            for c, s in cs.items() if s["kind"] != "state"]


def materialise(lock: dict, tasks: dict) -> dict[tuple[str, str], list[str]]:
    table = {}
    for task, cid in live_components(lock):
        t = tasks[task]
        table[(task, cid)] = R.escaped_labels(t.get("instruction"), t.get("grading"), cid)
    return table


def inject(table: dict) -> None:
    ex.LABELS.clear()
    ex.LABELS.update(table)


def r_is_dirty() -> str | None:
    out = subprocess.run(
        ["git", "status", "--porcelain", "--", str(R_PATH.relative_to(ROOT))],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    if out.returncode != 0:
        return f"git status failed: {out.stderr.strip()}"
    if out.stdout.strip():
        return f"uncommitted edits in {R_PATH.name}: {out.stdout.strip()!r}"
    return None


def recategorize(row: dict, matched: bool) -> str:
    vac = row["category"] == "VACUOUS_GOLD" or row.get("gold") is None
    tp = bool(row.get("text_present"))
    if vac:
        return "VACUOUS_GOLD"
    if matched and tp:
        return "MATCH"
    if matched and not tp:
        return "ANOMALY"
    if tp:
        return "RECALL_MISS"
    return "ABSENT"


def fmt_shortfall(failed: list[tuple[str, int, int]]) -> str:
    n = len(failed)
    lines = [f"G2 FAIL — {n} component{'s' if n != 1 else ''} not reconstructed"]
    for key, n_diff, n_rows in failed:
        lines.append(f"  {key}  {n_diff}/{n_rows} rows differ")
    return "\n".join(lines)


def selftest() -> int:
    bad: list[str] = []
    src = SELF_PATH.read_text()
    other = _other_corpus_file()
    if other in src:
        bad.append(f"runner source names {other}")

    got = R.derive_labels("Report the alpha beta figure.", "", "alpha_beta")
    if got != ["alpha", "beta", "alpha beta"]:
        bad.append(f"R fixture drifted: {got}")
    if g1b_hits():
        bad.append(f"G1b literals in R: {g1b_hits()}")

    # Injection is a total replace: leftover frozen keys are a gate fail.
    saved = dict(ex.LABELS)
    fake = {("synth", "alpha_beta"): R.escaped_labels("the alpha beta total", "", "alpha_beta")}
    try:
        inject(fake)
        if set(ex.LABELS) != set(fake):
            bad.append(f"inject left extra keys: {set(ex.LABELS) - set(fake)}")
        if ex.LABELS[("synth", "alpha_beta")] != fake[("synth", "alpha_beta")]:
            bad.append("inject did not store R's escaped labels")
        got_m = ex.extract_money("the alpha beta is $12.00", ex.LABELS[("synth", "alpha_beta")])
        if got_m is None or str(got_m) != "12.00":
            bad.append(f"injected extract missed: {got_m}")
    finally:
        inject(saved)

    msg = fmt_shortfall([("alpha/beta", 2, 4), ("gamma/delta", 1, 1)])
    if not msg.startswith("G2 FAIL — 2 components not reconstructed"):
        bad.append(f"shortfall banner: {msg!r}")
    if "do not" in msg.lower() or "try" in msg.lower() or "variant" in msg.lower():
        bad.append("shortfall text must not suggest a fix")

    print(f"R blob {r_blob()}")
    if bad:
        print("selftest FAIL")
        for b in bad:
            print(f"  {b}")
        return 4
    print("selftest PASS")
    print("  runner does not name the sealed corpus")
    print("  R fixtures and G1b hold")
    print("  inject replaces LABELS entirely with R's escaped output")
    print("  shortfall banner names a count, not a repair")
    return 0


def pre_replay(lock: dict, tasks: dict, table: dict) -> list[str]:
    bad = []
    dirty = r_is_dirty()
    if dirty:
        bad.append(dirty)
    try:
        p31.check_provenance()
    except SystemExit:
        bad.append("frozen extractor/apply/classifier blob mismatch")
    live = live_components(lock)
    if len(live) != 30:
        bad.append(f"{len(live)} live components, expected 30")
    if set(table) != set(live):
        bad.append("materialised keys != 30 live components")
    hits = g1b_hits()
    if hits:
        bad.append(f"G1b fail after materialisation: {hits}")
    for key, labs in table.items():
        task, cid = key
        t = tasks[task]
        want = R.escaped_labels(t.get("instruction"), t.get("grading"), cid)
        if labs != want:
            bad.append(f"{task}/{cid}: table != R.escaped_labels")
        for raw, esc in zip(R.derive_labels(t.get("instruction"), t.get("grading"), cid), labs):
            if esc != __import__("re").escape(raw):
                bad.append(f"{task}/{cid}: not an escaped literal")
    return bad


def cmd_run(audit: Path, a_legs: Path, p3_legs: Path) -> int:
    print(f"R blob {r_blob()}  ({R_PATH.relative_to(ROOT)})")
    print("G2 uses this blob. A different file is a different experiment.")

    tasks = {t["id"]: t for t in json.loads(TASKS.read_text())}
    lock = json.loads(LOCK.read_text())
    table = materialise(lock, tasks)

    gates = pre_replay(lock, tasks, table)
    if gates:
        print("ABORT: pre-replay gate failed. This is not a G2 verdict.", file=sys.stderr)
        for g in gates:
            print(f"  - {g}", file=sys.stderr)
        return 2

    pop = p31.load_population(audit, a_legs, p3_legs)
    if pop is None:
        return 3
    rows, answers, guests, _lock = pop
    live = set(live_components(lock))
    row_comps = {(r["task"], r["component_id"]) for r in rows
                 if (r["task"], r["component_id"]) in live}
    print(f"pre-replay PASS          : R clean, 30 components, "
          f"{len(table)} injected, G1b hold")
    print(f"                         : {len(row_comps)} of 30 appear in the 134")

    inject(table)
    extra = set(ex.LABELS) - set(table)
    missing = set(table) - set(ex.LABELS)
    if extra or missing:
        print(f"ABORT: LABELS after inject extra={extra} missing={missing}",
              file=sys.stderr)
        return 2
    print("LABELS is exactly R     : 30 keys, no leftover frozen patterns")

    results = {}
    cats = {k: 0 for k in p31.BASELINE_CATEGORIES}
    per_comp: dict[str, list[bool]] = defaultdict(list)
    for r in rows:
        key = (r["lane"], r["task"], r["leg"], r["component_id"])
        spec = lock["components"][r["task"]][r["component_id"]]
        gold = ex.gold_for_component(guests[(r["lane"], r["task"], r["leg"])],
                                     r["task"], r["component_id"], lock)
        ev = p31.evaluate(r, spec, gold, answers[(r["lane"], r["task"], r["leg"])], set())
        results[key] = ev
        cats[recategorize(r, ev["matched"])] += 1
        ck = f"{r['task']}/{r['component_id']}"
        if (r["task"], r["component_id"]) in live:
            same = (p31._j(ex._jsonable(ev["reported"])) == p31._j(r["reported"])
                    and ev["matched"] == bool(r["extractor_match"]))
            per_comp[ck].append(same)

    failed = []
    for ck in sorted(per_comp):
        flags = per_comp[ck]
        n_diff = sum(1 for s in flags if not s)
        if n_diff:
            failed.append((ck, n_diff, len(flags)))

    print(f"\nFROZEN replay            : {len(rows)} rows")
    cat_diff = p31.category_diff(cats, p31.BASELINE_CATEGORIES)
    print(f"134-row categorisation   : {dict(sorted(cats.items()))}")
    if cat_diff:
        print("  differs from frozen    : "
              + ", ".join(f"{k} {o} vs {f}" for k, o, f in cat_diff))
    else:
        print("  matches frozen 20/39/61/14/0")

    tax = p31.taxonomy_of(results, rows)
    tdiff = []
    for cat, want in p31.FROZEN_TAXONOMY.items():
        got = tax.get(cat, {})
        for k, n in want.items():
            if got.get(k, 0) != n:
                tdiff.append(f"{cat}/{k}: {got.get(k, 0)} != published {n}")
    print("cause taxonomy           : "
          f"RECALL_MISS {dict(sorted(tax.get('RECALL_MISS', {}).items()))}")
    print("                         : "
          f"ABSENT {dict(sorted(tax.get('ABSENT', {}).items()))}")
    if tdiff:
        print("  differs from 0.7       : " + "; ".join(tdiff))

    r1 = [r for r in rows if r["category"] in ("MATCH", "RECALL_MISS")]
    abst = sum(1 for e in results.values() if e["reported"] is None)
    m4 = sum(1 for e in results.values() if e["reported"] is not None and not e["matched"])
    sens = sum(1 for r in r1
               if results[(r["lane"], r["task"], r["leg"], r["component_id"])]["matched"])
    a10 = {"sensitivity": (sens, len(r1)),
           "abstention": (abst, len(rows)),
           "confident_wrong": (m4, len(rows) - abst)}
    print(f"A-10 FROZEN              : sens {sens}/{len(r1)}  "
          f"abstain {abst}/{len(rows)}  conf-wrong {m4}/{len(rows) - abst}")
    a10_diff = [k for k in A10_FROZEN if a10[k] != A10_FROZEN[k]]
    if a10_diff:
        print("  differs from published : "
              + ", ".join(f"{k} {a10[k]} vs {A10_FROZEN[k]}" for k in a10_diff))

    print()
    if failed or cat_diff or tdiff or a10_diff:
        print(fmt_shortfall(failed))
        print(f"reconstructed {30 - len(failed)}/30")
        print("G2 is not a loop. R is not revised.")
        return 5
    print("G2 PASS — 30/30 components reconstructed")
    print("134-row categorisation, 0.7 taxonomy, and A-10 FROZEN row match.")
    return 0


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["selftest", "run"])
    ap.add_argument("--audit", default="out/p3_0_recall_audit.jsonl")
    ap.add_argument("--a-legs", default="out/study2_hatd_legs.jsonl")
    ap.add_argument("--p3-legs", default="out/p3_0_extracted.jsonl")
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    return cmd_run(Path(a.audit), Path(a.a_legs), Path(a.p3_legs))


if __name__ == "__main__":
    raise SystemExit(main())
