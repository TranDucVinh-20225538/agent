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
import hashlib
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
from study2_hatd_apply import match_one  # noqa: E402  the frozen comparison, imported not copied
from matching import Kind  # noqa: E402
import p3_0_identification_audit as idaud  # noqa: E402  0.7's cause classifier, reused

# ---------------------------------------------------------------------------
# Module provenance, checked rather than assumed. 2.0 parity applied to the
# imports themselves.
#
# study2_hatd_apply hardcodes VINH = /data2/hpcshared/Vinh-/agent and inserts
# VINH/scripts at sys.path[0] on import. Two host roots exist -- that module also
# names VINH_FROZEN = /data2/hpcshared/Vinh/agent, which is where the recorded traj
# paths live -- so "the frozen extractor" is not automatically the one in this tree.
# This script happens to import study2_hatd_extract first, which puts it in
# sys.modules before that path insert can take effect, but relying on import order
# is precisely the kind of unstated dependency that has already cost one host run.
# The blob hashes below make it a checked property: a different copy aborts.
# ---------------------------------------------------------------------------
FROZEN_BLOBS = {
    "study2_hatd_extract": "438a4eafb175785376fa714a3cbc1a8564f327ba",
    "study2_hatd_apply": "cafd8a6252febd0bf2fb88b7376884a5c5ff0484",
    # The P3-0 cause classifier. Imported, not reimplemented, for the same reason
    # match_one is: the per-configuration taxonomy must be compared against 0.7's own
    # classifier rather than a look-alike of mine. That makes it load-bearing, so it is
    # pinned too.
    "p3_0_identification_audit": "86820e4a63870256154b7b71c5e1af4e7685bcf8",
}


def git_blob(path: Path) -> str:
    """Reproduce `git hash-object <path>` so the check is externally verifiable."""
    data = path.read_bytes()
    h = hashlib.sha1()
    h.update(b"blob " + str(len(data)).encode() + b"\0")
    h.update(data)
    return h.hexdigest()


def check_provenance() -> None:
    import study2_hatd_apply as ap
    import p3_0_identification_audit as _id
    bad = []
    for mod, want in FROZEN_BLOBS.items():
        p = Path(sys.modules[mod].__file__).resolve()
        got = git_blob(p)
        if got != want:
            bad.append(f"{mod}: loaded {p}\n      blob {got}\n      frozen {want}")
    if bad:
        print("ABORT: a loaded module is not the frozen artifact. Refusing to produce "
              "numbers against an unknown instrument.", file=sys.stderr)
        for b in bad:
            print(f"  - {b}", file=sys.stderr)
        raise SystemExit(6)
    _ = (ap, _id)  # imported for sys.modules registration only

GATES = ROOT / "out" / "p3_1_gates.json"
OUT_RUN = ROOT / "out" / "p3_1_run_development.json"
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
    """The frozen `match_one` is called first, unchanged. R-CMP only ever *adds* a match.

    Wrapping rather than reimplementing matters here: under FROZEN this function is
    exactly `match_one`, so the parity gate compares the frozen comparison against its
    own recorded output rather than against a look-alike of mine.
    """
    if match_one(spec, gold, reported):
        return True
    if "R-CMP" in cfg and gold is not None and reported is not None \
            and Kind(spec["kind"]) in (Kind.CATEGORICAL, Kind.ENTITY):
        g, r = norm_r1(gold), norm_r1(reported)
        return bool(g) and g in r
    return False


# ---------------------------------------------------------------------------
# Configuration application. FROZEN patches nothing.
# ---------------------------------------------------------------------------
# Every aggregation decision made during one extraction, in call order. 0.7's classifier
# needs `filtered` and `returned` per call to separate M1 from M2/M3, so the same
# observation is recorded here. The wrapper returns fn(vals) untouched, and `run` proves
# it is pass-through by re-verifying FROZEN against 0.6 with instrumentation active.
AGG_CALLS: list[dict] = []


def _instrumented(fn):
    def wrapped(vals):
        filtered = _frozen_filter(vals)
        out = fn(vals)
        AGG_CALLS.append({"filtered": filtered, "returned": out})
        return out
    return wrapped


