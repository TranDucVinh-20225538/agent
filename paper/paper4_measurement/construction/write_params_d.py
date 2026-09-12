#!/usr/bin/env python3
"""Emit params_d.json. Data table only. generate_d.py has no per-id branch.

P4-C2 Phase 1. No anchors. New dialect. Does not copy C/B ids or last-texts.
"""
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


def live(left, right, key, field, eq):
    return {
        "op": "live_not_stale",
        "left": left,
        "right": right,
        "left_where": [{"col": key, "eq": eq}],
        "right_where": [{"col": key, "eq": eq}],
        "key": key,
        "field": field,
    }


P: dict = {}

P["D01"] = {
    "family": "Locate",
    "kind": "money_usd",
    "slot": "C1-intended",
    "component_id": "folio_vellum_fee",
    "instruction": "Report the folio vellum fee posted on the quire rubric sheet.",
    "locator": loc_join(
        "Finance/quire_rubric.csv",
        "Mail/folio_note.eml",
        "sku",
        "amount",
        [{"col": "sku", "eq": "vellum-folio"}],
    ),
    "files": [
        csv(
            "Finance/quire_rubric.csv",
            ["sku", "amount"],
            [
                {"sku": "vellum-folio", "amount": "81.60"},
                {"sku": "codex-gilt", "amount": "18.45"},
                {"sku": "recto-verso", "amount": "9.35"},
                {"sku": "flyleaf-uncial", "amount": "22.70"},
            ],
        ),
        kv("Mail/folio_note.eml", [{"sku": "vellum-folio", "listed": "yes"}]),
    ],
}

P["D02"] = {
    "family": "Locate",
    "kind": "money_usd",
    "slot": "C2-intended",
    "component_id": "quire_recto_due",
    "instruction": "Report the quire recto due on the morocco gilt sheet.",
    "locator": loc_join(
        "Finance/morocco_gilt.csv",
        "Mail/quire_quote.eml",
        "sku",
        "amount",
        [{"col": "sku", "eq": "recto-quire"}],
    ),
    "files": [
        csv(
            "Finance/morocco_gilt.csv",
            ["sku", "amount"],
            [
                {"sku": "recto-quire", "amount": "46.75"},
                {"sku": "folio-codex", "amount": "14.80"},
                {"sku": "uncial-verso", "amount": "6.55"},
                {"sku": "colophon-rubric", "amount": "31.20"},
            ],
        ),
        kv("Mail/quire_quote.eml", [{"sku": "recto-quire", "listed": "yes"}]),
        kv("Notes/posted_board.txt", [{"sku": "recto-quire", "amount": "90.00", "mark": "draft board"}]),
    ],
}

P["D03"] = {
    "family": "Locate",
    "kind": "entity",
    "slot": "C1-intended",
    "component_id": "uncial_keeper",
    "instruction": "Name the uncial keeper listed on the flyleaf colophon card.",
    "locator": loc_join("Notes/flyleaf_colophon.txt", "Finance/uncial_roster.csv", "keeper", "keeper"),
    "files": [
        kv("Notes/flyleaf_colophon.txt", [{"keeper": "Tesfaye Holm", "post": "uncial"}]),
        csv(
            "Finance/uncial_roster.csv",
            ["keeper", "post"],
            [
                {"keeper": "Tesfaye Holm", "post": "uncial"},
                {"keeper": "Anouk Veld", "post": "recto"},
                {"keeper": "Ilaria Moss", "post": "verso"},
                {"keeper": "Joren Pike", "post": "quire"},
            ],
        ),
    ],
}

P["D04"] = {
    "family": "Locate",
    "kind": "categorical",
    "slot": "C2-intended",
    "component_id": "pressmark_bind",
    "instruction": "Give the bind status for the pressmark gathering slip.",
    "locator": loc_join(
        "Notes/pressmark_gathering.txt",
        "Calendar/gathering_watch.ics",
        "location",
        "bind_status",
        [{"col": "location", "eq": "pressmark-gathering"}],
    ),
    "files": [
        kv("Notes/pressmark_gathering.txt", [{"location": "pressmark-gathering", "bind_status": "foxed"}]),
        ics(
            "Calendar/gathering_watch.ics",
            [
                {"summary": "watch", "location": "pressmark-gathering", "hours": "8"},
                {"summary": "spare", "location": "recto-folio", "hours": "15"},
                {"summary": "open", "location": "verso-codex", "hours": "11"},
                {"summary": "sealed", "location": "quire-gilt", "hours": "19"},
            ],
        ),
        kv("Notes/draft_bind.txt", [{"location": "pressmark-gathering", "bind_status": "bound", "note": "board draft"}]),
    ],
}

