# Paper 1 STS replay (no new runs)

Pairs: **24**. Component bits from `tracking_evidence.md`.
Alignment cell vs Paper 1 class: **24/24** match.

Do not headline a pooled STS. Partial STS (pair mean < 1):

| Model | Task | STS0 | STS1 | STS | cell | Paper 1 |
|---|---|---:|---:|---:|---|---|
| Claude | preference_inference-f018 | 1 | 0.5 | 0.75 | type_b | type_b |
| GPT | counterfactual-f004 | 1 | 0 | 0.5 | type_b | type_b |
| Claude | retrieval-f030 | 0.5 | 1 | 0.75 | type_b | type_b |
| Qwen3.5-9B | retrieval-f016 | 0.5 | 1 | 0.75 | type_b | type_b |
| Qwen3.8-Flash | retrieval-f029 | 1 | 0.5 | 0.75 | type_b | type_b |

