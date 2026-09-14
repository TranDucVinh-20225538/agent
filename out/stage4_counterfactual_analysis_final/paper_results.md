# Paper 1 — results prose (source material for `paper/paper1_counterfactual_cua/main.tex`)

Snapshot `b7b4203`. Universe: 10 pre-registered Stage-4 + Phase-B tasks x 5 model
lanes = 46 cells, 92 base/cf trajectory legs. Validity: `DONE` iff the last
`traj.jsonl` action is `DONE`; a pair is valid iff both legs are `DONE`. 57/92
legs are `DONE`; 35/92 are execution failures (`failure_audit.csv`), never
coded as "does not track." 24/46 cells are valid pairs.

## Per-model reportable unit (never pooled across models)

| Model | Tier | Valid | Tracking-valid | Type A | Sensitive | Type B | Invariance rate | 95% CI |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Claude | primary | 9 | 7 | 6 | 1 | 2 | 0.857 | [0.421, 0.996] |
| GPT | primary | 8 | 7 | 3 | 4 | 1 | 0.429 | [0.099, 0.816] |
| Qwen3.5-35B-A3B | primary | 1 | 1 | 1 | 0 | 0 | 1.000 | [0.025, 1.000] |
| Qwen3.5-9B | size ablation | 3 | 2 | 1 | 1 | 1 | 0.500 | [0.013, 0.987] |
| Qwen3.8-Flash | exploratory | 3 | 2 | 1 | 1 | 1 | 0.500 | [0.013, 0.987] |

Every CI is wide (n<=9 per model); none of the three tiers should be read as a
precise point estimate. Qwen3.5-35B-A3B's primary-tier n is 1 because 9 of its
10 cells are execution failures (mostly `EMPTY_XML`), not because it was
excluded — see `failure_audit.csv`.

## Result 1 — separability, stated at the level the data supports

Across the 24 valid pairs, three properties are jointly observed and do not
coincide: (a) task completion (`DONE`, independent of score), (b) tracking
(does the final answer follow the manipulated determining set `D` on both
legs?), (c) score invariance (does the judge move when gold moves?). All
three are possible independently:
- Track + invariant (Type A): the majority pattern among tracking-valid
  pairs for Claude (6/7) and the single Qwen3.5-35B-A3B pair, roughly even
  for GPT (3/7) and the two smaller-tier models (1/2 each).
- Track + score moves (score-sensitive): 4/7 GPT tracking-valid pairs, 1/7
  Claude, 1/2 each of the two smaller-tier models.
- Incomplete tracking + score stays high (Type B): 2/9 Claude valid pairs,
  1/8 GPT, 1/3 each of the two smaller-tier models.

No number here claims a rate that would generalize past this frozen 10-task,
24-pair sample; the CIs above are the honest expression of that.

## Result 2 — designed role vs. observed class (the paper's second axis)

Three tasks were pre-registered as "designed Type B" (`preference_inference-f018`,
`retrieval-f030`, `aggregation-f018`) and two as "score-sensitive contrast"
(`counterfactual-f004`, `preference_inference-f004`). Observed class does not
always match the design intent, and both directions occur:

- `aggregation-f018` (designed Type B) is **observed Type A** for Claude — the
  only model+task cell run on it — with fully correct joint tracking on both
  legs, including an explicit, correct flag of the deliberately-untouched
  local file as a stale mismatch. This is a genuine positive control: the
  agent tracked a two-field sqlite-only joint `D` while a dual-channel
  distractor field was held constant, and the rubric did not mask it.
- `retrieval-f030` (designed Type B) is **observed Type B for Claude** (a
  wrong-tax-year read on the base leg, not a miss on the manipulated field)
  and **observed score-sensitive for GPT** (both legs fully correct; score
  still moves 53->100 for reasons unrelated to the two `D` components).
- `preference_inference-f018` (designed Type B, Stage-4 lock) replicates as
  Type B for the one model run on it (Claude): the joint `D` has two
  components (GME shares, OddsMarket YES bet); only one is tracked on the CF
  leg, and the score (100/100) does not reflect the miss.
- `counterfactual-f004` (designed score-sensitive contrast) is **observed
  Type B for GPT**: this commit's SQL patch correctly zeroes the 1099 field
  for all three tax years (the whitespace bug noted in Round 25/26 of the
  prior audit is fixed at this snapshot), yet the agent's CF answer is
  near-identical to its base answer and still nets the stale $1,068/yr
  figure — a genuine miss, not a patch artifact.
- `preference_inference-f004` (designed score-sensitive contrast) replicates
  as score-sensitive for both Claude and GPT: both track the HangryDash
  order-count winner flip correctly (Cooper's -> Backyard Ale House) while
  the rubric's pinned "Cooper's is top" criterion goes stale and the score
  drops (100->79 Claude, 100->58 GPT).

## Result 3 — two verify-don't-overclaim findings outside the primary tier

- Qwen3.5-9B `retrieval-f016`: the base-leg answer reports a total cost basis
  of $8,788.75 against a true gold value of $8,213.25 (delta $575.50, source
  not identifiable from the trajectory) while the CF leg is exact
  ($7,114.20). Both legs score 100/100. This is a base-leg factual miss, not
  a tracking-direction claim — the CF leg is the one that is exactly right.
- Qwen3.8-Flash `retrieval-f029`: the CF leg reports "$91,200" for Box-1
  wages against a true CF gold of $90,000 (off by exactly $1,200, an
  amount matching no combination of the SQL patch); the paired federal
  withholding figure is exactly correct ($18,000). Both legs score 100/100.
  This is classified Type B (partial tracking of one field within a
  dual-channel manipulated pair), not "does not track" — the file/sqlite
  cross-check on withholding is intact.

## Rubric-mechanism reading (see `rubric_mechanism.md` for the full table)

Five cells are individually explained by their `per_rubric_max` arrays rather
than guessed at: GPT `aggregation-f003`'s stable `[1,1,0,0]` (Type A is not a
rubric-blindness artifact on the two moving criteria; the other two never
fire in either condition); the two smaller-tier models' single-additional-
criterion pattern on the same task (`[1,1,0,0]->[1,1,1,0]` and
`[1,1,1,0]->[1,1,1,1]`); Claude `retrieval-f003`'s stable, always-failing
third criterion (explains a non-100 score under full tracking and full
invariance); GPT `retrieval-f029`'s wage-criterion-invariant `[1,0,0]->[1,1,1]`
(the large 33->100 swing is driven by criteria unrelated to the wage figure
itself); and Qwen3.5-9B `retrieval-f016`'s `[1,1,1,1]` in both conditions
despite the base-leg cost-basis error — the rubric does not check the
reported grand total against gold at the precision this would require.

## What this tier of evidence does not support

This is a 24-valid-pair, 10-task, 5-model audit on one frozen benchmark
snapshot. It supports the claim that task completion, tracking, and score
invariance are separable properties observed to diverge in this sample. It
does not support a claim about population-level rates for any model, a claim
that any model is broadly unreliable, or a claim that score invariance is
inherently a flaw (see the "why invariance can be expected" framing already
in `paper/v0.1/main.tex`, which still applies to the channel-invariant
eligibility screen used here).
