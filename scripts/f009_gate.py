#!/usr/bin/env python3
"""Gate Phase C: dump both rankings; exit 2 if they name the same store."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import f009_dynamic  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def load_rows(path: Path) -> list[dict]:
    payload = json.loads(path.read_text())
    raw = payload.get("probe_before") or payload.get("probe_after")
    if isinstance(raw, str):
        return f009_dynamic.parse_rankings(raw)
    return f009_dynamic.parse_rankings(json.dumps(raw))


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: f009_gate.py <guest.json> [out.txt]", file=sys.stderr)
        return 2
    src = Path(sys.argv[1])
    dest = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "results" / "preference_f009_probe.sql.txt"
    rows = load_rows(src)
    dest.parent.mkdir(parents=True, exist_ok=True)
    lines = ["-- live Kwik-E-Mart ranking, Michael Scott", "store_id\tstore\tn\tspend"]
    for row in rows:
        lines.append(f"{row['store_id']}\t{row['store']}\t{row['n']}\t{row['spend']}")
    identical = f009_dynamic.bases_identical(rows)
    if identical:
        c0, _, s0, _ = f009_dynamic.winners(rows)
        lines += [
            "",
            "GATE: count winner and spend winner are the same store "
            f"({c0['store']}). The two bases cannot be distinguished. Stop.",
        ]
        dest.write_text("\n".join(lines) + "\n")
        print(dest.read_text())
        return 2
    count_w, count_2, spend_w, spend_2 = f009_dynamic.winners(rows)
    lines += [
        "",
        f"order-count winner = {count_w['store']} (n={count_w['n']})",
        f"order-count runner-up = {count_2['store']} (n={count_2['n']})",
        f"total-spend winner = {spend_w['store']} (spend={spend_w['spend']})",
        f"total-spend runner-up = {spend_2['store']} (spend={spend_2['spend']})",
        "",
        "Bases differ. Condition A flips count only; Condition B flips spend only.",
    ]
    dest.write_text("\n".join(lines) + "\n")
    print(dest.read_text())
    return 0


if __name__ == "__main__":
    sys.exit(main())
