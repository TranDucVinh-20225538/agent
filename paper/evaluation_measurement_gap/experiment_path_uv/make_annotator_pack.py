#!/usr/bin/env python3
"""Build a blind U2 Stage-1 pack for three human annotators. No keep/discard."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
SHOTS = ROOT / "data" / "screenshots" / "fara7b_om2w_browserbase"
PACK = ROOT / "annotators"
PILOT = {
    "Airbnb--a13e4231",
    "Akc--eb2db4b7",
    "Allrecipes--75a1b5dc",
    "Amtrak--323bd85e",
    "Apartments--c0fa2c0e",
    "Arxiv--71f8de18",
}


def main() -> None:
    inst = {}
    for line in (OUT / "export_om2w.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        inst[r["task_id"]] = (r.get("instruction") or "").strip()

    sheet = list(csv.DictReader((OUT / "u2_stage1_sheet.csv").open()))
    pack_png = PACK / "png"
    pack_png.mkdir(parents=True, exist_ok=True)

    rows = []
    missing = 0
    for r in sheet:
        tid = r["task_id"]
        idx = int(r["frame_index"])
        src = SHOTS / tid / f"{idx:04d}.png"
        dest = pack_png / f"{r['item_id']}.png"
        if src.exists():
            if dest.exists() or dest.is_symlink():
                dest.unlink()
            dest.hardlink_to(src)
        else:
            missing += 1
        rows.append(
            {
                "item_id": r["item_id"],
                "task": inst.get(tid, tid),
                "png": f"png/{r['item_id']}.png",
                "isolation": "",
                "notes": "",
            }
        )

    def write(name: str, data: list[dict]) -> None:
        with (PACK / name).open("w", newline="") as f:
            w = csv.DictWriter(
                f, fieldnames=["item_id", "task", "png", "isolation", "notes"]
            )
            w.writeheader()
            w.writerows(data)

    write("stage1_all.csv", rows)
    pilot_ids = {x["item_id"] for x in sheet if x["task_id"] in PILOT}
    write("stage1_pilot.csv", [r for r in rows if r["item_id"] in pilot_ids])
    print(f"wrote {PACK}  all={len(rows)} pilot={len(pilot_ids)} missing_png={missing}")


if __name__ == "__main__":
    main()
