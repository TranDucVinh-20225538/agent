"""Build preference_inference-f004 HangryDash rank-flip from the live guest ranking.

Frozen constraints (cf/phase_b_interventions.json):
- HangryDash count winner must change from Cooper's Seafood House
- TableFind is not touched (no SQL against tablefind.sqlite)
- k and restaurant ids are computed from live HD counts, not from a
  hand-written ranking. Do not open the UI and edit SQL after seeing it.

Rule: reassign the k lowest-id HangryDash orders of the current unique
count winner to the current runner-up, where

    k = floor((n0 - n1) / 2) + 1

so the winner is unique after the move. Total HD order count is unchanged,
so the dine-vs-delivery volume split is unchanged.
"""

from __future__ import annotations

import json
from typing import Callable

REQUIRED_WINNER = "Cooper's Seafood House"

RANK_SQL = """
SELECT r.id AS restaurant_id,
       r.name AS name,
       COUNT(*) AS n
FROM orders o
JOIN restaurants r ON r.id = o.restaurant_id
WHERE o.user_email = '{email}'
GROUP BY r.id, r.name
ORDER BY n DESC, r.name
"""


def parse_rankings(probe_json: str) -> list[dict]:
    rows = json.loads(probe_json or "[]")
    out = []
    for row in rows:
        out.append({
            "restaurant_id": int(row["restaurant_id"]),
            "name": row["name"],
            "n": int(row["n"]),
        })
    return out


def flip_k(n_win: int, n_run: int) -> int:
    if n_run >= n_win:
        raise SystemExit(
            f"GATE: HangryDash winner n={n_win} is not strictly ahead of "
            f"runner-up n={n_run}; cannot flip a unique top."
        )
    return (n_win - n_run) // 2 + 1


def quote(value: str) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def build(sqlite_fn: Callable[..., str], email: str) -> list[str]:
    raw = sqlite_fn(RANK_SQL.format(email=email), True)
    rows = parse_rankings(raw)
    if len(rows) < 2:
        raise SystemExit(
            "GATE: fewer than two HangryDash restaurants in the order history; "
            "cannot flip the count winner."
        )
    winner, runner = rows[0], rows[1]
    if winner["name"] != REQUIRED_WINNER:
        raise SystemExit(
            f"GATE: live HangryDash winner is {winner['name']!r}, not "
            f"{REQUIRED_WINNER!r}. The frozen contrast requires Cooper's as "
            f"the HD top that I moves. Do not invent a different I."
        )
    k = flip_k(winner["n"], runner["n"])
    win_id = int(winner["restaurant_id"])
    run_id = int(runner["restaurant_id"])
    # Nested subquery: SQLite rejects LIMIT directly inside some IN-forms.
    sql = (
        f"UPDATE orders SET restaurant_id = {run_id} "
        f"WHERE id IN ("
        f"SELECT id FROM ("
        f"SELECT id FROM orders "
        f"WHERE user_email = {quote(email)} AND restaurant_id = {win_id} "
        f"ORDER BY id ASC LIMIT {k}"
        f") AS _f004_ids)"
    )
    return [sql]


def self_test() -> None:
    assert flip_k(88, 28) == 31
    assert 88 - 31 == 57
    assert 28 + 31 == 59

    def sqlite_fn(sql: str, json_out: bool = False) -> str:
        assert "COUNT" in sql.upper()
        return json.dumps([
            {"restaurant_id": 11, "name": "Cooper's Seafood House", "n": 88},
            {"restaurant_id": 22, "name": "Backyard Ale House", "n": 28},
            {"restaurant_id": 33, "name": "Northern Light Espresso Bar", "n": 28},
        ])

    stmts = build(sqlite_fn, "michael.scott@dundermifflin.com")
    assert len(stmts) == 1
    sql = stmts[0]
    assert "LIMIT 31" in sql
    assert "restaurant_id = 22" in sql
    assert "restaurant_id = 11" in sql
    assert "tablefind" not in sql.lower()

    def bad_winner(sql: str, json_out: bool = False) -> str:
        return json.dumps([
            {"restaurant_id": 22, "name": "Backyard Ale House", "n": 88},
            {"restaurant_id": 11, "name": "Cooper's Seafood House", "n": 28},
        ])

    try:
        build(bad_winner, "michael.scott@dundermifflin.com")
    except SystemExit as exc:
        assert "not" in str(exc) and "Cooper" in str(exc)
    else:
        raise AssertionError("expected GATE on non-Cooper winner")


if __name__ == "__main__":
    self_test()
    print("f004_dynamic self-test ok")
