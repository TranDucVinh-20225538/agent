#!/usr/bin/env python3
"""Classify Path A on admitted JSON.

Pass 1 (no V): episode_status + I classify via extract_i.
Pass 2: join released oracle V (cum_reward).
Pass 3: HIT/MISS for WA/VWA mechanical exact/must_include/url only.
"""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote

from extract_i import classify_i, episode_status, extract_ans, extract_url

ROOT = Path(__file__).resolve().parent
KEYS = ROOT / "schema" / "admitted_keys.csv"
DEST = ROOT / "data" / "admitted"
OUT = ROOT / "out"
GOLD_WA = ROOT / "schema" / "webarena_test.raw.json"
VWA_META = ROOT / "schema" / "visualwebarena.csv"
VWA_RAW = {
    "classifieds": ROOT / "schema" / "vwa_classifieds.raw.json",
    "reddit": ROOT / "schema" / "vwa_reddit.raw.json",
    "shopping": ROOT / "schema" / "vwa_shopping.raw.json",
}

JQ = (
    "{valid,benchmark,goal,"
    "summary_info:{err_msg:.summary_info.err_msg,cum_reward:.summary_info.cum_reward},"
    "steps:[.steps[]|{action,url,chat_messages}]}"
)


def slim_load(path: Path) -> dict:
    proc = subprocess.run(
        ["jq", "-c", JQ, str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


def v_bin(cum) -> str:
    if cum is None:
        return "UNKNOWN_V"
    try:
        x = float(cum)
    except (TypeError, ValueError):
        return "UNKNOWN_V"
    return "SUCCESS" if x > 0 else "FAIL"


def load_wa_gold() -> dict:
    data = json.loads(GOLD_WA.read_text())
    out = {}
    for item in data:
        out[int(item["task_id"])] = item.get("eval") or {}
    return out


def load_vwa_site_gold() -> dict[str, list]:
    out = {}
    for site, path in VWA_RAW.items():
        out[site] = json.loads(path.read_text())
    return out


def load_vwa_sites() -> dict[str, str]:
    m = {}
    with VWA_META.open(newline="") as f:
        for row in csv.DictReader(f):
            m[row["task_name"]] = row["sites"].strip().split()[0]
    return m


def goal_core(goal: str | None) -> str:
    if not goal:
        return ""
    g = str(goal)
    for sep in ("\nInput image", "Input image"):
        if sep in g:
            g = g.split(sep, 1)[0]
    return g.strip()


def vwa_eval(site_gold: dict, site: str, goal: str) -> dict | None:
    items = site_gold.get(site) or []
    core = goal_core(goal)
    hits = [item for item in items if str(item.get("intent") or "").strip() == core]
    if len(hits) == 1:
        return hits[0].get("eval") or {}
    prefix = [
        item
        for item in items
        if core and str(item.get("intent") or "").strip() and core.startswith(str(item.get("intent")).strip())
    ]
    if len(prefix) == 1:
        return prefix[0].get("eval") or {}
    return None


def corr_string(ans: str | None, ev: dict) -> str:
    if not ans or not str(ans).strip():
        return "SKIP"
    refs = (ev or {}).get("reference_answers") or {}
    if not isinstance(refs, dict):
        refs = {}
    exact = refs.get("exact_match")
    must = refs.get("must_include") or []
    fuzzy = refs.get("fuzzy_match") or []
    if exact not in (None, ""):
        return "HIT" if str(ans).strip() == str(exact).strip() else "MISS"
    if must:
        a = str(ans)
        return "HIT" if all(str(m) in a for m in must) else "MISS"
    if fuzzy:
        return "CORR_UNEVALUABLE"
    return "NO_GOLD"


def corr_url(url: str | None, ev: dict) -> str:
    if not url:
        return "SKIP"
    ref = (ev or {}).get("reference_url") or ""
    if not str(ref).strip():
        return "NO_GOLD"
    pred = unquote(url).rstrip("/")
    refn = unquote(str(ref)).rstrip("/")
    return "HIT" if (refn in pred or pred in refn) else "MISS"


def combine_string_url(cs: str, cu: str) -> str:
    bad = {"CORR_UNEVALUABLE", "NO_GOLD", "SKIP", ""}
    if cs in bad or cu in bad:
        if "CORR_UNEVALUABLE" in (cs, cu):
            return "CORR_UNEVALUABLE"
        return "NO_GOLD"
    return "HIT" if cs == "HIT" and cu == "HIT" else "MISS"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    gold_wa = load_wa_gold()
    gold_vwa_site = load_vwa_site_gold()
    vwa_sites = load_vwa_sites()
    rows_in = list(csv.DictReader(KEYS.open()))
    out_rows = []
    missing = 0
    jq_fail = 0
    for i, key in enumerate(rows_in, 1):
        path = DEST / key["rel_path"]
        if not path.exists():
            missing += 1
            continue
        try:
            traj = slim_load(path)
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            jq_fail += 1
            print("JQ_FAIL", key["rel_path"], e, flush=True)
            continue
        status = episode_status(traj)
        fam = key["family"]
        i_fam = "string" if fam == "assistant" else fam
        e = ""
        ans = url = None
        if status == "ELIGIBLE":
            e = classify_i(i_fam, traj)
            ans = extract_ans(traj)
            url = extract_url(traj)
        v = v_bin((traj.get("summary_info") or {}).get("cum_reward")) if status == "ELIGIBLE" else ""
        corr = ""
        gold_used = ""
        if status == "ELIGIBLE" and e == "DETERMINING" and fam != "assistant":
            bench = key["benchmark"]
            ev = None
            if bench == "webarena":
                num = key["task_id"].rsplit(".", 1)[-1]
                ev = gold_wa.get(int(num)) if num.isdigit() else None
                gold_used = "wa" if ev else ""
            elif bench == "visualwebarena":
                canon = key["task_id"].replace(".resized", "")
                site = vwa_sites.get(canon, "")
                ev = vwa_eval(gold_vwa_site, site, traj.get("goal") or "")
                gold_used = f"vwa:{site}" if ev else ""
            if ev:
                if fam == "string":
                    corr = corr_string(ans, ev)
                elif fam == "url":
                    corr = corr_url(url, ev)
                elif fam == "string_url":
                    corr = combine_string_url(corr_string(ans, ev), corr_url(url, ev))
            else:
                corr = "NO_GOLD"
        out_rows.append(
            {
                "benchmark": key["benchmark"],
                "task_id": key["task_id"],
                "model_name": key["model_name"],
                "exp_name": key["exp_name"],
                "family": fam,
                "episode": status,
                "E": e,
                "V": v,
                "corr": corr,
                "gold": gold_used,
            }
        )
        if i % 25 == 0:
            print(f"classified {i}/{len(rows_in)} missing={missing} jq_fail={jq_fail}", flush=True)

    csv_path = OUT / "path_a_cells.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "benchmark",
                "task_id",
                "model_name",
                "exp_name",
                "family",
                "episode",
                "E",
                "V",
                "corr",
                "gold",
            ],
        )
        w.writeheader()
        w.writerows(out_rows)

    elig = [r for r in out_rows if r["episode"] == "ELIGIBLE"]
    execf = [r for r in out_rows if r["episode"] == "EXEC_FAIL"]
    print("n_rows", len(out_rows), "missing_json", missing, "jq_fail", jq_fail)
    print("EXEC_FAIL", len(execf), "ELIGIBLE", len(elig))
    print("E", Counter(r["E"] for r in elig))
    print("V among ELIGIBLE", Counter(r["V"] for r in elig))
    print("E x V", Counter((r["E"], r["V"]) for r in elig))
    ab = [r for r in elig if r["family"] == "assistant"]
    wav = [r for r in elig if r["family"] != "assistant"]
    print("AssistantBench ELIGIBLE", len(ab), "E", Counter(r["E"] for r in ab), "ExV", Counter((r["E"], r["V"]) for r in ab))
    print("WA/VWA ELIGIBLE", len(wav), "E", Counter(r["E"] for r in wav), "ExV", Counter((r["E"], r["V"]) for r in wav))
    print("corr WA/VWA DETERMINING", Counter(r["corr"] for r in wav if r["E"] == "DETERMINING"))
    print("wrote", csv_path)


if __name__ == "__main__":
    main()
