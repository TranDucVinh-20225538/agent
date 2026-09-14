#!/usr/bin/env python3
"""One-shot join of locked M1a rows to locked Study-2 S/Y/DONE.

Implements experiment_m1a_location/PROTOCOL.md. Read-only. No extractor. No traj OCR.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = Path(__file__).resolve().parent

M1A = [
    ("flash", "counterfactual-f010", "G0", "liquid_cash"),
    ("flash", "counterfactual-f013", "G0", "batbucks_dividends"),
    ("flash", "counterfactual-f013", "G0", "gringotts_savings"),
    ("flash", "counterfactual-f013", "G1", "gringotts_savings"),
    ("flash", "retrieval-f009", "G1", "nyc_flight_confirmation"),
    ("flash", "retrieval-f010", "G1", "host_name"),
    ("gpt", "aggregation-f020", "G0", "batbucks_cash"),
    ("gpt", "retrieval-f009", "G0", "nyc_hotel_confirmation"),
    ("gpt", "retrieval-f009", "G1", "nyc_flight_confirmation"),
    ("flash", "counterfactual-f005", "G1", "gme_shares"),
    ("claude", "counterfactual-f005", "G0", "gme_avg_cost"),
    ("claude", "counterfactual-f005", "G0", "gme_shares"),
    ("flash", "aggregation-f020", "G1", "batbucks_cash"),
]


def load_csv(path: Path) -> list[dict]:
    with path.open() as f:
        return list(csv.DictReader(f))


def main() -> int:
    vp = { (r["lane"], r["task"]): r for r in load_csv(ROOT / "out/study2_valid_pairs.csv") }
    la = { (r["lane"], r["task"]): r for r in load_csv(ROOT / "out/study2_layerA.csv") }
    sts = json.loads((ROOT / "out/study2_sts_pairs.json").read_text())
    sts_ix = { (r["lane"], r["task"]): r for r in sts }
    cc_path = ROOT / "out/study2_completion_conditional.json"
    if not cc_path.exists():
        cc_path = ROOT / ".hpc_import/out/study2_completion_conditional.json"
    cc = json.loads(cc_path.read_text())
    high = {}
    for lane, block in cc["lanes"].items():
        for cell in block.get("high_S_no_DONE_cells") or []:
            high[(lane, cell["task"], cell["leg"])] = cell

    traj_probed = 0
    traj_found = 0
    rows = []
    for lane, task, leg, cid in M1A:
        rec = {
            "lane": lane,
            "task": task,
            "leg": leg,
            "component": cid,
            "gold_in_answer": True,
            "gold_in_found": True,
            "extractor_match": False,
            "in_A": (lane, task) in vp,
            "Y_pair": None,
            "S_leg": None,
            "DONE": None,
            "S_source": None,
            "component_match_in_sts": None,
            "STS_leg": None,
            "traj_tool_gold": "STOP-NO-TRAJ",
        }
        if (lane, task) in la:
            rec["Y_pair"] = int(float(la[(lane, task)]["Y"]))
        key = (lane, task)
        if key in vp:
            rec["DONE"] = True
            rec["S_leg"] = int(vp[key]["s0"] if leg == "G0" else vp[key]["s1"])
            rec["S_source"] = "valid_pairs"
            if key in sts_ix:
                st = sts_ix[key]
                rec["STS_leg"] = st["sts0"] if leg == "G0" else st["sts1"]
                mk = st["matches0"] if leg == "G0" else st["matches1"]
                rec["component_match_in_sts"] = mk.get(cid)
        elif (lane, task, leg) in high:
            rec["DONE"] = False
            rec["S_leg"] = int(high[(lane, task, leg)]["score"])
            rec["S_source"] = "high_S_no_DONE"
            rec["terminal_reason"] = high[(lane, task, leg)]["reason"]
        else:
            rec["S_source"] = "UNKNOWN"

        # Probe traj only to classify STOP vs present; do not parse if missing.
        hatd = ROOT / "out/study2_hatd_legs.jsonl"
        traj_probed += 1
        rec["traj_tool_gold"] = "STOP-NO-TRAJ"
        if hatd.exists():
            for line in hatd.read_text().splitlines():
                if not line.strip():
                    continue
                h = json.loads(line)
                if h.get("lane") == lane and h.get("task") == task and h.get("leg") == leg:
                    p = Path(h.get("traj") or "")
                    if p.exists():
                        traj_found += 1
                        rec["traj_tool_gold"] = "TRAJ_PRESENT_NOT_PARSED"
                    break
        rows.append(rec)

    joinable = [r for r in rows if r["S_leg"] is not None]
    s100 = [r for r in joinable if r["S_leg"] == 100]
    in_a = [r for r in rows if r["in_A"]]
    y0 = [r for r in in_a if r["Y_pair"] == 0]
    unknown = [r for r in rows if r["S_leg"] is None]
    not_done_s100 = [r for r in rows if r["DONE"] is False and r["S_leg"] == 100]

    summary = {
        "n_m1a": 13,
        "n_joinable_S": len(joinable),
        "n_unknown_S": len(unknown),
        "n_S100_among_joinable": len(s100),
        "n_in_A": len(in_a),
        "n_in_A_Y0": len(y0),
        "n_not_DONE_S100": len(not_done_s100),
        "traj_channel": "STOP-NO-TRAJ",
        "traj_files_present": traj_found,
        "traj_rows_probed": traj_probed,
        "rows": rows,
    }
    (OUT_DIR / "join.json").write_text(json.dumps(summary, indent=2) + "\n")

    lines = [
        "# M1a × locked score join — RESULT",
        "",
        "**Population:** 13 locked M1a rows (P3-0.7 / P3-1 A-9.3).",
        "**Traj/tool channel:** STOP-NO-TRAJ (Paper-2 `traj.jsonl` not on this workstation).",
        "",
        f"- Joinable per-leg \(S\): **{len(joinable)}/13**",
        f"- UNKNOWN \(S\): **{len(unknown)}/13** (not imputed)",
        f"- \(S=100\) among joinable: **{len(s100)}/{len(joinable)}**",
        f"- In \(\\mathcal{{A}}\): **{len(in_a)}/13**; pair-level \(Y=0\): **{len(y0)}/{len(in_a)}**",
        f"- Non-DONE and \(S=100\) (locked high-S list): **{len(not_done_s100)}**",
        "",
        "| lane | task | leg | component | in A | DONE | S | Y | S source |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        y = r["Y_pair"] if r["Y_pair"] is not None else "N/A"
        s = r["S_leg"] if r["S_leg"] is not None else "UNKNOWN"
        d = {True: "yes", False: "no", None: "UNKNOWN"}[r["DONE"]]
        lines.append(
            f"| {r['lane']} | {r['task']} | {r['leg']} | `{r['component']}` | "
            f"{'yes' if r['in_A'] else 'no'} | {d} | {s} | {y} | {r['S_source']} |"
        )
    lines += [
        "",
        "## Licensed reading",
        "",
        "Gold was in the answer and in `found` on all 13 rows (definitional M1a).",
        "Where a locked screenshot-rubric \(S\) exists, it can be 100 on the same leg.",
        "Pair-level binary tracking is 0 on every M1a row that sits in \(\\mathcal{A}\).",
        "This is not a 171-N result, not screenshot evidence, and not a new metric.",
        "",
        "## Not established",
        "",
        "- Gold in tool traces or screenshots",
        "- Prevalence of score/evidence collapse",
        "- Transport of M1a",
        "",
    ]
    (OUT_DIR / "RESULT.md").write_text("\n".join(lines))
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
