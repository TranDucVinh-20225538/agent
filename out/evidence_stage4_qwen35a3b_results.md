# Stage 4 exploratory qwen35a3b (same frozen tasks/SQL as Claude)

Exploratory cross-model transfer under the same frozen task/intervention protocol. Agent/model changed (qwen35a3b); tasks, SQL, rubric, and DVs are unchanged. Not confirmatory Qwen replication. Claude Stage 4 tables were not modified.

Funnel: 184 → 10 eligible → 8 confirmatory sample → 4 confounded (no Claude, remain in sample) → 4 identifiable Claude (this session). Reserves retrieval-f003 / retrieval-f016 were not promoted.

Confounded sample members not run: retrieval-f029, retrieval-f030, aggregation-f018, preference_inference-f004.

Judge score is auxiliary. Attribution DV is the final-answer field named in PROMPT_STAGE4.md.

| task_id | evidence_type | determining_set | baseline_gold | counterfactual_gold | baseline_DV | counterfactual_DV | tracks_determining_set | judge_score_baseline | judge_score_counterfactual | intervention | status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| retrieval-f001 | point_field | dinoco-airlines.sqlite loyalty.{status,miles,miles_ytd} | Gold Voyager / 38450 miles / 14280 ytd | Silver Voyager / 8620 miles / 8620 ytd | silver=False gold=True numbers=['38450'] | silver=True gold=False numbers=['8620'] | yes | 100 | 100 | UPDATE loyalty SET status=Silver Voyager, miles=8620, miles_ytd=8620 | ok |
| aggregation-f003 | aggregation | filed prior-year tax_returns.{federal_refund_amount,state_refund_amount} | n_filed=2 combined=4871.70 years=[2023,2024] | n_filed=2 combined=400.00 years=[2023,2024] | numbers=['202', '3', '202', '4', '3150', '202', '3', '1722', '100', '3150', '1722', '4872'] | numbers=[] | unclear | 75 | 0 | filed 2023 refunds 100+50; filed 2024 refunds 200+50; 2025 untouched | ok |
| preference_inference-f018 | multi_record | batbucks holdings GME.{shares,avg_cost} AND oddsmarket WILL-GME-100-YEAREND YES | GME 85@42.12 AND OM YES 200 active | GME shares=0 AND OM YES shares=0 status=closed | asserts_gme_shares=True asserts_yes_bet=True | asserts_gme_shares=False asserts_yes_bet=False | unclear | 100 | 21 | GME shares=0; OM YES shares=0 status=closed (joint D, not 2x2) | ok |
| counterfactual-f004 | contradiction_cross_source | Gringotts improv income + SpeedTax 1099 amounts (tuition/calendar/mail held fixed) | pays tuition AND receives 1099 (contradiction present) | pays tuition; improv income/1099 amount = 0 (contradiction absent) | missing | missing | unclear | 0 | 0 | zero positive improv transactions; zero 1099_amount_0 and 1099 nonemployee_compensation | failure |

Nulls and failures are kept as rows. No sampled id was omitted.