P["D05"] = {
    "family": "Locate",
    "kind": "money_usd",
    "slot": "ordinary",
    "component_id": "morocco_gilt_fee",
    "instruction": "Report the morocco gilt fee on the palimpsest incunable sheet.",
    "locator": loc_join(
        "Finance/palimpsest_incunable.csv",
        "Mail/morocco_note.eml",
        "sku",
        "amount",
        [{"col": "sku", "eq": "gilt-morocco"}],
    ),
    "files": [
        csv(
            "Finance/palimpsest_incunable.csv",
            ["sku", "amount"],
            [
                {"sku": "gilt-morocco", "amount": "63.20"},
                {"sku": "rubric-codex", "amount": "7.15"},
                {"sku": "folio-quire", "amount": "19.40"},
                {"sku": "recto-flyleaf", "amount": "3.85"},
            ],
        ),
        kv("Mail/morocco_note.eml", [{"sku": "gilt-morocco", "listed": "yes"}]),
    ],
}

P["D06"] = {
    "family": "Compute",
    "kind": "money_usd",
    "slot": "C1-intended",
    "component_id": "folio_crate_sum",
    "instruction": "Sum the folio vellum crate costs that the quire rubric note lists.",
    "locator": loc_join(
        "Finance/crate_vellum.csv",
        "Notes/quire_rubric_list.txt",
        "sku",
        "amount",
        [{"col": "yard", "eq": "folio"}],
        op="sum_join",
    ),
    "files": [
        csv(
            "Finance/crate_vellum.csv",
            ["sku", "yard", "amount"],
            [
                {"sku": "crate-a", "yard": "folio", "amount": "31.40"},
                {"sku": "crate-b", "yard": "folio", "amount": "20.70"},
                {"sku": "crate-c", "yard": "recto", "amount": "8.15"},
                {"sku": "crate-d", "yard": "verso", "amount": "12.55"},
            ],
        ),
        kv(
            "Notes/quire_rubric_list.txt",
            [{"sku": "crate-a", "listed": "yes"}, {"sku": "crate-b", "listed": "yes"}],
        ),
        html("Receipts/spare_costs.html", ["sku", "amount"], [{"sku": "crate-e", "amount": "15.90"}]),
    ],
}

P["D07"] = {
    "family": "Compute",
    "kind": "money_usd",
    "slot": "C2-intended",
    "component_id": "recto_crate_sum",
    "instruction": "Sum the recto flyleaf crate costs that the colophon note lists.",
    "locator": loc_join(
        "Finance/recto_crates.csv",
        "Notes/colophon_list.txt",
        "sku",
        "amount",
        [{"col": "yard", "eq": "recto"}],
        op="sum_join",
    ),
    "files": [
        csv(
            "Finance/recto_crates.csv",
            ["sku", "yard", "amount"],
            [
                {"sku": "t-a", "yard": "recto", "amount": "15.55"},
                {"sku": "t-b", "yard": "recto", "amount": "22.80"},
                {"sku": "t-c", "yard": "folio", "amount": "5.50"},
                {"sku": "t-d", "yard": "verso", "amount": "9.65"},
            ],
        ),
        kv("Notes/colophon_list.txt", [{"sku": "t-a", "listed": "yes"}, {"sku": "t-b", "listed": "yes"}]),
        kv("Notes/pre_sum.txt", [{"yard": "recto", "amount": "50.00", "note": "draft total"}]),
    ],
}

