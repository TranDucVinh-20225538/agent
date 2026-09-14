# `out/stage4_counterfactual_analysis_final/` — canonical audit, snapshot `b7b4203`

This is a from-scratch, independent rebuild. It was generated entirely by the
scripts in this directory (`_extract.py` -> `_extract3.py`/`_extract3b.py` ->
`build_final.py` -> `build_figures.py`), reading only `results/`, `cf/`, and
`out/PHASE_B.md`. No number in this directory was copied from
`out/stage4_counterfactual_analysis/` (prior audit, left untouched, reference
only) or `out/stage4_phase_b_interim_analysis/` (superseded interim, ignored).

## Universe and validity

10 pre-registered tasks (4 Phase A / Stage-4-locked + 6 Phase B, seed
`20260826`, see `out/PHASE_B.md`) × 5 model lanes = **50 intended**
cells. Qwen3.5-9B and Qwen3.8-Flash were never scheduled on
`preference_inference-f018` or `counterfactual-f004` (4 cells / 8 legs).
The executed universe is **46 cells**, each with a base (`E^0`) and
counterfactual (`E^1=I(E^0)`) leg = 92 trajectory rows
(`trajectory_cells.csv`). Never-scheduled cells are omitted from that CSV;
they are not coded as execution failures.

- **DONE** iff the last row of `traj.jsonl` has `action == "DONE"`. Nothing
  else (`result.txt`, writer `track` fields, presence of a `scores.json`)
  is treated as a substitute. 57/92 legs are DONE; 35/92 are execution
  failures, itemized in `failure_audit.csv` by `failure_type`
  (`EMPTY_XML`, `AGENT_FAIL`, `SCREENSHOT_DECODE_CRASH`, `STEP_LIMIT_NO_DONE`)
  — never coded as "does not track."
- **Gold** for every task is read only from the pre-registered
  `*.guest.json` probes (`probe_before`/`probe_after`/`extra_probes_*`),
  cross-referenced against `cf/phase_b_interventions.json` (Phase B) or
  `cf/stage4_locked.json` (Phase A). Writer `track` fields are never used
  as gold.
- **Final-answer text**: Claude runs carry `messages.json` (last assistant
  `text` block); GPT and Qwen runs carry no `messages.json` — final-answer
  text is read from the last `traj.jsonl` row's `response` field instead.
  This is a real schema difference in this repo, not a workaround.
- A **valid pair** requires both legs DONE. 24/46 cells are valid pairs.
  Every valid pair was classified by hand, directly against gold and
  final-answer text (see `tracking_evidence.md` for the full per-pair
  evidence trail); no classification is inherited from the prior audit or
  from the interim Phase B report.

## Tiers (never pooled into one headline number)

- **Primary**: Claude, GPT, Qwen3.5-35B-A3B.
- **Size ablation**: Qwen3.5-9B (same architecture family/training recipe as
  the primary Qwen entry, smaller).
- **Exploratory**: Qwen3.8-Flash (different family; reported for completeness,
  not folded into the primary claim).

`statistical_summary.json` keeps a `primary_pooled_DO_NOT_HEADLINE` field
purely for reference; it must not be quoted as a single "the models are X%
invariant" number — the audit brief this was built against explicitly
disallows pooling Claude+GPT+Qwen3.5-35B-A3B into one rate, and the
per-model Clopper-Pearson CIs (n<=9 each) are too wide to license it anyway.

## Classification (per valid pair)

- **Type A**: tracked (both legs correctly reflect `D`) and score-invariant.
- **score-sensitive**: tracked and the score moves with gold.
- **Type B**: incomplete/incorrect tracking on at least one leg, while the
  score stays high or unchanged.

Per-model counts, invariance rate (`Type A / (Type A + score-sensitive)`),
and an exact Clopper-Pearson 95% CI (computed from scratch, no `scipy`, via
the regularized incomplete beta function) are in `statistical_summary.json`
and `table_primary.md`/`.tex`, `table_ablation.md`, `table_exploratory.md`.

## Files in this directory

- `_extract.py`, `_extract2.py`, `_extract3.py`, `_extract3b.py` — mechanical
  extraction pipeline (raw cells -> semantic dumps); `_raw_cells.json`,
  `_mechanical.csv`, `_semantic_dump.txt`, `_gpt_fix_dump.txt`,
  `_valid_pairs_dump.txt` are their intermediate outputs, kept for
  traceability.
- `build_final.py` — the single script that produces every required table
  and CSV from `_raw_cells.json` plus the hand-derived `CLASS` dict
  (24 valid-pair classifications, each with a one-line gold statement and a
  one-line evidence-grounded mechanism, both traceable to
  `tracking_evidence.md`).
- `build_figures.py` — produces the four figures below from
  `paired_results.csv` / `statistical_summary.json` only (no new numbers).
- `trajectory_cells.csv` — 92 rows, one per (model, task, condition).
- `paired_results.csv` — 24 rows, one per valid pair, with classification,
  gold statement, and mechanism.
- `failure_audit.csv` — 35 rows, one per non-DONE leg, with failure type and
  exclusion reason.
- `rubric_item_audit.csv` / `rubric_mechanism.md` — per-criterion
  `per_rubric_max` arrays for 7 cells whose score behavior is not explained
  by the tracking classification alone, plus a prose reading of each.
- `tracking_evidence.md` — full per-task, per-model evidence trail for all
  24 valid pairs.
- `statistical_summary.json`, `table_primary.md/.tex`, `table_ablation.md`,
  `table_exploratory.md` — the numeric results.
- `paper_results.md` — prose results summary, source material for the paper.
- `score_pairs_primary.png`, `score_pairs_ablation.png`,
  `invariance_by_tier.png`, `gold_state_change.png` — figures (matplotlib
  3.10.9 was available on this machine; no `FIGURES_SKIPPED.txt` needed).

## Discrepancies vs. prior/interim analyses (documented, not silently changed)

- The ablation tier grows from 2 valid pairs (prior `out/stage4_counterfactual_analysis/`,
  Stage-4-only) to 3 here, because Phase B adds `retrieval-f016` for
  Qwen3.5-9B. This is an addition, not a revision of the Stage-4-only cells.
- `out/stage4_phase_b_interim_analysis/` is explicitly superseded and was not
  read for any number used here; its `interim_*` files predate the final
  Phase B run set used in this audit.
- Every PART-F pre-flagged mechanism (Claude `retrieval-f030`'s base-leg
  wrong-tax-year read; Claude `preference_inference-f018`'s partial joint-D
  tracking; GPT `counterfactual-f004`'s genuine Type B given a now-fixed SQL
  patch) was independently re-derived here from raw trajectory/guest files,
  not assumed from the task brief's placeholder text.

## Known limitation carried over from the frozen protocol

`hard_app-f033` and `situated_action-f028` remain outside this universe
(per `PHASE_A_memo.md`'s "pilot cell" designation, see prior-round audit
notes) and are not claimed here.
