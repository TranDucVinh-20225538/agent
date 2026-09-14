#!/usr/bin/env python3
"""Gate slot 5: dump Chili's item frequencies; exit 2 if the modal cannot be flipped."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sa009_dynamic  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def load_orders(path: Path) -> list[dict]:
    payload = json.loads(path.read_text())
    raw = payload.get("probe_before") or payload.get("probe_after")
    if not isinstance(raw, str):
        raw = json.dumps(raw)
    return sa009_dynamic.parse_orders(raw)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: sa009_gate.py <guest.json> [out.txt]", file=sys.stderr)
        return 2
    src = Path(sys.argv[1])
    dest = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "results" / "sa009_probe.sql.txt"
    orders = load_orders(src)
    dest.parent.mkdir(parents=True, exist_ok=True)
    lines = ["-- live HangryDash Chili's history, Michael Scott", "id\tplaced_at\titems"]
    for order in orders:
        lines.append(f"{order['id']}\t{order['placed_at']}\t{order['items']}")
    reason = sa009_dynamic.gate_reason(orders)
    counts = sa009_dynamic.frequencies(orders)
    lines += ["", "item\tn"]
    for name, n in counts.most_common():
        lines.append(f"{name}\t{n}")
    if reason:
        lines += ["", reason]
        dest.write_text("\n".join(lines) + "\n")
        print(dest.read_text())
        return 2
    modal, n0, runner, n1 = sa009_dynamic.modal_and_runner(counts)
    recent = orders[0] if orders else None
    lines += [
        "",
        f"modal item = {modal} (n={n0})",
        f"runner-up item = {runner} (n={n1})",
        f"most-recent Chili's basket = {recent['items'] if recent else None}",
        f"modal == most-recent singleton: {recent['items'] == [modal] if recent else None}",
        "",
        "Condition A clones older runner-up orders until the modal flips; recency is held.",
        "Condition B rewrites only the most-recent items; refused if that would move the modal.",
    ]
    dest.write_text("\n".join(lines) + "\n")
    print(dest.read_text())
    return 0


if __name__ == "__main__":
    sys.exit(main())