P["D08"] = {
    "family": "Compute",
    "kind": "integer",
    "slot": "C1-intended",
    "component_id": "codex_bin_sum",
    "instruction": "Sum the codex rubric crate counts that the palimpsest roster lists.",
    "locator": loc_join(
        "Finance/codex_counts.csv",
        "Notes/palimpsest_roster.txt",
        "sku",
        "qty",
        [{"col": "site", "eq": "codex"}],
        op="sum_join",
    ),
    "files": [
        csv(
            "Finance/codex_counts.csv",
            ["sku", "site", "qty"],
            [
                {"sku": "bin-a", "site": "codex", "qty": "10"},
                {"sku": "bin-b", "site": "codex", "qty": "15"},
                {"sku": "bin-c", "site": "folio", "qty": "19"},
                {"sku": "bin-d", "site": "recto", "qty": "21"},
            ],
        ),
        kv("Notes/palimpsest_roster.txt", [{"sku": "bin-a", "listed": "yes"}, {"sku": "bin-b", "listed": "yes"}]),
        ics("Calendar/spare_bins.ics", [{"summary": "bin-e", "location": "verso", "hours": "11"}]),
    ],
}

P["D09"] = {
    "family": "Compute",
    "kind": "integer",
    "slot": "ordinary",
    "component_id": "quire_hours_sum",
    "instruction": "Sum the quire colophon shift hours that the morocco card lists.",
    "locator": loc_join(
        "Finance/quire_hours.csv",
        "Notes/morocco_card.txt",
        "shift",
        "hours",
        [{"col": "craft", "eq": "quire"}],
        op="sum_join",
    ),
    "files": [
        csv(
            "Finance/quire_hours.csv",
            ["shift", "craft", "hours"],
            [
                {"shift": "prime", "craft": "quire", "hours": "11"},
                {"shift": "sext", "craft": "quire", "hours": "17"},
                {"shift": "none", "craft": "verso", "hours": "19"},
                {"shift": "late", "craft": "folio", "hours": "8"},
            ],
        ),
        kv("Notes/morocco_card.txt", [{"shift": "prime", "listed": "yes"}, {"shift": "sext", "listed": "yes"}]),
        ics("Calendar/other_shifts.ics", [{"summary": "idle", "location": "recto", "hours": "21"}]),
    ],
}

P["D10"] = {
    "family": "Compute",
    "kind": "integer",
    "slot": "C2-intended",
    "component_id": "verso_qty_sum",
    "instruction": "Sum the verso palimpsest crate counts that the rubric roster lists.",
    "locator": loc_join(
        "Finance/verso_counts.csv",
        "Notes/rubric_roster.txt",
        "sku",
        "qty",
        [{"col": "site", "eq": "verso"}],
        op="sum_join",
    ),
    "files": [
        csv(
            "Finance/verso_counts.csv",
            ["sku", "site", "qty"],
            [
                {"sku": "p-a", "site": "verso", "qty": "9"},
                {"sku": "p-b", "site": "verso", "qty": "18"},
                {"sku": "p-c", "site": "recto", "qty": "16"},
                {"sku": "p-d", "site": "folio", "qty": "8"},
            ],
        ),
        kv("Notes/rubric_roster.txt", [{"sku": "p-a", "listed": "yes"}, {"sku": "p-b", "listed": "yes"}]),
        kv("Notes/board_total.txt", [{"site": "verso", "qty": "30", "note": "draft count"}]),
    ],
}

P["D11"] = {
    "family": "Reconcile",
    "kind": "money_usd",
    "slot": "C1-intended",
    "component_id": "live_folio_crate",
    "instruction": "Report the live folio crate total from the finance sheet, not the mail quote.",
    "locator": live("Finance/folio_live.csv", "Mail/folio_quote.eml", "item", "amount", "folio-crate"),
    "files": [
        csv(
            "Finance/folio_live.csv",
            ["item", "amount"],
            [
                {"item": "folio-crate", "amount": "68.40"},
                {"item": "recto-bin", "amount": "10.20"},
                {"item": "verso-bin", "amount": "13.75"},
                {"item": "quire-bin", "amount": "22.90"},
            ],
        ),
        kv("Mail/folio_quote.eml", [{"item": "folio-crate", "amount": "31.00", "subject": "stale quote"}]),
    ],
}

P["D12"] = {
    "family": "Reconcile",
    "kind": "money_usd",
    "slot": "C2-intended",
    "component_id": "live_quire_gilt",
    "instruction": "Report the live quire gilt total from the finance sheet, not the mail quote.",
    "locator": live("Finance/quire_live.csv", "Mail/quire_mail.eml", "item", "amount", "quire-gilt"),
    "files": [
        csv(
            "Finance/quire_live.csv",
            ["item", "amount"],
            [
                {"item": "quire-gilt", "amount": "41.25"},
                {"item": "codex-bin", "amount": "4.90"},
                {"item": "uncial-bin", "amount": "14.25"},
                {"item": "flyleaf-bin", "amount": "27.50"},
            ],
        ),
        kv("Mail/quire_mail.eml", [{"item": "quire-gilt", "amount": "88.00", "subject": "posted quote"}]),
    ],
}