class Configured:
    def __init__(self, cfg: set[str], instrument: bool = False):
        self.cfg = cfg
        self.instrument = instrument
        self.saved: dict[str, Any] = {}

    def __enter__(self):
        if "R-AGG" in self.cfg:
            self.saved["_unique_or_none"] = ex._unique_or_none
            ex._unique_or_none = plurality_or_none
        if self.instrument:
            # Wrap whichever decision rule this configuration installed, so the recorded
            # calls describe the configuration actually under test.
            self.saved.setdefault("_unique_or_none", ex._unique_or_none)
            ex._unique_or_none = _instrumented(ex._unique_or_none)
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
def _j(x: Any) -> str:
    """The comparison idiom 0.7 used for its faithfulness guard, reused unchanged."""
    return json.dumps(x, sort_keys=True, default=str)


def count_categories(rows: list[dict]) -> dict[str, int]:
    """Count over the full frozen category set, so a zero-count category still has a key.

    0.6's categorize() can emit any of BASELINE_CATEGORIES; a category with no rows is a
    finding, not an absence, so it must be representable as 0.
    """
    cats = {k: 0 for k in BASELINE_CATEGORIES}
    for r in rows:
        cats[r["category"]] = cats.get(r["category"], 0) + 1
    return cats


def category_diff(observed: dict[str, int], frozen: dict[str, int]) -> list[tuple]:
    """Per-category disagreement over the union of keys, absent meaning zero.

    A count of 0 and an absent key denote the same fact, so they must compare equal. This
    does not weaken the criterion: every category count must still equal the frozen
    baseline, ANOMALY included, and a category 0.6 never emitted before still aborts.
    """
    return [(k, observed.get(k, 0), frozen.get(k, 0))
            for k in sorted(set(observed) | set(frozen))
            if observed.get(k, 0) != frozen.get(k, 0)]


def load_population(audit: Path, a_legs: Path, p3_legs: Path):
    """Rows, answers, guests and the lock, or None if the population is not the frozen one.

    `run` uses this same loader, so the sweep cannot operate on a population that differs
    from the one parity verified.
    """
    for p in (audit, a_legs, p3_legs):
        if not p.exists():
            print(f"ABORT: {p} not found. This requires the 0.6 record and the Study 2 "
                  f"archive it points at; run this on the host.", file=sys.stderr)
            return None
    rows = [json.loads(l) for l in audit.read_text().splitlines() if l.strip()]
    # Paths are not in the audit file; they are rejoined on (lane, task, leg),
    # exactly as P3_0_IDENTIFICATION_AUDIT_SPEC section 3 requires.
    paths: dict[tuple, tuple] = {}
    for p in (a_legs, p3_legs):
        for line in p.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                paths[(r["lane"], r["task"], r["leg"])] = (r.get("traj"), r.get("guest"))

    cats = count_categories(rows)
    legs = {(r["lane"], r["task"], r["leg"]) for r in rows}
    bad: list[str] = []
    if len(rows) != BASELINE_ROWS:
        bad.append(f"{len(rows)} rows, expected {BASELINE_ROWS}")
    if len(legs) != BASELINE_LEGS:
        bad.append(f"{len(legs)} legs, expected {BASELINE_LEGS}")
    cat_diff = category_diff(cats, BASELINE_CATEGORIES)
    if cat_diff:
        bad.append("categories differ from frozen (observed vs frozen): "
                   + ", ".join(f"{k} {o} vs {f}" for k, o, f in cat_diff))
    missing = sorted(k for k in legs if k not in paths)
    if missing:
        bad.append(f"no traj/guest path for {len(missing)} leg(s): {missing[:3]}")
    if bad:
        print("ABORT: population disagrees with the frozen baseline", file=sys.stderr)
        for b in bad:
            print(f"  - {b}", file=sys.stderr)
        return None
    print(f"population verified       : {len(rows)} rows over {len(legs)} legs, "
          f"categories {dict(sorted(cats.items()))}")

    # Reachability is checked separately so an unresolvable path reports as one legible
    # error instead of surfacing as 134 value mismatches. 0.7 proved these paths resolve
    # on the host; if they stop resolving, that is the finding, not a parity failure.
    unreachable = []
    for key in sorted(legs):
        traj_s, guest_s = paths[key]
        for label, s in (("traj", traj_s), ("guest", guest_s)):
            if not s or not Path(s).exists():
                unreachable.append(f"{key} {label}: {s}")
    if unreachable:
        print(f"ABORT: {len(unreachable)} path(s) not reachable from this machine. Parity "
              f"must run where the Study 2 archive lives.", file=sys.stderr)
        for u in unreachable[:10]:
            print(f"  - {u}", file=sys.stderr)
        return None
    print(f"archive reachable         : {len(legs)} legs, traj + guest both present")

    lock = ex.load_lock()
    answers: dict[tuple, str] = {}
    guests: dict[tuple, dict] = {}
    for key in sorted(legs):
        traj_s, guest_s = paths[key]
        tp = Path(traj_s) if traj_s else None
        answers[key] = ex.final_answer_from_traj(tp) if tp and tp.exists() else ""
        gp = Path(guest_s) if guest_s else None
        guests[key] = ex.load_guest(gp) if gp and gp.exists() else {}
    rows = sorted(rows, key=lambda x: (x["stratum"], x["lane"], x["task"],
                                       x["leg"], x["component_id"]))
    return rows, answers, guests, lock


