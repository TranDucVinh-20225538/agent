#!/usr/bin/env python3
"""Write Stage 4 confirmatory results. Judge score is auxiliary, not the DV.

Set STAGE4_TAG=openai to read results/stage4-openai-<task>/ and write
out/evidence_stage4_openai_results.{md,csv} without touching the Claude tables.
"""
from __future__ import annotations

import csv
import json
import os
import re
from pathlib import Path

A = Path(os.environ.get("MYPCBENCH_AGENT_ROOT") or Path(__file__).resolve().parents[1])
TAG = (os.environ.get("STAGE4_TAG") or "").strip()
_PREFIX = f"stage4-{TAG}-" if TAG else "stage4-"
_OUT = f"evidence_stage4_{TAG}_results" if TAG else "evidence_stage4_results"
OUT_MD = A / "out" / f"{_OUT}.md"
OUT_CSV = A / "out" / f"{_OUT}.csv"

LOCKED = {
    "retrieval-f001": {
        "evidence_type": "point_field",
        "determining_set": "dinoco-airlines.sqlite loyalty.{status,miles,miles_ytd}",
        "baseline_gold": "Gold Voyager / 38450 miles / 14280 ytd",
        "counterfactual_gold": "Silver Voyager / 8620 miles / 8620 ytd",
        "intervention": "UPDATE loyalty SET status=Silver Voyager, miles=8620, miles_ytd=8620",
    },
    "aggregation-f003": {
        "evidence_type": "aggregation",
        "determining_set": "filed prior-year tax_returns.{federal_refund_amount,state_refund_amount}",
        "baseline_gold": "n_filed=2 combined=4871.70 years=[2023,2024]",
        "counterfactual_gold": "n_filed=2 combined=400.00 years=[2023,2024]",
        "intervention": "filed 2023 refunds 100+50; filed 2024 refunds 200+50; 2025 untouched",
    },
    "preference_inference-f018": {
        "evidence_type": "multi_record",
        "determining_set": "batbucks holdings GME.{shares,avg_cost} AND oddsmarket WILL-GME-100-YEAREND YES",
        "baseline_gold": "GME 85@42.12 AND OM YES 200 active",
        "counterfactual_gold": "GME shares=0 AND OM YES shares=0 status=closed",
        "intervention": "GME shares=0; OM YES shares=0 status=closed (joint D, not 2x2)",
    },
    "counterfactual-f004": {
        "evidence_type": "contradiction_cross_source",
        "determining_set": "Gringotts improv income + SpeedTax 1099 amounts (tuition/calendar/mail held fixed)",
        "baseline_gold": "pays tuition AND receives 1099 (contradiction present)",
        "counterfactual_gold": "pays tuition; improv income/1099 amount = 0 (contradiction absent)",
        "intervention": "zero positive improv transactions; zero 1099_amount_0 and 1099 nonemployee_compensation",
    },
}

COLS = [
    "task_id",
    "evidence_type",
    "determining_set",
    "baseline_gold",
    "counterfactual_gold",
    "baseline_DV",
    "counterfactual_DV",
    "tracks_determining_set",
    "judge_score_baseline",
    "judge_score_counterfactual",
    "intervention",
    "status",
]


def load_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text())


def last_done(cell: Path) -> str:
    traj = None
    for candidate in cell.glob("*/traj.jsonl"):
        traj = candidate
        break
    if traj is None:
        traj = cell / "traj.jsonl"
    if not traj.exists():
        return ""
    last = ""
    for line in traj.read_text().splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        if obj.get("action") == "DONE" or obj.get("done") is True:
            last = obj.get("response") or ""
    return last


def judge_score(cell: Path) -> str:
    scores = load_json(cell / "scores.json")
    if scores and scores.get("rows"):
        raw = scores["rows"][0].get("raw")
        if raw is not None:
            return str(raw)
        score = scores["rows"][0].get("score")
        if score is not None:
            return str(int(round(float(score) * 100))) if float(score) <= 1 else str(score)
    for judged in cell.glob("*/rubric_judge_result.json"):
        data = load_json(judged)
        if data and "result" in data:
            return str(data["result"])
    return "missing"


def guest(cell: Path, task_id: str):
    path = cell / f"{task_id}.guest.json"
    if path.exists():
        return load_json(path)
    hits = list(cell.glob("*.guest.json"))
    return load_json(hits[0]) if hits else None


def dv_f001(text: str) -> str:
    low = text.lower()
    silver = "silver" in low
    gold = "gold" in low
    miles = re.findall(r"\b(\d{4,6})\b", text.replace(",", ""))
    return f"silver={silver} gold={gold} numbers={miles[:6]}"


def dv_f003(text: str) -> str:
    nums = re.findall(r"\$?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?|[0-9]+\.[0-9]+)", text)
    compact = [n.replace(",", "") for n in nums[:12]]
    return f"numbers={compact}"


def dv_f018(text: str) -> str:
    low = text.lower()
    open_gme = bool(re.search(r"\b85\b", text)) or ("gme" in low and "share" in low and "0 share" not in low)
    yes_bet = "200" in text and ("yes" in low or "oddsmarket" in low or "gamestop" in low)
    return f"asserts_gme_shares={open_gme} asserts_yes_bet={yes_bet}"


def dv_f004(text: str) -> str:
    low = text.lower()
    flags = bool(re.search(r"contradict|conflict|inconsist|both student and teacher|student.vs.teacher|can't be both|cannot be both", low))
    no_flag = bool(re.search(r"no contradiction|not a contradiction|no conflict|all.clear", low))
    if flags and not no_flag:
        flag = "yes"
    elif no_flag and not flags:
        flag = "no"
    else:
        flag = "unclear"
    savings = "unclear"
    if re.search(r"1099|nonemployee|teaching income", low):
        savings = "mentions_1099"
    return f"contradiction_flag={flag} savings_1099={savings}"


