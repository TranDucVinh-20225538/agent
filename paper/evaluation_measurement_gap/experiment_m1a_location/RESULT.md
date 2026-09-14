# M1a location join — RESULT

Review-only join on the **13 locked M1a rows**. Not a 171-trajectory audit.
Denominator is **joinable M1a rows**, not 171.

## Summaries

- n_joinable_S = **10/13**
- n_S100 / joinable = **7/10**
- UNKNOWN S (3): `claude/counterfactual-f005/G0/gme_avg_cost`, `claude/counterfactual-f005/G0/gme_shares`, `flash/aggregation-f020/G1/batbucks_cash`
- n_in_A = **9**; n_in_A with Y=0 = **9**
- n_not_DONE and S=100 from the locked high-S list = **1**
- traj present = **13**; STOP-NO-TRAJ = **0**
- n_gold_in_earlier_traj_text (among rows with traj parsed) = **8**

## Table of 13 rows

| lane | task | leg | component | S | DONE | Y | in_A | traj_status | gold_last | gold_earlier |
|---|---|---|---|---|---|---|---|---|---|---|
| flash | counterfactual-f010 | G0 | liquid_cash | 100 | TRUE | 0 | TRUE | PRESENT | TRUE | TRUE |
| flash | counterfactual-f013 | G0 | batbucks_dividends | 100 | TRUE | 0 | TRUE | PRESENT | TRUE | TRUE |
| flash | counterfactual-f013 | G0 | gringotts_savings | 100 | TRUE | 0 | TRUE | PRESENT | TRUE | FALSE |
| flash | counterfactual-f013 | G1 | gringotts_savings | 100 | TRUE | 0 | TRUE | PRESENT | TRUE | TRUE |
| flash | retrieval-f009 | G1 | nyc_flight_confirmation | 100 | TRUE | 0 | TRUE | PRESENT | TRUE | TRUE |
| flash | retrieval-f010 | G1 | host_name | 100 | TRUE | 0 | TRUE | PRESENT | TRUE | TRUE |
| gpt | aggregation-f020 | G0 | batbucks_cash | 83 | TRUE | 0 | TRUE | PRESENT | TRUE | FALSE |
| gpt | retrieval-f009 | G0 | nyc_hotel_confirmation | 40 | TRUE | 0 | TRUE | PRESENT | TRUE | FALSE |
| gpt | retrieval-f009 | G1 | nyc_flight_confirmation | 40 | TRUE | 0 | TRUE | PRESENT | TRUE | FALSE |
| flash | counterfactual-f005 | G1 | gme_shares | 100 | FALSE | — | FALSE | PRESENT | TRUE | TRUE |
| claude | counterfactual-f005 | G0 | gme_avg_cost | — | — | — | FALSE | PRESENT | TRUE | TRUE |
| claude | counterfactual-f005 | G0 | gme_shares | — | — | — | FALSE | PRESENT | TRUE | TRUE |
| flash | aggregation-f020 | G1 | batbucks_cash | — | — | — | FALSE | PRESENT | TRUE | FALSE |

Definitional M1a on every row: `gold_in_answer=TRUE`, `gold_in_found=TRUE`, `extractor_match=FALSE`.

## Traj status

- `flash/counterfactual-f010/G0/liquid_cash`: PRESENT (`/data2/hpcshared/Vinh-/agent/results/paper2_exec/hpc-flash-small-gate0a-postpatch/counterfactual-f010/G0/counterfactual-f010/traj.jsonl`)
- `flash/counterfactual-f013/G0/batbucks_dividends`: PRESENT (`/data2/hpcshared/Vinh-/agent/results/paper2_exec/hpc-flash-small-gate0a-postpatch/counterfactual-f013/G0/counterfactual-f013/traj.jsonl`)
- `flash/counterfactual-f013/G0/gringotts_savings`: PRESENT (`/data2/hpcshared/Vinh-/agent/results/paper2_exec/hpc-flash-small-gate0a-postpatch/counterfactual-f013/G0/counterfactual-f013/traj.jsonl`)
- `flash/counterfactual-f013/G1/gringotts_savings`: PRESENT (`/data2/hpcshared/Vinh-/agent/results/paper2_exec/hpc-flash-small-gate0a-postpatch/counterfactual-f013/G1/counterfactual-f013/traj.jsonl`)
- `flash/retrieval-f009/G1/nyc_flight_confirmation`: PRESENT (`/data2/hpcshared/Vinh-/agent/results/paper2_exec/hpc-flash-small-gate0a-postpatch/retrieval-f009/G1/retrieval-f009/traj.jsonl`)
- `flash/retrieval-f010/G1/host_name`: PRESENT (`/data2/hpcshared/Vinh-/agent/results/paper2_exec/hpc-flash-small-gate0a-postpatch/retrieval-f010/G1/retrieval-f010/traj.jsonl`)
- `gpt/aggregation-f020/G0/batbucks_cash`: PRESENT (`/data2/hpcshared/Vinh/agent/results/paper2_exec/study2-gpt/aggregation-f020/G0/aggregation-f020/traj.jsonl`)
- `gpt/retrieval-f009/G0/nyc_hotel_confirmation`: PRESENT (`/data2/hpcshared/Vinh/agent/results/paper2_exec/study2-gpt/retrieval-f009/G0/retrieval-f009/traj.jsonl`)
- `gpt/retrieval-f009/G1/nyc_flight_confirmation`: PRESENT (`/data2/hpcshared/Vinh/agent/results/paper2_exec/study2-gpt/retrieval-f009/G1/retrieval-f009/traj.jsonl`)
- `flash/counterfactual-f005/G1/gme_shares`: PRESENT (`/data2/hpcshared/Vinh-/agent/results/paper2_exec/hpc-flash-small-gate0a-postpatch/counterfactual-f005/G1/counterfactual-f005/traj.jsonl`)
- `claude/counterfactual-f005/G0/gme_avg_cost`: PRESENT (`/data2/hpcshared/Vinh/agent/results/paper2_exec/study2-claude/counterfactual-f005/G0/counterfactual-f005/traj.jsonl`)
- `claude/counterfactual-f005/G0/gme_shares`: PRESENT (`/data2/hpcshared/Vinh/agent/results/paper2_exec/study2-claude/counterfactual-f005/G0/counterfactual-f005/traj.jsonl`)
- `flash/aggregation-f020/G1/batbucks_cash`: PRESENT (`/data2/hpcshared/Vinh-/agent/results/paper2_exec/hpc-flash-small-gate0a-postpatch/aggregation-f020/G1/aggregation-f020/traj.jsonl`)

## Licensed reading

On M1a rows that join to a locked Study-2 score, screenshot-rubric S can be 100 on the same leg where the frozen text extractor discarded collected gold.

## Not established

- 171 trajectories
- screenshots contained gold
- Flash is reliable
- prevalence
- P4-D
- Gate 0 revival
- earlier-text hit means the agent tracked gold
- earlier-text hit means the screenshot had gold

S/Y join used only `study2_valid_pairs.csv`, `study2_layerA.csv`, and the locked `high_S_no_DONE_cells` list.
Scores in `p3_0_legs.jsonl` were not used to fill UNKNOWN S.

