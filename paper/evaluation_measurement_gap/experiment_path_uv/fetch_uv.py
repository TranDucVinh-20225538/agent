#!/usr/bin/env python3
"""Fetch UV source + CUAVerifierBench trajectory metadata (no image decode)."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
SRC = DATA / "src"
OUT = ROOT / "out"

UV_PY = (
    "https://raw.githubusercontent.com/microsoft/fara/main/"
    "webeval/src/webeval/rubric_agent/mm_rubric_agent.py"
)
README = "https://huggingface.co/datasets/microsoft/CUAVerifierBench/raw/main/README.md"
PARQUET = {
    "om2w_0": "https://huggingface.co/datasets/microsoft/CUAVerifierBench/resolve/main/trajectories/fara7b_om2w_browserbase-00000-of-00002.parquet",
    "om2w_1": "https://huggingface.co/datasets/microsoft/CUAVerifierBench/resolve/main/trajectories/fara7b_om2w_browserbase-00001-of-00002.parquet",
    "internal_0": "https://huggingface.co/datasets/microsoft/CUAVerifierBench/resolve/main/trajectories/internal-00000-of-00002.parquet",
    "internal_1": "https://huggingface.co/datasets/microsoft/CUAVerifierBench/resolve/main/trajectories/internal-00001-of-00002.parquet",
}
META_COLS = [
    "task_id",
    "instruction",
    "n_screenshots",
    "uv_rubric_score",
    "uv_outcome_success",
    "final_human_outcome_label",
    "final_human_process_label",
    "is_aborted",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def get(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"GET {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "path-uv-fetch/1"})
    with urllib.request.urlopen(req) as r, dest.open("wb") as out:
        while True:
            buf = r.read(1 << 20)
            if not buf:
                break
            out.write(buf)
    print(f"  {dest.name} {dest.stat().st_size} {sha256(dest)}")


def project_parquet(path: Path, split: str) -> list[dict]:
    import pyarrow.parquet as pq

    pf = pq.ParquetFile(path)
    names = set(pf.schema_arrow.names)
    cols = [c for c in META_COLS if c in names]
    table = pf.read(columns=cols)
    rows = table.to_pylist()
    for r in rows:
        r["split"] = split
        r["parquet"] = path.name
    return rows


def main() -> None:
    DATA.mkdir(exist_ok=True)
    SRC.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(exist_ok=True)
    get(UV_PY, SRC / "mm_rubric_agent.py")
    get(README, DATA / "CUAVerifierBench_README.md")

    pq_dir = DATA / "parquet"
    all_rows = []
    for key, url in PARQUET.items():
        dest = pq_dir / f"{key}.parquet"
        if not dest.exists():
            get(url, dest)
        else:
            print(f"HAVE {dest} {dest.stat().st_size} {sha256(dest)}")
        split = "fara7b_om2w_browserbase" if key.startswith("om2w") else "internal"
        all_rows.extend(project_parquet(dest, split))

    meta_path = OUT / "u1_meta.jsonl"
    with meta_path.open("w") as f:
        for r in all_rows:
            f.write(json.dumps(r, default=str) + "\n")
    print(f"wrote {meta_path} n={len(all_rows)}")


if __name__ == "__main__":
    main()
