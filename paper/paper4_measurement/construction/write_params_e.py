#!/usr/bin/env python3
"""Author params_e.json for P4-D E01–E30. $0. No agents. No scorer edits.

Expands 10 families × 3 conditions. Does not write worlds.
Does not modify P4-B / P4-C / P4-C2 objects.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "params_e.json"


def csv(path, columns, rows):
    return {"path": path, "format": "csv", "columns": columns, "rows": rows}


def kv(path, rows):
    return {"path": path, "format": "kv", "rows": rows}


def ics(path, rows):
    return {"path": path, "format": "ics", "rows": rows}


def listed(*skus, key="sku"):
    return [{key: s, "listed": "yes"} for s in skus]


def rush_rows(prefix, n_yes, n_no=3):
    rows = [{"sku": f"{prefix}-{i}", "rush": "yes"} for i in range(n_yes)]
    rows += [{"sku": f"{prefix}-n{i}", "rush": "no"} for i in range(n_no)]
    return rows


def sheet_rows(prefix, n, extra=2, bin0=8):
    rows = [{"sku": f"{prefix}-{i}", "bin": str(bin0 + (i % 7))} for i in range(n)]
    rows += [{"sku": f"{prefix}-z{i}", "bin": str(30 + i)} for i in range(extra)]
    return rows


def cluster(cid, family_id, family, kind, condition, component_id, instruction, locator, files, competitors):
    return {
        cid: {
            "family_id": family_id,
            "family": family,
            "kind": kind,
            "condition": condition,
            "component_id": component_id,
            "instruction": instruction,
            "locator": locator,
            "competitors": competitors,
            "files": files,
        }
    }


def main() -> int:
    params: dict = {}

    # F01 Locate money
    inst = "Report the shawm bombard fee posted on the cromorne racket sheet."
    loc = {
        "op": "select_join",
        "left": "Finance/cromorne_racket.csv",
        "right": "Mail/shawm_note.eml",
        "key": "sku",
        "field": "amount",
        "left_where": [{"col": "sku", "eq": "bombard-shawm"}],
    }
    params.update(
        cluster(
            "E01", "F01", "Locate", "money_usd", "plus", "shawm_bombard_fee", inst, loc,
            [
                csv("Finance/cromorne_racket.csv", ["sku", "amount"], [
                    {"sku": "bombard-shawm", "amount": "44.80"},
                    {"sku": "tabor-far", "amount": "8.15"},
                    {"sku": "nakers-far", "amount": "3.40"},
                    {"sku": "rebec-far", "amount": "120.00"},
                ]),
                kv("Mail/shawm_note.eml", listed("bombard-shawm")),
            ],
            ["8.15", "3.40", "120.00"],
        )
    )
    params.update(
        cluster(
            "E02", "F01", "Locate", "money_usd", "minus", "shawm_bombard_fee", inst, loc,
            [
                csv("Finance/cromorne_racket.csv", ["sku", "amount"], [
                    {"sku": "bombard-shawm", "amount": "51.30"},
                    {"sku": "bombard-near", "amount": "48.70"},
                    {"sku": "tabor-x", "amount": "9.20"},
                    {"sku": "nakers-x", "amount": "4.15"},
                ]),
                kv("Mail/shawm_note.eml", listed("bombard-shawm")),
            ],
            ["48.70"],
        )
    )
    params.update(
        cluster(
            "E03", "F01", "Locate", "money_usd", "pm", "shawm_bombard_fee", inst, loc,
            [
                csv("Finance/cromorne_racket.csv", ["sku", "amount"], [
                    {"sku": "bombard-shawm", "amount": "34.10"},
                    {"sku": "bombard-tabor", "amount": "39.70"},
                    {"sku": "shawm-spare", "amount": "7.25"},
                    {"sku": "far-row", "amount": "4.80"},
                ]),
                kv("Mail/shawm_note.eml", listed("bombard-shawm")),
                kv("Notes/posted_index.txt", listed("bombard-shawm", "bombard-tabor")),
            ],
            ["39.70"],
        )
    )

    # F02 Locate integer
    inst = "Read the gittern tabor count on the psaltery citole card."
    loc = {
        "op": "select_join",
        "left": "Notes/psaltery_citole.txt",
        "right": "Finance/gittern_roster.csv",
        "key": "sku",
        "field": "qty",
        "left_where": [{"col": "sku", "eq": "tabor-gittern"}],
    }
    params.update(
        cluster(
            "E04", "F02", "Locate", "integer", "plus", "gittern_tabor_count", inst, loc,
            [
                kv("Notes/psaltery_citole.txt", [
                    {"sku": "tabor-gittern", "qty": "31"},
                    {"sku": "far-a", "qty": "8"},
                    {"sku": "far-b", "qty": "70"},
                    {"sku": "far-c", "qty": "4"},
                ]),
                csv("Finance/gittern_roster.csv", ["sku", "listed"], [
                    {"sku": "tabor-gittern", "listed": "yes"},
                ]),
            ],
            ["8", "70", "4"],
        )
    )
    params.update(
        cluster(
            "E05", "F02", "Locate", "integer", "minus", "gittern_tabor_count", inst, loc,
            [
                kv("Notes/psaltery_citole.txt", [
                    {"sku": "tabor-gittern", "qty": "36"},
                    {"sku": "tabor-near", "qty": "34"},
                    {"sku": "far-a", "qty": "7"},
                    {"sku": "far-b", "qty": "71"},
                ]),
                csv("Finance/gittern_roster.csv", ["sku", "listed"], [
                    {"sku": "tabor-gittern", "listed": "yes"},
                ]),
            ],
            ["34"],
        )
    )
    params.update(
        cluster(
            "E06", "F02", "Locate", "integer", "pm", "gittern_tabor_count", inst, loc,
            [
                kv("Notes/psaltery_citole.txt", [
                    {"sku": "tabor-gittern", "qty": "41"},
                    {"sku": "tabor-vielle", "qty": "43"},
                    {"sku": "far-a", "qty": "6"},
                    {"sku": "far-b", "qty": "80"},
                ]),
                csv("Finance/gittern_roster.csv", ["sku", "listed"], [
                    {"sku": "tabor-gittern", "listed": "yes"},
                ]),
                kv("Notes/both_listed.txt", listed("tabor-gittern", "tabor-vielle")),
            ],
            ["43"],
        )
    )

    # F03 Locate entity
    inst = "Name the dulcian cornett keeper listed on the sackbut gemshorn card."
    loc = {
        "op": "select_join",
        "left": "Notes/sackbut_gemshorn.txt",
        "right": "Finance/dulcian_roster.csv",
        "key": "keeper",
        "field": "keeper",
        "left_where": [],
    }
    params.update(
        cluster(
            "E07", "F03", "Locate", "entity", "plus", "dulcian_keeper", inst, loc,
            [
                kv("Notes/sackbut_gemshorn.txt", [
                    {"keeper": "Nima Kest", "post": "dulcian"},
                ]),
                csv("Finance/dulcian_roster.csv", ["keeper", "post"], [
                    {"keeper": "Nima Kest", "post": "dulcian"},
                ]),
                kv("Mail/spare_keepers.txt", [
                    {"keeper": "Palu Orth", "post": "shawm"},
                    {"keeper": "Soren Vesk", "post": "tabor"},
                    {"keeper": "Kira Mohl", "post": "rebec"},
                ]),
            ],
            ["Palu Orth", "Soren Vesk", "Kira Mohl"],
        )
    )
    params.update(
        cluster(
            "E08", "F03", "Locate", "entity", "minus", "dulcian_keeper", inst, loc,
            [
                kv("Notes/sackbut_gemshorn.txt", [
                    {"keeper": "Palu Orth", "post": "dulcian"},
                    {"alt": "Soren Vesk", "note": "same card"},
                ]),
                csv("Finance/dulcian_roster.csv", ["keeper", "post"], [
                    {"keeper": "Palu Orth", "post": "dulcian"},
                    {"keeper": "Soren Vesk", "post": "shawm"},
                    {"keeper": "Kira Mohl", "post": "tabor"},
                    {"keeper": "Eben Tulk", "post": "rebec"},
                ]),
            ],
            ["Soren Vesk"],
        )
    )
    params.update(
        cluster(
            "E09", "F03", "Locate", "entity", "pm", "dulcian_keeper", inst, loc,
            [
                kv("Notes/sackbut_gemshorn.txt", [
                    {"keeper": "Yara Nolt", "post": "dulcian"},
                ]),
                csv("Finance/dulcian_roster.csv", ["keeper", "post"], [
                    {"keeper": "Yara Nolt", "post": "dulcian"},
                    {"keeper": "Oda Wex", "post": "dulcian"},
                    {"keeper": "Lumen Brant", "post": "tabor"},
                    {"keeper": "Kira Mohl", "post": "rebec"},
                ]),
                kv("Notes/both_hands.txt", listed("Yara Nolt", "Oda Wex", key="keeper")),
            ],
            ["Oda Wex"],
        )
    )

    # F04 Compute money
    inst = "Sum the nakers shawm crate costs that the vielle note lists."
    loc = {
        "op": "sum_join",
        "left": "Finance/nakers_crates.csv",
        "right": "Notes/vielle_list.txt",
        "key": "sku",
        "field": "amount",
        "left_where": [{"col": "yard", "eq": "nakers"}],
    }
    params.update(
        cluster(
            "E10", "F04", "Compute", "money_usd", "plus", "nakers_crate_sum", inst, loc,
            [
                csv("Finance/nakers_crates.csv", ["sku", "yard", "amount"], [
                    {"sku": "n-a", "yard": "nakers", "amount": "15.20"},
                    {"sku": "n-b", "yard": "nakers", "amount": "18.40"},
                    {"sku": "n-c", "yard": "tabor", "amount": "5.10"},
                    {"sku": "n-d", "yard": "rebec", "amount": "6.05"},
                ]),
                kv("Notes/vielle_list.txt", listed("n-a", "n-b")),
                kv("Notes/pre_sum.txt", [{"yard": "nakers", "amount": "9.00", "note": "draft total"}]),
            ],
            ["5.10", "6.05", "9.00"],
        )
    )
    params.update(
        cluster(
            "E11", "F04", "Compute", "money_usd", "minus", "nakers_crate_sum", inst, loc,
            [
                csv("Finance/nakers_crates.csv", ["sku", "yard", "amount"], [
                    {"sku": "n-a", "yard": "nakers", "amount": "16.10"},
                    {"sku": "n-b", "yard": "nakers", "amount": "19.50"},
                    {"sku": "n-c", "yard": "tabor", "amount": "5.20"},
                    {"sku": "n-d", "yard": "rebec", "amount": "6.15"},
                ]),
                kv("Notes/vielle_list.txt", listed("n-a", "n-b")),
                kv("Notes/pre_sum.txt", [{"yard": "nakers", "amount": "37.80", "note": "draft total"}]),
            ],
            ["37.80"],
        )
    )
    params.update(
        cluster(
            "E12", "F04", "Compute", "money_usd", "pm", "nakers_crate_sum", inst, loc,
            [
                csv("Finance/nakers_crates.csv", ["sku", "yard", "amount"], [
                    {"sku": "n-a", "yard": "nakers", "amount": "14.70"},
                    {"sku": "n-b", "yard": "nakers", "amount": "17.90"},
                    {"sku": "n-c", "yard": "nakers", "amount": "31.45"},
                    {"sku": "n-d", "yard": "rebec", "amount": "6.25"},
                ]),
                kv("Notes/vielle_list.txt", listed("n-a", "n-b")),
                kv("Notes/all_nakers.txt", listed("n-a", "n-b", "n-c")),
            ],
            ["31.45"],
        )
    )

    # F05 Compute integer
    inst = "Sum the racket bombard crate counts that the crumhorn roster lists."
    loc = {
        "op": "sum_join",
        "left": "Finance/racket_counts.csv",
        "right": "Notes/crumhorn_roster.txt",
        "key": "sku",
        "field": "qty",
        "left_where": [{"col": "site", "eq": "racket"}],
    }
    params.update(
        cluster(
            "E13", "F05", "Compute", "integer", "plus", "racket_qty_sum", inst, loc,
            [
                csv("Finance/racket_counts.csv", ["sku", "site", "qty"], [
                    {"sku": "r-a", "site": "racket", "qty": "12"},
                    {"sku": "r-b", "site": "racket", "qty": "19"},
                    {"sku": "r-c", "site": "shawm", "qty": "4"},
                    {"sku": "r-d", "site": "tabor", "qty": "70"},
                ]),
                kv("Notes/crumhorn_roster.txt", listed("r-a", "r-b")),
            ],
            ["4", "70"],
        )
    )
    params.update(
        cluster(
            "E14", "F05", "Compute", "integer", "minus", "racket_qty_sum", inst, loc,
            [
                csv("Finance/racket_counts.csv", ["sku", "site", "qty"], [
                    {"sku": "r-a", "site": "racket", "qty": "14"},
                    {"sku": "r-b", "site": "racket", "qty": "21"},
                    {"sku": "r-c", "site": "shawm", "qty": "5"},
                    {"sku": "r-d", "site": "tabor", "qty": "72"},
                ]),
                kv("Notes/crumhorn_roster.txt", listed("r-a", "r-b")),
                kv("Notes/draft_qty.txt", [{"site": "racket", "qty": "37", "note": "draft"}]),
            ],
            ["37"],
        )
    )
    params.update(
        cluster(
            "E15", "F05", "Compute", "integer", "pm", "racket_qty_sum", inst, loc,
            [
                csv("Finance/racket_counts.csv", ["sku", "site", "qty"], [
                    {"sku": "r-a", "site": "racket", "qty": "13"},
                    {"sku": "r-b", "site": "racket", "qty": "20"},
                    {"sku": "r-c", "site": "racket", "qty": "35"},
                    {"sku": "r-d", "site": "tabor", "qty": "8"},
                ]),
                kv("Notes/crumhorn_roster.txt", listed("r-a", "r-b")),
                kv("Notes/all_racket.txt", listed("r-a", "r-b", "r-c")),
            ],
            ["35"],
        )
    )

    # F06 Reconcile money
    inst = "Report the live citole sackbut due on the citole live sheet."
    loc = {
        "op": "live_not_stale",
        "left": "Finance/citole_live.csv",
        "right": "Mail/sackbut_quote.eml",
        "key": "item",
        "field": "amount",
        "left_where": [{"col": "item", "eq": "citole-bin"}],
        "right_where": [{"col": "item", "eq": "citole-bin"}],
    }
    params.update(
        cluster(
            "E16", "F06", "Reconcile", "money_usd", "plus", "citole_live_due", inst, loc,
            [
                csv("Finance/citole_live.csv", ["item", "amount"], [
                    {"item": "citole-bin", "amount": "66.20"},
                    {"item": "far-a", "amount": "8.05"},
                    {"item": "far-b", "amount": "9.10"},
                    {"item": "far-c", "amount": "3.25"},
                ]),
                kv("Mail/sackbut_quote.eml", [
                    {"item": "citole-bin", "amount": "11.00", "subject": "stale quote"},
                ]),
            ],
            ["8.05", "9.10", "3.25", "11.00"],
        )
    )
    params.update(
        cluster(
            "E17", "F06", "Reconcile", "money_usd", "minus", "citole_live_due", inst, loc,
            [
                csv("Finance/citole_live.csv", ["item", "amount"], [
                    {"item": "citole-bin", "amount": "73.40"},
                    {"item": "far-a", "amount": "8.20"},
                    {"item": "far-b", "amount": "9.30"},
                    {"item": "far-c", "amount": "3.35"},
                ]),
                kv("Mail/sackbut_quote.eml", [
                    {"item": "citole-bin", "amount": "76.50", "subject": "stale quote"},
                ]),
            ],
            ["76.50"],
        )
    )
    params.update(
        cluster(
            "E18", "F06", "Reconcile", "money_usd", "pm", "citole_live_due", inst, loc,
            [
                csv("Finance/citole_live.csv", ["item", "amount"], [
                    {"item": "citole-bin", "amount": "82.15"},
                    {"item": "far-a", "amount": "8.40"},
                    {"item": "far-b", "amount": "9.50"},
                    {"item": "far-c", "amount": "3.55"},
                ]),
                kv("Mail/sackbut_quote.eml", [
                    {"item": "citole-bin", "amount": "88.05", "subject": "stale quote"},
                ]),
                kv("Notes/posted_due.txt", [
                    {"item": "citole-bin", "amount": "79.40", "mark": "board"},
                ]),
            ],
            ["88.05", "79.40"],
        )
    )

    # F07 Reconcile entity
    inst = "Name the live vielle gemshorn clerk on the vielle live sheet."
    loc = {
        "op": "live_not_stale",
        "left": "Finance/vielle_live.csv",
        "right": "Mail/gemshorn_roster.eml",
        "key": "seat",
        "field": "clerk",
        "left_where": [{"col": "seat", "eq": "vielle-desk"}],
        "right_where": [{"col": "seat", "eq": "vielle-desk"}],
    }
    params.update(
        cluster(
            "E19", "F07", "Reconcile", "entity", "plus", "vielle_live_clerk", inst, loc,
            [
                csv("Finance/vielle_live.csv", ["seat", "clerk"], [
                    {"seat": "vielle-desk", "clerk": "Eben Tulk"},
                    {"seat": "far-a", "clerk": "Nima Kest"},
                    {"seat": "far-b", "clerk": "Palu Orth"},
                    {"seat": "far-c", "clerk": "Kira Mohl"},
                ]),
                kv("Mail/gemshorn_roster.eml", [
                    {"seat": "vielle-desk", "clerk": "Soren Vesk", "subject": "stale roster"},
                ]),
            ],
            ["Soren Vesk"],
        )
    )
    params.update(
        cluster(
            "E20", "F07", "Reconcile", "entity", "minus", "vielle_live_clerk", inst, loc,
            [
                csv("Finance/vielle_live.csv", ["seat", "clerk"], [
                    {"seat": "vielle-desk", "clerk": "Lumen Brant"},
                    {"seat": "far-a", "clerk": "Nima Kest"},
                    {"seat": "far-b", "clerk": "Palu Orth"},
                    {"seat": "far-c", "clerk": "Kira Mohl"},
                ]),
                kv("Mail/gemshorn_roster.eml", [
                    {"seat": "vielle-desk", "clerk": "Oda Wex", "subject": "stale roster"},
                ]),
            ],
            ["Oda Wex"],
        )
    )
    params.update(
        cluster(
            "E21", "F07", "Reconcile", "entity", "pm", "vielle_live_clerk", inst, loc,
            [
                csv("Finance/vielle_live.csv", ["seat", "clerk"], [
                    {"seat": "vielle-desk", "clerk": "Yara Nolt"},
                    {"seat": "far-a", "clerk": "Nima Kest"},
                    {"seat": "far-b", "clerk": "Palu Orth"},
                    {"seat": "far-c", "clerk": "Kira Mohl"},
                ]),
                kv("Mail/gemshorn_roster.eml", [
                    {"seat": "vielle-desk", "clerk": "Oda Wex", "subject": "stale roster"},
                ]),
                kv("Notes/board_clerk.txt", [
                    {"seat": "vielle-desk", "clerk": "Eben Tulk", "mark": "board"},
                ]),
            ],
            ["Oda Wex", "Eben Tulk"],
        )
    )

    # F08 Filter categorical
    inst = "Give the reed status for the shawm dulcian sealed slip."
    loc = {
        "op": "select_join",
        "left": "Finance/shawm_sheet.csv",
        "right": "Notes/sealed_index.txt",
        "key": "sku",
        "field": "reed_status",
        "left_where": [
            {"col": "yard", "eq": "shawm"},
            {"col": "seal", "eq": "yes"},
        ],
    }
    params.update(
        cluster(
            "E22", "F08", "Filter", "categorical", "plus", "shawm_reed_status", inst, loc,
            [
                csv("Finance/shawm_sheet.csv", ["sku", "yard", "seal", "reed_status"], [
                    {"sku": "seal-a", "yard": "shawm", "seal": "yes", "reed_status": "keyed"},
                    {"sku": "seal-b", "yard": "tabor", "seal": "no", "reed_status": "none"},
                    {"sku": "seal-c", "yard": "rebec", "seal": "yes", "reed_status": "none"},
                    {"sku": "seal-d", "yard": "vielle", "seal": "no", "reed_status": "none"},
                ]),
                kv("Notes/sealed_index.txt", listed("seal-a")),
                kv("Notes/spare_marks.txt", [
                    {"mark": "capped"},
                    {"alt": "Palu Orth"},
                    {"spare": "tabor-x"},
                ]),
            ],
            ["capped"],
        )
    )
    params.update(
        cluster(
            "E23", "F08", "Filter", "categorical", "minus", "shawm_reed_status", inst, loc,
            [
                csv("Finance/shawm_sheet.csv", ["sku", "yard", "seal", "reed_status"], [
                    {"sku": "seal-a", "yard": "shawm", "seal": "yes", "reed_status": "capped"},
                    {"sku": "seal-near", "yard": "shawm", "seal": "no", "reed_status": "reeded"},
                    {"sku": "seal-c", "yard": "rebec", "seal": "yes", "reed_status": "keyed"},
                    {"sku": "seal-d", "yard": "vielle", "seal": "no", "reed_status": "fretted"},
                ]),
                kv("Notes/sealed_index.txt", listed("seal-a")),
            ],
            ["reeded"],
        )
    )
    params.update(
        cluster(
            "E24", "F08", "Filter", "categorical", "pm", "shawm_reed_status", inst, loc,
            [
                csv("Finance/shawm_sheet.csv", ["sku", "yard", "seal", "reed_status"], [
                    {"sku": "seal-a", "yard": "shawm", "seal": "yes", "reed_status": "reeded"},
                    {"sku": "seal-b", "yard": "shawm", "seal": "yes", "reed_status": "keyed"},
                    {"sku": "seal-c", "yard": "rebec", "seal": "no", "reed_status": "capped"},
                    {"sku": "seal-d", "yard": "vielle", "seal": "no", "reed_status": "fretted"},
                ]),
                kv("Notes/sealed_index.txt", listed("seal-a")),
                kv("Notes/all_shawm_seal.txt", listed("seal-a", "seal-b")),
            ],
            ["keyed"],
        )
    )

    # F09 Tally integer
    inst = "Count the bombard cromorne notes in the mail that also appear on the gittern sheet."
    loc = {
        "op": "count_join",
        "left": "Mail/cromorne_notes.eml",
        "right": "Finance/gittern_sheet.csv",
        "key": "sku",
        "field": "sku",
        "left_where": [{"col": "rush", "eq": "yes"}],
    }
    params.update(
        cluster(
            "E25", "F09", "Tally", "integer", "plus", "bombard_mail_count", inst, loc,
            [
                kv("Mail/cromorne_notes.eml", rush_rows("b", 21, 4)),
                csv("Finance/gittern_sheet.csv", ["sku", "bin"], sheet_rows("b", 21, extra=2)),
                kv("Notes/posted_n.txt", [{"n": "40", "note": "board tally"}]),
            ],
            ["40"],
        )
    )
    params.update(
        cluster(
            "E26", "F09", "Tally", "integer", "minus", "bombard_mail_count", inst, loc,
            [
                kv("Mail/cromorne_notes.eml", rush_rows("b", 34, 4)),
                csv("Finance/gittern_sheet.csv", ["sku", "bin"], sheet_rows("b", 32, extra=2)),
                kv("Notes/posted_n.txt", [{"n": "34", "note": "board tally"}]),
            ],
            ["34"],
        )
    )
    params.update(
        cluster(
            "E27", "F09", "Tally", "integer", "pm", "bombard_mail_count", inst, loc,
            [
                kv("Mail/cromorne_notes.eml", rush_rows("b", 26, 4)),
                csv("Finance/gittern_sheet.csv", ["sku", "bin"], sheet_rows("b", 23, extra=2)),
                kv("Notes/all_rush.txt", [{"n": "26", "note": "rush-only"}]),
            ],
            ["26"],
        )
    )

    # F10 Multi-step money
    inst = "Report the cornett tabor due that appears on the psaltery sheet, the citole card, and the rebec tag."
    loc = {
        "op": "select_join3",
        "left": "Finance/psaltery_sheet.csv",
        "mid": "Notes/citole_card.txt",
        "right": "Mail/rebec_tag.eml",
        "key": "sku",
        "field": "amount",
        "left_where": [{"col": "yard", "eq": "cornett"}],
    }
    params.update(
        cluster(
            "E28", "F10", "Multi-step", "money_usd", "plus", "cornett_triple_due", inst, loc,
            [
                csv("Finance/psaltery_sheet.csv", ["sku", "yard", "amount"], [
                    {"sku": "c-1", "yard": "cornett", "amount": "47.20"},
                    {"sku": "c-2", "yard": "tabor", "amount": "8.55"},
                    {"sku": "c-3", "yard": "shawm", "amount": "9.05"},
                    {"sku": "c-4", "yard": "vielle", "amount": "3.70"},
                ]),
                kv("Notes/citole_card.txt", listed("c-1")),
                kv("Mail/rebec_tag.eml", [{"sku": "c-1", "tag": "live"}]),
            ],
            ["8.55", "9.05", "3.70"],
        )
    )
    params.update(
        cluster(
            "E29", "F10", "Multi-step", "money_usd", "minus", "cornett_triple_due", inst, loc,
            [
                csv("Finance/psaltery_sheet.csv", ["sku", "yard", "amount"], [
                    {"sku": "c-1", "yard": "cornett", "amount": "54.05"},
                    {"sku": "c-2", "yard": "cornett", "amount": "58.70"},
                    {"sku": "c-3", "yard": "shawm", "amount": "9.15"},
                    {"sku": "c-4", "yard": "vielle", "amount": "3.80"},
                ]),
                kv("Notes/citole_card.txt", listed("c-1")),
                kv("Mail/rebec_tag.eml", [{"sku": "c-1", "tag": "live"}]),
            ],
            ["58.70"],
        )
    )
    params.update(
        cluster(
            "E30", "F10", "Multi-step", "money_usd", "pm", "cornett_triple_due", inst, loc,
            [
                csv("Finance/psaltery_sheet.csv", ["sku", "yard", "amount"], [
                    {"sku": "c-1", "yard": "cornett", "amount": "61.80"},
                    {"sku": "c-2", "yard": "cornett", "amount": "69.35"},
                    {"sku": "c-3", "yard": "shawm", "amount": "9.25"},
                    {"sku": "c-4", "yard": "vielle", "amount": "3.90"},
                ]),
                kv("Notes/citole_card.txt", listed("c-1", "c-2")),
                kv("Mail/rebec_tag.eml", [{"sku": "c-1", "tag": "live"}]),
            ],
            ["69.35"],
        )
    )

    ids = [f"E{i:02d}" for i in range(1, 31)]
    if list(params) != ids:
        raise SystemExit(f"key order {list(params)} != {ids}")
    OUT.write_text(json.dumps(params, indent=2) + "\n")
    print(f"wrote {len(params)} clusters to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