def gate_parity(audit: Path, a_legs: Path, p3_legs: Path) -> bool:
    pop = load_population(audit, a_legs, p3_legs)
    if pop is None:
        return False
    rows, answers, guests, lock = pop
    bad: list[str] = []
    checked = 0
    with Configured(set()):
        for r in rows:
            key = (r["lane"], r["task"], r["leg"])
            task, cid = r["task"], r["component_id"]
            spec = lock["components"][task][cid]
            gold = ex.gold_for_component(guests[key], task, cid, lock)
            rep = extract_for(task, cid, spec["kind"], answers[key], set())
            got = match_with_config(spec, gold, rep, set())
            if _j(ex._jsonable(gold)) != _j(r["gold"]):
                bad.append(f"gold {key}/{cid}: {ex._jsonable(gold)!r} != recorded {r['gold']!r}")
            if _j(ex._jsonable(rep)) != _j(r["reported"]):
                bad.append(f"reported {key}/{cid}: {ex._jsonable(rep)!r} != recorded {r['reported']!r}")
            if bool(got) != bool(r["extractor_match"]):
                bad.append(f"match {key}/{cid}: {got} != recorded {r['extractor_match']}")
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


# ---------------------------------------------------------------------------
# The measurement run: section 3 quantities and the residual cause decomposition over
# the six configurations of section 2.2, with the K0 and K3 guards.
# ---------------------------------------------------------------------------

# Section 1.1 as published from 0.7. The taxonomy implementation must reproduce these
# under FROZEN before any repaired number is printed. Without that, every
# per-configuration delta is a delta against an unknown baseline.
FROZEN_TAXONOMY = {
    "RECALL_MISS": {"M1": 20, "M1a": 13, "M1b": 7, "M2": 9, "M3": 5, "M4": 5},
    "ABSENT": {"M1": 25, "M2": 19, "M3": 2, "M4": 15},
}
K0_MODAL_GOLD_M1A = 7  # of 13, from 0.7. A guard on the implementation, not a result.


def is_m1c(dis: list[dict]) -> bool:
    """A-2.3: an M1 row whose disagreeing values are equal under R1 after stripping
    leading punctuation -- the instrument disagreeing with itself about formatting.

    Orthogonal to the M1a/M1b split, which stays as published, and reported beside it.
    """
    vals = [v for c in dis for v in c["filtered"]]
    if len(vals) < 2:
        return False
    return len({norm_r1(str(v).lstrip(" :;,.-\u2013\u2014")) for v in vals}) == 1


