#!/usr/bin/env python3
"""Freeze B2 episode/frame sample from B1 T=3 cells.

Does not label. Does not read Score as gold. Does not read human_label.json.
Requires screenshots before any human starts.
"""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "out"
MAX_IMAGE = 50
T = 3
SEED = 20260913
N_OPERATOR_NEARMISS = 10
N_OTHER_CONTROLS = 10
FRAMES_PER_CONTROL = 10


def load_jsonl(path: Path) -> list[dict]:
    text = path.read_text()
    if text.lstrip().startswith("["):
        return json.loads(text)
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def scores(rec: dict) -> list[int]:
    items = rec.get("image_judge_record") or []
    out = []
    for it in items:
        if isinstance(it, dict) and "Score" in it:
            try:
                out.append(int(it["Score"]))
            except (TypeError, ValueError):
                out.append(0)
    return out


def qualified_indices(sc: list[int]) -> list[int]:
    return [i for i, s in enumerate(sc) if s >= T]


def main() -> None:
    rng = random.Random(SEED)
    cells = list(csv.DictReader((OUT / "b1_cells.csv").open()))
    t3 = [r for r in cells if r["T"] == "3"]
    hits = [r for r in t3 if r["hit_cap"] == "1"]
    if len(hits) != 10:
        raise SystemExit(f"expected 10 T=3 cap hits, got {len(hits)}")

    op_near = [
        r
        for r in t3
        if r["agent_file"] == "operator_results.json"
        and r["hit_cap"] == "0"
        and int(r["n_qualified"]) >= 1
    ]
    op_near.sort(key=lambda r: abs(int(r["n_qualified"]) - MAX_IMAGE))
    op_near = op_near[:N_OPERATOR_NEARMISS]

    other = [
        r
        for r in t3
        if r["agent_file"] != "operator_results.json"
        and r["hit_cap"] == "0"
        and int(r["n_qualified"]) >= 1
    ]
    other = rng.sample(other, k=min(N_OTHER_CONTROLS, len(other)))

    episodes = []
    for role, recs in (
        ("cap_hit", hits),
        ("operator_nearmiss", op_near),
        ("other_control", other),
    ):
        for r in recs:
            episodes.append(
                {
                    "role": role,
                    "agent_file": r["agent_file"],
                    "task_id": r["task_id"],
                    "n_scored": r["n_scored"],
                    "n_qualified": r["n_qualified"],
                    "n_discard": r["n_discard"],
                    "hit_cap": r["hit_cap"],
                }
            )

    rec_index: dict[tuple[str, str], dict] = {}
    needed_files = {e["agent_file"] for e in episodes}
    for agent in needed_files:
        for rec in load_jsonl(DATA / agent):
            tid = rec.get("task_id") or rec.get("id") or ""
            rec_index[(agent, tid)] = rec

    frames = []
    for e in episodes:
        rec = rec_index[(e["agent_file"], e["task_id"])]
        qidx = qualified_indices(scores(rec))
        keep = qidx[:MAX_IMAGE]
        disc = qidx[MAX_IMAGE:]
        e["confirmed_task"] = rec.get("confirmed_task") or ""
        if e["role"] == "cap_hit":
            # All discarded frames (the B2 object). Equal-sized keep sample, blind.
            n_pair = len(disc)
            keep_s = keep[:]
            rng.shuffle(keep_s)
            keep_s = keep_s[:n_pair]
            for i in disc:
                frames.append({**e, "frame_index": i, "in_discard": 1, "reason": "all_discard"})
            for i in keep_s:
                frames.append({**e, "frame_index": i, "in_discard": 0, "reason": "matched_keep"})
        else:
            pool = qidx[:]
            rng.shuffle(pool)
            take = pool[: min(FRAMES_PER_CONTROL, len(pool))]
            for i in take:
                frames.append(
                    {
                        **e,
                        "frame_index": i,
                        "in_discard": 0,
                        "reason": "control_qualified",
                    }
                )

    ep_path = OUT / "b2_episode_sample.csv"
    fr_path = OUT / "b2_frame_sample.csv"
    ep_fields = [
        "role",
        "agent_file",
        "task_id",
        "n_scored",
        "n_qualified",
        "n_discard",
        "hit_cap",
        "confirmed_task",
    ]
    fr_fields = ep_fields + ["frame_index", "in_discard", "reason"]
    with ep_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ep_fields)
        w.writeheader()
        w.writerows(episodes)
    # annotation sheet hides keep/discard
    ann_fields = ["item_id", "agent_file", "task_id", "frame_index", "confirmed_task"]
    ann_rows = []
    shuffled = frames[:]
    rng.shuffle(shuffled)
    for n, row in enumerate(shuffled, start=1):
        ann_rows.append(
            {
                "item_id": f"B2-{n:04d}",
                "agent_file": row["agent_file"],
                "task_id": row["task_id"],
                "frame_index": row["frame_index"],
                "confirmed_task": row["confirmed_task"],
            }
        )
    with fr_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fr_fields)
        w.writeheader()
        w.writerows(frames)
    ann_path = OUT / "b2_annotation_sheet.csv"
    with ann_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ann_fields)
        w.writeheader()
        w.writerows(ann_rows)

    lines = [
        "# Path B2 sample (frozen before labels)",
        "",
        f"Seed `{SEED}`. Primary T={T}. `MAX_IMAGE={MAX_IMAGE}`.",
        "Does not use `human_label.json`, `Score`, or `final_eval` for sampling roles",
        "except the mechanical T=3 qualification already in B1.",
        "",
        f"Episodes: {len(episodes)} "
        f"(cap_hit={sum(1 for e in episodes if e['role']=='cap_hit')}, "
        f"operator_nearmiss={sum(1 for e in episodes if e['role']=='operator_nearmiss')}, "
        f"other_control={sum(1 for e in episodes if e['role']=='other_control')}).",
        f"Hidden key frames: {len(frames)}. Annotation items: {len(ann_rows)}.",
        f"Discarded frames in sample: {sum(1 for r in frames if r['in_discard']==1)}.",
        "",
        "Annotators receive `b2_annotation_sheet.csv` only (no `in_discard`).",
        "Screenshots are not in the released judge JSON. B2 remains blocked until",
        "v2 `trajectory/*.png` exist for every sampled `(agent_file, task_id)`.",
        "",
    ]
    (OUT / "b2_sample.md").write_text("\n".join(lines))
    print((OUT / "b2_sample.md").read_text())


if __name__ == "__main__":
    main()
