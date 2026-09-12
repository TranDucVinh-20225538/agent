#!/usr/bin/env python3
"""P4-C2 independent adjudicator A2. Trajectory + world → GT.

Does not import or call a correspondence scorer.
Does not read last assistant text.
No task_id / cluster_id branch. Conservative INDETERMINATE on Compute/Tally
when summands/members are not evidenced in tool results.
"""
from __future__ import annotations

import re
from decimal import Decimal

MONEY_RE = re.compile(
    r"\$\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?|\d{1,3}(?:,\d{3})*\.\d{1,2}"
)
INT_RE = re.compile(r"\d+")


def _norm_path(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def _gold_in_text(kind: str, gold: str, text: str) -> bool:
    if kind == "money_usd":
        target = Decimal(gold.replace("$", "").replace(",", ""))
        for m in MONEY_RE.finditer(text or ""):
            try:
                if Decimal(m.group(0).replace("$", "").replace(",", "")) == target:
                    return True
            except Exception:
                continue
        return False
    if kind == "integer":
        money_spans = [m.span() for m in MONEY_RE.finditer(text or "")]
        for m in INT_RE.finditer(text or ""):
            a, b = m.span()
            if any(a < mb and b > ma for ma, mb in money_spans):
                continue
            if m.group(0) == str(int(gold)):
                return True
        return False
    return gold.casefold() in (text or "").casefold()


def _same_kind_non_gold(kind: str, gold: str, text: str) -> list[str]:
    found: list[str] = []
    if kind == "money_usd":
        target = Decimal(gold.replace("$", "").replace(",", ""))
        for m in MONEY_RE.finditer(text or ""):
            raw = m.group(0).replace("$", "").replace(",", "")
            try:
                val = Decimal(raw)
            except Exception:
                continue
            if val != target:
                found.append(f"{val:.2f}")
        return found
    if kind == "integer":
        g = str(int(gold))
        money_spans = [m.span() for m in MONEY_RE.finditer(text or "")]
        for m in INT_RE.finditer(text or ""):
            a, b = m.span()
            if any(a < mb and b > ma for ma, mb in money_spans):
                continue
            if m.group(0) != g:
                found.append(m.group(0))
        return found
    g = gold.casefold()
    blob = (text or "").casefold()
    if gold and g not in blob and blob.strip():
        return [text.strip()[:80]]
    return []


def live_paths(locator: dict) -> list[str]:
    paths = [_norm_path(locator["left"])]
    if locator.get("op") == "select_join3" and locator.get("mid"):
        paths.append(_norm_path(locator["mid"]))
    return paths


def stale_path(locator: dict) -> str | None:
    if locator.get("op") == "live_not_stale":
        return _norm_path(locator["right"])
    return None


def source_paths(locator: dict) -> list[str]:
    paths = [_norm_path(locator["left"]), _norm_path(locator["right"])]
    if locator.get("mid"):
        paths.append(_norm_path(locator["mid"]))
    out: list[str] = []
    for p in paths:
        if p not in out:
            out.append(p)
    return out


def _read_events(tool_trace: list[dict]) -> list[dict]:
    reads = []
    for ev in tool_trace or []:
        tool = str(ev.get("tool") or ev.get("name") or "")
        if tool not in {"read_file", "read"}:
            continue
        path = ev.get("path") or ev.get("file") or ""
        result = ev.get("result") or ev.get("output") or ev.get("content") or ""
        reads.append({"path": _norm_path(str(path)), "result": str(result)})
    return reads


def adjudicate(
    *,
    kind: str,
    gold: str,
    locator: dict,
    world_files: dict[str, str],
    tool_trace: list[dict],
) -> dict:
    """Return GT in {SUCCESS, FAIL, INDETERMINATE}. Ignores last-text."""
    del world_files
    op = locator.get("op")
    reads = _read_events(tool_trace)
    live = live_paths(locator)
    stale = stale_path(locator)
    sources = source_paths(locator)

    live_gold_reads = [
        r for r in reads if r["path"] in live and _gold_in_text(kind, gold, r["result"])
    ]
    live_any_reads = [r for r in reads if r["path"] in live]
    stale_reads = [r for r in reads if stale and r["path"] == stale]

    if op in {"sum_join", "count_join"}:
        read_sources = {r["path"] for r in reads}
        if not set(sources).issubset(read_sources):
            return {"gt": "INDETERMINATE", "cause": "compute_tally_sources_unread"}
        joined_evidence = all(
            any(src in r["path"] or r["path"] == src for r in reads) for src in sources
        )
        if not joined_evidence:
            return {"gt": "INDETERMINATE", "cause": "compute_tally_incomplete"}
        return {"gt": "SUCCESS", "cause": "compute_tally_sources_read"}

    if live_gold_reads:
        if op == "live_not_stale" and stale_reads and not live_any_reads:
            return {"gt": "INDETERMINATE", "cause": "reconcile_stale_only"}
        if op == "live_not_stale" and stale_reads and not live_gold_reads:
            return {"gt": "INDETERMINATE", "cause": "reconcile_no_live_gold"}
        return {"gt": "SUCCESS", "cause": "live_gold_read"}

    if not live_any_reads:
        competing = []
        for r in reversed(reads):
            if r["path"] in live:
                continue
            toks = _same_kind_non_gold(kind, gold, r["result"])
            if len(set(toks)) == 1:
                competing.append(r)
                break
        if competing and not live_any_reads:
            return {"gt": "FAIL", "cause": "competing_read_without_live"}

    return {"gt": "INDETERMINATE", "cause": "otherwise"}
