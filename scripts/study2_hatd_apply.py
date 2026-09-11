#!/usr/bin/env python3
"""Apply locked hat-D extractor to Study 2 A legs, then STS / Y via matching.py.

Read-only on frozen archives. No LLM. No re-judge.
"""
from __future__ import annotations

import csv
import hashlib
import json
import random
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

VINH = Path("/data2/hpcshared/Vinh-/agent")
VINH_FROZEN = Path("/data2/hpcshared/Vinh/agent")
OUT = VINH / "out"
sys.path.insert(0, str(VINH / "scripts"))
sys.path.insert(0, str(VINH / "paper/paper2_counterfactual_eval/protocol"))

from study2_hatd_extract import (  # noqa: E402
    extract_leg,
    load_lock,
    GOLD_LOCK,
)
from matching import (  # noqa: E402
    Component,
    Kind,
    Role,
    binary_track,
    match_value,
    sts_leg,
)

LANES = {
    "gpt": VINH_FROZEN / "results/paper2_exec/study2-gpt",
    "flash": VINH / "results/paper2_exec/hpc-flash-small-gate0a-postpatch",
    "claude": VINH_FROZEN / "results/paper2_exec/study2-claude",
}
EXTRACTOR_SHA = "3242c30a1423f9ef90754809e50cd2698c5560b5"
SEED = 20260904
COMMON = [
    "counterfactual-f010",
    "preference_inference-f014",
    "retrieval-f002",
    "retrieval-f009",
]


def _jsonable(v: Any) -> Any:
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, dict):
        return {k: _jsonable(x) for k, x in v.items()}
    return v


def components_for(task: str, lock: dict[str, Any]) -> list[Component]:
    rows = []
    for cid, spec in (lock["components"][task]).items():
        role = Role(spec.get("role") or "determining")
        kind = Kind(spec["kind"])
        kk = tuple((k, Kind(v)) for k, v in (spec.get("key_kinds") or {}).items())
        rows.append(Component(id=cid, kind=kind, role=role, weight=Decimal("1"), key_kinds=kk))
    return rows


def match_one(spec: dict[str, Any], gold: Any, reported: Any) -> bool:
    if gold is None or reported is None:
        return False
    kind = Kind(spec["kind"])
    try:
        if kind is Kind.STATE:
            key_kinds = {k: Kind(v) for k, v in (spec.get("key_kinds") or {}).items()}
            if not isinstance(gold, dict) or not isinstance(reported, dict):
                return False
            return match_value(kind, gold, reported, key_kinds=key_kinds)
        return match_value(kind, gold, reported)
    except (TypeError, ValueError, InvalidOperation, ArithmeticError):
        return False


def bootstrap_mean(diffs: list[float], n: int = 5000, seed: int = SEED) -> dict[str, Any]:
    rng = random.Random(seed)
    k = len(diffs)
    if k == 0:
        return {"n": 0}
    obs = sum(diffs) / k
    dist = []
    for _ in range(n):
        samp = [diffs[rng.randrange(k)] for _ in range(k)]
        dist.append(sum(samp) / k)
    dist.sort()
    return {
        "n_pairs": k,
        "observed_mean_diff": obs,
        "ci95": [dist[int(0.025 * n)], dist[min(n - 1, int(0.975 * n))]],
        "n_boot": n,
        "seed": seed,
    }


def sgn(x: float | None) -> int | None:
    if x is None:
        return None
    if abs(x) < 1e-12:
        return 0
    return 1 if x > 0 else -1


def load_s_table() -> dict[tuple[str, str], dict[str, Any]]:
    rows = {}
    with (OUT / "study2_valid_pairs.csv").open() as f:
        for r in csv.DictReader(f):
            rows[(r["lane"], r["task"])] = {
                "s0": int(r["s0"]) if r["s0"] != "" else None,
                "s1": int(r["s1"]) if r["s1"] != "" else None,
                "delta_s": int(r["delta_s"]) if r["delta_s"] != "" else None,
            }
    return rows


