"""Finish the image download over parallel byte ranges and verify the digest.

A single HuggingFace connection settles around 1 MB/s here, which is roughly an
hour for the 5.13 GB image. The CDN sets Accept-Ranges, so the remaining bytes
are split across several connections and appended in order. The repo publishes
SHA256SUMS, so correctness is checked rather than assumed.
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

URL = (
    "https://huggingface.co/datasets/ljang0/mypcbench-qemu-baseline/"
    "resolve/main/michael_scott.qcow2"
)
TOTAL = 5_132_255_232
SHA256 = "6e2c6954b3f22daebef832b8b7d5bc0ea76fe540da57192fb8b0923cef5e4770"


def fetch_range(index: int, start: int, end: int, parts: Path) -> tuple[int, Path]:
    target = parts / f"part_{index:02d}"
    expected = end - start + 1
    if target.exists() and target.stat().st_size == expected:
        return index, target
    subprocess.run(
        ["curl", "-sfL", "--retry", "5", "--retry-delay", "2",
         "-r", f"{start}-{end}", "-o", str(target), URL],
        check=True,
    )
    got = target.stat().st_size
    if got != expected:
        raise RuntimeError(f"part {index}: expected {expected} bytes, got {got}")
    return index, target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path,
                        default=Path(__file__).resolve().parents[1] / "vm" / "michael_scott.qcow2")
    parser.add_argument("--streams", type=int, default=6)
    args = parser.parse_args()

    have = args.out.stat().st_size if args.out.exists() else 0
    remaining = TOTAL - have
    print(f"have {have:,} bytes, remaining {remaining:,}")

    if remaining > 0:
        parts = args.out.parent / "parts"
        parts.mkdir(exist_ok=True)
        chunk = remaining // args.streams + 1
        jobs = []
        for i in range(args.streams):
            start = have + i * chunk
            end = min(start + chunk - 1, TOTAL - 1)
            if start > end:
                break
            jobs.append((i, start, end))

        with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
            done = sorted(pool.map(lambda j: fetch_range(*j, parts), jobs))

        with open(args.out, "ab") as handle:
            for index, path in done:
                with open(path, "rb") as part:
                    while True:
                        buf = part.read(8 << 20)
                        if not buf:
                            break
                        handle.write(buf)
                path.unlink()
                print(f"appended part {index}")
        parts.rmdir()

    size = args.out.stat().st_size
    print(f"size {size:,} bytes (expected {TOTAL:,})")
    if size != TOTAL:
        print("SIZE MISMATCH")
        return 1

    digest = hashlib.sha256()
    with open(args.out, "rb") as handle:
        while True:
            buf = handle.read(16 << 20)
            if not buf:
                break
            digest.update(buf)
    actual = digest.hexdigest()
    print(f"sha256 {actual}")
    print("digest matches SHA256SUMS" if actual == SHA256 else "DIGEST MISMATCH")
    return 0 if actual == SHA256 else 1


if __name__ == "__main__":
    sys.exit(main())
