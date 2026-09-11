#!/usr/bin/env python3
"""Paper 1 canonical audit — final build.
Snapshot: b7b4203 (verified via git rev-parse). Read-only against results/, cf/, out/PHASE_B.md.
Writes ONLY under out/stage4_counterfactual_analysis_final/.
Classifications below were derived by hand from raw traj.jsonl / *.guest.json / messages-or-traj final
answer text, read directly (see _semantic_dump.txt / _gpt_fix_dump.txt built earlier in this session).
No number here was copied from out/stage4_counterfactual_analysis/ or out/stage4_phase_b_interim_analysis/.
"""
import json, csv, math
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(".").resolve()
OUT = ROOT / "out" / "stage4_counterfactual_analysis_final"
RESULTS = ROOT / "results"

cells = json.loads((OUT / "_raw_cells.json").read_text())
cell_index = {(c["base"]["model"], c["base"]["task"]): c for c in cells}

TIER = {
    "Claude": "primary", "GPT": "primary", "Qwen3.5-35B-A3B": "primary",
    "Qwen3.5-9B": "size_ablation", "Qwen3.8-Flash": "exploratory",
}
MODEL_ORDER = ["Claude", "GPT", "Qwen3.5-35B-A3B", "Qwen3.5-9B", "Qwen3.8-Flash"]
TASK_ORDER = [
    "retrieval-f001", "aggregation-f003", "preference_inference-f018", "counterfactual-f004",
    "retrieval-f003", "retrieval-f016", "retrieval-f029", "retrieval-f030",
    "aggregation-f018", "preference_inference-f004",
]
DESIGNED_ROLE = {
    "retrieval-f001": "control (channel-invariant, point value)",
    "aggregation-f003": "control (channel-invariant, aggregation)",
    "preference_inference-f018": "designed Type B (joint D, Stage 4 lock)",
    "counterfactual-f004": "score-sensitive contrast (contradiction removal; score auxiliary)",
    "retrieval-f003": "control (single sqlite channel)",
    "retrieval-f016": "control (single-app aggregation, distractor channel held constant)",
    "retrieval-f029": "control (dual-channel, sqlite+file must move together)",
    "retrieval-f030": "designed Type B (1099 dual-channel held constant; charitable sqlite-only moves)",
    "aggregation-f018": "designed Type B (charitable+home-office sqlite-only move; W-2/1099 dual-channel held)",
    "preference_inference-f004": "score-sensitive contrast (rubric pins Cooper's as HD top; D=1)",
}

