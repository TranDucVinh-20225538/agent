#!/usr/bin/env python3
"""P3-1: the repaired measurement instrument, and the gates that must pass before it runs.

Pre-registered by paper/paper3_observation_grounded/P3_1_REPAIR_SPEC.md, frozen at
b6edbba with amendment A-1 at fa4a642. This file implements that spec and does not
extend it. Where implementation forced a decision the spec had left ambiguous, the
decision is marked SPEC-NOTE and must be recorded as an amendment, never silently taken.

Nothing here modifies the frozen extractor, protocol/matching.py, the gold lock, any
archive or any trajectory. The four repairs are applied by patching a *copy* of the
frozen module's attributes inside a context manager; the FROZEN configuration patches
nothing at all, which is what makes the parity gate exact rather than approximate.

Order is enforced, not suggested:

    parity  -> synthetic -> run

    p3_1_repair.py parity        # FROZEN must reproduce 0.6/0.7 exactly, or abort
    p3_1_repair.py synthetic     # all 10 fixtures must meet their required outcome
    p3_1_repair.py run           # only legal after both gates have passed

`run` refuses to proceed unless parity and synthetic have both been run and passed in
this same invocation chain, recorded in out/p3_1_gates.json.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "paper" / "paper2_counterfactual_eval" / "protocol"))

import study2_hatd_extract as ex  # noqa: E402  the frozen extractor, imported not copied
from matching import Kind, match_value  # noqa: E402

GATES = ROOT / "out" / "p3_1_gates.json"
RECALL_AUDIT = ROOT / "out" / "p3_0_recall_audit.jsonl"
IDENT_AUDIT = ROOT / "out" / "p3_0_identification_audit.jsonl"

CONFIGS = ["FROZEN", "R-AGG", "R-SCOPE", "R-CMP", "R-CHAN", "ALL"]

# 0.6 baseline, frozen in spec 1.1. Parity is measured against these.
BASELINE_CATEGORIES = {"MATCH": 20, "RECALL_MISS": 39, "ABSENT": 61, "VACUOUS_GOLD": 14, "ANOMALY": 0}
BASELINE_ROWS = 134
BASELINE_LEGS = 57


# ---------------------------------------------------------------------------
# R1 normalisation, imported in spirit from P3_0_RECALL_AUDIT_SPEC 4.
# Re-stated here because 0.6's driver defined it inline; the definition is
# identical and the parity gate does not depend on it (R1 is only used by R-CMP).
# ---------------------------------------------------------------------------
_MD = str.maketrans({c: None for c in "*_`#"} | {"\u2013": "-", "\u2014": "-"})


def norm_r1(s: Any) -> str:
    t = str(s).translate(_MD).casefold()
    t = re.sub(r"\s+", " ", t).strip()
    return t.rstrip(".")


# ---------------------------------------------------------------------------
# R-AGG -- unanimity replaced by plurality over the frozen equivalence classes.
# ---------------------------------------------------------------------------
def _frozen_filter(vals: list[Any]) -> list[Any]:
    """Exactly the filtering _unique_or_none performs before deciding."""
    norm: list[Any] = []
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
    return norm


def _group_key(v: Any) -> Any:
    """The frozen equivalence relation: Decimal equality, else casefolded string."""
    if isinstance(v, Decimal):
        return v
    return str(v).casefold()


def plurality_or_none(vals: list[Any]) -> Any:
    norm = _frozen_filter(vals)
    if not norm:
        return None
    groups: dict[Any, list[Any]] = {}
    for v in norm:
        g = groups.setdefault(_group_key(v), [0, v])
        g[0] += 1
    top = max(g[0] for g in groups.values())
    winners = [g[1] for g in groups.values() if g[0] == top]
    if len(winners) != 1:
        return None  # exact tie for the modal group -> abstain, per spec 2 R-AGG
    return winners[0]


# ---------------------------------------------------------------------------
# R-SCOPE -- candidate scanning over the whole answer.
#
# SPEC-NOTE 1. The spec calls the frozen scope "the +-120-character label window".
# The frozen source has no such single window: extract_money scans
# text[m.end():m.end()+100], extract_int +80, extract_entity m.start()..m.end()+160
# plus a line-based branch, and only extract_date uses _window(), which is itself
# asymmetric at -40/+120. The *rule* R-SCOPE states is unaffected -- it replaces
# whatever local slice the frozen code took with the whole answer -- but the spec's
# description of the baseline is wrong and is corrected by amendment.
#
# SPEC-NOTE 2. "Whole answer" is read as the entire answer string, not "from the label
# to the end". The spec fixes this by cross-reference: "This is the scope of rule R1",
# and R1 in 0.6 was presence over the entire string. Consequence, deliberate and
# already priced by fixture S5: the pick becomes the first candidate in the document.
#
# A label hit is still required. With no label match the candidate list is empty and
# the result is None, so M2 rows cannot be recovered by R-SCOPE -- the K3 leakage
# guard holds by construction.
# ---------------------------------------------------------------------------
def scope_money(text: str, labels: list[str]) -> Optional[Decimal]:
    found: list[Decimal] = []
    for lab in labels:
        for _ in re.finditer(lab, text, re.IGNORECASE):
            after = re.split(r"\n\s*Breakdown", text, maxsplit=1, flags=re.I)[0]
            ms = ex.parse_moneys(after)
            if ms:
                found.append(ms[0])
    return ex._unique_or_none(found)


def scope_int(text: str, labels: list[str]) -> Optional[int]:
    found: list[int] = []
    for lab in labels:
        for _ in re.finditer(lab, text, re.IGNORECASE):
            ints = [int(x.group(1)) for x in ex.INT_RE.finditer(text)]
            if ints:
                found.append(ints[0])
    u = ex._unique_or_none(found)
    return int(u) if u is not None else None


def scope_date(text: str, labels: list[str]) -> Optional[str]:
    found: list[str] = []
    for lab in labels:
        for _ in re.finditer(lab, text, re.IGNORECASE):
            found.extend(ex._DATE_RE.findall(text))
    return ex._unique_or_none(found)


def scope_entity(text: str, labels: list[str]) -> Optional[str]:
    """Frozen extract_entity with both 160-char slices widened to the whole answer.

    The line-based branch uses absolute positions and is unchanged, so it is
    reproduced verbatim rather than paraphrased.
    """
    junk = {"on file", "on", "file", "name", "the", "a", "code", "host", "name on file"}
    found: list[str] = []
    confs: list[str] = []
    for lab in labels:
        for m in re.finditer(lab, text, re.IGNORECASE):
            win = text
            confs.extend(ex._CONF_RE.findall(win))
            found.extend(ex._EMAIL_RE.findall(win))
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
                    confs.extend(ex._CONF_RE.findall(tail))
            after = text
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
                confs.extend(ex._CONF_RE.findall(piece))
                break
    if confs:
        return ex._unique_or_none(confs)
    cleaned = []
    for x in found:
        x = str(x).strip().strip(".")
        if not x or x.casefold() in junk or x.replace(",", "").replace(".", "").isdigit():
            continue
        if len(x) < 4:
            continue
        cleaned.append(x)
    return ex._unique_or_none(cleaned)


# ---------------------------------------------------------------------------
# R-CHAN -- markup span deletion. Unterminated opener deletes to end of text.
# ---------------------------------------------------------------------------
_OPENERS = ["<function", "<tool"]


def chan_clean(text: str) -> str:
    out = text
    changed = True
    while changed:
        changed = False
        low = out.lower()
        for op in _OPENERS:
            i = low.find(op)
            if i < 0:
                continue
            closer = "</" + op[1:]
            j = low.find(closer, i)
            if j >= 0:
                k = out.find(">", j)
                end = (k + 1) if k >= 0 else len(out)
            else:
                m = out.find("/>", i)
                nxt = out.find("<", i + 1)
                if m >= 0 and (nxt < 0 or m < nxt):
                    end = m + 2
                else:
                    end = len(out)  # unterminated opener -> delete to end
            out = out[:i] + out[end:]
            changed = True
            break
    return out


# ---------------------------------------------------------------------------
# R-CMP -- one-directional containment for categorical/entity only.
# ---------------------------------------------------------------------------
def match_with_config(spec: dict[str, Any], gold: Any, reported: Any, cfg: set[str]) -> bool:
    if gold is None or reported is None:
        return False
    kind = Kind(spec["kind"])
    try:
        if kind is Kind.STATE:
            kk = {k: Kind(v) for k, v in (spec.get("key_kinds") or {}).items()}
            if not isinstance(gold, dict) or not isinstance(reported, dict):
                return False
            return match_value(kind, gold, reported, key_kinds=kk)
        if match_value(kind, gold, reported):
            return True
    except Exception:
        return False
    if "R-CMP" in cfg and kind in (Kind.CATEGORICAL, Kind.ENTITY):
        g, r = norm_r1(gold), norm_r1(reported)
        return bool(g) and g in r
    return False


# ---------------------------------------------------------------------------
# Configuration application. FROZEN patches nothing.
# ---------------------------------------------------------------------------
class Configured:
    def __init__(self, cfg: set[str]):
        self.cfg = cfg
        self.saved: dict[str, Any] = {}

    def __enter__(self):
        if "R-AGG" in self.cfg:
            self.saved["_unique_or_none"] = ex._unique_or_none
            ex._unique_or_none = plurality_or_none
        if "R-SCOPE" in self.cfg:
            for name, fn in (("extract_money", scope_money), ("extract_int", scope_int),
                             ("extract_date", scope_date), ("extract_entity", scope_entity)):
                self.saved[name] = getattr(ex, name)
                setattr(ex, name, fn)
        return self

    def __exit__(self, *a):
        for name, fn in self.saved.items():
            setattr(ex, name, fn)
        self.saved.clear()
        return False


def config_set(name: str) -> set[str]:
    if name == "FROZEN":
        return set()
    if name == "ALL":
        return {"R-AGG", "R-SCOPE", "R-CMP", "R-CHAN"}
    return {name}


def extract_for(task: str, cid: str, kind: str, answer: str, cfg: set[str]) -> Any:
    text = chan_clean(answer) if "R-CHAN" in cfg else answer
    return ex.extract_component(task, cid, kind, text)


# ---------------------------------------------------------------------------
# Gate 1: parity. FROZEN must reproduce 0.6/0.7 exactly.
# ---------------------------------------------------------------------------
def gate_parity() -> bool:
    if not RECALL_AUDIT.exists():
        print(f"ABORT: {RECALL_AUDIT} not found. Parity requires the 0.6 record and the "
              f"Study 2 archive it points at; run this on the host.", file=sys.stderr)
        return False
    rows = [json.loads(l) for l in RECALL_AUDIT.read_text().splitlines() if l.strip()]
    print(f"0.6 rows loaded            : {len(rows)}")
    if len(rows) != BASELINE_ROWS:
        print(f"ABORT: expected {BASELINE_ROWS} rows, got {len(rows)}", file=sys.stderr)
        return False
    cats: dict[str, int] = {}
    for r in rows:
        cats[r["category"]] = cats.get(r["category"], 0) + 1
    if cats != BASELINE_CATEGORIES:
        print(f"ABORT: category counts {cats} != baseline {BASELINE_CATEGORIES}", file=sys.stderr)
        return False
    legs = {(r["lane"], r["task"], r["leg"]) for r in rows}
    if len(legs) != BASELINE_LEGS:
        print(f"ABORT: expected {BASELINE_LEGS} legs, got {len(legs)}", file=sys.stderr)
        return False
    print(f"category counts            : {cats}  OK")
    print(f"distinct legs              : {len(legs)}  OK")

    lock = ex.load_lock()
    bad: list[str] = []
    checked = 0
    with Configured(set()):
        for r in rows:
            traj = Path(r["traj"])
            if not traj.exists():
                print(f"ABORT: trajectory not reachable: {traj}\n"
                      f"       Parity must run where the Study 2 archive lives.", file=sys.stderr)
                return False
            answer = ex.final_answer_from_traj(traj)
            guest = ex.load_guest(Path(r["guest"]))
            spec = (lock.get("components") or {}).get(r["task"], {}).get(r["component"]) or {}
            gold = ex.gold_for_component(guest, r["task"], r["component"], lock)
            rep = extract_for(r["task"], r["component"], spec.get("kind"), answer, set())
            got = match_with_config(spec, gold, rep, set())
            if ex._jsonable(gold) != r["gold"]:
                bad.append(f"gold {r['lane']}/{r['task']}/{r['leg']}/{r['component']}: "
                           f"{ex._jsonable(gold)!r} != recorded {r['gold']!r}")
            if ex._jsonable(rep) != r.get("reported"):
                bad.append(f"reported {r['lane']}/{r['task']}/{r['leg']}/{r['component']}: "
                           f"{ex._jsonable(rep)!r} != recorded {r.get('reported')!r}")
            if bool(got) != bool(r.get("matched")):
                bad.append(f"matched {r['lane']}/{r['task']}/{r['leg']}/{r['component']}: "
                           f"{got} != recorded {r.get('matched')}")
            checked += 1
    print(f"rows replayed under FROZEN : {checked}")
    if bad:
        print(f"\nPARITY FAILED: {len(bad)} mismatches. The frozen instrument is NOT to be "
              f"'fixed'; the wrapper is wrong.", file=sys.stderr)
        for b in bad[:40]:
            print("  !", b, file=sys.stderr)
        return False
    print("PARITY PASSED: FROZEN reproduces every gold, reported and matched value of 0.6.")
    return True


# ---------------------------------------------------------------------------
# Gate 2: the synthetic suite, spec 5.2, verbatim.
# ---------------------------------------------------------------------------
def FILL(n: int) -> str:
    unit = "the account notes contain no further figures. "
    return (unit * (n // len(unit) + 2))[:n]


FIXTURES = [
    dict(id="S1", req=(False, True,  "value"), target="R-AGG", sign="+", cid="settlement_total", kind="money_usd", gold="4820.50",
         text=("Settlement total: $4,820.50." + FILL(250) + "Settlement total confirmed at $4,820.50."
               + FILL(250) + "An older draft lists settlement total $3,910.00 (stale)."),
         require="FROZEN abstains; R-AGG matches"),
    dict(id="S2", req=(False, False, "value"), target="R-AGG", sign="-", cid="payout_total", kind="money_usd", gold="1205.00",
         text=("Payout total: $1,205.00." + FILL(250) + "Payout total shown as $990.00."
               + FILL(250) + "Payout total again $990.00."),
         require="FROZEN abstains; R-AGG reports a wrong value (confident-wrong caused by the repair)"),
    dict(id="S3", req=(False, False, "none"), target="R-AGG", sign="=", cid="transfer_total", kind="money_usd", gold="700.00",
         text=("Transfer total $700.00." + FILL(250) + "Transfer total $700.00." + FILL(250)
               + "Transfer total $512.00." + FILL(250) + "Transfer total $512.00."),
         require="both abstain (tie rule)"),
    dict(id="S4", req=(False, True,  "value"), target="R-SCOPE", sign="+", cid="rebate_total", kind="money_usd", gold="318.75",
         text=("Rebate total is stated below." + FILL(260) + "The credited figure is $318.75."),
         require="FROZEN abstains; R-SCOPE matches"),
    dict(id="S5", req=(True,  False, "value"), target="R-SCOPE", sign="-", cid="closing_balance", kind="money_usd", gold="2450.00",
         text=("Unrelated invoice total $77.10." + FILL(260) + "Closing balance: $2,450.00."),
         require="FROZEN matches; R-SCOPE reports a wrong value"),
    dict(id="S6", req=(False, True,  "value"), target="R-CMP", sign="+", cid="lodging_site", kind="categorical", gold="Cedarline Lodge",
         text="Lodging site Cedarline Lodge, amenities Pool, Wifi, Parking.",
         require="FROZEN misses; R-CMP matches"),
    dict(id="S7", req=(False, True,  "value"), target="R-CMP", sign="-", cid="lodging_site", kind="categorical", gold="Cedar Lodge",
         text="Lodging site Cedar Lodge Annex.",
         require="FROZEN misses correctly; R-CMP false-positives"),
    dict(id="S8", req=(False, False, "any"), target="R-CMP", sign="=", cid="lodging_site", kind="categorical",
         gold="Harbour Point (North Wing)",
         text="Lodging site Harbour Point (North Wing).",
         require="neither matches (one-directional asymmetry)"),
    dict(id="S9", req=(True,  False, "none"), target="R-CHAN", sign="+", cid="wire_total", kind="money_usd", gold="6100.00",
         text=('I could not retrieve the figure.'
               '<function=lookup>{"wire total": "$6,100.00"}</function>'),
         require="FROZEN matches spuriously; R-CHAN abstains"),
    dict(id="S10", req=(True,  False, "none"), target="R-CHAN", sign="-", cid="wire_total", kind="money_usd", gold="6100.00",
         text=('<function=lookup>{"q": "wire"}' ' The wire total is $6,100.00.'),
         require="FROZEN matches; R-CHAN loses the value"),
]

TASK = "synthetic-s000"


def _fix_eval(fx: dict[str, Any], cfgname: str) -> tuple[Any, bool]:
    cfg = config_set(cfgname)
    gold: Any = Decimal(fx["gold"]) if fx["kind"] in ("money_usd", "integer") else fx["gold"]
    spec = {"kind": fx["kind"]}
    with Configured(cfg):
        rep = extract_for(TASK, fx["cid"], fx["kind"], fx["text"], cfg)
    return rep, match_with_config(spec, gold, rep, cfg)


def gate_synthetic() -> bool:
    print(f"{'id':4s} {'target':8s} {'sg':2s} {'FROZEN rep':>22s} {'m':1s}   {'repaired rep':>26s} {'m':1s}  verdict")
    print("-" * 108)
    fails = []
    for fx in FIXTURES:
        fr, fm = _fix_eval(fx, "FROZEN")
        rr, rm = _fix_eval(fx, fx["target"])
        want_f, want_r, want_rep = fx["req"]
        ok = (fm is want_f) and (rm is want_r)
        if want_rep == "value":
            ok = ok and rr is not None
        elif want_rep == "none":
            ok = ok and rr is None
        if not ok:
            fails.append(fx["id"])
        print(f"{fx['id']:4s} {fx['target']:8s} {fx['sign']:2s} {str(fr)[:22]:>22s} {int(fm)}   "
              f"{str(rr)[:26]:>26s} {int(rm)}  {'OK' if ok else 'MISMATCH'}")
    print()
    if fails:
        print(f"K2 FIRES: {len(fails)} fixture(s) did not meet the required outcome: {fails}")
        print("Per spec 7 K2: fix the implementation, or amend the specification BEFORE the")
        print("archive is touched. Do not proceed to `run`.")
        return False
    print("SYNTHETIC PASSED: all 10 fixtures met their required outcome.")
    return True


def _write_gate(name: str, ok: bool) -> None:
    d = json.loads(GATES.read_text()) if GATES.exists() else {}
    d[name] = ok
    GATES.parent.mkdir(parents=True, exist_ok=True)
    GATES.write_text(json.dumps(d, indent=1))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["parity", "synthetic", "run"])
    a = ap.parse_args()
    if a.cmd == "parity":
        ok = gate_parity()
        _write_gate("parity", ok)
        return 0 if ok else 3
    if a.cmd == "synthetic":
        ok = gate_synthetic()
        _write_gate("synthetic", ok)
        return 0 if ok else 4
    g = json.loads(GATES.read_text()) if GATES.exists() else {}
    if not (g.get("parity") and g.get("synthetic")):
        print(f"ABORT: `run` requires both gates passed. out/p3_1_gates.json = {g}", file=sys.stderr)
        print("Order is parity -> synthetic -> run. No exceptions.", file=sys.stderr)
        return 5
    print("both gates passed; the repair run is not implemented in this commit by design.")
    print("Implementing it now would precede the amendment that records SPEC-NOTE 1 and 2.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
