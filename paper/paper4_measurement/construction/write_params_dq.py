#!/usr/bin/env python3
"""Emit params_dq.json. Data table only. generate_dq.py has no per-id branch.

P4-C2 Phase 2 Q2 synthetics. D dialect. No C/B last-texts. No anchors.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

P: dict = {}

P["DQ01"] = {
    "kind": "money_usd",
    "component_id": "folio_vellum_due",
    "instruction": "Report the folio vellum due on the quire rubric sheet.",
    "gold": "84.20",
    "wrong": "61.10",
    "line_extra": "12.50",
    "c5_working": "Spare folio note lists 9.15 for context.",
    "c6_working": "Spare quire note lists 3.80 for context.",
    "working": (
        "The quire rubric sheet lists:\n"
        "- spare-a: 12.50\n"
        "- vellum-folio: 84.20\n"
        "- spare-b: 9.15"
    ),
}

P["DQ02"] = {
    "kind": "money_usd",
    "component_id": "morocco_gilt_due",
    "instruction": "Report the morocco gilt due on the palimpsest sheet.",
    "gold": "91.35",
    "wrong": "33.80",
    "line_extra": "17.60",
    "c5_working": "Spare morocco note lists 4.25 for context.",
    "c6_working": "Spare gilt note lists 8.90 for context.",
    "working": (
        "The palimpsest incunable sheet lists:\n"
        "- spare-a: 17.60\n"
        "- gilt-morocco: 91.35\n"
        "- spare-b: 4.25"
    ),
}

P["DQ03"] = {
    "kind": "integer",
    "component_id": "codex_tally",
    "instruction": "Count the codex rubric tally on the palimpsest roster.",
    "gold": "41",
    "wrong": "22",
    "line_extra": "17",
    "c5_working": "Spare codex note lists 801 for context.",
    "c6_working": "Spare rubric note lists 726 for context.",
    "working": (
        "The palimpsest roster lists:\n"
        "- bin-a: 17\n"
        "- codex-rubric: 41\n"
        "- bin-b: 29"
    ),
}

P["DQ04"] = {
    "kind": "integer",
    "component_id": "quire_count",
    "instruction": "Read the quire colophon count from the morocco card.",
    "gold": "53",
    "wrong": "29",
    "line_extra": "11",
    "c5_working": "Spare quire note lists 64 for context.",
    "c6_working": "Spare colophon note lists 77 for context.",
    "working": (
        "The morocco card lists:\n"
        "- shift-a: 11\n"
        "- quire-colophon: 53\n"
        "- shift-b: 29"
    ),
}

P["DQ05"] = {
    "kind": "entity",
    "component_id": "uncial_keeper",
    "instruction": "Name the uncial keeper on the flyleaf colophon card.",
    "gold": "Helene Quill",
    "wrong": "Kaspar Veld",
    "c5_working": "Spare flyleaf note lists Mira Solt for context.",
    "c6_working": "Spare colophon note lists Pavel Orth for context.",
    "working": (
        "The flyleaf colophon card lists:\n"
        "- day: Kaspar Veld\n"
        "- uncial: Helene Quill\n"
        "- spare: Mira Solt"
    ),
}

P["DQ06"] = {
    "kind": "categorical",
    "component_id": "pressmark_bind",
    "instruction": "Give the pressmark gathering bind status on the verso card.",
    "gold": "sewn",
    "wrong": "cased",
    "c5_working": "Spare pressmark note lists loose for context.",
    "c6_working": "Spare gathering note lists tight for context.",
    "working": (
        "The verso card lists:\n"
        "- short: cased\n"
        "- pressmark-gathering: sewn\n"
        "- spare: loose"
    ),
}


def main() -> None:
    ids = [f"DQ{i:02d}" for i in range(1, 7)]
    missing = [i for i in ids if i not in P]
    extra = [k for k in P if k not in ids]
    if missing or extra:
        raise SystemExit(f"id mismatch missing={missing} extra={extra}")
    for cid, row in P.items():
        if "anchors" in row or "observations" in row:
            raise SystemExit(f"{cid}: forbidden param field")
    (ROOT / "params_dq.json").write_text(json.dumps({k: P[k] for k in ids}, indent=2) + "\n")
    print("wrote params_dq.json", len(ids))


if __name__ == "__main__":
    main()