# ---------------------------------------------------------------------------
# HAND-DERIVED CLASSIFICATIONS for the 24 valid pairs (both legs DONE).
# gold/D column = one-line statement of what was read from *.guest.json.
# mechanism = one-line statement of what was read from the final-answer text.
# clazz in {"type_a","type_b","sensitive"}.
# ---------------------------------------------------------------------------
CLASS = {
    ("Claude","retrieval-f001"): dict(clazz="type_a", gold="loyalty.status/miles Gold/38450->Silver/8620",
        mech="Base reports Gold/38,450; CF reports Silver/8,620. Both correct.", ds=0),
    ("GPT","retrieval-f001"): dict(clazz="type_a", gold="loyalty.status/miles Gold/38450->Silver/8620",
        mech="Base reports Gold/38,450; CF reports Silver/8,620. Both correct.", ds=0),
    ("Qwen3.5-35B-A3B","retrieval-f001"): dict(clazz="type_a", gold="loyalty.status/miles Gold/38450->Silver/8620",
        mech="Base reports Gold/38,450; CF reports Silver/8,620. Both correct.", ds=0),
    ("Qwen3.5-9B","retrieval-f001"): dict(clazz="type_a", gold="loyalty.status/miles Gold/38450->Silver/8620",
        mech="Base reports Gold/38,450; CF reports Silver/8,620. Both correct.", ds=0),
    ("Qwen3.8-Flash","retrieval-f001"): dict(clazz="type_a", gold="loyalty.status/miles Gold/38450->Silver/8620",
        mech="Base reports Gold/38,450; CF reports Silver/8,620. Both correct (plus extra MQM detail).", ds=0),

    ("Claude","aggregation-f003"): dict(clazz="type_a", gold="combined filed refund 4871.70->400.00",
        mech="Base reports $4,872; CF reports $400. Both correct.", ds=0),
    ("GPT","aggregation-f003"): dict(clazz="type_a", gold="combined filed refund 4871.70->400.00",
        mech="Base reports $4,871.70; CF reports $400. Both correct; absolute rubric score lower (misses a year-count criterion in both conditions).", ds=0),
    ("Qwen3.5-9B","aggregation-f003"): dict(clazz="sensitive", gold="combined filed refund 4871.70->400.00",
        mech="Base reports $4,872; CF reports $400. Both correct (tracks); score moves 50->80 on an unrelated per-year-breakdown criterion.", ds=30),
    ("Qwen3.8-Flash","aggregation-f003"): dict(clazz="sensitive", gold="combined filed refund 4871.70->400.00",
        mech="Base reports $4,872; CF reports $400. Both correct (tracks); score moves 80->100.", ds=20),

    ("Claude","preference_inference-f018"): dict(clazz="type_b", gold="joint D: GME shares 85->0 AND OddsMarket YES 200/active->0/settled",
        mech="CF answer correctly zeroes GME (0 sh, $0.00) but still lists OddsMarket GameStop-YES as 200 sh/$16.00, byte-identical to the base row. One of two D components tracked.", ds=0),

    ("GPT","counterfactual-f004"): dict(clazz="type_b", gold="1099_amount_0 for TY2023/2024/2025 all ->0 (this commit's patch zeroes all three; TY2025 was the whitespace-bug victim in the Stage-4-era commit, now fixed)",
        mech="Base and CF answers are near-identical: both state the 1099-NEC is $1,200 and both subtract it from net savings (~$1,068/yr). CF does not reflect the zeroed 1099 field.", ds=0),

    ("Claude","retrieval-f003"): dict(clazz="type_a", gold="TY2024 filed W-2 wages 136320->80000",
        mech="Base reports $136,320; CF reports $80,000. Both correct.", ds=0),
    ("GPT","retrieval-f003"): dict(clazz="type_a", gold="TY2024 filed W-2 wages 136320->80000",
        mech="Base reports 136,320; CF reports 80,000. Both correct.", ds=0),

    ("Claude","retrieval-f016"): dict(clazz="type_a", gold="VTI shares 5->0 / cash 420->50 (cost-basis total 8213.25->7114.20); GME held constant",
        mech="Base reports $8,213.25 total / $420 cash; CF reports $7,114.20 / $50. GME unchanged in both. Both correct.", ds=0),
    ("GPT","retrieval-f016"): dict(clazz="sensitive", gold="VTI shares 5->0 / cash 420->50 (cost-basis total 8213.25->7114.20); GME held constant",
        mech="Base reports $8,213.25 / $420; CF reports $7,114.20 / $50. Both correct (tracks); score moves 100->85.", ds=-15),
    ("Qwen3.5-9B","retrieval-f016"): dict(clazz="type_b", gold="VTI shares 5->0 / cash 420->50 (cost-basis total 8213.25->7114.20); GME held constant",
        mech="Base reports total cost basis $8,788.75 -- does not match true baseline gold $8,213.25 (delta $575.50, source of the error not identified in the trajectory). CF correctly reports $7,114.20 (matches true CF gold exactly). Base leg does not correctly reflect G0; CF leg does. Score 100/100 both.", ds=0),

    ("Claude","retrieval-f029"): dict(clazz="type_a", gold="dual-channel: sqlite+file W-2 wages 142000->90000, fed withheld 28400->18000 (file and sqlite must move together)",
        mech="Base reports $142,000/$28,400 (sqlite) cross-checked against file ($142,000); CF reports $90,000/$18,000 cross-checked against file ($90,000). Both channels tracked on both legs.", ds=0),
    ("GPT","retrieval-f029"): dict(clazz="sensitive", gold="dual-channel: sqlite+file W-2 wages 142000->90000, fed withheld 28400->18000",
        mech="Base reports $142,000/$28,400, cross-checked against file; CF reports $90,000/$18,000, cross-checked against file. Both legs correct (tracks); score moves 33->100 on criteria unrelated to the wage figure itself.", ds=67),
    ("Qwen3.8-Flash","retrieval-f029"): dict(clazz="type_b", gold="dual-channel: sqlite+file W-2 wages 142000->90000, fed withheld 28400->18000",
        mech="Base reports $142,000/$28,400 (correct). CF reports 'Total Income $91,200' for Box-1 wages -- does not match true CF gold $90,000 (off by exactly $1,200); federal withholding is reported correctly as $18,000. Partial/imprecise tracking of a manipulated field. Score 100/100 both.", ds=0),

    ("Claude","retrieval-f030"): dict(clazz="type_b", gold="D={1099 payer/amount HELD CONSTANT at $1,200 TY2025; charitable sqlite-only 950->100}. Primary probe (1099) is designed not to move.",
        mech="Base answers using TY2024 (filed) 1099 data ($1,080), not TY2025 (in-progress, the actually-tested row, $1,200) -- a wrong-year read, not a tracking miss on the manipulated field. CF correctly reports TY2025: 1099 unchanged at $1,200, charitable correctly moved to $100. The joint answer is internally inconsistent across the pair because of the base-leg year confusion, not because CF missed the sqlite move.", ds=0),
    ("GPT","retrieval-f030"): dict(clazz="sensitive", gold="D={1099 payer/amount HELD CONSTANT at $1,200 TY2025; charitable sqlite-only 950->100}",
        mech="Base correctly identifies TY2025 as most-recent, reports 1099 $1,200 (unchanged, correct) and charitable $950 (correct pre-image). CF reports 1099 still $1,200 (correctly unchanged) and charitable correctly moved to $100, flagging the file/sqlite mismatch explicitly. Full, correct tracking on both legs; score still moves 53->100 for reasons unrelated to the two D components.", ds=47),

    ("Claude","aggregation-f018"): dict(clazz="type_a", gold="D={charitable sqlite-only 950->0, home_office sqlite-only 104->0}; W-2/1099 dual-channel and files held constant",
        mech="Base reports SpeedTax charitable $950 / home-office 104 days, matching the (untouched) file. CF reports SpeedTax charitable $0.00 / home-office 0 days, explicitly flagging that the file still shows $950/104 as an unreconciled mismatch -- correct given only the sqlite side was patched. Both legs correct.", ds=0),

    ("Claude","preference_inference-f004"): dict(clazz="sensitive", gold="HangryDash order-count winner Cooper's(88)->Backyard Ale House(59); TableFind ranking held constant",
        mech="Base reports Cooper's as HD #1 (88); CF reports Backyard Ale House as HD #1 (59), Cooper's #2 (57). TableFind top-5 identical in both. Tracks correctly; score moves 100->79 as the rubric's pinned answer ('Cooper's is HD top') goes stale.", ds=-21),
    ("GPT","preference_inference-f004"): dict(clazz="sensitive", gold="HangryDash order-count winner Cooper's(88)->Backyard Ale House(59); TableFind ranking held constant",
        mech="Base reports Cooper's as HD #1 (88); CF reports Backyard Ale House as HD #1 (59), Cooper's #2 (57). Tracks correctly; score moves 100->58.", ds=-42),
}

