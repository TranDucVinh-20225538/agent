#!/usr/bin/env python3
"""Pick the Milestone 0 hand-reading sample and emit a fill-in template.

Stratified, not random: the population is dominated by long_horizon and
situated_action, so a random draw of 10 would spend the whole budget on the
most expensive and least informative tasks.
"""

import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (category, rubric_class filter, n) -- filter None means any class
QUOTA = [
    ("retrieval", None, 3),
    ("preference_inference", None, 3),
    ("situated_action", None, 2),
    (None, "procedural_only", 2),
]

QUESTIONS = [
    "Gold la gi (gia tri cu the)?",
    "Gold sinh tu record nao (app + bang/field)?",
    "Con nguon nao khac cung sinh ra dung gold do?",
    "Doi nguon o cau 2 thi gold co doi khong?",
    "Doi nguon o cau 2 thi rubric co phai sua khong (cau nao)?",
]


def main():
    rows = list(csv.DictReader(open(ROOT / "m0/milestone0_scan.csv")))
    tasks = {
        json.loads(line)["id"]: json.loads(line)
        for line in (ROOT / "data/mypcbench/tasks.jsonl").read_text().splitlines()
        if line.strip()
    }

    rng = random.Random(13)
    picked, seen = [], set()
    for category, rubric_class, n in QUOTA:
        pool = [
            r
            for r in rows
            if r["id"] not in seen
            and (category is None or r["category"] == category)
            and (rubric_class is None or r["rubric_class"] == rubric_class)
        ]
        pool.sort(key=lambda r: r["id"])
        for r in rng.sample(pool, min(n, len(pool))):
            picked.append(r)
            seen.add(r["id"])

    out = ["# Milestone 0 - hand reading, 10 tasks", "", "Seed 13. Stratified by category and rubric class.", ""]
    for r in picked:
        task = tasks[r["id"]]
        out += [
            f"## {r['id']}  ({r['category']} / {r['behavioral_type']} / {r['difficulty']})",
            "",
            f"- rubric_class: **{r['rubric_class']}** (pinned {r['n_pinned']}, seed-relative {r['n_seed_relative']}, procedural {r['n_procedural']})",
            f"- apps: {', '.join(task.get('apps_involved') or []) or '-'}",
            f"- seeded values quoted: {r['var_keys'] or '-'}",
            "",
            f"**Instruction.** {task['instruction']}",
            "",
            "**Rubrics.**",
            "",
        ]
        for i, crit in enumerate(task["grading"]["rubrics"], 1):
            out.append(f"{i}. {crit['criterion']}")
        out += ["", "**Answers.**", ""]
        for q in QUESTIONS:
            out += [f"- {q}", "  - "]
        out.append("")

    path = ROOT / "m0/milestone0_hand_reading.md"
    path.write_text("\n".join(out) + "\n")
    print("wrote", path)
    for r in picked:
        print(f"  {r['id']:<28} {r['category']:<20} {r['rubric_class']}")


if __name__ == "__main__":
    main()
