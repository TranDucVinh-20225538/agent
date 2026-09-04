# Paper 2 — analysis universe (frozen after inject-probe)

Originally frozen `2026-09-04T07:38:44.958454+00:00`. Amended `2026-09-04T08:04:27.214421+00:00`: `contradiction-f024` → REJECTED_NOT_IDENTIFIABLE (agent-facing receipt channel never moved; vaultbank PASS rescinded). Semantic D not rewritten. No agent.

- **|M|** = 4: `claude-opus-4-6, gpt-5.5, qwen/qwen3.8-flash, qwen/qwen3.5-9b`
- **|T|** = 25 tasks with ≥1 PASS variant
- **Surviving variants** = 32
- **n_multiI** (I1+I2 both PASS) = 7: `aggregation-f040, contradiction-f006, contradiction-f011, counterfactual-f002, counterfactual-f003, preference_inference-f014, retrieval-f017`
- **Rejected** = 2: `situated_action-f029`, `contradiction-f024`
- **Pending** = 0: (none)

## Legs (PAPER2_SPEC Cost)

`legs = |M|×|T|×2 + |M|×n_multiI = 4×25×2 + 4×7 = **228**`

- base paired: 200
- multi-I extra: 28

`n_min` = 3 (unchanged).

## Amendment — contradiction-f024

Tier-3 gate recorded PASS on a relative patch to vaultbank `CHILIS…` txn, while frozen component `chilis_receipt_amount` and the rubric/instruction require `~/Downloads` Chili's receipt (held in `do_not_touch`). That is a channel rescue, not identifiability of D. Reclassified **REJECTED_NOT_IDENTIFIABLE** before cell 1. No absolute file patch; no D rewrite.

## Surviving variants

- `aggregation-f004`
- `aggregation-f020`
- `aggregation-f036`
- `aggregation-f037`
- `aggregation-f040`
- `aggregation-f040-I2`
- `contradiction-f003`
- `contradiction-f004`
- `contradiction-f006`
- `contradiction-f006-I2`
- `contradiction-f011`
- `contradiction-f011-I2`
- `contradiction-f014`
- `contradiction-f017`
- `contradiction-f022`
- `counterfactual-f001`
- `counterfactual-f002`
- `counterfactual-f002-I2`
- `counterfactual-f003`
- `counterfactual-f003-I2`
- `counterfactual-f005`
- `counterfactual-f010`
- `counterfactual-f013`
- `preference_inference-f010`
- `preference_inference-f014`
- `preference_inference-f014-I2`
- `retrieval-f002`
- `retrieval-f005`
- `retrieval-f009`
- `retrieval-f010`
- `retrieval-f017`
- `retrieval-f017-I2`

## Tasks in analysis |T|

- `aggregation-f004`
- `aggregation-f020`
- `aggregation-f036`
- `aggregation-f037`
- `aggregation-f040`
- `contradiction-f003`
- `contradiction-f004`
- `contradiction-f006`
- `contradiction-f011`
- `contradiction-f014`
- `contradiction-f017`
- `contradiction-f022`
- `counterfactual-f001`
- `counterfactual-f002`
- `counterfactual-f003`
- `counterfactual-f005`
- `counterfactual-f010`
- `counterfactual-f013`
- `preference_inference-f010`
- `preference_inference-f014`
- `retrieval-f002`
- `retrieval-f005`
- `retrieval-f009`
- `retrieval-f010`
- `retrieval-f017`
