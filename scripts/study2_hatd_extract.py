#!/usr/bin/env python3
"""Study 2 hat-D extractor (DESIGN.md §3.1). No LLM. Fail-closed.

Last traj.jsonl response → reported value | None per (task, component_id).
Gold from per-leg guest.json via out/study2_gold_path_lock.json.
Matching is NOT done here (protocol/matching.py).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[1]
GOLD_LOCK = ROOT / "out" / "study2_gold_path_lock.json"
THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)
# Money: $1,975.00 or 1975.59, optional leading minus. Avoid SM-88431.
MONEY_RE = re.compile(
    r"(?<![A-Z])-?\$?\s*(\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?",
    re.IGNORECASE,
)
INT_RE = re.compile(r"(?<![\d.,])(\d{1,6})(?![\d.,])")

# Label windows: first match wins if all captured moneys/ints/entities agree.
LABELS: dict[tuple[str, str], list[str]] = {
    ("aggregation-f020", "card_balance"): [r"card balance", r"credit card", r"sapphire", r"balance due"],
    ("aggregation-f020", "batbucks_cash"): [r"batbucks", r"cash available", r"portfolio cash"],
    ("aggregation-f020", "card_limit"): [r"credit limit", r"card limit"],
    ("aggregation-f037", "top_sender"): [r"top (inbox )?sender", r"most (emails|messages)"],
    ("aggregation-f037", "top_sender_count"): [r"top_sender_count", r"message count", r"email count"],
    ("contradiction-f004", "batbucks_gme_shares"): [r"batbucks.*gme", r"gme shares", r"\bshares\b"],
    ("contradiction-f004", "gme_avg_cost"): [r"avg(erage)? cost", r"average cost"],
    ("contradiction-f006", "jamaica_hotel_total"): [r"jamaica", r"montego"],
    ("contradiction-f006", "barbados_hotel_total"): [r"barbados"],
    ("contradiction-f006", "credit_headroom"): [r"headroom", r"available credit"],
    ("counterfactual-f005", "gme_shares"): [r"gme shares", r"\bshares\b"],
    ("counterfactual-f005", "liquid_bank"): [r"checking", r"liquid", r"bank"],
    ("counterfactual-f005", "gme_avg_cost"): [r"avg(erage)? cost"],
    ("counterfactual-f010", "liquid_cash"): [r"checking \+ savings", r"liquid", r"available balance", r"combined"],
    ("counterfactual-f010", "n_upcoming_flights"): [r"upcoming (dinoco )?flights", r"\bflights\b"],
    ("counterfactual-f013", "gringotts_savings"): [r"gringotts savings", r"savings"],
    ("counterfactual-f013", "batbucks_dividends"): [r"dividend"],
    ("counterfactual-f013", "oddsmarket_balance"): [r"oddsmarket", r"odds market"],
    ("preference_inference-f010", "fastest_sender"): [r"fastest sender", r"fastest correspondent", r"fastest"],
    ("preference_inference-f010", "designated_sender_latency"): [r"latency", r"reply time", r"minutes"],
    ("preference_inference-f014", "designated_booking_property"): [r"property", r"hotel", r"radisson", r"booking"],
    ("preference_inference-f014", "designated_booking_total"): [r"total", r"price"],
    ("retrieval-f002", "sandals_jamaica_confirmation"): [r"confirmation"],
    ("retrieval-f009", "nyc_hotel_confirmation"): [r"greenwich", r"hotel confirmation"],
    ("retrieval-f009", "nyc_flight_confirmation"): [r"flight confirmation", r"dinoco", r"\bDN-"],
    ("retrieval-f009", "nyc_checkin_date"): [r"check-?in"],
    ("retrieval-f010", "jamaica_trip_total"): [r"total cost of the trip", r"trip total", r"\btotal:"],
    ("retrieval-f010", "host_name"): [r"host name", r"hosted by", r"\bhost\b"],
    ("retrieval-f017", "total_invested"): [r"total invested", r"invested"],
    ("retrieval-f017", "n_open_positions"): [r"open positions", r"\bn_open\b", r"positions"],
}


def strip_think(text: str) -> str:
    if not text:
        return ""
    return THINK_RE.sub("", text).strip()


def final_answer_from_traj(traj_path: Path) -> str:
    last = None
    with traj_path.open() as f:
        for line in f:
            if line.strip():
                last = line
    if not last:
        return ""
    try:
        obj = json.loads(last)
    except json.JSONDecodeError:
        return ""
    return strip_think(str(obj.get("response") or ""))


def _parse_jsonish(x: Any) -> Any:
    if isinstance(x, str):
        s = x.strip()
        if s.startswith("[") or s.startswith("{"):
            try:
                return json.loads(s)
            except json.JSONDecodeError:
                return x
    return x


def _parse_extras(raw: dict[str, Any], key: str) -> list[dict[str, Any]]:
    extras = []
    for e in raw.get(key) or []:
        ee = dict(e)
        ee["result"] = _parse_jsonish(e.get("result"))
        extras.append(ee)
    return extras


def canonicalize_guest(raw: dict[str, Any]) -> dict[str, Any]:
    """Bind lock paths probe_before / extra_probes to this leg's world.

    G0 guest files store the world in probe_before + extra_probes.
    Injected G1 files keep the pre-inject snapshot there and put the world
    the agent actually faced in probe_after + extra_probes_after.
    Gold is always the world after inject when those keys exist.
    Never copies the other leg's guest.
    """
    out = dict(raw)
    pb = _parse_jsonish(out.get("probe_before"))
    pa = _parse_jsonish(out.get("probe_after")) if "probe_after" in out else None
    extras = _parse_extras(out, "extra_probes")
    extras_after = _parse_extras(out, "extra_probes_after") if "extra_probes_after" in out else []
    out["_probe_preinject"] = pb
    out["_injected"] = "probe_after" in raw
    out["probe_before"] = pa if "probe_after" in raw else pb
    out["extra_probes"] = extras_after if "extra_probes_after" in raw else extras
    return out


def load_guest(path: Path) -> dict[str, Any]:
    return canonicalize_guest(json.loads(path.read_text()))


def _walk(root: Any, parts: list[str]) -> Any:
    cur = root
    i = 0
    while i < len(parts):
        p = parts[i]
        if p == "sum" and i + 1 < len(parts):
            field = parts[i + 1]
            if not isinstance(cur, list):
                return None
            vals = []
            for row in cur:
                if isinstance(row, dict) and field in row:
                    vals.append(Decimal(str(row[field])))
            return sum(vals) if vals else None
        if p.startswith("filter.") or (p.startswith("filter") and False):
            pass
        if p.startswith("filter."):
            spec = p[len("filter.") :]  # property_name~montego
            if "~" not in spec or not isinstance(cur, list):
                return None
            field, needle = spec.split("~", 1)
            hits = [row for row in cur if isinstance(row, dict) and needle.casefold() in str(row.get(field, "")).casefold()]
            if len(hits) != 1:
                return None
            cur = hits[0]
            i += 1
            continue
        if cur is None:
            return None
        if p.isdigit():
            idx = int(p)
            if not isinstance(cur, list) or idx >= len(cur):
                return None
            cur = cur[idx]
        else:
            if not isinstance(cur, dict) or p not in cur:
                return None
            cur = cur[p]
        i += 1
    return cur


def resolve_gold_path(guest: dict[str, Any], path: Optional[str]) -> Any:
    if not path:
        return None
    # special: extra_probes.0.result.where.departure_date==probe_before.0.check_in.confirmation_code
    if ".where." in path and "==" in path:
        left, rest = path.split(".where.", 1)
        cond, field = rest.rsplit(".", 1)
        # cond: departure_date==probe_before.0.check_in
        ck, rhs = cond.split("==", 1)
        rows = _walk(guest, left.split("."))
        rhs_val = _walk(guest, rhs.split("."))
        if not isinstance(rows, list) or rhs_val is None:
            return None
        hits = [r for r in rows if isinstance(r, dict) and str(r.get(ck)) == str(rhs_val)]
        if len(hits) != 1:
            return None
        return hits[0].get(field)
    if path.startswith("probe_before.filter."):
        # probe_before.filter.property_name~montego.confirmation_code
        rest = path[len("probe_before.filter.") :]
        spec, field = rest.rsplit(".", 1)
        fname, needle = spec.split("~", 1)
        rows = guest.get("probe_before")
        if not isinstance(rows, list):
            return None
        hits = [r for r in rows if isinstance(r, dict) and needle.casefold() in str(r.get(fname, "")).casefold()]
        if len(hits) != 1:
            return None
        return hits[0].get(field)
    return _walk(guest, path.split("."))


def gold_for_component(guest: dict[str, Any], task: str, component_id: str, lock: dict[str, Any]) -> Any:
    spec = (lock.get("components") or {}).get(task, {}).get(component_id) or {}
    val = resolve_gold_path(guest, spec.get("path"))
    if spec.get("kind") == "state" and isinstance(val, dict):
        keys = spec.get("key_kinds") or {}
        return {k: val.get(k) for k in keys}
    return val


def _to_decimal(tok: str) -> Optional[Decimal]:
    try:
        return Decimal(tok.replace(",", "").replace("$", "").replace(" ", ""))
    except (InvalidOperation, ValueError):
        return None


def parse_moneys(text: str) -> list[Decimal]:
    out = []
    for m in MONEY_RE.finditer(text):
        v = _to_decimal(m.group(0))
        if v is not None:
            out.append(v)
    return out


def _window(text: str, label: str, radius: int = 120) -> list[str]:
    wins = []
    for m in re.finditer(label, text, re.IGNORECASE):
        a = max(0, m.start() - 40)
        b = min(len(text), m.end() + radius)
        wins.append(text[a:b])
    return wins


def _unique_or_none(vals: list[Any]) -> Any:
    norm = []
    for v in vals:
        if v is None:
            continue
        if isinstance(v, Decimal):
            norm.append(v)
        elif isinstance(v, str):
            s = v.strip()
            if s:
                norm.append(s)
        else:
            norm.append(v)
    if not norm:
        return None
    first = norm[0]
    for x in norm[1:]:
        if isinstance(first, Decimal) and isinstance(x, Decimal):
            if first != x:
                return None
        elif str(first).casefold() != str(x).casefold():
            return None
    return first


def extract_money(text: str, labels: list[str]) -> Optional[Decimal]:
    found: list[Decimal] = []
    for lab in labels:
        for m in re.finditer(lab, text, re.IGNORECASE):
            after = text[m.end() : m.end() + 100]
            after = re.split(r"\n\s*Breakdown", after, maxsplit=1, flags=re.I)[0]
            ms = parse_moneys(after)
            if ms:
                found.append(ms[0])
    return _unique_or_none(found)


def extract_int(text: str, labels: list[str]) -> Optional[int]:
    found: list[int] = []
    for lab in labels:
        for m in re.finditer(lab, text, re.IGNORECASE):
            after = text[m.end() : m.end() + 80]
            ints = [int(x.group(1)) for x in INT_RE.finditer(after)]
            if ints:
                found.append(ints[0])
    u = _unique_or_none(found)
    return int(u) if u is not None else None


_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_CONF_RE = re.compile(r"\b[A-Z]{2,}[-–][A-Z0-9]{3,}\b")
_DATE_RE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")


def extract_entity(text: str, labels: list[str]) -> Optional[str]:
    junk = {"on file", "on", "file", "name", "the", "a", "code", "host", "name on file"}
    found: list[str] = []
    confs: list[str] = []
    for lab in labels:
        for m in re.finditer(lab, text, re.IGNORECASE):
            win = text[m.start() : m.end() + 160]
            confs.extend(_CONF_RE.findall(win))
            found.extend(_EMAIL_RE.findall(win))
            line_end = text.find("\n", m.end())
            if line_end == -1:
                line_end = len(text)
            line_start = text.rfind("\n", 0, m.start())
            line2 = re.sub(r"[*_`#]", "", text[line_start + 1 : line_end])
            if ":" in line2:
                tail = line2.split(":", 1)[1].strip()
                tail = re.sub(r"[*_`]", "", tail).strip()
                if tail and not tail.startswith("$"):
                    found.append(re.split(r"[(\[]", tail)[0].strip())
                    confs.extend(_CONF_RE.findall(tail))
            after = text[m.end() : m.end() + 160]
            nxt = [re.sub(r"[*_`#]", "", ln).strip() for ln in after.splitlines() if ln.strip()]
            for cand in nxt:
                if cand.startswith("$"):
                    continue
                piece = re.split(r"[(\[]", cand)[0].strip()
                if piece.casefold() in junk or "on file" in piece.casefold():
                    continue
                if len(piece) < 4:
                    continue
                found.append(piece)
                confs.extend(_CONF_RE.findall(piece))
                break
    if confs:
        return _unique_or_none(confs)
    cleaned = []
    for x in found:
        x = str(x).strip().strip(".")
        if not x or x.casefold() in junk or x.replace(",", "").replace(".", "").isdigit():
            continue
        if len(x) < 4:
            continue
        cleaned.append(x)
    return _unique_or_none(cleaned)


def extract_date(text: str, labels: list[str]) -> Optional[str]:
    found = []
    for lab in labels:
        for win in _window(text, lab):
            found.extend(_DATE_RE.findall(win))
    return _unique_or_none(found)


def extract_state_gme_yes(text: str) -> Optional[dict[str, Any]]:
    shares = extract_int(text, [r"oddsmarket", r"yes", r"position", r"\bshares\b"])
    status = None
    low = text.casefold()
    if "active" in low:
        status = "active"
    elif "settled" in low:
        status = "settled"
    if shares is None or status is None:
        return None
    return {"shares": shares, "status": status}


def extract_component(task: str, component_id: str, kind: str, text: str) -> Any:
    labels = LABELS.get((task, component_id), [re.escape(component_id.replace("_", " "))])
    if task == "contradiction-f004" and component_id == "oddsmarket_gme_yes":
        return extract_state_gme_yes(text)
    if kind == "money_usd":
        return extract_money(text, labels)
    if kind == "integer":
        return extract_int(text, labels)
    if kind == "categorical" and "date" in component_id:
        return extract_date(text, labels)
    if kind in ("entity", "categorical"):
        return extract_entity(text, labels)
    if kind == "state":
        return None
    return None


def load_lock(path: Path = GOLD_LOCK) -> dict[str, Any]:
    return json.loads(path.read_text())


def find_guest(leg_dir: Path) -> Optional[Path]:
    hits = list(leg_dir.glob("*.guest.json"))
    return hits[0] if hits else None


def find_traj(leg_dir: Path) -> Optional[Path]:
    hits = sorted(leg_dir.rglob("traj.jsonl"))
    return hits[0] if hits else None


def extract_leg(task: str, leg_dir: Path, lock: dict[str, Any]) -> dict[str, Any]:
    comps = (lock.get("components") or {}).get(task) or {}
    guest_p = find_guest(leg_dir)
    traj_p = find_traj(leg_dir)
    guest = load_guest(guest_p) if guest_p else {}
    answer = final_answer_from_traj(traj_p) if traj_p else ""
    reported = {}
    gold = {}
    for cid, spec in comps.items():
        kind = spec.get("kind")
        gold[cid] = gold_for_component(guest, task, cid, lock)
        reported[cid] = extract_component(task, cid, kind, answer)
    return {
        "task": task,
        "guest": str(guest_p) if guest_p else None,
        "traj": str(traj_p) if traj_p else None,
        "answer_chars": len(answer),
        "gold": {k: _jsonable(v) for k, v in gold.items()},
        "reported": {k: _jsonable(v) for k, v in reported.items()},
    }


def _jsonable(v: Any) -> Any:
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, dict):
        return {kk: _jsonable(vv) for kk, vv in v.items()}
    return v


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["answer", "leg"])
    ap.add_argument("path")
    ap.add_argument("--task", required=False)
    args = ap.parse_args()
    lock = load_lock()
    if args.cmd == "answer":
        text = strip_think(Path(args.path).read_text() if Path(args.path).suffix != ".jsonl" else final_answer_from_traj(Path(args.path)))
        print(text[:2000])
        return 0
    task = args.task
    if not task:
        print("--task required", file=sys.stderr)
        return 2
    print(json.dumps(extract_leg(task, Path(args.path), lock), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
