# Primary Phase A+B pairs (Claude / GPT / Qwen3.5-35B-A3B)

HEAD `b7b4203`. Not pooled as a common-rate estimator. Execution failures stay in this table with classification=execution_failure.

| model | task | valid | tracking | scores | Δ | class |
|---|---|---|---|---|---|---|
| claude | retrieval-f001 | True | True | 100→100 | 0 | Type A |
| claude | retrieval-f003 | True | True | 65→65 | 0 | Type A |
| claude | retrieval-f016 | True | True | 100→100 | 0 | Type A |
| claude | retrieval-f029 | True | True | 100→100 | 0 | Type A |
| claude | retrieval-f030 | True | False | 100→100 | 0 | Type B |
| claude | aggregation-f003 | True | True | 80→80 | 0 | Type A |
| claude | aggregation-f018 | True | True | 100→100 | 0 | Type A |
| claude | preference_inference-f004 | True | True | 100→79 | -21 | score-sensitive |
| claude | preference_inference-f018 | True | False | 100→100 | 0 | Type B |
| claude | counterfactual-f004 | False | None | 0→87 | None | execution_failure |
| openai | retrieval-f001 | True | True | 100→100 | 0 | Type A |
| openai | retrieval-f003 | True | True | 100→100 | 0 | Type A |
| openai | retrieval-f016 | True | True | 100→85 | -15 | score-sensitive |
| openai | retrieval-f029 | True | True | 33→100 | 67 | score-sensitive |
| openai | retrieval-f030 | True | True | 53→100 | 47 | score-sensitive |
| openai | aggregation-f003 | True | True | 50→50 | 0 | Type A |
| openai | aggregation-f018 | False | None | 100→0 | None | execution_failure |
| openai | preference_inference-f004 | True | True | 100→58 | -42 | score-sensitive |
| openai | preference_inference-f018 | False | None | 0→0 | None | execution_failure |
| openai | counterfactual-f004 | True | False | 87→87 | 0 | Type B |
| qwen35a3b | retrieval-f001 | True | True | 100→100 | 0 | Type A |
| qwen35a3b | retrieval-f003 | False | None | 65→0 | None | execution_failure |
| qwen35a3b | retrieval-f016 | False | None | 100→0 | None | execution_failure |
| qwen35a3b | retrieval-f029 | False | None | 0→0 | None | execution_failure |
| qwen35a3b | retrieval-f030 | False | None | 0→0 | None | execution_failure |
| qwen35a3b | aggregation-f003 | False | None | 75→0 | None | execution_failure |
| qwen35a3b | aggregation-f018 | False | None | 0→0 | None | execution_failure |
| qwen35a3b | preference_inference-f004 | False | None | 0→0 | None | execution_failure |
| qwen35a3b | preference_inference-f018 | False | None | 100→21 | None | execution_failure |
| qwen35a3b | counterfactual-f004 | False | None | 0→0 | None | execution_failure |
