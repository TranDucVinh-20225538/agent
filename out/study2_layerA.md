# Layer A — calibration of S⁰ vs Y (EXPLORATORY)

**Finding: calibration is degenerate.** Y = 0 on every pair in A (GPT 9/9, Flash 8/8, Claude 1/1). Score does not separate Y=1 vs Y=0 because there is no Y=1. Observed P(Y=1 | S⁰) = 0 for every S⁰ on A.

This is a Layer A result, not a reason to recode non-DONE as Y=0 or to retune hat-D (`3242c30`).

| Agent | |A| | ranked | n Y=1 | n Y=0 | mean S⁰ | mean S⁰ \| Y=1 | mean S⁰ \| Y=0 | mean pair-STS |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| GPT | 9 | yes | 0 | 9 | 69.333 | — | 69.333 | 0.130 |
| Flash | 8 | yes | 0 | 8 | 95.750 | — | 95.750 | 0.229 |
| Claude | 1 | no (coverage) | 0 | 1 | 100.000 | — | 100.000 | 0.000 |

- S⁰ range on ranked A: GPT [0, 100] · Flash [82, 100].
- Flash mean S⁰ is higher than GPT while both have Y=0. High completion score on A is not evidence of binary track.
- Pair STS is on [0,1] after locked extractor; also does not produce Y=1 (binary track requires every positive-weight bit on both legs).
- Claude `|A|=1` is coverage-only; not ranked; Layer B **NOT confirmatory** (§6.1(c)).
- Rubric S is the existing per-step judge on disk. No re-judge.

Per-pair table: `out/study2_layerA.csv`.
