# Study 2 — locked execution order (inspect-only)

**Status:** REPORT ONLY — no files under method/prereg/universe modified  
**Sources:** `out/study2_launch_manifest.{md,json}`, `out/paper2_cell_order.json`, `out/paper2_analysis_universe.json`, `scripts/study2_bind_execution_key.sh`  
**Inspected at (UTC):** 2026-09-06T17:07:11Z

---

## 1. Family / model schedule (manifest roster order)

Sequential families (57 legs each → 171 total). No Gate 0A smoke entrypoints.

| # | Family | Model ID | Output root |
| ---: | --- | --- | --- |
| 1 | Qwen | `qwen/qwen3.8-flash` | `results/paper2_exec/study2-flash` |
| 2 | OpenAI | `openai/gpt-5.5` | `results/paper2_exec/study2-gpt` |
| 3 | Anthropic | `anthropic/claude-opus-4.6` | `results/paper2_exec/study2-claude` |

**Bind (required before any OpenRouter call):** `source scripts/study2_bind_execution_key.sh`  
**Credential:** `sk-or-v1-008…9dd` only · SMALL forbidden  
**Cell order file:** `out/paper2_cell_order.json` · seed carry-forward `20260904`  
**Per family:** `|T|=25`, `multiI=7`, `N_fam=57`

---

## 2. Task order (frozen `order[]`)

1. `retrieval-f010`  
2. `retrieval-f017` ← multi-I  
3. `contradiction-f022`  
4. `counterfactual-f013`  
5. `aggregation-f036`  
6. `contradiction-f014`  
7. `aggregation-f020`  
8. `counterfactual-f002` ← multi-I  
9. `retrieval-f005`  
10. `preference_inference-f010`  
11. `contradiction-f003`  
12. `contradiction-f017`  
13. `retrieval-f002`  
14. `counterfactual-f003` ← multi-I  
15. `retrieval-f009`  
16. `aggregation-f004`  
17. `aggregation-f040` ← multi-I  
18. `counterfactual-f005`  
19. `preference_inference-f014` ← multi-I  
20. `contradiction-f006` ← multi-I  
21. `counterfactual-f010`  
22. `contradiction-f011` ← multi-I  
23. `counterfactual-f001`  
24. `contradiction-f004`  
25. `aggregation-f037`  

**multi_i_both_pass (7):** `aggregation-f040`, `contradiction-f006`, `contradiction-f011`, `counterfactual-f002`, `counterfactual-f003`, `preference_inference-f014`, `retrieval-f017`

---

## 3. Leg expansion rule (same as Study 1 / `paper2_exec_run.sh`)

For each task in order: **G0** (probe-only) → **G1** (I1) → **G2** (I2) iff task ∈ multi-I set.

### First task units (integrity-watch window)

| Leg # | Task | Leg | CF task |
| ---: | --- | --- | --- |
| 1 | `retrieval-f010` | G0 | `retrieval-f010` |
| 2 | `retrieval-f010` | G1 | `retrieval-f010` |
| 3 | `retrieval-f017` | G0 | `retrieval-f017` |
| 4 | `retrieval-f017` | G1 | `retrieval-f017` |
| 5 | `retrieval-f017` | G2 | `retrieval-f017-I2` |
| … | … | … | … through leg 57, then next family |

First **1–2 task units** = `retrieval-f010` (G0+G1) and optionally start of `retrieval-f017`.

---

## 4. Launch-script inventory (locked pre-launch path)

| Script / artifact | Role |
| --- | --- |
| `scripts/study2_bind_execution_key.sh` | **Only** Study 2 script present — credential bind + verify |
| `out/study2_launch_manifest.md` / `.json` | Snapshot: commit, prereg hash, roster, N, key, outs |
| `scripts/paper2_gate0a_*_smoke.sh` | **Forbidden** for main matrix (SMALL lane) |
| `scripts/paper2_exec_small_lane.sh` | **Forbidden** (binds SMALL) |
| Study 2 matrix runner (`study2_matrix*.sh` / equivalent) | **MISSING** |

Live bind recheck at inspect time: **PASS** (`008…9dd`, `limit_remaining≈$1268.49`, SMALL unset).
