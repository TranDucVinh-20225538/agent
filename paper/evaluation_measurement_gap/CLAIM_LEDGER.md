# Claim ledger (draft v0.3)

If a sentence is not licensed here, it does not go in `draft/main.tex`.
Statuses: **BACKGROUND** / **SAFE** (supporting evidence) / **CONTRIBUTION** / **SOFTEN** / **DELETE**.

**Exactly one primary CONTRIBUTION.**

Support: **E** = empirical locked artifact; **T** = accepted formalization; **S** = stop/audit; **L** = verified literature.

---

## Primary contribution (exactly one)

| ID | Exact manuscript wording (sense) | Evidence | Artifact/commit | Literature overlap | Strength | Allowed | Forbidden | Status |
|---|---|---|---|---|---|---|---|---|
| C-PRIM | A frozen CUA evaluation instrument can discard recoverable typed evidence after collection; permissive repair need not restore the intended measurement (R-AGG +8/−18; ALL worse); this is an instrument-level result, not a theorem that parsers cannot be repaired | E: 39/59; M1a 13/39; 7/13 majority; repair table | P3 extractor `3242c30`; AAMAS tab:causes/repairs | Dong/Xue/Rosset document missing evidence and last-frame loss, not post-collection discard + signed repair inside a frozen text extractor | Existence + signed diagnostic, this instrument | Isolate M1a; report repair non-dominance | First such phenomenon; agent FN; ship R-AGG; universal parser theorem | **CONTRIBUTION** |

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
| S1-1 | Score need not track world change (existence) | 24 valid pairs; Type A/B; wide CIs | `b7b4203` | Dissociation demonstration | Pooled invariance; prevalence; agent ranking | **SAFE** |
| S2-1 | Evaluation/selection can change the evidential basis of a comparison | \|A\|=9/8/1; selection not evaluated; Y=0 on 18/18 | `39cc662` | Eligibility / coverage | Evaluator changes the truth; rank 57 tasks | **SAFE** |
| B1 | Completion ≠ determining observation | 40 DONE / 30 ABSTAIN | `4c3d14b` | Constructive observation boundary | Agents failed; metric broken | **SAFE** |
| C1 | Unstructured last-text coverage can be low | Flash Cov 0.1667 | `42e49a6` | Coverage boundary | Flash incompetent | **SAFE** |
| C2 | Form can pass while two-sided CC unevaluable | Form 0.9333; H3 N/E | `2b1b8d6` | Interface boundary | Form=validity; no MISS exists | **SAFE** |
| D1 | Two-sided CC unidentifiable under competence | 30 HIT / 0 MISS; I_CC=0; G2 10/10; W1 | `c663cf8` | Identifiability | Flash 100% reliable; agent unreliable; reopen D | **SAFE** |

Secondary empirical bundle (not a second “primary contribution”): B1+C1+C2+D1 = constructive measurement boundaries.

---

## Formalization (not a contribution)

| ID | Wording | Evidence | Allowed | Forbidden | Status |
|---|---|---|---|---|
| M1 | \(\mathcal{M}(\tau,\mathcal{I})\) is notation for claims justified under a declared protocol | T P4-M CLOSED | Formalization / bookkeeping | New theory; novel validity framework; replacement metric | **BACKGROUND** (formalization) |
| M2 | Observable_τ ≠ Observable_I | T + E (P3, P4-B) | Measurement loss ≠ no claim | No CLAIM line = agent made no claim | **SAFE** |
| M3 | HIT ⇒ typed parse and match under A1–A4 | T no-leakage lemma | Narrow specification implication | Reliability/validity theorem; P4-M proven | **SAFE** (demoted) |
| T2 | \(\neg\mathrm{Justifiable}(C\mid\tau,I)\neq\mathrm{False}(C)\) | Interpretive principle | Justification ≠ truth | Novel theorem | **BACKGROUND** |

---

## External

| ID | Wording | Evidence | Allowed | Forbidden | Status |
|---|---|---|---|---|
| X1 | We did not identify a public corpus satisfying this frozen last-text typed observation contract | S `de66e0a`; light re-audit 2026-09-13 | Eligibility STOP | “Benchmarks are generally not measurement-ready”; WebArena agents unreliable | **SAFE** |

---

## Organizing device (not ontology)

| ID | Wording | Status |
|---|---|---|
| U1–U3 | Outcome / observation / justification gaps as analytic categories | **BACKGROUND** (organizing). Do not call them three laws. |

---

## Methodological consequence (not theory)

| ID | Wording | Status |
|---|---|---|
| F8 | Eight-slot reporting checklist | **SAFE** as practical consequence. Forbidden: new metric, theorem, validated standard. |

---

## Deleted / do not revive

| ID | Status |
|---|---|
| Broad thesis as novelty (“reliability evaluation is a measurement problem” as contribution) | **DELETE** as novelty; keep as **BACKGROUND** |
| P4 as four failed metrics | **DELETE** |
| Gate 0 as contribution (S3-7) | **DELETE** |
| Pooled S1 invariance | **DELETE** |
| P4-M empirically validated by P4-D | **DELETE** |
| Title “Evaluation Measurement Gap” as primary | **SOFTEN** → dropped |
