#!/usr/bin/env python3
"""Wave A gold-lock: slate-12, pre-inject guest only.

Does not read probe_after, gold_moved, agent traces, or STS.
Does not call a model. Does not boot a guest.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out" / "p3_cohort_probe"
EMAIL = "michael.scott@dundermifflin.com"

SLATE12 = [
    "aggregation-f004",
    "aggregation-f036",
    "aggregation-f040",
    "contradiction-f003",
    "contradiction-f011",
    "contradiction-f014",
    "contradiction-f017",
    "contradiction-f022",
    "counterfactual-f001",
    "counterfactual-f002",
    "counterfactual-f003",
    "retrieval-f005",
]

# Declared before this script scores. Paths are pre-inject only.
DECLARED = {
    "aggregation-f004": [
        {"id": "philly_hotel_total", "kind": "money_usd", "path": "probe_before.0.total_price"},
        {"id": "philly_card_incidentals", "kind": "money_usd", "path": "extra_probes.0.result.0.incidentals"},
    ],
    "aggregation-f036": [
        {"id": "improv_spend_last_full_year", "kind": "money_usd", "path": "probe_before.0.improv_spend"},
    ],
    "aggregation-f040": [
        {"id": "billpay_monthly_subtotal", "kind": "money_usd", "path": "probe_before.sum.amount"},
        {"id": "improv_recurring_amount", "kind": "money_usd", "path": "extra_probes.0.result.0.improv"},
    ],
    "contradiction-f003": [
        {"id": "loyalty_tier", "kind": "categorical", "path": "probe_before.0.status"},
        {"id": "loyalty_miles", "kind": "integer", "path": "probe_before.0.miles"},
    ],
    "contradiction-f011": [
        {"id": "claimed_charitable_2025", "kind": "money_usd", "path": "probe_before.unique.field_value"},
        {"id": "gringotts_donation_sum_2025", "kind": "money_usd", "path": "extra_probes.0.result.0.don"},
    ],
    "contradiction-f014": [
        {"id": "w2_gross_wages", "kind": "money_usd", "path": "probe_before.0.field_value"},
        {"id": "claimed_salary_dm", "kind": "money_usd", "path": "UNDECLARED_NO_PREINJECT_PROBE"},
    ],
    "contradiction-f017": [
        {"id": "largest_gringotts_spend", "kind": "money_usd", "path": "probe_before.0.amount"},
        {"id": "largest_batbucks_buy", "kind": "integer", "path": "extra_probes.0.result.0.shares"},
    ],
    "contradiction-f022": [
        {"id": "zelle_sent_ytd", "kind": "money_usd", "path": "probe_before.0.zelle_ytd"},
        {"id": "speedtax_charitable", "kind": "money_usd", "path": "extra_probes.0.unique.field_value"},
    ],
    "counterfactual-f001": [
        {"id": "jamaica_hotel_total", "kind": "money_usd", "path": "probe_before.0.total_price"},
        {"id": "jamaica_flight_cost", "kind": "money_usd", "path": "extra_probes.0.result.0.fare_paid"},
    ],
    "counterfactual-f002": [
        {"id": "liquid_cash", "kind": "money_usd", "path": "probe_before.sum.balance"},
        {"id": "hotel_settle", "kind": "money_usd", "path": "extra_probes.0.result.0.total_price"},
    ],
    "counterfactual-f003": [
        {"id": "credit_headroom", "kind": "money_usd", "path": "probe_before.0.headroom"},
        {"id": "venue_planned", "kind": "categorical", "path": "files_before.Dundies_2026_Categories.txt.venue_line"},
    ],
    "retrieval-f005": [
        {"id": "designated_payee_amount", "kind": "money_usd", "path": "probe_before.0.amount"},
        {"id": "monthly_recurring_total", "kind": "money_usd", "path": "UNDECLARED_NO_PREINJECT_PROBE"},
    ],
}

GUEST = {
    "aggregation-f004": ROOT / "results/paper2_tier1_probe/aggregation-f004/aggregation-f004.guest.json",
    "aggregation-f036": ROOT / "results/paper2_tier1_probe/aggregation-f036/aggregation-f036.guest.json",
    "aggregation-f040": ROOT / "results/paper2_tier1_probe/aggregation-f040/aggregation-f040.guest.json",
    "contradiction-f003": ROOT / "results/paper2_tier1_probe/contradiction-f003/contradiction-f003.guest.json",
    "contradiction-f011": ROOT / "results/paper2_tier1_probe/contradiction-f011/contradiction-f011.guest.json",
    "contradiction-f014": ROOT / "results/paper2_tier2_probe/contradiction-f014/contradiction-f014.guest.json",
    "contradiction-f017": ROOT / "results/paper2_tier1_probe/contradiction-f017/contradiction-f017.guest.json",
    "contradiction-f022": ROOT / "results/paper2_tier1_probe/contradiction-f022/contradiction-f022.guest.json",
    "counterfactual-f001": ROOT / "results/paper2_tier2_probe/counterfactual-f001/counterfactual-f001.guest.json",
    "counterfactual-f002": ROOT / "results/paper2_tier1_probe/counterfactual-f002/counterfactual-f002.guest.json",
    "counterfactual-f003": ROOT / "results/paper2_tier1_probe/counterfactual-f003/counterfactual-f003.guest.json",
    "retrieval-f005": ROOT / "results/paper2_tier1_probe/retrieval-f005/retrieval-f005.guest.json",
}
F003_FILE = ROOT / "results/paper2_f003_i2_probe/counterfactual-f003-I2.guest.json"


def parse_jsonish(value):
    if value is None or value == "":
        return None
    if isinstance(value, (list, dict)):
        return value
    text = str(value).strip()
    if not text:
        return None
    if text.startswith("ERROR"):
        return {"_error": text}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"_error": text}


def unique_field(rows, field):
    if not isinstance(rows, list) or not rows:
        return None, "empty"
    vals = [r.get(field) for r in rows if isinstance(r, dict)]
    if not vals:
        return None, "no-field"
    if any(v is None or v == "" for v in vals):
        return None, "null-member"
    norm = [str(v).strip() for v in vals]
    if len(set(norm)) != 1:
        return None, f"not-unique:{sorted(set(norm))[:4]}"
    return vals[0], "unique"


def resolve(guest: dict, path: str):
    if path.startswith("UNDECLARED"):
        return None, "no pre-inject probe declared for this determining component"
    if path == "files_before.Dundies_2026_Categories.txt.venue_line":
        files = guest.get("files_before") or {}
        text = ""
        for k, v in files.items():
            if "Dundies_2026_Categories" in str(k):
                text = v if isinstance(v, str) else ""
                break
        if not text:
            return None, "files_before missing Dundies categories"
        m = re.search(r"^VENUE:\s*(.+)$", text, re.M)
        if not m:
            return None, "no VENUE line"
        return m.group(1).strip(), "ok"
    extras = guest.get("extra_probes_before") or []

    def extra(i):
        if i >= len(extras) or not isinstance(extras[i], dict):
            return {"_error": "missing extra"}
        return parse_jsonish(extras[i].get("result"))

    if path.startswith("extra_probes."):
        rest = path[len("extra_probes.") :]
        i_s, _, tail = rest.partition(".")
        i = int(i_s)
        blob = extra(i)
        if isinstance(blob, dict) and "_error" in blob:
            return None, blob["_error"]
        if tail.startswith("result."):
            path = "probe_before." + tail[len("result.") :]
        elif tail.startswith("unique."):
            path = "probe_before." + tail
        else:
            path = tail
        guest = {"probe_before": blob}

    pb = parse_jsonish(guest.get("probe_before"))
    if isinstance(pb, dict) and "_error" in pb:
        return None, pb["_error"]
    if path.startswith("probe_before.unique."):
        field = path.split(".")[-1]
        val, why = unique_field(pb, field)
        return (val, why) if val is not None else (None, why)
    if path.startswith("extra_probes.0.unique.") or ".unique." in path:
        field = path.split(".")[-1]
        val, why = unique_field(pb, field)
        return (val, why) if val is not None else (None, why)
    if path.startswith("probe_before.sum."):
        field = path.split(".")[-1]
        if not isinstance(pb, list) or not pb:
            return None, "empty-for-sum"
        try:
            return sum(float(r[field]) for r in pb), "ok"
        except (KeyError, TypeError, ValueError) as e:
            return None, f"sum-fail:{e}"
    if path.startswith("probe_before.0."):
        field = path.split(".")[-1]
        if not isinstance(pb, list) or len(pb) != 1:
            n = len(pb) if isinstance(pb, list) else 0
            return None, f"want-1-row got {n}"
        if field not in pb[0]:
            return None, f"missing-field:{field}"
        val = pb[0][field]
        if val is None or val == "":
            return None, "null"
        return val, "ok"
    return None, f"unhandled-path:{path}"


def load_guest(tid: str) -> dict:
    g = json.loads(GUEST[tid].read_text())
    # Strip after-state so a later reader of this object cannot score movement.
    for k in ("probe_after", "extra_probes_after", "files_after", "gold_moved", "applied_sql", "patch"):
        g.pop(k, None)
    if tid == "counterfactual-f003" and F003_FILE.exists():
        other = json.loads(F003_FILE.read_text())
        fb = other.get("files_before") or {}
        g["files_before"] = fb
    g["extra_probes_before"] = g.get("extra_probes_before") or []
    return g


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for tid in SLATE12:
        comps = []
        ok_all = True
        guest = load_guest(tid)
        for spec in DECLARED[tid]:
            val, why = resolve(guest, spec["path"])
            locked = val is not None
            if not locked:
                ok_all = False
            comps.append(
                {
                    "id": spec["id"],
                    "kind": spec["kind"],
                    "path": spec["path"],
                    "locked": locked,
                    "reason": why,
                    "value_repr": None if not locked else (str(val)[:80]),
                }
            )
        rows.append(
            {
                "id": tid,
                "wave": "A",
                "survive": ok_all,
                "components": comps,
                "models": ["flash", "gpt"],
            }
        )
    n_yes = sum(1 for r in rows if r["survive"])
    doc = {
        "protocol": "P3_COHORT_PROBE_PROTOCOL.md",
        "wave": "A",
        "n_scored": len(rows),
        "n_survive": n_yes,
        "n_fail": len(rows) - n_yes,
        "note": "Wave B (16) not scored. Gate closed only after both waves.",
        "rows": rows,
    }
    (OUT / "wave_a.json").write_text(json.dumps(doc, indent=2) + "\n")
    lines = [
        "# Wave A — slate 12 gold-lock (pre-inject only)",
        "",
        f"Survivors: **{n_yes}/12**. Wave B (16) pending. Gate not closed.",
        "",
        "| id | survive | unlocked |",
        "|---|---|---|",
    ]
    for r in rows:
        bad = ", ".join(c["id"] for c in r["components"] if not c["locked"]) or "—"
        lines.append(f"| `{r['id']}` | {'YES' if r['survive'] else 'NO'} | {bad} |")
    lines.append("")
    lines.append("Failed determining components are not rewritten. No replacements.")
    (OUT / "wave_a.md").write_text("\n".join(lines) + "\n")
    print(f"Wave A {n_yes}/12 survive. wrote {OUT / 'wave_a.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
