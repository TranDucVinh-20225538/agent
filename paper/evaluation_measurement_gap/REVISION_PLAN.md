# Revision plan — major pass (claim-specific)

**Date:** 2026-09-13  
**Draft from:** v0.2 (`paper/evaluation_measurement_gap/draft/main.tex`)  
**Rule:** no new experiments; no frozen-artifact edits; abstract last.

---

## Title decision

| Candidate | Verdict |
|---|---|
| *The Evaluation Measurement Gap: What Evidence Justifies a Computer-Use Agent Reliability Claim?* | **Reject as primary title.** Overstates a background thesis (reliability evaluation is a measurement problem) as if it were the contribution. Overlaps Dong’s pipeline framing on sight. |
| *What a Frozen Observation Protocol Can Justify: Evidence Loss and Identifiability in Computer-Use Agent Evaluation* | Accurate but long; “what … can justify” still sounds like a general theory. |
| *From Trajectories to Evidence: Auditing Observation and Identifiability in Computer-Use Agent Evaluation* | **Selected.** Names the object (trajectory→evidence), the method (audit of a frozen instrument), and the secondary result (identifiability). Does not claim a new ontology of measurement. |

Working title:

> From Trajectories to Evidence: Auditing Observation Loss and Identifiability in Computer-Use Agent Evaluation

---

## A–G rows (claim-specific)

### C1 — Broad thesis as novelty

- **A. Current claim.** “Reliability evaluation of computer-use agents is itself a measurement problem” is the working object / intro spine.
- **B. Reviewer objection.** Kane/Messick/Bean/Jacobs already treat scores as interpretations requiring validity evidence. Dong already says a CUA score is a pipeline output.
- **C. Valid?** **Yes.**
- **D. Required revision.** Reposition as BACKGROUND. New central contribution: frozen instrument can discard recoverable typed evidence; permissive repair need not restore the intended measurement; two-sided correspondence can remain unidentifiable under competence.
- **E. Evidence.** Dong abstract (arXiv:2607.28367); Kane 1992/2013; Messick 1995; Bean et al. 2025 (NeurIPS D&B); Jacobs & Wallach FAccT 2021.
- **F. New experiment?** No.
- **G. Sections.** Title, abstract (later), §1, §2.4, §9, §13.

### C2 — “First” / pipeline-discovery claims

- **A.** Implicit first-ness around \(\tau\to I\to P\to E\to Y\to S\).
- **B.** Dong already: score as pipeline; trajectory observation as a stage; evaluator FNs; insufficient evidence.
- **C. Valid?** **Yes.**
- **D.** Explicitly: we do not invent validity theory; we do not claim first demonstration that scores are constructed. Residual: verdict audit of public FAIL traces vs. frozen transformation/instrument audit + repair experiment + constructive identifiability.
- **E.** Dong HTML/PDF (this pass). Residual distinction is **real but not unprecedented in spirit**; must not overclaim uniqueness of “instrument audit.”
- **F.** No.
- **G.** §1 ¶1–2, §2.3–2.4, discussion.

### C3 — Dong overlap (highest-stakes)

- **A.** Related work currently cites Dong as “150 FAIL trajectories; some FAIL verdicts are wrong.”
- **B.** Dong already establishes the background the paper currently headlines.
- **C. Valid?** **Yes.** After reading Dong, the residual is **sufficient for a narrower paper**, not for a “measurement-gap ontology” paper.
- **D.** Dedicated confrontation paragraph. Dong = retrospective verdict audit (wrong FAIL; broken tasks; 3.3% unclear from released evidence). This paper = freeze \(I/P/E\), isolate post-collection discard (M1a), experimentally test repairs (R-AGG +8/−18; ALL worse), construct last-text measurement and record observation/interface/identifiability boundaries.
- **E.** Dong §§1–4; P3 tables; P4-B/C/C2/D locks.
- **F.** No.
- **G.** §2.3, §2.4.

### C4 — Kane/Messick/Bean/Jacobs/Raji/Bowman

- **A.** Validity cited but “what we add” is notation \(\mathcal{M}(\tau,\mathcal{I})\).
- **B.** Notation is not novelty; Bean already gives construct-validity checklists for LLM benchmarks.
- **C. Valid?** **Yes.**
- **D.** “We do not invent validity theory.” Concrete addenda: CUA trajectory grain; frozen observation protocol; M1a; failed repair; ABSTAIN as missing correspondence; competence + zero negative variation → unidentifiable two-sided claim; 8-slot reporting checklist as methodological consequence, not a new standard.
- **E.** Verified records listed in `RELATED_WORK_VERIFICATION.md` (updated this pass).
- **F.** No.
- **G.** §2.2, §8, §10.