DV_FN = {
    "retrieval-f001": dv_f001,
    "aggregation-f003": dv_f003,
    "preference_inference-f018": dv_f018,
    "counterfactual-f004": dv_f004,
}


def tracks(task_id: str, base_dv: str, cf_dv: str, base_txt: str, cf_txt: str) -> str:
    if not cf_txt:
        return "unclear"
    b, c = base_txt.lower(), cf_txt.lower()
    if task_id == "retrieval-f001":
        if "silver" in c and ("8620" in c.replace(",", "") or "8,620" in cf_txt):
            return "yes"
        if "gold" in c and "38450" in c.replace(",", ""):
            return "no"
        return "unclear"
    if task_id == "aggregation-f003":
        cf_flat = cf_txt.replace(",", "")
        if re.search(r"\b400(\.0+)?\b", cf_flat) and "4871" not in cf_flat:
            return "yes"
        if "4871" in cf_flat:
            return "no"
        return "unclear"
    if task_id == "preference_inference-f018":
        still_85 = bool(re.search(r"\b85\b", cf_txt))
        still_200 = bool(re.search(r"\b200\b", cf_txt)) and "yes" in c
        if still_85 or still_200:
            return "no"
        if "gme" in c or "gamestop" in c:
            return "yes"
        return "unclear"
    if task_id == "counterfactual-f004":
        base_flag = "yes" in dv_f004(base_txt)
        cf_flag = dv_f004(cf_txt)
        if "contradiction_flag=yes" in dv_f004(base_txt) and "contradiction_flag=no" in cf_flag:
            return "yes"
        if "contradiction_flag=yes" in cf_flag:
            return "no"
        return "unclear"
    return "unclear"


def cell_dir(task_id: str, which: str) -> Path:
    return A / "results" / f"{_PREFIX}{task_id}" / which


def row_for(task_id: str) -> dict:
    meta = LOCKED[task_id]
    base = cell_dir(task_id, "base")
    cf = cell_dir(task_id, "cf")
    base_txt = last_done(base)
    cf_txt = last_done(cf)
    dv_fn = DV_FN[task_id]
    base_dv = dv_fn(base_txt) if base_txt else "missing"
    cf_dv = dv_fn(cf_txt) if cf_txt else "missing"
    g_cf = guest(cf, task_id) or {}
    g_base = guest(base, task_id) or {}
    status = "ok"
    if not base_txt and not (base / "scores.json").exists() and not list(base.glob("*/traj.jsonl")):
        status = "failure"
    if g_cf and g_cf.get("gold_moved") is False:
        status = "technical_failure"
    track = tracks(task_id, base_dv, cf_dv, base_txt, cf_txt)
    if status == "ok" and track == "no":
        status = "null"
    if status == "ok" and (base_dv == "missing" or cf_dv == "missing"):
        status = "failure"
    return {
        "task_id": task_id,
        "evidence_type": meta["evidence_type"],
        "determining_set": meta["determining_set"],
        "baseline_gold": meta["baseline_gold"],
        "counterfactual_gold": meta["counterfactual_gold"],
        "baseline_DV": base_dv.replace("|", "/"),
        "counterfactual_DV": cf_dv.replace("|", "/"),
        "tracks_determining_set": track,
        "judge_score_baseline": judge_score(base),
        "judge_score_counterfactual": judge_score(cf),
        "intervention": meta["intervention"],
        "status": status,
        "_base_probe": (g_base.get("probe_before") or "")[:240],
        "_cf_moved": g_cf.get("gold_moved"),
    }


def main() -> int:
    rows = [row_for(tid) for tid in LOCKED]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    title = "Stage 4 confirmatory Claude"
    body = (
        "Stage 1–2 frozen. Stage 3 probes frozen. This table is Stage 4 Claude "
        "on the 4 identifiable frozen-sample tasks only."
    )
    if TAG:
        title = f"Stage 4 exploratory {TAG} (same frozen tasks/SQL as Claude)"
        body = (
            "Exploratory cross-model transfer under the same frozen "
            "task/intervention protocol. Agent/model changed "
            f"({TAG}); tasks, SQL, rubric, and DVs are unchanged. Not "
            "confirmatory Qwen replication. Claude Stage 4 tables were not modified."
        )
    lines = [
        f"# {title}",
        "",
        body,
        "",
        "Funnel: 184 → 10 eligible → 8 confirmatory sample → 4 confounded (no Claude, remain in sample) → 4 identifiable Claude (this session). Reserves retrieval-f003 / retrieval-f016 were not promoted.",
        "",
        "Confounded sample members not run: retrieval-f029, retrieval-f030, aggregation-f018, preference_inference-f004.",
        "",
        "Judge score is auxiliary. Attribution DV is the final-answer field named in PROMPT_STAGE4.md.",
        "",
        "| " + " | ".join(COLS) + " |",
        "|" + "|".join(["---"] * len(COLS)) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[c]).replace("\n", " ") for c in COLS) + " |")
    lines += ["", "Nulls and failures are kept as rows. No sampled id was omitted."]
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_CSV}")
    for row in rows:
        print(f"{row['task_id']}\t{row['tracks_determining_set']}\t{row['status']}\tbase={row['judge_score_baseline']}\tcf={row['judge_score_counterfactual']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
