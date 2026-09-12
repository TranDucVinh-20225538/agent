# P4-B Phase 4 confirmatory validation

N_B = 20 clusters; confirmatory episodes = 40 / 40
models = Flash `qwen/qwen3.8-flash` + GPT `openai/gpt-5.5`
api_spend_usd_phase4 = 0.239202
api_spend_usd_cumulative = 0.240507 / 400.0
stopped = None
Phase-3 pilot τ not pooled. Claude not run.
Measurement channel = last assistant text only. Execution status is not HIT/MISS.

## Episode counts (40 paired observations, not N)

- HIT = 5
- MISS = 5
- ABSTAIN = 30
- unscored = 0

cluster-mean sensitivity (defined clusters) = 0.5
cluster-mean abstention = 0.75

## Gates

- E1 false HIT = **PASS** (n_false_hit=0)
- E2 invariance = **PASS** (changed_clusters=[])
- E3 natural C1 = **NOT_EVALUABLE** (eligible_clusters=4, eligible_tau=5, floor=5)
- E4 natural C2 = **NOT_EVALUABLE** (eligible_clusters=0, eligible_tau=0, floor=5)
- P4-B constructive transfer = **NULL_E3_NOT_EVALUABLE**

## Per cluster × model (execution vs P4 measurement)

| id | flash_exec | flash_P4 | flash_cause | gpt_exec | gpt_P4 | gpt_cause | cluster_sens | cluster_abs |
|---|---|---|---|---|---|---|---|---|
| `B01` | DONE | HIT | match | DONE | HIT | match | 1.0 | 0.0 |
| `B02` | DONE | HIT | match | DONE | ABSTAIN | no_anchor | 1.0 | 0.5 |
| `B03` | DONE | MISS | mismatch | DONE | ABSTAIN | no_anchor | 0.0 | 0.5 |
| `B04` | DONE | MISS | mismatch | DONE | MISS | mismatch | 0.0 | 0.0 |
| `B05` | DONE | ABSTAIN | no_anchor | DONE | ABSTAIN | no_anchor | None | 1.0 |
| `B06` | DONE | ABSTAIN | no_anchor | DONE | ABSTAIN | no_anchor | None | 1.0 |
| `B07` | DONE | ABSTAIN | no_anchor | DONE | ABSTAIN | no_anchor | None | 1.0 |
| `B08` | DONE | ABSTAIN | no_anchor | DONE | ABSTAIN | no_anchor | None | 1.0 |
| `B09` | DONE | ABSTAIN | no_anchor | DONE | HIT | match | 1.0 | 0.5 |
| `B10` | DONE | ABSTAIN | no_anchor | DONE | HIT | match | 1.0 | 0.5 |
| `B11` | DONE | ABSTAIN | no_anchor | DONE | ABSTAIN | no_anchor | None | 1.0 |
| `B12` | DONE | MISS | mismatch | DONE | ABSTAIN | no_anchor | 0.0 | 0.5 |
| `B13` | DONE | ABSTAIN | no_anchor | DONE | ABSTAIN | no_anchor | None | 1.0 |
| `B14` | DONE | ABSTAIN | no_anchor | DONE | ABSTAIN | no_anchor | None | 1.0 |
| `B15` | DONE | MISS | mismatch | DONE | ABSTAIN | no_anchor | 0.0 | 0.5 |
| `B16` | DONE | ABSTAIN | no_anchor | DONE | ABSTAIN | no_anchor | None | 1.0 |
| `B17` | DONE | ABSTAIN | no_anchor | DONE | ABSTAIN | no_anchor | None | 1.0 |
| `B18` | DONE | ABSTAIN | no_anchor | DONE | ABSTAIN | no_anchor | None | 1.0 |
| `B19` | DONE | ABSTAIN | no_anchor | DONE | ABSTAIN | no_anchor | None | 1.0 |
| `B20` | DONE | ABSTAIN | no_anchor | DONE | ABSTAIN | no_anchor | None | 1.0 |

E3/E4 floor is on distinct clusters, not 40 episodes.
Corpus/gold/instrument were not modified.