P["D13"] = {
    "family": "Reconcile",
    "kind": "entity",
    "slot": "C2-intended",
    "component_id": "live_recto_clerk",
    "instruction": "Name the live recto rubric clerk from the roster sheet, not the mail copy.",
    "locator": live("Finance/clerk_live.csv", "Mail/clerk_copy.eml", "post", "clerk", "recto-rubric"),
    "files": [
        csv(
            "Finance/clerk_live.csv",
            ["post", "clerk"],
            [
                {"post": "recto-rubric", "clerk": "Anouk Veld"},
                {"post": "verso-codex", "clerk": "Ilaria Moss"},
                {"post": "folio-crate", "clerk": "Joren Pike"},
                {"post": "quire-gilt", "clerk": "Tesfaye Holm"},
            ],
        ),
        kv("Mail/clerk_copy.eml", [{"post": "recto-rubric", "clerk": "Mira Solt", "subject": "stale roster"}]),
    ],
}

P["D14"] = {
    "family": "Reconcile",
    "kind": "categorical",
    "slot": "C1-intended",
    "component_id": "live_incunable_mark",
    "instruction": "Give the live incunable palimpsest mark from the yard card, not the mail mark.",
    "locator": live("Notes/yard_live.txt", "Mail/yard_mark.eml", "bin", "mark", "incunable-palimpsest"),
    "files": [
        kv(
            "Notes/yard_live.txt",
            [
                {"bin": "incunable-palimpsest", "mark": "taut"},
                {"bin": "verso-codex", "mark": "slack"},
                {"bin": "folio-quire", "mark": "bound"},
                {"bin": "recto-gilt", "mark": "foxed"},
            ],
        ),
        kv("Mail/yard_mark.eml", [{"bin": "incunable-palimpsest", "mark": "slack", "subject": "stale mark"}]),
    ],
}

P["D15"] = {
    "family": "Reconcile",
    "kind": "money_usd",
    "slot": "ordinary",
    "component_id": "live_morocco_bin",
    "instruction": "Report the live morocco bin total from the finance sheet, not the mail quote.",
    "locator": live("Finance/morocco_live.csv", "Mail/morocco_quote.eml", "item", "amount", "morocco-bin"),
    "files": [
        csv(
            "Finance/morocco_live.csv",
            ["item", "amount"],
            [
                {"item": "morocco-bin", "amount": "37.55"},
                {"item": "folio-bin", "amount": "8.15"},
                {"item": "recto-bin", "amount": "12.40"},
                {"item": "quire-bin", "amount": "5.85"},
            ],
        ),
        kv("Mail/morocco_quote.eml", [{"item": "morocco-bin", "amount": "20.00", "subject": "stale quote"}]),
    ],
}

P["D16"] = {
    "family": "Filter",
    "kind": "money_usd",
    "slot": "C1-intended",
    "component_id": "verso_rush_cost",
    "instruction": "Report the crate cost for the verso yard rush crate on the rubric sheet.",
    "locator": loc_join(
        "Finance/rubric_sheet.csv",
        "Mail/rush_flag.eml",
        "sku",
        "amount",
        [{"col": "yard", "eq": "verso"}, {"col": "rush", "eq": "yes"}],
    ),
    "files": [
        csv(
            "Finance/rubric_sheet.csv",
            ["sku", "yard", "rush", "amount"],
            [
                {"sku": "rush-a", "yard": "verso", "rush": "yes", "amount": "55.15"},
                {"sku": "rush-b", "yard": "verso", "rush": "no", "amount": "15.00"},
                {"sku": "rush-c", "yard": "folio", "rush": "yes", "amount": "18.20"},
                {"sku": "rush-d", "yard": "recto", "rush": "no", "amount": "44.05"},
                {"sku": "rush-e", "yard": "quire", "rush": "yes", "amount": "6.90"},
            ],
        ),
        kv("Mail/rush_flag.eml", [{"sku": "rush-a", "flag": "active"}]),
    ],
}

