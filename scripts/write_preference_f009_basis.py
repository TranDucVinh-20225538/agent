#!/usr/bin/env python3
"""Write results/preference_f009_basis.md from archived cells."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CELLS = [
    ("0 baseline", ROOT / "results" / "pref-f009-0"),
    ("A count-flip", ROOT / "results" / "pref-f009-A"),
    ("B spend-flip", ROOT / "results" / "pref-f009-B"),
    ("A+B", ROOT / "results" / "pref-f009-AB"),
]


def last_done(traj: Path) -> str:
    if not traj.exists():
        return "(missing traj)"
    answer = ""
    for line in traj.read_text().splitlines():
        row = json.loads(line)
        if row.get("action") == "DONE":
            answer = row.get("response") or ""
    answer = re.sub(r"```DONE```", "", answer).strip()
    return answer.replace("\n", " ")[:400] or "(no DONE)"


def winners_from_guest(path: Path) -> tuple[str, str]:
    if not path.exists():
        return "?", "?"
    payload = json.loads(path.read_text())
    raw = payload.get("probe_after") or payload.get("probe_before")
    rows = json.loads(raw) if isinstance(raw, str) else raw
    if not rows:
        return "?", "?"
    by_n = sorted(rows, key=lambda r: (-int(r["n"]), -float(r["spend"] or 0)))
    by_s = sorted(rows, key=lambda r: (-float(r["spend"] or 0), -int(r["n"])))
    return by_n[0]["store"], by_s[0]["store"]


def score_of(cell: Path) -> str:
    p = cell / "scores.json"
    if not p.exists():
        return "n/a"
    return str(json.loads(p.read_text()).get("avg_score", "n/a"))


def main() -> None:
    lines = [
        "# preference_inference-f009 basis factorial",
        "",
        "Pinned rubric admits both order count and total spend. DV is the agent's named store, not the judge score.",
        "",
        "| Condition | Count winner | Spend winner | Agent answer | Judge score |",
        "|-----------|--------------|--------------|--------------|-------------|",
    ]
    for label, cell in CELLS:
        if not cell.exists():
            continue
        guests = list(cell.glob("*.guest.json"))
        count_w, spend_w = winners_from_guest(guests[0]) if guests else ("?", "?")
        traj = next(cell.glob("*/traj.jsonl"), None)
        answer = last_done(traj) if traj else "(not run)"
        lines.append(f"| {label} | {count_w} | {spend_w} | {answer} | {score_of(cell)} |")
    out = ROOT / "results" / "preference_f009_basis.md"
    out.write_text("\n".join(lines) + "\n")
    print(out.read_text())


if __name__ == "__main__":
    main()
