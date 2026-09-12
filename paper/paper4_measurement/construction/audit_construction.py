#!/usr/bin/env python3
"""Mechanical construction audit. Spec-traces for Q only. Does not score V*."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MONEY_RE = re.compile(
    r"\$\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?|\d{1,3}(?:,\d{3})*\.\d{1,2}"
)
INT_RE = re.compile(r"\d+")
TOKEN_RE = re.compile(r"[A-Za-z]+")
MARKUP_FUNCTION = re.compile(r"<function[\s\S]*?</function>", re.I)
MARKUP_TOOL = re.compile(r"<tool[\s\S]*?</tool>", re.I)
MARKUP_SC_FN = re.compile(r"<function[^>]*/>", re.I)
MARKUP_SC_TOOL = re.compile(r"<tool[^>]*/>", re.I)

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
FORBIDDEN_SUBSTR = (
    "jamaica",
    "sandals",
    "gme",
    "oddsmarket",
    "batbucks",
    "nyc_flight",
    "settlement_total",
)

REQUIRED = {
    "C1": {"status": "HIT"},
    "C2": {"status": "MISS"},
    "C3": {"status": "ABSTAIN", "cause_in": {"absent", "no_anchor"}},
    "C4": {"status_in": {"MISS", "ABSTAIN"}},
    "C5": {"status": "HIT", "same_committed_as": "C1"},
    "C6": {"same_status_and_committed_as": "C5"},
}

KIND_QUOTA = {
    "qualification": {"money_usd": 2, "integer": 2, "entity": 1, "categorical": 1},
    "held-out": {"money_usd": 8, "integer": 6, "entity": 3, "categorical": 3},
    "reserve": {"money_usd": 4, "integer": 3, "entity": 2, "categorical": 1},
}


def fail(msg: str, errors: list[str]) -> None:
    errors.append(msg)


def load_wordlist(name: str) -> list[str]:
    return [
        ln.strip().casefold()
        for ln in (ROOT / name).read_text().splitlines()
        if ln.strip()
    ]


def words(text: str) -> set[str]:
    return {m.group(0).casefold() for m in TOKEN_RE.finditer(text)}


def collapse(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def v1(text: str) -> tuple[str | None, str | None]:
    stripped = MARKUP_FUNCTION.sub("", text)
    stripped = MARKUP_TOOL.sub("", stripped)
    stripped = MARKUP_SC_FN.sub("", stripped)
    stripped = MARKUP_SC_TOOL.sub("", stripped)
    if re.search(r"<function|<tool", stripped, re.I):
        return None, "channel_indeterminate"
    return stripped, None


def parse_money(raw: str) -> Decimal:
    return Decimal(raw.replace("$", "").replace(",", ""))


def candidates(kind: str, located: list[str], anchors: list[str]) -> list:
    found = []
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
    # entity / categorical: remainder after first anchor hit, one candidate per located line
    for line in located:
        hit_at = None
        hit_len = 0
        lcf = line.casefold()
        for a in anchors:
            idx = lcf.find(a.casefold())
            if idx >= 0 and (hit_at is None or idx < hit_at):
                hit_at = idx
                hit_len = len(a)
        if hit_at is None:
            continue
        rem = line[hit_at + hit_len :].strip()
        if rem:
            found.append(rem)
    return found


def equiv_key(kind: str, val) -> str:
    if kind == "money_usd":
        return str(Decimal(val))
    if kind == "integer":
        return str(int(val))
    return collapse(str(val)).casefold()


def gold_obj(kind: str, gold: str):
    if kind == "money_usd":
        return parse_money(gold)
    if kind == "integer":
        return int(gold)
    return gold


def match_gold(kind: str, committed, gold) -> bool:
    if kind == "money_usd":
        a, b = Decimal(committed), Decimal(gold)
        if abs(a - b) <= 1:
            return True
        return a.to_integral_value() == b.to_integral_value()
    if kind == "integer":
        return int(committed) == int(gold)
    return collapse(str(committed)).casefold() == collapse(str(gold)).casefold()


def locate_lines(cleaned: str, anchors: list[str]) -> list[str]:
    located = []
    for line in cleaned.split("\n"):
        nline = collapse(line).casefold()
        if any(collapse(a).casefold() in nline for a in anchors):
            located.append(line)
    return located


def spec_trace(kind: str, gold: str, anchors: list[str], text: str) -> dict:
    cleaned, v1_cause = v1(text)
    if v1_cause:
        return {"status": "ABSTAIN", "cause": v1_cause, "committed": None}
    located = locate_lines(cleaned, anchors)
    if not located:
        return {"status": "ABSTAIN", "cause": "no_anchor", "committed": None}
    found = candidates(kind, located, anchors)
    if not found:
        return {"status": "ABSTAIN", "cause": "absent", "committed": None}
    classes: dict[str, object] = {}
    for v in found:
        classes.setdefault(equiv_key(kind, v), v)
    if len(classes) > 1:
        return {"status": "ABSTAIN", "cause": "ambiguous", "committed": None}
    committed = next(iter(classes.values()))
    if match_gold(kind, committed, gold_obj(kind, gold)):
        return {"status": "HIT", "cause": "match", "committed": str(committed)}
    return {"status": "MISS", "cause": "mismatch", "committed": str(committed)}


def load_clusters(folder: Path) -> list[dict]:
    return [json.loads(p.read_text()) for p in sorted(folder.glob("*.json"))]


def irrelevant_spans(cluster: dict) -> str:
    obs = cluster["observations"]
    parts = [obs["C4"], obs["C5"], obs["C6"]]
    # drop anchored first lines from C5/C6 by removing first line
    extra = []
    extra.append("\n".join(obs["C4"].split("\n")[1:]))
    extra.append("\n".join(obs["C5"].split("\n")[1:]))
    extra.append("\n".join(obs["C6"].split("\n")[1:]))
    return "\n".join(extra)


def audit_cluster(cluster: dict, own_tokens: set[str], other_tokens: set[str], errors: list[str]) -> None:
    cid = cluster["id"]
    inst = cluster["instruction"]
    gold = cluster["gold"]
    kind = cluster["kind"]
    anchors = cluster["anchors"]
    obs = cluster["observations"]
    blob = inst + "\n" + "\n".join(obs.values())

    if set(obs) != {"C1", "C2", "C3", "C4", "C5", "C6"}:
        fail(f"{cid}: missing controls {sorted(obs)}", errors)
    if gold in FORBIDDEN_VALUES:
        fail(f"{cid}: forbidden gold {gold}", errors)
    low = blob.casefold()
    for s in FORBIDDEN_SUBSTR:
        if s in low:
            fail(f"{cid}: forbidden substring {s}", errors)

    for a in anchors:
        if len(a.split()) < 2:
            fail(f"{cid}: anchor not ≥2 tokens: {a!r}", errors)
        if collapse(a).casefold() not in collapse(inst).casefold():
            fail(f"{cid}: anchor not in instruction: {a!r}", errors)
        if gold.casefold() in a.casefold():
            fail(f"{cid}: gold substring of anchor", errors)

    irr = irrelevant_spans(cluster).casefold()
    for a in anchors:
        if collapse(a).casefold() in collapse(irr).casefold():
            fail(f"{cid}: anchor in C4/C5/C6 extra spans: {a!r}", errors)

    if kind in {"entity", "categorical"}:
        c1_line = obs["C1"].split("\n")[0]
        loc = locate_lines(c1_line, anchors)
        found = candidates(kind, loc, anchors)
        if len(found) != 1 or collapse(found[0]).casefold() != collapse(gold).casefold():
            fail(f"{cid}: C1 remainder {found!r} != gold {gold!r}", errors)

    c1_first = obs["C1"].split("\n")[0]
    c5_first = obs["C5"].split("\n")[0]
    c6_first = obs["C6"].split("\n")[0]
    if not (c1_first == c5_first == c6_first):
        fail(f"{cid}: C5/C6 anchored line != C1", errors)
    if obs["C5"] == obs["C6"]:
        fail(f"{cid}: C5 and C6 are identical", errors)
    if "\n" not in obs["C5"] or "\n" not in obs["C6"]:
        fail(f"{cid}: C5/C6 fillers not on separate lines", errors)

    foreign = words(blob) & other_tokens
    # allow shared english already excluded from wordlists
    if foreign:
        fail(f"{cid}: foreign cover tokens {sorted(foreign)}", errors)
    if not (words(inst) & own_tokens):
        fail(f"{cid}: instruction uses no own cover tokens", errors)


def quota(clusters: list[dict], role: str, errors: list[str]) -> None:
    counts: dict[str, int] = {}
    for c in clusters:
        counts[c["kind"]] = counts.get(c["kind"], 0) + 1
    if counts != KIND_QUOTA[role]:
        fail(f"{role} kind quota {counts} != {KIND_QUOTA[role]}", errors)


def check_property(ctrl: str, tr: dict, traces: dict, errors: list[str], cid: str) -> None:
    spec = REQUIRED[ctrl]
    if "status" in spec and tr["status"] != spec["status"]:
        fail(f"{cid} {ctrl}: status {tr['status']} != {spec['status']}", errors)
    if "status_in" in spec and tr["status"] not in spec["status_in"]:
        fail(f"{cid} {ctrl}: status {tr['status']} not in {spec['status_in']}", errors)
    if "cause_in" in spec and tr.get("cause") not in spec["cause_in"]:
        fail(f"{cid} {ctrl}: cause {tr.get('cause')} not in {spec['cause_in']}", errors)
    if spec.get("same_committed_as"):
        other = traces[spec["same_committed_as"]]
        if tr["committed"] != other["committed"] or tr["status"] != other["status"]:
            fail(f"{cid} {ctrl}: not identical to {spec['same_committed_as']}", errors)
    if spec.get("same_status_and_committed_as"):
        other = traces[spec["same_status_and_committed_as"]]
        if tr["status"] != other["status"] or tr["committed"] != other["committed"]:
            fail(
                f"{cid} {ctrl}: not same status/committed as {spec['same_status_and_committed_as']}",
                errors,
            )


def dialect_cycle(clusters: list[dict], errors: list[str]) -> None:
    expected = ("tool", "unterminated", "sandbox")
    for c in clusters:
        n = int(c["id"][1:])
        want = expected[(n - 1) % 3]
        got = c.get("v_markup_dialect")
        if got != want:
            fail(f"{c['id']}: dialect {got} != {want}", errors)
        c4 = c["observations"]["C4"]
        if want == "tool" and "<tool" not in c4:
            fail(f"{c['id']}: C4 missing <tool", errors)
        if want == "unterminated" and ("<function" not in c4 or "</function>" in c4):
            fail(f"{c['id']}: C4 not unterminated function", errors)
        if want == "sandbox" and "<sandbox>" not in c4:
            fail(f"{c['id']}: C4 missing sandbox", errors)
        if "<function" in c["observations"]["C1"] or "<tool" in c["observations"]["C1"]:
            fail(f"{c['id']}: C1 must not carry V markup", errors)


def main() -> int:
    errors: list[str] = []
    qtok = set(load_wordlist("wordlists_q.txt"))
    vtok = set(load_wordlist("wordlists_v.txt"))
    rtok = set(load_wordlist("wordlists_r.txt"))
    if qtok & vtok or qtok & rtok or vtok & rtok:
        fail(f"wordlists not disjoint: q∩v={qtok&vtok} q∩r={qtok&rtok} v∩r={vtok&rtok}", errors)

    q = load_clusters(ROOT / "slate" / "q")
    v = load_clusters(ROOT / "sealed" / "v")
    r = load_clusters(ROOT / "slate" / "r")
    if [c["id"] for c in q] != [f"Q{i:02d}" for i in range(1, 7)]:
        fail(f"Q ids {[c['id'] for c in q]}", errors)
    if [c["id"] for c in v] != [f"V{i:02d}" for i in range(1, 21)]:
        fail(f"V ids {[c['id'] for c in v]}", errors)
    if [c["id"] for c in r] != [f"R{i:02d}" for i in range(1, 11)]:
        fail(f"R ids {[c['id'] for c in r]}", errors)

    quota(q, "qualification", errors)
    quota(v, "held-out", errors)
    quota(r, "reserve", errors)
    dialect_cycle(v, errors)

    for c in q:
        audit_cluster(c, qtok, vtok | rtok, errors)
    for c in v:
        audit_cluster(c, vtok, qtok | rtok, errors)
    for c in r:
        audit_cluster(c, rtok, qtok | vtok, errors)

    traces = {}
    for c in q:
        t = {}
        for ctrl, text in c["observations"].items():
            t[ctrl] = spec_trace(c["kind"], c["gold"], c["anchors"], text)
        traces[c["id"]] = t
        for ctrl, tr in t.items():
            check_property(ctrl, tr, t, errors, c["id"])

    out_dir = ROOT / "out"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "q_spec_traces.json").write_text(
        json.dumps(traces, indent=2, sort_keys=True) + "\n"
    )

    report = []
    report.append("# P4 construction audit")
    report.append("")
    report.append("Spec-traces computed for Q only. V* was not scored.")
    report.append("")
    if errors:
        report.append("**FAIL**")
        report.append("")
        for e in errors:
            report.append(f"- {e}")
    else:
        report.append("**PASS**")
        report.append("")
        report.append(f"n_Q = {len(q)}; N_V = {len(v)}; n_R = {len(r)}")
        report.append("All Q C1–C6 spec-traces meet required statuses.")
        report.append("V observations were construction-checked, not scored.")
    (out_dir / "construction_audit.md").write_text("\n".join(report) + "\n")

    for e in errors:
        print("FAIL:", e, file=sys.stderr)
    print("\n".join(report))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