P["D17"] = {
    "family": "Filter",
    "kind": "money_usd",
    "slot": "C2-intended",
    "component_id": "folio_sealed_cost",
    "instruction": "Report the crate cost for the folio yard sealed crate on the palimpsest sheet.",
    "locator": loc_join(
        "Finance/palimpsest_sheet.csv",
        "Notes/sealed_index.txt",
        "sku",
        "amount",
        [{"col": "yard", "eq": "folio"}, {"col": "seal", "eq": "yes"}],
    ),
    "files": [
        csv(
            "Finance/palimpsest_sheet.csv",
            ["sku", "yard", "seal", "amount"],
            [
                {"sku": "seal-a", "yard": "folio", "seal": "yes", "amount": "26.45"},
                {"sku": "seal-b", "yard": "folio", "seal": "no", "amount": "16.10"},
                {"sku": "seal-c", "yard": "verso", "seal": "yes", "amount": "22.05"},
                {"sku": "seal-d", "yard": "recto", "seal": "no", "amount": "9.65"},
                {"sku": "seal-e", "yard": "codex", "seal": "yes", "amount": "31.40"},
            ],
        ),
        kv("Notes/sealed_index.txt", [{"sku": "seal-a", "listed": "yes"}]),
        kv("Notes/board_seal.txt", [{"sku": "seal-b", "amount": "99.00", "note": "posted unsealed"}]),
    ],
}

P["D18"] = {
    "family": "Filter",
    "kind": "entity",
    "slot": "ordinary",
    "component_id": "night_uncial_clerk",
    "instruction": "Name the night uncial clerk tagged on the gathering index.",
    "locator": loc_join(
        "Notes/gathering_index.csv",
        "Mail/night_tag.eml",
        "tag",
        "clerk",
        [{"col": "tag", "eq": "night"}],
    ),
    "files": [
        csv(
            "Notes/gathering_index.csv",
            ["clerk", "tag"],
            [
                {"clerk": "Joren Pike", "tag": "night"},
                {"clerk": "Tesfaye Holm", "tag": "day"},
                {"clerk": "Anouk Veld", "tag": "day"},
                {"clerk": "Ilaria Moss", "tag": "day"},
            ],
        ),
        kv("Mail/night_tag.eml", [{"tag": "night", "active": "yes"}]),
    ],
}

P["D19"] = {
    "family": "Filter",
    "kind": "categorical",
    "slot": "ordinary",
    "component_id": "long_recto_mark",
    "instruction": "Give the slip mark for the long recto pressmark berth.",
    "locator": loc_join(
        "Finance/slip_marks.csv",
        "Calendar/berth_watch.ics",
        "summary",
        "mark",
        [{"col": "dock", "eq": "recto"}, {"col": "length", "eq": "long"}],
    ),
    "files": [
        csv(
            "Finance/slip_marks.csv",
            ["summary", "dock", "length", "mark"],
            [
                {"summary": "n-long", "dock": "recto", "length": "long", "mark": "bound"},
                {"summary": "n-short", "dock": "recto", "length": "short", "mark": "taut"},
                {"summary": "s-long", "dock": "verso", "length": "long", "mark": "slack"},
                {"summary": "e-long", "dock": "folio", "length": "long", "mark": "foxed"},
            ],
        ),
        ics(
            "Calendar/berth_watch.ics",
            [
                {"summary": "n-long", "location": "recto", "hours": "8"},
                {"summary": "n-short", "location": "recto", "hours": "15"},
            ],
        ),
    ],
}

P["D20"] = {
    "family": "Filter",
    "kind": "integer",
    "slot": "C1-intended",
    "component_id": "rush_hours",
    "instruction": "Report the shift hours for the rush verso watch on the colophon card.",
    "locator": loc_join(
        "Calendar/verso_watch.ics",
        "Notes/rush_list.txt",
        "summary",
        "hours",
        [{"col": "location", "eq": "verso"}],
    ),
    "files": [
        ics(
            "Calendar/verso_watch.ics",
            [
                {"summary": "rush-a", "location": "verso", "hours": "19"},
                {"summary": "idle-b", "location": "recto", "hours": "8"},
                {"summary": "open-c", "location": "folio", "hours": "15"},
                {"summary": "late-d", "location": "quire", "hours": "21"},
            ],
        ),
        kv("Notes/rush_list.txt", [{"summary": "rush-a", "listed": "yes"}]),
    ],
}

