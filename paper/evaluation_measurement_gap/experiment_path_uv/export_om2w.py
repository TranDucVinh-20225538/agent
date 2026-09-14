#!/usr/bin/env python3
"""Export OM2W CUAVerifierBench screenshots from local parquet (no LLM)."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

import pyarrow.parquet as pq
from PIL import Image

ROOT = Path(__file__).resolve().parent
PQ = ROOT / "data" / "parquet"
SHOTS = ROOT / "data" / "screenshots" / "fara7b_om2w_browserbase"
META = ROOT / "out" / "export_om2w.jsonl"


def _to_image(cell) -> Image.Image | None:
    if cell is None:
        return None
    if isinstance(cell, dict) and cell.get("bytes"):
        return Image.open(BytesIO(cell["bytes"])).convert("RGB")
    if isinstance(cell, (bytes, bytearray)):
        return Image.open(BytesIO(cell)).convert("RGB")
    if hasattr(cell, "save"):
        return cell.convert("RGB")
    return None


def main() -> None:
    SHOTS.mkdir(parents=True, exist_ok=True)
    META.parent.mkdir(exist_ok=True)
    n_tasks = 0
    n_png = 0
    with META.open("w") as out:
        for name in ("om2w_0.parquet", "om2w_1.parquet"):
            pf = pq.ParquetFile(PQ / name)
            cols = [
                c
                for c in (
                    "task_id",
                    "instruction",
                    "init_url",
                    "n_screenshots",
                    "screenshots",
                    "final_answer",
                    "web_surfer_log",
                )
                if c in pf.schema_arrow.names
            ]
            for batch in pf.iter_batches(columns=cols, batch_size=8):
                for row in batch.to_pylist():
                    tid = row["task_id"]
                    dest = SHOTS / tid
                    dest.mkdir(exist_ok=True)
                    imgs = row.get("screenshots") or []
                    for i, cell in enumerate(imgs):
                        im = _to_image(cell)
                        if im is None:
                            continue
                        im.save(dest / f"{i:04d}.png")
                        n_png += 1
                    rec = {
                        "task_id": tid,
                        "instruction": row.get("instruction") or "",
                        "init_url": row.get("init_url") or "",
                        "n_screenshots": int(row.get("n_screenshots") or len(imgs)),
                        "n_exported": len(list(dest.glob("*.png"))),
                        "final_answer": (row.get("final_answer") or "")[:2000],
                    }
                    out.write(json.dumps(rec) + "\n")
                    n_tasks += 1
                    print(tid, rec["n_exported"])
    print(f"exported tasks={n_tasks} png={n_png}")


if __name__ == "__main__":
    main()
