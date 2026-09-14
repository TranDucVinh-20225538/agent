# P4 paper-level contribution audit

**Status: P4 theory CLOSED. Phase 1 NOT opened. This is an audit, not a new
experiment and not a paper draft.**  
**Question:** If the next step is a paper, do the five contribution tests
pass — and as *one* paper or as a programme with a split?

P4 is closed as a research layer:

```
P4-B   Observation gap                         CLOSED (positive-but-incomplete)
P4-C   Practical metric v1                     FAIL / CLOSED
P4-C2  Declared-claim metric v2                FAIL / CLOSED
P4-D   Natural two-sided CC                    FAIL / W1 / CLOSED
P4-M   Claim-justification framework           THEORY CLOSED
```

P4-M does not rescue C/C2/D. It names the measurement problem at another
abstraction: reliability measurement is a **justification problem
constrained by observation**, not a ground-truth outcome.

There is already an AAMAS 2027 GAAI draft in flight
(`paper/aamas2027_reliability_score/`): P1–P3 as three studies on one
frozen MyPCBench instrument. Abstract deadline 1 Oct 2026; paper 8 Oct.
That draft’s object is “what a reliability *score* actually measures.”
P4’s object is “what happens when one *constructs* an
observation-grounded metric, and what claims remain justifiable.”
Those are the same programme. They are **not** the same 8-page paper.

---

## Central contribution (one sentence)

Computer-use-agent “reliability scores” are constructed measurements
along

\[
\text{trajectory}\to\text{observation}\to\text{evidence}\to\text{decision}\to\text{score},
\]

and the scientifically honest object is not a scalar \(R(\tau)\) but
the set of reliability claims justified by what was actually
observable — with a typed, non-leaking correspondence lemma and an
explicit bound that natural-language denotation is out of scope.

If a reviewer cannot see that sentence as the spine of P1→P4-M, they
will see a pile of negative experiments. The audit below asks whether
the record supports that spine.

---

## 1. Novelty — **PASS at programme scope; do not claim “first to notice scores can be blind.”**

**Single contribution?** Yes, if scoped as a *measurement-audit
programme for CUA reliability*, not as a new leaderboard metric.

Closest neighbors (already in the P1 prior-art audit): Turk
(counterfactual clinical scores), Dong et al. (evaluator false
negatives), OSWorld §7 and WeaveBench (outcome-only overestimates),
AppWorld collateral-damage checks. None of them: (i) paired
determining-set intervention on a third-party CUA score, (ii)
functional/selection audit of that score, (iii) layer-wise evidence
loss and non-monotonic repair, (iv) *constructive* observation-grounded
instrument with sequential FAILs (execution≠evidence; Form≠validity;
natural two-sided CC unidentifiable under competence), (v) a
claim-justification object \(\mathcal{M}(\tau,\mathcal{I})\) with
typed soundness and NL denotation out of scope.

**Risk.** Kane-style argument-based validity and psychometric
“don’t infer beyond evidence” are old. P4-M’s novelty is the CUA
pipeline + typed-candidate non-leakage bound + empirical FAILs that
*force* that object, not the slogan. Related work for a P4 paper
must cite measurement-validity argument (Kane/Messick) and then
differentiate: trajectory/interface, independent \(L\), kind-only
\(E\), finding C.

**Verdict.** Programme novelty holds if claims stay in that scope.
One-paper novelty that includes both the MyPCBench three-study audit
*and* P4-M theory will look unfocused under an 8-page GAAI cap.

---

## 2. Evidence — **PASS per claim if papers are split; FAIL if P4-M is sold as empirically proven.**

| Claim | Status | Evidence |
|---|---|---|
| Score can dissociate from tracking / world | P1 | Empirical; AAMAS draft Study 1; do not restated as “first ever” |
| Score as selection/triage can be coverage-limited / unevaluable | P2 | Empirical; Study 2; valid-pair degeneracy |
| Trajectory→evidence transformation loses information; repairs not a universal fix | P3 | Empirical; Study 3; 39/59 miss; non-monotonic repairs; C7 \(n_{\mathrm{eff}}=1\) existence only |
| Execution ≠ determining observation | P4-B | Empirical; positive-but-incomplete; instrument v1 |
| Unstructured last-text metric (v1) fails as usable correspondence instrument | P4-C | Empirical FAIL (falsification of *that* metric) |
| Declared `CLAIM:` DFC: Form can pass; C2-intended MISS quota unevaluable | P4-C2 | Empirical FAIL H3; Form 0.9333; ordinary MISS existed |
| Controlled natural competitors without factory: 30/30 HIT, \(I_{CC}=0\), W1 | P4-D | Empirical FAIL; plus competence held |
| \(\mathcal{M}\neq f(\Omega)\); HIT soundness under A1–A4; NL denotation out of scope | P4-M | **Theory only.** Non-triviality checkpoint; typed-soundness lemma. No new \(\tau\) |

