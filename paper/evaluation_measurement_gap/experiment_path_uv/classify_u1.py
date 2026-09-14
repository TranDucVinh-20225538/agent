#!/usr/bin/env python3
"""U1: n_screenshots vs frozen K. Not discard. Not E2. Not gold."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
PRIMARY_K = 5
SENS_K = (3, 5, 7)


def main() -> None:
    rows = [json.loads(l) for l in (OUT / "u1_meta.jsonl").read_text().splitlines() if l]
    cells = []
    for r in rows:
        n = int(r.get("n_screenshots") or 0)
        for k in SENS_K:
            cells.append(
                {
                    "split": r["split"],
                    "task_id": r.get("task_id") or "",
                    "K": k,
                    "n_screenshots": n,
                    "hit_cap": int(n > k),
                    "n_over": max(0, n - k),
                    "uv_outcome_success": r.get("uv_outcome_success"),
                    "final_human_outcome_label": r.get("final_human_outcome_label"),
                }
            )

    cell_path = OUT / "u1_cells.csv"
    with cell_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(cells[0].keys()))
        w.writeheader()
        w.writerows(cells)

    lines = [
        "# Path UV U1 RESULT — n_screenshots vs K (upper bound only)",
        "",
        "Not discard. Not E2. Not gold. `uv_*` unused as evidence.",
        f"Primary K={PRIMARY_K} (`max_images_per_criterion`). Sensitivity K={SENS_K}.",
        "hit_cap = n_screenshots > K. Union-across-criteria discard needs R (not released).",
        "",
    ]
    for split in ("fara7b_om2w_browserbase", "internal"):
        lines.append(f"## {split}")
        lines.append("")
        for k in SENS_K:
            sub = [c for c in cells if c["split"] == split and c["K"] == k]
            n_ep = len(sub)
            n_hit = sum(c["hit_cap"] for c in sub)
            tag = "PRIMARY" if k == PRIMARY_K else "sensitivity"
            ns = [c["n_screenshots"] for c in sub]
            lines.append(f"### K={k} ({tag})")
            lines.append("")
            lines.append(f"Episodes: {n_ep}. n > K: {n_hit}/{n_ep}.")
            if ns:
                lines.append(
                    f"n_screenshots min/median/max: {min(ns)} / {sorted(ns)[len(ns)//2]} / {max(ns)}."
                )
            lines.append("")
        lines.append("")

    (OUT / "u1_result.md").write_text("\n".join(lines))
    print((OUT / "u1_result.md").read_text())


if __name__ == "__main__":
    main()