def main() -> int:
    lock = load_lock()
    pairs = json.loads((OUT / "study2_valid_pairs.json").read_text())["lanes"]
    s_table = load_s_table()
    legs_path = OUT / "study2_hatd_legs.jsonl"
    n_legs = 0
    pair_rows: list[dict[str, Any]] = []

    with legs_path.open("w") as out_f:
        for lane, meta in pairs.items():
            root = LANES[lane]
            for task in meta["tasks"]:
                comps = components_for(task, lock)
                specs = lock["components"][task]
                leg_extracted = {}
                for g in ("G0", "G1"):
                    rec = extract_leg(task, root / task / g, lock)
                    rec["lane"] = lane
                    rec["leg"] = g
                    rec["extractor_sha"] = EXTRACTOR_SHA
                    rec["gold_lock"] = str(GOLD_LOCK)
                    ans = ""
                    if rec.get("traj"):
                        from study2_hatd_extract import final_answer_from_traj

                        ans = final_answer_from_traj(Path(rec["traj"]))
                    rec["answer_sha256"] = hashlib.sha256(ans.encode()).hexdigest() if ans else None
                    matches = {
                        cid: match_one(specs[cid], rec["gold"].get(cid), rec["reported"].get(cid))
                        for cid in specs
                    }
                    rec["matches"] = matches
                    rec["sts_leg"] = float(sts_leg(comps, matches))
                    out_f.write(json.dumps(rec, default=str) + "\n")
                    leg_extracted[g] = rec
                    n_legs += 1
                m0 = leg_extracted["G0"]["matches"]
                m1 = leg_extracted["G1"]["matches"]
                sts0 = Decimal(str(leg_extracted["G0"]["sts_leg"]))
                sts1 = Decimal(str(leg_extracted["G1"]["sts_leg"]))
                y = binary_track(comps, m0, m1)
                s = s_table.get((lane, task), {})
                pair_rows.append({
                    "lane": lane,
                    "task": task,
                    "sts0": float(sts0),
                    "sts1": float(sts1),
                    "sts": float((sts0 + sts1) / 2),
                    "Y": int(y),
                    "s0": s.get("s0"),
                    "s1": s.get("s1"),
                    "delta_s": s.get("delta_s"),
                    "matches0": m0,
                    "matches1": m1,
                    "gold_null_any": any(
                        leg_extracted[g]["gold"].get(cid) is None
                        for g in ("G0", "G1")
                        for cid in specs
                    ),
                })

    json.dump(pair_rows, (OUT / "study2_sts_pairs.json").open("w"), indent=2)
    with (OUT / "study2_sts_pairs.csv").open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["lane", "task", "sts0", "sts1", "sts", "Y", "s0", "s1", "delta_s", "gold_null_any"],
        )
        w.writeheader()
        for r in pair_rows:
            w.writerow({k: r[k] for k in w.fieldnames})

    by = {(r["lane"], r["task"]): r for r in pair_rows}

    def mean_on(lane: str, field: str) -> float | None:
        xs = [r[field] for r in pair_rows if r["lane"] == lane and r[field] is not None]
        return (sum(xs) / len(xs)) if xs else None

    md = [
        "# Study 2 STS / Y on A (EXPLORATORY)",
        "",
        f"- extractor SHA: `{EXTRACTOR_SHA}`",
        f"- legs written: {n_legs} → `out/study2_hatd_legs.jsonl`",
        "- Y = binary_track on G0∧G1; non-A not recoded as Y=0",
        "- `preference_inference-f010` gold=null (no frozen latency formula) → fail-closed match 0",
        "",
        "| lane | task | STS0 | STS1 | STS | Y | S0 | S1 | ΔS | gold_null |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in pair_rows:
        md.append(
            f"| {r['lane']} | {r['task']} | {r['sts0']:.3f} | {r['sts1']:.3f} | {r['sts']:.3f} | {r['Y']} | {r['s0']} | {r['s1']} | {r['delta_s']} | {r['gold_null_any']} |"
        )
    md += [
        "",
        f"- GPT mean pair-STS={mean_on('gpt','sts')} mean Y={mean_on('gpt','Y')} n=9",
        f"- Flash mean pair-STS={mean_on('flash','sts')} mean Y={mean_on('flash','Y')} n=8",
        f"- Claude mean pair-STS={mean_on('claude','sts')} mean Y={mean_on('claude','Y')} n=1 (not ranked)",
        "",
    ]
    (OUT / "study2_sts_pairs.md").write_text("\n".join(md) + "\n")

    # §6.1(g) common support
    common_rows = []
    for task in COMMON:
        g = by[("gpt", task)]
        f = by[("flash", task)]
        ds = (f["s0"] - g["s0"]) if (f["s0"] is not None and g["s0"] is not None) else None
        dsts = f["sts"] - g["sts"]
        common_rows.append({
            "task": task,
            "S0_gpt": g["s0"],
            "S0_flash": f["s0"],
            "delta_S_gpt": g["delta_s"],
            "delta_S_flash": f["delta_s"],
            "STS_gpt": g["sts"],
            "STS_flash": f["sts"],
            "Y_gpt": g["Y"],
            "Y_flash": f["Y"],
            "delta_S0_flash_minus_gpt": ds,
            "delta_STS_flash_minus_gpt": dsts,
            "sign_delta_S0": sgn(ds),
            "sign_delta_STS": sgn(dsts),
            "sign_disagree": int(sgn(ds) != sgn(dsts)) if ds is not None else None,
        })

    n_disagree = sum(1 for r in common_rows if r["sign_disagree"])
    mean_s0_gpt = sum(r["S0_gpt"] for r in common_rows) / 4
    mean_s0_flash = sum(r["S0_flash"] for r in common_rows) / 4
    mean_sts_gpt = sum(r["STS_gpt"] for r in common_rows) / 4
    mean_sts_flash = sum(r["STS_flash"] for r in common_rows) / 4
    argmax_s = "flash" if mean_s0_flash > mean_s0_gpt else ("gpt" if mean_s0_gpt > mean_s0_flash else "tie")
    argmax_sts = "flash" if mean_sts_flash > mean_sts_gpt else ("gpt" if mean_sts_gpt > mean_sts_flash else "tie")
    boot_s = bootstrap_mean([r["delta_S0_flash_minus_gpt"] for r in common_rows])
    boot_sts = bootstrap_mean([r["delta_STS_flash_minus_gpt"] for r in common_rows])

    lopo = []
    for leave in COMMON:
        sub = [r for r in common_rows if r["task"] != leave]
        ms_g = sum(r["S0_gpt"] for r in sub) / 3
        ms_f = sum(r["S0_flash"] for r in sub) / 3
        mt_g = sum(r["STS_gpt"] for r in sub) / 3
        mt_f = sum(r["STS_flash"] for r in sub) / 3
        a_s = "flash" if ms_f > ms_g else ("gpt" if ms_g > ms_f else "tie")
        a_t = "flash" if mt_f > mt_g else ("gpt" if mt_g > mt_f else "tie")
        lopo.append({
            "leave_out": leave,
            "argmax_S0": a_s,
            "argmax_STS": a_t,
            "selection_disagree": a_s != a_t,
            "mean_delta_S0": ms_f - ms_g,
            "mean_delta_STS": mt_f - mt_g,
        })
    lopo_fragile = any(x["argmax_S0"] != argmax_s or x["argmax_STS"] != argmax_sts for x in lopo)

    sel = {
        "label": "EXPLORATORY §6.1(g)",
        "extractor_sha": EXTRACTOR_SHA,
        "layer_b_confirmatory": False,
        "common_support": COMMON,
        "n_common": 4,
        "mean_S0_gpt": mean_s0_gpt,
        "mean_S0_flash": mean_s0_flash,
        "mean_STS_gpt": mean_sts_gpt,
        "mean_STS_flash": mean_sts_flash,
        "argmax_S0_among_ranked": argmax_s,
        "argmax_STS_among_ranked": argmax_sts,
        "selection_disagreement": argmax_s != argmax_sts,
        "n_sign_disagree_tasks": n_disagree,
        "sign_disagree_tasks": [r["task"] for r in common_rows if r["sign_disagree"]],
        "paired_bootstrap_mean_S0_flash_minus_gpt": boot_s,
        "paired_bootstrap_mean_STS_flash_minus_gpt": boot_sts,
        "lopo": lopo,
        "lopo_argmax_fragile": lopo_fragile,
        "rows": common_rows,
    }
    json.dump(sel, (OUT / "study2_selection_g_sts.json").open("w"), indent=2)
    with (OUT / "study2_selection_g_sts.csv").open("w", newline="") as f:
        fields = [
            "task", "S0_gpt", "S0_flash", "STS_gpt", "STS_flash", "Y_gpt", "Y_flash",
            "delta_S0_flash_minus_gpt", "delta_STS_flash_minus_gpt",
            "sign_delta_S0", "sign_delta_STS", "sign_disagree",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in common_rows:
            w.writerow({k: r[k] for k in fields})

    (OUT / "study2_selection_g_sts.md").write_text(
        "\n".join([
            "# §6.1(g) exploratory ΔSTS on common support 4",
            "",
            f"- extractor `{EXTRACTOR_SHA}`. Layer B **NOT confirmatory** (§6.1(c)).",
            f"- common: {COMMON}",
            f"- mean S0 GPT={mean_s0_gpt} Flash={mean_s0_flash} → argmax_S0=**{argmax_s}**",
            f"- mean STS GPT={mean_sts_gpt:.3f} Flash={mean_sts_flash:.3f} → argmax_STS=**{argmax_sts}**",
            f"- selection disagreement (argmax_S0 vs argmax_STS): **{argmax_s != argmax_sts}**",
            f"- sign(ΔS0)≠sign(ΔSTS) on {n_disagree}/4 tasks: {[r['task'] for r in common_rows if r['sign_disagree']]}",
            f"- bootstrap mean(S0_Flash−S0_GPT)={boot_s}",
            f"- bootstrap mean(STS_Flash−STS_GPT)={boot_sts}",
            f"- LOPO argmax fragile: {lopo_fragile}",
            "",
            "| task | S0 GPT | S0 Flash | STS GPT | STS Flash | Y GPT | Y Flash | ΔS0 | ΔSTS | sign≠ |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ] + [
            f"| {r['task']} | {r['S0_gpt']} | {r['S0_flash']} | {r['STS_gpt']:.3f} | {r['STS_flash']:.3f} | {r['Y_gpt']} | {r['Y_flash']} | {r['delta_S0_flash_minus_gpt']} | {r['delta_STS_flash_minus_gpt']:.3f} | {r['sign_disagree']} |"
            for r in common_rows
        ] + ["", "LOPO:", ""] + [
            f"- leave {x['leave_out']}: argmax_S0={x['argmax_S0']} argmax_STS={x['argmax_STS']} disagree={x['selection_disagree']}"
            for x in lopo
        ] + [""])
    )

    # Layer A: S0 vs Y on ranked A
    la_rows = [r for r in pair_rows if r["lane"] in ("gpt", "flash")]
    n_y = sum(r["Y"] for r in la_rows)

    def calib(lane: str) -> dict[str, Any]:
        xs = [r for r in pair_rows if r["lane"] == lane]
        yt = [r for r in xs if r["Y"] == 1]
        yf = [r for r in xs if r["Y"] == 0]
        def mean_s0(rr):
            vs = [r["s0"] for r in rr if r["s0"] is not None]
            return (sum(vs) / len(vs)) if vs else None
        return {
            "n": len(xs),
            "n_Y1": len(yt),
            "n_Y0": len(yf),
            "mean_S0": mean_s0(xs),
            "mean_S0_Y1": mean_s0(yt),
            "mean_S0_Y0": mean_s0(yf),
            "mean_STS": mean_on(lane, "sts"),
            "mean_Y": mean_on(lane, "Y"),
        }

    layer = {
        "label": "EXPLORATORY Layer A (S vs Y on A)",
        "extractor_sha": EXTRACTOR_SHA,
        "n_ranked_pairs": len(la_rows),
        "n_Y1": n_y,
        "gpt": calib("gpt"),
        "flash": calib("flash"),
        "claude": calib("claude"),
        "note": "Small n. Do not treat as confirmatory calibration. Incomplete legs still not Y=0.",
    }
    json.dump(layer, (OUT / "study2_layerA_y.json").open("w"), indent=2)
    with (OUT / "study2_layerA_y.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["lane", "task", "S0", "S1", "delta_S", "STS", "Y"])
        w.writeheader()
        for r in pair_rows:
            w.writerow({
                "lane": r["lane"], "task": r["task"], "S0": r["s0"], "S1": r["s1"],
                "delta_S": r["delta_s"], "STS": r["sts"], "Y": r["Y"],
            })
    (OUT / "study2_layerA_y.md").write_text(
        "\n".join([
            "# Layer A (EXPLORATORY) — S vs Y on A",
            "",
            f"- extractor `{EXTRACTOR_SHA}`. Ranked roster GPT+Flash. Claude coverage-only.",
            f"- GPT: n=9 Y=1 in {layer['gpt']['n_Y1']} mean S0={layer['gpt']['mean_S0']} (Y1 {layer['gpt']['mean_S0_Y1']} / Y0 {layer['gpt']['mean_S0_Y0']}) mean STS={layer['gpt']['mean_STS']}",
            f"- Flash: n=8 Y=1 in {layer['flash']['n_Y1']} mean S0={layer['flash']['mean_S0']} (Y1 {layer['flash']['mean_S0_Y1']} / Y0 {layer['flash']['mean_S0_Y0']}) mean STS={layer['flash']['mean_STS']}",
            f"- Claude: n=1 Y={layer['claude']['n_Y1']} (not ranked)",
            "- Incomplete ≠ Y=0 (§6.1(e)).",
            "",
        ])
    )

    bias = json.loads((OUT / "study2_selection_g_completion_bias.json").read_text())
    bias["label"] = "EXPLORATORY §6.1(e) coverage + Y on A only"
    bias["Y_on_A"] = {
        "gpt": {"|A|": 9, "n_Y1": layer["gpt"]["n_Y1"], "mean_Y": layer["gpt"]["mean_Y"]},
        "flash": {"|A|": 8, "n_Y1": layer["flash"]["n_Y1"], "mean_Y": layer["flash"]["mean_Y"]},
        "claude": {"|A|": 1, "n_Y1": layer["claude"]["n_Y1"], "mean_Y": layer["claude"]["mean_Y"]},
    }
    bias["note"] = "Y defined only on A. TERMINAL_FAIL / one-leg DONE still not recoded Y=0."
    json.dump(bias, (OUT / "study2_selection_g_completion_bias.json").open("w"), indent=2)
    (OUT / "study2_selection_g_completion_bias.md").write_text(
        "# §6.1(e) completion-conditional bias (coverage, not Y=0)\n\n"
        f"- GPT DONE 32/57, |A|=9, Y=1 on {layer['gpt']['n_Y1']}/9 of A\n"
        f"- Flash DONE 29/57, |A|=8, Y=1 on {layer['flash']['n_Y1']}/8 of A\n"
        f"- Claude DONE 4/57, |A|=1, Y=1 on {layer['claude']['n_Y1']}/1 of A\n"
        "- Incomplete ≠ Y=0. Y is not defined off A.\n"
    )

    print(json.dumps({
        "n_legs": n_legs,
        "extractor_sha": EXTRACTOR_SHA,
        "argmax_S0": argmax_s,
        "argmax_STS": argmax_sts,
        "selection_disagreement": argmax_s != argmax_sts,
        "n_sign_disagree": n_disagree,
        "mean_STS": {"gpt": mean_on("gpt", "sts"), "flash": mean_on("flash", "sts"), "claude": mean_on("claude", "sts")},
        "mean_Y": {"gpt": mean_on("gpt", "Y"), "flash": mean_on("flash", "Y"), "claude": mean_on("claude", "Y")},
        "lopo_fragile": lopo_fragile,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
