# Claim ledger (draft v0.5)

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
| T-attr | Failure-attribution papers localize which agent/step caused task failure; that is not this paper's object | L Zhang et al. ICML 2025 (Who&When) | Adjacent trajectory-analysis cluster | **BACKGROUND** |

---

## Supporting evidence

| ID | Wording | Evidence | Artifact | Allowed | Forbidden | Status |
|---|---|---|---|---|---|
| S1-1 | Score need not track world change (existence) | 24 valid pairs; Type A/B in appendix | `b7b4203` | Dissociation demonstration | Pooled invariance; prevalence; agent ranking | **SAFE** |
| S2-1 | Evaluation/selection can change the evidential basis of a comparison | \|A\|=9/8/1; selection not evaluated; Y=0 on 18/18 | `39cc662` | Eligibility / coverage | Evaluator changes the truth; rank 57 tasks | **SAFE** |
| B1+C1 | Completion ≠ determining observation; unstructured last-text can be sparse | 40 DONE / 30 ABSTAIN; Flash Cov 0.1667 | `4c3d14b`; `42e49a6` | One observation-channel lesson | Agents failed; Flash incompetent; last-text canonical | **SAFE** |
| C2 | Form can pass while two-sided CC unevaluable | Form 0.9333; H3 N/E | `2b1b8d6` | Interface boundary | Form=validity; no MISS exists | **SAFE** |
| D1 | Two-sided CC unidentifiable under the locked rule in this HIT-only sample | 30 HIT / 0 MISS; I_CC=0; G2 10/10; W1 | `c663cf8` | Protocol/sample identifiability | Flash 100% reliable; competence causes unidentifiability; reopen D | **SAFE** |
| S3-join | On the 13 M1a rows, locked screenshot-rubric $S$ can be 100 while typed gold had been collected and discarded (7/10 joinable; 3 UNKNOWN; 9/9 in A have $Y=0$); gold string in earlier traj text on 8/13 | `experiment_m1a_location/` | Same-episode score/extractor disagreement; compact table in main §4 | Screenshot contained gold; 171-N; prevalence | **SAFE** (elevated supporting; not a second CORE) |
| A-FAIL | On 299 released FAIL (WebArena/VisualWebArena string·url, ELIGIBLE), the oracle collapses two different things into one number: 126 have no candidate in $I$ and 173 have a candidate then mismatch. ABSTAIN $\neq$ MISS. $V=0$ does not say which. | `experiment_path_a/RESULT.md`; cells sha256 `61441628…2fd516` | Heterogeneous FAIL; oracle does not separate evidential absence from mismatch; WA 52/145 vs 93 DETERMINING FAIL and VWA 74/154 vs 80 in appendix | 126/299 as unjustified or wrong FAIL; ARB-wide audit; 498 prevalence; pooling AssistantBench into 126/299; Dong-style “FAIL is incorrect” | **SAFE** (supporting public-$I$ check; not a second CORE) |
| A-AB | AssistantBench ELIGIBLE: 62/115 released FAIL have empty last `send_msg_to_user` (I-emptiness only) | same | Emptiness on that family, not pooled, no HIT/MISS | AssistantBench HIT/MISS; part of 126/299 | **SAFE** |
| A-HUM | Among released WA/VWA FAIL, ARB human Successful is 4/126 (empty \(I\)) vs 50/173 (mismatch); mostly single annotators | `experiment_path_a/out/human_crosstab.md`; csv sha256 `a96b6e07…b4ac8a` | Two FAIL kinds are not exchangeable vs human labels; empty \(I\) is not the hidden-success cell | Unjustified-FAIL rate; 50/173 as our discovery; Table 2 gold | **SAFE** (sensitivity; not CORE) |
| B-B1 | On released WebJudge o4-mini, after `Score≥3` then `[:50]`, cap-discard fires on 10/1790 episodes (all Operator; 536 frames). Instrument-internal; `Score` is not gold. | `experiment_path_b/RESULT.md`; cells sha256 `87b8a5e1…d25431` | Existence of collect-then-cap on this product; rarity + Operator-specificity | M1a transport; discarded frames are decisive; E2; benches invalid; put in PDF before B2 | **SAFE** (lab only until B2; not CORE; not in `main.tex` yet) |
| UV-U1 | On CUAVerifierBench OM2W (106), `n_screenshots > 5` on 93/106 (median 19). Necessary condition for UV top-K to drop a frame; not the discard set. Internal 52/154, median 0 — do not pool. | `experiment_path_uv/RESULT.md`; cells sha256 `db4e45d0…841a14` | Opportunity for per-criterion truncate on a public screenshot corpus | Discard rate; M1a transport; E2; Rosset κ audited; put in PDF before R+U2 | **SAFE** (lab only until R; not CORE; not in `main.tex` yet) |

Secondary empirical bundle (not a second primary contribution): B1+C1+C2+D1 = constructive measurement boundaries. Path A is a supporting public-oracle check, not a second CORE.

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
| P1/P2 as parallel contributions | **DELETE**; appendix only |
| Path A 126/299 “FAIL not justified from \(I\)” | **DELETE** |
| Path A eight SUCCESS ∩ ABSTAIN as a finding | **DELETE**; `webarena.723` QC_OPEN unexplained and closed; overlay only |
| “We audited AgentRewardBench” / 498 prevalence | **DELETE** |
| Title “Evaluation Measurement Gap” as primary | **SOFTEN** → dropped |
| Four parallel contributions in the Introduction | **DELETE** |
