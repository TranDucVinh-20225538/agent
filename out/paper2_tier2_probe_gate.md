# Paper 2 — Tier 2 inject-probe gate

Written 2026-09-03T21:28:59.456755+00:00.
Live apply via `cf_inject.py` (not `--probe-only`). Snapshot restore between units.
No agent. No judge. Sealed registry / D untouched.

Group 1 (non-`-I2`): **5** `contradiction-f014` … `retrieval-f010`
Group 2 (`-I2`): **1** `preference_inference-f014-I2` … `preference_inference-f014-I2`

**Total: 6 PASS / 0 REJECT (identifiability) / 0 REJECT (held-leak) / 0 technical-failure** (of 6).

### By group

| group | PASS | REJECT_id | REJECT_held | tech |
| --- | ---: | ---: | ---: | ---: |
| group1 non-I2 | 5 | 0 | 0 | 0 |
| group2 -I2 | 1 | 0 | 0 | 0 |

### `preference_inference-f014` pair (partial multi-I failure clause)

- I1 (`preference_inference-f014`): **PASS**
- I2 (`preference_inference-f014-I2`): **PASS**

Each variant is its own unit; a reject does not relabel the task as single-I.

| task_id | group | verdict | gold_moved | fails |
| --- | --- | --- | --- | --- |
| `contradiction-f014` | 1 | PASS | True |  |
| `counterfactual-f001` | 1 | PASS | True |  |
| `preference_inference-f014` | 1 | PASS | True |  |
| `retrieval-f009` | 1 | PASS | True |  |
| `retrieval-f010` | 1 | PASS | True |  |
| `preference_inference-f014-I2` | 2 | PASS | True |  |

