# Consistency checklist (frozen snapshot `b7b4203`)

Sources: `out/stage4_counterfactual_analysis_final/{paired_results.csv,statistical_summary.json,trajectory_cells.csv,failure_audit.csv,tracking_evidence.md}` and DONE rows in `results/`.

## Coverage denominators

| Quantity | Value | Notes |
|---|---:|---|
| Intended cells | 50 | 5 lanes × 10 tasks |
| Never scheduled | 4 | 9B + Flash × `preference_inference-f018`, `counterfactual-f004` |
| Executed cells | 46 | `trajectory_cells.csv` unique (model, task) |
| Trajectory legs | 92 | 46 × 2 |
| DONE legs | 57 | |
| Execution-failure legs | 35 | disjoint from 8 never-scheduled legs |
| Valid pairs (both DONE) | 24 | |
| Qwen3.5-35B-A3B incomplete legs | 15 | of 35 |

## Primary rates (invariance = Type A / tracking-valid)

| Model | Valid | Tracking-valid | Type A | Sensitive | Type B | Rate | 95% CI |
|---|---:|---:|---:|---:|---:|---|---|
| Claude | 9 | 7 | 6 | 1 | 2 | 6/7 = 0.857 | [0.421, 0.996] |
| GPT-5.5 | 8 | 7 | 3 | 4 | 1 | 3/7 = 0.429 | [0.099, 0.816] |
| Qwen3.5-35B-A3B | 1 | 1 | 1 | 0 | 0 | 1/1 = 1.000 | [0.025, 1.000] |

Do **not** headline 10/15, 15/18, or 18/24 as a common rate.

## Ablation / exploratory (not primary)

| Model | Valid | Tracking-valid | A | Sens. | B | Rate | 95% CI |
|---|---:|---:|---:|---:|---:|---|---|
| Qwen3.5-9B | 3 | 2 | 1 | 1 | 1 | 0.500 | [0.013, 0.987] |
| Qwen3.8-Flash | 3 | 2 | 1 | 1 | 1 | 0.500 | [0.013, 0.987] |

## Primary pair scores and labels

### Claude

| Task | Base | CF | Class |
|---|---:|---:|---|
| retrieval-f001 | 100 | 100 | Type A |
| retrieval-f003 | 65 | 65 | Type A |
| retrieval-f016 | 100 | 100 | Type A |
| retrieval-f029 | 100 | 100 | Type A |
| retrieval-f030 | 100 | 100 | Type B (wrong-year 1099 on **base**; CF charitable $100) |
| aggregation-f003 | 80 | 80 | Type A |
| aggregation-f018 | 100 | 100 | Type A (designed Type B; positive control) |
| preference_inference-f004 | 100 | 79 | score-sensitive |
| preference_inference-f018 | 100 | 100 | Type B (GME 0 tracked; OM YES still 200) |

### GPT-5.5

| Task | Base | CF | Class |
|---|---:|---:|---|
| retrieval-f001 | 100 | 100 | Type A |
| retrieval-f003 | 100 | 100 | Type A |
| retrieval-f016 | 100 | 85 | score-sensitive |
| retrieval-f029 | 33 | 100 | score-sensitive |
| retrieval-f030 | 53 | 100 | score-sensitive |
| aggregation-f003 | 50 | 50 | Type A |
| preference_inference-f004 | 100 | 58 | score-sensitive |
| counterfactual-f004 | 87 | 87 | Type B (stale $1,200 stipend) |

GPT `aggregation-f018`: CF `EMPTY_XML` → not a valid pair.
GPT `preference_inference-f018`: both legs not DONE → not a valid pair.

### Qwen3.5-35B-A3B

| Task | Base | CF | Class |
|---|---:|---:|---|
| retrieval-f001 | 100 | 100 | Type A |

Only valid semantic pair.

## Citations verified (repository `references.bib` + arXiv lookup)

| Key | ID | Status |
|---|---|---|
| jang2026mypcbench | 2606.16748 | verified |
| xie2024osworld | NeurIPS 2024 | verified |
| zhou2024webarena | ICLR 2024 | verified |
| koh2024visualwebarena | ACL 2024 | verified |
| pearl2009causality | CUP 2009 | verified |
| shao2026protocolvalidity | 2607.22368 | verified |
| turk2026counterfactualclinical | 2605.30590 | verified |
| bellibatlu2026judgesense | 2604.23478 | verified |
