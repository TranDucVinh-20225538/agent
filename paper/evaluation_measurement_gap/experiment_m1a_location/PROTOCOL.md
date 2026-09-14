# M1a × locked score join — protocol (frozen before counting)

**Status:** FROZEN. One read-only join. No new agent run. No new parser. No screenshot OCR. No P3/P4 instrument change.

**Date:** 2026-09-13  
**Parent paper commit at start of this workstream:** `8f58a3c`

This is **not** a 171-trajectory audit, not an Evidence Availability Matrix, and not a transport of M1a.

---

## Question

On the 13 locked M1a rows, what locked Study-2 score/eligibility facts join to the same `(lane, task, leg)`?

M1a already says: gold was in the answer and in `found`, then fail-closed aggregation discarded it. This join asks only whether the **screenshot-rubric score** \(S\) and pair-level \(Y\) on that same episode can be high / zero while that discard happens.

## Population (locked)

Exactly the 13 M1a rows named in `paper/paper3_observation_grounded/P3_1_REPAIR_SPEC.md` §A-9.3 (row-level agreement with P3-0.7):

| lane | task | leg | component |
|---|---|---|---|
| flash | counterfactual-f010 | G0 | liquid_cash |
| flash | counterfactual-f013 | G0 | batbucks_dividends |
| flash | counterfactual-f013 | G0 | gringotts_savings |
| flash | counterfactual-f013 | G1 | gringotts_savings |
| flash | retrieval-f009 | G1 | nyc_flight_confirmation |
| flash | retrieval-f010 | G1 | host_name |
| gpt | aggregation-f020 | G0 | batbucks_cash |
| gpt | retrieval-f009 | G0 | nyc_hotel_confirmation |
| gpt | retrieval-f009 | G1 | nyc_flight_confirmation |
| flash | counterfactual-f005 | G1 | gme_shares |
| claude | counterfactual-f005 | G0 | gme_avg_cost |
| claude | counterfactual-f005 | G0 | gme_shares |
| flash | aggregation-f020 | G1 | batbucks_cash |

No other rows. No 57-leg expansion. No 171-leg expansion.

## Channels (allowed / forbidden)

| Channel | Rule |
|---|---|
| Gold in answer | Definitional TRUE (R1 + M1a). Do not re-read traj. |
| Gold in `found` | Definitional TRUE (M1a). Do not re-wrap extractor. |
| Extractor match on this component | Definitional FALSE (M1a). Optionally confirm from `out/study2_sts_pairs.json` `matches0`/`matches1` when the cell is in \(\mathcal{A}\). |
| Pair-level \(Y\) | Join `out/study2_layerA.csv` on `(lane, task)` if that pair is in \(\mathcal{A}\). Else `Y = N/A`. |
| Leg \(S\) | If `(lane, task)` in `out/study2_valid_pairs.csv`, take `s0` for G0 and `s1` for G1. Else if `(lane, task, leg)` is in `study2_completion_conditional.json` → `high_S_no_DONE_cells`, take that `score` and mark `DONE=false`. Else **UNKNOWN**. Do not impute. |
| DONE | If pair in \(\mathcal{A}\): that leg is `VALID_DONE`. If listed in `high_S_no_DONE_cells`: not DONE. Else UNKNOWN. |
| Guest gold exists | Definitional TRUE (non-vacuous M1a). |
| Gold string in tool/action fields of `traj.jsonl` | Only if the Paper-2 traj file exists on this workstation. If missing: **STOP-NO-TRAJ** for this channel. Do not OCR screenshots. Do not treat screenshot bytes as text. |
| Screenshot contains determining evidence | **Forbidden.** |

## Licensed claim (max)

Existence + structure on joinable M1a rows:

> A screenshot-rubric score can be high (including 100) on the same leg where the frozen text extractor discarded gold it had already collected.

Forbidden:

- prevalence over CUA evaluators
- 171 as N
- “screenshots contained gold”
- “all Flash S=100 episodes are M1a”
- mixing P4-D into this join
- treating UNKNOWN as 0 or as 100

Denominator for any \(S=100\) count is **joinable rows only**.

## Inputs (read-only)

- This protocol
- `P3_1_REPAIR_SPEC.md` A-9.3
- `out/study2_valid_pairs.csv`
- `out/study2_layerA.csv`
- `out/study2_sts_pairs.json`
- `out/study2_completion_conditional.json` (or `.hpc_import/out/` copy if `out/` missing the high-S list)

Do not modify P3 extractor, P4 instruments, or Paper-2 archives.

## Execution

Run `join_m1a_scores.py` **once**. Write `RESULT.md` + `join.json`. Do not iterate the join rule after seeing counts.
