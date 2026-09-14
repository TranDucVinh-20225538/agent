# Size ablation (Qwen3.5-9B) — not primary

Do not pool into primary. HEAD `b7b4203`. Phase-B 9B dirs present.

| model | task | valid | tracking | scores | Δ | class |
|---|---|---|---|---|---|---|
| qwen359b | retrieval-f001 | True | True | 80→80 | 0 | Type A |
| qwen359b | retrieval-f003 | False | None | 65→65 | None | execution_failure |
| qwen359b | retrieval-f016 | True | False | 100→100 | 0 | Type B |
| qwen359b | retrieval-f029 | False | None | 0→33 | None | execution_failure |
| qwen359b | retrieval-f030 | False | None | 0→0 | None | execution_failure |
| qwen359b | aggregation-f003 | True | True | 50→80 | 30 | score-sensitive |
| qwen359b | aggregation-f018 | False | None | 0→0 | None | execution_failure |
| qwen359b | preference_inference-f004 | False | None | 0→0 | None | execution_failure |
| qwen359b | preference_inference-f018 | False | None | — | None | execution_failure |
| qwen359b | counterfactual-f004 | False | None | — | None | execution_failure |