def evaluate(r: dict, spec: dict, gold: Any, answer: str, cfg: set[str]) -> dict:
    """One row under one configuration: what was reported, whether it matched, and why."""
    AGG_CALLS.clear()
    with Configured(cfg, instrument=True):
        rep = extract_for(r["task"], r["component_id"], spec["kind"], answer, cfg)
        matched = match_with_config(spec, gold, rep, cfg)
    calls = list(AGG_CALLS)
    # The classifier decides M3 vs M2 by searching the text for a label, so it must see
    # the same text the extractor saw. Under FROZEN that is the raw answer, which is what
    # 0.7 classified.
    seen = chan_clean(answer) if "R-CHAN" in cfg else answer
    cause, dis = idaud.classify(spec, r["task"], r["component_id"], gold, rep,
                                matched, seen, calls)
    form = cause
    if cause == "M1":
        form = "M1a" if idaud.gold_among(
            spec, gold, [v for c in dis for v in c["filtered"]]) else "M1b"
    return {"reported": rep, "matched": bool(matched), "cause": cause,
            "form": form, "m1c": cause == "M1" and is_m1c(dis)}


def taxonomy_of(res: dict, rows: list[dict]) -> dict:
    """Cause counts split by the row's frozen baseline category, as 0.7 reported them."""
    out: dict[str, dict[str, int]] = {}
    for r in rows:
        cat = r["category"]
        key = (r["lane"], r["task"], r["leg"], r["component_id"])
        e = res[key]
        b = out.setdefault(cat, {})
        b[e["cause"]] = b.get(e["cause"], 0) + 1
        if e["cause"] == "M1":
            b[e["form"]] = b.get(e["form"], 0) + 1
    return out


