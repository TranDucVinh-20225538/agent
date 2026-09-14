# Exploratory (Qwen3.8-Flash) — not primary

Do not pool into primary. HEAD `b7b4203`. Phase-B Flash dirs present.

| model | task | valid | tracking | scores | Δ | class |
|---|---|---|---|---|---|---|
| qwen38flash | retrieval-f001 | True | True | 100→100 | 0 | Type A |
| qwen38flash | retrieval-f003 | False | None | 100→65 | None | execution_failure |
| qwen38flash | retrieval-f016 | False | None | 100→100 | None | execution_failure |
| qwen38flash | retrieval-f029 | True | False | 100→100 | 0 | Type B |
| qwen38flash | retrieval-f030 | False | None | 0→0 | None | execution_failure |
| qwen38flash | aggregation-f003 | True | True | 80→100 | 20 | score-sensitive |
| qwen38flash | aggregation-f018 | False | None | 0→0 | None | execution_failure |
| qwen38flash | preference_inference-f004 | False | None | 0→0 | None | execution_failure |
| qwen38flash | preference_inference-f018 | False | None | — | None | execution_failure |
| qwen38flash | counterfactual-f004 | False | None | — | None | execution_failure |
