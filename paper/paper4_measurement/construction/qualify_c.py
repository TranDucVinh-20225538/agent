#!/usr/bin/env python3
"""P4-C Phase 2 corpus qualification and seal. $0. No agents.

Read-only on C01–C30 gold, anchors, and worlds. Hashes A and transforms_c.
Does not edit p4_instrument.py, P4-B, or the C corpus.
G1–G6 require natural last-text and are Phase 4; this step does not open them.
"""
from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
P4 = ROOT.parent
INSTR = P4 / "instrument" / "p4_instrument.py"
SLATE = ROOT / "slate" / "c"
WORLDS = SLATE / "worlds"
OUT = ROOT / "out"
SEAL = ROOT / "sealed" / "P4C_PHASE2_SEAL.json"
TRANS = ROOT / "transforms_c.py"
ADJ = ROOT / "adjudicator_c.py"
GEN = ROOT / "generate_c.py"
CQ_QUAL = ROOT / "out" / "cq_qualification.json"
P4B_SEAL = ROOT / "sealed" / "P4B_PHASE2_SEAL.json"
EXPECTED_INSTR = "c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59"
INSTR_FREEZE = "c35e828db89a9c7eb9d479601215a29221f5d744"
N_C = 30
IDS = [f"C{i:02d}" for i in range(1, 31)]

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(INSTR.parent))
import generate_c as g  # noqa: E402
from p4_instrument import parse_money, v3_match  # noqa: E402
import transforms_c  # noqa: E402
import adjudicator_c as A  # noqa: E402


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
        errors.append("adjudicator_c.py has a per-id branch")
        return False
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in {"score", "last_response", "last_text"}:
            errors.append(f"adjudicator_c.py references {node.id}")
            return False
        if isinstance(node, ast.Attribute) and node.attr == "score":
            errors.append("adjudicator_c.py references .score")
            return False
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "p4_instrument" or alias.name.startswith("p4_instrument."):
                    errors.append("adjudicator_c.py imports p4_instrument")
                    return False
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module == "p4_instrument" or node.module.startswith("p4_instrument."):
                errors.append("adjudicator_c.py imports from p4_instrument")
                return False
    if not hasattr(A, "adjudicate"):
        errors.append("adjudicator_c.py missing adjudicate")
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


