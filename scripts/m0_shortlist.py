"""Pick the Milestone 0 hand-read shortlist and emit the review table.

Stratified, not random: random sampling over the 184 tasks is dominated by
long_horizon and situated_action, which are the most expensive to rerun and the
least informative about gold provenance. We take a few tasks per evidence
regime, prefer short rubrics and few apps so a counterfactual stays cheap, and
include controls whose rubric mass no personal counterfactual can move.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"

QUOTA = [
    ("retrieval", 3, "point lookup: gold should be one seeded field"),
    ("preference_inference", 3, "latent: gold should be a statistic over records"),
    ("situated_action", 2, "latent gold consumed by an action"),
    ("CONTROL", 2, "no rubric weight attributable to personal records"),
]


def pick(rows):
    chosen, seen = [], set()
    for bucket, n, note in QUOTA:
        if bucket == "CONTROL":
            pool = [r for r in rows if r["attributable_weight"] == 0.0]
            pool.sort(key=lambda r: (r["n_rubrics"], r["n_apps"]))
        else:
            pool = [r for r in rows if r["category"] == bucket]
            pool.sort(
                key=lambda r: (-r["attributable_weight"], r["n_rubrics"], r["n_apps"])
            )
        taken = 0
        for row in pool:
            if row["id"] in seen:
                continue
            chosen.append({**row, "bucket": bucket, "why": note})
            seen.add(row["id"])
            taken += 1
            if taken == n:
                break
    return chosen


def main() -> int:
    rows = json.loads((OUT / "m0_scan.json").read_text())
    chosen = pick(rows)

    lines = [
        "# Milestone 0 - hand-read shortlist",
        "",
        "Screening pass proposes the class of each rubric criterion; these ten are"
        " read by hand to check whether the machine label holds and whether a"
        " counterfactual keeps the task well defined.",
        "",
        "| task | category | rubrics | apps | attributable weight | rubric edit needed | variables quoted |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in chosen:
        lines.append(
            f"| `{row['id']}` | {row['category']} | {row['n_rubrics']} | {row['n_apps']} |"
            f" {row['attributable_weight']:.2f} | {'yes' if row['rubric_edit_needed'] else 'no'} |"
            f" {', '.join(row['variables']) or '-'} |"
        )

    lines += ["", "## Per task", ""]
    for row in chosen:
        lines += [
            f"### `{row['id']}`  ({row['bucket']} - {row['why']})",
            "",
            f"**Instruction.** {row['instruction']}",
            "",
            f"Apps: {', '.join(row['apps'])}",
            "",
            "| # | class | w | criterion |",
            "| --- | --- | --- | --- |",
        ]
        for i, item in enumerate(row["rubrics"], 1):
            crit = item["criterion"].replace("|", "\\|")
            lines.append(f"| {i} | {item['class']} | {item['weight']:.2f} | {crit} |")
        lines += [
            "",
            "Questions to answer by hand:",
            "",
            "1. What is the gold value?",
            "2. Which records generate it?",
            "3. Does any other record also generate it?",
            "4. If those records change, does the gold change?",
            "5. If those records change, must the rubric text change?",
            "",
        ]

    (OUT / "m0_shortlist.md").write_text("\n".join(lines))
    print("\n".join(lines[:6 + len(chosen)]))
    print(f"\nwrote {OUT / 'm0_shortlist.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
