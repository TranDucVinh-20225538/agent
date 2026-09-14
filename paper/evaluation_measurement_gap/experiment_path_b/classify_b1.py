#!/usr/bin/env python3
"""B1: reconstruct WebJudge keep-list discard. Outcome-blind on final_eval.

Does not treat Score as gold. Does not open B2.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "out"
MAX_IMAGE = 50
PRIMARY_T = 3
SENS_T = (2, 3, 4)
AGENTS = [
    "agente_results.json",
    "browser_use_results.json",
    "claude_computer_use_3.5_results.json",
    "claude_computer_use_3.7_results.json",
    "operator_results.json",
    "seeact_results.json",
]


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    text = path.read_text()
    if text.lstrip().startswith("["):
        return json.loads(text)
    for line in text.splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def scores(rec: dict) -> list[int]:
    items = rec.get("image_judge_record") or []
    out = []
    for it in items:
        if isinstance(it, dict) and "Score" in it:
            try:
                out.append(int(it["Score"]))
            except (TypeError, ValueError):
                out.append(0)
    return out


def classify_episode(sc: list[int], t: int) -> dict:
    qualified_idx = [i for i, s in enumerate(sc) if s >= t]
    n_q = len(qualified_idx)
    n_keep = min(n_q, MAX_IMAGE)
    n_disc = max(0, n_q - MAX_IMAGE)
    return {
        "n_scored": len(sc),
        "n_qualified": n_q,
        "n_keep": n_keep,
        "n_discard": n_disc,
        "hit_cap": int(n_q > MAX_IMAGE),
    }


def main() -> None:
    OUT.mkdir(exist_ok=True)
    cells = []
    for agent in AGENTS:
        path = DATA / agent
        recs = load_jsonl(path)
        for rec in recs:
            sc = scores(rec)
            tid = rec.get("task_id") or rec.get("id") or ""
            for t in SENS_T:
                c = classify_episode(sc, t)
                cells.append(
                    {
                        "agent_file": agent,
                        "task_id": tid,
                        "T": t,
                        **c,
                    }
                )

    cell_path = OUT / "b1_cells.csv"
    with cell_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(cells[0].keys()))
        w.writeheader()
        w.writerows(cells)

    lines = [
        "# Path B1 RESULT — instrument-internal discard",
        "",
        "Not E2. Not gold. `Score` is the judge's own intermediate mark.",
        f"`MAX_IMAGE={MAX_IMAGE}`. Primary T={PRIMARY_T}. Sensitivity T={SENS_T}.",
        "DISCARD = qualified frames after the first 50. Threshold misses are not DISCARD.",
        "",
    ]
    for t in SENS_T:
        sub = [r for r in cells if r["T"] == t]
        n_ep = len(sub)
        n_hit = sum(r["hit_cap"] for r in sub)
        n_disc_fr = sum(r["n_discard"] for r in sub)
        n_qual = sum(r["n_qualified"] for r in sub)
        by_agent = Counter()
        hit_agent = Counter()
        for r in sub:
            by_agent[r["agent_file"]] += 1
            hit_agent[r["agent_file"]] += r["hit_cap"]
        tag = "PRIMARY" if t == PRIMARY_T else "sensitivity"
        lines.append(f"## T={t} ({tag})")
        lines.append("")
        lines.append(f"Episodes: {n_ep}. Cap hits: {n_hit}.")
        lines.append(
            f"Qualified frames: {n_qual}. Discarded after cap: {n_disc_fr}."
        )
        if n_qual:
            lines.append(
                f"Discard / qualified: {n_disc_fr}/{n_qual} = {n_disc_fr/n_qual:.4f}."
            )
        lines.append("Cap hits by agent file:")
        for k in AGENTS:
            lines.append(f"- {k}: {hit_agent[k]}/{by_agent[k]}")
        lines.append("")

    (OUT / "b1_result.md").write_text("\n".join(lines) + "\n")
    print((OUT / "b1_result.md").read_text())


if __name__ == "__main__":
    main()
