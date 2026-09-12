"""P4 §2 correspondence instrument.

Inputs: channel text, kind, gold, anchors.
No task_id branch. Refuses any path under construction/sealed/v.
This is not R-AGG / R-SCOPE / R-CHAN / ALL / R / commit 3242c30.
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

def refuse_v_path(path: Path | str | None) -> None:
    if path is None:
        return
    parts = Path(path).resolve().parts
    for i, part in enumerate(parts):
        if part == "sealed" and i + 1 < len(parts) and parts[i + 1] == "v":
            raise RuntimeError("P4 instrument refuses sealed V* paths")


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


def locate_lines(cleaned: str, anchors: list[str]) -> list[str]:
    located = []
    for line in cleaned.split("\n"):
        nline = collapse(line).casefold()
        if any(collapse(a).casefold() in nline for a in anchors):
            located.append(line)
    return located


def first_anchor_cut(line: str, anchors: list[str]) -> int | None:
    best = None
    lcf = line.casefold()
    for a in anchors:
        idx = lcf.find(a.casefold())
        if idx >= 0 and (best is None or idx < best[0]):
            best = (idx, len(a))
    if best is None:
        return None
    return best[0] + best[1]


def extract_candidates(kind: str, located: list[str], anchors: list[str]) -> list:
    found: list = []
    if kind == "money_usd":
        for line in located:
            for m in MONEY_RE.finditer(line):
                found.append(parse_money(m.group(0)))
        return found
    if kind == "integer":
        for line in located:
            money_spans = [m.span() for m in MONEY_RE.finditer(line)]
            for m in INT_RE.finditer(line):
                a, b = m.span()
                if any(a < mb and b > ma for ma, mb in money_spans):
                    continue
                found.append(int(m.group(0)))
        return found
    if kind not in {"entity", "categorical"}:
        raise ValueError(f"unknown kind {kind}")
    for line in located:
        cut = first_anchor_cut(line, anchors)
        if cut is None:
            continue
        rem = line[cut:].strip()
        if rem:
            found.append(rem)
    return found


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


def score(channel: str, *, kind: str, gold: str, anchors: list[str]) -> dict:
    """Score one episode-component. Does not read task_id."""
    cleaned, v1_cause = v1_clean(channel)
    if v1_cause:
        return {"status": "ABSTAIN", "cause": v1_cause, "committed": None}
    located = locate_lines(cleaned, anchors)
    if not located:
        return {"status": "ABSTAIN", "cause": "no_anchor", "committed": None}
    found = extract_candidates(kind, located, anchors)
    if not found:
        return {"status": "ABSTAIN", "cause": "absent", "committed": None}
    classes: dict[str, object] = {}
    for val in found:
        classes.setdefault(equiv_key(kind, val), val)
    if len(classes) > 1:
        return {"status": "ABSTAIN", "cause": "ambiguous", "committed": None}
    committed = next(iter(classes.values()))
    if v3_match(kind, committed, gold):
        return {"status": "HIT", "cause": "match", "committed": str(committed)}
    return {"status": "MISS", "cause": "mismatch", "committed": str(committed)}
