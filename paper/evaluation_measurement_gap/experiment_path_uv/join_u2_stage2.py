#!/usr/bin/env python3
"""Build blinded Stage-2 galleries from majority Stage-1 DECISIVE. Lab construction."""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
PACK = ROOT / "annotators"
SHOTS = ROOT / "data" / "screenshots" / "fara7b_om2w_browserbase"
SEED = 20260913


def main() -> None:
    rng = random.Random(SEED)
    vi = json.loads((PACK / "task_vi.json").read_text())
    inst = {}
    for line in (OUT / "export_om2w.jsonl").read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            inst[r["task_id"]] = (r.get("instruction") or "").strip()

    r_keep: dict[str, list[int]] = {}
    for line in (OUT / "r_results.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        disc = set(int(i) for i in (r.get("discard") or []))
        n = int(r["n_frames"])
        r_keep[r["task_id"]] = [i for i in range(n) if i not in disc]

    join = list(csv.DictReader((OUT / "u2_stage1_join.csv").open()))
    targets = [
        r
        for r in join
        if r["role"] == "event" and r["majority"] == "DECISIVE"
    ]
    targets.sort(key=lambda r: (r["task_id"], int(r["frame_index"])))

    key_rows = []
    for r in targets:
        tid = r["task_id"]
        fr = int(r["frame_index"])
        keep = list(r_keep[tid])
        if r["in_discard"] == "1":
            gal = keep[:]
            kind = "discard_vs_keep"
        else:
            gal = [i for i in keep if i != fr]
            kind = "keep_foil"
        rng.shuffle(gal)
        key_rows.append(
            {
                "task_id": tid,
                "target_frame": str(fr),
                "in_discard": r["in_discard"],
                "kind": kind,
                "n_gallery": str(len(gal)),
                "gallery": " ".join(str(i) for i in gal),
                "s1_item_id": r["item_id"],
            }
        )

    rng.shuffle(key_rows)
    s2_png = PACK / "s2_png"
    s2_png.mkdir(parents=True, exist_ok=True)
    blind = []
    missing = 0
    for n, r in enumerate(key_rows, start=1):
        iid = f"U2S2-{n:04d}"
        tid = r["task_id"]
        fr = int(r["target_frame"])
        gal = [int(x) for x in r["gallery"].split()] if r["gallery"] else []
        frames = [fr] + gal
        pngs = []
        for i in frames:
            src = SHOTS / tid / f"{i:04d}.png"
            dest = s2_png / f"{tid.replace('/', '_')}__{i:04d}.png"
            if src.exists():
                if dest.exists() or dest.is_symlink():
                    dest.unlink()
                dest.hardlink_to(src)
            else:
                missing += 1
            pngs.append(f"s2_png/{dest.name}")
        task = inst.get(tid, tid)
        r["item_id"] = iid
        blind.append(
            {
                "item_id": iid,
                "task": task,
                "task_vi": vi.get(task, ""),
                "target_png": pngs[0],
                "gallery_png": " ".join(pngs[1:]),
                "equivalence": "",
                "notes": "",
            }
        )

    with (OUT / "u2_stage2_key.csv").open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "item_id",
                "s1_item_id",
                "task_id",
                "target_frame",
                "in_discard",
                "kind",
                "n_gallery",
                "gallery",
            ],
        )
        w.writeheader()
        w.writerows(key_rows)
    with (PACK / "stage2.csv").open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "item_id",
                "task",
                "task_vi",
                "target_png",
                "gallery_png",
                "equivalence",
                "notes",
            ],
        )
        w.writeheader()
        w.writerows(blind)

    n_disc = sum(1 for r in key_rows if r["in_discard"] == "1")
    n_foil = len(key_rows) - n_disc
    empty = sum(1 for r in key_rows if int(r["n_gallery"]) == 0)
    print(
        f"S2 items {len(key_rows)} (discard {n_disc} + foil {n_foil}); "
        f"empty gallery {empty}; missing png {missing}",
        flush=True,
    )
    print(f"wrote {OUT / 'u2_stage2_key.csv'} and {PACK / 'stage2.csv'}", flush=True)


if __name__ == "__main__":
    main()
