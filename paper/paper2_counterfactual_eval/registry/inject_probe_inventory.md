# Paper 2 inject-probe inventory (Phase 1)

Semantic \(D\) frozen. This table does **not** invent SQL.
Tiers corrected: f024 only in Tier 3; previously unassigned 8 tasks placed.

**Tier axis = probe/backend risk**, not operational volume. Multi-I is
an extra probe surface (column MULTI / two `--probe-only` variants), not
a reason to demote a clean sqlite task to Tier 2.

Models (sealed): `claude-opus-4-6`, `gpt-5.5`, `qwen/qwen3.8-flash`, `qwen/qwen3.5-9b`
(A3B→Flash amendment 2026-09-03; A3B is **not** in \(\mathcal{M}\)).

## Tiers

| Tier | Meaning | IDs |
| --- | --- | --- |
| 1 | SQL/numeric, prove harness | aggregation-f004, aggregation-f020, aggregation-f036, aggregation-f040, contradiction-f003, contradiction-f004, contradiction-f006, contradiction-f011, contradiction-f017, contradiction-f022, counterfactual-f002, counterfactual-f003, counterfactual-f005, counterfactual-f010, counterfactual-f013, retrieval-f002, retrieval-f005, retrieval-f017 |
| 2 | mixed booking/mail/identity | contradiction-f014, counterfactual-f001, preference_inference-f014, retrieval-f009, retrieval-f010 |
| 3 | probe gates / likely reject | aggregation-f037, contradiction-f024, preference_inference-f010, situated_action-f029 |

## Inventory

| Task | n_D | held | MULTI | Backend | Primitive | Risk |
| --- | ---: | --- | --- | --- | --- | --- |
| `aggregation-f004` T1 | 2 | — |  | multi-sqlite | sql_update (primary I) | low |
| `aggregation-f020` T1 | 2 | card_limit |  | multi-sqlite | sql_update (primary I) | low |
| `aggregation-f036` T1 | 1 | improv_txn_count_last_full_year |  | vaultbank.sqlite | sql_update (primary I) | low |
| `aggregation-f037` T3 | 2 | — |  | mail sqlite / timestamps | see review_decision — likely reject | HIGH |
| `aggregation-f040` T1 | 2 | — | yes | multi-sqlite | sql_update I1 + I2 (two variants) | low |
| `contradiction-f003` T1 | 2 | — |  | multi-sqlite | sql_update (primary I) | low |
| `contradiction-f004` T1 | 2 | gme_avg_cost |  | multi-sqlite | sql_update (primary I) | low |
| `contradiction-f006` T1 | 3 | — | yes | multi-sqlite | sql_update I1 + I2 (two variants) | low |
| `contradiction-f011` T1 | 2 | — | yes | multi-sqlite | sql_update I1 + I2 (two variants) | low |
| `contradiction-f014` T2 | 2 | lockedin_title_company |  | multi-sqlite | sql_update (primary I) | med |
| `contradiction-f017` T1 | 2 | — |  | multi-sqlite | sql_update (primary I) | low |
| `contradiction-f022` T1 | 2 | — |  | multi-sqlite | sql_update (primary I) | low |
| `contradiction-f024` T3 | 2 | — |  | file + sqlite | see review_decision — likely reject | HIGH |
| `counterfactual-f001` T2 | 2 | — |  | multi-sqlite | sql_update (primary I) | med |
| `counterfactual-f002` T1 | 2 | — | yes | multi-sqlite | sql_update I1 + I2 (two variants) | low |
| `counterfactual-f003` T1 | 2 | — | yes | multi-sqlite | sql_update I1 + I2 (two variants) | low |
| `counterfactual-f005` T1 | 2 | gme_avg_cost |  | multi-sqlite | sql_update (primary I) | low |
| `counterfactual-f010` T1 | 2 | — |  | multi-sqlite | sql_update (primary I) | low |
| `counterfactual-f013` T1 | 3 | — |  | multi-sqlite | sql_update (primary I) | low |
| `preference_inference-f010` T3 | 2 | — |  | mail sqlite / timestamps | see review_decision — likely reject | HIGH |
| `preference_inference-f014` T2 | 2 | — | yes | cheskepdia.sqlite | sql_update I1 + I2 (two variants) | med |
| `retrieval-f002` T1 | 1 | — |  | multi-sqlite | sql_update (primary I) | low |
| `retrieval-f005` T1 | 2 | monthly_payee_membership |  | multi-sqlite | sql_update (primary I) | low |
| `retrieval-f009` T2 | 3 | — |  | multi-sqlite | sql_update (primary I) | med |
| `retrieval-f010` T2 | 2 | — |  | cheskepdia.sqlite | sql_update (primary I) | med |
| `retrieval-f017` T1 | 2 | — | yes | oddsmarket.sqlite | sql_update I1 + I2 (two variants) | low |
| `situated_action-f029` T3 | 0 | — |  | file/action (no D) | see review_decision — likely reject | HIGH |