FOLIO_KEEPERS = [
    "Tesfaye Holm",
    "Anouk Veld",
    "Ilaria Moss",
    "Joren Pike",
    "Saskia Bel",
    "Oren Falk",
    "Mira Solt",
    "Pavel Orth",
    "Nila Ort",
    "Cadence Rue",
]

P["D21"] = {
    "family": "Tally",
    "kind": "integer",
    "slot": "C1-intended",
    "component_id": "folio_shift_count",
    "instruction": "Count the folio rubric shifts on the calendar that also appear on the palimpsest roster.",
    "locator": loc_join(
        "Calendar/folio_shifts.ics",
        "Notes/palimpsest_names.txt",
        "summary",
        "summary",
        [{"col": "location", "eq": "folio"}],
        op="count_join",
    ),
    "files": [
        ics(
            "Calendar/folio_shifts.ics",
            [
                *[{"summary": n, "location": "folio", "hours": h} for n, h in zip(FOLIO_KEEPERS, ["8", "15", "11", "9", "16", "7", "21", "19", "18", "23"])],
                {"summary": "Mael Quill", "location": "recto", "hours": "21"},
                {"summary": "Beren Ink", "location": "verso", "hours": "19"},
            ],
        ),
        kv("Notes/palimpsest_names.txt", [{"summary": n, "listed": "yes"} for n in FOLIO_KEEPERS]),
    ],
}

P["D22"] = {
    "family": "Tally",
    "kind": "integer",
    "slot": "C2-intended",
    "component_id": "rush_uncial_count",
    "instruction": "Count the rush uncial notes in the mail that also appear on the rubric sheet.",
    "locator": loc_join(
        "Mail/uncial_notes.eml",
        "Finance/rubric_mail.csv",
        "sku",
        "sku",
        [{"col": "rush", "eq": "yes"}],
        op="count_join",
    ),
    "files": [
        kv(
            "Mail/uncial_notes.eml",
            [{"sku": f"u-{i}", "rush": "yes"} for i in range(11)]
            + [{"sku": "u-11", "rush": "no"}],
        ),
        csv(
            "Finance/rubric_mail.csv",
            ["sku", "bin"],
            [{"sku": f"u-{i}", "bin": str(8 + i)} for i in range(11)]
            + [{"sku": "u-z", "bin": "21"}],
        ),
        kv("Notes/board_count.txt", [{"note": "posted tally 18"}]),
    ],
}

P["D23"] = {
    "family": "Tally",
    "kind": "integer",
    "slot": "ordinary",
    "component_id": "codex_palimpsest_count",
    "instruction": "Count the codex palimpsest shifts on the calendar that also appear on the quire card.",
    "locator": loc_join(
        "Calendar/codex_shifts.ics",
        "Notes/quire_card.txt",
        "summary",
        "summary",
        [{"col": "location", "eq": "codex"}],
        op="count_join",
    ),
    "files": [
        ics(
            "Calendar/codex_shifts.ics",
            [
                {"summary": s, "location": "codex", "hours": h}
                for s, h in [
                    ("prime", "8"),
                    ("terce", "15"),
                    ("sext", "11"),
                    ("none", "16"),
                    ("vesper", "19"),
                    ("compline", "7"),
                    ("matins", "9"),
                    ("lauds", "21"),
                    ("vigil", "18"),
                    ("nocturn", "23"),
                    ("chapter", "10"),
                    ("silence", "13"),
                    ("copy", "17"),
                    ("bind", "25"),
                    ("press", "27"),
                    ("idle", "18"),
                ]
            ]
            + [{"summary": "idle", "location": "recto", "hours": "18"}],
        ),
        kv(
            "Notes/quire_card.txt",
            [
                {"summary": s, "listed": "yes"}
                for s in [
                    "prime",
                    "terce",
                    "sext",
                    "none",
                    "vesper",
                    "compline",
                    "matins",
                    "lauds",
                    "vigil",
                    "nocturn",
                    "chapter",
                    "silence",
                    "copy",
                    "bind",
                    "press",
                ]
            ],
        ),
    ],
}

