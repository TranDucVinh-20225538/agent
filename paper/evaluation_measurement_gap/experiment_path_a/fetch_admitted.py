#!/usr/bin/env python3
"""Download admitted cleaned JSON only. No screenshots. No classification."""

from __future__ import annotations

import csv
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KEYS = ROOT / "schema" / "admitted_keys.csv"
DEST = ROOT / "data" / "admitted"
BASE = "https://huggingface.co/datasets/McGill-NLP/agent-reward-bench/resolve/main"
UA = "Mozilla/5.0 (PathA fetch; research)"


def _get(url: str, out: Path) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as resp, out.open("wb") as f:
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
    return "ok"


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(KEYS.open()))
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else len(rows)
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    jobs = []
    skip = 0
    for row in rows[:limit]:
        rel = row["rel_path"]
        out = DEST / rel
        if out.exists() and out.stat().st_size > 0:
            skip += 1
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        jobs.append((rel, out, f"{BASE}/{rel}"))
    print(f"to_fetch={len(jobs)} skip={skip} workers={workers}", flush=True)
    ok = fail = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(_get, url, out): rel for rel, out, url in jobs}
        for i, fut in enumerate(as_completed(futs), 1):
            rel = futs[fut]
            try:
                fut.result()
                ok += 1
            except Exception as e:
                fail += 1
                print("FAIL", rel, e, file=sys.stderr, flush=True)
            if i % 20 == 0 or i == len(futs):
                print(f"... {i}/{len(futs)} ok={ok} fail={fail}", flush=True)
    print(f"done ok={ok} skip={skip} fail={fail} dest={DEST}", flush=True)


if __name__ == "__main__":
    main()
