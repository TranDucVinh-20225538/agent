"""Draft Paper 2 registry rows: D, kind, role, w_i per sealed task (PAPER2_SPEC step 2).

Runs BEFORE inject-probe (PAPER2_SPEC step 3) and before any agent run.
Output is a DRAFT for human review, never an auto-freeze.

Frozen design rules for this script (2026-09-03, in response to the
Round-31 dilution concern — see decision doc Round 35/36):

  DESIGN.md keeps its own default: w_i=1 for every `determining` and
  `held` component, w_i=0 for `distractor`. That default is not touched
  here. Dilution is handled by keeping D NARROW, not by re-weighting:

  1. This script drafts `determining` components ONLY. A candidate is a
     rubric criterion that pins a specific value/record on a field the
     intervention is expected to move (a reportable quantity: a dollar
     figure, a count, a named record/identifier, a status/tier) as
     opposed to a pure action/process/style criterion.
  2. `held` is NEVER auto-drafted. It is added by hand, later, only when
     the instruction/rubric requires some OTHER field to be correct on
     BOTH legs and that field is untouched by I (the retrieval-f030
     pattern: 1099 amount+payer held while charitable moves). Promoting
     "the rest of the rubric" to held is exactly the failure mode this
     rule blocks.
  3. Every rubric criterion this script does not draft as `determining`
     is recorded in `omitted_rubric_ids` with a reason
     (`action_gate` | `style` | `not_in_D`). STS is not the whole
     rubric.
  4. `distractor` is NEVER auto-drafted either (needs world knowledge of
     what else exists and is deliberately left alone, e.g. GME on
     retrieval-f016 in Paper 1). Left as an empty list with a TODO note.
  5. w_i is role-based per DESIGN.md §2 (1 for determining/held, 0 for
     distractor) — this script does not invent per-component weights.
     Any hand exception must be written on the row BEFORE inject-probe,
     never after seeing D-hat.
  6. Soft cap: if a task drafts more than 4 positive (`determining`)
     components, or zero, the row is marked `needs_review` and is not
     eligible for auto-freeze.

`gold_path` (the guest-probe key each component will be checked against)
is left null here — it depends on the intervention SQL, which is
PAPER2_SPEC step 3 (inject-probe), not this step.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from evidence_screen import load_pinned  # noqa: E402

REGISTRY_DIR = ROOT / "paper" / "paper2_counterfactual_eval" / "registry"
SEALED_TASKS_PATH = REGISTRY_DIR / "sealed_tasks.json"
OUT_JSON = REGISTRY_DIR / "registry_rows_draft.json"
OUT_MD = REGISTRY_DIR / "registry_rows_draft.md"

POSITIVE_CAP = 4

# --- value/record detection (drives inclusion as a `determining` candidate) ---

IDENTIFIER_RE = re.compile(
    r"confirmation number|account number|reference number|policy number|"
    r"booking record|property name|payer\b",
    re.I,
)
CATEGORICAL_RE = re.compile(r"\btier\b|\bstatus\b|\bcategory\b|\bcabin class\b", re.I)
COUNT_RE = re.compile(
    r"\bmiles?\b|\blatency\b|\bnumber of\b|\bcount\b|\btimestamps?\b|\bdays?\b",
    re.I,
)
MONEY_RE = re.compile(
    r"\$|\btotal\b|\bcost\b|\bprice\b|\bdamage\b|\bfee\b|\brefund\b|\bbasis\b|"
    r"\bbalance\b|\bamounts?\b|\bfigure\b|\bexposure\b|\bdollar\b",
    re.I,
)
VALUE_ANY_RE = re.compile(
    "|".join(
        p.pattern
        for p in (IDENTIFIER_RE, CATEGORICAL_RE, COUNT_RE, MONEY_RE)
    ),
    re.I,
)

# --- exclusion-reason detection (for criteria NOT drafted as determining) ---

STYLE_RE = re.compile(
    r"\btone\b|\bvoice\b|\bframes?\b|\bpersona\b|\bover-the-top\b|\bin michael'?s voice\b",
    re.I,
)
ACTION_GATE_RE = re.compile(
    r"\bopens?\b(?!.{0,40}(reads|reporting))|\blocates?\b(?!.{0,40}(reads|reporting))|"
    r"\bsaves?\b|\bsends?\b|\bpersist\b|\battach(es|ed|ing)?\b|\badds? (at least )?five\b|"
    r"\bcites?\b|\bciting\b|\bcross-references?\b$",
    re.I,
)


def classify_component(criterion: str) -> dict | None:
    """Return a draft `determining` component dict, or None (not a candidate)."""
    if VALUE_ANY_RE.search(criterion):
        if IDENTIFIER_RE.search(criterion):
            kind = "entity"
        elif CATEGORICAL_RE.search(criterion):
            kind = "categorical"
        elif COUNT_RE.search(criterion) and not MONEY_RE.search(criterion):
            kind = "integer"
        else:
            kind = "money_usd"
        return {"kind": kind, "kind_basis": "heuristic_keyword_match"}
    return None


def classify_omit_reason(criterion: str) -> str:
    if STYLE_RE.search(criterion):
        return "style"
    if ACTION_GATE_RE.search(criterion):
        return "action_gate"
    return "not_in_D"


def draft_task_row(task: dict, pinned: dict) -> dict:
    tid = task["id"]
    pin = pinned.get(tid) or {}
    rubrics = (pin.get("grading") or {}).get("rubrics") or []

    components = []
    omitted = []
    for idx, r in enumerate(rubrics):
        criterion = r.get("criterion", "")
        c = classify_component(criterion)
        cid = f"{tid}.c{idx}"
        if c is not None:
            components.append(
                {
                    "id": cid,
                    "rubric_index": idx,
                    "kind": c["kind"],
                    "kind_basis": c["kind_basis"],
                    "role": "determining",
                    "weight": 1,
                    "gold_path": None,
                    "gold_path_note": "TBD at inject-probe design (PAPER2_SPEC step 3)",
                    "criterion": criterion,
                    "rubric_weight": r.get("weight"),
                }
            )
        else:
            omitted.append(
                {
                    "rubric_index": idx,
                    "reason": classify_omit_reason(criterion),
                    "criterion": criterion,
                    "rubric_weight": r.get("weight"),
                }
            )

    needs_review = []
    if len(components) > POSITIVE_CAP:
        needs_review.append(f"cap_gt{POSITIVE_CAP}_determining({len(components)})")
    if len(components) == 0:
        needs_review.append("zero_candidates")

    return {
        "id": tid,
        "category": task.get("category"),
        "state_family": task.get("state_family"),
        "apps": task.get("apps"),
        "mapped_dbs": task.get("mapped_dbs"),
        "n_rubric_criteria": len(rubrics),
        "determining": components,
        "held": [],
        "held_note": (
            "Not auto-drafted (rule 2). Add by hand only if instruction/rubric "
            "requires another field correct on BOTH legs and that field is not "
            "touched by I (retrieval-f030 pattern)."
        ),
        "distractor": [],
        "distractor_note": (
            "Not auto-drafted (rule 4). Add by hand if a field is in the world, "
            "unscored by the rubric (or scored but not in D), and deliberately "
            "left untouched (retrieval-f016 GME pattern)."
        ),
        "omitted_rubric_ids": omitted,
        "needs_review": needs_review,
        "_status": "DRAFT_NOT_FROZEN",
    }


def build_manifest(rows: list[dict]) -> str:
    n = len(rows)
    n_review = sum(1 for r in rows if r["needs_review"])
    n_clean = n - n_review
    total_det = sum(len(r["determining"]) for r in rows)
    lines = [
        "# Paper 2 registry rows — draft (D, kind, role, w_i)",
        "",
        "DRAFT, not frozen. Per-row human review required before any row is",
        "used for inject-probe design. Rules this draft follows (frozen",
        "2026-09-03): draft `determining` only from rubric criteria that pin a",
        "specific value/record; never auto-draft `held` or `distractor`;",
        "every non-drafted criterion is recorded under `omitted_rubric_ids`",
        "with a reason; w_i is role-based (1 for determining/held, 0 for",
        "distractor) per DESIGN.md §2, not re-derived here; rows with 0 or",
        f">{POSITIVE_CAP} determining candidates are flagged `needs_review` and",
        "excluded from auto-freeze.",
        "",
        f"- Tasks: **{n}**",
        f"- Clean (0 flags, still needs a human pass for `held`/`distractor`): **{n_clean}**",
        f"- `needs_review`: **{n_review}**",
        f"- Total drafted `determining` components: **{total_det}**",
        "",
        "## Rows",
        "",
        "| id | category | rubric criteria | determining (draft) | omitted | needs_review |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for r in rows:
        flags = "; ".join(r["needs_review"]) if r["needs_review"] else ""
        lines.append(
            f"| {r['id']} | {r['category']} | {r['n_rubric_criteria']} | "
            f"{len(r['determining'])} | {len(r['omitted_rubric_ids'])} | {flags} |"
        )
    lines += [
        "",
        "## needs_review detail",
        "",
    ]
    any_review = False
    for r in rows:
        if not r["needs_review"]:
            continue
        any_review = True
        lines.append(f"### {r['id']} — {', '.join(r['needs_review'])}")
        lines.append("")
        if r["determining"]:
            for c in r["determining"]:
                lines.append(f"- determining candidate `{c['id']}` ({c['kind']}): {c['criterion']}")
        else:
            lines.append("- (no determining candidates drafted — needs hand design)")
        lines.append("")
    if not any_review:
        lines.append("(none)")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    sealed = json.loads(SEALED_TASKS_PATH.read_text())
    tasks = sealed["tasks"]
    pinned = load_pinned()

    rows = [draft_task_row(t, pinned) for t in tasks]

    out = {
        "_status": "DRAFT_NOT_FROZEN",
        "_spec": "PAPER2_SPEC.md step 2 (registry rows), before step 3 (inject-probe)",
        "_rules_frozen_at": "2026-09-03",
        "_positive_cap": POSITIVE_CAP,
        "_source_sealed_tasks": str(SEALED_TASKS_PATH.relative_to(ROOT)),
        "n_tasks": len(rows),
        "n_needs_review": sum(1 for r in rows if r["needs_review"]),
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2) + "\n")
    OUT_MD.write_text(build_manifest(rows))

    print(f"drafted {len(rows)} rows -> {OUT_JSON.relative_to(ROOT)}")
    print(f"needs_review: {out['n_needs_review']}")
    print(f"wrote {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
