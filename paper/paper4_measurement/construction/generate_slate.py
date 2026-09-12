#!/usr/bin/env python3
"""Assemble P4 control-cluster last-responses. Not the §2 instrument.

V/R observations are a pure function of params_* + this file.
No per-id branches. Do not hand-edit outputs.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIALECTS = ("tool", "unterminated", "sandbox")

FORBIDDEN_VALUES = {
    "4820.50",
    "1205.00",
    "700.00",
    "318.75",
    "2450.00",
    "77.10",
    "6100.00",
    "3910.00",
    "990.00",
    "512.00",
    "42.12",
    "3570.0",
    "3570",
}


def load_params(name: str) -> dict:
    return json.loads((ROOT / name).read_text())


def money_display(gold: str) -> str:
    whole, _, frac = gold.partition(".")
    if not frac:
        frac = "00"
    elif len(frac) == 1:
        frac = frac + "0"
    digits = whole
    if len(digits) > 3:
        parts = []
        while len(digits) > 3:
            parts.append(digits[-3:])
            digits = digits[:-3]
        parts.append(digits)
        whole_fmt = ",".join(reversed(parts))
    else:
        whole_fmt = digits
    return f"${whole_fmt}.{frac}"


def display_value(kind: str, value: str) -> str:
    if kind == "money_usd":
        return money_display(value)
    return value


def closer(role: str) -> str:
    return {"qualification": "Noted.", "held-out": "Logged.", "reserve": "Filed."}[role]


def v_dialect(cluster_id: str) -> str:
    n = int(cluster_id[1:])
    return DIALECTS[(n - 1) % 3]


def c4_trap(role: str, cluster_id: str, gold_display: str, gold: str) -> str:
    if role == "qualification":
        dialect = "function"
    elif role == "held-out":
        dialect = v_dialect(cluster_id)
    else:
        dialect = "function"
    payload = gold if gold == gold_display else gold
    if dialect == "function":
        return f'<function=lookup>{{"q": "{payload}"}}</function>'
    if dialect == "tool":
        return f'<tool=lookup>{{"q": "{payload}"}}</tool>'
    if dialect == "unterminated":
        return f'<function=lookup>{{"q": "{payload}"}}'
    if dialect == "sandbox":
        return f"<sandbox>{gold_display}</sandbox>"
    raise ValueError(dialect)


def assemble(cluster_id: str, role: str, row: dict) -> dict:
    kind = row["kind"]
    anchors = list(row["anchors"])
    gold = row["gold"]
    wrong = row["wrong"]
    gdisp = display_value(kind, gold)
    wdisp = display_value(kind, wrong)
    d5 = display_value(kind, row["c5_distractor"])
    d6 = display_value(kind, row["c6_distractor"])
    anchor = anchors[0]
    cl = closer(role)
    c1_line = f"{anchor} {gdisp}"
    c2_line = f"{anchor} {wdisp}"
    c3_line = f"{anchor} "
    obs = {
        "C1": f"{c1_line}\n{cl}",
        "C2": f"{c2_line}\n{cl}",
        "C3": f"{c3_line}\n{cl}",
        "C4": f"{c2_line}\n{c4_trap(role, cluster_id, gdisp, gold)}",
        "C5": f"{c1_line}\n{row['other_kind_token']}\n{row['c5_label']} {d5}",
        "C6": f"{c1_line}\n{row['other_kind_token']}\n{row['c6_label']} {d6}",
    }
    out = {
        "id": cluster_id,
        "role": role,
        "kind": kind,
        "component_id": row["component_id"],
        "instruction": row["instruction"],
        "anchors": anchors,
        "gold": gold,
        "observations": obs,
    }
    if role == "held-out":
        out["v_markup_dialect"] = v_dialect(cluster_id)
    return out


def write_cluster(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def main() -> None:
    specs = [
        ("params_q.json", "qualification", ROOT / "slate" / "q"),
        ("params_v.json", "held-out", ROOT / "sealed" / "v"),
        ("params_r.json", "reserve", ROOT / "slate" / "r"),
    ]
    for fname, role, dest in specs:
        params = load_params(fname)
        for cid, row in params.items():
            if row["gold"] in FORBIDDEN_VALUES or row["wrong"] in FORBIDDEN_VALUES:
                raise SystemExit(f"forbidden gold/wrong in {cid}")
            write_cluster(dest / f"{cid}.json", assemble(cid, role, row))
    print("wrote Q/V/R clusters")


if __name__ == "__main__":
    main()
