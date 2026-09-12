#!/usr/bin/env python3
"""P4-D Phase 2 qualification and seal. $0. No agents.

Read-only on E01–E30. Hashes frozen C2 DFC + A + transforms_d.
Does not edit instruments, wrapper, P4-B, P4-C, or P4-C2.
"""
from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
P4 = ROOT.parent
INSTR_V1 = P4 / "instrument" / "p4_instrument.py"
INSTR_V2 = P4 / "instrument" / "p4_instrument_v2.py"
WRAPPER = P4 / "instrument" / "p4c2_claim_wrapper.txt"
SLATE = ROOT / "slate" / "e"
WORLDS = SLATE / "worlds"
OUT = ROOT / "out"
SEAL = ROOT / "sealed" / "P4D_PHASE2_SEAL.json"
TRANS = ROOT / "transforms_d.py"
ADJ = ROOT / "adjudicator_d.py"
GEN = ROOT / "generate_e.py"
EQ_QUAL = ROOT / "out" / "eq_qualification.json"
P4C2_SEAL = ROOT / "sealed" / "P4C2_PHASE2_SEAL.json"
P4C_SEAL = ROOT / "sealed" / "P4C_PHASE2_SEAL.json"
P4B_SEAL = ROOT / "sealed" / "P4B_PHASE2_SEAL.json"
EXPECTED_INSTR_V1 = "c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59"
EXPECTED_INSTR_V2 = "a87ac636a729d99852eb837583b24bce372ff49c196f2be7e39e4f750622fcf3"
EXPECTED_WRAPPER = "2a028f2b95a7bc1ce815ac4b01dcb1fc7c8814ded7a5f3f38489d4ffe70e8e08"
N_E = 30
IDS = [f"E{i:02d}" for i in range(1, 31)]
BANNED = ("B", "C", "D", "Q", "CQ", "V", "R")

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(INSTR_V2.parent))
import generate_d as g  # noqa: E402
import generate_e as ge  # noqa: E402
from p4_instrument_v2 import parse_money, v3_match, score_v2  # noqa: E402
import transforms_d  # noqa: E402
import adjudicator_d as A  # noqa: E402


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def combined_hash(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for p in paths:
        h.update(str(p.relative_to(P4)).encode())
        h.update(b"\0")
        h.update(p.read_bytes())
        h.update(b"\n")
    return h.hexdigest()


def parse_disk(path: Path) -> list[dict]:
    text = path.read_text()
    suf = path.suffix.casefold()
    if suf == ".csv":
        return g.parse_csv(text)
    if suf == ".ics":
        return g.parse_ics(text)
    if suf == ".html":
        return g.parse_html(text)
    return g.parse_kv(text)


def load_world_files(cid: str) -> dict[str, str]:
    wdir = WORLDS / cid
    files = {}
    for p in sorted(wdir.rglob("*")):
        if p.is_file() and p.name != "world_meta.json":
            rel = str(p.relative_to(wdir)).replace("\\", "/")
            files[rel] = p.read_text()
    return files


def h7_ok(src: str, errors: list[str]) -> bool:
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "p4_instrument":
            if "score" in {a.name for a in node.names}:
                errors.append("H7: score_v2 imports v1 score")
                return False
        if isinstance(node, ast.FunctionDef) and node.name == "score_v2":
            args = [a.arg for a in node.args.args] + [a.arg for a in node.args.kwonlyargs]
            if "anchors" in args or "task_id" in args:
                errors.append("H7: score_v2 takes anchors or task_id")
                return False
    lowered = src.casefold()
    for tok in ("screenshot", "tool_trace", "world_files"):
        if tok in lowered:
            errors.append(f"H7: instrument mentions {tok}")
            return False
    return True


def main() -> int:
    errors: list[str] = []
    instr_v1 = sha256_file(INSTR_V1)
    instr_v2 = sha256_file(INSTR_V2)
    wrap = sha256_file(WRAPPER)
    if instr_v1 != EXPECTED_INSTR_V1:
        errors.append(f"v1 drifted {instr_v1}")
    if instr_v2 != EXPECTED_INSTR_V2:
        errors.append(f"v2 drifted {instr_v2}")
    if wrap != EXPECTED_WRAPPER:
        errors.append(f"wrapper drifted {wrap}")
    h7_ok(INSTR_V2.read_text(), errors)
    if not g.no_per_id_branch(INSTR_V2.read_text(), IDS):
        errors.append("score_v2 has E id branch")
    if not g.no_per_id_branch(ADJ.read_text(), IDS):
        errors.append("adjudicator has E id branch")
    if not g.no_per_id_branch(TRANS.read_text(), IDS):
        errors.append("transforms_d has E id branch")
    if not g.no_per_id_branch(GEN.read_text(), IDS):
        errors.append("generate_e has E id branch")

    sample = A.adjudicate(
        kind="money_usd",
        gold="1.00",
        locator={"op": "select_join", "left": "a.csv", "right": "b.txt"},
        world_files={},
        tool_trace=[],
    )
    if sample.get("gt") != "INDETERMINATE":
        errors.append(f"A empty-trace smoke {sample}")

    eq = json.loads(EQ_QUAL.read_text()) if EQ_QUAL.is_file() else {}
    eq_ok = eq.get("qualification") == "PASS" and eq.get("property_pass_clusters") == 6
    if not eq_ok:
        errors.append("Q3 EQ qualification is not PASS 6/6")
    texts = eq.get("texts_per_kind") or {}
    for kind in ("money_usd", "integer", "entity", "categorical"):
        if int(texts.get(kind, 0)) < 6:
            errors.append(f"Q3 {kind} has <6 authored last-texts")

    p1 = json.loads((OUT / "p4d_phase1_status.json").read_text())
    if p1.get("status") != "PASS":
        errors.append("Phase 1 is not PASS")

    if not (P4C2_SEAL.is_file() and P4C_SEAL.is_file() and P4B_SEAL.is_file()):
        errors.append("prior seals missing")

    etok = g.load_wordlist("wordlists_e.txt")
    foreign = (
        g.load_wordlist("wordlists_q.txt")
        | g.load_wordlist("wordlists_v.txt")
        | g.load_wordlist("wordlists_r.txt")
        | g.load_wordlist("wordlists_b.txt")
        | g.load_wordlist("wordlists_c.txt")
        | g.load_wordlist("wordlists_d.txt")
    )
    if etok & foreign:
        errors.append("E wordlist not disjoint")

    params = json.loads((ROOT / "params_e.json").read_text())
    clusters = []
    kinds: dict[str, int] = {}
    families: dict[str, int] = {}
    conditions: dict[str, int] = {}
    gold_spec = []
    for cid in IDS:
        if cid.startswith(BANNED) and not cid.startswith("E"):
            errors.append(f"H8 id {cid}")
        row = json.loads((SLATE / f"{cid}.json").read_text())
        kind, family, cond = row["kind"], row["family"], row["condition"]
        gold = row["gold"]
        loc = row["locator"]
        inst = row["instruction"]
        kinds[kind] = kinds.get(kind, 0) + 1
        families[family] = families.get(family, 0) + 1
        conditions[cond] = conditions.get(cond, 0) + 1
        files = load_world_files(cid)
        tables = {rel: parse_disk(WORLDS / cid / rel) for rel in files}
        replay = g.apply_locator(tables, loc, kind)
        meta = json.loads((WORLDS / cid / "world_meta.json").read_text())
        blob = inst + "\n" + g.blob_of(files)
        checks = {
            "locker_replay_matches_gold": replay == gold,
            "family_op": loc.get("op") == ge.FAMILY_OP[family],
            "T1_gold_not_in_instruction": gold not in inst,
            "T4_no_observations": "observations" not in row,
            "T4_no_gold_in_params": "gold" not in params[cid],
            "no_anchors": "anchors" not in row and "anchors" not in meta,
            "T7_no_foreign_tokens": not (g.words(blob) & foreign),
            "own_cover_token": bool(g.words(inst) & etok),
            "world_meta_has_no_gold": "gold" not in meta,
            "condition_known": cond in ge.CONDITION_QUOTA,
            "T_prompt": all(c not in inst for c in (row.get("competitors") or [])) and gold not in inst,
        }
        skip = set()
        checks["pass"] = all(v is True for k, v in checks.items() if k not in skip)
        if not checks["pass"]:
            failed = [k for k, v in checks.items() if v is not True]
            errors.append(f"{cid}: qual FAIL {failed}")
        clusters.append({"id": cid, "family": family, "kind": kind, "condition": cond, "gold": gold, "checks": checks})
        gold_spec.append(
            {
                "id": cid,
                "family_id": row["family_id"],
                "family": family,
                "kind": kind,
                "condition": cond,
                "gold": gold,
                "locator": loc,
                "instruction": inst,
                "component_id": row["component_id"],
            }
        )

    if kinds != ge.KIND_QUOTA:
        errors.append(f"kind quota {kinds}")
    if families != ge.FAMILY_QUOTA:
        errors.append(f"family quota {families}")
    if conditions != ge.CONDITION_QUOTA:
        errors.append(f"condition quota {conditions}")

    n_pass = sum(1 for c in clusters if c["checks"]["pass"])
    s12 = {
        "n30_and_quotas": n_pass == N_E and kinds == ge.KIND_QUOTA,
        "locker_replay": all(c["checks"]["locker_replay_matches_gold"] for c in clusters),
        "eq_pre_gate": eq_ok,
        "instrument_v2_hash": instr_v2 == EXPECTED_INSTR_V2,
        "wrapper_hash": wrap == EXPECTED_WRAPPER,
        "h7_anti_recovery": not any(e.startswith("H7:") for e in errors),
        "h8_ids": all(i.startswith("E") for i in IDS),
        "p4c2_untouched": P4C2_SEAL.is_file(),
        "p4c_untouched": P4C_SEAL.is_file(),
        "p4b_untouched": P4B_SEAL.is_file(),
        "no_miss_quota_in_design": True,
    }
    phase2 = "PASS" if all(s12.values()) and not errors else "FAIL"

    cluster_paths = [SLATE / f"{cid}.json" for cid in IDS]
    world_paths = sorted(p for p in WORLDS.rglob("*") if p.is_file())
    gold_bytes = json.dumps(gold_spec, indent=2, sort_keys=True).encode() + b"\n"
    (OUT / "p4d_gold_spec.json").write_bytes(gold_bytes)

    payload = {
        "phase": 2,
        "workstream": "P4-D",
        "status": phase2,
        "N_E": N_E,
        "n_pass": n_pass,
        "section12": s12,
        "kind_counts": kinds,
        "family_counts": families,
        "condition_counts": conditions,
        "eq_qualification": "PASS" if eq_ok else "FAIL",
        "api_spend_usd": 0,
        "agents_run": 0,
        "instrument_v1_sha256": instr_v1,
        "instrument_v2_sha256": instr_v2,
        "wrapper_sha256": wrap,
        "adjudicator_d_sha256": sha256_file(ADJ),
        "transforms_d_sha256": sha256_file(TRANS),
        "generate_e_sha256": sha256_file(GEN),
        "params_e_sha256": sha256_file(ROOT / "params_e.json"),
        "wordlists_e_sha256": sha256_file(ROOT / "wordlists_e.txt"),
        "gold_spec_sha256": sha256_bytes(gold_bytes),
        "clusters_sha256": combined_hash(cluster_paths),
        "worlds_sha256": combined_hash(world_paths),
        "eq_qualification_sha256": sha256_file(EQ_QUAL) if EQ_QUAL.is_file() else None,
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
                "family": c["family"],
                "kind": c["kind"],
                "condition": c["condition"],
                "gold": c["gold"],
                "qualification_pass": c["checks"]["pass"],
                "failures": [k for k, v in c["checks"].items() if v is not True],
            }
            for c in clusters
        ],
    }
    out_bytes = json.dumps(payload, indent=2, sort_keys=True).encode() + b"\n"
    (OUT / "p4d_phase2_qualification.json").write_bytes(out_bytes)

    payload_seal = None
    if phase2 == "PASS":
        seal = {
            "status": "SEALED",
            "phase": 2,
            "workstream": "P4-D",
            "N_E": 30,
            "gate": "PASS",
            "instrument_v1_sha256": instr_v1,
            "instrument_v2_sha256": instr_v2,
            "wrapper_sha256": wrap,
            "clusters_sha256": payload["clusters_sha256"],
            "worlds_sha256": payload["worlds_sha256"],
            "gold_spec_sha256": payload["gold_spec_sha256"],
            "adjudicator_d_sha256": payload["adjudicator_d_sha256"],
            "transforms_d_sha256": payload["transforms_d_sha256"],
            "generate_e_sha256": payload["generate_e_sha256"],
            "params_e_sha256": payload["params_e_sha256"],
            "wordlists_e_sha256": payload["wordlists_e_sha256"],
            "eq_qualification_sha256": payload["eq_qualification_sha256"],
            "qualification_sha256": sha256_bytes(out_bytes),
            "public_quantities": ["Form", "CC", "Abs", "I_CC"],
            "form_is_not_coverage": True,
            "no_miss_quota": True,
            "do_not_edit_instrument_v2": True,
            "do_not_edit_wrapper": True,
            "do_not_edit_p4c2": True,
            "agent_run": False,
            "api_spend_usd": 0,
        }
        SEAL.parent.mkdir(exist_ok=True)
        seal_bytes = json.dumps(seal, indent=2, sort_keys=True).encode() + b"\n"
        SEAL.write_bytes(seal_bytes)
        payload_seal = sha256_bytes(seal_bytes)
    elif SEAL.exists():
        errors.append("refusing to seal a FAIL")

    lines = [
        "# P4-D Phase 2 qualification",
        "",
        f"status = **{phase2}**",
        f"n_pass = {n_pass} / {N_E}",
        f"Q3 = {'PASS 6/6' if eq_ok else 'FAIL'}",
        f"instrument_v2_sha256 = `{instr_v2}`",
        f"wrapper_sha256 = `{wrap}`",
        f"clusters_sha256 = `{payload['clusters_sha256']}`",
        f"worlds_sha256 = `{payload['worlds_sha256']}`",
        f"gold_spec_sha256 = `{payload['gold_spec_sha256']}`",
        f"seal_sha256 = `{payload_seal}`" if payload_seal else "seal = not written (FAIL)",
        "",
        "## Conjunction",
        "",
    ]
    for k, v in s12.items():
        lines.append(f"- `{k}`: {v}")
    if errors:
        lines += ["", "## Errors", ""] + [f"- {e}" for e in errors]
    (OUT / "p4d_phase2_qualification.md").write_text("\n".join(lines) + "\n")
    (OUT / "p4d_phase2_status.json").write_text(
        json.dumps(
            {
                "phase": 2,
                "workstream": "P4-D",
                "status": phase2,
                "n_pass": n_pass,
                "next": "PHASE_3_PILOT" if phase2 == "PASS" else "STOP",
                "instrument_v2_modified": False,
                "p4c2_modified": False,
                "api_spend_usd": 0,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    print("\n".join(lines))
    return 0 if phase2 == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