### C5 — Shao et al.

- **A.** One-line cite of protocol validity.
- **B.** Shao already: capability claims depend on protocol properties; 2,385 traces / 15 benchmarks; Mislead gap.
- **C. Valid?** **Yes.**
- **D.** Distinguish exposure→exploitation→misleading shortcuts (Shao) vs. observation→evidence→correspondence/measurement loss (this paper). Do not claim “scores justify claims” is new.
- **E.** arXiv:2607.22368 abstract (verified this pass).
- **F.** No.
- **G.** §2.1, §2.4.

### C6 — Study 1 framed as prevalence / invariance headline

- **A.** Table of Type A rates with CIs; 24 pairs.
- **B.** n small; CIs huge; pooling temptation.
- **C. Valid?** **Yes as warning.** Existence/dissociation is supported; prevalence is not.
- **D.** Lead with the scientific question; 24 pairs as existence sample; Type A/B; wide uncertainty; no pooled rate; compress methods.
- **E.** `EVIDENCE_MAP.md` P1; snapshot `b7b4203`.
- **F.** No. Do not invent pairs.
- **G.** §4.

### C7 — Study 2 “evaluator changes the claim”

- **A.** Already locked heading is better; leftover “larger contribution” rhetoric in discussion.
- **B.** Too strong; coverage is not ranking.
- **C. Valid?** **Yes.**
- **D.** Keep locked heading. Role: comparison can become conditional on eligibility. Compress. Retain |A|=9/8/1, Y=0 on 18/18, selection not evaluated.
- **E.** tag `paper2-frozen` / `39cc662`.
- **F.** No.
- **G.** §5, discussion.

### C8 — Study 3 not the empirical core

- **A.** M1a and repairs are present but sit after S1/S2 as equal-weight studies.
- **B.** Reviewer: if anything is new, it is post-collection discard + repair non-dominance inside a frozen extractor.
- **C. Valid?** **Yes.**
- **D.** Foreground 39/59, 13/39 M1a, 7/13 majority discard; distinguish from agent failure / judge disagreement / screenshot omission / generic missing data. Repair: R-AGG +8/−18; ALL worse. Claim: permissive repair is **not guaranteed** to restore intended measurement *in this instrument*.
- **E.** P3 locked tables; extractor `3242c30`.
- **F.** No.
- **G.** §6 (expand relative to §4–5).

### C9 — P4 as four failed metrics

- **A.** Subsections still say Metric v1 FAIL / v2 FAIL.
- **B.** Sounds like a leaderboard of broken scores.
- **C. Valid?** **Yes.**
- **D.** One table: constructed / failed / boundary. Sequence: construction → observation → interface → identifiability. No “Flash 100% reliable”; no “metric broken”; no MISS factory.
- **E.** P4-B `4c3d14b`; C `42e49a6`; C2 `2b1b8d6`; D `c663cf8`.
- **F.** No.
- **G.** §7.

### C10 — P4-M as theory / validity theorem

- **A.** Own section “Claim justification”; \(\mathcal{M}\) as framework; soundness as named result.
- **B.** Definitional; not empirically implemented; not a reliability theorem.
- **C. Valid?** **Yes.** Mandatory demotion.
- **D.** Formalization/notation for claims justified under a declared protocol. \(\neg\mathrm{Justifiable}\neq\mathrm{False}\) as interpretive principle (justification vs truth), not a novel theorem. Out of scope explicit.
- **E.** `P4_M_CLAIM_JUSTIFICATION_DESIGN.md` THEORY CLOSED; empirical NOT STARTED.
- **F.** No.
- **G.** §8.

### C11 — Typed correspondence soundness overclaimed

- **A.** Own section.
- **B.** Specification-level implication under HIT + no-leakage.
- **C. Valid?** **Yes.**
- **D.** Compress to short proposition/sketch inside §8. Rename “narrow no-leakage property.”
- **E.** `P4_M_VALIDITY_THEOREM_DRAFT.md` ACCEPT as no-leakage lemma.
- **F.** No.
- **G.** §8.3.

### C12 — Three gaps as ontology

