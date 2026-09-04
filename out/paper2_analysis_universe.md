# Paper 2 — analysis universe (frozen after inject-probe)

Frozen 2026-09-04T07:38:44.958454+00:00. No agent. Sealed semantic registry untouched.

- **|M|** = 4: `claude-opus-4-6, gpt-5.5, qwen/qwen3.8-flash, qwen/qwen3.5-9b`
- **|T|** = 26 tasks with ≥1 PASS variant
- **Surviving variants** = 33
- **n_multiI** (I1+I2 both PASS) = 7: `aggregation-f040, contradiction-f006, contradiction-f011, counterfactual-f002, counterfactual-f003, preference_inference-f014, retrieval-f017`
- **Rejected** = 1: `situated_action-f029`
- **Pending** = 0: (none)

## Legs (PAPER2_SPEC Cost)

`legs = |M|×|T|×2 + |M|×n_multiI = 4×26×2 + 4×7 = **236**`

- base paired: 208
- multi-I extra: 28

`n_min` = 3 (unchanged).

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
- `contradiction-f024`
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
- `contradiction-f024`
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

