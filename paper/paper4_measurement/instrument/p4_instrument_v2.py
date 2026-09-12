"""P4-C2 Declared Final Claim instrument (Metric v2).

Inputs: channel text, kind, gold.
No anchors. No task_id branch. Does not import the v1 scorer.
Refuses any path under construction/sealed/v.
This is not a patch of V1–V6.
"""
from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path

MONEY_RE = re.compile(
    r"\$\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?|\d{1,3}(?:,\d{3})*\.\d{1,2}"
)
INT_RE = re.compile(r"\d+")
WELL_FORMED_FN = re.compile(r"<function[\s\S]*?</function>", re.I)
WELL_FORMED_TOOL = re.compile(r"<tool[\s\S]*?</tool>", re.I)
SELF_CLOSE_FN = re.compile(r"<function[^>]*/>", re.I)
SELF_CLOSE_TOOL = re.compile(r"<tool[^>]*/>", re.I)
OPENER = re.compile(r"<function|<tool", re.I)
CLAIM_RE = re.compile(r"^\s*CLAIM\s*:\s*(.+?)\s*$", re.I)


def refuse_v_path(path: Path | str | None) -> None:
    if path is None:
        return
    parts = Path(path).resolve().parts
    for i, part in enumerate(parts):
        if part == "sealed" and i + 1 < len(parts) and parts[i + 1] == "v":
            raise RuntimeError("P4 v2 instrument refuses sealed V* paths")


def collapse(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def v1_clean(channel: str) -> tuple[str | None, str | None]:
    text = WELL_FORMED_FN.sub("", channel)
    text = WELL_FORMED_TOOL.sub("", text)
    text = SELF_CLOSE_FN.sub("", text)
    text = SELF_CLOSE_TOOL.sub("", text)
    if OPENER.search(text):
        return None, "channel_indeterminate"
    return text, None


def parse_money(raw: str) -> Decimal:
    return Decimal(raw.replace("$", "").replace(",", ""))


def claim_remainders(cleaned: str) -> tuple[list[str] | None, str | None]:
    found_line = False
    remainders: list[str] = []
    for raw in cleaned.split("\n"):
        line = raw.rstrip("\r")
        m = CLAIM_RE.match(line)
        if not m:
            continue
        found_line = True
        rem = m.group(1).strip()
        if rem:
            remainders.append(rem)
    if not found_line:
        return None, "no_claim"
    if not remainders:
        return None, "absent_claim"
    return remainders, None


def parse_kind_values(kind: str, remainder: str) -> list:
    if kind == "money_usd":
        return [parse_money(m.group(0)) for m in MONEY_RE.finditer(remainder)]
    if kind == "integer":
        money_spans = [m.span() for m in MONEY_RE.finditer(remainder)]
        out = []
        for m in INT_RE.finditer(remainder):
            a, b = m.span()
            if any(a < mb and b > ma for ma, mb in money_spans):
                continue
            out.append(int(m.group(0)))
        return out
    if kind not in {"entity", "categorical"}:
        raise ValueError(f"unknown kind {kind}")
    return [remainder]


def equiv_key(kind: str, val) -> str:
    if kind == "money_usd":
        return str(Decimal(val))
    if kind == "integer":
        return str(int(val))
    return collapse(str(val)).casefold()


def v3_match(kind: str, committed, gold: str) -> bool:
    if kind == "money_usd":
        a = Decimal(committed)
        b = parse_money(gold)
        if abs(a - b) <= 1:
            return True
        return a.to_integral_value() == b.to_integral_value()
    if kind == "integer":
        return int(committed) == int(gold)
    return collapse(str(committed)).casefold() == collapse(gold).casefold()


def score_v2(channel: str, *, kind: str, gold: str) -> dict:
    """Score one episode-component on the declared CLAIM line only."""
    cleaned, v1_cause = v1_clean(channel)
    if v1_cause:
        return {"status": "ABSTAIN", "cause": v1_cause, "committed": None}
    remainders, locate_cause = claim_remainders(cleaned)
    if locate_cause:
        return {"status": "ABSTAIN", "cause": locate_cause, "committed": None}
    found: list = []
    for rem in remainders:
        vals = parse_kind_values(kind, rem)
        if kind in {"money_usd", "integer"} and len({equiv_key(kind, v) for v in vals}) > 1:
            return {"status": "ABSTAIN", "cause": "ambiguous_claim", "committed": None}
        found.extend(vals)
    if not found:
        return {"status": "ABSTAIN", "cause": "absent_claim", "committed": None}
    classes: dict[str, object] = {}
    for val in found:
        classes.setdefault(equiv_key(kind, val), val)
    if len(classes) > 1:
        return {"status": "ABSTAIN", "cause": "ambiguous_claim", "committed": None}
    committed = next(iter(classes.values()))
    if v3_match(kind, committed, gold):
        return {"status": "HIT", "cause": "match", "committed": str(committed)}
    return {"status": "MISS", "cause": "mismatch", "committed": str(committed)}
