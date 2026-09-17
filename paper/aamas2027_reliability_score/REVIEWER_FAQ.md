# Reviewer FAQ (internal; not in the PDF)

Answers use locked paper numbers plus the HPC jackknife. No new estimand.

## Q1. Why is +8/−18 not given a confidence interval?

It is a census of the sealed 134-row corpus, not a sample from a superpopulation.
A CI would invite “significant / not significant,” which the paper already
declines (no prevalence claim). The reviewer question that is in scope is
concentration: is the split an artefact of a few tasks? That is leave-one-task-out,
not a bootstrap.

## Q2. Is +8/−18 driven by a few tasks?

No. Thirteen tasks contribute any of the 26 released abstentions (not padded to
the paper’s 61-task corpus count). Dropping any one of those 13 leaves
C ∈ [5, 8], W ∈ [10, 18], C−W ∈ [−12, −3], with C>0, W>0, and C<W in every fold
(13/13). No single task is necessary. Largest shares: 3/8 new-correct on
`retrieval-f009`; 8/18 new-wrong on `counterfactual-f013`.

ALL is not the same object. FROZEN→ALL does not uniquely reproduce +10/−20
(released 31 = +5 match / +26 M4; MATCH destroyed 16; sens Δ −10, M4 Δ +20,
abstention Δ −10). The paper’s ALL claim stays “worse, not better”; we do not
re-interpret +10/−20.

## Q3. Why no second human annotator on M1a–M4?

Those codes are operational predicates on frozen extractor logs (gold entered
`found` and the decision failed; label hit; gold inside vs outside the window;
reported ≠ gold). A second human applying the same rule is not an independent
rating. The integrity check is scripted recompute plus parity/synthetic gates.

## Q4. Why not transport M1a to OSWorld / WebArena / CUAVerifierBench?

Licensed limitation: one frozen instrument. The paper does not claim 13/39
holds under another extractor. No public corpus met the frozen eligibility
contract without changing the observation protocol. Path UV human confirmation
did not meet the bar; those numbers stay out of the paper.

## Q5. Why was the n≥20 comparative cohort not opened?

Pre-specified gate: 16 of 28 candidates survived the frozen feasibility probe,
16<20, FAIL, branch closed. Not a headline. Not reopened by lowering the
threshold.

## Q6. Why not ship R-AGG?

It is a diagnostic intervention, not a replacement instrument. It is the only
repair that raises sensitivity (20→28), by releasing 26 abstentions as +8
correct / +18 wrong. No tested repair dominates.
