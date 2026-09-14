#!/usr/bin/env python3
"""Locked P3-H Stage-1 draw. Does not label. Does not call an API."""

from __future__ import annotations

import csv
import json
import random
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
JOIN = ROOT / "join.json"
HPC = ROOT / "hpc_import"
OUT = ROOT / "out_p3h"
SEED = 20260913

TASK_TEXT = {
    "counterfactual-f010": (
        "Analyze the guest's banking and upcoming flights. Decide whether "
        "cash on hand covers optional flight upgrades without using a credit card."
    ),
    "counterfactual-f013": (
        "Compare banking and investment balances after a world change. "
        "Report the relevant account figures the task asks for."
    ),
    "retrieval-f009": (
        "Find the New York trip records (hotel and/or flight) and report "
        "the confirmation identifiers the task asks for."
    ),
    "retrieval-f010": (
        "Find who is hosting or concierge-handling the stay and report that name."
    ),
    "aggregation-f020": (
        "Read the BatBucks cash position the task asks you to report."
    ),
    "counterfactual-f005": (
        "Inspect the GME position after a world change. Report share count "
        "and/or average cost as the task specifies."
    ),
}


def gold_needles(gold: str) -> list[str]:
    g = (gold or "").strip()
    out = [g]
    if g.endswith(".0"):
        out.append(g[:-2])
    if re.fullmatch(r"[\d.]+", g):
        try:
            n = float(g)
            if n == int(n):
                out.append(str(int(n)))
        except ValueError:
            pass
    # unique, longest first
    seen = []
    for x in out:
        if x and x not in seen:
            seen.append(x)
    return seen


def line_text(obj: dict) -> str:
    parts = []
    for k in ("action", "response", "info"):
        v = obj.get(k)
        if isinstance(v, str):
            parts.append(v)
        elif v is not None:
            parts.append(json.dumps(v, ensure_ascii=False))
    return "\n".join(parts)


def find_traj(dest: Path) -> Path:
    hits = list(dest.rglob("traj.jsonl"))
    if not hits:
        raise FileNotFoundError(dest)
    return hits[0]


def load_traj(path: Path) -> list[dict]:
    rows = []
    for ln in path.read_text().splitlines():
        if ln.strip():
            rows.append(json.loads(ln))
    return rows


def pick_frames(traj: list[dict], golds: list[str]) -> list[int]:
    n = len(traj)
    last = n - 1
    needles = []
    for g in golds:
        needles.extend(gold_needles(g))
    earlier_hits = []
    for i, obj in enumerate(traj[:-1]):
        text = line_text(obj)
        if any(nd and nd in text for nd in needles):
            earlier_hits.append(i)
    picked = []
    # prefer later gold-in-text frames (closer to the answer)
    for i in reversed(earlier_hits):
        if i not in picked:
            picked.append(i)
        if len(picked) == 2:
            break
    j = last - 1
    while len(picked) < 2 and j >= 0:
        if j not in picked:
            picked.append(j)
        j -= 1
    frames = sorted(set(picked[:2] + [last]))
    return frames