P["D24"] = {
    "family": "Tally",
    "kind": "integer",
    "slot": "ordinary",
    "component_id": "verso_quire_count",
    "instruction": "Count the verso quire crates on the sheet that also appear on the morocco note.",
    "locator": loc_join(
        "Finance/quire_sheet.csv",
        "Notes/morocco_note.txt",
        "sku",
        "sku",
        [{"col": "craft", "eq": "quire"}],
        op="count_join",
    ),
    "files": [
        csv(
            "Finance/quire_sheet.csv",
            ["sku", "craft", "bin"],
            [{"sku": f"k-{i}", "craft": "quire", "bin": str(8 + i)} for i in range(18)]
            + [{"sku": "k-x", "craft": "verso", "bin": "6"}],
        ),
        kv("Notes/morocco_note.txt", [{"sku": f"k-{i}", "listed": "yes"} for i in range(18)]),
    ],
}

P["D25"] = {
    "family": "Tally",
    "kind": "integer",
    "slot": "C2-intended",
    "component_id": "gilt_mail_count",
    "instruction": "Count the gilt rubric notes in the mail that also appear on the colophon sheet.",
    "locator": loc_join(
        "Mail/gilt_notes.eml",
        "Finance/colophon_sheet.csv",
        "sku",
        "sku",
        [{"col": "rush", "eq": "yes"}],
        op="count_join",
    ),
    "files": [
        kv(
            "Mail/gilt_notes.eml",
            [{"sku": f"g-{i}", "rush": "yes"} for i in range(20)]
            + [{"sku": "g-20", "rush": "no"}],
        ),
        csv(
            "Finance/colophon_sheet.csv",
            ["sku", "bin"],
            [{"sku": f"g-{i}", "bin": str(8 + (i % 12))} for i in range(20)]
            + [{"sku": "g-z", "bin": "21"}],
        ),
        kv("Notes/posted_n.txt", [{"n": "18", "note": "board tally"}]),
    ],
}

P["D26"] = {
    "family": "Multi-step",
    "kind": "entity",
    "slot": "C1-intended",
    "component_id": "triple_folio_clerk",
    "instruction": "Name the folio gathering clerk who appears on the rubric sheet, the palimpsest card, and the uncial tag.",
    "locator": join3(
        "Finance/rubric_clerks.csv",
        "Notes/palimpsest_card.txt",
        "Mail/uncial_tag.eml",
        "clerk",
        "clerk",
        [{"col": "post", "eq": "folio"}],
    ),
    "files": [
        csv(
            "Finance/rubric_clerks.csv",
            ["clerk", "post"],
            [
                {"clerk": "Saskia Bel", "post": "folio"},
                {"clerk": "Tesfaye Holm", "post": "recto"},
                {"clerk": "Anouk Veld", "post": "verso"},
                {"clerk": "Ilaria Moss", "post": "quire"},
            ],
        ),
        kv("Notes/palimpsest_card.txt", [{"clerk": "Saskia Bel", "listed": "yes"}, {"clerk": "Tesfaye Holm", "listed": "yes"}]),
        kv("Mail/uncial_tag.eml", [{"clerk": "Saskia Bel", "tag": "live"}]),
    ],
}

P["D27"] = {
    "family": "Multi-step",
    "kind": "entity",
    "slot": "C2-intended",
    "component_id": "triple_verso_hand",
    "instruction": "Name the verso rubric hand who appears on the gilt sheet, the colophon card, and the morocco tag.",
    "locator": join3(
        "Finance/gilt_hands.csv",
        "Notes/colophon_card.txt",
        "Mail/morocco_tag.eml",
        "hand",
        "hand",
        [{"col": "yard", "eq": "verso"}],
    ),
    "files": [
        csv(
            "Finance/gilt_hands.csv",
            ["hand", "yard"],
            [
                {"hand": "Oren Falk", "yard": "verso"},
                {"hand": "Mira Solt", "yard": "folio"},
                {"hand": "Pavel Orth", "yard": "recto"},
                {"hand": "Joren Pike", "yard": "quire"},
            ],
        ),
        kv("Notes/colophon_card.txt", [{"hand": "Oren Falk", "listed": "yes"}, {"hand": "Mira Solt", "listed": "yes"}]),
        kv("Mail/morocco_tag.eml", [{"hand": "Oren Falk", "tag": "live"}]),
        kv("Notes/board_hand.txt", [{"hand": "Mira Solt", "note": "posted hand"}]),
    ],
}

