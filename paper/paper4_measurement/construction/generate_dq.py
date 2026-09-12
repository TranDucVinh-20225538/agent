#!/usr/bin/env python3
"""Assemble DQ01–DQ06 authored last-texts for P4-C2 Q2. $0. No agents.

No per-id branch. Does not call generate_slate (v1 anchor assembler).
Does not copy C/B last-texts. No anchors.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEST = ROOT / "slate" / "dq"
DQ_IDS = [f"DQ{i:02d}" for i in range(1, 7)]


def no_per_id_branch(src: str) -> bool:
    tree = ast.parse(src)
    banned = set(DQ_IDS)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in {"task_id", "cluster_id"}:
            return False
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value in banned:
                return False
    return True


def assemble(row: dict) -> dict:
    gold = row["gold"]
    wrong = row["wrong"]
    kind = row["kind"]
    working = row["working"].rstrip("\n")
    hit = f"{working}\n\nCLAIM: {gold}\n"
    obs = {
        "HIT_CLAIM": hit,
        "MISS_CLAIM": f"{working}\n\nCLAIM: {wrong}\n",
        "NO_CLAIM": f"{working}\n\nTotal in working: {gold}\n",
        "AMBIGUOUS_TWO": f"{working}\n\nCLAIM: {gold}\nCLAIM: {wrong}\n",
        "C3_NO_CLAIM": working.replace(gold, "[redacted]") + "\n",
        "C4_MARKUP": working.replace(gold, "")
        + f'\n<function=lookup>{{"q": "{gold}"}}</function>\n',
        "C5_WORKING": hit.rstrip("\n") + "\n" + row["c5_working"].strip() + "\n",
        "C6_WORKING": hit.rstrip("\n") + "\n" + row["c6_working"].strip() + "\n",
        "C6_CLAIM": f"{working}\n\nCLAIM: {wrong}\n",
    }
    extra = row.get("line_extra")
    if extra:
        obs["AMBIGUOUS_LINE"] = f"{working}\n\nCLAIM: {gold} ({extra})\n"
    out = {
        "id": None,
        "role": "qualification",
        "kind": kind,
        "component_id": row["component_id"],
        "instruction": row["instruction"],
        "gold": gold,
        "wrong": wrong,
        "observations": obs,
    }
    return out


def main() -> int:
    if not no_per_id_branch(Path(__file__).read_text()):
        raise SystemExit("generate_dq.py has a per-id branch")
    params = json.loads((ROOT / "params_dq.json").read_text())
    if list(params) != DQ_IDS:
        raise SystemExit(f"params_dq keys {list(params)} != {DQ_IDS}")
    DEST.mkdir(parents=True, exist_ok=True)
    for cid in DQ_IDS:
        row = params[cid]
        if "anchors" in row or "observations" in row:
            raise SystemExit(f"{cid}: forbidden param field")
        obj = assemble(row)
        obj["id"] = cid
        (DEST / f"{cid}.json").write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    print(f"wrote {len(DQ_IDS)} DQ clusters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
