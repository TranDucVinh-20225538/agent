# Study 2 valid pairs |A|

- rule: G0∧G1 VALID_DONE; G2 ignored; n_min=3
- GPT |A|=9 ['aggregation-f020', 'aggregation-f037', 'contradiction-f004', 'counterfactual-f005', 'counterfactual-f010', 'preference_inference-f014', 'retrieval-f002', 'retrieval-f009', 'retrieval-f017']
- Flash |A|=8 ['contradiction-f006', 'counterfactual-f010', 'counterfactual-f013', 'preference_inference-f010', 'preference_inference-f014', 'retrieval-f002', 'retrieval-f009', 'retrieval-f010']
- Claude |A|=1 ['counterfactual-f013'] (report, not rank)
- Ranked roster (exploratory): GPT + Flash
- Layer B confirmatory: **NO** (§6.1(c))
- Do not recode non-DONE as Y=0
