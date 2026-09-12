#!/usr/bin/env python3
"""Emit params_c.json. Data table only. generate_c.py has no per-id branch."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def csv(path, columns, rows):
    return {"path": path, "format": "csv", "columns": columns, "rows": rows}


def kv(path, rows):
    return {"path": path, "format": "kv", "rows": rows}


def ics(path, rows):
    return {"path": path, "format": "ics", "rows": rows}


def html(path, columns, rows):
    return {"path": path, "format": "html", "columns": columns, "rows": rows}


def loc_join(left, right, key, field, where=None, op="select_join"):
    return {
        "op": op,
        "left": left,
        "right": right,
        "key": key,
        "field": field,
        "left_where": where or [],
    }


def join3(left, mid, right, key, field, where=None):
    return {
        "op": "select_join3",
        "left": left,
        "mid": mid,
        "right": right,
        "key": key,
        "field": field,
        "left_where": where or [],
    }


P: dict = {}

P["C01"] = {
    "family": "Locate",
    "kind": "money_usd",
    "slot": "C1-intended",
    "component_id": "ridge_tarn_fee",
    "instruction": "Report the ridge tarn fee posted on the bothy grit sheet.",
    "anchors": ["ridge tarn fee"],
    "locator": loc_join(
        "Finance/bothy_grit.csv",
        "Mail/ridge_note.eml",
        "sku",
        "amount",
        [{"col": "sku", "eq": "tarn-ridge"}],
    ),
    "files": [
        csv(
            "Finance/bothy_grit.csv",
            ["sku", "amount"],
            [
                {"sku": "tarn-ridge", "amount": "71.30"},
                {"sku": "fell-glen", "amount": "18.40"},
                {"sku": "wold-tor", "amount": "9.55"},
                {"sku": "beck-crag", "amount": "22.10"},
            ],
        ),
        kv("Mail/ridge_note.eml", [{"sku": "tarn-ridge", "listed": "yes"}]),
    ],
}

P["C02"] = {
    "family": "Locate",
    "kind": "money_usd",
    "slot": "C2-intended",
    "component_id": "scree_fell_due",
    "instruction": "Report the scree fell due on the glen peat sheet.",
    "anchors": ["scree fell due"],
    "locator": loc_join(
        "Finance/glen_peat.csv",
        "Mail/scree_quote.eml",
        "sku",
        "amount",
        [{"col": "sku", "eq": "fell-scree"}],
    ),
    "files": [
        csv(
            "Finance/glen_peat.csv",
            ["sku", "amount"],
            [
                {"sku": "fell-scree", "amount": "53.80"},
                {"sku": "ridge-tor", "amount": "14.20"},
                {"sku": "bothy-kist", "amount": "6.75"},
                {"sku": "clough-grit", "amount": "31.00"},
            ],
        ),
        kv("Mail/scree_quote.eml", [{"sku": "fell-scree", "listed": "yes"}]),
        kv("Notes/posted_board.txt", [{"sku": "fell-scree", "amount": "90.00", "mark": "draft board"}]),
    ],
}

P["C03"] = {
    "family": "Locate",
    "kind": "entity",
    "slot": "C1-intended",
    "component_id": "bothy_skipper",
    "instruction": "Name the bothy skipper listed on the tarn crag card.",
    "anchors": ["bothy skipper"],
    "locator": loc_join("Notes/tarn_crag.txt", "Finance/bothy_roster.csv", "skipper", "skipper"),
    "files": [
        kv("Notes/tarn_crag.txt", [{"skipper": "Ivo Nair", "post": "bothy"}]),
        csv(
            "Finance/bothy_roster.csv",
            ["skipper", "post"],
            [
                {"skipper": "Ivo Nair", "post": "bothy"},
                {"skipper": "Lene Brack", "post": "fell"},
                {"skipper": "Corin Vale", "post": "glen"},
                {"skipper": "Maia Skell", "post": "tor"},
            ],
        ),
    ],
}

P["C04"] = {
    "family": "Locate",
    "kind": "categorical",
    "slot": "C2-intended",
    "component_id": "north_tor_wire",
    "instruction": "Give the wire status for the north tor dock slip.",
    "anchors": ["wire status"],
    "locator": loc_join(
        "Notes/north_tor.txt",
        "Calendar/tor_watch.ics",
        "location",
        "wire_status",
        [{"col": "location", "eq": "north-tor"}],
    ),
    "files": [
        kv("Notes/north_tor.txt", [{"location": "north-tor", "wire_status": "pale"}]),
        ics(
            "Calendar/tor_watch.ics",
            [
                {"summary": "watch", "location": "north-tor", "hours": "8"},
                {"summary": "spare", "location": "south-tor", "hours": "15"},
                {"summary": "open", "location": "east-tor", "hours": "11"},
                {"summary": "sealed", "location": "west-tor", "hours": "2"},
            ],
        ),
        kv("Notes/draft_wire.txt", [{"location": "north-tor", "wire_status": "dusk", "note": "board draft"}]),
    ],
}

P["C05"] = {
    "family": "Locate",
    "kind": "money_usd",
    "slot": "ordinary",
    "component_id": "bracken_howe_fee",
    "instruction": "Report the bracken howe fee on the kist clough sheet.",
    "anchors": ["bracken howe fee"],
    "locator": loc_join(
        "Finance/kist_clough.csv",
        "Mail/bracken_note.eml",
        "sku",
        "amount",
        [{"col": "sku", "eq": "howe-bracken"}],
    ),
    "files": [
        csv(
            "Finance/kist_clough.csv",
            ["sku", "amount"],
            [
                {"sku": "howe-bracken", "amount": "44.15"},
                {"sku": "grit-peat", "amount": "7.80"},
                {"sku": "ridge-glen", "amount": "19.25"},
                {"sku": "tarn-fell", "amount": "3.60"},
            ],
        ),
        kv("Mail/bracken_note.eml", [{"sku": "howe-bracken", "listed": "yes"}]),
    ],
}

P["C06"] = {
    "family": "Compute",
    "kind": "money_usd",
    "slot": "C1-intended",
    "component_id": "glen_crate_sum",
    "instruction": "Sum the glen wold crate costs that the bothy grit note lists.",
    "anchors": ["glen wold crate"],
    "locator": loc_join(
        "Finance/crate_wold.csv",
        "Notes/bothy_grit_list.txt",
        "sku",
        "amount",
        [{"col": "yard", "eq": "glen"}],
        op="sum_join",
    ),
    "files": [
        csv(
            "Finance/crate_wold.csv",
            ["sku", "yard", "amount"],
            [
                {"sku": "crate-a", "yard": "glen", "amount": "21.40"},
                {"sku": "crate-b", "yard": "glen", "amount": "17.85"},
                {"sku": "crate-c", "yard": "tor", "amount": "8.10"},
                {"sku": "crate-d", "yard": "fell", "amount": "12.00"},
            ],
        ),
        kv(
            "Notes/bothy_grit_list.txt",
            [{"sku": "crate-a", "listed": "yes"}, {"sku": "crate-b", "listed": "yes"}],
        ),
        html("Receipts/spare_costs.html", ["sku", "amount"], [{"sku": "crate-e", "amount": "15.90"}]),
    ],
}

P["C07"] = {
    "family": "Compute",
    "kind": "money_usd",
    "slot": "C2-intended",
    "component_id": "tor_crate_sum",
    "instruction": "Sum the tor beck crate costs that the ridge note lists.",
    "anchors": ["tor beck crate"],
    "locator": loc_join(
        "Finance/tor_crates.csv",
        "Notes/ridge_list.txt",
        "sku",
        "amount",
        [{"col": "yard", "eq": "tor"}],
        op="sum_join",
    ),
    "files": [
        csv(
            "Finance/tor_crates.csv",
            ["sku", "yard", "amount"],
            [
                {"sku": "t-a", "yard": "tor", "amount": "11.20"},
                {"sku": "t-b", "yard": "tor", "amount": "28.05"},
                {"sku": "t-c", "yard": "glen", "amount": "5.50"},
                {"sku": "t-d", "yard": "fell", "amount": "9.40"},
            ],
        ),
        kv("Notes/ridge_list.txt", [{"sku": "t-a", "listed": "yes"}, {"sku": "t-b", "listed": "yes"}]),
        kv("Notes/pre_sum.txt", [{"yard": "tor", "amount": "50.00", "note": "draft total"}]),
    ],
}

P["C08"] = {
    "family": "Compute",
    "kind": "integer",
    "slot": "C1-intended",
    "component_id": "crag_bin_sum",
    "instruction": "Sum the crag grit crate counts that the peat roster lists.",
    "anchors": ["crag grit crate"],
    "locator": loc_join(
        "Finance/crag_counts.csv",
        "Notes/peat_roster.txt",
        "sku",
        "qty",
        [{"col": "site", "eq": "crag"}],
        op="sum_join",
    ),
    "files": [
        csv(
            "Finance/crag_counts.csv",
            ["sku", "site", "qty"],
            [
                {"sku": "bin-a", "site": "crag", "qty": "7"},
                {"sku": "bin-b", "site": "crag", "qty": "9"},
                {"sku": "bin-c", "site": "glen", "qty": "2"},
                {"sku": "bin-d", "site": "tor", "qty": "4"},
            ],
        ),
        kv("Notes/peat_roster.txt", [{"sku": "bin-a", "listed": "yes"}, {"sku": "bin-b", "listed": "yes"}]),
        ics("Calendar/spare_bins.ics", [{"summary": "bin-e", "location": "fell", "hours": "11"}]),
    ],
}

P["C09"] = {
    "family": "Compute",
    "kind": "integer",
    "slot": "ordinary",
    "component_id": "kist_hours_sum",
    "instruction": "Sum the kist clough shift hours that the howe card lists.",
    "anchors": ["kist clough shift"],
    "locator": loc_join(
        "Finance/kist_hours.csv",
        "Notes/howe_card.txt",
        "shift",
        "hours",
        [{"col": "craft", "eq": "kist"}],
        op="sum_join",
    ),
    "files": [
        csv(
            "Finance/kist_hours.csv",
            ["shift", "craft", "hours"],
            [
                {"shift": "dawn", "craft": "kist", "hours": "4"},
                {"shift": "dusk", "craft": "kist", "hours": "9"},
                {"shift": "noon", "craft": "fell", "hours": "2"},
                {"shift": "late", "craft": "glen", "hours": "8"},
            ],
        ),
        kv("Notes/howe_card.txt", [{"shift": "dawn", "listed": "yes"}, {"shift": "dusk", "listed": "yes"}]),
        ics("Calendar/other_shifts.ics", [{"summary": "idle", "location": "tor", "hours": "11"}]),
    ],
}

P["C10"] = {
    "family": "Compute",
    "kind": "integer",
    "slot": "C2-intended",
    "component_id": "beck_qty_sum",
    "instruction": "Sum the beck peat crate counts that the grit roster lists.",
    "anchors": ["beck peat crate"],
    "locator": loc_join(
        "Finance/beck_counts.csv",
        "Notes/grit_roster.txt",
        "sku",
        "qty",
        [{"col": "site", "eq": "beck"}],
        op="sum_join",
    ),
    "files": [
        csv(
            "Finance/beck_counts.csv",
            ["sku", "site", "qty"],
            [
                {"sku": "p-a", "site": "beck", "qty": "5"},
                {"sku": "p-b", "site": "beck", "qty": "11"},
                {"sku": "p-c", "site": "tor", "qty": "3"},
                {"sku": "p-d", "site": "glen", "qty": "8"},
            ],
        ),
        kv("Notes/grit_roster.txt", [{"sku": "p-a", "listed": "yes"}, {"sku": "p-b", "listed": "yes"}]),
        kv("Notes/board_total.txt", [{"site": "beck", "qty": "20", "note": "draft count"}]),
    ],
}

P["C11"] = {
    "family": "Reconcile",
    "kind": "money_usd",
    "slot": "C1-intended",
    "component_id": "live_ridge_crate",
    "instruction": "Report the live ridge crate total from the finance sheet, not the mail quote.",
    "anchors": ["live ridge crate"],
    "locator": {
        "op": "live_not_stale",
        "left": "Finance/ridge_live.csv",
        "right": "Mail/ridge_quote.eml",
        "left_where": [{"col": "item", "eq": "ridge-crate"}],
        "right_where": [{"col": "item", "eq": "ridge-crate"}],
        "key": "item",
        "field": "amount",
    },
    "files": [
        csv(
            "Finance/ridge_live.csv",
            ["item", "amount"],
            [
                {"item": "ridge-crate", "amount": "48.70"},
                {"item": "tarn-bin", "amount": "10.20"},
                {"item": "fell-bin", "amount": "13.35"},
                {"item": "glen-bin", "amount": "22.40"},
            ],
        ),
        kv("Mail/ridge_quote.eml", [{"item": "ridge-crate", "amount": "31.00", "subject": "stale quote"}]),
    ],
}

P["C12"] = {
    "family": "Reconcile",
    "kind": "money_usd",
    "slot": "C2-intended",
    "component_id": "live_scree_peat",
    "instruction": "Report the live scree peat total from the finance sheet, not the mail quote.",
    "anchors": ["live scree peat"],
    "locator": {
        "op": "live_not_stale",
        "left": "Finance/scree_live.csv",
        "right": "Mail/scree_mail.eml",
        "left_where": [{"col": "item", "eq": "scree-peat"}],
        "right_where": [{"col": "item", "eq": "scree-peat"}],
        "key": "item",
        "field": "amount",
    },
    "files": [
        csv(
            "Finance/scree_live.csv",
            ["item", "amount"],
            [
                {"item": "scree-peat", "amount": "62.45"},
                {"item": "bothy-bin", "amount": "4.40"},
                {"item": "tor-bin", "amount": "14.25"},
                {"item": "peat-bin", "amount": "27.50"},
            ],
        ),
        kv("Mail/scree_mail.eml", [{"item": "scree-peat", "amount": "88.00", "subject": "posted quote"}]),
    ],
}

P["C13"] = {
    "family": "Reconcile",
    "kind": "entity",
    "slot": "C2-intended",
    "component_id": "live_glen_clerk",
    "instruction": "Name the live glen grit clerk from the roster sheet, not the mail copy.",
    "anchors": ["live glen grit"],
    "locator": {
        "op": "live_not_stale",
        "left": "Finance/clerk_live.csv",
        "right": "Mail/clerk_copy.eml",
        "left_where": [{"col": "post", "eq": "glen-grit"}],
        "right_where": [{"col": "post", "eq": "glen-grit"}],
        "key": "post",
        "field": "clerk",
    },
    "files": [
        csv(
            "Finance/clerk_live.csv",
            ["post", "clerk"],
            [
                {"post": "glen-grit", "clerk": "Rune Pell"},
                {"post": "tor-beck", "clerk": "Lene Brack"},
                {"post": "fell-crate", "clerk": "Corin Vale"},
                {"post": "tarn-fell", "clerk": "Ivo Nair"},
            ],
        ),
        kv("Mail/clerk_copy.eml", [{"post": "glen-grit", "clerk": "Maia Skell", "subject": "stale roster"}]),
    ],
}

P["C14"] = {
    "family": "Reconcile",
    "kind": "categorical",
    "slot": "C1-intended",
    "component_id": "live_kist_mark",
    "instruction": "Give the live kist peat mark from the yard card, not the mail mark.",
    "anchors": ["live kist peat"],
    "locator": {
        "op": "live_not_stale",
        "left": "Notes/yard_live.txt",
        "right": "Mail/yard_mark.eml",
        "left_where": [{"col": "bin", "eq": "kist-peat"}],
        "right_where": [{"col": "bin", "eq": "kist-peat"}],
        "key": "bin",
        "field": "mark",
    },
    "files": [
        kv(
            "Notes/yard_live.txt",
            [
                {"bin": "kist-peat", "mark": "keen"},
                {"bin": "tor-beck", "mark": "raw"},
                {"bin": "fell-glen", "mark": "still"},
                {"bin": "peat-fell", "mark": "dusk"},
            ],
        ),
        kv("Mail/yard_mark.eml", [{"bin": "kist-peat", "mark": "pale", "subject": "stale mark"}]),
    ],
}

P["C15"] = {
    "family": "Reconcile",
    "kind": "money_usd",
    "slot": "ordinary",
    "component_id": "live_bracken_bin",
    "instruction": "Report the live bracken bin total from the finance sheet, not the mail quote.",
    "anchors": ["live bracken bin"],
    "locator": {
        "op": "live_not_stale",
        "left": "Finance/bracken_live.csv",
        "right": "Mail/bracken_quote.eml",
        "left_where": [{"col": "item", "eq": "bracken-bin"}],
        "right_where": [{"col": "item", "eq": "bracken-bin"}],
        "key": "item",
        "field": "amount",
    },
    "files": [
        csv(
            "Finance/bracken_live.csv",
            ["item", "amount"],
            [
                {"item": "bracken-bin", "amount": "36.90"},
                {"item": "ridge-bin", "amount": "8.15"},
                {"item": "tarn-bin", "amount": "12.40"},
                {"item": "scree-bin", "amount": "5.05"},
            ],
        ),
        kv("Mail/bracken_quote.eml", [{"item": "bracken-bin", "amount": "20.00", "subject": "stale quote"}]),
    ],
}

P["C16"] = {
    "family": "Filter",
    "kind": "money_usd",
    "slot": "C1-intended",
    "component_id": "fell_rush_cost",
    "instruction": "Report the crate cost for the fell yard rush crate on the grit sheet.",
    "anchors": ["fell yard rush"],
    "locator": loc_join(
        "Finance/grit_sheet.csv",
        "Mail/rush_flag.eml",
        "sku",
        "amount",
        [{"col": "yard", "eq": "fell"}, {"col": "rush", "eq": "yes"}],
    ),
    "files": [
        csv(
            "Finance/grit_sheet.csv",
            ["sku", "yard", "rush", "amount"],
            [
                {"sku": "rush-a", "yard": "fell", "rush": "yes", "amount": "27.40"},
                {"sku": "rush-b", "yard": "fell", "rush": "no", "amount": "15.00"},
                {"sku": "rush-c", "yard": "glen", "rush": "yes", "amount": "18.20"},
                {"sku": "rush-d", "yard": "tor", "rush": "no", "amount": "44.05"},
                {"sku": "rush-e", "yard": "peat", "rush": "yes", "amount": "6.90"},
            ],
        ),
        kv("Mail/rush_flag.eml", [{"sku": "rush-a", "flag": "active"}]),
    ],
}

P["C17"] = {
    "family": "Filter",
    "kind": "money_usd",
    "slot": "C2-intended",
    "component_id": "glen_sealed_cost",
    "instruction": "Report the crate cost for the glen yard sealed crate on the peat sheet.",
    "anchors": ["glen yard sealed"],
    "locator": loc_join(
        "Finance/peat_sheet.csv",
        "Notes/sealed_index.txt",
        "sku",
        "amount",
        [{"col": "yard", "eq": "glen"}, {"col": "seal", "eq": "yes"}],
    ),
    "files": [
        csv(
            "Finance/peat_sheet.csv",
            ["sku", "yard", "seal", "amount"],
            [
                {"sku": "seal-a", "yard": "glen", "seal": "yes", "amount": "33.50"},
                {"sku": "seal-b", "yard": "glen", "seal": "no", "amount": "16.10"},
                {"sku": "seal-c", "yard": "fell", "seal": "yes", "amount": "22.05"},
                {"sku": "seal-d", "yard": "tor", "seal": "no", "amount": "9.70"},
                {"sku": "seal-e", "yard": "ridge", "seal": "yes", "amount": "31.40"},
            ],
        ),
        kv("Notes/sealed_index.txt", [{"sku": "seal-a", "listed": "yes"}]),
        kv("Notes/board_seal.txt", [{"sku": "seal-b", "amount": "99.00", "note": "posted unsealed"}]),
    ],
}

P["C18"] = {
    "family": "Filter",
    "kind": "entity",
    "slot": "ordinary",
    "component_id": "night_tarn_clerk",
    "instruction": "Name the night tarn clerk tagged on the bothy index.",
    "anchors": ["night tarn"],
    "locator": loc_join(
        "Notes/bothy_index.csv",
        "Mail/night_tag.eml",
        "tag",
        "clerk",
        [{"col": "tag", "eq": "night"}],
    ),
    "files": [
        csv(
            "Notes/bothy_index.csv",
            ["clerk", "tag"],
            [
                {"clerk": "Odas Wynn", "tag": "night"},
                {"clerk": "Ivo Nair", "tag": "day"},
                {"clerk": "Lene Brack", "tag": "day"},
                {"clerk": "Corin Vale", "tag": "day"},
            ],
        ),
        kv("Mail/night_tag.eml", [{"tag": "night", "active": "yes"}]),
    ],
}

P["C19"] = {
    "family": "Filter",
    "kind": "categorical",
    "slot": "ordinary",
    "component_id": "long_north_mark",
    "instruction": "Give the slip mark for the long north tor dock berth.",
    "anchors": ["north tor dock"],
    "locator": loc_join(
        "Finance/slip_marks.csv",
        "Calendar/berth_watch.ics",
        "summary",
        "mark",
        [{"col": "dock", "eq": "north"}, {"col": "length", "eq": "long"}],
    ),
    "files": [
        csv(
            "Finance/slip_marks.csv",
            ["summary", "dock", "length", "mark"],
            [
                {"summary": "n-long", "dock": "north", "length": "long", "mark": "still"},
                {"summary": "n-short", "dock": "north", "length": "short", "mark": "keen"},
                {"summary": "s-long", "dock": "south", "length": "long", "mark": "raw"},
                {"summary": "e-long", "dock": "east", "length": "long", "mark": "dusk"},
            ],
        ),
        ics(
            "Calendar/berth_watch.ics",
            [
                {"summary": "n-long", "location": "north", "hours": "8"},
                {"summary": "n-short", "location": "north", "hours": "15"},
            ],
        ),
    ],
}

P["C20"] = {
    "family": "Filter",
    "kind": "integer",
    "slot": "C1-intended",
    "component_id": "rush_hours",
    "instruction": "Report the shift hours for the rush fell watch on the clough card.",
    "anchors": ["rush fell watch"],
    "locator": loc_join(
        "Calendar/fell_watch.ics",
        "Notes/rush_list.txt",
        "summary",
        "hours",
        [{"col": "location", "eq": "fell"}],
    ),
    "files": [
        ics(
            "Calendar/fell_watch.ics",
            [
                {"summary": "rush-a", "location": "fell", "hours": "13"},
                {"summary": "idle-b", "location": "tor", "hours": "8"},
                {"summary": "open-c", "location": "glen", "hours": "15"},
                {"summary": "late-d", "location": "peat", "hours": "2"},
            ],
        ),
        kv("Notes/rush_list.txt", [{"summary": "rush-a", "listed": "yes"}]),
    ],
}

P["C21"] = {
    "family": "Tally",
    "kind": "integer",
    "slot": "C1-intended",
    "component_id": "glen_shift_count",
    "instruction": "Count the glen grit shifts on the calendar that also appear on the peat roster.",
    "anchors": ["glen grit shifts"],
    "locator": loc_join(
        "Calendar/glen_shifts.ics",
        "Notes/peat_names.txt",
        "summary",
        "summary",
        [{"col": "location", "eq": "glen"}],
        op="count_join",
    ),
    "files": [
        ics(
            "Calendar/glen_shifts.ics",
            [
                {"summary": "Ivo Nair", "location": "glen", "hours": "8"},
                {"summary": "Lene Brack", "location": "glen", "hours": "15"},
                {"summary": "Corin Vale", "location": "glen", "hours": "11"},
                {"summary": "Odas Wynn", "location": "glen", "hours": "9"},
                {"summary": "Nyla Pell", "location": "glen", "hours": "16"},
                {"summary": "Pia Vale", "location": "glen", "hours": "7"},
                {"summary": "Maia Skell", "location": "tor", "hours": "21"},
                {"summary": "Rune Pell", "location": "fell", "hours": "19"},
            ],
        ),
        kv(
            "Notes/peat_names.txt",
            [
                {"summary": "Ivo Nair", "listed": "yes"},
                {"summary": "Lene Brack", "listed": "yes"},
                {"summary": "Corin Vale", "listed": "yes"},
                {"summary": "Odas Wynn", "listed": "yes"},
                {"summary": "Nyla Pell", "listed": "yes"},
                {"summary": "Pia Vale", "listed": "yes"},
            ],
        ),
    ],
}

P["C22"] = {
    "family": "Tally",
    "kind": "integer",
    "slot": "C2-intended",
    "component_id": "rush_tarn_count",
    "instruction": "Count the rush tarn notes in the mail that also appear on the grit sheet.",
    "anchors": ["rush tarn notes"],
    "locator": loc_join(
        "Mail/tarn_notes.eml",
        "Finance/grit_mail.csv",
        "sku",
        "sku",
        [{"col": "rush", "eq": "yes"}],
        op="count_join",
    ),
    "files": [
        kv(
            "Mail/tarn_notes.eml",
            [
                {"sku": "tarn-a", "rush": "yes"},
                {"sku": "tarn-b", "rush": "yes"},
                {"sku": "tarn-c", "rush": "yes"},
                {"sku": "tarn-d", "rush": "yes"},
                {"sku": "tarn-e", "rush": "yes"},
                {"sku": "tarn-f", "rush": "yes"},
                {"sku": "tarn-g", "rush": "yes"},
                {"sku": "tarn-h", "rush": "no"},
            ],
        ),
        csv(
            "Finance/grit_mail.csv",
            ["sku", "bin"],
            [
                {"sku": "tarn-a", "bin": "8"},
                {"sku": "tarn-b", "bin": "15"},
                {"sku": "tarn-c", "bin": "11"},
                {"sku": "tarn-d", "bin": "16"},
                {"sku": "tarn-e", "bin": "19"},
                {"sku": "tarn-f", "bin": "7"},
                {"sku": "tarn-g", "bin": "9"},
                {"sku": "tarn-z", "bin": "21"},
            ],
        ),
        kv("Notes/board_count.txt", [{"note": "posted tally 18"}]),
    ],
}

P["C23"] = {
    "family": "Tally",
    "kind": "integer",
    "slot": "ordinary",
    "component_id": "bothy_peat_count",
    "instruction": "Count the bothy peat shifts on the calendar that also appear on the kist card.",
    "anchors": ["bothy peat shifts"],
    "locator": loc_join(
        "Calendar/bothy_shifts.ics",
        "Notes/kist_card.txt",
        "summary",
        "summary",
        [{"col": "location", "eq": "bothy"}],
        op="count_join",
    ),
    "files": [
        ics(
            "Calendar/bothy_shifts.ics",
            [
                {"summary": "dawn", "location": "bothy", "hours": "8"},
                {"summary": "dusk", "location": "bothy", "hours": "15"},
                {"summary": "noon", "location": "bothy", "hours": "11"},
                {"summary": "late", "location": "bothy", "hours": "16"},
                {"summary": "prime", "location": "bothy", "hours": "19"},
                {"summary": "vesper", "location": "bothy", "hours": "7"},
                {"summary": "watch", "location": "bothy", "hours": "9"},
                {"summary": "close", "location": "bothy", "hours": "21"},
                {"summary": "idle", "location": "tor", "hours": "18"},
            ],
        ),
        kv(
            "Notes/kist_card.txt",
            [
                {"summary": "dawn", "listed": "yes"},
                {"summary": "dusk", "listed": "yes"},
                {"summary": "noon", "listed": "yes"},
                {"summary": "late", "listed": "yes"},
                {"summary": "prime", "listed": "yes"},
                {"summary": "vesper", "listed": "yes"},
                {"summary": "watch", "listed": "yes"},
                {"summary": "close", "listed": "yes"},
            ],
        ),
    ],
}

P["C24"] = {
    "family": "Tally",
    "kind": "integer",
    "slot": "ordinary",
    "component_id": "fell_kist_count",
    "instruction": "Count the fell kist crates on the sheet that also appear on the howe note.",
    "anchors": ["fell kist crates"],
    "locator": loc_join(
        "Finance/kist_sheet.csv",
        "Notes/howe_note.txt",
        "sku",
        "sku",
        [{"col": "craft", "eq": "kist"}],
        op="count_join",
    ),
    "files": [
        csv(
            "Finance/kist_sheet.csv",
            ["sku", "craft", "bin"],
            [
                {"sku": "k-a", "craft": "kist", "bin": "8"},
                {"sku": "k-b", "craft": "kist", "bin": "15"},
                {"sku": "k-c", "craft": "kist", "bin": "11"},
                {"sku": "k-d", "craft": "kist", "bin": "16"},
                {"sku": "k-e", "craft": "kist", "bin": "19"},
                {"sku": "k-f", "craft": "kist", "bin": "7"},
                {"sku": "k-g", "craft": "kist", "bin": "9"},
                {"sku": "k-h", "craft": "kist", "bin": "21"},
                {"sku": "k-i", "craft": "kist", "bin": "18"},
                {"sku": "k-j", "craft": "fell", "bin": "6"},
            ],
        ),
        kv(
            "Notes/howe_note.txt",
            [
                {"sku": "k-a", "listed": "yes"},
                {"sku": "k-b", "listed": "yes"},
                {"sku": "k-c", "listed": "yes"},
                {"sku": "k-d", "listed": "yes"},
                {"sku": "k-e", "listed": "yes"},
                {"sku": "k-f", "listed": "yes"},
                {"sku": "k-g", "listed": "yes"},
                {"sku": "k-h", "listed": "yes"},
                {"sku": "k-i", "listed": "yes"},
            ],
        ),
    ],
}

P["C25"] = {
    "family": "Tally",
    "kind": "integer",
    "slot": "C2-intended",
    "component_id": "wold_mail_count",
    "instruction": "Count the wold grit notes in the mail that also appear on the clough sheet.",
    "anchors": ["wold grit notes"],
    "locator": loc_join(
        "Mail/wold_notes.eml",
        "Finance/clough_sheet.csv",
        "sku",
        "sku",
        [{"col": "rush", "eq": "yes"}],
        op="count_join",
    ),
    "files": [
        kv(
            "Mail/wold_notes.eml",
            [
                {"sku": "w-a", "rush": "yes"},
                {"sku": "w-b", "rush": "yes"},
                {"sku": "w-c", "rush": "yes"},
                {"sku": "w-d", "rush": "yes"},
                {"sku": "w-e", "rush": "yes"},
                {"sku": "w-f", "rush": "yes"},
                {"sku": "w-g", "rush": "no"},
            ],
        ),
        csv(
            "Finance/clough_sheet.csv",
            ["sku", "bin"],
            [
                {"sku": "w-a", "bin": "8"},
                {"sku": "w-b", "bin": "15"},
                {"sku": "w-c", "bin": "11"},
                {"sku": "w-d", "bin": "16"},
                {"sku": "w-e", "bin": "19"},
                {"sku": "w-f", "bin": "7"},
                {"sku": "w-z", "bin": "21"},
            ],
        ),
        kv("Notes/posted_n.txt", [{"n": "18", "note": "board tally"}]),
    ],
}

P["C26"] = {
    "family": "Multi-step",
    "kind": "entity",
    "slot": "C1-intended",
    "component_id": "triple_ridge_clerk",
    "instruction": "Name the ridge bothy clerk who appears on the grit sheet, the peat card, and the tarn tag.",
    "anchors": ["ridge bothy clerk"],
    "locator": join3(
        "Finance/grit_clerks.csv",
        "Notes/peat_card.txt",
        "Mail/tarn_tag.eml",
        "clerk",
        "clerk",
        [{"col": "post", "eq": "ridge"}],
    ),
    "files": [
        csv(
            "Finance/grit_clerks.csv",
            ["clerk", "post"],
            [
                {"clerk": "Sera Pell", "post": "ridge"},
                {"clerk": "Ivo Nair", "post": "glen"},
                {"clerk": "Lene Brack", "post": "tor"},
                {"clerk": "Corin Vale", "post": "fell"},
            ],
        ),
        kv("Notes/peat_card.txt", [{"clerk": "Sera Pell", "listed": "yes"}, {"clerk": "Ivo Nair", "listed": "yes"}]),
        kv("Mail/tarn_tag.eml", [{"clerk": "Sera Pell", "tag": "live"}]),
    ],
}

P["C27"] = {
    "family": "Multi-step",
    "kind": "entity",
    "slot": "C2-intended",
    "component_id": "triple_fell_hand",
    "instruction": "Name the fell grit hand who appears on the wold sheet, the clough card, and the howe tag.",
    "anchors": ["fell grit hand"],
    "locator": join3(
        "Finance/wold_hands.csv",
        "Notes/clough_card.txt",
        "Mail/howe_tag.eml",
        "hand",
        "hand",
        [{"col": "yard", "eq": "fell"}],
    ),
    "files": [
        csv(
            "Finance/wold_hands.csv",
            ["hand", "yard"],
            [
                {"hand": "Bram Kist", "yard": "fell"},
                {"hand": "Maia Skell", "yard": "glen"},
                {"hand": "Rune Pell", "yard": "tor"},
                {"hand": "Odas Wynn", "yard": "peat"},
            ],
        ),
        kv("Notes/clough_card.txt", [{"hand": "Bram Kist", "listed": "yes"}, {"hand": "Maia Skell", "listed": "yes"}]),
        kv("Mail/howe_tag.eml", [{"hand": "Bram Kist", "tag": "live"}]),
        kv("Notes/board_hand.txt", [{"hand": "Maia Skell", "note": "posted hand"}]),
    ],
}

P["C28"] = {
    "family": "Multi-step",
    "kind": "categorical",
    "slot": "ordinary",
    "component_id": "triple_tor_mark",
    "instruction": "Give the tor peat mark that appears on the kist sheet, the beck card, and the glen tag.",
    "anchors": ["tor peat mark"],
    "locator": join3(
        "Finance/kist_marks.csv",
        "Notes/beck_card.txt",
        "Mail/glen_tag.eml",
        "bin",
        "mark",
        [{"col": "bin", "eq": "tor-peat"}],
    ),
    "files": [
        csv(
            "Finance/kist_marks.csv",
            ["bin", "mark"],
            [
                {"bin": "tor-peat", "mark": "raw"},
                {"bin": "fell-glen", "mark": "keen"},
                {"bin": "ridge-tarn", "mark": "still"},
                {"bin": "scree-howe", "mark": "dusk"},
            ],
        ),
        kv("Notes/beck_card.txt", [{"bin": "tor-peat", "listed": "yes"}]),
        kv("Mail/glen_tag.eml", [{"bin": "tor-peat", "live": "yes"}]),
    ],
}

P["C29"] = {
    "family": "Multi-step",
    "kind": "money_usd",
    "slot": "ordinary",
    "component_id": "triple_clough_fee",
    "instruction": "Report the clough grit fee that appears on the live sheet, the peat index, and the bothy tag.",
    "anchors": ["clough grit fee"],
    "locator": join3(
        "Finance/clough_live.csv",
        "Notes/peat_index.txt",
        "Mail/bothy_tag.eml",
        "sku",
        "amount",
        [{"col": "sku", "eq": "clough-grit"}],
    ),
    "files": [
        csv(
            "Finance/clough_live.csv",
            ["sku", "amount"],
            [
                {"sku": "clough-grit", "amount": "19.85"},
                {"sku": "tor-bin", "amount": "6.40"},
                {"sku": "fell-bin", "amount": "11.20"},
                {"sku": "glen-bin", "amount": "8.05"},
            ],
        ),
        kv("Notes/peat_index.txt", [{"sku": "clough-grit", "listed": "yes"}]),
        kv("Mail/bothy_tag.eml", [{"sku": "clough-grit", "live": "yes"}]),
    ],
}

P["C30"] = {
    "family": "Multi-step",
    "kind": "money_usd",
    "slot": "ordinary",
    "component_id": "triple_howe_due",
    "instruction": "Report the howe bracken due that appears on the live sheet, the tarn index, and the scree tag.",
    "anchors": ["howe bracken due"],
    "locator": join3(
        "Finance/howe_live.csv",
        "Notes/tarn_index.txt",
        "Mail/scree_tag.eml",
        "sku",
        "amount",
        [{"col": "sku", "eq": "howe-bracken"}],
    ),
    "files": [
        csv(
            "Finance/howe_live.csv",
            ["sku", "amount"],
            [
                {"sku": "howe-bracken", "amount": "24.60"},
                {"sku": "kist-bin", "amount": "5.15"},
                {"sku": "peat-bin", "amount": "10.80"},
                {"sku": "ridge-bin", "amount": "7.35"},
            ],
        ),
        kv("Notes/tarn_index.txt", [{"sku": "howe-bracken", "listed": "yes"}]),
        kv("Mail/scree_tag.eml", [{"sku": "howe-bracken", "live": "yes"}]),
    ],
}


def main() -> None:
    ids = [f"C{i:02d}" for i in range(1, 31)]
    missing = [i for i in ids if i not in P]
    extra = [k for k in P if k not in ids]
    if missing or extra:
        raise SystemExit(f"id mismatch missing={missing} extra={extra}")
    ordered = {i: P[i] for i in ids}
    (ROOT / "params_c.json").write_text(json.dumps(ordered, indent=2) + "\n")
    print(f"wrote params_c.json n={len(ordered)}")


if __name__ == "__main__":
    main()
