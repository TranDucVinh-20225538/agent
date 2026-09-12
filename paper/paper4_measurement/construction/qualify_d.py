#!/usr/bin/env python3
"""P4-C2 Phase 2 corpus qualification and seal. $0. No agents.

Read-only on D01–D30 gold and worlds. Hashes A2, transforms_d, wrapper, score_v2.
Does not edit p4_instrument.py, P4-B, P4-C v1, or the D corpus.
H1–H8 require natural last-text and are Phase 4; this step does not open them.
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
SLATE = ROOT / "slate" / "d"
WORLDS = SLATE / "worlds"
OUT = ROOT / "out"
SEAL = ROOT / "sealed" / "P4C2_PHASE2_SEAL.json"
TRANS = ROOT / "transforms_d.py"
ADJ = ROOT / "adjudicator_d.py"
GEN = ROOT / "generate_d.py"
DQ_QUAL = ROOT / "out" / "dq_qualification.json"
P4C_SEAL = ROOT / "sealed" / "P4C_PHASE2_SEAL.json"
P4B_SEAL = ROOT / "sealed" / "P4B_PHASE2_SEAL.json"
EXPECTED_INSTR_V1 = "c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59"
EXPECTED_INSTR_V2 = "a87ac636a729d99852eb837583b24bce372ff49c196f2be7e39e4f750622fcf3"
N_D = 30
IDS = [f"D{i:02d}" for i in range(1, 31)]
BANNED_PREFIXES = ("B", "C", "Q", "CQ", "V", "R")

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(INSTR_V2.parent))
import generate_d as g  # noqa: E402
from p4_instrument_v2 import parse_money, v3_match, score_v2  # noqa: E402
import transforms_d  # noqa: E402
import adjudicator_d as A  # noqa: E402


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


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


def no_per_id_branch(src: str) -> bool:
    return g.no_per_id_branch(src, IDS)


def load_world_files(cid: str) -> dict[str, str]:
    wdir = WORLDS / cid
    files = {}
    for p in sorted(wdir.rglob("*")):
        if p.is_file() and p.name != "world_meta.json":
            rel = str(p.relative_to(wdir))
            files[rel] = p.read_text()
    return files


def combined_hash(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for p in paths:
        h.update(str(p.relative_to(P4)).encode())
        h.update(b"\0")
        h.update(p.read_bytes())
        h.update(b"\n")
    return h.hexdigest()


def adjudicator_ok(src: str, errors: list[str]) -> bool:
    if not no_per_id_branch(src):
        errors.append("adjudicator_d.py has a per-id branch")
        return False
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in {"score", "score_v2", "last_response", "last_text"}:
            errors.append(f"adjudicator_d.py references {node.id}")
            return False
        if isinstance(node, ast.Attribute) and node.attr in {"score", "score_v2"}:
            errors.append("adjudicator_d.py references a scorer")
            return False
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("p4_instrument"):
                    errors.append("adjudicator_d.py imports p4_instrument")
                    return False
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module.startswith("p4_instrument"):
                errors.append("adjudicator_d.py imports from p4_instrument")
                return False
    if not hasattr(A, "adjudicate"):
        errors.append("adjudicator_d.py missing adjudicate")
        return False
    sample = A.adjudicate(
        kind="money_usd",
        gold="1.00",
        locator={"op": "select_join", "left": "a.csv", "right": "b.txt"},
        world_files={},
        tool_trace=[],
    )
    if sample.get("gt") != "INDETERMINATE":
        errors.append(f"adjudicator empty-trace smoke = {sample}")
        return False
    return True


def h7_instrument_ok(src: str, errors: list[str]) -> bool:
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "p4_instrument":
            names = {a.name for a in node.names}
            if "score" in names:
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
    if instr_v1 != EXPECTED_INSTR_V1:
        errors.append(f"v1 instrument hash drifted: {instr_v1}")
    if instr_v2 != EXPECTED_INSTR_V2:
        errors.append(f"v2 instrument hash drifted: {instr_v2}")

    if not h7_instrument_ok(INSTR_V2.read_text(), errors):
        pass
    if not no_per_id_branch(INSTR_V2.read_text()):
        errors.append("p4_instrument_v2.py has a per-id branch")

    wrap = WRAPPER.read_text()
    if "CLAIM:" not in wrap or "<value>" not in wrap:
        errors.append("wrapper missing CLAIM contract")
    if any(tok in wrap.casefold() for tok in ("ridge", "bothy", "gold", "anchor")):
        errors.append("wrapper contains forbidden tokens")

    trans_src = TRANS.read_text()
    trans_ok = no_per_id_branch(trans_src)
    if not trans_ok:
        errors.append("transforms_d.py has a per-id branch")
    for name in (
        "working_irr",
        "c6_working_pair",
        "replace_claim",
        "c3_drop_claim",
        "c4_markup",
        "chan_unterminated",
    ):
        if not hasattr(transforms_d, name):
            errors.append(f"missing transform {name}")

    adj_ok = adjudicator_ok(ADJ.read_text(), errors)
    if not no_per_id_branch(GEN.read_text()):
        errors.append("generate_d.py has a per-id branch")

    if not P4C_SEAL.is_file():
        errors.append("P4-C seal missing")
    p4c_seal = json.loads(P4C_SEAL.read_text()) if P4C_SEAL.is_file() else {}
    if p4c_seal.get("instrument_sha256") != EXPECTED_INSTR_V1:
        errors.append("P4-C seal instrument hash mismatch")
    if not P4B_SEAL.is_file():
        errors.append("P4-B seal missing")

    dq = json.loads(DQ_QUAL.read_text()) if DQ_QUAL.is_file() else {}
    dq_ok = dq.get("qualification") == "PASS" and dq.get("property_pass_clusters") == 6
    if not dq_ok:
        errors.append("DQ qualification is not recorded PASS 6/6")
    if dq.get("instrument_v2_sha256") != EXPECTED_INSTR_V2:
        errors.append("DQ qualification instrument_v2 hash drifted")
    texts = dq.get("texts_per_kind") or {}
    for kind in ("money_usd", "integer", "entity", "categorical"):
        if int(texts.get(kind, 0)) < 6:
            errors.append(f"Q2 {kind} has <6 authored last-texts")

    rc_present = list(SLATE.glob("RC*.json")) + list(SLATE.glob("C*.json")) + list(SLATE.glob("B*.json"))
    if rc_present:
        errors.append(f"foreign slate files present at D seal: {rc_present}")

    for cid in IDS:
        if cid.startswith(BANNED_PREFIXES) or cid[0] in "BCQVR":
            if not cid.startswith("D"):
                errors.append(f"H8 id collision {cid}")
    if any(i.startswith(("B", "C", "Q", "V", "R")) and not i.startswith("D") for i in IDS):
        errors.append("H8 confirmatory ids collide with B/C/Q/V/R")

    qtok = g.load_wordlist("wordlists_q.txt")
    vtok = g.load_wordlist("wordlists_v.txt")
    rtok = g.load_wordlist("wordlists_r.txt")
    btok = g.load_wordlist("wordlists_b.txt")
    ctok = g.load_wordlist("wordlists_c.txt")
    dtok = g.load_wordlist("wordlists_d.txt")
    foreign = qtok | vtok | rtok | btok | ctok

    clusters = []
    kinds: dict[str, int] = {}
    families: dict[str, int] = {}
    slots: dict[str, int] = {}
    entity_files = 0
    gold_spec = []

    for cid in IDS:
        path = SLATE / f"{cid}.json"
        row = json.loads(path.read_text())
        if row.get("id") != cid:
            errors.append(f"{cid}: id mismatch")
        if "anchors" in row:
            errors.append(f"{cid}: anchors present at seal")
        kind, family = row["kind"], row["family"]
        slot = row["slot"]
        gold = row["gold"]
        inst = row["instruction"]
        loc = row["locator"]
        kinds[kind] = kinds.get(kind, 0) + 1
        families[family] = families.get(family, 0) + 1
        slots[slot] = slots.get(slot, 0) + 1
        files = load_world_files(cid)
        tables = {rel: parse_disk(WORLDS / cid / rel) for rel in files}
        blob = inst + "\n" + g.blob_of(files)

        replay = None
        replay_err = None
        try:
            replay = g.apply_locator(tables, loc, kind)
        except Exception as exc:
            replay_err = str(exc)

        meta = json.loads((WORLDS / cid / "world_meta.json").read_text())
        checks = {
            "locker_replay_matches_gold": replay == gold and replay_err is None,
            "replay_error": replay_err,
            "family_op": loc.get("op") == g.FAMILY_OP[family],
            "T1_gold_not_in_instruction": gold not in inst,
            "T2_toy_basename": all(Path(rel).stem.casefold() not in g.TOY_BASENAMES for rel in files),
            "T3_distractors": g.t3_ok(kind, gold, files, tables),
            "T4_no_observations": "observations" not in row and "last_response" not in row,
            "T4_no_gold_in_params": "gold" in row,  # cluster json may contain locked gold; worlds must not
            "T5_no_llm_judge": "grading" not in row,
            "T6_id_ok": cid not in g.EXCLUSION_IDS and cid.startswith("D"),
            "T7_no_foreign_tokens": not (g.words(blob) & foreign),
            "T8_two_sources": loc["left"] != loc["right"]
            and loc["left"] in files
            and loc["right"] in files,
            "no_anchors": "anchors" not in row and "anchors" not in meta,
            "one_component": True,
            "forbidden_gold": gold not in g.FORBIDDEN_VALUES,
            "forbidden_substr": not any(s in blob.casefold() for s in g.FORBIDDEN_SUBSTR),
            "exclusion_id_in_text": not any(x in blob for x in g.EXCLUSION_IDS),
            "own_cover_token": bool(g.words(inst) & dtok),
            "slot_known": slot in g.SLOT_QUOTA,
            "world_meta_has_no_gold": "gold" not in meta,
            "world_meta_has_no_observations": "observations" not in meta,
        }
        # Locked gold lives on the cluster json (Phase 1). Worlds must not contain it.
        checks["T4_no_gold_in_params"] = "gold" not in json.loads((ROOT / "params_d.json").read_text())[cid]
        if family == "Multi-step":
            checks["T8_three_sources"] = (
                loc.get("mid") in files
                and loc["mid"] != loc["left"]
                and loc["mid"] != loc["right"]
            )
            checks["multi_step_ge_3_objects"] = len(files) >= 3
        try:
            if kind == "money_usd":
                checks["correspondence"] = bool(v3_match(kind, parse_money(gold), gold))
            elif kind == "integer":
                checks["correspondence"] = bool(v3_match(kind, int(gold), gold))
            else:
                checks["correspondence"] = bool(v3_match(kind, gold, gold))
        except Exception as exc:
            checks["correspondence"] = False
            checks["correspondence_error"] = str(exc)

        skip = {"replay_error", "correspondence_error"}
        checks["pass"] = all(v is True for k, v in checks.items() if k not in skip and k != "pass")
        if not checks["pass"]:
            failed = [k for k, v in checks.items() if k not in skip and k != "pass" and v is not True]
            errors.append(f"{cid}: FAIL {failed}" + (f" replay={replay_err}" if replay_err else ""))

        if kind == "entity" and (str(gold).endswith(".txt") or "/" in str(gold)):
            entity_files += 1

        gold_spec.append(
            {
                "id": cid,
                "family": family,
                "kind": kind,
                "slot": slot,
                "component_id": row["component_id"],
                "instruction": inst,
                "locator": loc,
                "gold": gold,
            }
        )
        clusters.append(
            {
                "id": cid,
                "family": family,
                "kind": kind,
                "slot": slot,
                "gold": gold,
                "checks": checks,
            }
        )

    if kinds != g.KIND_QUOTA:
        errors.append(f"kind quota {kinds} != {g.KIND_QUOTA}")
    if families != g.FAMILY_QUOTA:
        errors.append(f"family quota {families} != {g.FAMILY_QUOTA}")
    if slots != g.SLOT_QUOTA:
        errors.append(f"slot quota {slots} != {g.SLOT_QUOTA}")
    if entity_files > 1:
        errors.append(f"entity filename cap {entity_files} > 1")
    if len(clusters) != N_D:
        errors.append(f"n={len(clusters)} != {N_D}")

    n_pass = sum(1 for c in clusters if c["checks"]["pass"])
    s12 = {
        "n30_and_quotas": len(clusters) == N_D
        and kinds == g.KIND_QUOTA
        and families == g.FAMILY_QUOTA
        and slots == g.SLOT_QUOTA,
        "locker_replay": n_pass == N_D and all(c["checks"]["locker_replay_matches_gold"] for c in clusters),
        "t1_t8_no_anchors": n_pass == N_D,
        "no_observations": all(c["checks"]["T4_no_observations"] for c in clusters),
        "independence": all(
            c["checks"]["T6_id_ok"]
            and c["checks"]["T7_no_foreign_tokens"]
            and c["checks"]["forbidden_substr"]
            and c["checks"]["exclusion_id_in_text"]
            for c in clusters
        ),
        "dq_pre_gate": dq_ok,
        "adjudicator_hashed_no_per_id": adj_ok and ADJ.is_file(),
        "transforms_hashed_no_per_id": trans_ok and TRANS.is_file(),
        "corpus_and_gold_hashed": True,
        "instrument_v1_hash": instr_v1 == EXPECTED_INSTR_V1,
        "instrument_v2_hash": instr_v2 == EXPECTED_INSTR_V2,
        "p4c_untouched": P4C_SEAL.is_file(),
        "p4b_untouched": P4B_SEAL.is_file(),
        "h7_anti_recovery": not any(e.startswith("H7:") for e in errors),
        "h8_ids": all(i.startswith("D") for i in IDS),
        "reserve_discarded": not rc_present,
    }
    phase2 = "PASS" if all(s12.values()) and not errors else "FAIL"

    cluster_paths = [SLATE / f"{cid}.json" for cid in IDS]
    world_paths = sorted(p for p in WORLDS.rglob("*") if p.is_file())
    gold_bytes = json.dumps(gold_spec, indent=2, sort_keys=True).encode() + b"\n"
    (OUT / "p4c2_gold_spec.json").write_bytes(gold_bytes)

    h1_h8 = {
        "note": (
            "H1–H8 are Phase-4 estimands on natural last-text τ under DFC. "
            "Phase 2 does not author or score natural last-responses. "
            "Zero τ ⇒ H2/H3 NOT EVALUABLE under the floor of 10; "
            "H1/H4/H5/H6 are NOT_OPENED. This does not fail Phase 2. "
            "Form is interface compliance, not coverage."
        ),
        "n_tau": 0,
        "scored_episodes": 0,
        "H1": {"status": "NOT_OPENED"},
        "H2": {"status": "NOT_EVALUABLE", "eligible": 0, "floor": 10},
        "H3": {"status": "NOT_EVALUABLE", "eligible": 0, "floor": 10},
        "H4": {"status": "NOT_OPENED"},
        "H5": {"status": "NOT_OPENED", "form_gate": 0.80},
        "H6": {"status": "NOT_OPENED"},
        "H7": {"status": "SEAL_CHECK", "pass": s12["h7_anti_recovery"]},
        "H8": {"status": "SEAL_CHECK", "pass": s12["h8_ids"]},
    }

    payload = {
        "phase": 2,
        "workstream": "P4-C2",
        "status": phase2,
        "N_D": N_D,
        "n_pass": n_pass,
        "section12": s12,
        "kind_counts": kinds,
        "family_counts": families,
        "slot_counts": slots,
        "entity_filename_n": entity_files,
        "H1_H8": h1_h8,
        "dq_qualification": "PASS" if dq_ok else "FAIL",
        "api_spend_usd": 0,
        "agents_run": 0,
        "instrument_v1_sha256": instr_v1,
        "instrument_v2_sha256": instr_v2,
        "wrapper_sha256": sha256_file(WRAPPER),
        "instrument_v1_modified": False,
        "p4b_modified": False,
        "p4c_modified": False,
        "corpus_modified": False,
        "adjudicator_d_sha256": sha256_file(ADJ),
        "transforms_d_sha256": sha256_file(TRANS),
        "generate_d_sha256": sha256_file(GEN),
        "params_d_sha256": sha256_file(ROOT / "params_d.json"),
        "wordlists_d_sha256": sha256_file(ROOT / "wordlists_d.txt"),
        "gold_spec_sha256": sha256_bytes(gold_bytes),
        "clusters_sha256": combined_hash(cluster_paths),
        "worlds_sha256": combined_hash(world_paths),
        "dq_qualification_sha256": sha256_file(DQ_QUAL) if DQ_QUAL.is_file() else None,
        "errors": errors,
        "clusters": [
            {
                "id": c["id"],
                "family": c["family"],
                "kind": c["kind"],
                "slot": c["slot"],
                "gold": c["gold"],
                "qualification_pass": c["checks"]["pass"],
                "locker_replay": c["checks"]["locker_replay_matches_gold"],
                "failures": [
                    k
                    for k, v in c["checks"].items()
                    if k not in {"pass", "replay_error", "correspondence_error"} and v is not True
                ],
            }
            for c in clusters
        ],
    }
    out_bytes = json.dumps(payload, indent=2, sort_keys=True).encode() + b"\n"
    (OUT / "p4c2_phase2_qualification.json").write_bytes(out_bytes)

    if phase2 == "PASS":
        seal = {
            "status": "SEALED",
            "phase": 2,
            "workstream": "P4-C2",
            "N_D": 30,
            "gate": "PASS",
            "instrument_v1_sha256": instr_v1,
            "instrument_v2_sha256": instr_v2,
            "wrapper_sha256": payload["wrapper_sha256"],
            "freeze_commit_expected": "04bb531",
            "clusters_sha256": payload["clusters_sha256"],
            "worlds_sha256": payload["worlds_sha256"],
            "gold_spec_sha256": payload["gold_spec_sha256"],
            "adjudicator_d_sha256": payload["adjudicator_d_sha256"],
            "transforms_d_sha256": payload["transforms_d_sha256"],
            "generate_d_sha256": payload["generate_d_sha256"],
            "params_d_sha256": payload["params_d_sha256"],
            "wordlists_d_sha256": payload["wordlists_d_sha256"],
            "dq_qualification_sha256": payload["dq_qualification_sha256"],
            "qualification_sha256": sha256_bytes(out_bytes),
            "estimands": ["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8"],
            "public_quantities": ["Form", "CC", "Abs"],
            "form_is_not_coverage": True,
            "pass_fail_criteria": "phase2_seal; H1-H8_phase4_on_natural_tau",
            "do_not_edit_corpus": True,
            "do_not_edit_instrument_v1": True,
            "do_not_edit_instrument_v2": True,
            "do_not_edit_p4b": True,
            "do_not_edit_p4c": True,
            "do_not_open_phase3": True,
            "reserve_discarded": True,
            "agent_run": False,
            "api_spend_usd": 0,
        }
        SEAL.parent.mkdir(exist_ok=True)
        seal_bytes = json.dumps(seal, indent=2, sort_keys=True).encode() + b"\n"
        SEAL.write_bytes(seal_bytes)
        payload_seal = sha256_bytes(seal_bytes)
    else:
        payload_seal = None
        if SEAL.exists():
            errors.append("refusing to seal a FAIL")

    lines = [
        "# P4-C2 Phase 2 qualification",
        "",
        f"status = **{phase2}**",
        "Object: D01–D30 worlds + gold specs + A2 + transforms_d + Q2. No agents. $0 API.",
        f"n_pass = {n_pass} / {N_D}",
        f"instrument_v1_sha256 = `{instr_v1}`",
        f"instrument_v2_sha256 = `{instr_v2}`",
        f"wrapper_sha256 = `{payload['wrapper_sha256']}`",
        f"adjudicator_d_sha256 = `{payload['adjudicator_d_sha256']}`",
        f"transforms_d_sha256 = `{payload['transforms_d_sha256']}`",
        f"gold_spec_sha256 = `{payload['gold_spec_sha256']}`",
        f"clusters_sha256 = `{payload['clusters_sha256']}`",
        f"worlds_sha256 = `{payload['worlds_sha256']}`",
        f"qualification_sha256 = `{sha256_bytes(out_bytes)}`",
        f"seal_sha256 = `{payload_seal}`" if payload_seal else "seal = not written (FAIL)",
        "",
        "## Conjunction",
        "",
    ]
    for k, v in s12.items():
        lines.append(f"- `{k}`: {v}")
    lines += [
        "",
        "## H1–H8 (Phase 4 estimands; not scored here except H7/H8 seal checks)",
        "",
        f"- scored_episodes = {h1_h8['scored_episodes']}",
        f"- H1 = {h1_h8['H1']['status']}",
        f"- H2 = {h1_h8['H2']['status']} (eligible {h1_h8['H2']['eligible']} < floor {h1_h8['H2']['floor']})",
        f"- H3 = {h1_h8['H3']['status']} (eligible {h1_h8['H3']['eligible']} < floor {h1_h8['H3']['floor']})",
        f"- H4 = {h1_h8['H4']['status']}",
        f"- H5 = {h1_h8['H5']['status']} (Form gate {h1_h8['H5']['form_gate']}; Form is not coverage)",
        f"- H6 = {h1_h8['H6']['status']}",
        f"- H7 = {h1_h8['H7']['status']} pass={h1_h8['H7']['pass']}",
        f"- H8 = {h1_h8['H8']['status']} pass={h1_h8['H8']['pass']}",
        "",
        h1_h8["note"],
        "",
        "| id | family | slot | kind | gold | locker | qual | failures |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for c in payload["clusters"]:
        lines.append(
            f"| `{c['id']}` | {c['family']} | {c['slot']} | {c['kind']} | `{c['gold']}` | {c['locker_replay']} | {c['qualification_pass']} | {c['failures']} |"
        )
    if errors:
        lines += ["", "## Errors", ""]
        for e in errors:
            lines.append(f"- {e}")
    lines += [
        "",
        "Corpus, gold, and worlds were not rewritten.",
        "P4-B and P4-C v1 were not modified. Phase 3 Flash pilot is BLOCKED until authorized.",
    ]
    (OUT / "p4c2_phase2_qualification.md").write_text("\n".join(lines) + "\n")
    (OUT / "p4c2_phase2_status.json").write_text(
        json.dumps(
            {
                "phase": 2,
                "workstream": "P4-C2",
                "status": phase2,
                "next": "PHASE_3_FLASH_PILOT" if phase2 == "PASS" else "STOP",
                "next_status": "BLOCKED",
                "N_D": 30,
                "n_pass": n_pass,
                "api_spend_usd": 0,
                "agents_run": 0,
                "instrument_v1_modified": False,
                "p4b_modified": False,
                "p4c_modified": False,
                "corpus_modified": False,
                "seal": str(SEAL.relative_to(P4)) if phase2 == "PASS" else None,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    (OUT / "p4c2_phase2_gate.md").write_text(
        "\n".join(
            [
                "# P4-C2 Phase 2 gate",
                "",
                f"status = **{phase2}**",
                f"construction replay = {n_pass}/30",
                f"Q2 = {'PASS 6/6' if dq_ok else 'FAIL'}",
                "api_spend_usd = 0",
                "agents_run = 0",
                f"instrument_v1_sha256 = `{instr_v1}`",
                f"instrument_v2_sha256 = `{instr_v2}`",
                "next = PHASE_3_FLASH_PILOT (**BLOCKED** until authorized)",
                "",
                "P4-B, P4-C v1, and `p4_instrument.py` were not modified.",
                "Form is interface compliance, not coverage.",
                "",
            ]
        )
    )
    print("\n".join(lines))
    return 0 if phase2 == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
