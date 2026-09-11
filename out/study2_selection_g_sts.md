# §6.1(g) exploratory ΔSTS on common support 4

- extractor `3242c30a1423f9ef90754809e50cd2698c5560b5`. Layer B **NOT confirmatory** (§6.1(c)).
- common: ['counterfactual-f010', 'preference_inference-f014', 'retrieval-f002', 'retrieval-f009']
- mean S0 GPT=49.5 Flash=96.0 → argmax_S0=**flash**
- mean STS GPT=0.250 Flash=0.208 → argmax_STS=**gpt**
- selection disagreement (argmax_S0 vs argmax_STS): **True**
- sign(ΔS0)≠sign(ΔSTS) on 4/4 tasks: ['counterfactual-f010', 'preference_inference-f014', 'retrieval-f002', 'retrieval-f009']
- bootstrap mean(S0_Flash−S0_GPT)={'n_pairs': 4, 'observed_mean_diff': 46.5, 'ci95': [21.0, 72.0], 'n_boot': 5000, 'seed': 20260904}
- bootstrap mean(STS_Flash−STS_GPT)={'n_pairs': 4, 'observed_mean_diff': -0.04166666666666666, 'ci95': [-0.12499999999999997, 0.0], 'n_boot': 5000, 'seed': 20260904}
- LOPO argmax fragile: True

| task | S0 GPT | S0 Flash | STS GPT | STS Flash | Y GPT | Y Flash | ΔS0 | ΔSTS | sign≠ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| counterfactual-f010 | 83 | 100 | 0.000 | 0.000 | 0 | 0 | 17 | 0.000 | 1 |
| preference_inference-f014 | 0 | 84 | 0.000 | 0.000 | 0 | 0 | 84 | 0.000 | 1 |
| retrieval-f002 | 75 | 100 | 0.500 | 0.500 | 0 | 0 | 25 | 0.000 | 1 |
| retrieval-f009 | 40 | 100 | 0.500 | 0.333 | 0 | 0 | 60 | -0.167 | 1 |

LOPO:

- leave counterfactual-f010: argmax_S0=flash argmax_STS=gpt disagree=True
- leave preference_inference-f014: argmax_S0=flash argmax_STS=gpt disagree=True
- leave retrieval-f002: argmax_S0=flash argmax_STS=gpt disagree=True
- leave retrieval-f009: argmax_S0=flash argmax_STS=tie disagree=True