# ---------------------------------------------------------------------------
# Execution-failure taxonomy for invalid pairs (mechanical, from last_action).
# ---------------------------------------------------------------------------
def failure_type(last_action):
    if last_action is None:
        return "NO_TRAJ"
    la = str(last_action)
    if la.startswith("EMPTY_XML"):
        return "EMPTY_XML"
    if la == "FAIL":
        return "AGENT_FAIL"
    if la == "PREDICT_CRASH":
        return "SCREENSHOT_DECODE_CRASH"
    if la in ("TOOL_CALL", "WAIT"):
        return "STEP_LIMIT_NO_DONE"
    if la.startswith("pyautogui") or "import base64" in la:
        return "STEP_LIMIT_NO_DONE"
    return "STEP_LIMIT_NO_DONE"

# ---------------------------------------------------------------------------
# Build trajectory_cells.csv (one row per cell = per model,task,condition)
# ---------------------------------------------------------------------------
traj_rows = []
for c in cells:
    for cond in ("base", "cf"):
        d = c[cond]
        traj_rows.append({
            "model": d["model"], "tier": TIER[d["model"]], "phase": d["phase"], "task": d["task"],
            "condition": d["condition"], "dir": d["dir"], "n_steps": d["n_steps"],
            "last_action": d["last_action"], "done": d["done"], "score_raw": d["score_raw"],
            "exec_failure": d["exec_failure"],
        })

