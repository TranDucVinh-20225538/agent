# From Trajectories to Evidence (full paper, venue unset)

**Status:** draft v0.3 after major revision.  
**Not:** AAMAS 8-page stuffing. Venue unset. No new experiments.

**Central contribution (one):**

A frozen CUA evaluation instrument can discard recoverable typed evidence after collection; permissive repair need not restore the intended measurement; constructing an observation-grounded last-text protocol then exposes identifiability boundaries.

The statement “reliability evaluation is a measurement problem” is **background**, not novelty.

Working title:

> From Trajectories to Evidence: Auditing Observation Loss and Identifiability in Computer-Use Agent Evaluation

## What lives here

| File | Role |
|---|---|
| `REVISION_PLAN.md` | Claim-specific revision map |
| `EVIDENCE_MAP.md` | Study → artifact → commit → number; hierarchy |
| `CLAIM_LEDGER.md` | Licensed wording; one CONTRIBUTION |
| `QUANTITATIVE_CLAIM_AUDIT.md` | Every manuscript number |
| `POST_REVISION_REVIEW.md` | Three reviewers + kill tests |
| `RELATED_WORK_VERIFICATION.md` | Cite only verified records |
| `FIGURE_TABLE_INVENTORY.md` | Figures/tables |
| `draft/main.tex` | v0.3 manuscript |
| `draft/refs.bib` | Verified bibliography |
| `draft/main.pdf` | Compiled draft |

The AAMAS 2027 8-pager remains frozen at `paper/aamas2027_reliability_score/` (P1–P3 only). Do not merge this file into that PDF.

## Compile

```bash
cd paper/evaluation_measurement_gap/draft
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

Target 12–16 pages excluding padding. Do not add experiments to fill space.

## Hard writing locks

- Do not headline a pooled Study 1 invariance rate.
- Do not add Study 1 + Study 2 sample sizes.
- Study 3 C7 / \(\Delta\mathrm{STS}\) inversion: existence only, \(n_{\mathrm{eff}}=1\).
- P4-B/C/C2/D are **constructive boundaries**, not four failed metrics.
- P4-M is notation / claim-justification formalization, not a new score or theorem.
- External validation is an eligibility STOP under a frozen last-text contract, not a general indictment of CUA artifacts.
- Do not claim firstness on measurement, pipelines, or “scores can be wrong.”
