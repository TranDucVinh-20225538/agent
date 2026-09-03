"""Seal Paper 2 model list and task universe (PAPER2_SPEC steps 2–3).

Eligibility flags are computed with the same logic as evidence_screen.py
(APP_DB, GUI_RE, MONEY_RE, cua_required from rubrics) — not read from
m0_scan.json, which does not store those fields.

Paper 2 §4 drops channel_invariant and evidence_type_other requirements.
"""

from __future__ import annotations

import json
import random
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from evidence_screen import load_pinned, screen_one  # noqa: E402

OUT_DIR = ROOT / "paper" / "paper2_counterfactual_eval" / "registry"

# Pre-registered. Must differ from evidence_screen.SEED (20260826).
MULTI_I_SEED = 20260903

# PAPER2_SPEC §3: >=4 CUAs, >=2 providers, >=1 open-weight hosted lane.
SEALED_MODELS = [
    {
        "id": "claude-opus-4-6",
        "agent_type": "claude_cuabash",
        "provider": "anthropic",
        "note": "Paper 1 primary; harness validated",
    },
    {
        "id": "gpt-5.5",
        "agent_type": "openai_cuabash",
        "provider": "openai",
        "note": "Paper 1 primary; harness validated",
    },
    {
        "id": "qwen/qwen3.8-flash",
        "agent_type": "qwen_cuabash",
        "provider": "openrouter",
        "note": (
            "Open-weight hosted; replaces Qwen3.5-35B-A3B per PAPER2_SPEC.md "
            "§3 amendment (2026-09-03) — execution feasibility/budget, "
            "before any Paper 2 execution, not a Paper 2 outcome."
        ),
    },
    {
        "id": "qwen/qwen3.5-9b",
        "agent_type": "qwen_cuabash",
        "provider": "openrouter",
        "note": "4th model satisfies §3 minimum; size ablation lane",
    },
]

# Observed harness wall times (TCG, Intel Mac). See seal_manifest.md.
WALL_MIN_OBSERVED = 12  # results/counterfactual_report.md retrieval-f001
WALL_MAX_OBSERVED = 32  # Round 24 mixed Paper 1 universe (internal log)


def load_paper1_excluded() -> set[str]:
    reg = json.loads((ROOT / "cf" / "phase_b_registry.json").read_text())
    return {t["task_id"] for t in reg["tasks"]}


def paper2_eligible(row: dict, paper1_ids: set[str]) -> tuple[bool, list[str]]:
    """PAPER2_SPEC §4 — six rules."""
    reasons: list[str] = []
    if not row["sqlite_mapped"]:
        reasons.append("no_mapped_sqlite")
    if row["cua_required"]:
        reasons.append("cua_required")
    if row["gui_artifact"]:
        reasons.append("gui_artifact")
    if row["instruction_pins_gold"]:
        reasons.append("instruction_pins_gold")
    if not row["dv_from_answer"]:
        reasons.append("not_dv_from_answer")
    if row["id"] in paper1_ids:
        reasons.append("in_paper1_ten")
    return (not reasons, reasons)


def assign_state_family(task: dict, pin: dict) -> tuple[str, str]:
    """Return (family, rationale) — heuristic, tagged before any agent run."""
    cat = task.get("category") or ""
    inst = (task.get("instruction") or "").lower()
    rubrics = (pin.get("grading") or {}).get("rubrics", [])
    rubric_text = " ".join(r.get("criterion", "") for r in rubrics).lower()
    combined = inst + " " + rubric_text

    if cat == "aggregation":
        return "aggregation", "category=aggregation → derived total"
    if cat == "preference_inference":
        return "preference_recommendation", "category=preference_inference → entity"

    temporal_markers = (
        "most recent",
        "latest",
        "current year",
        "this year",
        "last year",
        "newest",
        "upcoming",
    )
    if any(m in inst for m in temporal_markers):
        return "temporal", f"instruction temporal cue: {next(m for m in temporal_markers if m in inst)}"

    if cat in {"contradiction", "counterfactual"} and any(
        w in combined for w in ("both", "all agree", "cross-source", "two sources", " and ")
    ):
        return "relational_joint", f"category={cat} with multi-source / joint cue"

    categorical_markers = (
        "tier",
        "status",
        "loyalty",
        "gold",
        "silver",
        "category",
        "level",
    )
    if any(m in inst for m in categorical_markers):
        return "categorical", f"instruction categorical cue"

    if cat == "situated_action":
        return "relational_joint", "situated_action → joint state / action gate"

    numeric_markers = ("$", "miles", "shares", "balance", "total", "amount", "count")
    if any(m in combined for m in numeric_markers):
        return "numeric", "money_usd / integer stress in instruction or rubric"

    if cat == "retrieval":
        return "numeric", "retrieval default → numeric field read"

    if cat in {"contradiction", "counterfactual"}:
        return "relational_joint", f"category={cat} default → cross-source joint"

    return "numeric", "fallback → numeric (review if ambiguous)"