def cmd_run(audit: Path, a_legs: Path, p3_legs: Path) -> int:
    pop = load_population(audit, a_legs, p3_legs)
    if pop is None:
        return 3
    rows, answers, guests, lock = pop

    specs, golds = {}, {}
    for r in rows:
        key = (r["lane"], r["task"], r["leg"], r["component_id"])
        specs[key] = lock["components"][r["task"]][r["component_id"]]
        golds[key] = ex.gold_for_component(guests[(r["lane"], r["task"], r["leg"])],
                                           r["task"], r["component_id"], lock)

    results: dict[str, dict] = {}
    for cfgname in CONFIGS:
        cfg = config_set(cfgname)
        res = {}
        for r in rows:
            key = (r["lane"], r["task"], r["leg"], r["component_id"])
            res[key] = evaluate(r, specs[key], golds[key],
                                answers[(r["lane"], r["task"], r["leg"])], cfg)
        results[cfgname] = res

    # --- faithfulness of the instrumented FROZEN pass, before anything is interpreted ---
    fz = results["FROZEN"]
    bad = []
    for r in rows:
        key = (r["lane"], r["task"], r["leg"], r["component_id"])
        if _j(ex._jsonable(fz[key]["reported"])) != _j(r["reported"]):
            bad.append(f"reported {key}: {fz[key]['reported']!r} != 0.6 {r['reported']!r}")
        if fz[key]["matched"] != bool(r["extractor_match"]):
            bad.append(f"match {key}: {fz[key]['matched']} != 0.6 {r['extractor_match']}")
    if bad:
        print(f"ABORT: instrumentation is not pass-through; {len(bad)} FROZEN rows differ "
              f"from 0.6.", file=sys.stderr)
        for b in bad[:20]:
            print("  !", b, file=sys.stderr)
        return 7
    print(f"FROZEN reproduces 0.6 with instrumentation active : {len(rows)} rows")

    fz_tax = taxonomy_of(fz, rows)
    tdiff = []
    for cat, want in FROZEN_TAXONOMY.items():
        got = fz_tax.get(cat, {})
        for k, n in want.items():
            if got.get(k, 0) != n:
                tdiff.append(f"{cat}/{k}: {got.get(k, 0)} != published {n}")
    if tdiff:
        print("ABORT: the cause taxonomy does not reproduce 0.7 under FROZEN. Every "
              "per-configuration delta would be measured against an unknown baseline.",
              file=sys.stderr)
        for t in tdiff:
            print("  !", t, file=sys.stderr)
        return 8
    print("cause taxonomy reproduces 0.7 under FROZEN        : "
          f"RECALL_MISS {dict(sorted(fz_tax['RECALL_MISS'].items()))}")
    print("                                                   "
          f"ABSENT {dict(sorted(fz_tax['ABSENT'].items()))}")

    # --- K3 leakage guard, and K0 --------------------------------------------------
    r1_rows = [r for r in rows if r["category"] in ("MATCH", "RECALL_MISS")]
    m2_keys = [k for k, e in fz.items() if e["cause"] == "M2"]
    m1a_keys = [k for k, e in fz.items() if e["form"] == "M1a"]
    leaks = {c: sorted(k for k in m2_keys if results[c][k]["matched"]) for c in CONFIGS}
    leaks = {c: v for c, v in leaks.items() if v}
    k0 = sum(1 for k in m1a_keys if results["R-AGG"][k]["matched"])

    print()
    print(f"K0  R-AGG recovers {k0} of {len(m1a_keys)} M1a rows; 0.7 says "
          f"{K0_MODAL_GOLD_M1A} have modal gold -> "
          f"{'PASS' if k0 == K0_MODAL_GOLD_M1A else 'FAIL, implementation unfaithful'}")
    if leaks:
        print(f"K3  FIRES: {ilen(leaks)} M2 row(s) recovered: "
              f"{ {c: len(v) for c, v in leaks.items()} }")
        print("    Per spec 7 K3 the run is VOID. M2 rows are the internal negative "
              "control; recovering one means a repair reached outside its layer.")
    else:
        print(f"K3  no configuration recovers any of the {len(m2_keys)} M2 rows -> PASS")
    # K0 is evaluated first: if the implementation is unfaithful, K3's verdict is not
    # trustworthy either. Both abort, and neither writes an artefact -- a voided run must
    # not leave a file behind that later reads as a valid result.
    if k0 != K0_MODAL_GOLD_M1A:
        print("\nABORT on K0: fix the implementation before reading any other number.",
              file=sys.stderr)
        return 9
    if leaks:
        print(f"\nABORT on K3: the run is VOID per spec 7. Nothing is written.",
              file=sys.stderr)
        for c, v in leaks.items():
            for k in v[:5]:
                print(f"  ! {c} recovered M2 row {k}", file=sys.stderr)
        return 10

    # --- section 3 quantities ------------------------------------------------------
    print()
    hdr = (f"{'config':8s} {'sens (MATCH/59)':>20s} {'abstain/134':>18s} "
           f"{'conf-wrong M4/rep':>22s}")
    print(hdr)
    print("-" * len(hdr))
    summary = {}
    for c in CONFIGS:
        res = results[c]
        sens_k = sum(1 for r in r1_rows
                     if res[(r["lane"], r["task"], r["leg"], r["component_id"])]["matched"])
        abst_k = sum(1 for e in res.values() if e["reported"] is None)
        rep_n = len(rows) - abst_k
        m4_k = sum(1 for e in res.values() if e["reported"] is not None and not e["matched"])
        summary[c] = {
            "sensitivity": [sens_k, len(r1_rows), idaud.wilson(sens_k, len(r1_rows))],
            "abstention": [abst_k, len(rows), idaud.wilson(abst_k, len(rows))],
            "confident_wrong": [m4_k, rep_n, idaud.wilson(m4_k, rep_n) if rep_n else None],
            "taxonomy": taxonomy_of(res, rows),
            "m1c": sum(1 for e in res.values() if e["m1c"]),
        }
        s, a, w = (summary[c]["sensitivity"], summary[c]["abstention"],
                   summary[c]["confident_wrong"])
        print(f"{c:8s} {fmt_ci(s):>20s} {fmt_ci(a):>18s} {fmt_ci(w):>22s}")

    print()
    print("residual cause decomposition (RECALL_MISS | ABSENT), M1c flagged separately")
    for c in CONFIGS:
        t = summary[c]["taxonomy"]
        print(f"  {c:8s} RECALL_MISS {dict(sorted(t.get('RECALL_MISS', {}).items()))}")
        print(f"  {'':8s} ABSENT      {dict(sorted(t.get('ABSENT', {}).items()))}"
              f"   M1c={summary[c]['m1c']}")

    OUT_RUN.parent.mkdir(parents=True, exist_ok=True)
    OUT_RUN.write_text(json.dumps({
        "corpus": "development", "rows": len(rows), "r1_rows": len(r1_rows),
        "k0": {"recovered": k0, "m1a": len(m1a_keys), "expected": K0_MODAL_GOLD_M1A},
        "k3": {"m2_rows": len(m2_keys), "leaks": {c: len(v) for c, v in leaks.items()}},
        "frozen_taxonomy_reproduced": True,
        "configurations": summary,
    }, indent=1, default=str))
    print(f"\nwritten: {OUT_RUN}")
    print("Development corpus only. Sections 4 and 6 are separate invocations so the "
          "sealed corpus stays a single deliberate run.")
    return 0