Every *empirical* FAIL above has a locked protocol and hashes. P4-M
must not borrow P4-D’s 30/30 as “proof of the lemma.” It is an
*instance* of unidentifiable two-sided CC, which the theory then
*interprets*.

---

## 3. Negative results — **PASS if named as failure modes; FAIL if listed as retries.**

| Result | Finding (not “we failed”) |
|---|---|
| P4-C | A usable correspondence instrument is not recovered from unstructured last-text without a declared channel (Form/coverage confusion) |
| P4-C2 | Declaring the channel can fix Form and still not identify two-sided CC; a MISS *quota* is a factory, not a correspondence test |
| P4-D | Competence-preserving natural challenge need not produce MISS; \(I_{CC}=0\) is observability, not “Flash is too good” |
| P4-M C | Formal correspondence guarantee lives on typed candidates, not English denotation |

These are four distinct modes of the same construction problem. They
only become “a bunch of failed attempts” if the paper’s question remains
“find a score that passes.” The paper’s question must remain the boxed
\(\mathcal{M}\).

---

## 4. Related work — **PARTIAL. The full pipeline audit is not in the CUA benchmark literature; the *justification* slogan is in measurement theory.**

CUA eval landscape (OSWorld, WebArena, τ-bench, MyPCBench, …) grades
**one** execution against world/DB/rubric. It does not treat the
*score itself* as the object under test, does not pair determining-set
interventions, and does not sequential-construct an observation-grounded
metric until two-sided CC fails under competence.

What *is* nearby and must be written carefully:

- Evaluator audits (Dong; Online-Mind2Web WebJudge vs self-report)
- Outcome-only overestimation (WeaveBench)
- Counterfactual score-blindness in another domain (Turk)
- Argument-based validity (Kane); construct validity (Messick);
  “absence of evidence ≠ evidence of absence” as a proverb

P4-M without Kane/Messick will look naive. P4-M *as* Kane without
typed \(E\), independent \(L\), and P4-D W1 will look like a rename
of 2006 educational measurement. The combination is the claim.

No search in this audit re-ran the 2026 prior-art sweep. Before a P4
manuscript, one focused related-work pass on **argument-based validity
× agent evaluation** is warranted. That is library work, not Phase 1.

---

## 5. AAMAS / GAAI fit — **PASS for the P1–P3 draft already aimed at GAAI; P4 is a second paper, not a stuffing.**

GAAI cares about how agents are evaluated. “The score is a pipeline;
justified claims are observation-bounded” is on-topic.

**Do not** merge P4-B/C/C2/D/M into the 8-page AAMAS 2027 PDF now:

- Claims and numbers there are already locked to MyPCBench Studies 1–3.
- Page budget is tight (~5 pages compiled; 8 max).
- P4-M is theory-plus-construction-FAILs; it needs space to *not* look
  like leftover experiments.
- Dual-object papers (“audit this score” + “here is a new formal
  framework”) are a classic GAAI reject pattern: unclear contribution.

**Fit of a later P4 paper (AAMAS/JAIR/workshop):** high if titled as
measurement construction + bounded justification, with C/C2/D as
findings and P4-M as the endpoint — not as “Metric v3.”

---

## Five-question scorecard

| # | Question | Verdict |
|---|---|---|
| 1 | One central contribution? | **Yes at programme level.** Not as a single 8-page merge. |
| 2 | Evidence behind each claim? | **Yes if P4-M stays theoretical.** No if P4-M is “validated.” |
| 3 | FAILs as findings? | **Yes**, under the \(\mathcal{M}\) question; no under “find a passing metric.” |
| 4 | Full pipeline already done? | **Not in CUA benchmarks.** Partial overlap with evaluator audits + psychometric validity. Must cite both. |
| 5 | GAAI-clear? | **Yes for P1–P3 AAMAS draft.** P4 should be a **separate** manuscript. |

**Do not research further because a phase remains.** The remaining
work is narrative and related-work hygiene, not another corpus.

---

## Recommendation

1. **Keep AAMAS 2027 as P1–P3 only.** Do not insert P4-M or P4-D W1
   into that PDF before 8 Oct unless a *tiny* forward pointer (“a
   constructive follow-on is out of scope here”) is wanted. Default:
   no pointer that implies a submitted companion.
2. **Treat P4 as Paper 4 / Paper 2 of the measurement series:**
   constructive boundary (B, C, C2, D) + P4-M endpoint. Working
   claim: *when observation-grounded CUA metrics are built rather
   than audited, Form, competence, and two-sided correspondence come
   apart; justified claims are typed, recoverable, non-circular
   correspondence, not NL denotation.*
3. **Empirical implementation of P4-M stays optional future work.**
   Typed soundness does not authorize Phase 1.
4. Hard writing problem, not a lab problem: one spine sentence,
   four named failure modes, one bounded lemma, no metric hunt.

P4 as a digging programme stops here.
