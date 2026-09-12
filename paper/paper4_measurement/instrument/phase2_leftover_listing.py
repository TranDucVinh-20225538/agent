#!/usr/bin/env python3
"""P4 Phase-2 leftover listing L. IDs and categories only. No gold-lock. No agents."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P4 = Path(__file__).resolve().parents[1]
TASKS = ROOT / "external" / "MyPCBench-main" / "tasks" / "final" / "all_tasks_with_grading.json"
CELL_ORDER = ROOT / "out" / "paper2_cell_order.json"
PAPER1 = ROOT / "paper" / "paper2_counterfactual_eval" / "registry" / "paper1_replay.json"
GATE = ROOT / "out" / "p3_cohort_probe" / "gate.json"
OUT = P4 / "construction" / "out"

PREFIX_OR_CATEGORY = (
    "situated_action",
    "long_horizon",
    "cua_only",
    "hard_app",
)
PREF_PREFIX = "preference_inference"
P3_SLATE_28 = [
    "aggregation-f004",
    "aggregation-f036",
    "aggregation-f040",
    "contradiction-f003",
    "contradiction-f011",
    "contradiction-f014",
    "contradiction-f017",
    "contradiction-f022",
    "counterfactual-f001",
    "counterfactual-f002",
    "counterfactual-f003",
    "retrieval-f005",
    "aggregation-f001",
    "aggregation-f002",
    "aggregation-f005",
    "aggregation-f008",
    "aggregation-f009",
    "aggregation-f010",
    "aggregation-f011",
    "aggregation-f019",
    "aggregation-f023",
    "aggregation-f029",
    "aggregation-f030",
    "aggregation-f031",
    "aggregation-f033",
    "contradiction-f005",
    "contradiction-f008",
    "contradiction-f012",
]
C7 = [
    "counterfactual-f010",
    "preference_inference-f014",
    "retrieval-f002",
    "retrieval-f009",
]
F024 = "contradiction-f024"


def prefix_of(task_id: str) -> str:
    return task_id.split("-", 1)[0]


def main() -> None:
    universe = [
        {"id": t["id"], "category": t["category"]}
        for t in json.loads(TASKS.read_text())
    ]
    study2 = list(json.loads(CELL_ORDER.read_text())["order"])
    paper1 = [t["id"] for t in json.loads(PAPER1.read_text())["tasks"]]
    gate = json.loads(GATE.read_text())
    survivors16 = list(gate["survivors_wave_a"]) + list(gate["survivors_wave_b"])

    excluded_ids = {
        "study2_25": set(study2),
        "c7_four": set(C7),
        "p3_slate_28": set(P3_SLATE_28),
        "p3_survivors_16": set(survivors16),
        "paper1_10": set(paper1),
        "contradiction_f024": {F024},
    }
    id_union = set().union(*excluded_ids.values())

    leftover = []
    dropped = []
    for row in universe:
        tid, cat = row["id"], row["category"]
        reasons = []
        if tid in excluded_ids["study2_25"]:
            reasons.append("study2_25")
        if tid in excluded_ids["c7_four"]:
            reasons.append("c7_four")
        if tid in excluded_ids["p3_slate_28"]:
            reasons.append("p3_slate_28")
        if tid in excluded_ids["p3_survivors_16"]:
            reasons.append("p3_survivors_16")
        if tid in excluded_ids["paper1_10"]:
            reasons.append("paper1_10")
        if tid == F024:
            reasons.append("contradiction_f024")
        if prefix_of(tid) == PREF_PREFIX:
            reasons.append("preference_inference_prefix")
        if prefix_of(tid) in PREFIX_OR_CATEGORY:
            reasons.append("id_prefix_gui_or_long")
        if cat in PREFIX_OR_CATEGORY:
            reasons.append("category_gui_or_long")
        if reasons:
            dropped.append({"id": tid, "category": cat, "reasons": reasons})
        else:
            leftover.append({"id": tid, "category": cat})

    leftover.sort(key=lambda r: r["id"])
    L = len(leftover)
    opened = L >= 8
    n_a = min(L, 20) if opened else None
    payload = {
        "universe_n": len(universe),
        "pinned_task_file": str(TASKS.relative_to(ROOT)),
        "L": L,
        "gate_L_ge_8": opened,
        "N_A": n_a,
        "phase2": "openable_before_gold_lock" if opened else "closed",
        "gold_lock_run": False,
        "agent_run": False,
        "api_spend_usd": 0,
        "leftover_lexicographic": leftover,
        "exclusion_set_sizes": {k: len(v) for k, v in excluded_ids.items()},
        "dropped_n": len(dropped),
        "note": "IDs and categories only. No gold-lock. No usefulness filter.",
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "phase2_leftover.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    lines = [
        "# P4 Phase-2 leftover listing L",
        "",
        "Mechanical §4.1 subtraction from the pinned 184-task file.",
        "No gold-lock. No agents. No usefulness filter.",
        "",
        f"Universe n = {len(universe)}",
        f"**L = {L}**",
        f"Gate L ≥ 8 = **{'PASS' if opened else 'FAIL'}**",
        f"N_A = {n_a if n_a is not None else 'n/a (Phase 2 closed)'}",
        f"Phase 2 = **{'not opened for gold-lock this step; L≥8 so N_A=min(L,20) is declared' if opened else 'CLOSED, $0'}**",
        "",
        "## Leftover IDs (lexicographic)",
        "",
    ]
    if leftover:
        for r in leftover:
            lines.append(f"- `{r['id']}` ({r['category']})")
    else:
        lines.append("- (empty)")
    lines += ["", "## Exclusion-set sizes", ""]
    for k, n in payload["exclusion_set_sizes"].items():
        lines.append(f"- {k}: {n}")
    lines.append(f"- dropped rows: {len(dropped)}")
    (OUT / "phase2_leftover.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
