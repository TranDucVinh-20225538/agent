#!/usr/bin/env python3
"""Export CUAVerifierBench PNGs. Run only when U2/R is being opened.

Does not label. Does not call an LLM. Downloads ~3GB parquet if missing.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
SHOTS = DATA / "screenshots"


def main() -> None:
    from datasets import load_dataset

    SHOTS.mkdir(parents=True, exist_ok=True)
    for split in ("fara7b_om2w_browserbase", "internal"):
        ds = load_dataset("microsoft/CUAVerifierBench", "trajectories", split=split)
        out = SHOTS / split
        out.mkdir(exist_ok=True)
        for row in ds:
            tid = row["task_id"]
            dest = out / tid
            dest.mkdir(exist_ok=True)
            for i, im in enumerate(row["screenshots"] or []):
                im.save(dest / f"{i:04d}.png")
            print(tid, row.get("n_screenshots"))


if __name__ == "__main__":
    main()
