# FINAL STRUCTURAL REVISION REPORT

Manuscript: `draft/main.tex` v0.4  
Prior commit: `9b1b4ab`  
Hostile review: `FINAL_HOSTILE_REVIEW.md` (verdict B → V4+V5)  
External audit: `8680588` STOP-NO-CORPUS (unchanged)

This pass restructured the paper only. No experiments. No frozen-artifact edits.

---

## STATUS

Structural revision executed as specified: P3 is the empirical core; P1/P2 compressed to one supporting subsection plus appendix; P4 is one constructive sequence with B+C merged; P4-M is one paragraph; external STOP is in Limitations.

## PAGE COUNT

14 pages total (letter, 11pt, 1-inch margins).

- Body through conclusion: ~9 pages (pp. 1–9; references begin on p. 9)
- References: ~2.5 pages (pp. 9–11)
- Appendix A–C: 3 pages (pp. 12–14)

Under the 10–12-before-refs target on the short side. Not padded. Novelty-to-evidence ratio is the objective.

## CORE CONTRIBUTION

Exactly one:

In the frozen MyPCBench extractor `3242c30`, determining gold entered `found` and was discarded (M1a: 13/39 of 59 R1-positive misses). A pre-specified permissive aggregation repair released +8 correct and +18 wrong matches; ALL was worse than frozen (10 vs 20).

## P1/P2 TREATMENT

COMPRESS (mandatory V4).

Main §3.1 “Supporting evidence: score and eligibility dissociation” (~0.5 page).

Retained in main: 24 valid pairs; existence of score/tracking dissociation; \|A\|=9/8/1; Y=0 on 18/18; selection not evaluated.

Moved to Appendix A/B: Type A/B table, CIs, scatter, 4-task bootstrap, `retrieval-f009`, excluded-cell S≥90.

## P3 TREATMENT

CORE. Main §4, including cause table and compact repair table.

Retained: 59 denominator; 39 misses; 13 M1a; 7/13 majority; independent gold; frozen extractor; +8/+18; ALL 10 vs 20; instrument-specific reading.

Moved to Appendix C: C7 \(n_{\mathrm{eff}}=1\); G2 9/30; comparative 16/28 gate; full six-configuration repair table.

## P4 TREATMENT

One constructive section (§5), subordinate to P3.

- §5.1 merges B+C: 40/40 DONE, 30 ABSTAIN, Flash Cov 0.1667. One lesson.
- §5.2 C2: Form 0.9333; H3 NOT_EVALUABLE.
- §5.3 D: 30 HIT / 0 MISS; \(I_{CC}=0\); G2 10/10; wording is sample/protocol: “this sample did not contain enough negative observations to identify the two-sided estimand.”

Not four failed metrics. Not a Flash reliability study.

## P4-M TREATMENT

Standalone theory section deleted.

One bookkeeping paragraph in §3: \(\mathcal{M}(\tau,\mathcal{I})\); Observable_τ ≠ Observable_I; ¬Justifiable ≠ False; typed correspondence as specification implication, not a proof.

## EXTERNAL STOP TREATMENT

Standalone §11 deleted.

Limitations: 3 sentences. Wording matches the locked STOP: no corpus satisfied the frozen eligibility contract; no transport of M1a. Not called validation or replication.

## MAIN FIGURES

1. Pipeline \(\tau\to I\to P\to E\to Y\to S\) with P3/P4 marks.

P1 scatter moved to appendix. P4 sequence TikZ removed (table + prose). Misnamed `gold_state_change.png` (Type A/B chart including non-primary lanes) omitted.

## MAIN TABLES

1. Evidence map (core / secondary / supporting)
2. P3 miss causes
3. Compact FROZEN / R-AGG / ALL
4. P4 three boundaries
5. Eight-slot reporting checklist (one boxed table; no second “how we filled the slots” list)

## APPENDIX MATERIAL

- A: Study 1 table, CIs, scatter
- B: Study 2 coverage table, exploratory 4-task reversal
- C: full repair table, C7, G2, 16/28 gate

## NOVELTY RISK

Unchanged from the hostile review: this remains a **single-instrument** audit beside Dong’s multi-benchmark verdict study. Residual (post-collection discard + signed repair) is real; scale is not. v0.4 does not inflate novelty.

## REMAINING STRONGEST OBJECTION

“This is still a MyPCBench parser audit, and Dong already showed evaluators err.”

The paper now answers with location (post-`found`, pre-Y) and signed repair, not with more studies. That is the honest residual. Transport is unavailable under `8680588`.

## AAMAS FIT

MODERATE. Agent-evaluation / methodology. No new metric (acceptable for this contribution). Constructed P4 is labeled as such. Lack of public replication is a limitation, not a hidden result.

## FINAL VERDICT

**READY**

No unsupported claim discovered that would require a new experiment. Remaining risk is significance-vs-Dong, which frozen evidence cannot enlarge.

---

Reviewer-attack posture after revision (not a claim that the attacks are false):

| Attack | How v0.4 handles it |
|---|---|
| R1 Dong | Residual quote in §2.4; M1a location not visible to verdict audit |
| R2 parser bug | Isolated as post-collection discard; 7/13 majority; not shipped as a fix |
| R3 debugging | Signed +8/−18; ALL worse; not a method paper |
| R4 last-text strawman | Declared severe channel, not canonical; ABSTAIN rather than fallback |
| R5 P4-D zero variance | Sample/protocol identifiability; 0 MISS under a two-sided rule |
| R6 M(τ,I) trivial | One paragraph; bookkeeping |
| R7 small n | Existence + signed diagnostic; no prevalence |
| R8 single instrument | Stated in Limitations |
| R9 no external replication | STOP in Limitations; not a result |
| R10 too many pieces | P1/P2 compressed; P4-M folded; external folded |

Memory test (desired three): (1) gold entered `found` and was discarded; (2) +8 correct / +18 wrong; (3) 30 HIT / 0 MISS left two-sided correspondence unidentified. Three gaps / eight slots / 24 pairs / 4-task reversal are no longer the main-line story.
