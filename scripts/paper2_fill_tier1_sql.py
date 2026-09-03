"""Fill Tier 1 Paper 2 intervention SQL from schema columns (relative patches).

Does not invent G0/G1 literals. Uses SET col = col * k / + k so live probe
measures movement. 0-row UPDATE → gold_moved false → REJECT, not a D rewrite.

Venue I2 for counterfactual-f003 stays PENDING (Files, not sqlite).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "cf" / "paper2_interventions.json"
EMAIL = ":email"

# Shared WHERE fragments
IMPROV_DEBIT = (
    "lower(t.description) LIKE '%scranton improv workshop%' OR "
    "lower(t.description) LIKE '%scranton improv academy%'"
)
PHILLY_BOOKING = (
    "(lower(property_name) LIKE '%philadelphia%' OR lower(location) LIKE '%philadelphia%' "
    "OR lower(address) LIKE '%philadelphia%')"
)
JAMAICA_HOTEL = (
    "(lower(property_name) LIKE '%sandals%' AND (lower(location) LIKE '%jamaica%' "
    "OR lower(property_name) LIKE '%montego%'))"
)
BARBADOS_HOTEL = (
    "(lower(property_name) LIKE '%barbados%' OR lower(location) LIKE '%barbados%')"
)
CREDIT = "lower(type) LIKE '%credit%' AND ifnull(credit_limit,0) > 0"
CHECKING = "lower(type) LIKE '%check%'"
SAVINGS = "lower(type) LIKE '%sav%'"
CHARITY_TXN = (
    "(lower(t.description) LIKE '%donat%' OR lower(t.description) LIKE '%charit%' "
    "OR lower(ifnull(t.category,'')) LIKE '%charit%')"
)
BILL_NOT_CARD = "lower(ifnull(payee,'')) NOT LIKE '%credit card%' AND lower(ifnull(payee,'')) NOT LIKE '%sapphire%'"


def ep(db: str, sql: str) -> dict:
    return {"db": db, "sql": sql}


def fill(entry: dict, **kwargs) -> None:
    entry.update(kwargs)
    entry["role"] = "paper2_tier1"
    if entry.get("probe"):
        entry["_sql_status"] = "READY_RELATIVE"
    entry["_sql_note"] = (
        "Relative patch from schema columns; G0/G1 filled by live --probe-only. "
        "Zero-row UPDATE is identifiability reject, not a D rewrite."
    )


def main() -> int:
    doc = json.loads(PATH.read_text())
    by_id = {e["id"]: e for e in doc["interventions"]}

    # --- aggregation-f004: move hotel total; incidentals unmoved ---
    fill(
        by_id["aggregation-f004"],
        db="cheskepdia.sqlite",
        probe=(
            "SELECT id, property_name, location, check_in, total_price "
            f"FROM bookings WHERE user_email = {EMAIL} AND {PHILLY_BOOKING}"
        ),
        patch=[
            f"UPDATE bookings SET total_price = total_price + 250 "
            f"WHERE user_email = {EMAIL} AND {PHILLY_BOOKING}"
        ],
        extra_probes=[
            ep(
                "vaultbank.sqlite",
                "SELECT ifnull(sum(t.amount),0) AS incidentals FROM transactions t "
                "JOIN accounts a ON a.id = t.account_id "
                f"WHERE a.user_email = {EMAIL} AND t.date IN ("
                f"SELECT check_in FROM bookings WHERE user_email = {EMAIL} AND {PHILLY_BOOKING})"
            )
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "I1 moves philly_hotel_total only.",
        },
        do_not_touch="vaultbank transactions; other bookings",
        moves=["philly_hotel_total"],
        holds_this_I=["philly_card_incidentals"],
    )

    fill(
        by_id["aggregation-f020"],
        db="vaultbank.sqlite",
        probe=(
            f"SELECT id, type, name, balance, credit_limit FROM accounts "
            f"WHERE user_email = {EMAIL} AND {CREDIT}"
        ),
        patch=[
            f"UPDATE accounts SET balance = balance + 400 "
            f"WHERE user_email = {EMAIL} AND {CREDIT}"
        ],
        extra_probes=[
            ep("vaultbank.sqlite", f"SELECT credit_limit FROM accounts WHERE user_email = {EMAIL} AND {CREDIT}"),
            ep("batbucks.sqlite", f"SELECT cash FROM portfolio WHERE user_email = {EMAIL}"),
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "Moves card_balance; card_limit held; batbucks_cash unmoved determining.",
        },
        do_not_touch="credit_limit; batbucks cash",
        moves=["card_balance"],
        holds_this_I=["card_limit", "batbucks_cash"],
    )

    fill(
        by_id["aggregation-f036"],
        db="vaultbank.sqlite",
        probe=(
            "SELECT ifnull(sum(t.amount),0) AS improv_spend, count(*) AS n "
            "FROM transactions t JOIN accounts a ON a.id = t.account_id "
            f"WHERE a.user_email = {EMAIL} AND t.amount < 0 AND ({IMPROV_DEBIT}) "
            "AND strftime('%Y', t.date) = CAST(strftime('%Y','now','-1 year') AS TEXT)"
        ),
        patch=[
            "UPDATE transactions SET amount = amount * 1.4 WHERE id IN ("
            "SELECT t.id FROM transactions t JOIN accounts a ON a.id = t.account_id "
            f"WHERE a.user_email = {EMAIL} AND t.amount < 0 AND ({IMPROV_DEBIT}) "
            "AND strftime('%Y', t.date) = CAST(strftime('%Y','now','-1 year') AS TEXT))"
        ],
        extra_probes=[
            ep(
                "vaultbank.sqlite",
                "SELECT count(*) AS n FROM transactions t JOIN accounts a ON a.id = t.account_id "
                f"WHERE a.user_email = {EMAIL} AND t.amount < 0 AND ({IMPROV_DEBIT}) "
                "AND strftime('%Y', t.date) = CAST(strftime('%Y','now','-1 year') AS TEXT)",
            )
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "Scale amounts only; n_txn held. Calendar year = last full year via now-1 year.",
        },
        do_not_touch="row count of qualifying improv debits",
        moves=["improv_spend_last_full_year"],
        holds_this_I=["improv_txn_count_last_full_year"],
    )

    fill(
        by_id["aggregation-f040"],
        db="vaultbank.sqlite",
        probe=(
            f"SELECT id, payee, amount, frequency FROM bill_pay WHERE user_email = {EMAIL} "
            f"AND {BILL_NOT_CARD} ORDER BY payee"
        ),
        patch=[
            f"UPDATE bill_pay SET amount = amount * 1.25 WHERE user_email = {EMAIL} AND {BILL_NOT_CARD}"
        ],
        extra_probes=[
            ep(
                "vaultbank.sqlite",
                "SELECT ifnull(sum(t.amount),0) AS improv FROM transactions t "
                "JOIN accounts a ON a.id = t.account_id "
                f"WHERE a.user_email = {EMAIL} AND t.amount < 0 AND ({IMPROV_DEBIT})",
            )
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "I1 billpay_monthly_subtotal; improv unmoved.",
        },
        moves=["billpay_monthly_subtotal"],
        holds_this_I=["improv_recurring_amount"],
    )
    fill(
        by_id["aggregation-f040-I2"],
        db="vaultbank.sqlite",
        probe=(
            "SELECT ifnull(sum(t.amount),0) AS improv FROM transactions t "
            "JOIN accounts a ON a.id = t.account_id "
            f"WHERE a.user_email = {EMAIL} AND t.amount < 0 AND ({IMPROV_DEBIT})"
        ),
        patch=[
            "UPDATE transactions SET amount = amount * 1.5 WHERE id IN ("
            "SELECT t.id FROM transactions t JOIN accounts a ON a.id = t.account_id "
            f"WHERE a.user_email = {EMAIL} AND t.amount < 0 AND ({IMPROV_DEBIT}))"
        ],
        extra_probes=[
            ep(
                "vaultbank.sqlite",
                f"SELECT ifnull(sum(amount),0) AS billpay FROM bill_pay WHERE user_email = {EMAIL} AND {BILL_NOT_CARD}",
            )
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "I2 improv_recurring_amount; bill_pay unmoved.",
        },
        moves=["improv_recurring_amount"],
        holds_this_I=["billpay_monthly_subtotal"],
    )

    fill(
        by_id["contradiction-f003"],
        db="dinoco-airlines.sqlite",
        probe=f"SELECT status, miles, miles_ytd FROM loyalty WHERE user_email = {EMAIL}",
        patch=[
            f"UPDATE loyalty SET status = 'Silver Voyager', miles = miles / 2, miles_ytd = miles_ytd / 2 "
            f"WHERE user_email = {EMAIL}"
        ],
        extra_probes=[],
        expect={"probe_changes": True, "note": "Moves loyalty_tier + loyalty_miles (both determining)."},
        do_not_touch="flights itinerary",
        moves=["loyalty_tier", "loyalty_miles"],
        holds_this_I=[],
    )

    fill(
        by_id["contradiction-f004"],
        db="batbucks.sqlite",
        probe=f"SELECT ticker, shares, avg_cost FROM holdings WHERE user_email = {EMAIL} AND upper(ticker)='GME'",
        patch=[f"UPDATE holdings SET shares = shares + 40 WHERE user_email = {EMAIL} AND upper(ticker)='GME'"],
        extra_probes=[
            ep("batbucks.sqlite", f"SELECT avg_cost FROM holdings WHERE user_email = {EMAIL} AND upper(ticker)='GME'"),
            ep(
                "oddsmarket.sqlite",
                f"SELECT shares, status, market_ticker FROM positions WHERE user_email = {EMAIL} "
                "AND (upper(market_ticker) LIKE '%GME%' OR lower(title) LIKE '%gamestop%')",
            ),
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "Moves GME shares; avg_cost held; OM YES unmoved determining.",
        },
        do_not_touch="GME avg_cost; OddsMarket GME YES",
        moves=["batbucks_gme_shares"],
        holds_this_I=["gme_avg_cost", "oddsmarket_gme_yes"],
    )

    fill(
        by_id["contradiction-f006"],
        db="cheskepdia.sqlite",
        probe=f"SELECT id, property_name, total_price FROM bookings WHERE user_email = {EMAIL} AND {JAMAICA_HOTEL}",
        patch=[
            f"UPDATE bookings SET total_price = total_price + 500 WHERE user_email = {EMAIL} AND {JAMAICA_HOTEL}"
        ],
        extra_probes=[
            ep(
                "cheskepdia.sqlite",
                f"SELECT total_price FROM bookings WHERE user_email = {EMAIL} AND {BARBADOS_HOTEL}",
            ),
            ep(
                "vaultbank.sqlite",
                f"SELECT balance, credit_limit, (ifnull(credit_limit,0)-balance) AS headroom "
                f"FROM accounts WHERE user_email = {EMAIL} AND {CREDIT}",
            ),
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "I1 jamaica_hotel_total.",
        },
        moves=["jamaica_hotel_total"],
        holds_this_I=["barbados_hotel_total", "credit_headroom"],
    )
    fill(
        by_id["contradiction-f006-I2"],
        db="vaultbank.sqlite",
        probe=(
            f"SELECT balance, credit_limit, (ifnull(credit_limit,0)-balance) AS headroom "
            f"FROM accounts WHERE user_email = {EMAIL} AND {CREDIT}"
        ),
        patch=[f"UPDATE accounts SET balance = balance + 800 WHERE user_email = {EMAIL} AND {CREDIT}"],
        extra_probes=[
            ep(
                "cheskepdia.sqlite",
                f"SELECT property_name, total_price FROM bookings WHERE user_email = {EMAIL} "
                f"AND ({JAMAICA_HOTEL} OR {BARBADOS_HOTEL})",
            )
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "I2 credit_headroom via higher card balance; hotels unmoved.",
        },
        moves=["credit_headroom"],
        holds_this_I=["jamaica_hotel_total", "barbados_hotel_total"],
    )

    fill(
        by_id["contradiction-f011"],
        db="speedtax.sqlite",
        probe=(
            "SELECT d.field_name, d.field_value FROM tax_data d "
            "JOIN tax_returns tr ON tr.id = d.return_id "
            f"WHERE tr.user_email = {EMAIL} AND tr.tax_year = 2025 "
            "AND d.field_name IN ('charitable_contributions','charitable_total')"
        ),
        patch=[
            "UPDATE tax_data SET field_value = CAST(CAST(field_value AS REAL) + 400 AS TEXT) "
            "WHERE field_name IN ('charitable_contributions','charitable_total') AND return_id IN ("
            f"SELECT id FROM tax_returns WHERE user_email = {EMAIL} AND tax_year = 2025)"
        ],
        extra_probes=[
            ep(
                "vaultbank.sqlite",
                "SELECT ifnull(sum(t.amount),0) AS don FROM transactions t "
                "JOIN accounts a ON a.id = t.account_id "
                f"WHERE a.user_email = {EMAIL} AND strftime('%Y', t.date)='2025' AND {CHARITY_TXN}",
            )
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "I1 claimed_charitable_2025.",
        },
        moves=["claimed_charitable_2025"],
        holds_this_I=["gringotts_donation_sum_2025"],
    )
    fill(
        by_id["contradiction-f011-I2"],
        db="vaultbank.sqlite",
        probe=(
            "SELECT ifnull(sum(t.amount),0) AS don FROM transactions t "
            "JOIN accounts a ON a.id = t.account_id "
            f"WHERE a.user_email = {EMAIL} AND strftime('%Y', t.date)='2025' AND {CHARITY_TXN}"
        ),
        patch=[
            "UPDATE transactions SET amount = amount * 1.6 WHERE id IN ("
            "SELECT t.id FROM transactions t JOIN accounts a ON a.id = t.account_id "
            f"WHERE a.user_email = {EMAIL} AND strftime('%Y', t.date)='2025' AND {CHARITY_TXN})"
        ],
        extra_probes=[
            ep(
                "speedtax.sqlite",
                "SELECT d.field_value FROM tax_data d JOIN tax_returns tr ON tr.id = d.return_id "
                f"WHERE tr.user_email = {EMAIL} AND tr.tax_year = 2025 "
                "AND d.field_name IN ('charitable_contributions','charitable_total')",
            )
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "I2 donation ledger; SpeedTax claim unmoved.",
        },
        moves=["gringotts_donation_sum_2025"],
        holds_this_I=["claimed_charitable_2025"],
    )

    fill(
        by_id["contradiction-f017"],
        db="vaultbank.sqlite",
        probe=(
            "SELECT t.id, t.date, t.description, t.amount FROM transactions t "
            "JOIN accounts a ON a.id = t.account_id "
            f"WHERE a.user_email = {EMAIL} AND t.amount < 0 "
            "AND lower(t.description) NOT LIKE '%transfer%' "
            "AND lower(t.description) NOT LIKE '%payment%' "
            "ORDER BY t.amount ASC LIMIT 1"
        ),
        patch=[
            "UPDATE transactions SET amount = amount * 2 WHERE id = ("
            "SELECT t.id FROM transactions t JOIN accounts a ON a.id = t.account_id "
            f"WHERE a.user_email = {EMAIL} AND t.amount < 0 "
            "AND lower(t.description) NOT LIKE '%transfer%' "
            "AND lower(t.description) NOT LIKE '%payment%' "
            "ORDER BY t.amount ASC LIMIT 1)"
        ],
        extra_probes=[
            ep(
                "batbucks.sqlite",
                f"SELECT ticker, shares, side, status FROM orders "
                f"WHERE user_email = {EMAIL} AND lower(side) LIKE '%buy%' "
                "ORDER BY shares DESC LIMIT 1",
            )
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "Scale current max Gringotts debit; BatBucks max buy unmoved.",
        },
        moves=["largest_gringotts_spend"],
        holds_this_I=["largest_batbucks_buy"],
    )

    fill(
        by_id["contradiction-f022"],
        db="vaultbank.sqlite",
        probe=(
            f"SELECT ifnull(sum(amount),0) AS zelle_ytd FROM zelle_transfers "
            f"WHERE user_email = {EMAIL} AND lower(direction) LIKE '%sent%'"
        ),
        patch=[
            f"UPDATE zelle_transfers SET amount = amount * 1.3 "
            f"WHERE user_email = {EMAIL} AND lower(direction) LIKE '%sent%'"
        ],
        extra_probes=[
            ep(
                "speedtax.sqlite",
                "SELECT d.field_name, d.field_value FROM tax_data d "
                "JOIN tax_returns tr ON tr.id = d.return_id "
                f"WHERE tr.user_email = {EMAIL} AND d.field_name IN "
                "('charitable_contributions','charitable_total')",
            )
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "I1 zelle_sent_ytd; SpeedTax charitable unmoved.",
        },
        moves=["zelle_sent_ytd"],
        holds_this_I=["speedtax_charitable"],
    )

    fill(
        by_id["counterfactual-f002"],
        db="vaultbank.sqlite",
        probe=(
            f"SELECT type, name, balance FROM accounts WHERE user_email = {EMAIL} "
            f"AND ({CHECKING} OR {SAVINGS})"
        ),
        patch=[
            f"UPDATE accounts SET balance = balance * 0.5 WHERE user_email = {EMAIL} "
            f"AND ({CHECKING} OR {SAVINGS})"
        ],
        extra_probes=[
            ep(
                "cheskepdia.sqlite",
                f"SELECT total_price, property_name FROM bookings WHERE user_email = {EMAIL} "
                "AND lower(property_name) LIKE '%barbados%'",
            )
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "I1 liquid_cash.",
        },
        moves=["liquid_cash"],
        holds_this_I=["hotel_settle"],
    )
    fill(
        by_id["counterfactual-f002-I2"],
        db="cheskepdia.sqlite",
        probe=(
            f"SELECT id, property_name, total_price FROM bookings WHERE user_email = {EMAIL} "
            "AND lower(property_name) LIKE '%barbados%'"
        ),
        patch=[
            f"UPDATE bookings SET total_price = total_price + 700 WHERE user_email = {EMAIL} "
            "AND lower(property_name) LIKE '%barbados%'"
        ],
        extra_probes=[
            ep(
                "vaultbank.sqlite",
                f"SELECT ifnull(sum(balance),0) AS liquid FROM accounts WHERE user_email = {EMAIL} "
                f"AND ({CHECKING} OR {SAVINGS})",
            )
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "I2 hotel_settle.",
        },
        moves=["hotel_settle"],
        holds_this_I=["liquid_cash"],
    )

    fill(
        by_id["counterfactual-f003"],
        db="vaultbank.sqlite",
        probe=(
            f"SELECT balance, credit_limit, (ifnull(credit_limit,0)-balance) AS headroom "
            f"FROM accounts WHERE user_email = {EMAIL} AND {CREDIT}"
        ),
        patch=[f"UPDATE accounts SET credit_limit = credit_limit - 500 WHERE user_email = {EMAIL} AND {CREDIT}"],
        extra_probes=[],
        expect={"probe_changes": True, "note": "I1 credit_headroom. venue_planned is Files — I2 not sqlite."},
        moves=["credit_headroom"],
        holds_this_I=["venue_planned"],
    )
    # I2 stays pending
    by_id["counterfactual-f003-I2"]["_sql_status"] = "PENDING_FILE_BACKEND"
    by_id["counterfactual-f003-I2"]["_sql_note"] = (
        "venue_planned lives in Files/HooliMail (Dundies doc/thread), not a mapped sqlite field. "
        "Do not invent a sqlite stand-in. Probe on guest files or REJECT this variant."
    )
    by_id["counterfactual-f003-I2"]["moves"] = ["venue_planned"]
    by_id["counterfactual-f003-I2"]["holds_this_I"] = ["credit_headroom"]

    fill(
        by_id["counterfactual-f005"],
        db="batbucks.sqlite",
        probe=f"SELECT ticker, shares, avg_cost FROM holdings WHERE user_email = {EMAIL} AND upper(ticker)='GME'",
        patch=[f"UPDATE holdings SET shares = shares * 2 WHERE user_email = {EMAIL} AND upper(ticker)='GME'"],
        extra_probes=[
            ep("batbucks.sqlite", f"SELECT avg_cost FROM holdings WHERE user_email = {EMAIL} AND upper(ticker)='GME'"),
            ep(
                "vaultbank.sqlite",
                f"SELECT type, balance FROM accounts WHERE user_email = {EMAIL} AND {CHECKING}",
            ),
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "Moves gme_shares; avg_cost held; liquid_bank = checking unmoved this I.",
        },
        do_not_touch="GME avg_cost; checking balance",
        moves=["gme_shares"],
        holds_this_I=["gme_avg_cost", "liquid_bank"],
    )

    fill(
        by_id["counterfactual-f010"],
        db="vaultbank.sqlite",
        probe=(
            f"SELECT ifnull(sum(balance),0) AS liquid FROM accounts WHERE user_email = {EMAIL} "
            f"AND ({CHECKING} OR {SAVINGS})"
        ),
        patch=[
            f"UPDATE accounts SET balance = balance * 0.4 WHERE user_email = {EMAIL} "
            f"AND ({CHECKING} OR {SAVINGS})"
        ],
        extra_probes=[
            ep(
                "dinoco-airlines.sqlite",
                f"SELECT count(*) AS n_upcoming FROM flights WHERE user_email = {EMAIL} "
                "AND date(departure_date) >= date('now')",
            )
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "I1 liquid_cash; n_upcoming unmoved determining.",
        },
        moves=["liquid_cash"],
        holds_this_I=["n_upcoming_flights"],
    )

    fill(
        by_id["counterfactual-f013"],
        db="vaultbank.sqlite",
        probe=f"SELECT type, name, balance FROM accounts WHERE user_email = {EMAIL} AND {SAVINGS}",
        patch=[f"UPDATE accounts SET balance = balance * 0.2 WHERE user_email = {EMAIL} AND {SAVINGS}"],
        extra_probes=[
            ep("batbucks.sqlite", f"SELECT ifnull(sum(amount),0) AS divs FROM dividends WHERE user_email = {EMAIL}"),
            ep("oddsmarket.sqlite", f"SELECT balance FROM account WHERE user_email = {EMAIL}"),
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "I1 gringotts_savings only; do not merge buckets.",
        },
        moves=["gringotts_savings"],
        holds_this_I=["batbucks_dividends", "oddsmarket_balance"],
    )

    fill(
        by_id["retrieval-f002"],
        db="cheskepdia.sqlite",
        probe=(
            f"SELECT confirmation_code, property_name FROM bookings WHERE user_email = {EMAIL} "
            "AND lower(property_name) LIKE '%sandals%' AND (lower(location) LIKE '%jamaica%' "
            "OR lower(property_name) LIKE '%montego%')"
        ),
        patch=[
            f"UPDATE bookings SET confirmation_code = confirmation_code || '-CF' "
            f"WHERE user_email = {EMAIL} AND lower(property_name) LIKE '%sandals%' "
            "AND (lower(location) LIKE '%jamaica%' OR lower(property_name) LIKE '%montego%')"
        ],
        extra_probes=[],
        expect={"probe_changes": True, "note": "Moves confirmation string only."},
        moves=["sandals_jamaica_confirmation"],
        holds_this_I=[],
    )

    fill(
        by_id["retrieval-f005"],
        db="vaultbank.sqlite",
        probe=(
            f"SELECT id, payee, amount FROM bill_pay WHERE user_email = {EMAIL} "
            "AND lower(ifnull(frequency,'')) LIKE '%month%' ORDER BY payee LIMIT 1"
        ),
        patch=[
            f"UPDATE bill_pay SET amount = amount + 15 WHERE id = ("
            f"SELECT id FROM bill_pay WHERE user_email = {EMAIL} "
            "AND lower(ifnull(frequency,'')) LIKE '%month%' ORDER BY payee LIMIT 1)"
        ],
        extra_probes=[
            ep(
                "vaultbank.sqlite",
                f"SELECT count(*) AS n FROM bill_pay WHERE user_email = {EMAIL} "
                "AND lower(ifnull(frequency,'')) LIKE '%month%'",
            )
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "One payee amount; membership count held. monthly_recurring_total derived from list.",
        },
        moves=["designated_payee_amount", "monthly_recurring_total"],
        holds_this_I=["monthly_payee_membership"],
    )

    fill(
        by_id["retrieval-f017"],
        db="oddsmarket.sqlite",
        probe=f"SELECT total_invested, balance FROM account WHERE user_email = {EMAIL}",
        patch=[f"UPDATE account SET total_invested = total_invested * 1.5 WHERE user_email = {EMAIL}"],
        extra_probes=[
            ep(
                "oddsmarket.sqlite",
                f"SELECT count(*) AS n FROM positions WHERE user_email = {EMAIL} AND lower(status)='active'",
            )
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "I1 total_invested; n_open unmoved.",
        },
        moves=["total_invested"],
        holds_this_I=["n_open_positions"],
    )
    fill(
        by_id["retrieval-f017-I2"],
        db="oddsmarket.sqlite",
        probe=f"SELECT count(*) AS n FROM positions WHERE user_email = {EMAIL} AND lower(status)='active'",
        patch=[
            f"UPDATE positions SET status = 'settled' WHERE id = ("
            f"SELECT id FROM positions WHERE user_email = {EMAIL} AND lower(status)='active' "
            "ORDER BY id LIMIT 1)"
        ],
        extra_probes=[
            ep("oddsmarket.sqlite", f"SELECT total_invested FROM account WHERE user_email = {EMAIL}"),
        ],
        expect={
            "probe_changes": True,
            "extra_probes_must_not_change": True,
            "note": "I2 settle one open position; total_invested unmoved.",
        },
        moves=["n_open_positions"],
        holds_this_I=["total_invested"],
    )

    PATH.write_text(json.dumps(doc, indent=2) + "\n")
    ready = sum(1 for e in doc["interventions"] if e.get("_sql_status") == "READY_RELATIVE")
    pending = [e["id"] for e in doc["interventions"] if e.get("_sql_status") != "READY_RELATIVE"]
    print(f"READY_RELATIVE {ready}")
    print(f"not ready {len(pending)}")
    for i in pending:
        print(" ", i, by_id[i].get("_sql_status"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
