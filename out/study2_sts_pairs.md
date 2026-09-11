# Study 2 STS / Y on A (EXPLORATORY)

- extractor SHA: `3242c30a1423f9ef90754809e50cd2698c5560b5`
- legs written: 36 → `out/study2_hatd_legs.jsonl`
- Y = binary_track on G0∧G1; non-A not recoded as Y=0
- `preference_inference-f010` gold=null (no frozen latency formula) → fail-closed match 0

| lane | task | STS0 | STS1 | STS | Y | S0 | S1 | ΔS | gold_null |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| gpt | aggregation-f020 | 0.000 | 0.333 | 0.167 | 0 | 83 | 64 | -19 | False |
| gpt | aggregation-f037 | 0.000 | 0.000 | 0.000 | 0 | 100 | 75 | -25 | False |
| gpt | contradiction-f004 | 0.000 | 0.000 | 0.000 | 0 | 85 | 85 | 0 | False |
| gpt | counterfactual-f005 | 0.000 | 0.000 | 0.000 | 0 | 83 | 100 | 17 | False |
| gpt | counterfactual-f010 | 0.000 | 0.000 | 0.000 | 0 | 83 | 87 | 4 | False |
| gpt | preference_inference-f014 | 0.000 | 0.000 | 0.000 | 0 | 0 | 52 | 52 | False |
| gpt | retrieval-f002 | 1.000 | 0.000 | 0.500 | 0 | 75 | 75 | 0 | False |
| gpt | retrieval-f009 | 0.667 | 0.333 | 0.500 | 0 | 40 | 40 | 0 | False |
| gpt | retrieval-f017 | 0.000 | 0.000 | 0.000 | 0 | 75 | 100 | 25 | False |
| flash | contradiction-f006 | 0.000 | 0.000 | 0.000 | 0 | 82 | 82 | 0 | False |
| flash | counterfactual-f010 | 0.000 | 0.000 | 0.000 | 0 | 100 | 100 | 0 | False |
| flash | counterfactual-f013 | 0.333 | 0.667 | 0.500 | 0 | 100 | 100 | 0 | False |
| flash | preference_inference-f010 | 0.000 | 0.000 | 0.000 | 0 | 100 | 100 | 0 | True |
| flash | preference_inference-f014 | 0.000 | 0.000 | 0.000 | 0 | 84 | 100 | 16 | False |
| flash | retrieval-f002 | 1.000 | 0.000 | 0.500 | 0 | 100 | 100 | 0 | False |
| flash | retrieval-f009 | 0.667 | 0.000 | 0.333 | 0 | 100 | 100 | 0 | False |
| flash | retrieval-f010 | 1.000 | 0.000 | 0.500 | 0 | 100 | 100 | 0 | False |
| claude | counterfactual-f013 | 0.000 | 0.000 | 0.000 | 0 | 100 | 100 | 0 | False |

- GPT mean pair-STS=0.12962962962962962 mean Y=0.0 n=9
- Flash mean pair-STS=0.22916666666666666 mean Y=0.0 n=8
- Claude mean pair-STS=0.0 mean Y=0.0 n=1 (not ranked)

