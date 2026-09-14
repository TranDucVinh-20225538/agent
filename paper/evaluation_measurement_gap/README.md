# From Trajectories to Evidence (full paper, venue unset)

**Status:** draft v0.5 + Path A **STOPPED** (licensed split 126 vs 173 only). P1/P2 appendix-only; M1a×S compact table in main. Not 126/299 as unjustified FAIL. Eight SUCCESS∩ABSTAIN not in the PDF.

**Central contribution (one):**

A frozen CUA evaluation instrument can discard recoverable typed evidence after collection; permissive repair need not restore the intended measurement.

Working title:

> From Trajectories to Evidence: Auditing Observation Loss and Identifiability in Computer-Use Agent Evaluation

## What lives here

| File | Role |
|---|---|
| `CLAIM_LEDGER.md` | Licensed wording; one CONTRIBUTION |
| `EVIDENCE_MAP.md` | Study → artifact → commit → number; hierarchy |
| `QUANTITATIVE_CLAIM_AUDIT.md` | Every manuscript number |
| `FIGURE_TABLE_INVENTORY.md` | Figures/tables |
| `FINAL_HOSTILE_REVIEW.md` | Submission-gate audit that required V4+V5 |
| `FINAL_STRUCTURAL_REVISION_REPORT.md` | This revision's gate |
| `draft/main.tex` | v0.4 manuscript |
| `draft/refs.bib` | Verified bibliography |
| `draft/main.pdf` | Compiled draft |
| `POST_REVISION_REVIEW.md` | v0.3 self-review (superseded) |
| `REVISION_PLAN.md` | v0.3 plan (executed) |

The AAMAS 2027 8-pager remains frozen at `paper/aamas2027_reliability_score/` (P1–P3 only). Do not merge this file into that PDF.

## Compile

```bash
cd paper/evaluation_measurement_gap/draft
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

v0.4 target is a sharp methods/evaluation paper. Do not add experiments to fill space.

## Hard writing locks

- Exactly one CORE contribution: P3 M1a + signed repair.
- P1/P2 live only in Appendix A–B.
- Path A (`experiment_path_a/`): **STOPPED.** Manuscript may use the licensed 126 vs 173 FAIL split only. Forbidden: unjustified-FAIL rate; eight SUCCESS ABSTAIN; 498 prevalence; further Path A rates.
- Do not headline a pooled Study 1 invariance rate.
- Do not add Study 1 + Study 2 sample sizes.
- Study 3 C7 / \(\Delta\mathrm{STS}\) inversion: appendix only, \(n_{\mathrm{eff}}=1\).
- P4-B/C are one observation-channel lesson; C2 and D stay distinct.
- P4-M is one bookkeeping paragraph, not a section.
- External STOPs (`de66e0a`, `8680588`) live in Limitations, not a result section.
- Do not claim firstness on measurement, pipelines, or “scores can be wrong.”
