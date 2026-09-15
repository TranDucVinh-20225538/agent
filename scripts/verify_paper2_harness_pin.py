#!/usr/bin/env python3
"""Verify out/paper2_harness_pin.json against on-disk bytes (no network)."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    pin_path = root / "out" / "paper2_harness_pin.json"
    pin = json.loads(pin_path.read_text())
    drift = []
    missing = []
    for section in ("tracked_measurement_patch", "upstream_gitignored_harness"):
        for rel, meta in pin.get(section, {}).items():
            p = root / rel
            if not p.exists():
                missing.append(rel)
                continue
            got = sha256(p)
            if got != meta.get("sha256"):
                drift.append({"path": rel, "expected": meta.get("sha256"), "got": got})
    report = {
        "pin": str(pin_path),
        "ok": not drift and not missing,
        "drift": drift,
        "missing": missing,
        "closure_C_answer": pin.get("closure_C", {}).get("answer"),
        "unresolved": pin.get("closure_C", {}).get("unresolved", []),
    }
    out = root / "out" / "gate15_closure_C_verify.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
