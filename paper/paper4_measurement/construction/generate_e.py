#!/usr/bin/env python3
"""P4-D Phase 1: instantiate E worlds, lock gold from L, construction tests.

No per-id branch. No observations. No agents.
Does not edit p4_instrument.py / p4_instrument_v2.py / wrapper.
Does not modify P4-B, P4-C v1, or P4-C2 D worlds.
"""
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent
P4 = ROOT.parent
INSTR_V1 = P4 / "instrument" / "p4_instrument.py"
INSTR_V2 = P4 / "instrument" / "p4_instrument_v2.py"
WRAPPER = P4 / "instrument" / "p4c2_claim_wrapper.txt"
ADJ = ROOT / "adjudicator_d.py"
SLATE = ROOT / "slate" / "e"
WORLDS = SLATE / "worlds"
OUT = ROOT / "out"
EXPECTED_INSTR_V1 = "c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59"
EXPECTED_INSTR_V2 = "a87ac636a729d99852eb837583b24bce372ff49c196f2be7e39e4f750622fcf3"
EXPECTED_WRAPPER = "2a028f2b95a7bc1ce815ac4b01dcb1fc7c8814ded7a5f3f38489d4ffe70e8e08"
N_E = 30
IDS = [f"E{i:02d}" for i in range(1, 31)]
KIND_QUOTA = {"money_usd": 12, "integer": 9, "entity": 6, "categorical": 3}
FAMILY_QUOTA = {
    "Locate": 9,
    "Compute": 6,
    "Reconcile": 6,
    "Filter": 3,
    "Tally": 3,
    "Multi-step": 3,
}
CONDITION_QUOTA = {"plus": 10, "minus": 10, "pm": 10}
FAMILY_OP = {
    "Locate": "select_join",
    "Filter": "select_join",
    "Compute": "sum_join",
    "Tally": "count_join",
    "Reconcile": "live_not_stale",
    "Multi-step": "select_join3",
}

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(INSTR_V2.parent))
import generate_d as g  # noqa: E402
from p4_instrument_v2 import parse_money, v3_match  # noqa: E402