def select_multi_i(task_ids: list[str], seed: int) -> list[str]:
    n = min(8, (len(task_ids) * 25 + 99) // 100)  # ceil(0.25 * |T|)
    rng = random.Random(seed)
    pool = sorted(task_ids)
    return sorted(rng.sample(pool, n))


def build_manifest(
    *,
    sealed_tasks: list[dict],
    multi_i: list[str],
    funnel: dict,
) -> str:
    n_models = len(SEALED_MODELS)
    n_tasks = len(sealed_tasks)
    base_legs = n_models * n_tasks * 2
    multi_legs = n_models * len(multi_i)
    total_legs = base_legs + multi_legs

    family_counts = Counter(t["state_family"] for t in sealed_tasks)
    cat_counts = Counter(t["category"] for t in sealed_tasks)

    lines = [
        "# Paper 2 seal manifest",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} UTC",
        f"Spec: `paper/paper2_counterfactual_eval/PAPER2_SPEC.md`",
        f"Multi-I seed: `{MULTI_I_SEED}` (not `20260826`)",
        "",
        "## Sealed models (§3)",
        "",
        f"**{n_models} models** — satisfies minimum ≥4 CUAs, ≥2 providers, ≥1 open-weight.",
        "",
        "| id | agent_type | provider |",
        "| --- | --- | --- |",
    ]
    for m in SEALED_MODELS:
        lines.append(f"| `{m['id']}` | `{m['agent_type']}` | {m['provider']} |")

    lines += [
        "",
        "Qwen 9B added as 4th model so Layer B retains ≥3 ranked agents if one "
        "model falls below `n_min=3` valid pairs. Qwen3.5-35B-A3B replaced by "
        "Qwen3.8-Flash per the `PAPER2_SPEC.md` §3 amendment log (2026-09-03) "
        "— execution feasibility/budget, before any Paper 2 execution, not a "
        "Paper 2 outcome (see PAPER2_SPEC.md §3 for the full amendment text).",
        "",
        "## Sealed task universe (§4)",
        "",
        f"**{n_tasks} tasks** — all eligible under Paper 2 §4 (no channel_invariant).",
        f"Paper 1 ten excluded via `cf/phase_b_registry.json`.",
        "",
        "### Exclusion funnel (not mutually exclusive)",
        "",
        "| reason | n |",
        "| --- | ---: |",
    ]
    for reason, count in sorted(funnel["exclude_counts"].items(), key=lambda x: -x[1]):
        lines.append(f"| `{reason}` | {count} |")
    lines += [
        "",
        f"- Eligible: **{funnel['eligible']}** / {funnel['screened']} screened",
        "",
        "### By category",
        "",
        "| category | n |",
        "| --- | ---: |",
    ]
    for cat, count in sorted(cat_counts.items()):
        lines.append(f"| {cat} | {count} |")

    lines += [
        "",
        "### By state family (pre-run tags)",
        "",
        "| state_family | n |",
        "| --- | ---: |",
    ]
    for fam, count in sorted(family_counts.items()):
        lines.append(f"| {fam} | {count} |")

    lines += [
        "",
        "## Multi-I subset (§4 robustness)",
        "",
        f"**{len(multi_i)} tasks** get an extra G₂ leg "
        f"(min(8, ⌈0.25×{n_tasks}⌉) = {len(multi_i)}):",
        "",
    ]
    for tid in multi_i:
        lines.append(f"- `{tid}`")

    lines += [
        "",
        "## Leg count (§ Cost)",
        "",
        f"- Base paired legs: |M| × |T| × 2 = {n_models} × {n_tasks} × 2 = **{base_legs}**",
        f"- Multi-I extra: |M| × {len(multi_i)} = {n_models} × {len(multi_i)} = **{multi_legs}**",
        f"- **Total ≈ {total_legs} legs**",
        "",
        "### Wall-time estimate (planning only)",
        "",
        "Sources (TCG, no KVM — same harness as Paper 1):",
        "",
        f"- Floor **~{WALL_MIN_OBSERVED} min/leg**: `results/counterfactual_report.md` "
        "(retrieval-f001 base + CF harness wall, Aug 2026).",
        f"- Ceiling **~{WALL_MAX_OBSERVED} min/leg**: Round 24 mixed Paper 1 universe "
        "(internal run log; aggregation/contradiction tasks run longer).",
        "",
        f"Planning range **{WALL_MIN_OBSERVED}–{WALL_MAX_OBSERVED} min/leg** → "
        f"**~{total_legs * WALL_MIN_OBSERVED // 60}–{total_legs * WALL_MAX_OBSERVED // 60} hours** "
        f"serial wall time ({total_legs} legs). Parallelism depends on host/QEMU slots.",
        "",
        "## Next (PAPER2_SPEC)",
        "",
        "1. ~~Agree spec~~ · ~~Seal lists~~ (this file)",
        "2. Registry rows: D, kind, role, wᵢ per task (before inject-probe)",
        "3. Inject-probe identifiability on sealed universe",
        "4. Agent runs (no ID changes after outcomes)",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    tasks = json.loads((ROOT / "out" / "m0_scan.json").read_text())
    pinned = load_pinned()
    paper1_ids = load_paper1_excluded()

    # All-invariant set: only used so screen_one computes flags, not Paper 1 eligibility.
    all_ids = {t["id"] for t in tasks}

    screened: list[dict] = []
    exclude_counter: Counter[str] = Counter()

    for task in tasks:
        row = screen_one(task, pinned, all_ids)
        ok, reasons = paper2_eligible(row, paper1_ids)
        for r in reasons:
            exclude_counter[r] += 1
        pin = pinned.get(task["id"]) or {}
        family, family_rationale = assign_state_family(task, pin)
        screened.append(
            {
                **row,
                "paper2_eligible": ok,
                "paper2_exclude_reason": "|".join(reasons),
                "state_family": family,
                "state_family_rationale": family_rationale,
            }
        )

    eligible = [r for r in screened if r["paper2_eligible"]]
    eligible.sort(key=lambda r: r["id"])

    if len(eligible) != 27:
        print(f"WARNING: expected 27 eligible, got {len(eligible)}", file=sys.stderr)
        for r in eligible:
            print(f"  {r['id']}", file=sys.stderr)

    multi_i = select_multi_i([r["id"] for r in eligible], MULTI_I_SEED)

    sealed_tasks = []
    for r in eligible:
        sealed_tasks.append(
            {
                "id": r["id"],
                "category": r["category"],
                "state_family": r["state_family"],
                "state_family_rationale": r["state_family_rationale"],
                "apps": r["apps"],
                "mapped_dbs": r["mapped_dbs"],
                "multi_i_extra_leg": r["id"] in multi_i,
                "instruction_summary": (r["instruction"] or "")[:200],
            }
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    models_doc = {
        "_status": "sealed",
        "_sealed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "_spec": "paper/paper2_counterfactual_eval/PAPER2_SPEC.md §3",
        "_rationale": (
            "Four models satisfy §3 minimum. Qwen 9B added (not 3-model set) "
            "to preserve meaningful Layer B ranking if one model drops below "
            "n_min=3. Qwen3.5-35B-A3B replaced by Qwen3.8-Flash per the "
            "PAPER2_SPEC.md §3 amendment log (2026-09-03), before any Paper 2 "
            "execution."
        ),
        "models": SEALED_MODELS,
    }
    (OUT_DIR / "sealed_models.json").write_text(json.dumps(models_doc, indent=2) + "\n")

    tasks_doc = {
        "_status": "sealed",
        "_sealed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "_spec": "paper/paper2_counterfactual_eval/PAPER2_SPEC.md §4",
        "_multi_i_seed": MULTI_I_SEED,
        "_paper1_excluded": sorted(paper1_ids),
        "n_tasks": len(sealed_tasks),
        "tasks": sealed_tasks,
    }
    (OUT_DIR / "sealed_tasks.json").write_text(json.dumps(tasks_doc, indent=2) + "\n")

    funnel = {
        "screened": len(screened),
        "eligible": len(eligible),
        "exclude_counts": dict(exclude_counter),
    }
    manifest = build_manifest(sealed_tasks=sealed_tasks, multi_i=multi_i, funnel=funnel)
    (OUT_DIR / "seal_manifest.md").write_text(manifest + "\n")

    print(f"screened {len(screened)}  paper2_eligible {len(eligible)}  multi_i {len(multi_i)}")
    print(f"models {len(SEALED_MODELS)}  legs ≈ {len(SEALED_MODELS) * len(eligible) * 2 + len(SEALED_MODELS) * len(multi_i)}")
    print(f"wrote {OUT_DIR / 'sealed_models.json'}")
    print(f"wrote {OUT_DIR / 'sealed_tasks.json'}")
    print(f"wrote {OUT_DIR / 'seal_manifest.md'}")
    for t in sealed_tasks:
        flag = " [multi-I]" if t["multi_i_extra_leg"] else ""
        print(f"  {t['id']:<35} {t['state_family']:<28}{flag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