- **A.** “One contribution, three gaps.”
- **B.** Renamed measurement error; Dong already has construction/observation/scoring/reporting stages.
- **C. Valid?** **Partially.** Keep as organizing device; disclaim “three laws.”
- **D.** Analytic categories. Explain “evaluation measurement gap” = local name for score↔outcome / evidence↔observation / evidence↔justified claim in this frozen setting.
- **E.** Table of studies.
- **F.** No.
- **G.** §3, §9.

### C13 — Reporting framework as new theory

- **A.** Eight slots presented as the methodological punchline.
- **B.** Bean already has checklists; Kane already has interpretation/use arguments.
- **C. Valid?** **Yes as overclaim.**
- **D.** Practical reporting checklist derived from the studies. Actionable questions. Not a validated standard.
- **E.** Studies 3–4 + P4-D identifiability.
- **F.** No.
- **G.** §10.

### C14 — External STOP wording too broad

- **A.** “existing CUA benchmark artifacts are not necessarily measurement-ready”
- **B.** Overgeneralizes an eligibility FAIL under one frozen \(I\).
- **C. Valid?** **Yes.**
- **D.** “We did not identify a public corpus satisfying this specific frozen last-text typed observation contract.” Light re-audit (this pass): `markov-ai/computer-use` (OSWorld successes + screenshots/a11y; score-filtered); AgentTrove (mixed terminus-2, not typed \(k\)+\(L\)). Using them would require a new adapter/parser or a change of \(I\). **KEEP STOP.**
- **E.** `de66e0a`; `P4_EXTERNAL_VALIDATION_RESULT.md`.
- **F.** No execution.
- **G.** §11.

### C15 — Bibliography errors

- **A.** OSWorld Daoguang Shin; VisualWebArena Vishakh Duvvur; \(\tau\)-bench as `@misc` 2024.
- **B.** Factually wrong / venue inflation.
- **C. Valid?** **Yes.**
- **D.** Dongchan Shin (NeurIPS 2024 D&B). Vikram Duvvur; ACL official “Ming Lim”, “Russ Salakhutdinov”. \(\tau\)-bench ICLR 2025. Label preprint vs conference vs workshop. Add verified: Bean, Jacobs & Wallach, Raji, Bowman & Dahl, Xue/WebJudge (COLM 2025), Rosset (arXiv:2604.06240).
- **E.** NeurIPS proceedings; ACL Anthology; ICLR 2025 proceedings; arXiv abs pages this pass.
- **F.** No.
- **G.** `refs.bib`; all cites.

### C16 — Abstract overstates

- **A.** Opens with the broad measurement thesis.
- **B.** Same as C1.
- **C. Valid?** **Yes.**
- **D.** Write last. No prevalence, no first, no replacement metric. Evidence loss / failed repair / identifiability; frozen CUA setting.
- **E.** After body freeze.
- **F.** No.
- **G.** abstract.

---

## Rejected reviewer suggestions (explicit)

Add new metric; more MyPCBench legs for n; MISS factory; amp distractors; relax parser; NLP denotation; screenshot/DOM fallback; pool natural/synthetic or P1–P4 populations; claim public benchmarks invalid; Flash unreliable from P4; P4-M validated by P4-D; P4-D as 100% reliability; P4-E; reader study; venue selection.

---

## Dong residual — is it strong enough?

**Yes for a narrower empirical paper; no for a measurement-theory paper.**

Dong already owns: score-as-pipeline, trajectory observation as a reliability stage, evaluator false negatives, insufficient/unclear released evidence, public multi-benchmark verdict audit.

This paper owns, if framed tightly: (i) post-collection discard inside a **frozen** extractor (M1a); (ii) signed repair experiment showing permissiveness can release more wrong than right matches; (iii) constructive last-text measurement exposing completion-without-evidence, Form-without-two-sided-identifiability, and competence-without-negative-variation.

If a reviewer still says “Dong already did this,” the honest reply is: Dong audited **verdicts**; we audited a **frozen transformation** and then **tried to construct** an observation-grounded instrument. That is the paper. It is not a new theory of measurement.

---

## Hierarchy after revision

1. **PRIMARY CONTRIBUTION:** P3 M1a + repair non-dominance.  
2. **SECONDARY:** P4 constructive boundaries / identifiability.  
3. **SUPPORTING:** P1/P2 existence of outcome/eligibility gaps.  
4. **FORMALIZATION:** P4-M notation (not a theory contribution).  
5. **EXTERNAL:** eligibility STOP.

---

## New experiment?

**No**, unless a later authorization names a new question. Existing evidence cannot estimate prevalence of M1a across public CUA benchmarks; that would be a different paper (and would likely require changing \(I\)).
