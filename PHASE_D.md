# Phase D — confirmatory sample, not slot-picking

Hypothesis (the thing we are allowed to test):

> Overall task success is insufficient to identify which personal evidence
> produced that success.

Not: every task will fail to track its records. A task that tracks its
determining set is a control, not a refutation.

## Stage 1 — Screening (no Claude)

```bash
python3 scripts/evidence_screen.py
```

Writes one row per task in `out/evidence_screening.csv`. Every exclusion has a
reason. Identifiability that needs a guest dump is `pending_dummy_probe`, not a
reason to drop the row or to prefer a different task.

Eligibility A–E (pre-registered):

| | |
| --- | --- |
| A | rubric channel-invariant |
| B | at least one app maps to a SQLite file the harness warms |
| C | `cua_required` is false on the pinned rubric |
| D | instruction/rubric/apps do not name LibreOffice/spreadsheet/chart |
| E | instruction does not pin a dollar gold |

## Stage 2 — Selection (fixed rule, no peeking at agent outcomes)

For each evidence type: sort eligible ids. If n≤3, take all. If n>3,
`random.Random(20260826).sample(ids, 3)`.

Do not replace a sampled task that later fails dummy-probe identifiability.
Record it as `rejected_not_identifiable` (see `preference_inference-f009`).

Pilot runs already on disk (retrieval-f001, hard_app-f033, f009, f028) are not
the selection rule. They stay in `results/evidence_coverage.csv` labelled as
pilot.

## Stage 3 — Probe all 10 eligible ($0)

Dummy/schema probe for **all 10 eligible** tasks (8 sample + 2 reserve).
See `PROMPT_STAGE3_PROBE.md` and `out/evidence_probe_results.md`.

The 2 reserve ids are not replacements. A failed probe is recorded in place.

Stage 3 result on the frozen 8:

- identifiable: `retrieval-f001`, `aggregation-f003`,
  `preference_inference-f018`, `counterfactual-f004`
- confounded (remain in sample): `retrieval-f029`, `retrieval-f030`,
  `aggregation-f018`, `preference_inference-f004`

Reserves `retrieval-f003` and `retrieval-f016` are identifiable and **not
promoted**.

## Stage 4 — Claude only on the 4 identifiable sample members

See `PROMPT_STAGE4.md` and `cf/stage4_locked.json`.

Do not run Claude on confounded sample members. Do not promote reserves.
Judge score is auxiliary. For `counterfactual-f004` the DV is
`contradiction_flag` in the answer, not the score.

`retrieval-f001` is a confirmatory re-run of the same intervention as the
pilot (seed selected it). That is replication, not cherry-picking.

Report every sampled id: Claude outcome, null, failure, or confounded.