def cmd_diag_k0(audit: Path, a_legs: Path, p3_legs: Path) -> int:
    """Read-only diagnosis of why K0 counted 8 where 0.7 recorded 7. Writes nothing.

    P3_0_CONCLUSION records the 7 as rows in which gold was a **strict majority** of the
    accumulated candidates, with tallies 10/12, 4/5 and 3/4. §7 K0 restated that as "the
    modal group". Strict majority is a *proper* subset of unique mode, so plurality must
    recover at least 7, and 8 is consistent with a faithful implementation.

    This prints the per-call tallies so the difference is visible per row instead of
    inferred, and separates the two candidate explanations for the eighth row: gold modal
    without being a majority, versus a pick that matches gold only through the frozen
    money tolerance.
    """
    pop = load_population(audit, a_legs, p3_legs)
    if pop is None:
        return 3
    rows, answers, guests, lock = pop

    n_maj = n_mode = n_rec = n_tol = 0
    print()
    print("13 M1a rows: per-call candidate tallies under FROZEN, then the R-AGG outcome")
    print("=" * 100)
    for r in rows:
        key = (r["lane"], r["task"], r["leg"], r["component_id"])
        spec = lock["components"][r["task"]][r["component_id"]]
        gold = ex.gold_for_component(guests[(r["lane"], r["task"], r["leg"])],
                                     r["task"], r["component_id"], lock)
        answer = answers[(r["lane"], r["task"], r["leg"])]
        AGG_CALLS.clear()
        with Configured(set(), instrument=True):
            rep0 = extract_for(r["task"], r["component_id"], spec["kind"], answer, set())
            m0 = match_with_config(spec, gold, rep0, set())
        calls = list(AGG_CALLS)
        cause, dis = idaud.classify(spec, r["task"], r["component_id"], gold, rep0, m0,
                                    answer, calls)
        if cause != "M1" or not idaud.gold_among(
                spec, gold, [v for c in dis for v in c["filtered"]]):
            continue

        gk = _group_key(gold)
        maj = mode = False
        print(f"\n{r['lane']}/{r['task']}/{r['leg']}/{r['component_id']}  "
              f"kind={spec['kind']}  gold={ex._jsonable(gold)!r}")
        for i, c in enumerate(dis):
            tally: dict[Any, int] = {}
            for v in c["filtered"]:
                tally[_group_key(v)] = tally.get(_group_key(v), 0) + 1
            n = sum(tally.values())
            gc = tally.get(gk, 0)
            top = max(tally.values())
            is_maj = gc * 2 > n
            is_mode = gc == top and sum(1 for t in tally.values() if t == top) == 1
            maj = maj or is_maj
            mode = mode or is_mode
            print(f"  call {i}: n={n:>3d} gold_group={gc:>3d} top={top:>3d} "
                  f"groups={len(tally)}  strict_majority={is_maj}  unique_mode={is_mode}")
            if len(tally) <= 6:
                print(f"           tally={ {str(k)[:18]: v for k, v in tally.items()} }")
        AGG_CALLS.clear()
        with Configured({"R-AGG"}, instrument=True):
            rep1 = extract_for(r["task"], r["component_id"], spec["kind"], answer,
                               {"R-AGG"})
            m1 = match_with_config(spec, gold, rep1, {"R-AGG"})
        exact = _group_key(rep1) == gk if rep1 is not None else False
        tol = bool(m1) and not exact
        n_maj += maj
        n_mode += mode
        n_rec += bool(m1)
        n_tol += tol
        print(f"  R-AGG -> {ex._jsonable(rep1)!r} matched={bool(m1)} "
              f"exact_gold_group={exact} matched_via_tolerance_only={tol}")

    print()
    print("=" * 100)
    print(f"gold a strict majority in at least one call : {n_maj}   <- 0.7 records 7")
    print(f"gold the unique mode in at least one call   : {n_mode}")
    print(f"R-AGG recovers                              : {n_rec}   <- K0 observed 8")
    print(f"  of which matched only via money tolerance : {n_tol}")
    print()
    print("Strict majority implies unique mode, never the converse, so recovered >= 7 is")
    print("required of a faithful implementation. Nothing is written; no quantity of "
          "section 3 is computed.")
    return 0


