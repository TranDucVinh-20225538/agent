# Claim ledger (draft v0.4)

If a sentence is not licensed here, it does not go in `draft/main.tex`.
Statuses: **BACKGROUND** / **SAFE** (supporting evidence) / **CONTRIBUTION** / **SOFTEN** / **DELETE**.

**Exactly one primary CONTRIBUTION.**

Support: **E** = empirical locked artifact; **T** = accepted formalization; **S** = stop/audit; **L** = verified literature.

---

## Primary contribution (exactly one)

| ID | Exact manuscript wording (sense) | Evidence | Artifact/commit | Literature overlap | Strength | Allowed | Forbidden | Status |
|---|---|---|---|---|---|---|---|---|
| C-PRIM | In this frozen extractor, determining gold was present in the trajectory and had entered `found`, but fail-closed aggregation discarded it; a pre-specified permissive aggregation repair released +8 correct and +18 wrong matches; ALL was worse than frozen (10 vs 20). Instrument-specific; not a theorem that parsers cannot be repaired. | E: 39/59; M1a 13/39; 7/13 majority; repair table | P3 extractor `3242c30` | Dong/Xue/Rosset document missing evidence and last-frame loss, not post-collection discard + signed repair inside a frozen text extractor | Existence + signed diagnostic, this instrument | Isolate M1a; report repair non-dominance | First such phenomenon; agent FN; ship R-AGG; universal parser theorem; prevalence | **CONTRIBUTION** |

---

## Background

| ID | Wording | Evidence | Overlap | Status |
|---|---|---|---|---|
| T0 | CUA reliability scores are evaluation outputs, not direct observations | L Dong; Kane/Messick | Dong pipeline; Kane interpretation/use | **BACKGROUND** |
| T-val | We do not invent validity theory | L Kane 1992/2013, Messick 1995, Cronbach & Meehl 1955, Jacobs & Wallach 2021, Bean 2025, Raji 2021, Bowman & Dahl 2021 | Entire validity literature | **BACKGROUND** |
| T-dong | Dong: retrospective FAIL-verdict audit; score as pipeline | L arXiv:2607.28367 | Direct prior art | **BACKGROUND** |
| T-shao | Protocol validity: exposure → exploitation → misleading shortcuts | L arXiv:2607.22368 | Adjacent; different axis | **BACKGROUND** |

---

## Supporting evidence

| ID | Wording | Evidence | Artifact | Allowed | Forbidden | Status |
|---|---|---|---|---|---|
| S1-1 | Score need not track world change (existence) | 24 valid pairs; Type A/B in appendix | `b7b4203` | Dissociation demonstration | Pooled invariance; prevalence; agent ranking | **SAFE** |
| S2-1 | Evaluation/selection can change the evidential basis of a comparison | \|A\|=9/8/1; selection not evaluated; Y=0 on 18/18 | `39cc662` | Eligibility / coverage | Evaluator changes the truth; rank 57 tasks | **SAFE** |
| B1+C1 | Completion ≠ determining observation; unstructured last-text can be sparse | 40 DONE / 30 ABSTAIN; Flash Cov 0.1667 | `4c3d14b`; `42e49a6` | One observation-channel lesson | Agents failed; Flash incompetent; last-text canonical | **SAFE** |
| C2 | Form can pass while two-sided CC unevaluable | Form 0.9333; H3 N/E | `2b1b8d6` | Interface boundary | Form=validity; no MISS exists | **SAFE** |
| D1 | Two-sided CC unidentifiable under the locked rule in this HIT-only sample | 30 HIT / 0 MISS; I_CC=0; G2 10/10; W1 | `c663cf8` | Protocol/sample identifiability | Flash 100% reliable; competence causes unidentifiability; reopen D | **SAFE** |

Secondary empirical bundle (not a second primary contribution): B1+C1+C2+D1 = constructive measurement boundaries.

---

## Formalization (not a contribution)

| ID | Wording | Evidence | Allowed | Forbidden | Status |
|---|---|---|---|---|
| M1 | \(\mathcal{M}(\tau,\mathcal{I})\) is notation for claims justified under a declared protocol | T P4-M CLOSED | Formal bookkeeping, one paragraph | New theory; novel validity framework; replacement metric; standalone section | **BACKGROUND** (formalization) |
| M2 | Observable_τ ≠ Observable_I | T + E (P3, P4-B) | Measurement loss ≠ no claim | No CLAIM line = agent made no claim | **SAFE** |
| T2 | \(\neg\mathrm{Justifiable}(C\mid\tau,I)\neq\mathrm{False}(C)\) | Interpretive principle | Justification ≠ truth | Novel theorem | **BACKGROUND** |
| M3 | HIT ⇒ typed parse and match under no-leakage maps | Specification implication | One sentence | Reliability/validity theorem; proof subsection | **SAFE** (demoted) |

---

## External

| ID | Wording | Evidence | Allowed | Forbidden | Status |
|---|---|---|---|---|
| X1 | No public corpus satisfied the frozen eligibility contract without changing observation protocol or evaluator; we do not claim transport of M1a beyond the frozen MyPCBench instrument | S `de66e0a`; `8680588` STOP-NO-CORPUS | Limitations paragraph | Validation; replication; “benchmarks are generally not measurement-ready” | **SAFE** |

---

## Organizing device (not ontology)

| ID | Wording | Status |
|---|---|---|
| U1–U3 | Outcome / observation / justification gaps as analytic categories, stated once | **BACKGROUND** (organizing). Do not call them three laws. Do not redefine in Discussion. |

---

## Methodological consequence (not theory)

| ID | Wording | Status |
|---|---|---|
| F8 | Eight-slot reporting checklist (one table). “Practical reporting consequence, not a validated universal standard.” Forbidden: second enumeration of how this paper filled each slot; new metric; theorem. | **SAFE** |

---

## Deleted / do not revive

| ID | Status |
|---|---|
| Broad thesis as novelty (“reliability evaluation is a measurement problem” as contribution) | **DELETE** as novelty; keep as **BACKGROUND** |
| P4 as four failed metrics | **DELETE** |
| Gate 0 as contribution | **DELETE** |
| Pooled S1 invariance | **DELETE** |
| P4-M empirically validated by P4-D | **DELETE** |
| Standalone P4-M / typed-correspondence-soundness section | **DELETE** from main; one bookkeeping paragraph only |
| Standalone external-validation section | **DELETE** from main; fold into Limitations |
| P1/P2 as parallel contributions | **DELETE**; supporting subsection + appendix |
| Title “Evaluation Measurement Gap” as primary | **SOFTEN** → dropped |
| Four parallel contributions in the Introduction | **DELETE** |
