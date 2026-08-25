"""Milestone 0 screening pass over the MyPCBench task set.

For every rubric criterion, ask one question: what makes this criterion true?

  value    the criterion names the target value, so a counterfactual on the
           seed also requires editing the rubric text
  record   the criterion requires reading or computing over the persona's
           records, so the criterion text survives a counterfactual and the
           judge has to recompute the target
  action   the criterion is satisfied by performing an interface side effect
           (post, send, create, save, navigate) and no personal record
           determines whether it passes
  style    the criterion is a tone or quality judgement
  unclear  none of the above matched; needs a human read

Precedence is value > record > style > action, because a criterion such as
"adds the same items from Michael's most recent order" is both an action and
record-determined, and the record dependence is what an intervention can move.

The benchmark's own `type` field is uniformly "llm_judge", so the grading
instrument carries no label of its own about evidence kind.

Weights matter: rubric weights sum to 1 per task, and the headline "perfect"
metric requires every criterion to pass.
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "mypcbench"
OUT = ROOT / "out"

RECORD = re.compile(
    r"""(?:
        (?:order|browsing|purchase|ride|transaction|payment|reply|chat|search)\s+history
      | \bhistory\b
      | ledger | transactions | statement | seeded | saved\s+(?:address|payment|card|location)
      | as\s+read\s+from | grounded\s+in | cross[-\s]references? | reconcile
      | enumerates | pairs\s+them | computes? .{0,40}\bfrom\b | reads?\s+(?:off|from)
      | matches?\s+(?:his|her|the\s+persona) | Michael'?s | his\s+(?:usual|typical|prior|past)
      | most[-\s](?:recent|frequent|common) | modal | median | \bmean\b | average
      | \busual\b | typical | prior\s+(?:order|booking|trip) | past\s+\w+
      | existing | actual\s+(?:per-session|amount|charge|balance)
      | from\s+the\s+(?:document|file|booking|profile|contacts?|calendar|inbox)
    )""",
    re.I | re.X,
)

ACTION = re.compile(
    r"""^\s*(?:Agent\s+)?(?:
        opens | navigates | clicks | scrolls | switches | launches | logs\s+in
      | posts | sends | drafts | writes | composes | creates | saves | uploads
      | downloads | moves | copies | deletes | searches | adds | submits
      | schedules | books | places | enters | applies | selects | sets
      | attempts | confirms | records | assigns | re-?assigned | scopes
      | starts | rerun | reorders | attaches | exports
    )\b""",
    re.I | re.X,
)

STYLE = re.compile(
    r"\b(?:tone|voice|style|persona\s+voice|not\s+fan-fiction|over-the-top|"
    r"readable|well[-\s]formatted|concise|professional)\b",
    re.I,
)

MONEY = re.compile(r"\$\s?\d[\d,]*(?:\.\d+)?")
CODE = re.compile(r"\b[A-Z]{2,}[0-9]{2,}[A-Z0-9]*\b|\b[A-Z0-9]{7,}\b")
DATEISH = re.compile(r"\b(?:20\d\d-\d\d-\d\d|\d{1,2}/\d{1,2}/\d{2,4})\b")

CLASSES = ["value", "record", "action", "style", "unclear"]
ATTRIBUTABLE = ("value", "record")


GENERIC_WORDS = {
    "single", "married", "none", "true", "false", "other", "primary", "home",
    "work", "office", "checking", "savings", "credit", "monthly", "weekly",
}


def _distinctive_string(val: str) -> bool:
    """Keep values that can only plausibly appear in text as the answer.

    A bare lowercase word such as "single" (SPEEDTAX_FILING_STATUS) matches any
    sentence containing it, so it cannot be used as evidence that a criterion
    quotes the seeded value. Proper nouns, codes and multi-word values can.
    """
    if "${" in val or len(val) < 5 or val.lower() in GENERIC_WORDS:
        return False
    return bool(
        any(ch.isdigit() for ch in val)
        or " " in val
        or "'" in val
        or val[0].isupper()
    )


def variable_value_strings(variables: dict) -> dict:
    """Map printable forms of ground-truth values back to their variable name."""
    forms: dict[str, str] = {}
    for key, val in variables.items():
        candidates = set()
        if isinstance(val, bool) or isinstance(val, (list, dict)) or val is None:
            continue
        if isinstance(val, str):
            if _distinctive_string(val):
                candidates.add(val)
        elif isinstance(val, (int, float)):
            # Small numbers collide with step counts and quantities in rubric
            # prose, so only keep printed forms long enough to be a value.
            for form in ({f"{val}", f"{int(val):,}"} if float(val).is_integer() else {f"{val}"}):
                if len(form.replace(",", "")) >= 4:
                    candidates.add(form)
        for form in candidates:
            forms.setdefault(form, key)
    return forms


def classify(criterion: str, value_forms: dict) -> tuple[str, list[str]]:
    hits = sorted(
        {
            key
            for form, key in value_forms.items()
            if re.search(rf"(?<!\w){re.escape(form)}(?!\w)", criterion)
        }
    )
    if hits:
        return "value", hits
    if RECORD.search(criterion):
        return "record", []
    if MONEY.search(criterion) or CODE.search(criterion) or DATEISH.search(criterion):
        return "value", []
    if STYLE.search(criterion):
        return "style", []
    if ACTION.search(criterion):
        return "action", []
    return "unclear", []


def main() -> int:
    tasks = [json.loads(line) for line in (DATA / "tasks.jsonl").open()]
    variables = json.loads((DATA / "variables.json").read_text())
    value_forms = variable_value_strings(variables)

    rows = []
    item_counts: Counter = Counter()
    item_weight: Counter = Counter()

    for task in tasks:
        counts: Counter = Counter()
        weights: Counter = Counter()
        var_hits: set[str] = set()
        annotated = []

        for item in task["grading"]["rubrics"]:
            kind, hits = classify(item["criterion"], value_forms)
            weight = float(item.get("weight", 0))
            counts[kind] += 1
            weights[kind] += weight
            item_counts[kind] += 1
            item_weight[kind] += weight
            var_hits.update(hits)
            annotated.append({"criterion": item["criterion"], "class": kind, "weight": weight})

        total_weight = sum(weights.values()) or 1.0
        attributable_weight = sum(weights[k] for k in ATTRIBUTABLE) / total_weight
        rows.append(
            {
                "id": task["id"],
                "category": task["category"],
                "behavioral_type": task["behavioral_type"],
                "difficulty": task["difficulty"],
                "n_apps": len(task["apps_involved"]),
                "n_rubrics": task["num_rubrics"],
                "counts": {k: counts[k] for k in CLASSES},
                "attributable_weight": round(attributable_weight, 3),
                "has_action_gate": counts["action"] > 0,
                "rubric_edit_needed": counts["value"] > 0,
                "variables": sorted(var_hits),
                "apps": task["apps_involved"],
                "instruction": task["instruction"],
                "rubrics": annotated,
            }
        )

    OUT.mkdir(exist_ok=True)
    (OUT / "m0_scan.json").write_text(json.dumps(rows, indent=2))

    n_items = sum(item_counts.values())
    total_w = sum(item_weight.values())
    print(f"tasks {len(rows)}   rubric criteria {n_items}\n")
    print("what makes a criterion true")
    for kind in CLASSES:
        print(
            f"  {kind:<9} n={item_counts[kind]:>4}  {item_counts[kind] / n_items:6.1%}"
            f"   weight {item_weight[kind] / total_w:6.1%}"
        )

    attributable = sum(item_counts[k] for k in ATTRIBUTABLE)
    print(
        f"\n  attributable to personal records: {attributable}/{n_items}"
        f" = {attributable / n_items:.1%} of criteria,"
        f" {sum(item_weight[k] for k in ATTRIBUTABLE) / total_w:.1%} of weight"
    )

    print("\ntasks by attributable weight share")
    bands = Counter()
    for row in rows:
        frac = row["attributable_weight"]
        band = (
            "0.00"
            if frac == 0
            else "(0, .33]"
            if frac <= 1 / 3
            else "(.33, .66]"
            if frac <= 2 / 3
            else "(.66, 1)"
            if frac < 1
            else "1.00"
        )
        bands[band] += 1
    for band in ["0.00", "(0, .33]", "(.33, .66]", "(.66, 1)", "1.00"]:
        print(f"  {band:<11} {bands[band]:>4}")

    gated = sum(1 for r in rows if r["has_action_gate"])
    edits = sum(1 for r in rows if r["rubric_edit_needed"])
    print(f"\ntasks with >=1 action-only criterion (gates the perfect metric): {gated}/{len(rows)}")
    print(f"tasks whose rubric text must be edited under counterfactual:      {edits}/{len(rows)}")
    print(f"tasks quoting a named variables.json value:                       "
          f"{sum(1 for r in rows if r['variables'])}/{len(rows)}")

    print("\nmean attributable weight by internal category")
    by_cat = defaultdict(list)
    for row in rows:
        by_cat[row["category"]].append(row["attributable_weight"])
    for cat, vals in sorted(by_cat.items(), key=lambda kv: -sum(kv[1]) / len(kv[1])):
        print(f"  {cat:<20} n={len(vals):>3}  mean={sum(vals) / len(vals):.2f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