P["D28"] = {
    "family": "Multi-step",
    "kind": "categorical",
    "slot": "ordinary",
    "component_id": "triple_recto_mark",
    "instruction": "Give the recto palimpsest mark that appears on the quire sheet, the flyleaf card, and the folio tag.",
    "locator": join3(
        "Finance/quire_marks.csv",
        "Notes/flyleaf_card.txt",
        "Mail/folio_tag.eml",
        "bin",
        "mark",
        [{"col": "bin", "eq": "recto-palimpsest"}],
    ),
    "files": [
        csv(
            "Finance/quire_marks.csv",
            ["bin", "mark"],
            [
                {"bin": "recto-palimpsest", "mark": "slack"},
                {"bin": "verso-folio", "mark": "taut"},
                {"bin": "codex-uncial", "mark": "bound"},
                {"bin": "quire-gilt", "mark": "foxed"},
            ],
        ),
        kv("Notes/flyleaf_card.txt", [{"bin": "recto-palimpsest", "listed": "yes"}]),
        kv("Mail/folio_tag.eml", [{"bin": "recto-palimpsest", "live": "yes"}]),
    ],
}

P["D29"] = {
    "family": "Multi-step",
    "kind": "money_usd",
    "slot": "ordinary",
    "component_id": "triple_colophon_fee",
    "instruction": "Report the colophon rubric fee that appears on the live sheet, the palimpsest index, and the gathering tag.",
    "locator": join3(
        "Finance/colophon_live.csv",
        "Notes/palimpsest_index.txt",
        "Mail/gathering_tag.eml",
        "sku",
        "amount",
        [{"col": "sku", "eq": "colophon-rubric"}],
    ),
    "files": [
        csv(
            "Finance/colophon_live.csv",
            ["sku", "amount"],
            [
                {"sku": "colophon-rubric", "amount": "72.80"},
                {"sku": "recto-bin", "amount": "6.40"},
                {"sku": "verso-bin", "amount": "11.35"},
                {"sku": "folio-bin", "amount": "8.05"},
            ],
        ),
        kv("Notes/palimpsest_index.txt", [{"sku": "colophon-rubric", "listed": "yes"}]),
        kv("Mail/gathering_tag.eml", [{"sku": "colophon-rubric", "live": "yes"}]),
    ],
}

P["D30"] = {
    "family": "Multi-step",
    "kind": "money_usd",
    "slot": "ordinary",
    "component_id": "triple_morocco_due",
    "instruction": "Report the morocco incunable due that appears on the live sheet, the flyleaf index, and the quire tag.",
    "locator": join3(
        "Finance/morocco_due.csv",
        "Notes/flyleaf_index.txt",
        "Mail/quire_tag.eml",
        "sku",
        "amount",
        [{"col": "sku", "eq": "morocco-incunable"}],
    ),
    "files": [
        csv(
            "Finance/morocco_due.csv",
            ["sku", "amount"],
            [
                {"sku": "morocco-incunable", "amount": "29.15"},
                {"sku": "quire-bin", "amount": "5.15"},
                {"sku": "gilt-bin", "amount": "10.80"},
                {"sku": "folio-bin", "amount": "7.35"},
            ],
        ),
        kv("Notes/flyleaf_index.txt", [{"sku": "morocco-incunable", "listed": "yes"}]),
        kv("Mail/quire_tag.eml", [{"sku": "morocco-incunable", "live": "yes"}]),
    ],
}


def main() -> None:
    ids = [f"D{i:02d}" for i in range(1, 31)]
    missing = [i for i in ids if i not in P]
    extra = [k for k in P if k not in ids]
    if missing or extra:
        raise SystemExit(f"id mismatch missing={missing} extra={extra}")
    for cid, row in P.items():
        if "anchors" in row or "gold" in row or "observations" in row:
            raise SystemExit(f"{cid}: forbidden param field")
    (ROOT / "params_d.json").write_text(json.dumps({k: P[k] for k in ids}, indent=2) + "\n")
    print("wrote params_d.json", len(ids))


if __name__ == "__main__":
    main()
