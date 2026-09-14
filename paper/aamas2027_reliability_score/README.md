# What Does a Computer-Use Agent Reliability Score Actually Measure?

AAMAS 2027 main-track draft (area: **GAAI**).
One measurement audit, three complementary studies. No new experiments.

## Compile

```bash
pdflatex main && bibtex main && pdflatex main && pdflatex main
pdflatex supplement && bibtex supplement && pdflatex supplement && pdflatex supplement
```

`main.pdf` must be ≤ 8 pages of body (references may continue).
Current compile: **5 pages total** (body through related work + references).
That is legal and tight; it is not padded to 8. Room remains for protocol
examples, not for new numbers.
`supplement.pdf` is the optional 25 MB zip payload; reviewers need not read it.

This draft uses `\documentclass[sigconf,anonymous,review]{acmart}`.
If AAMAS 2027 posts a wrapper class (`acm/aamas`), swap it in without
changing layout parameters.

## Locked claims

See the conversation lock and `paper/paper3_observation_grounded/CLAIM_EVIDENCE_AUDIT.md`.
Do not pool Study 1 / 2 / 3 sample sizes. Do not promote C7 beyond existence
(`n_eff=1`). Do not treat repairs as a method. Cohort 16/28 is appendix only.

## Calendar (AoE)

| Item | Date |
|---|---|
| OpenReview author accounts | 17 Sep 2026 |
| Abstract (~100–300 words) + frozen author list | 1 Oct 2026 |
| Paper + supplement zip | 8 Oct 2026 |

Abstract text is the `main.tex` abstract. Authors cannot be added after 1 Oct.

## Dual-submission

Do not submit this manuscript while a substantially overlapping archival
workshop paper is under review. Non-archival workshops and arXiv preprints
are allowed; do not cite an earlier version of this work in the anonymized PDF.
