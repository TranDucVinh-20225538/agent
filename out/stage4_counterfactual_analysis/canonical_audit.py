#!/usr/bin/env python3
"""Canonical read-only Phase A (locked Stage-4) + Phase B primary audit.

Gold from guest.json / sql-patch only. DONE iff last traj action == DONE.
Does not call APIs, modify experiment artifacts, or use expected-result tables
as ground truth.
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
from pathlib import Path

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    plt = None

ROOT = Path("/Users/cubo/CMU/agent")
RESULTS = ROOT / "results"
OUT = ROOT / "out" / "stage4_counterfactual_analysis"

TASKS = [
    "retrieval-f001",
    "retrieval-f003",
    "retrieval-f016",
    "retrieval-f029",
    "retrieval-f030",
    "aggregation-f003",
    "aggregation-f018",
    "preference_inference-f004",
    "preference_inference-f018",
    "counterfactual-f004",
]
LOCKED_PHASE_A = {
    "retrieval-f001",
    "aggregation-f003",
    "preference_inference-f018",
    "counterfactual-f004",
}
PRIMARY = ["claude", "openai", "qwen35a3b"]
SKIP = ("attempt", "incomplete", "cf-attempt")
HIGH_SCORE = 80


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "unknown"


def _binom_tail_ge(k: int, n: int, p: float) -> float:
    from math import comb

    if p <= 0:
        return 1.0 if k <= 0 else 0.0
    if p >= 1:
        return 1.0
    return sum(comb(n, i) * (p ** i) * ((1 - p) ** (n - i)) for i in range(k, n + 1))


def _binom_cdf(k: int, n: int, p: float) -> float:
    from math import comb

    if p <= 0:
        return 1.0 if k >= 0 else 0.0
    if p >= 1:
        return 1.0
    return sum(comb(n, i) * (p ** i) * ((1 - p) ** (n - i)) for i in range(0, k + 1))


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> tuple[float | None, float | None]:
    """Clopper–Pearson via binomial-tail inversion (no scipy required)."""
    if n <= 0:
        return None, None
    try:
        from scipy.stats import beta as beta_dist

        lo = 0.0 if k == 0 else float(beta_dist.ppf(alpha / 2, k, n - k + 1))
        hi = 1.0 if k == n else float(beta_dist.ppf(1 - alpha / 2, k + 1, n - k))
        return lo, hi
    except ImportError:
        target = alpha / 2.0
        lo, hi = 0.0, 1.0
        if k == 0:
            lo = 0.0
        else:
            a, b = 0.0, 1.0
            for _ in range(80):
                mid = 0.5 * (a + b)
                if _binom_tail_ge(k, n, mid) < target:
                    a = mid
                else:
                    b = mid
            lo = 0.5 * (a + b)
        if k == n:
            hi = 1.0
        else:
            a, b = 0.0, 1.0
            for _ in range(80):
                mid = 0.5 * (a + b)
                if _binom_cdf(k, n, mid) < target:
                    b = mid
                else:
                    a = mid
            hi = 0.5 * (a + b)
        return lo, hi


def cell_dir(model: str, task: str, cond: str) -> Path:
    locked_prefix = {
        "claude": f"stage4-{task}",
        "openai": f"stage4-openai-{task}",
        "qwen35a3b": f"stage4-qwen35a3b-{task}",
        "qwen359b": f"stage4-qwen359b-{task}",
        "qwen38flash": f"stage4-qwen38flash-{task}",
    }
    if task in LOCKED_PHASE_A:
        return RESULTS / locked_prefix[model] / cond
    return RESULTS / f"phaseb-{model}-{task}" / cond


def find_traj(cond_dir: Path) -> Path | None:
    if not cond_dir.is_dir():
        return None
    direct = list(cond_dir.glob("*/traj.jsonl")) + (
        [cond_dir / "traj.jsonl"] if (cond_dir / "traj.jsonl").is_file() else []
    )
    direct = [p for p in direct if p.is_file() and not any(s in str(p) for s in SKIP)]
    if direct:
        return sorted(direct, key=lambda p: len(p.parts))[0]
    cands = [p for p in cond_dir.rglob("traj.jsonl") if not any(s in str(p) for s in SKIP)]
    return cands[0] if cands else None


def find_guest(cond_dir: Path) -> Path | None:
    if not cond_dir.is_dir():
        return None
    hits = [p for p in cond_dir.glob("*.guest.json") if not any(s in str(p) for s in SKIP)]
    if hits:
        return hits[0]
    hits = [p for p in cond_dir.rglob("*.guest.json") if not any(s in str(p) for s in SKIP)]
    if hits:
        return hits[0]
    if cond_dir.name == "cf":
        alt = cond_dir.parent / "cf-retry-inject"
        gs = list(alt.glob("*.guest.json")) if alt.is_dir() else []
        if gs:
            return gs[0]
    return None


def load_traj(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(errors="replace").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def score_of(cond_dir: Path) -> int | None:
    for p in [cond_dir / "scores.json", *cond_dir.glob("*/scores.json")]:
        if not p.is_file():
            continue
        d = json.loads(p.read_text())
        rows = d.get("rows") or []
        if rows and rows[0].get("raw") is not None:
            return int(rows[0]["raw"])
        if rows and rows[0].get("score") is not None:
            sc = float(rows[0]["score"])
            return int(round(sc * 100)) if sc <= 1 else int(round(sc))
        if "avg_score" in d:
            return int(round(float(d["avg_score"]) * 100))
    return None


def per_rubric_max(cond_dir: Path) -> list | None:
    cands = [
        p
        for p in cond_dir.rglob("rubric_result.json")
        if not any(s in str(p) for s in SKIP)
    ]
    if not cands:
        return None
    d = json.loads(cands[0].read_text())
    return d.get("per_rubric_max")


def inject_ok(guest: dict | None):
    if guest is None:
        return None
    if guest.get("ok") is False:
        return False
    if guest.get("ok") is True:
        return True
    if "probe_after" in guest or guest.get("gold_moved") is not None:
        return True
    return None


def classify_failure(action: str, resp: str, n: int) -> str:
    a = action or ""
    r = resp or ""
    if a == "DONE":
        return ""
    if "Computer tool only allows" in r or "openai api error" in r.lower():
        return "OTHER_EXECUTION_FAILURE"
    if a == "EMPTY_XML":
        return "PARSER_FAILURE"
    if a == "TOOL_CALL":
        return "TOOL_CALL_FAILURE"
    if a in {"FAIL", "PREDICT_CRASH"}:
        return "OTHER_EXECUTION_FAILURE"
    if "timeout" in r.lower():
        return "TIMEOUT"
    if not a:
        return "NO_ACTION"
    if n >= 80 or a.startswith("pyautogui") or a == "WAIT":
        return "NOT_DONE"
    return "NOT_DONE"


def has_num(text: str, *vals) -> bool:
    t = text.replace(",", "")
    for v in vals:
        s = str(v)
        if re.search(rf"(?<!\d){re.escape(s)}(?!\d)", t):
            return True
    return False


def gold_from_guest(task: str, cond: str, guest: dict | None) -> str:
    """Compact gold label parsed from guest probes; never dump raw JSON into CSVs."""
    if not guest:
        return "guest_missing" if cond == "cf" else "base_unpatched_world"
    gm = guest.get("gold_moved")
    blob = " ".join(
        [
            str(guest.get("probe_before") or ""),
            str(guest.get("probe_after") or ""),
            json.dumps(guest.get("extra_probes_after") or [])[:800],
        ]
    )
    blob_c = blob.replace(",", "")
    bits = [f"gold_moved={gm}"]
    if task == "retrieval-f001":
        if "Silver Voyager" in blob:
            bits.append("Silver/8620")
        elif "Gold Voyager" in blob:
            bits.append("Gold/38450")
    elif task == "retrieval-f003":
        bits.append("80000" if "80000" in blob_c and cond == "cf" else "136320")
    elif task == "retrieval-f016":
        bits.append("7114.20/cash50" if cond == "cf" and "7114" in blob_c else "8213.25/cash420")
    elif task == "retrieval-f029":
        bits.append("90000/18000" if cond == "cf" and "90000" in blob_c else "142000/28400")
    elif task == "retrieval-f030":
        bits.append("1099=1200 held")
        bits.append("charitable=100" if cond == "cf" and '"100"' in blob else "charitable=950")
    elif task == "aggregation-f003":
        bits.append("combined=400" if cond == "cf" else "combined=4871.70")
    elif task == "aggregation-f018":
        bits.append("char+HO=0 sqlite" if cond == "cf" else "char=950 HO=104")
    elif task == "preference_inference-f004":
        bits.append("HD Backyard 59" if cond == "cf" and "Backyard" in blob else "HD Cooper 88; TF Cooper 12")
    elif task == "preference_inference-f018":
        bits.append("GME 0 + OM settled" if cond == "cf" else "GME 85 + OM YES")
    elif task == "counterfactual-f004":
        bits.append("improv/1099 zeroed" if cond == "cf" else "improv/1099 present")
    return "; ".join(bits)


def track_items(task: str, cond: str, text: str) -> dict[str, bool]:
    t = text.replace(",", "")
    low = text.lower()
    if task == "retrieval-f001":
        if cond == "base":
            return {
                "tier": "gold" in low,
                "miles": has_num(t, "38450"),
            }
        return {
            "tier": "silver" in low,
            "miles": has_num(t, "8620"),
        }
    if task == "retrieval-f003":
        if cond == "base":
            return {"w2_wages_2024": has_num(t, "136320")}
        return {"w2_wages_2024": has_num(t, "80000")}
    if task == "retrieval-f016":
        if cond == "base":
            return {
                "cost_basis": has_num(t, "8213.25"),
                "cash": has_num(t, "420"),
            }
        return {
            "cost_basis": has_num(t, "7114.20", "7114.2"),
            "cash": bool(re.search(r"\$50(?:\.00)?\b", text) or "cash: $50" in low or has_num(t, "50.00")),
        }
    if task == "retrieval-f029":
        if cond == "base":
            return {
                "wages": has_num(t, "142000"),
                "fed_wh": has_num(t, "28400"),
                "employer": "dunder" in low,
            }
        return {
            "wages": has_num(t, "90000"),
            "fed_wh": has_num(t, "18000"),
            "employer": "dunder" in low,
        }
    if task == "retrieval-f030":
        # D: most-recent (TY2025) 1099 1200 + SIA; charitable 950 vs 100.
        # Reporting TY2024 $1080 as the 1099 amount is not tracking D.
        amt_1200 = has_num(t, "1200") and "1080" not in t.replace(",", "")
        # if both 1080 and 1200, require 1200 as the stated return amount
        if has_num(t, "1080") and "most-recent filed" in low and not re.search(
            r"(2025|in progress).{0,80}1,?200", text, re.I | re.S
        ):
            amt_1200 = False
        if cond == "cf" and has_num(t, "1200"):
            amt_1200 = True
        payer = "scranton" in low
        if cond == "base":
            char = has_num(t, "950")
        else:
            char = bool(
                re.search(r"charitable[^\n]{0,80}\$100(?:\.00)?", text, re.I)
                or re.search(r"claimed[^\n]{0,40}\$100", text, re.I)
                or "charitable contributions claimed on return:** $100" in low
                or "charitable contributions claimed on return: $100" in low
            )
        return {"1099_amount": amt_1200, "1099_payer": payer, "charitable": char}
    if task == "aggregation-f003":
        if cond == "base":
            return {"combined_refund": has_num(t, "4871.70", "4871", "4872")}
        return {"combined_refund": has_num(t, "400") and not has_num(t, "4871", "4872")}
    if task == "aggregation-f018":
        w2 = has_num(t, "142000") and has_num(t, "28400")
        nec = has_num(t, "1200") and "scranton" in low
        if cond == "base":
            return {
                "charitable_sqlite": has_num(t, "950"),
                "home_office_sqlite": has_num(t, "104"),
                "w2_held": w2,
                "1099_held": nec,
            }
        char0 = bool(
            re.search(r"charitable[^\n|]{0,80}(\$0(?:\.00)?|\b0\b)", text, re.I)
            or "**$0.00**" in text
            or "SpeedTax Return | **$0" in text
        )
        ho0 = bool(re.search(r"(home-office|home office|days worked)[^\n]{0,40}\b0\b", text, re.I))
        return {
            "charitable_sqlite": char0,
            "home_office_sqlite": ho0,
            "w2_held": w2,
            "1099_held": nec,
        }
    if task == "preference_inference-f004":
        tf = "cooper" in low and has_num(t, "12")
        if cond == "base":
            return {"tf_top": tf, "hd_top": "cooper" in low and has_num(t, "88")}
        return {
            "tf_top": tf,
            "hd_top": "backyard" in low and has_num(t, "59"),
        }
    if task == "preference_inference-f018":
        if cond == "base":
            gme = "gme" in low and has_num(t, "85")
            om = ("yes" in low and "gamestop" in low) or ("will-gme" in low)
            return {"gme_shares": gme, "om_yes_active": om or ("yes" in low and "100" in t)}
        gme0 = bool(
            re.search(r"gme[^\n]{0,40}(\|\s*0\b|:\s*0\b|shares?\s*=\s*0|0 shares)", low)
            or "gme    | 0" in low
        )
        om_still = bool(
            re.search(r"gamestop above \$100.{0,80}yes.{0,40}200", text, re.I | re.S)
            or ("**yes** | **200**" in low and "gamestop" in low)
        )
        om_cleared = "settled" in low and not om_still
        return {"gme_shares": gme0, "om_yes_active": om_cleared and not om_still}
    if task == "counterfactual-f004":
        if cond == "base":
            return {
                "1099_or_improv_income": has_num(t, "1200") or "1099" in low,
            }
        still = has_num(t, "1200") and ("stipend" in low or "1099" in low)
        gone = any(x in low for x in ("$0", "zero", "no 1099", "not teaching", "no guest"))
        return {"1099_or_improv_income": (not still) or gone}
    return {}


def all_tracked(items: dict[str, bool]) -> bool:
    return bool(items) and all(items.values())


def inspect_cell(model: str, task: str, cond: str) -> dict:
    d = cell_dir(model, task, cond)
    traj = find_traj(d)
    guest_p = find_guest(d)
    guest = json.loads(guest_p.read_text()) if guest_p else None
    rows = load_traj(traj) if traj else []
    action = str(rows[-1].get("action") or "") if rows else ""
    resp = str(rows[-1].get("response") or "") if rows else ""
    done = action == "DONE"
    items = track_items(task, cond, resp) if done else {}
    return {
        "model": model,
        "task": task,
        "condition": cond,
        "phase": (
            "ablation"
            if model == "qwen359b"
            else "exploratory"
            if model == "qwen38flash"
            else "phase_a_locked"
            if task in LOCKED_PHASE_A
            else "phase_b"
        ),
        "dir": d,
        "trajectory_path": str(traj.relative_to(ROOT)) if traj else "",
        "exists": traj is not None,
        "last_action": action.replace("\n", " ")[:180],
        "done": done,
        "step_count": len(rows),
        "failure_type": classify_failure(action, resp, len(rows)) if not done else "",
        "guest_path": str(guest_p.relative_to(ROOT)) if guest_p else "",
        "guest": guest,
        "inject_ok": inject_ok(guest),
        "gold_moved": None if not guest else guest.get("gold_moved"),
        "gold_state": gold_from_guest(task, cond, guest),
        "response": resp,
        "final_excerpt": re.sub(r"\s+", " ", resp.strip().split("```")[0].strip())[:400],
        "score": score_of(d),
        "tracking_items": items,
        "tracking": all_tracked(items) if done else None,
        "per_rubric_max": per_rubric_max(d),
        "notes": "source="
        + ("stage4_reuse" if task in LOCKED_PHASE_A else "phaseb")
        + (
            "; not_primary_ablation"
            if model == "qwen359b"
            else "; not_primary_exploratory"
            if model == "qwen38flash"
            else ""
        ),
    }


def ablation_dir(family: str, task: str, cond: str) -> Path:
    prefix = "stage4-qwen359b" if family == "qwen359b" else "stage4-qwen38flash"
    return RESULTS / f"{prefix}-{task}" / cond


def inspect_ablation(family: str, task: str, cond: str) -> dict:
    d = ablation_dir(family, task, cond)
    # reuse inspect by temporarily... just duplicate path logic
    traj = find_traj(d)
    guest_p = find_guest(d)
    guest = json.loads(guest_p.read_text()) if guest_p else None
    rows = load_traj(traj) if traj else []
    action = str(rows[-1].get("action") or "") if rows else ""
    resp = str(rows[-1].get("response") or "") if rows else ""
    done = action == "DONE"
    items = track_items(task, cond, resp) if done else {}
    return {
        "model": family,
        "task": task,
        "condition": cond,
        "trajectory_path": str(traj.relative_to(ROOT)) if traj else "",
        "exists": traj is not None,
        "last_action": action,
        "done": done,
        "step_count": len(rows),
        "failure_type": classify_failure(action, resp, len(rows)) if not done else "",
        "guest": guest,
        "inject_ok": inject_ok(guest),
        "gold_moved": None if not guest else guest.get("gold_moved"),
        "gold_state": gold_from_guest(task, cond, guest),
        "response": resp,
        "final_excerpt": re.sub(r"\s+", " ", resp.strip().split("```")[0].strip())[:400],
        "score": score_of(d),
        "tracking_items": items,
        "tracking": all_tracked(items) if done else None,
        "dir": d,
        "per_rubric_max": per_rubric_max(d),
        "phase": "ablation",
        "guest_path": str(guest_p.relative_to(ROOT)) if guest_p else "",
        "notes": "ablation_or_exploratory_not_primary",
    }


def pair_row(b: dict, c: dict, registry: dict) -> dict:
    both = b["done"] and c["done"]
    inj = c["inject_ok"]
    valid = bool(both and inj is not False and c["guest"] is not None)
    if both and c["guest"] is None:
        valid = False
    tb, tc = b["tracking"], c["tracking"]
    tpair = bool(tb and tc) if valid else None
    bs, cs = b["score"], c["score"]
    delta = None if (not valid or bs is None or cs is None) else cs - bs
    inv = None if delta is None else delta == 0
    items_b = b["tracking_items"] or {}
    items_c = c["tracking_items"] or {}
    incomplete = valid and tpair is False
    high = (
        bs is not None
        and cs is not None
        and min(bs, cs) >= HIGH_SCORE
        and inv is True
    )
    if not valid:
        cls = "execution_failure"
    elif tpair and inv:
        cls = "Type A"
    elif tpair and inv is False:
        cls = "score-sensitive"
    elif incomplete and high:
        cls = "Type B"
    elif incomplete and inv is True:
        cls = "incomplete_tracking_score_invariant_not_high"
    elif incomplete:
        cls = "incomplete_tracking_score_moved"
    else:
        cls = "valid_unclassified"
    rt = registry.get(b["task"], {})
    gold_changed = None
    if c["guest"] is not None:
        if b["task"] == "retrieval-f030":
            gold_changed = True  # charitable moved; 1099 held
        else:
            gold_changed = bool(c["gold_moved"])
    return {
        "model": b["model"],
        "task": b["task"],
        "phase": b["phase"],
        "base_done": b["done"],
        "cf_done": c["done"],
        "valid_pair": valid,
        "base_gold": b["gold_state"],
        "cf_gold": c["gold_state"],
        "gold_changed": gold_changed,
        "determining_set": json.dumps(rt.get("determining_set") or []),
        "tracking_items_base": json.dumps(items_b),
        "tracking_items_cf": json.dumps(items_c),
        "tracking_base": tb,
        "tracking_cf": tc,
        "tracking_pair": tpair,
        "base_final_excerpt": b["final_excerpt"],
        "cf_final_excerpt": c["final_excerpt"],
        "base_score": bs,
        "cf_score": cs,
        "score_delta": delta,
        "score_invariant": inv,
        "classification": cls,
        "base_traj": b["trajectory_path"],
        "cf_traj": c["trajectory_path"],
        "notes": "; ".join(
            x
            for x in [
                b["notes"],
                "guest.gold_moved=%s" % c["gold_moved"] if c["guest"] else "no_cf_guest",
                "pair incomplete" if not both else "",
            ]
            if x
        ),
        "_b": b,
        "_c": c,
        "_reg": rt,
    }


def rate_block(pairs: list[dict], label: str) -> dict:
    valid = [p for p in pairs if p["valid_pair"]]
    track = [p for p in valid if p["tracking_pair"]]
    inv = [p for p in track if p["score_invariant"]]
    sens = [p for p in track if p["score_invariant"] is False]
    typb = [p for p in valid if p["classification"] == "Type B"]
    k, n = len(inv), len(track)
    lo, hi = clopper_pearson(k, n)
    return {
        "label": label,
        "valid_paired_cells": len(valid),
        "tracking_valid": len(track),
        "score_invariant": k,
        "score_sensitive": len(sens),
        "type_b": len(typb),
        "invariance_rate": None if n == 0 else k / n,
        "clopper_pearson_95ci": [lo, hi],
        "type_b_over_valid": None if not valid else len(typb) / len(valid),
        "pairs": [(p["model"], p["task"], p["base_score"], p["cf_score"]) for p in inv],
        "sensitive_pairs": [(p["model"], p["task"], p["base_score"], p["cf_score"]) for p in sens],
        "type_b_pairs": [(p["model"], p["task"], p["base_score"], p["cf_score"]) for p in typb],
    }


def md_escape(s) -> str:
    return str(s).replace("|", "/").replace("\n", " ")[:180]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    head = git_head()
    REG = json.loads((ROOT / "cf" / "phase_b_registry.json").read_text())
    registry = {t["task_id"]: t for t in REG["tasks"]}

    cells = [inspect_cell(m, t, c) for m in PRIMARY for t in TASKS for c in ("base", "cf")]
    by = {(r["model"], r["task"], r["condition"]): r for r in cells}
    pairs = [
        pair_row(by[(m, t, "base")], by[(m, t, "cf")], registry)
        for m in PRIMARY
        for t in TASKS
    ]

    abl_cells = [
        inspect_cell(m, t, c)
        for m in ("qwen359b", "qwen38flash")
        for t in TASKS
        for c in ("base", "cf")
    ]
    for r in abl_cells:
        r["phase"] = "ablation" if r["model"] == "qwen359b" else "exploratory"
    abl_by = {(r["model"], r["task"], r["condition"]): r for r in abl_cells}
    phase_b_ablation_present = any(
        (RESULTS / f"phaseb-{fam}-{t}").is_dir()
        for fam in ("qwen359b", "qwen38flash")
        for t in TASKS
    )

    def make_abl_pairs(fam):
        outp = []
        for t in TASKS:
            key_b, key_c = (fam, t, "base"), (fam, t, "cf")
            if key_b not in abl_by:
                continue
            b, c = abl_by[key_b], abl_by[key_c]
            outp.append(pair_row(b, c, registry))
        return outp

    p9 = make_abl_pairs("qwen359b")
    pflash = make_abl_pairs("qwen38flash")
    inventory_cells = cells + abl_cells

    # trajectory_cells.csv
    with (OUT / "trajectory_cells.csv").open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "model",
                "task",
                "condition",
                "phase",
                "trajectory_path",
                "exists",
                "last_action",
                "done",
                "step_count",
                "failure_type",
                "score",
                "tracking",
                "tracking_items",
                "guest_path",
                "notes",
            ],
        )
        w.writeheader()
        for r in inventory_cells:
            w.writerow(
                {
                    "model": r["model"],
                    "task": r["task"],
                    "condition": r["condition"],
                    "phase": r["phase"],
                    "trajectory_path": r["trajectory_path"],
                    "exists": str(r["exists"]).lower(),
                    "last_action": r["last_action"],
                    "done": str(r["done"]).lower(),
                    "step_count": r["step_count"],
                    "failure_type": r["failure_type"],
                    "score": "" if r["score"] is None else r["score"],
                    "tracking": "" if r["tracking"] is None else str(r["tracking"]).lower(),
                    "tracking_items": json.dumps(r["tracking_items"]),
                    "guest_path": r["guest_path"],
                    "notes": r["notes"],
                }
            )

    pair_cols = [
        "model",
        "task",
        "phase",
        "base_done",
        "cf_done",
        "valid_pair",
        "base_gold",
        "cf_gold",
        "gold_changed",
        "determining_set",
        "tracking_items_base",
        "tracking_items_cf",
        "tracking_base",
        "tracking_cf",
        "tracking_pair",
        "base_score",
        "cf_score",
        "score_delta",
        "score_invariant",
        "classification",
        "base_traj",
        "cf_traj",
        "notes",
    ]
    with (OUT / "paired_results.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=pair_cols)
        w.writeheader()
        for p in pairs:
            row = {k: p[k] for k in pair_cols}
            for k, v in row.items():
                if isinstance(v, bool):
                    row[k] = str(v).lower()
                elif v is None:
                    row[k] = ""
            w.writerow(row)

    with (OUT / "paired_ablation.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=pair_cols)
        w.writeheader()
        for p in p9 + pflash:
            row = {k: p[k] for k in pair_cols}
            for k, v in row.items():
                if isinstance(v, bool):
                    row[k] = str(v).lower()
                elif v is None:
                    row[k] = ""
            w.writerow(row)

    with (OUT / "failure_audit.csv").open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "model",
                "task",
                "condition",
                "failure_type",
                "last_action",
                "step_count",
                "evidence",
                "semantic_or_execution",
            ],
        )
        w.writeheader()
        for r in inventory_cells:
            if r["done"]:
                continue
            ev = (r["response"] or r["notes"] or "missing traj")[:400].replace("\n", " ")
            w.writerow(
                {
                    "model": r["model"],
                    "task": r["task"],
                    "condition": r["condition"],
                    "failure_type": r["failure_type"] or "NOT_DONE",
                    "last_action": r["last_action"],
                    "step_count": r["step_count"],
                    "evidence": ev,
                    "semantic_or_execution": "execution",
                }
            )

    # rubric item audit
    with (OUT / "rubric_item_audit.csv").open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "model",
                "task",
                "criterion_index",
                "criterion_text",
                "depends_on_D",
                "base_per_rubric_max",
                "cf_per_rubric_max",
                "item_delta",
                "pair_classification",
                "registry_score_dependency",
                "notes",
            ],
        )
        w.writeheader()
        for p in pairs + p9 + pflash:
            if not p["valid_pair"]:
                continue
            rt = p["_reg"]
            bits = [x.strip() for x in (rt.get("rubric") or "").split(";") if x.strip()]
            bm = p["_b"]["per_rubric_max"] or []
            cm = p["_c"]["per_rubric_max"] or []
            n = max(len(bits), len(bm), len(cm))
            for i in range(n):
                txt = bits[i] if i < len(bits) else ""
                bv = bm[i] if i < len(bm) else ""
                cv = cm[i] if i < len(cm) else ""
                delta = ""
                if bv != "" and cv != "":
                    try:
                        delta = int(cv) - int(bv)
                    except Exception:
                        delta = ""
                depends = "unknown"
                if any(
                    k in txt.lower()
                    for k in ("cooper", "value", "pin", "wages", "gme", "yes")
                ):
                    depends = "likely_yes"
                if "does not name" in txt.lower() or "does not pin" in (rt.get("score_dependency") or "").lower():
                    depends = "rubric_does_not_name_seed"
                w.writerow(
                    {
                        "model": p["model"],
                        "task": p["task"],
                        "criterion_index": i,
                        "criterion_text": txt,
                        "depends_on_D": depends,
                        "base_per_rubric_max": bv,
                        "cf_per_rubric_max": cv,
                        "item_delta": delta,
                        "pair_classification": p["classification"],
                        "registry_score_dependency": rt.get("score_dependency") or "",
                        "notes": "per_rubric_max from rubric_result.json; criterion text from frozen registry",
                    }
                )

    ev = [
        "# Tracking evidence (canonical)",
        "",
        f"Git HEAD `{head}`. Tracking from final DONE answers vs guest/SQL gold. Not from score.",
        "",
    ]
    for r in inventory_cells:
        if not r["done"]:
            continue
        ev += [
            f"## {r['model']} / {r['task']} / {r['condition']}",
            "",
            f"- Traj: `{r['trajectory_path']}`",
            f"- Guest: `{r['guest_path']}` gold_moved={r['gold_moved']} inject_ok={r['inject_ok']}",
            f"- Gold: {r['gold_state'][:400]}",
            f"- Item tracking: `{json.dumps(r['tracking_items'])}` → tracking={r['tracking']}",
            f"- Score: {r['score']}",
            "",
            "```",
            r["final_excerpt"][:800],
            "```",
            "",
        ]
    (OUT / "tracking_evidence.md").write_text("\n".join(ev) + "\n")

    mech = [
        "# Rubric mechanism (canonical)",
        "",
        "Only **valid pairs**. Registry rubric text is the criterion source; `per_rubric_max` is observed judge credit.",
        "Do not treat registry `score_dependency` as a result — it is a pre-registered hypothesis.",
        "",
    ]
    for p in pairs + p9 + pflash:
        if not p["valid_pair"]:
            continue
        rt = p["_reg"]
        mech += [
            f"## {p['model']} / {p['task']}",
            "",
            f"- D: {rt.get('determining_set')}",
            f"- Rubric: {rt.get('rubric')}",
            f"- Registry score_dependency (hypothesis, not finding): {rt.get('score_dependency')}",
            f"- Observed scores: {p['base_score']} → {p['cf_score']} (Δ={p['score_delta']})",
            f"- Tracking pair: {p['tracking_pair']} items_base={p['tracking_items_base']} items_cf={p['tracking_items_cf']}",
            f"- Classification: **{p['classification']}**",
            f"- Judge per_rubric_max base={p['_b']['per_rubric_max']} cf={p['_c']['per_rubric_max']}",
            "",
        ]
    (OUT / "rubric_mechanism.md").write_text("\n".join(mech) + "\n")

    primary_all = rate_block(pairs, "primary_descriptive_union_not_a_common_rate")
    by_model = {m: rate_block([p for p in pairs if p["model"] == m], m) for m in PRIMARY}
    r9 = rate_block(p9, "qwen359b_ablation")
    rflash = rate_block(pflash, "qwen38flash_exploratory")

    def write_pair_md(path: Path, title: str, plist: list[dict], extra: str):
        lines = [f"# {title}", "", extra, "", "| model | task | valid | tracking | scores | Δ | class |", "|---|---|---|---|---|---|---|"]
        for p in plist:
            scores = f"{p['base_score']}→{p['cf_score']}" if p["base_score"] is not None else "—"
            lines.append(
                f"| {p['model']} | {p['task']} | {p['valid_pair']} | {p['tracking_pair']} | {scores} | {p['score_delta']} | {p['classification']} |"
            )
        path.write_text("\n".join(lines) + "\n")

    write_pair_md(
        OUT / "table_primary.md",
        "Primary Phase A+B pairs (Claude / GPT / Qwen3.5-35B-A3B)",
        pairs,
        f"HEAD `{head}`. Not pooled as a common-rate estimator. Execution failures stay in this table with classification=execution_failure.",
    )
    write_pair_md(
        OUT / "table_ablation.md",
        "Size ablation (Qwen3.5-9B) — not primary",
        p9,
        f"Do not pool into primary. HEAD `{head}`. "
        + (
            "Phase-B 9B dirs present."
            if phase_b_ablation_present
            else "GitHub has Stage-4 9B only (f001, aggregation-f003); no phaseb-qwen359b-*."
        ),
    )
    write_pair_md(
        OUT / "table_exploratory.md",
        "Exploratory (Qwen3.8-Flash) — not primary",
        pflash,
        f"Do not pool into primary. HEAD `{head}`. "
        + (
            "Phase-B Flash dirs present."
            if phase_b_ablation_present
            else "GitHub has Stage-4 Flash only (f001, aggregation-f003); no phaseb-qwen38flash-*."
        ),
    )

    tex = [
        r"% Auto-generated canonical audit. Do not treat as camera-ready without review.",
        r"\begin{tabular}{llrrrl}",
        r"\toprule",
        r"Model & Task & $S_{\mathrm{base}}$ & $S_{\mathrm{CF}}$ & $\Delta S$ & Class \\",
        r"\midrule",
    ]
    name = {"claude": "Claude", "openai": "GPT", "qwen35a3b": "Qwen-35B-A3B"}
    for p in pairs:
        if not p["valid_pair"]:
            continue
        tex.append(
            f"{name[p['model']]} & \\texttt{{{p['task']}}} & {p['base_score']} & {p['cf_score']} & {p['score_delta']} & {p['classification']} \\\\"
        )
    tex += [r"\bottomrule", r"\end{tabular}", ""]
    (OUT / "table_primary.tex").write_text("\n".join(tex))

    abl_tex = [
        r"% Ablation/exploratory — do not pool with primary.",
        r"\begin{tabular}{llrrrl}",
        r"\toprule",
        r"Lane & Task & $S_{\mathrm{base}}$ & $S_{\mathrm{CF}}$ & $\Delta S$ & Class \\",
        r"\midrule",
    ]
    for lab, plist in (("9B", p9), ("Flash", pflash)):
        for p in plist:
            if not p["valid_pair"]:
                continue
            abl_tex.append(
                f"{lab} & \\texttt{{{p['task']}}} & {p['base_score']} & {p['cf_score']} & {p['score_delta']} & {p['classification']} \\\\"
            )
    abl_tex += [r"\bottomrule", r"\end{tabular}", ""]
    (OUT / "table_ablation.tex").write_text("\n".join(abl_tex))
    (OUT / "table_exploratory.tex").write_text("\n".join(abl_tex))

    stats = {
        "git_head": head,
        "denominator_policy": {
            "valid_pair": "both DONE + CF guest inject not failed",
            "tracking_valid": "valid_pair and every coded D item tracked on both legs",
            "invariance_rate": "score_invariant / tracking_valid  (P(ΔS=0 | tracked D))",
            "type_b": "valid_pair, incomplete tracking, both scores >= 80 and ΔS=0",
            "execution_excluded_from_semantic": True,
            "pooled_primary": "descriptive union only; not a common-rate estimator",
        },
        "primary_descriptive_union": {k: v for k, v in primary_all.items() if k != "pairs" and "pairs" not in k or k in ("pairs", "sensitive_pairs", "type_b_pairs")},
        "by_model": {},
        "execution_coverage": {},
        "ablation_qwen359b": {k: v for k, v in r9.items() if not k.endswith("pairs") or k in ("pairs", "sensitive_pairs", "type_b_pairs")},
        "exploratory_qwen38flash": {k: v for k, v in rflash.items() if not k.endswith("pairs") or k in ("pairs", "sensitive_pairs", "type_b_pairs")},
    }
    # slim json
    def slim(block):
        d = dict(block)
        d.pop("label", None)
        return d

    stats["primary_descriptive_union"] = slim(primary_all)
    for m in PRIMARY:
        stats["by_model"][m] = slim(by_model[m])
    for m in PRIMARY:
        mc = [r for r in cells if r["model"] == m]
        stats["execution_coverage"][m] = {
            "done_trajectories": sum(1 for r in mc if r["done"]),
            "expected_trajectories": 20,
            "present_traj": sum(1 for r in mc if r["exists"]),
            "valid_pairs": by_model[m]["valid_paired_cells"],
            "expected_pairs": 10,
        }
    for m, label in (("qwen359b", "ablation_9b"), ("qwen38flash", "exploratory_flash")):
        mc = [r for r in abl_cells if r["model"] == m]
        stats["execution_coverage"][m] = {
            "done_trajectories": sum(1 for r in mc if r["done"]),
            "expected_trajectories": 20,
            "present_traj": sum(1 for r in mc if r["exists"]),
            "valid_pairs": (r9 if m == "qwen359b" else rflash)["valid_paired_cells"],
            "expected_pairs": 10,
            "lane": label,
        }
    (OUT / "statistical_summary.json").write_text(json.dumps(stats, indent=2) + "\n")

    def fmt_ci(block):
        n = block["tracking_valid"]
        k = block["score_invariant"]
        lo, hi = block["clopper_pearson_95ci"]
        rate = block["invariance_rate"]
        if n == 0:
            return "undefined (tracking-valid n=0)"
        return f"{k}/{n} = {rate:.3f}; 95% CI [{lo:.3f}, {hi:.3f}]"

    paper = [
        "# Canonical primary results (Phase A locked + Phase B)",
        "",
        f"Snapshot `{head}`. Semantic inference uses only valid paired episodes.",
        "Invariance rate = Type A / tracking-valid = P(ΔS=0 | agent tracked D).",
        "The three-model union is **descriptive**, not a pooled common-rate estimate.",
        "Qwen3.5-35B-A3B execution failures are not coded as non-tracking.",
        "",
        "## Per-model invariance (preferred reporting unit)",
        "",
        f"- Claude: {fmt_ci(by_model['claude'])}",
        f"- GPT: {fmt_ci(by_model['openai'])}",
        f"- Qwen3.5-35B-A3B: {fmt_ci(by_model['qwen35a3b'])}",
        "",
        "## Descriptive union (labelled, not a common rate)",
        "",
        f"- {fmt_ci(primary_all)}",
        "",
        "## Type A",
        "",
    ]
    for p in pairs:
        if p["classification"] == "Type A":
            paper.append(f"- {p['model']} {p['task']}: {p['base_score']}→{p['cf_score']}")
    paper += ["", "## Score-sensitive", ""]
    for p in pairs:
        if p["classification"] == "score-sensitive":
            paper.append(f"- {p['model']} {p['task']}: {p['base_score']}→{p['cf_score']} (Δ {p['score_delta']})")
    paper += ["", "## Type B (incomplete tracking, score high and invariant)", ""]
    for p in pairs:
        if p["classification"] == "Type B":
            paper.append(
                f"- {p['model']} {p['task']}: {p['base_score']}→{p['cf_score']}; base_items={p['tracking_items_base']}; cf_items={p['tracking_items_cf']}"
            )
    paper += ["", "## Other valid incomplete-tracking", ""]
    for p in pairs:
        if p["valid_pair"] and p["classification"] not in {"Type A", "score-sensitive", "Type B"}:
            paper.append(f"- {p['model']} {p['task']}: {p['classification']} {p['base_score']}→{p['cf_score']}")
    paper += ["", "## Execution coverage", ""]
    for m in PRIMARY:
        e = stats["execution_coverage"][m]
        paper.append(
            f"- {m}: DONE {e['done_trajectories']}/20 traj; valid pairs {e['valid_pairs']}/10"
        )
    paper += [
        "",
        "## Size ablation (Qwen3.5-9B) — not primary",
        "",
        f"- {fmt_ci(r9)}",
    ]
    for p in p9:
        paper.append(
            f"- {p['task']}: valid={p['valid_pair']} tracking={p['tracking_pair']} "
            f"{p['base_score']}→{p['cf_score']} **{p['classification']}** items_cf={p['tracking_items_cf']}"
        )
    paper += [
        "",
        "## Exploratory (Qwen3.8-Flash) — not primary",
        "",
        f"- {fmt_ci(rflash)}",
    ]
    for p in pflash:
        paper.append(
            f"- {p['task']}: valid={p['valid_pair']} tracking={p['tracking_pair']} "
            f"{p['base_score']}→{p['cf_score']} **{p['classification']}** items_cf={p['tracking_items_cf']}"
        )
    paper += [
        "",
        "## What not to claim",
        "",
        "- Do not report a single invariance rate as the paper headline without the per-model breakdown.",
        "- Do not treat Qwen EMPTY_XML as Type B or as track=0.",
        "- 9B/Flash remain ablation/exploratory and are not pooled with Claude/GPT/35B-A3B.",
        "- Phase B 9B/Flash six-task lanes are not on origin/phase-a-results; do not impute them.",
        "",
    ]
    (OUT / "paper_results.md").write_text("\n".join(paper) + "\n")

    if HAS_MPL:
        fig, ax = plt.subplots(figsize=(7.2, 4.2))
        labels, rates, yerr_lo, yerr_hi, ns = [], [], [], [], []
        for m, lab in [("claude", "Claude"), ("openai", "GPT"), ("qwen35a3b", "Qwen 35B-A3B")]:
            b = by_model[m]
            labels.append(lab)
            n = b["tracking_valid"]
            ns.append(n)
            if n == 0:
                rates.append(0)
                yerr_lo.append(0)
                yerr_hi.append(0)
            else:
                rates.append(b["invariance_rate"])
                lo, hi = b["clopper_pearson_95ci"]
                yerr_lo.append(b["invariance_rate"] - lo)
                yerr_hi.append(hi - b["invariance_rate"])
        ax.bar(labels, rates, yerr=[yerr_lo, yerr_hi], capsize=4, color="#4C6B8A")
        ax.set_ylim(0, 1.05)
        ax.set_ylabel("P(ΔS=0 | tracked D)")
        ax.set_title("Type A rate among tracking-valid pairs (Clopper–Pearson 95% CI)")
        for i, n in enumerate(ns):
            ax.text(i, 0.05, f"n={n}", ha="center", color="white", fontsize=9)
        fig.tight_layout()
        fig.savefig(OUT / "invariance_by_model.png", dpi=140)
        plt.close()

        fig, ax = plt.subplots(figsize=(8.5, 4.8))
        colors = {
            "Type A": "#2A6F4D",
            "score-sensitive": "#2C5F8A",
            "Type B": "#A15C2A",
            "execution_failure": "#888888",
        }
        for p in pairs:
            if p["base_score"] is None or p["cf_score"] is None:
                continue
            cls = p["classification"]
            col = colors.get(cls, "#555")
            ax.plot([0, 1], [p["base_score"], p["cf_score"]], color=col, alpha=0.7, lw=1.4)
            ax.scatter([0, 1], [p["base_score"], p["cf_score"]], color=col, s=18, zorder=3)
        ax.set_xticks([0, 1], ["Base", "CF"])
        ax.set_ylabel("Judge score")
        ax.set_title("Primary score trajectories (color = classification)")
        ax.set_ylim(-5, 105)
        fig.tight_layout()
        fig.savefig(OUT / "score_pairs_primary.png", dpi=140)
        plt.close()

        fig, ax = plt.subplots(figsize=(6.5, 3.8))
        labs, done, validn = [], [], []
        for m, lab in [("claude", "Claude"), ("openai", "GPT"), ("qwen35a3b", "Qwen 35B")]:
            e = stats["execution_coverage"][m]
            labs.append(lab)
            done.append(e["done_trajectories"] / 20)
            validn.append(e["valid_pairs"] / 10)
        x = range(len(labs))
        ax.bar([i - 0.18 for i in x], done, 0.36, label="DONE traj / 20", color="#4C6B8A")
        ax.bar([i + 0.18 for i in x], validn, 0.36, label="valid pairs / 10", color="#A15C2A")
        ax.set_xticks(list(x), labs)
        ax.set_ylim(0, 1.05)
        ax.set_ylabel("Coverage")
        ax.set_title("Execution coverage (not semantic tracking)")
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(OUT / "execution_coverage.png", dpi=140)
        plt.close()
    else:
        (OUT / "FIGURES_SKIPPED.txt").write_text(
            "matplotlib not installed in this Python; tables and CIs were still written.\n"
        )

    # stdout
    def dump(title, b):
        print(title)
        print(f"valid paired cells: {b['valid_paired_cells']}")
        print(f"tracking-valid: {b['tracking_valid']}")
        print(f"score-invariant: {b['score_invariant']}")
        print(f"score-sensitive: {b['score_sensitive']}")
        print(f"Type B candidates: {b['type_b']}")
        print(f"invariance rate: {b['invariance_rate']}")
        print(f"Clopper-Pearson 95% CI: {b['clopper_pearson_95ci']}")
        print()

    print("PRIMARY (descriptive union; not a common-rate estimator)")
    dump("", primary_all)
    for m in PRIMARY:
        print(m.upper())
        dump("", by_model[m])
    print("QWEN EXECUTION", stats["execution_coverage"]["qwen35a3b"])
    print("PHASE_B_ABLATION_DIRS", phase_b_ablation_present)
    print("ABLATION QWEN3.5-9B (not primary)")
    dump("", r9)
    print("EXPLORATORY QWEN3.8-FLASH (not primary)")
    dump("", rflash)


if __name__ == "__main__":
    main()
