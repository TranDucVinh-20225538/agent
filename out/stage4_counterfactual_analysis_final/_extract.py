#!/usr/bin/env python3
"""Mechanical extraction pass (Round 27 continuation, Paper 1 canonical audit).
Reads only from results/. Writes only under out/stage4_counterfactual_analysis_final/.
"""
import json, csv, sys
from pathlib import Path

ROOT = Path(".").resolve()
RESULTS = ROOT / "results"
OUT = ROOT / "out" / "stage4_counterfactual_analysis_final"

PHASE_A_TASKS = ["retrieval-f001", "aggregation-f003", "preference_inference-f018", "counterfactual-f004"]
PHASE_A_PREFIX = {
    "Claude": "stage4",
    "GPT": "stage4-openai",
    "Qwen3.5-35B-A3B": "stage4-qwen35a3b",
    "Qwen3.5-9B": "stage4-qwen359b",
    "Qwen3.8-Flash": "stage4-qwen38flash",
}
PHASE_B_TASKS = ["retrieval-f003","retrieval-f016","retrieval-f029","retrieval-f030","aggregation-f018","preference_inference-f004"]
PHASE_B_PREFIX = {
    "Claude": "phaseb-claude",
    "GPT": "phaseb-openai",
    "Qwen3.5-35B-A3B": "phaseb-qwen35a3b",
    "Qwen3.5-9B": "phaseb-qwen359b",
    "Qwen3.8-Flash": "phaseb-qwen38flash",
}
TIER = {
    "Claude": "primary", "GPT": "primary", "Qwen3.5-35B-A3B": "primary",
    "Qwen3.5-9B": "size_ablation", "Qwen3.8-Flash": "exploratory",
}

def load_json(p):
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text())
    except Exception as e:
        return {"__error__": str(e)}

def load_traj(p):
    if not p.is_file():
        return []
    rows = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows

def last_action_info(rows):
    if not rows:
        return {"n_steps": 0, "last_action": None, "done": False, "last_response": ""}
    last = rows[-1]
    act = str(last.get("action") or "")
    return {
        "n_steps": len(rows),
        "last_action": act,
        "done": act == "DONE",
        "last_response": str(last.get("response") or "")[:4000],
    }

def score_from(scores_json):
    if not scores_json or "__error__" in scores_json:
        return None
    rows = scores_json.get("rows") or []
    if rows:
        return rows[0].get("raw")
    return None

def rel(p):
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)

def audit_cell(model, phase, task, lane_dir):
    """lane_dir: results/<prefix>-<task> ; returns dict per condition (base/cf)."""
    out = {}
    for cond in ("base", "cf"):
        cond_dir = lane_dir / cond
        task_dir = cond_dir / task
        traj_path = task_dir / "traj.jsonl"
        guest_path = cond_dir / f"{task}.guest.json"
        scores_path = cond_dir / "scores.json"
        sqlpatch_path = cond_dir / "sql-patch.json"
        rubric_path = task_dir / "rubric_result.json"
        result_txt = task_dir / "result.txt"

        traj_rows = load_traj(traj_path)
        ai = last_action_info(traj_rows)
        scores = load_json(scores_path)
        guest = load_json(guest_path)
        rubric = load_json(rubric_path)
        sqlpatch = load_json(sqlpatch_path)
        result_txt_val = result_txt.read_text().strip() if result_txt.is_file() else None

        exec_failure = None
        if not cond_dir.is_dir():
            exec_failure = "MISSING_CELL"
        elif not traj_path.is_file():
            exec_failure = "NO_TRAJ"
        elif not ai["done"]:
            la = ai["last_action"] or "EMPTY"
            exec_failure = f"NOT_DONE:{la}"
        elif scores is None:
            exec_failure = "NO_SCORES"

        out[cond] = {
            "model": model, "phase": phase, "task": task, "condition": cond,
            "dir": rel(cond_dir),
            "traj_path": rel(traj_path) if traj_path.is_file() else None,
            "guest_path": rel(guest_path) if guest_path.is_file() else None,
            "n_steps": ai["n_steps"], "last_action": ai["last_action"], "done": ai["done"],
            "score_raw": score_from(scores),
            "result_txt": result_txt_val,
            "exec_failure": exec_failure,
            "guest": guest,
            "sql_patch": sqlpatch,
            "rubric_per_max": (rubric or {}).get("per_rubric_max") if isinstance(rubric, dict) else None,
            "final_response": ai["last_response"],
        }
    return out

cells = []

# Phase A locked reuse: which lanes actually have which tasks
for model, prefix in PHASE_A_PREFIX.items():
    for task in PHASE_A_TASKS:
        lane_dir = RESULTS / f"{prefix}-{task}"
        if lane_dir.is_dir():
            c = audit_cell(model, "phase_a_locked", task, lane_dir)
            cells.append(c)

# Phase B new tasks
for model, prefix in PHASE_B_PREFIX.items():
    for task in PHASE_B_TASKS:
        lane_dir = RESULTS / f"{prefix}-{task}"
        if lane_dir.is_dir():
            c = audit_cell(model, "phase_b", task, lane_dir)
            cells.append(c)

# Write full raw dump (working file, not a required deliverable, but useful to me)
(OUT / "_raw_cells.json").write_text(json.dumps(cells, indent=1, default=str))

# Also write a compact CSV of mechanical facts (this feeds trajectory_cells.csv later)
rows_flat = []
for c in cells:
    for cond in ("base", "cf"):
        d = c[cond]
        rows_flat.append({
            "model": d["model"], "phase": d["phase"], "task": d["task"], "condition": d["condition"],
            "dir": d["dir"], "n_steps": d["n_steps"], "last_action": d["last_action"],
            "done": d["done"], "score_raw": d["score_raw"], "exec_failure": d["exec_failure"],
            "result_txt": d["result_txt"],
        })

with open(OUT / "_mechanical.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows_flat[0].keys()))
    w.writeheader()
    for r in rows_flat:
        w.writerow(r)

print(f"cells (model,task combos): {len(cells)}")
print(f"total rows (base+cf): {len(rows_flat)}")
n_done = sum(1 for r in rows_flat if r["done"])
print(f"DONE rows: {n_done} / {len(rows_flat)}")
n_fail = sum(1 for r in rows_flat if r["exec_failure"])
print(f"exec_failure rows: {n_fail}")
