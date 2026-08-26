# Stage 4 exploratory openai (same frozen tasks/SQL as Claude)

Exploratory cross-model transfer under the same frozen task/intervention protocol. Agent/model changed (openai); tasks, SQL, rubric, and DVs are unchanged. Not confirmatory Qwen replication. Claude Stage 4 tables were not modified.

Funnel: 184 → 10 eligible → 8 confirmatory sample → 4 confounded (no Claude, remain in sample) → 4 identifiable Claude (this session). Reserves retrieval-f003 / retrieval-f016 were not promoted.

Confounded sample members not run: retrieval-f029, retrieval-f030, aggregation-f018, preference_inference-f004.

Judge score is auxiliary. Attribution DV is the final-answer field named in PROMPT_STAGE4.md.

| task_id | evidence_type | determining_set | baseline_gold | counterfactual_gold | baseline_DV | counterfactual_DV | tracks_determining_set | judge_score_baseline | judge_score_counterfactual | intervention | status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| retrieval-f001 | point_field | dinoco-airlines.sqlite loyalty.{status,miles,miles_ytd} | Gold Voyager / 38450 miles / 14280 ytd | Silver Voyager / 8620 miles / 8620 ytd | silver=False gold=True numbers=['38450'] | silver=True gold=False numbers=['8620', '8620'] | yes | 100 | 100 | UPDATE loyalty SET status=Silver Voyager, miles=8620, miles_ytd=8620 | ok |
| aggregation-f003 | aggregation | filed prior-year tax_returns.{federal_refund_amount,state_refund_amount} | n_filed=2 combined=4871.70 years=[2023,2024] | n_filed=2 combined=400.00 years=[2023,2024] | numbers=['4871.70', '4872', '4871.70', '4872', '4871.70', '202', '4', '202', '3', '4872', '4871.70', '202'] | numbers=['400'] | yes | 50 | 50 | filed 2023 refunds 100+50; filed 2024 refunds 200+50; 2025 untouched | ok |
| preference_inference-f018 | multi_record | batbucks holdings GME.{shares,avg_cost} AND oddsmarket WILL-GME-100-YEAREND YES | GME 85@42.12 AND OM YES 200 active | GME shares=0 AND OM YES shares=0 status=closed | missing | missing | unclear | 0 | 0 | GME shares=0; OM YES shares=0 status=closed (joint D, not 2x2) | failure |
| counterfactual-f004 | contradiction_cross_source | Gringotts improv income + SpeedTax 1099 amounts (tuition/calendar/mail held fixed) | pays tuition AND receives 1099 (contradiction present) | pays tuition; improv income/1099 amount = 0 (contradiction absent) | contradiction_flag=unclear savings_1099=mentions_1099 | contradiction_flag=unclear savings_1099=mentions_1099 | unclear | 87 | 87 | zero positive improv transactions; zero 1099_amount_0 and 1099 nonemployee_compensation | ok |

Nulls and failures are kept as rows. No sampled id was omitted.
