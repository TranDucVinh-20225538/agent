"""Build situated_action-f009 patches from live HangryDash Chili's history.

A: clone older orders of the runner-up item until it is the unique modal;
   most-recent Chili's basket is not touched.
B: rewrite only the most-recent Chili's `items` to a non-modal basket;
   refuse if that would also change the modal.
"""

from __future__ import annotations

import json
from collections import Counter
from typing import Callable

CHILI_SQL = """
SELECT o.id,
       o.items,
       o.placed_at,
       o.date,
       r.name AS restaurant
FROM orders o
JOIN restaurants r ON r.id = o.restaurant_id
WHERE o.user_email = '{email}'
  AND lower(r.name) LIKE '%chili%'
ORDER BY COALESCE(o.placed_at, o.date) DESC, o.id DESC
"""

ROW_SQL = "SELECT * FROM orders WHERE id = {oid}"

INSERT_COLS = [
    "user_email", "restaurant_id", "date", "status", "subtotal", "tax",
    "service_fee", "tip", "delivery_fee", "total", "delivery_address", "items",
    "placed_at", "fulfillment_type", "promo_code", "promo_discount",
    "credits_applied", "dashpass_applied", "dashpass_savings", "tip_amount",
    "tip_adjusted_at", "delivered_at",
]


def parse_items(raw) -> list[str]:
    if raw is None or raw == "":
        return []
    if isinstance(raw, list):
        data = raw
    else:
        try:
            data = json.loads(raw)
        except (TypeError, json.JSONDecodeError):
            return [str(raw).strip()] if str(raw).strip() else []
    names = []
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return [str(data)]
    for item in data:
        if isinstance(item, str):
            names.append(item.strip())
        elif isinstance(item, dict):
            name = item.get("name") or item.get("item") or item.get("title") or item.get("product_name")
            if name:
                names.append(str(name).strip())
    return [n for n in names if n]


def parse_orders(probe_json: str) -> list[dict]:
    rows = json.loads(probe_json or "[]")
    out = []
    for row in rows:
        items = parse_items(row.get("items"))
        out.append({
            "id": int(row["id"]),
            "items": items,
            "items_raw": row.get("items"),
            "placed_at": row.get("placed_at") or row.get("date"),
            "restaurant": row.get("restaurant"),
        })
    return out


def frequencies(orders: list[dict]) -> Counter:
    counts: Counter = Counter()
    for order in orders:
        for name in dict.fromkeys(order["items"]):
            counts[name] += 1
    return counts


def modal_and_runner(counts: Counter) -> tuple[str | None, int, str | None, int]:
    if not counts:
        return None, 0, None, 0
    ranked = counts.most_common()
    modal, n0 = ranked[0]
    if len(ranked) == 1:
        return modal, n0, None, 0
    return modal, n0, ranked[1][0], ranked[1][1]


def quote(value) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def gate_reason(orders: list[dict]) -> str | None:
    if not orders:
        return "GATE: no Chili's orders on this seed; cannot reconstruct a usual item."
    counts = frequencies(orders)
    modal, n0, runner, n1 = modal_and_runner(counts)
    if runner is None:
        return (
            f"GATE: only one distinct Chili's item ({modal}, n={n0}). "
            "Cannot flip the modal onto another observed item."
        )
    return None


def template_order_for_item(orders: list[dict], item: str) -> dict | None:
    singleton = [o for o in orders if o["items"] == [item]]
    if singleton:
        return singleton[0]
    containing = [o for o in orders if item in o["items"]]
    return containing[0] if containing else None


def build(kind: str, sqlite_fn: Callable[..., str], email: str) -> list[str]:
    orders = parse_orders(sqlite_fn(CHILI_SQL.format(email=email), True))
    reason = gate_reason(orders)
    if reason:
        raise SystemExit(reason)
    counts = frequencies(orders)
    modal, n0, runner, n1 = modal_and_runner(counts)
    recent = orders[0]
    if kind == "A":
        template = template_order_for_item(orders, runner)
        if template is None:
            raise SystemExit(f"GATE: no Chili's order to clone for runner-up {runner!r}")
        if template["items"] != [runner]:
            raise SystemExit(
                f"GATE: runner-up {runner!r} only appears inside mixed baskets; "
                "cloning would also increment other items."
            )
        k = n0 - n1 + 1
        row = json.loads(sqlite_fn(ROW_SQL.format(oid=template["id"]), True))[0]
        oldest = min(o["placed_at"] or "" for o in orders)
        statements = []
        for i in range(k):
            values = []
            for col in INSERT_COLS:
                if col == "placed_at":
                    values.append(f"datetime({quote(oldest)}, '-{i + 1} hours')")
                elif col == "date":
                    values.append(f"date(datetime({quote(oldest)}, '-{i + 1} hours'))")
                else:
                    values.append(quote(row.get(col)))
            statements.append(
                f"INSERT INTO orders ({', '.join(INSERT_COLS)}) VALUES ({', '.join(values)})"
            )
        return statements
    if kind == "B":
        if recent["items"] == [runner]:
            raise SystemExit(
                "GATE: most-recent Chili's basket is already the runner-up; recency cannot be flipped."
            )
        runner_order = template_order_for_item(orders, runner)
        if runner_order is None or runner_order["items"] != [runner]:
            raise SystemExit(
                f"GATE: no singleton basket for runner-up {runner!r} to copy into most-recent."
            )
        updated = counts.copy()
        for name in dict.fromkeys(recent["items"]):
            updated[name] -= 1
            if updated[name] <= 0:
                del updated[name]
        updated[runner] += 1
        top = updated.most_common()
        if not top or top[0][0] != modal or (len(top) > 1 and top[0][1] == top[1][1]):
            raise SystemExit(
                "GATE: rewriting the most-recent basket would change or tie the modal. Refuse B."
            )
        return [
            f"UPDATE orders SET items = {quote(runner_order['items_raw'])} "
            f"WHERE id = {recent['id']}"
        ]
    if kind == "AB":
        return build("A", sqlite_fn, email) + build("B", sqlite_fn, email)
    raise SystemExit(f"unknown sa009 patch kind {kind!r}")