def ilen(d: dict) -> int:
    return sum(len(v) for v in d.values())


def fmt_ci(t) -> str:
    k, n, ci = t
    if not n:
        return "n/a"
    c = f"[{ci[0]:.3f},{ci[1]:.3f}]" if ci else ""
    return f"{k}/{n}={k / n:.3f} {c}"


def gate_deps(paths: tuple | None) -> dict:
    """What a gate result actually depends on: the frozen modules and, for parity, the
    input bytes. Deliberately not this harness's own hash -- that changes whenever the
    run path is extended, and it is not what parity proved.
    """
    d: dict[str, Any] = {"frozen_blobs": {
        m: git_blob(Path(sys.modules[m].__file__).resolve()) for m in FROZEN_BLOBS}}
    if paths:
        d["inputs"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    return d


def _write_gate(name: str, ok: bool, deps: dict) -> None:
    d = json.loads(GATES.read_text()) if GATES.exists() else {}
    d[name] = {"ok": ok, "deps": deps}
    GATES.parent.mkdir(parents=True, exist_ok=True)
    GATES.write_text(json.dumps(d, indent=1))


def gates_ok(paths: tuple) -> tuple[bool, str]:
    """Both gates must have passed *on the dependencies now present*.

    out/p3_1_gates.json is untracked, so it survives `git checkout`. A bare
    {"parity": true} therefore cannot authorise a run: it does not record what was
    verified. Stale or bool-only records require re-running the gates.
    """
    if not GATES.exists():
        return False, "out/p3_1_gates.json absent; run parity then synthetic"
    absent = [str(p) for p in paths if not p.exists()]
    if absent:
        return False, ("input(s) absent, so the gate pin cannot even be evaluated: "
                       + ", ".join(absent))
    g = json.loads(GATES.read_text())
    for name, want in (("parity", gate_deps(paths)), ("synthetic", gate_deps(None))):
        rec = g.get(name)
        if not isinstance(rec, dict):
            return False, (f"gate '{name}' is recorded in the pre-A-6 format with no "
                           f"dependency pin; re-run it")
        if not rec.get("ok"):
            return False, f"gate '{name}' did not pass"
        for k, v in want.items():
            if rec["deps"].get(k) != v:
                return False, (f"gate '{name}' was recorded against different {k}; "
                               f"re-run it")
    return True, ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["parity", "synthetic", "run", "diag-k0"])
    ap.add_argument("--audit", default="out/p3_0_recall_audit.jsonl")
    ap.add_argument("--a-legs", default="out/study2_hatd_legs.jsonl")
    ap.add_argument("--p3-legs", default="out/p3_0_extracted.jsonl")
    a = ap.parse_args()
    check_provenance()
    paths = (Path(a.audit), Path(a.a_legs), Path(a.p3_legs))
    if a.cmd == "parity":
        ok = gate_parity(*paths)
        if ok:
            _write_gate("parity", True, gate_deps(paths))
        return 0 if ok else 3
    if a.cmd == "synthetic":
        ok = gate_synthetic()
        if ok:
            _write_gate("synthetic", True, gate_deps(None))
        return 0 if ok else 4
    if a.cmd == "diag-k0":
        # Diagnostic only: reads the archive, writes nothing, computes no section 3
        # quantity and cannot record a gate.
        return cmd_diag_k0(*paths)
    ok, why = gates_ok(paths)
    if not ok:
        print(f"ABORT: `run` requires both gates passed on the present dependencies. {why}",
              file=sys.stderr)
        print("Order is parity -> synthetic -> run. No exceptions.", file=sys.stderr)
        return 5
    return cmd_run(*paths)


if __name__ == "__main__":
    raise SystemExit(main())
