# Stage 4 size ablation Qwen3.5-9B (frozen f001+f003)

Confirmatory size ablation vs OpenRouter Qwen3.5-35B-A3B. Same SQL, rubric, and qwen_cuabash. Not a substitute for 35B-A3B.

Funnel: 184 → 10 eligible → 8 confirmatory sample → 4 confounded (no Claude, remain in sample) → 4 identifiable Claude (this session). Reserves retrieval-f003 / retrieval-f016 were not promoted.

Confounded sample members not run: retrieval-f029, retrieval-f030, aggregation-f018, preference_inference-f004.

Judge score is auxiliary. Attribution DV is the final-answer field named in PROMPT_STAGE4.md.

| task_id | evidence_type | determining_set | baseline_gold | counterfactual_gold | baseline_DV | counterfactual_DV | tracks_determining_set | judge_score_baseline | judge_score_counterfactual | intervention | status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| retrieval-f001 | point_field | dinoco-airlines.sqlite loyalty.{status,miles,miles_ytd} | Gold Voyager / 38450 miles / 14280 ytd | Silver Voyager / 8620 miles / 8620 ytd | silver=False gold=True numbers=['38450', '38450'] | silver=True gold=False numbers=['8620', '8620', '8620'] | yes | 80 | 80 | UPDATE loyalty SET status=Silver Voyager, miles=8620, miles_ytd=8620 | ok |
| aggregation-f003 | aggregation | filed prior-year tax_returns.{federal_refund_amount,state_refund_amount} | n_filed=2 combined=4871.70 years=[2023,2024] | n_filed=2 combined=400.00 years=[2023,2024] | numbers=['202', '4', '202', '3', '202', '4', '3150', '2556', '594', '202', '3', '1722'] | numbers=['202', '4', '202', '3', '202', '3', '202', '3', '150', '100', '50', '202'] | yes | 50 | 80 | filed 2023 refunds 100+50; filed 2024 refunds 200+50; 2025 untouched | ok |

Rows in this table: retrieval-f001, aggregation-f003. f018/f004 were not run in this job.
