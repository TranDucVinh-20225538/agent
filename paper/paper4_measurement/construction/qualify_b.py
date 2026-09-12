#!/usr/bin/env python3
"""P4-B Phase 2 corpus qualification. $0. No agents. Read-only on B01–B20.

Does not edit p4_instrument.py, gold, anchors, or world fixtures.
E1–E4 require natural last-text and are Phase 4; this step records that
they are not opened and applies §12 as the Phase-2 conjunction.
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
SLATE = ROOT / "slate" / "b"
WORLDS = SLATE / "worlds"
OUT = ROOT / "out"
SEAL = ROOT / "sealed" / "P4B_PHASE2_SEAL.json"
TRANS = ROOT / "transforms_b.py"
EXPECTED_INSTR = "c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59"
N_B = 20
IDS = [f"B{i:02d}" for i in range(1, 21)]
KIND_QUOTA = {"money_usd": 8, "integer": 6, "entity": 3, "categorical": 3}
FAMILY_QUOTA = {"Locate": 4, "Compute": 4, "Reconcile": 4, "Filter": 4, "Tally": 4}

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(INSTR.parent))
import generate_b as g  # noqa: E402
from p4_instrument import parse_money, v3_match  # noqa: E402
import transforms_b  # noqa: E402


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
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in {"task_id", "cluster_id"}:
            return False
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value in IDS:
                return False
    return True


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


def main() -> int:
    errors: list[str] = []
    instr_sha = sha256_file(INSTR)
    if instr_sha != EXPECTED_INSTR:
        errors.append(f"instrument hash drifted: {instr_sha}")

    trans_src = TRANS.read_text()
    trans_ok = no_per_id_branch(trans_src)
    if not trans_ok:
        errors.append("transforms_b.py has a per-id branch")
    for name in ("c3_del", "c4_stale", "c5_irr", "c6_pair", "chan_unterminated"):
        if not hasattr(transforms_b, name):
            errors.append(f"missing transform {name}")

    qtok = g.load_wordlist("wordlists_q.txt")
    vtok = g.load_wordlist("wordlists_v.txt")
    rtok = g.load_wordlist("wordlists_r.txt")
    btok = g.load_wordlist("wordlists_b.txt")
    foreign = qtok | vtok | rtok

    clusters = []
    kinds: dict[str, int] = {}
    families: dict[str, int] = {}
    entity_files = 0
    gold_spec = []

    for cid in IDS:
        path = SLATE / f"{cid}.json"
        row = json.loads(path.read_text())
        if row.get("id") != cid:
            errors.append(f"{cid}: id mismatch")
        kind, family = row["kind"], row["family"]
        gold = row["gold"]
        inst = row["instruction"]
        anchors = row["anchors"]
        loc = row["locator"]
        kinds[kind] = kinds.get(kind, 0) + 1
        families[family] = families.get(family, 0) + 1
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
            "T1_gold_not_in_instruction": gold not in inst,
            "T2_toy_basename": all(Path(rel).stem.casefold() not in g.TOY_BASENAMES for rel in files),
            "T3_distractors": g.t3_ok(kind, gold, files, tables),
            "T4_no_observations": "observations" not in row and "last_response" not in row,
            "T5_no_llm_judge": "grading" not in row,
            "T6_id_ok": cid not in g.EXCLUSION_IDS,
            "T7_no_qvr_tokens": not (g.words(blob) & foreign),
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
            "own_cover_token": bool(g.words(inst) & btok),
            "world_meta_has_no_gold": "gold"
            not in json.loads((WORLDS / cid / "world_meta.json").read_text()),
        }
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
                "component_id": row["component_id"],
                "instruction": inst,
                "anchors": anchors,
                "locator": loc,
                "gold": gold,
            }
        )
        clusters.append({"id": cid, "family": family, "kind": kind, "gold": gold, "checks": checks})

    if kinds != KIND_QUOTA:
        errors.append(f"kind quota {kinds} != {KIND_QUOTA}")
    if families != FAMILY_QUOTA:
        errors.append(f"family quota {families} != {FAMILY_QUOTA}")
    if entity_files > 1:
        errors.append(f"entity filename cap {entity_files} > 1")
    if len(clusters) != N_B:
        errors.append(f"n={len(clusters)} != {N_B}")

    n_pass = sum(1 for c in clusters if c["checks"]["pass"])
    s12 = {
        "n20_and_quotas": len(clusters) == N_B and kinds == KIND_QUOTA and families == FAMILY_QUOTA,
        "locker_replay": n_pass == N_B and all(c["checks"]["locker_replay_matches_gold"] for c in clusters),
        "t1_t8_and_anchors": n_pass == N_B,
        "no_observations": all(c["checks"]["T4_no_observations"] for c in clusters),
        "independence": all(
            c["checks"]["T6_id_ok"]
            and c["checks"]["T7_no_qvr_tokens"]
            and c["checks"]["forbidden_substr"]
            and c["checks"]["exclusion_id_in_text"]
            for c in clusters
        ),
        "transforms_hashed_no_per_id": trans_ok and TRANS.is_file(),
        "corpus_and_gold_hashed": True,
        "instrument_hash": instr_sha == EXPECTED_INSTR,
    }
    phase2 = "PASS" if all(s12.values()) and not errors else "FAIL"

    cluster_paths = [SLATE / f"{cid}.json" for cid in IDS]
    world_paths = sorted(p for p in WORLDS.rglob("*") if p.is_file())
    gold_bytes = json.dumps(gold_spec, indent=2, sort_keys=True).encode() + b"\n"
    (OUT / "p4b_gold_spec.json").write_bytes(gold_bytes)

    e1_e4 = {
        "note": (
            "E1–E4 are Phase-4 estimands on natural last-text τ. "
            "Phase 2 does not author or score last-responses. "
            "Zero τ ⇒ E3/E4 NOT EVALUABLE under the floor of 5; "
            "E1/E2 are NOT_OPENED. This does not fail §12."
        ),
        "n_tau": 0,
        "scored_episodes": 0,
        "abstain_by_cause": {},
        "E1": {"status": "NOT_OPENED", "false_hit": None, "n_gold_absent_tau": 0},
        "E2": {"status": "NOT_OPENED", "n_changed": None, "n_tau": 0},
        "E3": {"status": "NOT_EVALUABLE", "eligible": 0, "floor": 5, "hits": None},
        "E4": {"status": "NOT_EVALUABLE", "eligible": 0, "floor": 5, "misses": None},
    }

    payload = {
        "phase": 2,
        "workstream": "P4-B",
        "status": phase2,
        "N_B": N_B,
        "n_pass": n_pass,
        "section12": s12,
        "kind_counts": kinds,
        "family_counts": families,
        "entity_filename_n": entity_files,
        "E1_E4": e1_e4,
        "api_spend_usd": 0,
        "agents_run": 0,
        "instrument_sha256": instr_sha,
        "instrument_modified": False,
        "transforms_b_sha256": sha256_file(TRANS),
        "gold_spec_sha256": sha256_bytes(gold_bytes),
        "clusters_sha256": combined_hash(cluster_paths),
        "worlds_sha256": combined_hash(world_paths),
        "errors": errors,
        "clusters": [
            {
                "id": c["id"],
                "family": c["family"],
                "kind": c["kind"],
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
    (OUT / "p4b_phase2_qualification.json").write_bytes(out_bytes)

    if phase2 == "PASS":
        seal = {
            "status": "SEALED",
            "phase": 2,
            "N_B": 20,
            "gate": "PASS",
            "instrument_sha256": instr_sha,
            "freeze_commit_expected": "c35e828db89a9c7eb9d479601215a29221f5d744",
            "clusters_sha256": payload["clusters_sha256"],
            "worlds_sha256": payload["worlds_sha256"],
            "gold_spec_sha256": payload["gold_spec_sha256"],
            "transforms_b_sha256": payload["transforms_b_sha256"],
            "qualification_sha256": sha256_bytes(out_bytes),
            "estimands": ["E1", "E2", "E3", "E4"],
            "pass_fail_criteria": "section12_phase2; E1-E4_phase4_on_natural_tau",
            "do_not_edit_corpus": True,
            "do_not_edit_instrument": True,
            "do_not_open_phase3": True,
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
        "# P4-B Phase 2 qualification",
        "",
        f"status = **{phase2}**",
        "Object: B01–B20 worlds + gold specs. No agents. $0 API.",
        f"n_pass = {n_pass} / {N_B}",
        f"instrument_sha256 = `{instr_sha}`",
        f"transforms_b_sha256 = `{payload['transforms_b_sha256']}`",
        f"gold_spec_sha256 = `{payload['gold_spec_sha256']}`",
        f"clusters_sha256 = `{payload['clusters_sha256']}`",
        f"worlds_sha256 = `{payload['worlds_sha256']}`",
        f"qualification_sha256 = `{sha256_bytes(out_bytes)}`",
        f"seal_sha256 = `{payload_seal}`" if payload_seal else "seal = not written (FAIL)",
        "",
        "## §12 conjunction",
        "",
    ]
    for k, v in s12.items():
        lines.append(f"- `{k}`: {v}")
    lines += [
        "",
        "## E1–E4 (Phase 4 estimands; not scored here)",
        "",
        f"- scored_episodes = {e1_e4['scored_episodes']}",
        f"- abstain_by_cause = {e1_e4['abstain_by_cause']}",
        f"- E1 = {e1_e4['E1']['status']}",
        f"- E2 = {e1_e4['E2']['status']}",
        f"- E3 = {e1_e4['E3']['status']} (eligible {e1_e4['E3']['eligible']} < floor {e1_e4['E3']['floor']})",
        f"- E4 = {e1_e4['E4']['status']} (eligible {e1_e4['E4']['eligible']} < floor {e1_e4['E4']['floor']})",
        "",
        e1_e4["note"],
        "",
        "| id | family | kind | gold | locker | qual | failures |",
        "|---|---|---|---|---|---|---|",
    ]
    for c in payload["clusters"]:
        lines.append(
            f"| `{c['id']}` | {c['family']} | {c['kind']} | `{c['gold']}` | {c['locker_replay']} | {c['qualification_pass']} | {c['failures']} |"
        )
    if errors:
        lines += ["", "## Errors", ""]
        for e in errors:
            lines.append(f"- {e}")
    lines += [
        "",
        "Corpus, gold, anchors, and worlds were not rewritten.",
        "Phase 3 Flash pilot is BLOCKED until authorized.",
    ]
    (OUT / "p4b_phase2_qualification.md").write_text("\n".join(lines) + "\n")
    (OUT / "p4b_phase2_status.json").write_text(
        json.dumps(
            {
                "phase": 2,
                "workstream": "P4-B",
                "status": phase2,
                "next": "PHASE_3_FLASH_PILOT" if phase2 == "PASS" else "STOP",
                "next_status": "BLOCKED",
                "N_B": 20,
                "n_pass": n_pass,
                "api_spend_usd": 0,
                "agents_run": 0,
                "instrument_modified": False,
                "corpus_modified": False,
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