with open(OUT / "trajectory_cells.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(traj_rows[0].keys()))
    w.writeheader()
    for r in traj_rows:
        w.writerow(r)

# ---------------------------------------------------------------------------
# Build paired_results.csv + failure_audit.csv
# ---------------------------------------------------------------------------
paired_rows = []
failure_rows = []
for c in cells:
    b, cf = c["base"], c["cf"]
    model, task = b["model"], b["task"]
    key = (model, task)
    valid_pair = b["done"] and cf["done"]
    if valid_pair and key in CLASS:
        info = CLASS[key]
        paired_rows.append({
            "model": model, "tier": TIER[model], "task": task,
            "designed_role": DESIGNED_ROLE[task],
            "base_score": b["score_raw"], "cf_score": cf["score_raw"],
            "score_delta": info["ds"],
            "classification": info["clazz"],
            "gold_intervention": info["gold"],
            "tracking_mechanism": info["mech"],
        })
    else:
        # invalid pair -> failure row(s)
        for cond, d in (("base", b), ("cf", cf)):
            if not d["done"]:
                failure_rows.append({
                    "model": model, "tier": TIER[model], "task": task, "condition": cond,
                    "dir": d["dir"], "n_steps": d["n_steps"], "last_action": d["last_action"],
                    "failure_type": failure_type(d["last_action"]),
                    "why_excluded": "not DONE (last traj.jsonl action != 'DONE'); result.txt/writer status/score are not substitutes",
                })

with open(OUT / "paired_results.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(paired_rows[0].keys()))
    w.writeheader()
    for r in paired_rows:
        w.writerow(r)

with open(OUT / "failure_audit.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(failure_rows[0].keys()))
    w.writeheader()
    for r in failure_rows:
        w.writerow(r)

# ---------------------------------------------------------------------------
# rubric_item_audit.csv -- per-criterion arrays for the notable / surprising cells
# ---------------------------------------------------------------------------
rubric_targets = [
    ("Claude","retrieval-f003"), ("GPT","aggregation-f003"), ("Qwen3.5-9B","aggregation-f003"),
    ("Qwen3.8-Flash","aggregation-f003"), ("GPT","retrieval-f029"), ("Qwen3.5-9B","retrieval-f016"),
    ("Claude","preference_inference-f018"),
]
rubric_rows = []
for key in rubric_targets:
    c = cell_index.get(key)
    if not c:
        continue
    for cond in ("base","cf"):
        d = c[cond]
        rubric_rows.append({
            "model": key[0], "task": key[1], "condition": cond,
            "score": d["score_raw"], "per_rubric_max": json.dumps(d["rubric_per_max"]),
        })
with open(OUT / "rubric_item_audit.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rubric_rows[0].keys()))
    w.writeheader()
    for r in rubric_rows:
        w.writerow(r)

# ---------------------------------------------------------------------------
# Statistics per tier
# ---------------------------------------------------------------------------
def clopper_pearson(k, n, alpha=0.05):
    # exact binomial-tail inversion, no scipy.
    if n == 0:
        return (None, None)
    lo = 0.0 if k == 0 else _beta_ppf(alpha/2, k, n-k+1)
    hi = 1.0 if k == n else _beta_ppf(1-alpha/2, k+1, n-k)
    return (lo, hi)

def _beta_ppf(p, a, b, tol=1e-10, maxit=200):
    # bisection on the regularized incomplete beta function I_x(a,b)
    lo, hi = 0.0, 1.0
    for _ in range(maxit):
        mid = (lo+hi)/2
        if _betainc(mid, a, b) < p:
            lo = mid
        else:
            hi = mid
        if hi-lo < tol:
            break
    return (lo+hi)/2

def _betainc(x, a, b):
    # regularized incomplete beta via continued fraction (Numerical Recipes style)
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a+b)
    front = math.exp(math.log(x)*a + math.log(1-x)*b - lbeta) / a
    if x < (a+1)/(a+b+2):
        return front * _betacf(x, a, b)
    else:
        return 1.0 - (math.exp(math.log(1-x)*b + math.log(x)*a - lbeta)/b) * _betacf(1-x, b, a)

def _betacf(x, a, b, maxit=200, eps=3e-12):
    qab = a+b; qap = a+1; qam = a-1
    c = 1.0
    d = 1.0 - qab*x/qap
    if abs(d) < 1e-30: d = 1e-30
    d = 1.0/d
    h = d
    for m in range(1, maxit+1):
        m2 = 2*m
        aa = m*(b-m)*x/((qam+m2)*(a+m2))
        d = 1.0 + aa*d
        if abs(d) < 1e-30: d = 1e-30
        c = 1.0 + aa/c
        if abs(c) < 1e-30: c = 1e-30
        d = 1.0/d
        h *= d*c
        aa = -(a+m)*(qab+m)*x/((a+m2)*(qap+m2))
        d = 1.0 + aa*d
        if abs(d) < 1e-30: d = 1e-30
        c = 1.0 + aa/c
        if abs(c) < 1e-30: c = 1e-30
        d = 1.0/d
        delta = d*c
        h *= delta
        if abs(delta-1.0) < eps:
            break
    return h

def tier_stats(tier_name, rows):
    rows = [r for r in rows if r["tier"] == tier_name]
    valid = len(rows)
    type_a = sum(1 for r in rows if r["classification"] == "type_a")
    sensitive = sum(1 for r in rows if r["classification"] == "sensitive")
    type_b = sum(1 for r in rows if r["classification"] == "type_b")
    tracking_valid = type_a + sensitive
    inv_rate = (type_a / tracking_valid) if tracking_valid else None
    ci = clopper_pearson(type_a, tracking_valid) if tracking_valid else (None, None)
    return dict(valid_pairs=valid, tracking_valid=tracking_valid, type_a=type_a,
                sensitive=sensitive, type_b=type_b, invariance_rate=inv_rate,
                clopper_pearson_95ci=list(ci))

per_model = {}
for model in MODEL_ORDER:
    rows = [r for r in paired_rows if r["model"] == model]
    valid = len(rows)
    type_a = sum(1 for r in rows if r["classification"] == "type_a")
    sensitive = sum(1 for r in rows if r["classification"] == "sensitive")
    type_b = sum(1 for r in rows if r["classification"] == "type_b")
    tracking_valid = type_a + sensitive
    inv_rate = (type_a / tracking_valid) if tracking_valid else None
    ci = clopper_pearson(type_a, tracking_valid) if tracking_valid else (None, None)
    per_model[model] = dict(tier=TIER[model], valid_pairs=valid, tracking_valid=tracking_valid,
                             type_a=type_a, sensitive=sensitive, type_b=type_b,
                             invariance_rate=inv_rate, clopper_pearson_95ci=list(ci))

primary_pooled = tier_stats("primary", paired_rows)  # reference only -- paper reports per-model, not pooled
ablation = tier_stats("size_ablation", paired_rows)
exploratory = tier_stats("exploratory", paired_rows)

summary = {
    "snapshot": "b7b4203",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "note": "Per-model counts are the reportable unit. 'primary_pooled' is kept for reference only and MUST NOT be headlined -- pooling Claude+GPT+Qwen3.5-35B-A3B into one rate is explicitly disallowed by the audit brief.",
    "per_model": per_model,
    "primary_pooled_DO_NOT_HEADLINE": primary_pooled,
    "size_ablation": ablation,
    "exploratory": exploratory,
}
(OUT / "statistical_summary.json").write_text(json.dumps(summary, indent=2))

# ---------------------------------------------------------------------------
# table_primary.md / .tex  (Claude, GPT, Qwen3.5-35B-A3B)
# ---------------------------------------------------------------------------
def fmt_ci(ci):
    if ci[0] is None:
        return "n/a"
    return f"[{ci[0]:.3f}, {ci[1]:.3f}]"

def fmt_rate(x):
    return "n/a" if x is None else f"{x:.3f}"

with open(OUT / "table_primary.md", "w") as f:
    f.write("| Model | Valid | Tracking-valid | Type A | Sensitive | Type B | Invariance rate | 95% CI |\n")
    f.write("|---|---:|---:|---:|---:|---:|---:|---|\n")
    for model in ["Claude","GPT","Qwen3.5-35B-A3B"]:
        s = per_model[model]
        f.write(f"| {model} | {s['valid_pairs']} | {s['tracking_valid']} | {s['type_a']} | {s['sensitive']} | {s['type_b']} | {fmt_rate(s['invariance_rate'])} | {fmt_ci(s['clopper_pearson_95ci'])} |\n")

with open(OUT / "table_primary.tex", "w") as f:
    f.write("\\begin{tabular}{lrrrrrrl}\n\\toprule\n")
    f.write("Model & Valid & Tracking-valid & Type A & Sensitive & Type B & Invariance & 95\\% CI \\\\\n\\midrule\n")
    for model in ["Claude","GPT","Qwen3.5-35B-A3B"]:
        s = per_model[model]
        f.write(f"{model} & {s['valid_pairs']} & {s['tracking_valid']} & {s['type_a']} & {s['sensitive']} & {s['type_b']} & {fmt_rate(s['invariance_rate'])} & {fmt_ci(s['clopper_pearson_95ci'])} \\\\\n")
    f.write("\\bottomrule\n\\end{tabular}\n")

with open(OUT / "table_ablation.md", "w") as f:
    f.write("| Model | Valid | Tracking-valid | Type A | Sensitive | Type B | Invariance rate | 95% CI |\n")
    f.write("|---|---:|---:|---:|---:|---:|---:|---|\n")
    s = per_model["Qwen3.5-9B"]
    f.write(f"| Qwen3.5-9B | {s['valid_pairs']} | {s['tracking_valid']} | {s['type_a']} | {s['sensitive']} | {s['type_b']} | {fmt_rate(s['invariance_rate'])} | {fmt_ci(s['clopper_pearson_95ci'])} |\n")

with open(OUT / "table_exploratory.md", "w") as f:
    f.write("| Model | Valid | Tracking-valid | Type A | Sensitive | Type B | Invariance rate | 95% CI |\n")
    f.write("|---|---:|---:|---:|---:|---:|---:|---|\n")
    s = per_model["Qwen3.8-Flash"]
    f.write(f"| Qwen3.8-Flash | {s['valid_pairs']} | {s['tracking_valid']} | {s['type_a']} | {s['sensitive']} | {s['type_b']} | {fmt_rate(s['invariance_rate'])} | {fmt_ci(s['clopper_pearson_95ci'])} |\n")

# ---------------------------------------------------------------------------
# tracking_evidence.md -- one entry per valid pair, quoting the mechanism
# ---------------------------------------------------------------------------
with open(OUT / "tracking_evidence.md", "w") as f:
    f.write("# Tracking evidence, per valid pair\n\n")
    f.write("Gold column is read from `*.guest.json` (`probe_before`/`probe_after`/`extra_probes_*`), ")
    f.write("never from writer `track` fields. Mechanism column is read from the agent's final answer ")
    f.write("(`messages.json` last assistant text block, or `traj.jsonl` last-step `response` field when ")
    f.write("no `messages.json` exists -- GPT and Qwen runs in this repo carry no `messages.json`).\n\n")
    for task in TASK_ORDER:
        rows = [r for r in paired_rows if r["task"] == task]
        if not rows:
            continue
        f.write(f"\n## {task} -- {DESIGNED_ROLE[task]}\n\n")
        for r in rows:
            f.write(f"**{r['model']}** (base={r['base_score']}, cf={r['cf_score']}, delta={r['score_delta']}, class={r['classification']})\n\n")
            f.write(f"- Gold/D: {r['gold_intervention']}\n")
            f.write(f"- Mechanism: {r['tracking_mechanism']}\n\n")

# ---------------------------------------------------------------------------
# rubric_mechanism.md
# ---------------------------------------------------------------------------
with open(OUT / "rubric_mechanism.md", "w") as f:
    f.write("# Rubric mechanism notes\n\n")
    f.write("Per-criterion `per_rubric_max` arrays for cells whose score behavior is otherwise unexplained ")
    f.write("by the tracking classification alone. Source: `rubric_result.json` in each run directory.\n\n")
    f.write("| Model | Task | Condition | Score | per_rubric_max |\n|---|---|---|---:|---|\n")
    for r in rubric_rows:
        f.write(f"| {r['model']} | {r['task']} | {r['condition']} | {r['score']} | {r['per_rubric_max']} |\n")
    f.write("\n## Reading\n\n")
    f.write("- **GPT `aggregation-f003`**: `[1,1,0,0]` in both conditions -- the two criteria that move with the "
             "combined-refund figure are satisfied both times (Type A here is not a rubric-blindness artifact on "
             "those two items specifically); the other two criteria (a year-count/format check) are never satisfied, "
             "in either condition, so they contribute nothing to the base->CF comparison.\n")
    f.write("- **Qwen3.5-9B `aggregation-f003`**: `[1,1,0,0]`->`[1,1,1,0]` -- one additional criterion is satisfied "
             "only under CF. Score-sensitivity here traces to a single rubric item, not a wholesale change in "
             "competence.\n")
    f.write("- **Qwen3.8-Flash `aggregation-f003`**: `[1,1,1,0]`->`[1,1,1,1]` -- same pattern, one additional item.\n")
    f.write("- **Claude `retrieval-f003`**: `[1,1,0]` in both conditions -- a fixed third criterion is never "
             "satisfied in either condition; irrelevant to the base/CF contrast, but explains the non-100 score "
             "under a fully-tracked, fully-invariant pair.\n")
    f.write("- **GPT `retrieval-f029`**: `[1,0,0]`->`[1,1,1]` -- the wage-figure criterion (index 0) is satisfied "
             "in *both* conditions; the two criteria that move are unrelated to the manipulated field itself, so "
             "the large score swing (33->100) is not evidence about D-tracking.\n")
    f.write("- **Qwen3.5-9B `retrieval-f016`**: `[1,1,1,1]` in both conditions (100/100) despite the base answer "
             "reporting an incorrect total cost basis ($8,788.75 vs. true $8,213.25). The rubric evidently does "
             "not check the reported grand total against the gold value at the precision this would require -- a "
             "concrete instance of rubric insensitivity to the exact manipulated figure, not an aggregation-masking "
             "or task-structure explanation.\n")
    f.write("\nNo case in this audit required an aggregation-masking or task-structure explanation beyond what is "
             "stated above; where the mechanism is unclear from the available criteria it is reported as such rather than guessed.\n")

print("done. paired_rows:", len(paired_rows), "failure_rows:", len(failure_rows))
print(json.dumps(per_model, indent=1))
print("ABLATION", ablation)
print("EXPLORATORY", exploratory)
