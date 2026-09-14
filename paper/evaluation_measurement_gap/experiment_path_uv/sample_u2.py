#!/usr/bin/env python3
"""Build U2 sheets from SAMPLE_LOCK.md. Run once after full R. Does not label."""

from __future__ import annotations

import csv
import json
import random
import statistics
from pathlib import Path

from group_r import K

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
SEED = 20260913
SPLIT = "fara7b_om2w_browserbase"


def by_task_id(rows: list[dict]) -> list[dict]:
    return sorted(rows, key=lambda r: r["task_id"])


def pick_controls(C: list[dict], event: list[dict], n_ctrl: int) -> list[dict]:
    """Nearest |n_frames - median(E)|; ties broken by task_id (stable)."""
    if n_ctrl <= 0 or not C:
        return []
    med = statistics.median(int(r["n_frames"]) for r in event)
    ranked = sorted(C, key=lambda r: (abs(int(r["n_frames"]) - med), r["task_id"]))
    return ranked[:n_ctrl]


def main() -> None:
    rng = random.Random(SEED)
    results = []
    p = OUT / "r_results.jsonl"
    if not p.exists():
        raise SystemExit("need out/r_results.jsonl")
    for line in p.read_text().splitlines():
        if line.strip():
            results.append(json.loads(line))
    if len(results) < 100:
        raise SystemExit(f"R incomplete: {len(results)} rows (need OM2W ~106)")

    results = by_task_id(results)
    E = by_task_id([r for r in results if int(r["n_discard"]) >= 1])
    C = by_task_id(
        [
            r
            for r in results
            if int(r["n_discard"]) == 0 and int(r["n_frames"]) > K
        ]
    )
    if len(E) <= 40:
        event = list(E)
        n_ctrl = min(20, len(C))
    else:
        event = by_task_id(rng.sample(E, 40))
        n_ctrl = min(20, len(C))
    ctrl = pick_controls(C, event, n_ctrl)
    event = by_task_id(event)
    ctrl = by_task_id(ctrl)
    pilot = [r["task_id"] for r in event[:6]]

    ep_rows = []
    st1 = []
    for role, recs in (("event", event), ("control", ctrl)):
        for r in recs:
            disc = sorted(int(i) for i in (r.get("discard") or []))
            disc_set = set(disc)
            n_fr = int(r["n_frames"])
            keep = [i for i in range(n_fr) if i not in disc_set]
            ep_rows.append(
                {
                    "role": role,
                    "task_id": r["task_id"],
                    "n_frames": n_fr,
                    "n_discard": r["n_discard"],
                    "n_keep": len(keep),
                    "pilot6": int(r["task_id"] in set(pilot) and role == "event"),
                }
            )
            if role == "event":
                keep_s = keep[:]
                rng.shuffle(keep_s)
                keep_s = keep_s[: min(len(disc), len(keep_s))]
                for i in disc:
                    st1.append(
                        {
                            **ep_rows[-1],
                            "frame_index": i,
                            "in_discard": 1,
                            "reason": "all_discard",
                        }
                    )
                for i in keep_s:
                    st1.append(
                        {
                            **ep_rows[-1],
                            "frame_index": i,
                            "in_discard": 0,
                            "reason": "matched_keep",
                        }
                    )
            else:
                pool = list(range(n_fr))
                rng.shuffle(pool)
                for i in pool[: min(10, n_fr)]:
                    st1.append(
                        {
                            **ep_rows[-1],
                            "frame_index": i,
                            "in_discard": 0,
                            "reason": "control_frame",
                        }
                    )

    sheet = st1[:]
    rng.shuffle(sheet)
    ann = []
    for n, row in enumerate(sheet, start=1):
        ann.append(
            {
                "item_id": f"U2S1-{n:04d}",
                "task_id": row["task_id"],
                "frame_index": row["frame_index"],
            }
        )

    fields_ep = ["role", "task_id", "n_frames", "n_discard", "n_keep", "pilot6"]
    fields_fr = fields_ep + ["frame_index", "in_discard", "reason"]
    with (OUT / "u2_episode_sample.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields_ep)
        w.writeheader()
        w.writerows(ep_rows)
    with (OUT / "u2_stage1_key.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields_fr)
        w.writeheader()
        w.writerows(st1)
    with (OUT / "u2_stage1_sheet.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["item_id", "task_id", "frame_index"])
        w.writeheader()
        w.writerows(ann)

    md = [
        "# U2 sample (drawn after R, rule locked before R)",
        "",
        f"Seed `{SEED}`. Event episodes: {len(event)}. Controls: {len(ctrl)}.",
        f"Pilot-6 (first event task_id): {', '.join(pilot)}.",
        f"Stage-1 items: {len(ann)}. Discard items: {sum(1 for r in st1 if r['in_discard']==1)}.",
        "Stage-2 sheet is built after stage-1 DECISIVE labels (`join_u2_stage2.py`).",
        "",
    ]
    (OUT / "u2_sample.md").write_text("\n".join(md))
    print((OUT / "u2_sample.md").read_text())


if __name__ == "__main__":
    main()
