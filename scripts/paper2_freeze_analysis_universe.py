#!/usr/bin/env python3
"""Freeze Paper 2 analysis universe from inject-probe gate outcomes; count N/legs.

No agent. Does not edit sealed_tasks / sealed_models / registry_semantic_frozen.
Reads gate reports + interventions; writes out/paper2_analysis_universe.*.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
INTER = ROOT / "cf" / "paper2_interventions.json"
MODELS = ROOT / "paper/paper2_counterfactual_eval/registry/sealed_models.json"
TASKS = ROOT / "paper/paper2_counterfactual_eval/registry/sealed_tasks.json"

GATE_SOURCES = [
    ("tier1", OUT / "paper2_tier1_probe_gate.json"),
    ("tier2", OUT / "paper2_tier2_probe_gate.json"),
    ("tier3", OUT / "paper2_tier3_probe_gate.json"),
    ("f003_i2", OUT / "paper2_f003_i2_probe_gate.json"),
]


def load_models() -> list[str]:
    doc = json.loads(MODELS.read_text())
    rows = doc.get("models") or doc.get("rows") or doc
    if isinstance(rows, dict):
        rows = rows.get("models") or list(rows.values())
    return [m["id"] if isinstance(m, dict) else m for m in rows]


def load_variant_rows() -> list[dict]:
    rows: list[dict] = []
    for src, path in GATE_SOURCES:
        if not path.is_file():
            continue
        doc = json.loads(path.read_text())
        if src == "f003_i2":
            r = doc.get("row") or {}
            if r:
                r = dict(r)
                r["source"] = src
                rows.append(r)
            continue
        for r in doc.get("rows") or []:
            rr = dict(r)
            rr["source"] = src
            rows.append(rr)
    return rows


def normalize_verdict(v: str) -> str:
    v = (v or "").strip()
    if v == "PASS":
        return "PASS"
    if v in ("REJECTED_NOT_IDENTIFIABLE", "needs_hand_D_design", "REJECT_identifiability"):
        return "REJECTED_NOT_IDENTIFIABLE" if "IDENTIFIABLE" in v.upper() or v.startswith("needs_") or v == "REJECT_identifiability" else v
    if v == "REJECT_held_leak":
        return "REJECT_held_leak"
    if v == "technical_failure":
        return "technical_failure"
    return v


def main() -> int:
    inter = json.loads(INTER.read_text())
    by_id = {e["id"]: e for e in inter["interventions"]}
    sealed = json.loads(TASKS.read_text())
    sealed_ids = [t["id"] for t in (sealed.get("tasks") or sealed.get("rows") or [])]

    raw = load_variant_rows()
    # Prefer latest row per task_id
    latest: dict[str, dict] = {}
    for r in raw:
        tid = r.get("task_id") or r.get("id")
        if not tid:
            continue
        r["verdict"] = normalize_verdict(r.get("verdict") or "")
        # f029 amendment may appear as REJECTED in interventions even if older row
        if tid == "situated_action-f029":
            r["verdict"] = "REJECTED_NOT_IDENTIFIABLE"
        latest[tid] = r

    # Ensure every intervention id with a gate-relevant status is represented
    for e in inter["interventions"]:
        tid = e["id"]
        st = e.get("_sql_status")
        if tid in latest:
            if st == "REJECTED_NOT_IDENTIFIABLE":
                latest[tid]["verdict"] = "REJECTED_NOT_IDENTIFIABLE"
            continue
        if st == "REJECTED_NOT_IDENTIFIABLE":
            latest[tid] = {
                "task_id": tid,
                "verdict": "REJECTED_NOT_IDENTIFIABLE",
                "source": "interventions",
            }
        elif st == "PENDING_FILE_BACKEND":
            latest[tid] = {
                "task_id": tid,
                "verdict": "PENDING_FILE_BACKEND",
                "source": "interventions",
            }

    variants = sorted(latest.values(), key=lambda r: r["task_id"])
    surviving = [r for r in variants if r.get("verdict") == "PASS"]
    rejected = [
        r
        for r in variants
        if r.get("verdict") in ("REJECTED_NOT_IDENTIFIABLE", "REJECT_identifiability", "REJECT_held_leak")
    ]
    pending = [r for r in variants if r.get("verdict") == "PENDING_FILE_BACKEND"]
    tech = [r for r in variants if r.get("verdict") == "technical_failure"]

    surviving_ids = [r["task_id"] for r in surviving]
    # Task universe: unique task_id (strip -I2) with ≥1 surviving variant
    def base_task(vid: str) -> str:
        return vid[:-3] if vid.endswith("-I2") else vid

    tasks_with_pass = sorted({base_task(i) for i in surviving_ids})
    # Multi-I extra leg: both bare id and -I2 survive
    multi_both = []
    for t in tasks_with_pass:
        if f"{t}-I2" in surviving_ids and t in surviving_ids:
            multi_both.append(t)

    models = load_models()
    m = len(models)
    n_tasks = len(tasks_with_pass)
    n_variants = len(surviving_ids)
    n_multi = len(multi_both)
    # PAPER2_SPEC Cost: legs ≈ |M|×|T|×2 + |M|×n_multiI
    legs = m * n_tasks * 2 + m * n_multi

    freeze = {
        "_status": "ANALYSIS_UNIVERSE_FROZEN",
        "_frozen_at": datetime.now(timezone.utc).isoformat(),
        "_source_gates": [str(p.relative_to(ROOT)) for _, p in GATE_SOURCES if p.is_file()],
        "_note": (
            "Surviving inject-probe variants only. Rejected variants contribute zero. "
            "Multi-I task stays in T if any variant PASSed; extra G2 leg only when both "
            "I1 and I2 PASS. No agent runs yet."
        ),
        "n_min": 3,
        "models": models,
        "n_models": m,
        "n_tasks": n_tasks,
        "n_surviving_variants": n_variants,
        "n_multi_i_both_pass": n_multi,
        "tasks": tasks_with_pass,
        "surviving_variants": surviving_ids,
        "multi_i_both_pass": multi_both,
        "rejected_variants": [
            {"id": r["task_id"], "verdict": r.get("verdict"), "source": r.get("source")}
            for r in rejected
        ],
        "pending_variants": [r["task_id"] for r in pending],
        "technical_failures": [r["task_id"] for r in tech],
        "legs": {
            "formula": "|M| * |T| * 2 + |M| * n_multiI",
            "M": m,
            "T": n_tasks,
            "n_multiI": n_multi,
            "base_paired": m * n_tasks * 2,
            "multi_i_extra": m * n_multi,
            "total": legs,
        },
        "sealed_task_count": len(sealed_ids),
        "sealed_minus_analysis": sorted(set(sealed_ids) - set(tasks_with_pass)),
    }

    OUT.mkdir(parents=True, exist_ok=True)
    json_path = OUT / "paper2_analysis_universe.json"
    json_path.write_text(json.dumps(freeze, indent=2) + "\n")

    csv_path = OUT / "paper2_analysis_universe.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["variant_id", "task_id", "verdict", "in_analysis", "source"],
        )
        w.writeheader()
        for r in variants:
            vid = r["task_id"]
            w.writerow(
                {
                    "variant_id": vid,
                    "task_id": base_task(vid),
                    "verdict": r.get("verdict"),
                    "in_analysis": vid in surviving_ids,
                    "source": r.get("source"),
                }
            )

    md = [
        "# Paper 2 — analysis universe (frozen after inject-probe)",
        "",
        f"Frozen {freeze['_frozen_at']}. No agent. Sealed semantic registry untouched.",
        "",
        f"- **|M|** = {m}: `{', '.join(models)}`",
        f"- **|T|** = {n_tasks} tasks with ≥1 PASS variant",
        f"- **Surviving variants** = {n_variants}",
        f"- **n_multiI** (I1+I2 both PASS) = {n_multi}: `{', '.join(multi_both) or '(none)'}`",
        f"- **Rejected** = {len(rejected)}: "
        + (", ".join(f"`{r['task_id']}`" for r in rejected) or "(none)"),
        f"- **Pending** = {len(pending)}: "
        + (", ".join(f"`{r}`" for r in freeze["pending_variants"]) or "(none)"),
        "",
        "## Legs (PAPER2_SPEC Cost)",
        "",
        f"`legs = |M|×|T|×2 + |M|×n_multiI = {m}×{n_tasks}×2 + {m}×{n_multi} = "
        f"**{legs}**`",
        "",
        f"- base paired: {m * n_tasks * 2}",
        f"- multi-I extra: {m * n_multi}",
        "",
        f"`n_min` = {freeze['n_min']} (unchanged).",
        "",
        "## Surviving variants",
        "",
    ]
    for vid in surviving_ids:
        md.append(f"- `{vid}`")
    md.extend(["", "## Tasks in analysis |T|", ""])
    for t in tasks_with_pass:
        md.append(f"- `{t}`")
    md.append("")

    (OUT / "paper2_analysis_universe.md").write_text("\n".join(md) + "\n")
    print(f"wrote {json_path}")
    print(f"wrote {csv_path}")
    print(f"wrote {OUT / 'paper2_analysis_universe.md'}")
    print(
        f"FREEZE |M|={m} |T|={n_tasks} variants={n_variants} "
        f"n_multiI={n_multi} legs={legs}"
    )
    if pending:
        print("WARNING: pending variants remain:", pending)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
