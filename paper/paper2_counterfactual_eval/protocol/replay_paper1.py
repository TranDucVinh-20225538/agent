#!/usr/bin/env python3
"""Replay STS on Paper 1's 24 valid pairs. No agent runs."""

from __future__ import annotations

import csv
import json
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "protocol"))

from matching import (  # noqa: E402
    AlignmentCell,
    Component,
    Kind,
    Role,
    alignment_cell,
    binary_track,
    sts_leg,
)

PAPER1_CLASS = {
    "type_a": AlignmentCell.TYPE_A,
    "sensitive": AlignmentCell.SCORE_SENSITIVE,
    "type_b": AlignmentCell.TYPE_B,
}


def load_components() -> dict[str, list[Component]]:
    raw = json.loads((ROOT / "registry" / "paper1_replay.json").read_text())
    out: dict[str, list[Component]] = {}
    for task in raw["tasks"]:
        comps = []
        for c in task["components"]:
            kk = tuple((k, Kind(v)) for k, v in c.get("key_kinds", {}).items())
            comps.append(
                Component(
                    id=c["id"],
                    kind=Kind(c["kind"]),
                    role=Role(c["role"]),
                    key_kinds=kk,
                )
            )
        out[task["id"]] = comps
    return out


def main() -> int:
    comps_by_task = load_components()
    bits = json.loads((ROOT / "registry" / "paper1_component_bits.json").read_text())["pairs"]
    pairs_path = REPO / "out" / "stage4_counterfactual_analysis_final" / "paired_results.csv"
    out_dir = ROOT / "out"
    out_dir.mkdir(exist_ok=True)

    rows_out = []
    mismatches = []
    with pairs_path.open() as f:
        for row in csv.DictReader(f):
            key = f"{row['model']}\t{row['task']}"
            if key not in bits:
                raise SystemExit(f"missing component bits for {key!r}")
            comps = comps_by_task[row["task"]]
            m0, m1 = bits[key]["m0"], bits[key]["m1"]
            sts0 = sts_leg(comps, m0)
            sts1 = sts_leg(comps, m1)
            sts = (sts0 + sts1) / 2
            track = binary_track(comps, m0, m1)
            s0, s1 = int(row["base_score"]), int(row["cf_score"])
            cell = alignment_cell(track=track, s0=s0, s1=s1)
            paper1 = PAPER1_CLASS[row["classification"]]
            ok = cell == paper1
            if not ok:
                mismatches.append((key, paper1.value, cell.value))
            rows_out.append(
                {
                    "model": row["model"],
                    "tier": row["tier"],
                    "task": row["task"],
                    "S0": s0,
                    "S1": s1,
                    "delta_S": s1 - s0,
                    "STS0": format(sts0, "f"),
                    "STS1": format(sts1, "f"),
                    "STS": format(sts, "f"),
                    "track": int(track),
                    "alignment": cell.value,
                    "paper1_class": row["classification"],
                    "class_match": ok,
                }
            )

    csv_path = out_dir / "paper1_sts_replay.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
        w.writeheader()
        w.writerows(rows_out)

    partial = [r for r in rows_out if Decimal(r["STS"]) < 1]
    md = [
        "# Paper 1 STS replay (no new runs)",
        "",
        f"Pairs: **{len(rows_out)}**. Component bits from `tracking_evidence.md`.",
        f"Alignment cell vs Paper 1 class: **{len(rows_out) - len(mismatches)}/{len(rows_out)}** match.",
        "",
        "Do not headline a pooled STS. Partial STS (pair mean < 1):",
        "",
        "| Model | Task | STS0 | STS1 | STS | cell | Paper 1 |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for r in partial:
        md.append(
            f"| {r['model']} | {r['task']} | {r['STS0']} | {r['STS1']} | {r['STS']} | {r['alignment']} | {r['paper1_class']} |"
        )
    md.append("")
    md_path = out_dir / "paper1_sts_replay.md"
    md_path.write_text("\n".join(md) + "\n")

    print(f"wrote {csv_path}")
    print(f"wrote {md_path}")
    print(f"pairs={len(rows_out)} class_match={len(rows_out) - len(mismatches)}")
    for r in partial:
        print(
            f"  partial {r['model']} {r['task']} STS={r['STS']} "
            f"({r['STS0']}/{r['STS1']}) {r['alignment']}"
        )
    if mismatches:
        print("MISMATCH", mismatches)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