def main() -> None:
    data = json.loads(JOIN.read_text())
    rows = data["rows"]
    by_dir: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for r in rows:
        by_dir[(r["lane"], r["task"], r["leg"])].append(r)

    rng = random.Random(SEED)
    dir_draw = []
    st1_key = []
    for key in sorted(by_dir):
        lane, task, leg = key
        dest = HPC / lane / task / leg
        comps = by_dir[key]
        golds = [c["gold"] for c in comps]
        traj_path = find_traj(dest)
        traj = load_traj(traj_path)
        frames = pick_frames(traj, golds)
        shots = []
        gold_on = []
        for i in frames:
            name = traj[i].get("screenshot_file") or ""
            png = dest / name
            shots.append(
                {
                    "frame_index": i,
                    "screenshot": name,
                    "is_last": int(i == len(traj) - 1),
                    "png_exists": int(png.exists()),
                    "gold_in_line_text": int(
                        any(
                            nd in line_text(traj[i])
                            for g in golds
                            for nd in gold_needles(g)
                        )
                    ),
                }
            )
            gold_on.append(shots[-1]["gold_in_line_text"])
        dir_draw.append(
            {
                "lane": lane,
                "task": task,
                "leg": leg,
                "n_traj": len(traj),
                "components": ",".join(c["component"] for c in comps),
                "golds": ",".join(golds),
                "frames": ",".join(str(s["frame_index"]) for s in shots),
                "screenshots": ",".join(s["screenshot"] for s in shots),
                "n_drawn": len(shots),
                "n_png_ok": sum(s["png_exists"] for s in shots),
            }
        )
        for c in comps:
            for s in shots:
                st1_key.append(
                    {
                        "lane": lane,
                        "task": task,
                        "leg": leg,
                        "component": c["component"],
                        "row_id": f"{lane}/{task}/{leg}/{c['component']}",
                        "frame_index": s["frame_index"],
                        "screenshot": s["screenshot"],
                        "is_last": s["is_last"],
                        "png_exists": s["png_exists"],
                        "gold_in_line_text": s["gold_in_line_text"],
                        "png_path": str(
                            (dest / s["screenshot"]).relative_to(ROOT)
                        ),
                    }
                )

    sheet = st1_key[:]
    rng.shuffle(sheet)
    ann = []
    for n, row in enumerate(sheet, start=1):
        ann.append(
            {
                "item_id": f"P3H-S1-{n:04d}",
                "task": row["task"],
                "leg": row["leg"],
                "task_text": TASK_TEXT[row["task"]],
                "png_path": row["png_path"],
            }
        )
        row["item_id"] = f"P3H-S1-{n:04d}"

    OUT.mkdir(exist_ok=True)
    with (OUT / "p3h_dir_draw.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(dir_draw[0]))
        w.writeheader()
        w.writerows(dir_draw)
    fields_key = [
        "item_id",
        "lane",
        "task",
        "leg",
        "component",
        "row_id",
        "frame_index",
        "screenshot",
        "is_last",
        "png_exists",
        "gold_in_line_text",
        "png_path",
    ]
    with (OUT / "p3h_stage1_key.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields_key)
        w.writeheader()
        w.writerows(st1_key)
    with (OUT / "p3h_stage1_sheet.csv").open("w", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=["item_id", "task", "leg", "task_text", "png_path"]
        )
        w.writeheader()
        w.writerows(ann)
    blank = [
        {
            "item_id": r["item_id"],
            "isolation": "",
            "notes": "",
        }
        for r in ann
    ]
    with (OUT / "p3h_stage1_labels_BLANK.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["item_id", "isolation", "notes"])
        w.writeheader()
        w.writerows(blank)

    md = [
        "# P3-H Stage-1 draw",
        "",
        f"Seed `{SEED}`. Unique dirs: {len(dir_draw)}. Stage-1 items: {len(ann)}.",
        "Annotator sheet hides component, gold, S, Y, found, is_last.",
        "PNG bundle present; STOP-NO-PNG lifted.",
        "Labels: fill `p3h_stage1_labels_BLANK.csv` (DECISIVE / NOT_DECISIVE / UNCLEAR).",
        "This script does not label.",
        "",
        "| dir | comps | n_traj | frames | png_ok |",
        "|---|---|---:|---|---:|",
    ]
    for d in dir_draw:
        md.append(
            f"| {d['lane']}/{d['task']}/{d['leg']} | {d['components']} | "
            f"{d['n_traj']} | {d['frames']} | {d['n_png_ok']}/{d['n_drawn']} |"
        )
    (OUT / "p3h_draw.md").write_text("\n".join(md) + "\n")
    print((OUT / "p3h_draw.md").read_text())


if __name__ == "__main__":
    main()