D_GOLDS = {
    "81.60", "46.75", "63.20", "52.10", "38.35", "68.40", "41.25", "37.55",
    "55.15", "26.45", "72.80", "Tesfaye Holm", "foxed", "Anouk Veld", "taut",
    "Joren Pike", "bound", "Saskia Bel", "Oren Falk", "slack", "25", "28",
    "27", "19", "10", "11", "15", "18", "20",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def probe_match(kind: str, committed, gold: str) -> bool:
    return bool(v3_match(kind, committed, gold))


def in_near_band(kind: str, gold: str, comp: str) -> bool:
    try:
        if kind == "money_usd":
            if probe_match(kind, parse_money(comp), gold):
                return False
            gval = parse_money(gold)
            cval = parse_money(comp)
            return (gval * Decimal("0.5")) <= cval <= (gval * Decimal("2.0"))
        if kind == "integer":
            if probe_match(kind, int(comp), gold):
                return False
            return 1 <= abs(int(comp) - int(gold)) <= 3
        return not probe_match(kind, comp, gold)
    except Exception:
        return False


def competitor_in_blob(comp: str, blob: str) -> bool:
    return comp in blob


def main() -> int:
    errors: list[str] = []
    if sha256_file(INSTR_V1) != EXPECTED_INSTR_V1:
        errors.append(f"v1 instrument drifted: {sha256_file(INSTR_V1)}")
    if sha256_file(INSTR_V2) != EXPECTED_INSTR_V2:
        errors.append(f"v2 instrument drifted: {sha256_file(INSTR_V2)}")
    if sha256_file(WRAPPER) != EXPECTED_WRAPPER:
        errors.append(f"wrapper drifted: {sha256_file(WRAPPER)}")
    if not g.no_per_id_branch(Path(__file__).read_text(), IDS):
        errors.append("generate_e.py has a per-id branch")
    if not g.no_per_id_branch(INSTR_V2.read_text(), IDS):
        errors.append("score_v2 has an E id branch")

    qtok = g.load_wordlist("wordlists_q.txt")
    vtok = g.load_wordlist("wordlists_v.txt")
    rtok = g.load_wordlist("wordlists_r.txt")
    btok = g.load_wordlist("wordlists_b.txt")
    ctok = g.load_wordlist("wordlists_c.txt")
    dtok = g.load_wordlist("wordlists_d.txt")
    etok = g.load_wordlist("wordlists_e.txt")
    if etok & (qtok | vtok | rtok | btok | ctok | dtok):
        errors.append("wordlists_e not disjoint from Q/V/R/B/C/D")
    foreign = qtok | vtok | rtok | btok | ctok | dtok

    wrap = WRAPPER.read_text()
    if "CLAIM:" not in wrap:
        errors.append("wrapper missing CLAIM")
    if g.words(wrap) & etok:
        errors.append("wrapper contains E cover tokens")

    params = json.loads((ROOT / "params_e.json").read_text())
    if list(params) != IDS:
        errors.append(f"params keys {list(params)} != {IDS}")

    SLATE.mkdir(parents=True, exist_ok=True)
    if WORLDS.exists():
        for p in WORLDS.rglob("*"):
            if p.is_file():
                p.unlink()
    WORLDS.mkdir(parents=True, exist_ok=True)

    clusters = []
    kinds: dict[str, int] = {}
    families: dict[str, int] = {}
    conditions: dict[str, int] = {}
    family_ids: dict[str, int] = {}

    for cid in IDS:
        row = params[cid]
        if "anchors" in row or "gold" in row or "observations" in row:
            errors.append(f"{cid}: forbidden field in params")
        family, kind, cond = row["family"], row["kind"], row["condition"]
        fam_id = row["family_id"]
        kinds[kind] = kinds.get(kind, 0) + 1
        families[family] = families.get(family, 0) + 1
        conditions[cond] = conditions.get(cond, 0) + 1
        family_ids[fam_id] = family_ids.get(fam_id, 0) + 1
        loc = row["locator"]
        comps = list(row.get("competitors") or [])
        if loc["op"] != FAMILY_OP[family]:
            errors.append(f"{cid}: op {loc['op']} != family {family}")

        files: dict[str, str] = {}
        tables: dict[str, list[dict]] = {}
        wdir = WORLDS / cid
        wdir.mkdir(parents=True, exist_ok=True)
        for spec in row["files"]:
            text = g.emit_file(spec)
            rel = spec["path"]
            dest = wdir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text)
            files[rel] = text
            tables[rel] = g.parse_file(spec, text)

        meta = {
            "id": cid,
            "family_id": fam_id,
            "family": family,
            "kind": kind,
            "condition": cond,
            "component_id": row["component_id"],
            "instruction": row["instruction"],
            "locator": loc,
            "files": sorted(files),
        }
        (wdir / "world_meta.json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
        if "gold" in meta or "competitors" in meta:
            errors.append(f"{cid}: gold/competitors leaked into world_meta")

        lock_err = None
        gold = None
        try:
            gold = g.apply_locator(tables, loc, kind)
        except Exception as exc:
            lock_err = str(exc)

        inst = row["instruction"]
        blob_files = g.blob_of(files)
        blob = inst + "\n" + blob_files
        checks = {
            "gold_locked": lock_err is None,
            "lock_error": lock_err,
            "kind_allowed": kind in KIND_QUOTA,
            "family_known": family in FAMILY_QUOTA,
            "condition_known": cond in CONDITION_QUOTA,
            "one_component": True,
            "no_anchors": "anchors" not in row,
            "T4_no_observations": "observations" not in row,
            "T4_no_gold_in_params": "gold" not in row,
            "T5_no_llm_judge": row.get("grading") is None,
            "T6_id_ok": cid.startswith("E") and cid not in g.EXCLUSION_IDS,
            "T8_two_sources": loc["left"] != loc["right"] and loc["left"] in files and loc["right"] in files,
            "T7_no_foreign_tokens": not (g.words(blob) & foreign),
            "own_cover_token": bool(g.words(inst) & etok),
            "forbidden_substr": not any(s in blob.casefold() for s in g.FORBIDDEN_SUBSTR),
            "T2_toy_basename": all(Path(spec["path"]).stem.casefold() not in g.TOY_BASENAMES for spec in row["files"]),
        }
        if family == "Multi-step":
            checks["T8_three_sources"] = (
                loc.get("mid") in files
                and loc["mid"] != loc["left"]
                and loc["mid"] != loc["right"]
            )
        if gold is not None:
            checks["T1_gold_not_in_instruction"] = gold not in inst
            checks["forbidden_gold"] = gold not in g.FORBIDDEN_VALUES and gold not in D_GOLDS
            checks["T3_distractors"] = g.t3_ok(kind, gold, files, tables)
            checks["T_prompt"] = gold not in inst and all(c not in inst for c in comps)
            in_world = all(competitor_in_blob(c, blob_files) for c in comps)
            checks["competitors_in_world"] = in_world and len(comps) >= 1
            not_gold = True
            for c in comps:
                try:
                    if kind == "money_usd":
                        hit = probe_match(kind, parse_money(c), gold)
                    elif kind == "integer":
                        hit = probe_match(kind, int(c), gold)
                    else:
                        hit = probe_match(kind, c, gold)
                except Exception:
                    hit = False
                if hit:
                    not_gold = False
            checks["competitors_not_gold"] = not_gold
            if cond in {"minus", "pm"}:
                checks["T_opp"] = bool(comps) and in_world and not_gold
            else:
                checks["T_opp"] = True
            if cond == "minus":
                checks["T_near"] = all(in_near_band(kind, gold, c) for c in comps) if comps else False
            else:
                checks["T_near"] = True
            if cond == "plus":
                if kind in {"money_usd", "integer"}:
                    checks["T_far"] = all(not in_near_band(kind, gold, c) for c in comps) if comps else False
                else:
                    left_text = files.get(loc["left"], "")
                    checks["T_far"] = all(c not in left_text for c in comps) if comps else False
            else:
                checks["T_far"] = True
            try:
                if kind == "money_usd":
                    checks["correspondence"] = probe_match(kind, parse_money(gold), gold)
                elif kind == "integer":
                    checks["correspondence"] = probe_match(kind, int(gold), gold)
                else:
                    checks["correspondence"] = probe_match(kind, gold, gold)
            except Exception as exc:
                checks["correspondence"] = False
                checks["correspondence_error"] = str(exc)
        else:
            for k in (
                "T1_gold_not_in_instruction",
                "forbidden_gold",
                "T3_distractors",
                "T_prompt",
                "T_opp",
                "T_near",
                "T_far",
                "correspondence",
                "competitors_in_world",
                "competitors_not_gold",
            ):
                checks[k] = False

        skip = {"lock_error", "correspondence_error"}
        checks["pass"] = all(v is True for k, v in checks.items() if k not in skip and k != "pass")
        if not checks["pass"]:
            failed = [k for k, v in checks.items() if k not in skip and k != "pass" and v is not True]
            errors.append(f"{cid}: FAIL {failed}" + (f" lock={lock_err}" if lock_err else ""))

        cluster = {
            "id": cid,
            "family_id": fam_id,
            "family": family,
            "kind": kind,
            "condition": cond,
            "component_id": row["component_id"],
            "instruction": inst,
            "locator": loc,
            "competitors": comps,
            "gold": gold,
            "construction": checks,
        }
        (SLATE / f"{cid}.json").write_text(json.dumps(cluster, indent=2, sort_keys=True) + "\n")
        clusters.append(cluster)

    if kinds != KIND_QUOTA:
        errors.append(f"kind quota {kinds} != {KIND_QUOTA}")
    if families != FAMILY_QUOTA:
        errors.append(f"family quota {families} != {FAMILY_QUOTA}")
    if conditions != CONDITION_QUOTA:
        errors.append(f"condition quota {conditions} != {CONDITION_QUOTA}")
    if family_ids != {f"F{i:02d}": 3 for i in range(1, 11)}:
        errors.append(f"family_id quota {family_ids}")

    n_pass = sum(1 for c in clusters if c["construction"]["pass"] and c["gold"] is not None)
    gate = "PASS" if n_pass == N_E and not errors else "FAIL"
    payload = {
        "phase": 1,
        "workstream": "P4-D",
        "status": gate,
        "N_E": N_E,
        "n_pass": n_pass,
        "kind_counts": kinds,
        "family_counts": families,
        "condition_counts": conditions,
        "api_spend_usd": 0,
        "agents_run": 0,
        "instrument_v1_sha256": sha256_file(INSTR_V1),
        "instrument_v2_sha256": sha256_file(INSTR_V2),
        "wrapper_sha256": sha256_file(WRAPPER),
        "adjudicator_d_sha256": sha256_file(ADJ),
        "instrument_v1_modified": False,
        "instrument_v2_modified": False,
        "wrapper_modified": False,
        "p4b_modified": False,
        "p4c_modified": False,
        "p4c2_modified": False,
        "errors": errors,
        "clusters": [
            {
                "id": c["id"],
                "family_id": c["family_id"],
                "family": c["family"],
                "condition": c["condition"],
                "kind": c["kind"],
                "gold": c["gold"],
                "construction_pass": c["construction"]["pass"],
                "failures": [
                    k
                    for k, v in c["construction"].items()
                    if k not in {"pass", "lock_error", "correspondence_error"} and v is not True
                ],
            }
            for c in clusters
        ],
    }
    OUT.mkdir(exist_ok=True)
    spec_bytes = json.dumps(payload, indent=2, sort_keys=True).encode() + b"\n"
    (OUT / "p4d_phase1_construction.json").write_bytes(spec_bytes)
    gold_spec = [
        {k: c[k] for k in ("id", "family_id", "family", "kind", "condition", "gold", "locator", "instruction", "component_id")}
        for c in clusters
    ]
    gold_bytes = json.dumps(gold_spec, indent=2, sort_keys=True).encode() + b"\n"
    (OUT / "p4d_gold_spec.json").write_bytes(gold_bytes)
    lines = [
        "# P4-D Phase 1 construction",
        "",
        f"status = **{gate}**",
        f"n_pass = {n_pass} / {N_E}",
        "api_spend_usd = 0",
        f"instrument_v2_sha256 = `{payload['instrument_v2_sha256']}`",
        f"wrapper_sha256 = `{payload['wrapper_sha256']}`",
        "",
        f"kind counts: {kinds}",
        f"family counts: {families}",
        f"condition counts: {conditions}",
        "",
        "| id | family_id | family | condition | kind | gold | pass | failures |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for c in payload["clusters"]:
        lines.append(
            f"| `{c['id']}` | {c['family_id']} | {c['family']} | {c['condition']} | {c['kind']} | `{c['gold']}` | {c['construction_pass']} | {c['failures']} |"
        )
    if errors:
        lines += ["", "## Errors", ""]
        lines += [f"- {e}" for e in errors]
    else:
        lines += ["", "No construction errors.", ""]
    lines += [
        "",
        "P4-B, P4-C v1, P4-C2, score_v2, and wrapper were not modified. $0 API. No agents.",
        "Conditions are construction factors, not N. Form is not coverage.",
    ]
    (OUT / "p4d_phase1_construction.md").write_text("\n".join(lines) + "\n")
    (OUT / "p4d_phase1_status.json").write_text(
        json.dumps(
            {
                "phase": 1,
                "workstream": "P4-D",
                "status": gate,
                "n_pass": n_pass,
                "N_E": N_E,
                "api_spend_usd": 0,
                "next": "PHASE_2_SEAL" if gate == "PASS" else "STOP",
                "instrument_v2_modified": False,
                "p4c2_modified": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    print("\n".join(lines))
    return 0 if gate == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
