#!/usr/bin/env python3
"""Write results/sa009_basis.md from archived cells."""

from __future__ import annotations

import json
import re
from pathlib import Path

sys_path_setup = True
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sa009_dynamic  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CELLS = [
    ("0 baseline", ROOT / "results" / "sa009-0"),
    ("A modal-flip", ROOT / "results" / "sa009-A"),
    ("B recency-flip", ROOT / "results" / "sa009-B"),
]


def last_done(traj: Path) -> str:
    if not traj.exists():
        return "(missing traj)"
    answer = ""
    for line in traj.read_text().splitlines():
        row = json.loads(line)
        if row.get("action") == "DONE":
            answer = row.get("response") or ""
    return re.sub(r"```DONE```", "", answer).strip().replace("\n", " ")[:400] or "(no DONE)"


def snapshot(guest: Path) -> str:
    payload = json.loads(guest.read_text())
    raw = payload.get("probe_after") or payload.get("probe_before")
    if not isinstance(raw, str):
        raw = json.dumps(raw)
    orders = sa009_dynamic.parse_orders(raw)
    if not orders:
        return "no Chili's orders"
    counts = sa009_dynamic.frequencies(orders)
    modal, n0, runner, n1 = sa009_dynamic.modal_and_runner(counts)
    recent = orders[0]["items"]
    return f"modal={modal} n={n0}; recent={recent}"


def score_of(cell: Path) -> str:
    p = cell / "scores.json"
    if not p.exists():
        return "n/a"
    return str(json.loads(p.read_text()).get("avg_score", "n/a"))


def main() -> None:
    lines = [
        "# situated_action-f009 modal vs recency",
        "",
        "DV is the Chili's item the agent tries to order, not checkout success and not the judge score.",
        "",
        "| Condition | History | Agent answer | Judge score |",
        "|-----------|---------|--------------|-------------|",
    ]
    for label, cell in CELLS:
        if not cell.exists():
            continue
        guests = list(cell.glob("*.guest.json"))
        hist = snapshot(guests[0]) if guests else "?"
        traj = next(cell.glob("*/traj.jsonl"), None)
        answer = last_done(traj) if traj else "(not run)"
        lines.append(f"| {label} | {hist} | {answer} | {score_of(cell)} |")
    out = ROOT / "results" / "sa009_basis.md"
    out.write_text("\n".join(lines) + "\n")
    print(out.read_text())


if __name__ == "__main__":
    main()