def main() -> int:
    errors: list[str] = []
    instr_sha = sha256_file(INSTR)
    if instr_sha != EXPECTED_INSTR:
        errors.append(f"instrument hash drifted: {instr_sha}")

    trans_src = TRANS.read_text()
    trans_ok = no_per_id_branch(trans_src)
    if not trans_ok:
        errors.append("transforms_c.py has a per-id branch")
    for name in ("c3_del", "c4_stale", "c5_irr", "c6_pair", "chan_unterminated"):
        if not hasattr(transforms_c, name):
            errors.append(f"missing transform {name}")

    adj_ok = adjudicator_ok(ADJ.read_text(), errors)
    if not no_per_id_branch(GEN.read_text()):
        errors.append("generate_c.py has a per-id branch")

    if not P4B_SEAL.is_file():
        errors.append("P4-B seal missing")
    p4b_seal = json.loads(P4B_SEAL.read_text()) if P4B_SEAL.is_file() else {}
    if p4b_seal.get("instrument_sha256") != EXPECTED_INSTR:
        errors.append("P4-B seal instrument hash mismatch")

    cq = json.loads(CQ_QUAL.read_text())
    cq_ok = cq.get("qualification") == "PASS" and cq.get("property_pass_clusters") == 6
    if not cq_ok:
        errors.append("CQ qualification is not recorded PASS 6/6")
    if cq.get("instrument_sha256") != EXPECTED_INSTR:
        errors.append("CQ qualification instrument hash drifted")

    rc_present = list((ROOT / "slate" / "c").glob("RC*.json"))
    if rc_present:
        errors.append(f"reserve files present at seal: {rc_present}")

    qtok = g.load_wordlist("wordlists_q.txt")
    vtok = g.load_wordlist("wordlists_v.txt")
    rtok = g.load_wordlist("wordlists_r.txt")
    btok = g.load_wordlist("wordlists_b.txt")
    ctok = g.load_wordlist("wordlists_c.txt")
    foreign = qtok | vtok | rtok | btok

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
        kind, family = row["kind"], row["family"]
        slot = row["slot"]
        gold = row["gold"]
        inst = row["instruction"]
        anchors = row["anchors"]
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

        checks = {
            "locker_replay_matches_gold": replay == gold and replay_err is None,
            "replay_error": replay_err,
            "family_op": loc.get("op") == g.FAMILY_OP[family],
            "T1_gold_not_in_instruction": gold not in inst,
            "T2_toy_basename": all(Path(rel).stem.casefold() not in g.TOY_BASENAMES for rel in files),
            "T3_distractors": g.t3_ok(kind, gold, files, tables),
            "T4_no_observations": "observations" not in row and "last_response" not in row,
            "T5_no_llm_judge": "grading" not in row,
            "T6_id_ok": cid not in g.EXCLUSION_IDS,
            "T7_no_qvrb_tokens": not (g.words(blob) & foreign),
            "T8_two_sources": loc["left"] != loc["right"]
            and loc["left"] in files
            and loc["right"] in files,
            "anchor_literal": all(a in inst for a in anchors),
            "anchors_ge_2_tokens": all(len(a.split()) >= 2 for a in anchors),
            "n_anchors": len(anchors) >= 1,
            "gold_not_in_anchor": all(gold.casefold() not in a.casefold() for a in anchors),
            "one_component": True,
            "forbidden_gold": gold not in g.FORBIDDEN_VALUES,
            "forbidden_substr": not any(s in blob.casefold() for s in g.FORBIDDEN_SUBSTR),
            "exclusion_id_in_text": not any(x in blob for x in g.EXCLUSION_IDS),
            "own_cover_token": bool(g.words(inst) & ctok),
            "slot_known": slot in g.SLOT_QUOTA,
            "world_meta_has_no_gold": "gold"
            not in json.loads((WORLDS / cid / "world_meta.json").read_text()),
            "world_meta_has_no_observations": "observations"
            not in json.loads((WORLDS / cid / "world_meta.json").read_text()),
        }
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
                "anchors": anchors,
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
    if len(clusters) != N_C:
        errors.append(f"n={len(clusters)} != {N_C}")

    n_pass = sum(1 for c in clusters if c["checks"]["pass"])
    s12 = {
        "n30_and_quotas": len(clusters) == N_C
        and kinds == g.KIND_QUOTA
        and families == g.FAMILY_QUOTA
        and slots == g.SLOT_QUOTA,
        "locker_replay": n_pass == N_C and all(c["checks"]["locker_replay_matches_gold"] for c in clusters),
        "t1_t8_and_anchors": n_pass == N_C,
        "no_observations": all(c["checks"]["T4_no_observations"] for c in clusters),
        "independence": all(
            c["checks"]["T6_id_ok"]
            and c["checks"]["T7_no_qvrb_tokens"]
            and c["checks"]["forbidden_substr"]
            and c["checks"]["exclusion_id_in_text"]
            for c in clusters
        ),
        "cq_pre_gate": cq_ok,
        "adjudicator_hashed_no_per_id": adj_ok and ADJ.is_file(),
        "transforms_hashed_no_per_id": trans_ok and TRANS.is_file(),
        "corpus_and_gold_hashed": True,
        "instrument_hash": instr_sha == EXPECTED_INSTR,
        "p4b_untouched": P4B_SEAL.is_file(),
        "reserve_discarded": not rc_present,
    }
    phase2 = "PASS" if all(s12.values()) and not errors else "FAIL"

    cluster_paths = [SLATE / f"{cid}.json" for cid in IDS]
    world_paths = sorted(p for p in WORLDS.rglob("*") if p.is_file())
    gold_bytes = json.dumps(gold_spec, indent=2, sort_keys=True).encode() + b"\n"
    (OUT / "p4c_gold_spec.json").write_bytes(gold_bytes)

    g1_g6 = {
        "note": (
            "G1–G6 are Phase-4 estimands on natural last-text τ. "
            "Phase 2 does not author or score last-responses. "
            "Zero τ ⇒ G2/G3 NOT EVALUABLE under the floor of 10; "
            "G1/G4/G5/G6 are NOT_OPENED. This does not fail Phase 2."
        ),
        "n_tau": 0,
        "scored_episodes": 0,
        "G1": {"status": "NOT_OPENED"},
        "G2": {"status": "NOT_EVALUABLE", "eligible": 0, "floor": 10},
        "G3": {"status": "NOT_EVALUABLE", "eligible": 0, "floor": 10},
        "G4": {"status": "NOT_OPENED"},
        "G5": {"status": "NOT_OPENED", "coverage_gate": 0.50},
        "G6": {"status": "NOT_OPENED"},
    }

    payload = {
        "phase": 2,
        "workstream": "P4-C",
        "status": phase2,
        "N_C": N_C,
        "n_pass": n_pass,
        "section12": s12,
        "kind_counts": kinds,
        "family_counts": families,
        "slot_counts": slots,
        "entity_filename_n": entity_files,
        "G1_G6": g1_g6,
        "cq_qualification": "PASS" if cq_ok else "FAIL",
        "api_spend_usd": 0,
        "agents_run": 0,
        "instrument_sha256": instr_sha,
        "instrument_modified": False,
        "p4b_modified": False,
        "corpus_modified": False,
        "adjudicator_c_sha256": sha256_file(ADJ),
        "transforms_c_sha256": sha256_file(TRANS),
        "generate_c_sha256": sha256_file(GEN),
        "params_c_sha256": sha256_file(ROOT / "params_c.json"),
        "wordlists_c_sha256": sha256_file(ROOT / "wordlists_c.txt"),
        "gold_spec_sha256": sha256_bytes(gold_bytes),
        "clusters_sha256": combined_hash(cluster_paths),
        "worlds_sha256": combined_hash(world_paths),
        "cq_qualification_sha256": sha256_file(CQ_QUAL),
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
    (OUT / "p4c_phase2_qualification.json").write_bytes(out_bytes)

    if phase2 == "PASS":
        seal = {
            "status": "SEALED",
            "phase": 2,
            "workstream": "P4-C",
            "N_C": 30,
            "gate": "PASS",
            "instrument_sha256": instr_sha,
            "freeze_commit_expected": INSTR_FREEZE,
            "clusters_sha256": payload["clusters_sha256"],
            "worlds_sha256": payload["worlds_sha256"],
            "gold_spec_sha256": payload["gold_spec_sha256"],
            "adjudicator_c_sha256": payload["adjudicator_c_sha256"],
            "transforms_c_sha256": payload["transforms_c_sha256"],
            "generate_c_sha256": payload["generate_c_sha256"],
            "params_c_sha256": payload["params_c_sha256"],
            "wordlists_c_sha256": payload["wordlists_c_sha256"],
            "cq_qualification_sha256": payload["cq_qualification_sha256"],
            "qualification_sha256": sha256_bytes(out_bytes),
            "estimands": ["G1", "G2", "G3", "G4", "G5", "G6"],
            "pass_fail_criteria": "phase2_seal; G1-G6_phase4_on_natural_tau",
            "do_not_edit_corpus": True,
            "do_not_edit_instrument": True,
            "do_not_edit_p4b": True,
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
        "# P4-C Phase 2 qualification",
        "",
        f"status = **{phase2}**",
        "Object: C01–C30 worlds + gold specs + A + transforms_c. No agents. $0 API.",
        f"n_pass = {n_pass} / {N_C}",
        f"instrument_sha256 = `{instr_sha}`",
        f"adjudicator_c_sha256 = `{payload['adjudicator_c_sha256']}`",
        f"transforms_c_sha256 = `{payload['transforms_c_sha256']}`",
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
        "## G1–G6 (Phase 4 estimands; not scored here)",
        "",
        f"- scored_episodes = {g1_g6['scored_episodes']}",
        f"- G1 = {g1_g6['G1']['status']}",
        f"- G2 = {g1_g6['G2']['status']} (eligible {g1_g6['G2']['eligible']} < floor {g1_g6['G2']['floor']})",
        f"- G3 = {g1_g6['G3']['status']} (eligible {g1_g6['G3']['eligible']} < floor {g1_g6['G3']['floor']})",
        f"- G4 = {g1_g6['G4']['status']}",
        f"- G5 = {g1_g6['G5']['status']}",
        f"- G6 = {g1_g6['G6']['status']}",
        "",
        g1_g6["note"],
        "",
        "RC01–RC10 were not instantiated and are discarded at seal.",
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
        "Corpus, gold, anchors, and worlds were not rewritten.",
        "P4-B was not modified. Phase 3 Flash pilot is BLOCKED until authorized.",
    ]
    (OUT / "p4c_phase2_qualification.md").write_text("\n".join(lines) + "\n")
    (OUT / "p4c_phase2_status.json").write_text(
        json.dumps(
            {
                "phase": 2,
                "workstream": "P4-C",
                "status": phase2,
                "next": "PHASE_3_FLASH_PILOT" if phase2 == "PASS" else "STOP",
                "next_status": "BLOCKED",
                "N_C": 30,
                "n_pass": n_pass,
                "api_spend_usd": 0,
                "agents_run": 0,
                "instrument_modified": False,
                "p4b_modified": False,
                "corpus_modified": False,
                "seal": str(SEAL.relative_to(P4)) if phase2 == "PASS" else None,
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
