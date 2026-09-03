# Paper 2 — Tier 1 inject-probe gate

Written 2026-09-03T20:25:07.340926+00:00.
Live apply via `cf_inject.py` (not `--probe-only`). Snapshot restore between units.
No agent. No judge. Sealed registry / D untouched.

Group 1 (non-`-I2`): **18** `aggregation-f004` … `retrieval-f017`
Group 2 (`-I2`): **5** `aggregation-f040-I2` … `retrieval-f017-I2`

**Total: 21 PASS / 0 REJECT (identifiability) / 1 REJECT (held-leak) / 1 technical-failure** (of 23).

### By group

| group | PASS | REJECT_id | REJECT_held | tech |
| --- | ---: | ---: | ---: | ---: |
| group1 non-I2 | 16 | 0 | 1 | 1 |
| group2 -I2 | 5 | 0 | 0 | 0 |

### `contradiction-f011` pair (partial multi-I failure clause)

- I1 (`contradiction-f011`): **PASS**
- I2 (`contradiction-f011-I2`): **PASS**

Each variant is its own unit; a reject does not relabel the task as single-I.

| task_id | group | verdict | gold_moved | fails |
| --- | --- | --- | --- | --- |
| `aggregation-f004` | 1 | PASS | True |  |
| `aggregation-f020` | 1 | REJECT_held_leak | True | extra probes moved but must not |
| `aggregation-f036` | 1 | PASS | True |  |
| `aggregation-f040` | 1 | technical_failure | None | restore_failed |
| `contradiction-f003` | 1 | PASS | True |  |
| `contradiction-f004` | 1 | PASS | True |  |
| `contradiction-f006` | 1 | PASS | True |  |
| `contradiction-f011` | 1 | PASS | True |  |
| `contradiction-f017` | 1 | PASS | True |  |
| `contradiction-f022` | 1 | PASS | True |  |
| `counterfactual-f002` | 1 | PASS | True |  |
| `counterfactual-f003` | 1 | PASS | True |  |
| `counterfactual-f005` | 1 | PASS | True |  |
| `counterfactual-f010` | 1 | PASS | True |  |
| `counterfactual-f013` | 1 | PASS | True |  |
| `retrieval-f002` | 1 | PASS | True |  |
| `retrieval-f005` | 1 | PASS | True |  |
| `retrieval-f017` | 1 | PASS | True |  |
| `aggregation-f040-I2` | 2 | PASS | True |  |
| `contradiction-f006-I2` | 2 | PASS | True |  |
| `contradiction-f011-I2` | 2 | PASS | True |  |
| `counterfactual-f002-I2` | 2 | PASS | True |  |
| `retrieval-f017-I2` | 2 | PASS | True |  |

