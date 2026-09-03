#!/usr/bin/env python3
"""Fill Paper 2 inventory Tier 2 intervention SQL (relative patches).

Scope = inject_probe_inventory.md Tier 2 only:
  contradiction-f014, counterfactual-f001, preference_inference-f014(+I2),
  retrieval-f009, retrieval-f010.

Does **not** fill inventory Tier 3 (aggregation-f037, contradiction-f024,
preference_inference-f010, situated_action-f029) or counterfactual-f003-I2.

Does not invent G0/G1 literals. Relative SET col = col * k / + k / || suffix.
Zero-row UPDATE → gold_moved false → REJECT, not a D rewrite.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "cf" / "paper2_interventions.json"
EMAIL = ":email"

# --- shared WHERE fragments (schema-backed; no G0 literals in SET targets) ---
MONTEGO = (
    "lower(property_name) LIKE '%montego bay%' OR "
    "(lower(property_name) LIKE '%sandals%' AND lower(location) LIKE '%montego%')"
)
# Prefer the named Montego Bay property (SM-88431) over Royal Caribbean Suite.
MONTEGO_BAY_STAY = "lower(property_name) LIKE '%montego bay%'"
GREENWICH = "lower(property_name) LIKE '%greenwich%'"
RADISSON = "lower(property_name) LIKE '%radisson%'"
JAMAICA_FLIGHT = (
    "upper(destination) = 'MBJ' OR lower(destination_city) LIKE '%jamaica%' "
    "OR upper(ifnull(flight_number,'')) = 'DN1562'"
)
NYC_FLIGHT = (
    "upper(destination) = 'JFK' OR lower(destination_city) LIKE '%new york%' "
    "OR lower(destination_city) LIKE '%manhattan%' "
    "OR upper(ifnull(flight_number,'')) = 'DN6769'"
)
W2_GROSS = "field_name = 'w2_gross_wages'"
SALARY_DM = (
    "(lower(content) LIKE '%160k%' OR lower(content) LIKE '%160 k%' "
    "OR (lower(content) LIKE '%160%' AND lower(content) LIKE '%base%'))"
)
LOCKEDIN_CURRENT = (
    "profile_id IN (SELECT id FROM profiles WHERE email = :email) AND ifnull(is_current,0) = 1"
)


def ep(db: str, sql: str) -> dict:
    return {"db": db, "sql": sql}


def fill(entry: dict, **kwargs) -> None:
    entry.update(kwargs)
    entry["role"] = "paper2_tier2"
    if entry.get("probe") and entry.get("patch") is not None:
        entry["_sql_status"] = "READY_RELATIVE"
    entry["_sql_note"] = (
        "Tier 2 relative patch from guest schema dump (out/paper2_tier2_schema_dump.json). "
        "G0/G1 from live inject-probe. Zero-row UPDATE is identifiability reject, not a D rewrite."
    )
    entry["_inventory_tier"] = 2


def main() -> int:
    doc = json.loads(PATH.read_text())
    by_id = {e["id"]: e for e in doc["interventions"]}

    # --- contradiction-f014: move W-2 gross; hold LockedIn + salary DM ---
    fill(
        by_id["contradiction-f014"],
        db="speedtax.sqlite",
        probe=(
            "SELECT d.field_name, d.field_value FROM tax_data d "
            "JOIN tax_returns tr ON tr.id = d.return_id "
            f"WHERE tr.user_email = {EMAIL} AND tr.tax_year = 2025 AND {W2_GROSS}"
        ),
        patch=[
            "UPDATE tax_data SET field_value = CAST(CAST(field_value AS REAL) * 0.75 AS TEXT) "
            f"WHERE {W2_GROSS} AND return_id IN ("
            f"SELECT id FROM tax_returns WHERE user_email = {EMAIL} AND tax_year = 2025)"
        ],
        extra_probes=[
            ep(
                "lockedin.sqlite",
                f"SELECT title, company FROM experience WHERE {LOCKEDIN_CURRENT}",
            ),
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": (
                "I moves w2_gross_wages only. lockedin_title_company probed held. "
                "claimed_salary_dm held by do_not_touch (no buzzchat patch this I)."
            ),
        },
        do_not_touch="lockedin experience; buzzchat/hoolichat salary DM; paycheck deposits",
        moves=["w2_gross_wages"],
        holds_this_I=["lockedin_title_company", "claimed_salary_dm"],
        semantic_held=["lockedin_title_company"],
    )

    # --- counterfactual-f001: move Jamaica hotel total; hold Dinoco Jamaica fare ---
    fill(
        by_id["counterfactual-f001"],
        db="cheskepdia.sqlite",
        probe=(
            f"SELECT id, property_name, location, total_price FROM bookings "
            f"WHERE user_email = {EMAIL} AND ({MONTEGO_BAY_STAY})"
        ),
        patch=[
            f"UPDATE bookings SET total_price = total_price * 1.35 "
            f"WHERE user_email = {EMAIL} AND ({MONTEGO_BAY_STAY})"
        ],
        extra_probes=[
            ep(
                "dinoco-airlines.sqlite",
                f"SELECT id, flight_number, destination, destination_city, fare_paid, confirmation_code "
                f"FROM flights WHERE user_email = {EMAIL} AND ({JAMAICA_FLIGHT})",
            )
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "I1 jamaica_hotel_total (Montego Bay); jamaica_flight_cost held this I.",
        },
        do_not_touch="dinoco jamaica fare_paid; calendar/mail/etaxi",
        moves=["jamaica_hotel_total"],
        holds_this_I=["jamaica_flight_cost"],
    )

    # --- preference_inference-f014 multi-I: designated Radisson row ---
    fill(
        by_id["preference_inference-f014"],
        db="cheskepdia.sqlite",
        probe=(
            f"SELECT id, property_name, total_price, confirmation_code FROM bookings "
            f"WHERE user_email = {EMAIL} AND ({RADISSON})"
        ),
        patch=[
            f"UPDATE bookings SET property_name = property_name || ' (Budget Reflag)' "
            f"WHERE user_email = {EMAIL} AND ({RADISSON})"
        ],
        extra_probes=[
            ep(
                "cheskepdia.sqlite",
                f"SELECT total_price FROM bookings WHERE user_email = {EMAIL} AND ({RADISSON})",
            )
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "I1 designated_booking_property; total held.",
        },
        do_not_touch="designated total; other bookings",
        moves=["designated_booking_property"],
        holds_this_I=["designated_booking_total"],
    )
    fill(
        by_id["preference_inference-f014-I2"],
        db="cheskepdia.sqlite",
        probe=(
            f"SELECT id, property_name, total_price, confirmation_code FROM bookings "
            f"WHERE user_email = {EMAIL} AND ({RADISSON})"
        ),
        patch=[
            f"UPDATE bookings SET total_price = total_price * 1.5 "
            f"WHERE user_email = {EMAIL} AND ({RADISSON})"
        ],
        extra_probes=[
            ep(
                "cheskepdia.sqlite",
                f"SELECT property_name FROM bookings WHERE user_email = {EMAIL} AND ({RADISSON})",
            )
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "I2 designated_booking_total; property held.",
        },
        do_not_touch="designated property_name; other bookings",
        moves=["designated_booking_total"],
        holds_this_I=["designated_booking_property"],
    )

    # --- retrieval-f009: move Greenwich hotel conf; hold flight conf + check-in ---
    fill(
        by_id["retrieval-f009"],
        db="cheskepdia.sqlite",
        probe=(
            f"SELECT confirmation_code, property_name, check_in FROM bookings "
            f"WHERE user_email = {EMAIL} AND ({GREENWICH})"
        ),
        patch=[
            f"UPDATE bookings SET confirmation_code = confirmation_code || '-CF' "
            f"WHERE user_email = {EMAIL} AND ({GREENWICH})"
        ],
        extra_probes=[
            ep(
                "dinoco-airlines.sqlite",
                f"SELECT confirmation_code, flight_number, destination, departure_date "
                f"FROM flights WHERE user_email = {EMAIL} AND ({NYC_FLIGHT})",
            ),
            ep(
                "cheskepdia.sqlite",
                f"SELECT check_in FROM bookings WHERE user_email = {EMAIL} AND ({GREENWICH})",
            ),
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "Moves nyc_hotel_confirmation; flight conf + check_in held in D.",
        },
        do_not_touch="dinoco NYC confirmation; greenwich check_in",
        moves=["nyc_hotel_confirmation"],
        holds_this_I=["nyc_flight_confirmation", "nyc_checkin_date"],
    )

    # --- retrieval-f010: move Montego Bay total; hold host_name ---
    fill(
        by_id["retrieval-f010"],
        db="cheskepdia.sqlite",
        probe=(
            f"SELECT id, property_name, total_price, host_name FROM bookings "
            f"WHERE user_email = {EMAIL} AND ({MONTEGO_BAY_STAY})"
        ),
        patch=[
            f"UPDATE bookings SET total_price = total_price * 1.25 "
            f"WHERE user_email = {EMAIL} AND ({MONTEGO_BAY_STAY})"
        ],
        extra_probes=[
            ep(
                "cheskepdia.sqlite",
                f"SELECT host_name FROM bookings WHERE user_email = {EMAIL} AND ({MONTEGO_BAY_STAY})",
            )
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "Moves jamaica_trip_total; host_name held.",
        },
        do_not_touch="host_name; amenities",
        moves=["jamaica_trip_total"],
        holds_this_I=["host_name"],
    )

    # Leave Tier 3 skeletons untouched (still PENDING_GUEST_SCHEMA).
    tier3 = [
        "aggregation-f037",
        "contradiction-f024",
        "preference_inference-f010",
        "situated_action-f029",
    ]
    for tid in tier3:
        e = by_id[tid]
        assert e.get("_sql_status") == "PENDING_GUEST_SCHEMA", tid
        e["_inventory_tier"] = 3
        e["_sql_note"] = (
            (e.get("_sql_note") or "")
            + " Deferred: inventory Tier 3 / likely reject — fill after Tier 2 gate."
        ).strip()

    PATH.write_text(json.dumps(doc, indent=2) + "\n")
    ready = [
        e["id"]
        for e in doc["interventions"]
        if e.get("_sql_status") == "READY_RELATIVE" and e.get("_inventory_tier") == 2
    ]
    print(f"wrote {PATH}")
    print(f"Tier 2 READY_RELATIVE ({len(ready)}):", " ".join(sorted(ready)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
