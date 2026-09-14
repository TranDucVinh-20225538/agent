# §6.1(e) completion-conditional bias (EXPLORATORY)

Excluded cells **do not enter argmax**. Incomplete / TERMINAL_FAIL is **not** Y=0.
A = G0∧G1 both VALID_DONE; G2 ignored. S is 0–100 on-disk rubric (no re-judge).

## (i) |A| and DONE rate

| Agent | |A| | cells | VALID_DONE | DONE rate | n excluded | mean S excluded | excluded S≥90 and not DONE |
|---|---:|---:|---:|---:|---:|---:|---:|
| gpt | 9 | 57 | 32 | 0.561 | 39 | 46.4 | 2 |
| flash | 8 | 57 | 29 | 0.509 | 41 | 44.9 | 2 |
| claude | 1 | 57 | 4 | 0.070 | 55 | 26.1 | 1 |

## (ii) mean S on cells excluded from A, by terminal reason

| Agent | terminal reason | n | mean S | n S≥90 | n score missing |
|---|---|---:|---:|---:|---:|
| gpt | `MAX_STEPS:GUI` | 12 | 21.8 | 0 | 0 |
| gpt | `MAX_STEPS:TOOL_CALL` | 3 | 41.0 | 1 | 0 |
| gpt | `MAX_STEPS:WAIT` | 5 | 24.8 | 0 | 0 |
| gpt | `TERMINAL_FAIL:FAIL` | 1 | 0.0 | 0 | 0 |
| gpt | `TERMINAL_FAIL:GUI` | 1 | — | 0 | 1 |
| gpt | `TERMINAL_FAIL:NO_ACTION_ABORT` | 2 | 50.0 | 1 | 0 |
| gpt | `TERMINAL_FAIL:PREDICT_CRASH` | 1 | 20.0 | 0 | 0 |
| gpt | `VALID_DONE` | 14 | 81.2 | 6 | 0 |
| flash | `MAX_STEPS:GUI` | 9 | 31.0 | 0 | 0 |
| flash | `MAX_STEPS:TOOL_CALL` | 4 | 20.8 | 0 | 0 |
| flash | `MAX_STEPS:WAIT` | 1 | 20.0 | 0 | 0 |
| flash | `TERMINAL_FAIL:FAIL` | 1 | 100.0 | 1 | 0 |
| flash | `TERMINAL_FAIL:NO_ACTION_ABORT` | 1 | 100.0 | 1 | 0 |
| flash | `TERMINAL_FAIL:PREDICT_CRASH` | 12 | 2.8 | 0 | 0 |
| flash | `VALID_DONE` | 13 | 94.4 | 9 | 0 |
| claude | `MAX_STEPS:GUI` | 39 | 22.4 | 1 | 0 |
| claude | `MAX_STEPS:TOOL_CALL` | 8 | 42.5 | 0 | 0 |
| claude | `MAX_STEPS:WAIT` | 1 | 0.0 | 0 | 0 |
| claude | `TERMINAL_FAIL:NO_ACTION_ABORT` | 5 | 5.0 | 0 | 0 |
| claude | `VALID_DONE` | 2 | 100.0 | 2 | 0 |

## (iii) excluded cells with S≥90 and no canonical DONE

- GPT: **2** — preference_inference-f010/G0 (S=100, MAX_STEPS:TOOL_CALL), retrieval-f010/G1 (S=100, TERMINAL_FAIL:NO_ACTION_ABORT)
- Flash: **2** — aggregation-f037/G0 (S=100, TERMINAL_FAIL:NO_ACTION_ABORT), counterfactual-f005/G1 (S=100, TERMINAL_FAIL:FAIL)
- Claude: **1** — retrieval-f002/G0 (S=100, MAX_STEPS:GUI)

Cell lists are in `out/study2_completion_conditional.json` → `high_S_no_DONE_cells`.
Unpaired VALID_DONE (one leg of a non-pair, or G2) can be excluded from A while still DONE; those are not counted in (iii).
