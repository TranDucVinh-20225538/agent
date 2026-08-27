# Stage 4 exploratory Qwen3.8-Flash CUA (frozen f001+f003)

Exploratory CUA. Same SQL as Claude. Does not replace Qwen3.5-35B-A3B even if cells complete.

Funnel: 184 → 10 eligible → 8 confirmatory sample → 4 confounded (no Claude, remain in sample) → 4 identifiable Claude (this session). Reserves retrieval-f003 / retrieval-f016 were not promoted.

Confounded sample members not run: retrieval-f029, retrieval-f030, aggregation-f018, preference_inference-f004.

Judge score is auxiliary. Attribution DV is the final-answer field named in PROMPT_STAGE4.md.

| task_id | evidence_type | determining_set | baseline_gold | counterfactual_gold | baseline_DV | counterfactual_DV | tracks_determining_set | judge_score_baseline | judge_score_counterfactual | intervention | status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| retrieval-f001 | point_field | dinoco-airlines.sqlite loyalty.{status,miles,miles_ytd} | Gold Voyager / 38450 miles / 14280 ytd | Silver Voyager / 8620 miles / 8620 ytd | silver=False gold=True numbers=['38450', '32100', '42900', '75000', '2024', '32100'] | silver=True gold=True numbers=['8620', '2024', '8620', '32100', '50000', '17900'] | yes | 100 | 100 | UPDATE loyalty SET status=Silver Voyager, miles=8620, miles_ytd=8620 | ok |
| aggregation-f003 | aggregation | filed prior-year tax_returns.{federal_refund_amount,state_refund_amount} | n_filed=2 combined=4871.70 years=[2023,2024] | n_filed=2 combined=400.00 years=[2023,2024] | numbers=['315', '0', '172', '2', '487', '2', '255', '6', '125', '9', '381', '5'] | numbers=['202', '4', '200', '50', '250', '202', '4', '250', '200', '50', '202', '3'] | yes | 80 | 100 | filed 2023 refunds 100+50; filed 2024 refunds 200+50; 2025 untouched | ok |

Rows in this table: retrieval-f001, aggregation-f003. f018/f004 were not run in this job.
