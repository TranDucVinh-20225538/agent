# Milestone 0 — is there a measurement hole in MyPCBench?

Screening pass over the released task set. No model runs, no VM. Artifacts:
`data/mypcbench/tasks.jsonl` (184 tasks, 1,191 rubric criteria) and
`data/mypcbench/variables.json` (213 named ground-truth values), both from the
public release. Scripts: `scripts/m0_scan.py`, `scripts/m0_shortlist.py`.

## What the grading instrument is

Every criterion is graded the same way. The `type` field is `llm_judge` for all
1,191 items, so the instrument carries no label of its own about what kind of
evidence a criterion tests. Weights sum to 1 per task; the headline metric
(`perfect`) requires every criterion in a task to pass.

## What makes a criterion true

Each criterion was auto-classified by what determines its truth value.

| class | criteria | share | weight share |
| --- | --- | --- | --- |
| value — criterion names the target value | 116 | 9.7% | 11.9% |
| record — criterion requires reading or computing over the persona's records | 252 | 21.2% | 23.7% |
| action — criterion is satisfied by an interface side effect | 306 | 25.7% | 24.3% |
| style — tone or quality judgement | 10 | 0.8% | 1.1% |
| unclear — needs a human read | 507 | 42.6% | 39.1% |

Attributable to personal records (value + record): **30.9% of criteria, 35.5%
of rubric weight**. The 42.6% unclear bucket is the calibration target for the
hand read; the attributable share is therefore a lower bound.

Two facts that bear directly on the object:

- **117 of 184 tasks contain at least one action-only criterion.** Because
  `perfect` requires all criteria to pass, those tasks can be zeroed by
  execution failure regardless of whether the agent used personal information.
- Mean attributable weight is far from uniform across the benchmark's own
  internal categories: retrieval 0.62, preference_inference 0.58, aggregation
  0.43, situated_action 0.38, contradiction 0.32, long_horizon 0.21. The
  headline number averages over these.

## Counterfactual cost

- **59 of 184 tasks** quote a value in the rubric text, so a counterfactual on
  the seed also requires editing the rubric.
- The remaining tasks state a procedure rather than an answer, so the rubric
  text survives a counterfactual unchanged. This is cheaper than assumed, but
  it moves the burden onto the judge, which then has to recompute the target
  from the trajectory. Judge behaviour becomes a confound and needs its own
  control.

## Existence proof, both directions

`preference_inference-f009` — "What's my favorite grocery store, and what do I
actually buy there?" Criterion 1 reads: *identifies Michael's favorite
Kwik-E-Mart grocery store as the top-by-order-count store from live order
history (/api/orders), naming whichever store has the plurality of orders.*
The gold function is written into the rubric (`argmax` of order count per
store, over a named endpoint), 0.93 of the weight is record-determined, and no
rubric text needs editing under a counterfactual.

`situated_action-f028` — "Book me an upcoming Scranton weekend, pick a
well-rated property." No criterion is determined by personal records. A
counterfactual on identity, history or preference should not move this task at
all. This is a control, not a failure case.

## Read

A measurement hole exists and is visible in the grading instrument before any
model is run: roughly a third of rubric weight is attributable to personal
records, roughly a quarter is interface execution, and the two are averaged
into one number that the paper's title interprets as personal intelligence.
Both the intervenable set and the control set are non-empty.

Not yet established: whether the auto-classification survives a hand read, and
whether a counterfactual on the determining records leaves the task well
defined in the live VM. Next step is the ten-task hand read in
`out/m0_shortlist.md`.
