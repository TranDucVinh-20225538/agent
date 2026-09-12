#!/usr/bin/env python3
"""P4 Phase-2 gold-lock from task-side specification only.

No guest probe. No agents. No observations. No p4_instrument.py edits.
Slate is the frozen leftover 11. Clusters are not added or dropped for usefulness.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P4 = Path(__file__).resolve().parents[1]
INSTR = Path(__file__).resolve().parent / "p4_instrument.py"
TASKS = ROOT / "external" / "MyPCBench-main" / "tasks" / "final" / "all_tasks_with_grading.json"
LEFTOVER = P4 / "construction" / "out" / "phase2_leftover.json"
OUT = P4 / "construction" / "out"
SEAL_DIR = P4 / "construction" / "sealed"

EXPECTED_INSTR = "c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59"
ALLOWED_KINDS = ("money_usd", "integer", "entity", "categorical")
SLATE = [
    "contradiction-f013",
    "contradiction-f015",
    "contradiction-f016",
    "contradiction-f021",
    "contradiction-f023",
    "counterfactual-f008",
    "counterfactual-f014",
    "retrieval-f020",
    "retrieval-f032",
    "retrieval-f033",
    "retrieval-f035",
]
N_A = 11

# Same patterns as frozen p4_instrument.py. Duplicated so gold-lock does not
# score any observation channel.
MONEY_RE = re.compile(
    r"\$\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?|\d{1,3}(?:,\d{3})*\.\d{1,2}"
)
INT_RE = re.compile(r"\d+")
FILE_RE = re.compile(r"\b[\w.-]+\.(?:txt|m3u)\b", re.I)
WORD_RE = re.compile(r"[A-Za-z]+")

RULE = (
    "Task-side instruction + rubric criteria only. "
    "Lock iff exactly one unique P4 money_usd match XOR exactly one unique "
    ".txt/.m3u basename (kind entity). Integers in llm_judge prose never lock. "
    "No task_id branch. No guest probe. No agent observation."
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def unique(seq: list[str]) -> list[str]:
    out: list[str] = []
    for x in seq:
        if x not in out:
            out.append(x)
    return out


def task_text(row: dict) -> str:
    crits = [(item.get("criterion") or "") for item in (row.get("grading") or {}).get("rubrics") or []]
    return (row.get("instruction") or "") + "\n" + "\n".join(crits)


def extract_candidates(text: str) -> dict:
    money = unique([m.group(0) for m in MONEY_RE.finditer(text)])
    money_spans = [m.span() for m in MONEY_RE.finditer(text)]
    ints: list[str] = []
    for m in INT_RE.finditer(text):
        a, b = m.span()
        if any(a < mb and b > ma for ma, mb in money_spans):
            continue
        ints.append(m.group(0))
    files = unique([m.group(0) for m in FILE_RE.finditer(text)])
    return {
        "money_usd": money,
        "integer": unique(ints),
        "entity_file": files,
    }


def lock_kind(cands: dict) -> tuple[str | None, str | None, str]:
    money, files = cands["money_usd"], cands["entity_file"]
    n_money, n_file = len(money), len(files)
    if n_money == 1 and n_file == 0:
        return "money_usd", money[0], "unique_money"
    if n_money == 0 and n_file == 1:
        return "entity", files[0], "unique_txt_or_m3u_basename"
    if n_money == 1 and n_file == 1:
        return None, None, "competing_money_and_file"
    if n_money > 1:
        return None, None, "nonunique_money"
    if n_file > 1:
        return None, None, "nonunique_file"
    return None, None, "no_unique_allowed_kind_value"


def ngrams(instruction: str) -> list[str]:
    tokens = instruction.split()
    out: list[str] = []
    for n in range(4, 1, -1):
        for i in range(0, len(tokens) - n + 1):
            out.append(" ".join(tokens[i : i + n]))
    return out


def pick_anchors(instruction: str, gold: str) -> list[str]:
    gold_cf = gold.casefold()
    gtoks = {m.group(0).casefold() for m in WORD_RE.finditer(gold)}
    ranked: list[tuple[int, int, int, str]] = []
    for ng in ngrams(instruction):
        if gold_cf in ng.casefold() or ng.casefold() in gold_cf:
            continue
        if ng not in instruction:
            continue
        if len(ng.split()) < 2:
            continue
        ngtoks = {m.group(0).casefold() for m in WORD_RE.finditer(ng)}
        overlap = len(ngtoks & gtoks)
        ranked.append((-len(ng.split()), -overlap, instruction.find(ng), ng))
    if not ranked:
        return []
    ranked.sort()
    # Prefer token overlap with gold when any ngram overlaps; else longest-first.
    with_overlap = [r for r in ranked if r[1] < 0]
    chosen = (with_overlap or ranked)[0][3]
    return [chosen]


def correspondence_ok(kind: str, gold: str) -> dict:
    """Gold is a well-formed value of `kind` under frozen §2 / Paper 2 rules."""
    sys.path.insert(0, str(INSTR.parent))
    from p4_instrument import parse_money, v3_match  # noqa: E402

    checks = {"kind_allowed": kind in ALLOWED_KINDS, "gold_nonempty": bool(gold)}
    if kind == "money_usd":
        try:
            val = parse_money(gold)
            checks["parses_as_kind"] = True
            checks["self_match"] = bool(v3_match(kind, val, gold))
        except Exception:
            checks["parses_as_kind"] = False
            checks["self_match"] = False
    elif kind == "integer":
        try:
            val = int(gold)
            checks["parses_as_kind"] = True
            checks["self_match"] = bool(v3_match(kind, val, gold))
        except Exception:
            checks["parses_as_kind"] = False
            checks["self_match"] = False
    else:
        checks["parses_as_kind"] = True
        checks["self_match"] = bool(v3_match(kind, gold, gold))
    checks["pass"] = all(checks.values())
    return checks


def construction_ok(instruction: str, kind: str, gold: str, anchors: list[str]) -> dict:
    checks = {
        "kind_allowed": kind in ALLOWED_KINDS,
        "gold_nonnull": bool(gold),
        "n_anchors": len(anchors) >= 1,
        "anchors_ge_2_tokens": all(len(a.split()) >= 2 for a in anchors) if anchors else False,
        "anchor_literal_in_instruction": all(a in instruction for a in anchors) if anchors else False,
        "gold_not_substring_of_anchor": (
            all(gold.casefold() not in a.casefold() for a in anchors) if gold and anchors else False
        ),
    }
    corr = correspondence_ok(kind, gold)
    checks["correspondence"] = corr
    checks["pass"] = all(v is True for k, v in checks.items() if k != "correspondence") and corr["pass"]
    return checks


def main() -> int:
    instr_sha = sha256_file(INSTR)
    if instr_sha != EXPECTED_INSTR:
        raise SystemExit(f"instrument hash drifted: {instr_sha}")

    leftover = json.loads(LEFTOVER.read_text())
    leftover_ids = [r["id"] for r in leftover["leftover_lexicographic"]]
    if leftover_ids != SLATE:
        raise SystemExit(f"leftover slate drifted: {leftover_ids}")
    if leftover.get("N_A") != N_A:
        raise SystemExit(f"N_A drifted: {leftover.get('N_A')}")

    by_id = {t["id"]: t for t in json.loads(TASKS.read_text())}
    missing = [i for i in SLATE if i not in by_id]
    if missing:
        raise SystemExit(f"missing from pinned file: {missing}")

    source = []
    clusters = []
    for tid in SLATE:
        t = by_id[tid]
        source.append(
            {
                "id": tid,
                "category": t["category"],
                "instruction": t["instruction"],
                "grading": t["grading"],
            }
        )
        text = task_text(t)
        cands = extract_candidates(text)
        kind, gold, reason = lock_kind(cands)
        rec = {
            "id": tid,
            "category": t["category"],
            "instruction": t["instruction"],
            "grading_type": (t.get("grading") or {}).get("type"),
            "candidates": cands,
            "lock_reason": reason,
            "locked": False,
            "component_id": None,
            "kind": None,
            "gold": None,
            "anchors": [],
        }
        if kind and gold:
            anchors = pick_anchors(t["instruction"], gold)
            rec.update(
                {
                    "component_id": "task_side_determining",
                    "kind": kind,
                    "gold": gold,
                    "anchors": anchors,
                    "construction": construction_ok(t["instruction"], kind, gold, anchors),
                }
            )
            rec["locked"] = bool(rec["construction"]["pass"])
            if not rec["locked"]:
                failed = [
                    k
                    for k, v in rec["construction"].items()
                    if k not in {"pass", "correspondence"} and v is not True
                ]
                if not rec["construction"]["correspondence"]["pass"]:
                    failed.append("correspondence")
                rec["lock_reason"] = "construction_check_failed:" + ",".join(failed)
        else:
            rec["construction"] = {
                "pass": False,
                "reason": reason,
                "grading_is_llm_judge": rec["grading_type"] == "llm_judge",
            }
        clusters.append(rec)

    locked = [c for c in clusters if c["locked"]]
    n_locked = len(locked)
    gate = "PASS" if n_locked == N_A else "FAIL"
    payload = {
        "slate": SLATE,
        "N_A_declared": N_A,
        "n_attempted": 11,
        "n_locked": n_locked,
        "survivors": [c["id"] for c in locked],
        "gate": gate,
        "rule": RULE,
        "instrument_sha256": instr_sha,
        "instrument_modified": False,
        "agent_run": False,
        "api_spend_usd": 0,
        "clusters": clusters,
    }

    OUT.mkdir(exist_ok=True)
    SEAL_DIR.mkdir(exist_ok=True)
    src_path = OUT / "phase2_taskside_source.json"
    spec_path = OUT / "phase2_gold_lock.json"
    src_bytes = json.dumps(source, indent=2, ensure_ascii=False, sort_keys=True).encode() + b"\n"
    spec_bytes = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True).encode() + b"\n"
    src_path.write_bytes(src_bytes)
    spec_path.write_bytes(spec_bytes)

    seal = {
        "status": "SEALED",
        "n_attempted": 11,
        "n_locked": n_locked,
        "gate": gate,
        "N_A_declared": N_A,
        "survivors": [c["id"] for c in locked],
        "phase2_gold_lock_sha256": sha256_bytes(spec_bytes),
        "phase2_taskside_source_sha256": sha256_bytes(src_bytes),
        "pinned_tasks_sha256": sha256_file(TASKS),
        "instrument_sha256": instr_sha,
        "gold_lock_script_sha256": sha256_file(Path(__file__).resolve()),
        "leftover_listing_sha256": sha256_file(LEFTOVER),
        "rule": RULE,
        "agent_run": False,
        "api_spend_usd": 0,
        "do_not_edit": True,
        "do_not_lower_N_A": True,
        "do_not_open_agents": gate != "PASS",
    }
    seal_path = SEAL_DIR / "PHASE2_GOLD_LOCK_SEAL.json"
    seal_bytes = json.dumps(seal, indent=2, sort_keys=True).encode() + b"\n"
    seal_path.write_bytes(seal_bytes)

    lines = [
        "# P4 Phase-2 gold-lock",
        "",
        "Task-side instruction + rubric criteria only. No agents. $0 API.",
        "Instrument not modified.",
        "",
        f"N_A declared = {N_A}",
        f"n_attempted = 11",
        f"n_locked = {n_locked}",
        f"gate (n_locked == N_A) = **{gate}**",
        "",
        f"instrument_sha256 = `{instr_sha}`",
        f"phase2_gold_lock_sha256 = `{seal['phase2_gold_lock_sha256']}`",
        f"phase2_taskside_source_sha256 = `{seal['phase2_taskside_source_sha256']}`",
        f"seal_sha256 = `{sha256_bytes(seal_bytes)}`",
        "",
        RULE,
        "",
        "| id | locked | kind | gold | anchors | reason |",
        "|---|---|---|---|---|---|",
    ]
    for c in clusters:
        gold = c.get("gold") if c.get("gold") is not None else ""
        anchors = c.get("anchors") or []
        lines.append(
            f"| `{c['id']}` | {str(c['locked']).upper()} | {c.get('kind') or ''} | `{gold}` | {anchors} | {c['lock_reason']} |"
        )
    lines += [
        "",
        "No IDs added or removed from the leftover 11.",
        "If FAIL: do not lower N_A. Do not start agents. Construction fail of Phase 2.",
    ]
    (OUT / "phase2_gold_lock.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
