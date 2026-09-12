#!/usr/bin/env python3
"""Hash and seal V01–V20. Does not score them."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VDIR = ROOT / "sealed" / "v"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def main() -> None:
    files = sorted(VDIR.glob("V*.json"))
    if [p.stem for p in files] != [f"V{i:02d}" for i in range(1, 21)]:
        raise SystemExit(f"unexpected V set: {[p.name for p in files]}")
    per = {}
    h = hashlib.sha256()
    for p in files:
        digest = sha256_file(p)
        per[p.name] = digest
        h.update(digest.encode())
        h.update(b"\n")
    seal = {
        "status": "SEALED",
        "n": 20,
        "combined_sha256": h.hexdigest(),
        "files": per,
        "params_v_sha256": sha256_file(ROOT / "params_v.json"),
        "generator_sha256": sha256_file(ROOT / "generate_slate.py"),
        "wordlist_v_sha256": sha256_file(ROOT / "wordlists_v.txt"),
        "authorship_sha256": sha256_file(ROOT / "P4_AUTHORSHIP.md"),
        "rule": "Do not score V* until instrument freeze. Do not edit observations.",
    }
    out = ROOT / "sealed" / "V_SEAL.json"
    out.write_text(json.dumps(seal, indent=2, sort_keys=True) + "\n")
    marker = ROOT / "sealed" / "DO_NOT_SCORE.txt"
    marker.write_text(
        "V01–V20 are sealed. Scoring before freeze voids the seal.\n"
        f"combined_sha256={seal['combined_sha256']}\n"
    )
    print(json.dumps({"combined_sha256": seal["combined_sha256"], "n": 20}, indent=2))


if __name__ == "__main__":
    main()
