#!/usr/bin/env python3
"""Read-only P4-B pre-observation anti-circularity audit.

Does not edit instrument, gold, worlds, clusters, transforms, or the seal.
Does not call generate_b.main() (that regenerates worlds).
Does not import OpenRouter, score natural τ, or spend API money.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
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
GEN = ROOT / "generate_b.py"
PARAMS = ROOT / "params_b.json"
GOLD_SPEC = OUT / "p4b_gold_spec.json"
EXPECTED_INSTR = "c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59"
IDS = [f"B{i:02d}" for i in range(1, 21)]
KIND_QUOTA = {"money_usd": 8, "integer": 6, "entity": 3, "categorical": 3}
FAMILY_QUOTA = {"Locate": 4, "Compute": 4, "Reconcile": 4, "Filter": 4, "Tally": 4}
FAMILY_OP = {
    "Locate": "select_join",
    "Filter": "select_join",
    "Compute": "sum_join",
    "Tally": "count_join",
    "Reconcile": "live_not_stale",
}
OUTCOME_KEYS = {
    "observations",
    "last_response",
    "last_text",
    "tau",
    "status",
    "cause",
    "committed",
    "expected_status",
    "hit",
    "miss",
    "abstain",
}
TOKEN_RE = re.compile(r"[A-Za-z]+")

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(INSTR.parent))
import generate_b as g  # noqa: E402


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


def words(text: str) -> set[str]:
    return {m.group(0).casefold() for m in TOKEN_RE.finditer(text)}


def load_wordlist(name: str) -> set[str]:
    return {
        ln.strip().casefold()
        for ln in (ROOT / name).read_text().splitlines()
        if ln.strip()
    }


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


def ast_per_id_hits(src: str, path: str) -> list[str]:
    hits = []
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in {"task_id", "cluster_id"}:
            hits.append(f"{path}: Name {node.id} L{node.lineno}")
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value in IDS:
                hits.append(f"{path}: literal {node.value} L{node.lineno}")
    return hits


def outcome_keys_present(obj, path="$") -> list[str]:
    found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in OUTCOME_KEYS and k != "status":
                found.append(f"{path}.{k}")
            if k == "status" and path != "$" and "construction" not in path:
                # cluster top-level should not have a measurement status
                if path == "$":
                    found.append(f"{path}.status")
            found.extend(outcome_keys_present(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            found.extend(outcome_keys_present(v, f"{path}[{i}]"))
    return found


def main() -> int:
    errors: list[str] = []
    seal = json.loads(SEAL.read_text())
    instr_sha = sha256_file(INSTR)
    cluster_paths = [SLATE / f"{cid}.json" for cid in IDS]
    world_paths = sorted(p for p in WORLDS.rglob("*") if p.is_file())
    clusters_sha = combined_hash(cluster_paths)
    worlds_sha = combined_hash(world_paths)
    gold_spec = json.loads(GOLD_SPEC.read_text())
    gold_bytes = json.dumps(gold_spec, indent=2, sort_keys=True).encode() + b"\n"
    gold_sha = sha256_bytes(gold_bytes)
    trans_sha = sha256_file(TRANS)

    hash_ok = {
        "instrument": instr_sha == EXPECTED_INSTR == seal["instrument_sha256"],
        "clusters": clusters_sha == seal["clusters_sha256"],
        "worlds": worlds_sha == seal["worlds_sha256"],
        "gold_spec": gold_sha == seal["gold_spec_sha256"],
        "transforms": trans_sha == seal["transforms_b_sha256"],
        "seal_gate": seal.get("gate") == "PASS",
        "seal_n": seal.get("N_B") == 20,
        "seal_agents": seal.get("agent_run") is False and seal.get("api_spend_usd") == 0,
    }
    if not all(hash_ok.values()):
        errors.append(f"hash/seal mismatch: { {k: v for k, v in hash_ok.items() if not v} }")

    gen_hits = ast_per_id_hits(GEN.read_text(), "generate_b.py")
    trans_hits = ast_per_id_hits(TRANS.read_text(), "transforms_b.py")
    instr_hits = ast_per_id_hits(INSTR.read_text(), "p4_instrument.py")
    instr_src = INSTR.read_text()
    instr_forbids = {
        "no_B_ids": "B01" not in instr_src and "B20" not in instr_src,
        "no_mypcbench_ids": "retrieval-f020" not in instr_src,
        "no_task_id_branch_doc": "No task_id branch" in instr_src,
    }

    qtok = load_wordlist("wordlists_q.txt")
    vtok = load_wordlist("wordlists_v.txt")
    rtok = load_wordlist("wordlists_r.txt")
    btok = load_wordlist("wordlists_b.txt")
    wordlists = {
        "b_n": len(btok),
        "b_q": sorted(btok & qtok),
        "b_v": sorted(btok & vtok),
        "b_r": sorted(btok & rtok),
        "q_v": sorted(qtok & vtok),
        "q_r": sorted(qtok & rtok),
        "v_r": sorted(vtok & rtok),
        "b_tokens": sorted(btok),
    }
    if wordlists["b_q"] or wordlists["b_v"] or wordlists["b_r"]:
        errors.append("wordlists_b intersects Q/V/R")

    params = json.loads(PARAMS.read_text())
    if list(params) != IDS:
        errors.append("params_b keys != B01–B20")

    kinds: dict[str, int] = {}
    families: dict[str, int] = {}
    rows_out = []
    n_entity_filename = 0
    n_gold_as_cell = 0
    n_compute_gold_not_cell = 0

    for cid in IDS:
        cluster = json.loads((SLATE / f"{cid}.json").read_text())
        prow = params[cid]
        kind, family = cluster["kind"], cluster["family"]
        gold = cluster["gold"]
        inst = cluster["instruction"]
        anchors = cluster["anchors"]
        loc = cluster["locator"]
        kinds[kind] = kinds.get(kind, 0) + 1
        families[family] = families.get(family, 0) + 1

        files = load_world_files(cid)
        tables = {rel: parse_disk(WORLDS / cid / rel) for rel in files}
        replay = g.apply_locator(tables, loc, kind)
        meta = json.loads((WORLDS / cid / "world_meta.json").read_text())

        param_keys = set(prow)
        cluster_outcome = [
            k
            for k in cluster
            if k in {"observations", "last_response", "last_text", "expected_status", "tau"}
        ]
        cells = []
        for rel, recs in tables.items():
            for rec in recs:
                cells.extend(str(v) for v in rec.values())
        gold_in_cells = gold in cells
        if gold_in_cells:
            n_gold_as_cell += 1
        if family == "Compute" and not gold_in_cells:
            n_compute_gold_not_cell += 1
        if kind == "entity" and (str(gold).endswith(".txt") or "/" in str(gold)):
            n_entity_filename += 1

        blob = inst + "\n" + g.blob_of(files)
        cover_hits = sorted(words(inst) & btok)
        qvr_hits = sorted(words(blob) & (qtok | vtok | rtok))

        competing = []
        if family in {"Locate", "Reconcile"}:
            field = loc["field"]
            left_vals = [str(r.get(field, "")) for r in tables.get(loc["left"], [])]
            right_vals = [str(r.get(field, "")) for r in tables.get(loc["right"], [])]
            competing = sorted({v for v in left_vals + right_vals if v and v != str(gold)})

        row = {
            "id": cid,
            "family": family,
            "kind": kind,
            "op": loc["op"],
            "op_matches_family": loc["op"] == FAMILY_OP[family],
            "gold": gold,
            "replay": replay,
            "replay_matches": replay == gold,
            "n_world_files": len(files),
            "n_where": len(loc.get("left_where") or []) + len(loc.get("right_where") or []),
            "n_anchors": len(anchors),
            "anchors": anchors,
            "anchor_literal": all(a in inst for a in anchors),
            "gold_in_instruction": gold in inst,
            "gold_in_anchor": any(gold.casefold() in a.casefold() for a in anchors),
            "gold_in_world_meta": "gold" in meta,
            "gold_in_params": "gold" in prow,
            "locator_in_world_meta": "locator" in meta,
            "observations_in_cluster": cluster_outcome,
            "observations_in_params": [k for k in param_keys if k in OUTCOME_KEYS],
            "gold_in_cells": gold_in_cells,
            "competing_same_field": competing[:12],
            "n_competing_same_field": len(competing),
            "b_cover_in_instruction": cover_hits,
            "qvr_in_blob": qvr_hits,
            "sources": [loc["left"], loc["right"]],
            "distinct_sources": loc["left"] != loc["right"],
        }
        if not row["replay_matches"]:
            errors.append(f"{cid}: replay {replay} != gold {gold}")
        if not row["op_matches_family"]:
            errors.append(f"{cid}: op/family mismatch")
        if cluster_outcome:
            errors.append(f"{cid}: outcome keys {cluster_outcome}")
        rows_out.append(row)

    quota_ok = kinds == KIND_QUOTA and families == FAMILY_QUOTA
    if not quota_ok:
        errors.append(f"quota {kinds} {families}")
    if n_entity_filename > 1:
        errors.append(f"entity filename cap {n_entity_filename}")

    instr_imports = {
        "generate_b_imports_instrument": "from p4_instrument import parse_money, v3_match" in GEN.read_text(),
        "generate_b_does_not_import_mypcbench": "MyPCBench" not in GEN.read_text()
        and "all_tasks_with_grading" not in GEN.read_text(),
        "generate_b_exclusion_ids_are_blocklist_only": "retrieval-f020" in GEN.read_text(),
    }

    payload = {
        "audit": "P4-B pre-observation anti-circularity",
        "agents_run": 0,
        "api_spend_usd": 0,
        "read_only": True,
        "did_not_call_generate_b_main": True,
        "hash_ok": hash_ok,
        "hashes": {
            "instrument_sha256": instr_sha,
            "clusters_sha256": clusters_sha,
            "worlds_sha256": worlds_sha,
            "gold_spec_sha256": gold_sha,
            "transforms_b_sha256": trans_sha,
            "params_b_sha256": sha256_file(PARAMS),
            "generate_b_sha256": sha256_file(GEN),
            "wordlists_b_sha256": sha256_file(ROOT / "wordlists_b.txt"),
            "seal_file_sha256": sha256_file(SEAL),
        },
        "ast_per_id": {
            "generate_b.py": gen_hits,
            "transforms_b.py": trans_hits,
            "p4_instrument.py": instr_hits,
        },
        "instrument_forbids": instr_forbids,
        "instrument_imports": instr_imports,
        "wordlists": wordlists,
        "quotas": {"kinds": kinds, "families": families, "ok": quota_ok},
        "entity_filename_n": n_entity_filename,
        "n_gold_as_cell": n_gold_as_cell,
        "n_compute_gold_not_cell": n_compute_gold_not_cell,
        "n_replay_match": sum(1 for r in rows_out if r["replay_matches"]),
        "n_anchor_literal": sum(1 for r in rows_out if r["anchor_literal"]),
        "n_locator_in_world_meta": sum(1 for r in rows_out if r["locator_in_world_meta"]),
        "n_gold_in_params": sum(1 for r in rows_out if r["gold_in_params"]),
        "n_gold_in_world_meta": sum(1 for r in rows_out if r["gold_in_world_meta"]),
        "errors": errors,
        "clusters": rows_out,
    }
    OUT.mkdir(exist_ok=True)
    out_path = OUT / "p4b_anti_circularity_audit.json"
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: payload[k] for k in ("n_replay_match", "hash_ok", "quotas", "ast_per_id", "wordlists", "entity_filename_n", "n_gold_as_cell", "n_compute_gold_not_cell", "n_locator_in_world_meta", "n_gold_in_params", "errors", "agents_run", "api_spend_usd")}, indent=2))
    print(f"wrote {out_path}")
    return 0 if not errors and all(hash_ok.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
