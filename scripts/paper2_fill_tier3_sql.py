#!/usr/bin/env python3
"""Fill Paper 2 inventory Tier 3 intervention SQL (relative where D exists).

Units:
  aggregation-f037, contradiction-f024, preference_inference-f010
    → READY_RELATIVE (relative SQL; gate may REJECT)
  situated_action-f029
    → NEEDS_HAND_D (frozen determining=[], do not invent D)

Does not touch counterfactual-f003-I2.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "cf" / "paper2_interventions.json"
EMAIL = ":email"

TOP_SENDER_PROBE = (
    "SELECT from_email AS top_sender, count(*) AS top_sender_count "
    f"FROM emails WHERE user_email = {EMAIL} "
    "GROUP BY from_email ORDER BY count(*) DESC LIMIT 1"
)
# Reassign a batch of messages from the current top sender (subquery — no G0 literal).
TOP_SENDER_PATCH = (
    "UPDATE emails SET from_email = from_email || '.cf-moved' WHERE id IN ("
    "SELECT id FROM emails WHERE user_email = :email AND from_email = ("
    "SELECT from_email FROM emails WHERE user_email = :email "
    "GROUP BY from_email ORDER BY count(*) DESC LIMIT 1"
    ") ORDER BY id LIMIT 80)"
)

# Designated human correspondent for latency (not a noreply bot).
JIM = "lower(from_email) = 'jim.halpert@dundermifflin.com'"
TOBY = "lower(from_email) = 'toby.flenderson@dundermifflin.com'"

# Chili's card charge on receipt date (vaultbank). Receipt file itself is not
# relatively patchable with current inject (string replace needs absolute G0).
CHILI_MAR22 = (
    "lower(t.description) LIKE '%chili%' AND t.date = '2026-03-22'"
)


def ep(db: str, sql: str) -> dict:
    return {"db": db, "sql": sql}


def fill(entry: dict, **kwargs) -> None:
    entry.update(kwargs)
    entry["role"] = "paper2_tier3"
    entry["_inventory_tier"] = 3
    if entry.get("_sql_status") == "NEEDS_HAND_D":
        return
    if entry.get("probe") and entry.get("patch") is not None:
        entry["_sql_status"] = "READY_RELATIVE"
    entry["_sql_note"] = (
        "Tier 3 relative patch from guest schema dump "
        "(out/paper2_tier3_schema_dump.json). G0/G1 from live inject-probe. "
        "Zero-row / unstable gold → REJECT, not a D rewrite."
    )


def main() -> int:
    doc = json.loads(PATH.read_text())
    by_id = {e["id"]: e for e in doc["interventions"]}

    # --- aggregation-f037: move top-sender identity/count via reassignment ---
    fill(
        by_id["aggregation-f037"],
        db="mail.sqlite",
        probe=TOP_SENDER_PROBE,
        patch=[TOP_SENDER_PATCH],
        extra_probes=[
            # Held: a mid-rank human sender's count (toby) must not move.
            ep(
                "mail.sqlite",
                f"SELECT from_email, count(*) AS n FROM emails "
                f"WHERE user_email = {EMAIL} AND {TOBY} GROUP BY from_email",
            )
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": (
                "Reassign 80 msgs from current top from_email. "
                "Unstable mail gold → REJECT ok; do not rewrite D."
            ),
        },
        do_not_touch="toby.flenderson message set; non-top senders",
        moves=["top_sender", "top_sender_count"],
        holds_this_I=["toby_sender_count"],
    )

    # --- contradiction-f024: relative vault chili charge; hold SpeedTax ---
    # Semantic D includes file receipt amount; file channel cannot do relative
    # SET without absolute replace. Vault March-22 chili is the relative SQL
    # surface available on mapped_dbs. Gate may REJECT if this is not
    # identifiable against the receipt file component — that is allowed.
    fill(
        by_id["contradiction-f024"],
        db="vaultbank.sqlite",
        probe=(
            "SELECT t.id, t.date, t.description, t.amount FROM transactions t "
            "JOIN accounts a ON a.id = t.account_id "
            f"WHERE a.user_email = {EMAIL} AND {CHILI_MAR22}"
        ),
        patch=[
            "UPDATE transactions SET amount = amount * 1.5 WHERE id IN ("
            "SELECT t.id FROM transactions t JOIN accounts a ON a.id = t.account_id "
            f"WHERE a.user_email = {EMAIL} AND {CHILI_MAR22})"
        ],
        extra_probes=[
            ep(
                "speedtax.sqlite",
                "SELECT d.field_name, d.field_value FROM tax_data d "
                "JOIN tax_returns tr ON tr.id = d.return_id "
                f"WHERE tr.user_email = {EMAIL} AND tr.tax_year = 2025 "
                "AND d.field_name IN ("
                "'charitable_contributions','charitable_total',"
                "'medical_expenses','home_office_days') "
                "ORDER BY d.field_name",
            )
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": (
                "Relative vault Chili's 2026-03-22 amount; SpeedTax deductions held. "
                "Receipt file not relatively patchable — REJECT ok if not identifiable."
            ),
        },
        do_not_touch="speedtax tax_data; Downloads/Chilis_Receipt_March_2026.txt",
        moves=["chilis_receipt_amount"],
        holds_this_I=["speedtax_overlap"],
    )

    # --- preference_inference-f010: shift Jim timestamps; hold Toby dates ---
    fill(
        by_id["preference_inference-f010"],
        db="mail.sqlite",
        probe=(
            f"SELECT id, from_email, date FROM emails "
            f"WHERE user_email = {EMAIL} AND {JIM} ORDER BY date, id LIMIT 10"
        ),
        patch=[
            # Relative +3 days on ISO-ish timestamps; if format breaks → tech/REJECT.
            "UPDATE emails SET date = "
            "strftime('%Y-%m-%dT%H:%M:%SZ', datetime(replace(substr(date,1,19),'T',' '), '+3 days')) "
            f"WHERE user_email = {EMAIL} AND {JIM}"
        ],
        extra_probes=[
            ep(
                "mail.sqlite",
                f"SELECT id, date FROM emails WHERE user_email = {EMAIL} AND {TOBY} "
                "ORDER BY date, id LIMIT 10",
            )
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": (
                "Perturb Jim inbound dates (+3d) as designated_sender_latency surface. "
                "Mail timestamps may be non-deterministic → REJECT ok."
            ),
        },
        do_not_touch="toby.flenderson timestamps; sent table",
        moves=["designated_sender_latency"],
        holds_this_I=["toby_inbound_dates"],
    )

    # --- situated_action-f029: NO D — do not invent ---
    e = by_id["situated_action-f029"]
    e["role"] = "paper2_tier3"
    e["_inventory_tier"] = 3
    e["_sql_status"] = "NEEDS_HAND_D"
    e["patch"] = []
    e["probe"] = ""
    e["extra_probes"] = []
    e["_sql_note"] = (
        "Stopped before SQL: registry_semantic_frozen.json has determining=[]. "
        "review_decision: no invented D (action/style only; former zero_candidates). "
        "Hand-design D in a separate dated amendment before any inject-probe. "
        "Do not invent D under gate time pressure (DESIGN.md §2)."
    )
    e["gate_skip_reason"] = "needs_hand_D_design"

    PATH.write_text(json.dumps(doc, indent=2) + "\n")
    ready = [
        x["id"]
        for x in doc["interventions"]
        if x.get("_inventory_tier") == 3 and x.get("_sql_status") == "READY_RELATIVE"
    ]
    needs = [
        x["id"]
        for x in doc["interventions"]
        if x.get("_sql_status") == "NEEDS_HAND_D"
    ]
    print(f"wrote {PATH}")
    print(f"Tier 3 READY_RELATIVE ({len(ready)}):", " ".join(sorted(ready)))
    print(f"Tier 3 NEEDS_HAND_D ({len(needs)}):", " ".join(sorted(needs)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
