"""Build preference_inference-f009 patches from the live guest ranking.

Count flip inserts zero-total clone orders at the runner-up store so spend
does not move. Spend flip adds a delta to one existing order at the runner-up
spend store so the row count does not move.

If the two winners are the same store, the experiment cannot tell the bases
apart and every builder refuses to patch.
"""

from __future__ import annotations

import json
from typing import Callable

RANK_SQL = """
SELECT s.id AS store_id,
       s.name AS store,
       COUNT(*) AS n,
       SUM(o.total) AS spend
FROM orders o
JOIN stores s ON s.id = o.store_id
WHERE o.user_email = '{email}'
GROUP BY s.id, s.name
ORDER BY n DESC, spend DESC
"""

TEMPLATE_SQL = """
SELECT id, user_email, store_id, world_id, actor_id, vm_id, status,
       delivery_fee, service_fee, tip, delivery_window, substitution_preference,
       delivery_slot_id, delivery_slot_label, delivery_slot_price,
       promo_code, promo_discount, tracking_status, shopper_name, shopper_photo,
       is_express, created_at, delivered_at, address
FROM orders
WHERE user_email = '{email}'
ORDER BY id
LIMIT 1
"""


def parse_rankings(probe_json: str) -> list[dict]:
    rows = json.loads(probe_json or "[]")
    for row in rows:
        row["n"] = int(row["n"])
        row["spend"] = float(row["spend"] or 0)
        row["store_id"] = int(row["store_id"])
    return rows


def winners(rows: list[dict]) -> tuple[dict, dict, dict, dict]:
    if len(rows) < 2:
        raise SystemExit("GATE: fewer than two stores in the order history; cannot split bases")
    by_n = sorted(rows, key=lambda r: (-r["n"], -r["spend"], r["store"]))
    by_s = sorted(rows, key=lambda r: (-r["spend"], -r["n"], r["store"]))
    return by_n[0], by_n[1], by_s[0], by_s[1]


def bases_identical(rows: list[dict]) -> bool:
    c0, _, s0, _ = winners(rows)
    return c0["store_id"] == s0["store_id"]


def quote(value) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def insert_zero_total_clones(template: dict, store_id: int, k: int) -> list[str]:
    cols = [
        "user_email", "store_id", "world_id", "actor_id", "vm_id", "status",
        "total", "delivery_fee", "service_fee", "tip", "delivery_window",
        "substitution_preference", "delivery_slot_id", "delivery_slot_label",
        "delivery_slot_price", "promo_code", "promo_discount", "tracking_status",
        "shopper_name", "shopper_photo", "is_express", "created_at",
        "delivered_at", "address",
    ]
    statements = []
    for _ in range(k):
        values = []
        for col in cols:
            if col == "store_id":
                values.append(str(store_id))
            elif col == "total":
                values.append("0")
            else:
                values.append(quote(template.get(col)))
        statements.append(
            f"INSERT INTO orders ({', '.join(cols)}) VALUES ({', '.join(values)}); "
            "INSERT INTO order_items "
            "(order_id, product_id, product_name, quantity, price, "
            "substitution_type, substitution_product_id, substitution_product_name, "
            "world_id, actor_id, vm_id) "
            "SELECT last_insert_rowid(), product_id, product_name, quantity, 0, "
            "substitution_type, substitution_product_id, substitution_product_name, "
            "world_id, actor_id, vm_id "
            f"FROM order_items WHERE order_id = {int(template['id'])} LIMIT 1"
        )
    return statements


def build(kind: str, sqlite_fn: Callable[..., str], email: str) -> list[str]:
    rows = parse_rankings(sqlite_fn(RANK_SQL.format(email=email), True))
    if bases_identical(rows):
        raise SystemExit(
            "GATE: order-count winner and total-spend winner are the same store; "
            "the two bases cannot be distinguished. Do not run A/B. Dump the "
            "ranking and stop."
        )
    count_w, count_2, spend_w, spend_2 = winners(rows)
    if kind == "A":
        k = count_w["n"] - count_2["n"] + 1
        raw = sqlite_fn(TEMPLATE_SQL.format(email=email), True)
        template = json.loads(raw)[0]
        return insert_zero_total_clones(template, count_2["store_id"], k)
    if kind == "B":
        delta = spend_w["spend"] - spend_2["spend"] + 0.01
        return [
            "UPDATE orders SET total = total + {delta} WHERE id = ("
            "SELECT id FROM orders WHERE user_email = {email} "
            "AND store_id = {sid} ORDER BY id LIMIT 1)"
            .format(delta=delta, email=quote(email), sid=int(spend_2["store_id"]))
        ]
    if kind == "AB":
        return build("A", sqlite_fn, email) + build("B", sqlite_fn, email)
    raise SystemExit(f"unknown f009 patch kind {kind!r}")
