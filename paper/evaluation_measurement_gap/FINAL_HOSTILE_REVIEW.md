# FINAL HOSTILE REVIEW — SUBMISSION-GATE AUDIT

Review-only. No manuscript edits. No experiments. No invented literature.  
Manuscript: `draft/main.tex` v0.3 (commit `9b1b4ab`). External experiment: `8680588` STOP-NO-CORPUS (not in the PDF).

---

FINAL HOSTILE REVIEW — TERMINAL
--------------------------------

VERDICT: **B. ONE MORE REVISION** (not submission-ready)

STRONGEST CONTRIBUTION: Frozen-extractor **post-collection discard (M1a)** plus a **signed repair** showing permissive aggregation released more wrong matches than correct ones, in one MyPCBench instrument.

STRONGEST REMAINING OBJECTION: This is still a **single-instrument parser/audit paper** sitting next to Dong’s 150-trace multi-benchmark verdict audit. The residual is real; the **scale and generality** are not.

P1: Supporting existence dissociation. Wide CIs. **COMPRESS.** Attack surface, not core.

P2: Eligibility / coverage. **COMPRESS.** The 4-task exploratory reversal is a liability.

P3: **CORE.** Keep. Cut C7 / G2 / comparative-gate from the main line.

P4: **SECONDARY, coherent.** Keep the sequence; collapse B+C; keep C2+D.

P4-M: Formal bookkeeping. **One paragraph, not a section.**

EXTERNAL: Honest STOP. **Move into Limitations.** Not evidence of generality.

NOVELTY / 5: **3**

SIGNIFICANCE / 5: **3**

AAMAS FIT: **MODERATE**

NEW EXPERIMENT REQUIRED: **No** (not for the licensed claim). Transport would be a different paper; `8680588` already showed it is not available under the frozen contract.

FINAL STRUCTURAL RECOMMENDATION: **V4 + V5** — compress P1+P2 to one short supporting section; fold P4-M into a paragraph; keep P3+P4 as the paper.

FINAL SUBMISSION DECISION: **B** — one more structural revision, then it can be submitted as a **methods / evaluation paper**, not as a major empirical CUA paper that “settles” reliability measurement.

---

## 1. Executive verdict

The v0.3 narrowing worked. The paper no longer claims to have discovered that evaluation is a measurement problem. Dong, Kane, Shao, Xue, and Rosset are confronted. Hygiene on prevalence, pooling, and “failed metrics” is unusually careful.

That is necessary and not sufficient.

A hostile CUA reviewer who has read Dong will still write: *you audited one extractor on one bench family, found a fail-closed aggregation bug, confirmed that loosening it hurts precision, then built a last-text instrument that mostly abstains or never sees a MISS.* That review is **not a misreading**. It is a ranking of *significance relative to Dong/Shao/Xue*, not a claim that M1a is identical to Dong.

The paper is scientifically honest and **too wide**. Thirteen sections, three supporting studies, a four-stage construction, a formal object, a checklist, and an eligibility STOP. The thing a reader should remember is two sentences: gold entered `found` and was discarded; making aggregation more permissive released +8/−18. Everything else either motivates that, bounds it, or invites a new attack.

**Submission-ready as-is: no.**  
**Fatal scientific error: no.**  
**Needs a new experiment to support C-PRIM: no.**

---

## 2. Reviewer A — CUA / ML agent evaluation

Primary attack: *“Dong already did this.”*

### A1. What exactly did Dong establish?

Dong et al. (arXiv:2607.28367): a CUA **score is a pipeline output**; reliability can fail at task construction, trajectory observation, scoring, and reporting; a retrospective audit of **150 public FAIL-scored traces** across five benches finds **15.3% of FAIL verdicts wrong** (10.7% evaluator FNs, 4.7% broken tasks, 3.3% unclear from released evidence).

That is a **verdict audit** on **public multi-benchmark** traces.

**SEVERITY:** NONE as a fact about Dong. **MAJOR** as an overlap the paper must live with.

**EVIDENCE:** Paper §2.3 quotes this accurately.

**REQUIRED FIX:** None on Dong’s claims. Do not compete on n=150.

**NEW EXPERIMENT?** No.

### A2. What exactly does this paper establish?

On **one frozen MyPCBench extractor**: of 59 rows with gold literally in the answer, 39 missed; **13** after gold was already in `found`. Pre-specified plurality repair: +8 correct, +18 wrong; ALL worse than frozen. On a **constructed last-text instrument**: DONE≠evidence, sparse coverage, Form≠two-sided ID, 30 HIT / 0 MISS ⇒ \(I_{CC}=0\).

**SEVERITY:** NONE (this is the paper).

### A3. Is the residual scientifically meaningful?

**Yes, narrowly.** Dong asks: is the published FAIL *correct*? This paper asks: did the frozen *transformation* collect gold and then drop it, and does loosening the drop restore the intended measurement?

Dong does not freeze \(P\), does not count accumulator states, and does not run signed layer repairs. Xue/Rosset do not measure discard **after** gold entered a typed `found` list.

**SEVERITY of “no residual”:** MAJOR if the paper still sounds like a pipeline paper in the intro; **NONE** if the reader reaches §6. Intro still lists “four things,” which re-inflates the residual into a programme.

**REQUIRED FIX:** Make the residual the title of the empirical core, not the fourth bullet of a four-part show. Structural, not experimental.

**NEW EXPERIMENT?** No.

### A4. Is M1a new enough to matter?

**Mechanism isolation: yes. Field-level novelty: borderline.** Fail-closed unique-candidate aggregation is a known software pattern. What is new is **treating that pattern as the object of a CUA measurement audit** with independent gold, a frozen extractor hash, and a pre-specified repair.

A reviewer who thinks “parser bug” will not be moved by the label M1a. They will be moved only if they accept that **instrument-level discard after collection is a different error from “the oracle said FAIL.”**

**SEVERITY:** MAJOR (significance), not FATAL (identity).

**REQUIRED FIX:** One paragraph that says: we are not claiming the first evaluator error; we are claiming a **distinct error location** (post-R, pre-Y) that verdict audits cannot see.

Already partly in §6. Tighten; do not add studies.

**NEW EXPERIMENT?** No for the licensed claim. Transport would raise significance from 3 to 4; `8680588` shows it is not available without changing protocol.

### A5. Is the repair experiment meaningful or debugging?

**Meaningful as a diagnostic, not as engineering success.** +8/−18 is the result that stops “just fix the parser.” ALL=10 vs frozen=20 is the result that stops “compose the patches.”

If the paper presents four named repairs + C7 sign flip, it looks like a debug log.

**SEVERITY:** MAJOR if C7 stays in the P3 climax; MINOR if the table is compact and C7 is cut.

**REQUIRED FIX:** Keep Table `tab:repairs` and the +8/−18 sentence. Move C7 (\(n_{\mathrm{eff}}=1\)), G2 9/30, and the 16/28 gate to appendix or delete from the story.

**NEW EXPERIMENT?** No.

### A6. Is P4-D real science or zero variance?

See §10. **Observability under a locked two-sided rule**, not a discovery about Flash. W1 (“challenge weak”) is already the paper’s own classification. A hostile reviewer will quote 30/0 and stop reading the W1 sentence.

**SEVERITY:** MAJOR for overclaim; MINOR if wording stays at sample+rule.

**REQUIRED FIX:** Do not let abstract/conclusion say “competence without negative variation” as if it were a general law. Keep “this sample / locked rule.”

**NEW EXPERIMENT?** Manufacturing MISS is forbidden and would **destroy** the result’s meaning.

### A7. Does the paper need external replication?

For **C-PRIM as an instrument-level existence result: no.**  
For **a major-venue “CUA evaluation fails like this” paper: yes**, and it is unavailable (`8680588`).

**SEVERITY:** MAJOR for significance/generality; **not FATAL** for an existence methods paper if the limitation stays loud.

**REQUIRED FIX:** Do not add a section that sounds like a failed replication of P4-M’s last-text \(I\). The PDF’s §11 is the wrong grain (last-text typed contract), and `8680588` is not even in the PDF.

**NEW EXPERIMENT?** Only if the *goal* changes to prevalence. That is a different paper.

### A8. Does small n undermine the central claim?

**No**, if the claim is existence+signed diagnostic. **Yes**, if anyone reads Claude 0.857 as a finding. P1 CIs are an own-goal.

**SEVERITY:** MAJOR for P1/P2 presentation; NONE for M1a 13/39 as a count in a frozen 59-row R1 set.

**REQUIRED FIX:** Compress P1/P2; do not lead with rates.

**NEW EXPERIMENT?** No.

### A9. Is last-text a strawman?

**P4-B/C: largely yes** (“undeclared last-text is sparse”). Xue/Rosset already said last-frame visual is lossy; last-text is harsher.  
**P4-D: no** — the channel is *dense* (30 HIT, 0 ABSTAIN) and the two-sided estimand still fails.

**SEVERITY:** MAJOR for P4-B/C occupying equal billing with P4-D; FATAL only if the whole constructive programme is B/C.

**REQUIRED FIX:** Collapse B+C to one paragraph. Let D (and C2) carry P4.

**NEW EXPERIMENT?** No.

### A10. Is the paper just a MyPCBench parser audit?

**P3: yes, that is what it is, and that can be a paper.**  
**The current PDF: no, because it refuses to be only that**, and the extra studies are what make it look unfocused.

**SEVERITY:** MAJOR (framing).

**REQUIRED FIX:** Lean into the parser-audit-as-measurement-object framing. Stop looking like a four-paper programme.

**NEW EXPERIMENT?** No.

---

## 3. Reviewer B — measurement / HCI / methodology

### B1. “This is just Kane/Messick.”

**SEVERITY:** MINOR (answered in §2.2).  
**VULNERABLE:** Intro still spends a paragraph on the pipeline as if the object were validity theory.  
**SKEPTIC:** *You operationalized Kane at CUA grain; Bean already gave checklists.*  
**CURRENT TEXT:** Explicitly “we do not invent validity.”  
**CHANGE:** None required beyond not letting \(\mathcal{M}\) look like a theory section.

### B2. “\(\mathcal{M}(\tau,I)\) is trivial notation.”

**SEVERITY:** MAJOR if §8 remains a full section; NONE as a one-line definition.  
**VULNERABLE:** §8 entire; Eq. (2).  
**SKEPTIC:** *This is a set-builder for “claims we can support.”*  
**CURRENT TEXT:** Already says bookkeeping. Then spends a page anyway.  
**CHANGE:** Delete the section; keep the sentence in §3.

### B3. “Typed correspondence is definitional.”

**SEVERITY:** MINOR (answered).  
**VULNERABLE:** §8.1.  
**SKEPTIC:** *HIT ⇒ parse and match is the definition of HIT.*  
**CURRENT TEXT:** “specification-level implication.”  
**CHANGE:** Keep at most three lines. Do not name it a “property” in a subsection title if space is tight.

### B4. “Three gaps are renamed measurement errors.”

**SEVERITY:** MINOR.  
**VULNERABLE:** Fig. 1 note; §3 bullets; §9 headings.  
**SKEPTIC:** *Dong already has construction/observation/scoring/reporting.*  
**CURRENT TEXT:** “analytic labels, not new laws”; overlap with Dong stated.  
**CHANGE:** Do not let Table `tab:core` plus three gap paragraphs plus Fig. 1 **repeat** the ontology three times.

### B5. “P4-D merely has no negative variance.”

**SEVERITY:** MAJOR.  
**VULNERABLE:** Abstract “competence without negative variation”; §7.4.  
**SKEPTIC:** *Identifiability of a two-sided parameter requires negatives. You observed none. That is a sample fact.*  
**CURRENT TEXT:** W1 / G3 / locked \(I_{CC}\) rule. Good. Abstract still sounds law-like.  
**CHANGE:** Abstract/conclusion must say **this sample, this rule**.

### B6. “ABSTAIN is just missing data.”

**SEVERITY:** MINOR.  
**VULNERABLE:** §7.1.  
**SKEPTIC:** *Missingness is not a contribution.*  
**CURRENT TEXT:** Distinguishes ABSTAIN from MISS and DONE. That **is** the point for CUA leaderboards that collapse them.  
**CHANGE:** None if B/C are compressed; don’t build a theory of missingness.

### B7. “Last-text is an arbitrary channel.”

**SEVERITY:** MAJOR for P4-B/C; MINOR for a declared severe \(I\).  
**VULNERABLE:** §3 “never screenshots or tool traces as a silent fallback”; §7.2 last sentence.  
**SKEPTIC:** *You forbade the channels CUA evaluation actually uses, then discovered they were needed.*  
**CURRENT TEXT:** Limitations cite Xue/Rosset; “not canonical.”  
**CHANGE:** Say **why** the channel was frozen (non-leakage / no silent fallback), not that agents “need not” communicate that way as if that were surprising.

### B8. “You confuse observability with validity.”

**SEVERITY:** MINOR.  
**VULNERABLE:** “justification gap”; \(I_{CC}=0\) as “cannot justify a two-sided claim.”  
**SKEPTIC:** *Unidentifiable ≠ invalid construct.*  
**CURRENT TEXT:** Mostly careful.  
**CHANGE:** Keep “cannot estimate two-sided CC from this sample,” not “the claim is invalid.”

### B9. “You confuse evaluator failure with agent failure.”

**SEVERITY:** NONE as written.  
**VULNERABLE:** None fatal; P4-B 40 DONE / 30 ABSTAIN is the teaching example.  
**CURRENT TEXT:** Repeated disclaimers.  
**CHANGE:** None.

### B10. “The reporting checklist is generic.”

**SEVERITY:** MINOR.  
**VULNERABLE:** §10 eight slots + second enumerate of how the programme fills them.  
**SKEPTIC:** *Bean already has a checklist. Kane already has IUA.*  
**CURRENT TEXT:** “not a validated standard.”  
**CHANGE:** Keep the eight questions as a box. Delete the second “how we filled the slots” list. It reads like padding.

---

## 4. Reviewer C — hostile CUA benchmark researcher

Default: *ordinary parser bugs in measurement clothing.*

| Attack | Hostile version | Is it fair? | Paper’s legitimate reply | Residual |
|---|---|---|---|---|
| A. M1a is a bug | Fail-closed unique match dropped extra candidates. Fix uniqueness. | **Fair as engineering.** Unfair as “therefore not science”: the paper **measured** the bug’s signed repair. | The bug is the **measurand**. We froze it and tested the obvious fix. | Still one extractor. |
| B. Repairs are debugging | Four patches, one table. | **Fair** if C7/G2 stay. | +8/−18 is a scientific outcome of a pre-specified intervention. | Looks like a systems note if P3 is ⅓ of a 13-section paper. |
| C. P3 is tiny | 13 M1a cases. | **Fair for prevalence.** Unfair for existence. | 13/39 of misses in a locked 59-row R1 set; not a rate over CUA. | Significance. |
| D. P4 is constructed | Synthetic slate, last-text. | **Fair.** Constructive measurement is allowed; it is not OSWorld. | Sequence is where construction **stops**, not a hidden leaderboard. | Will never beat a public-bench paper on “real CUA.” |
| E. 30/0 uninformative | Model succeeded. | **Fair as W1.** | Locked \(I_{CC}\) needs ≥8 MISS; sample produced 0; G2 held. | Easy to misread as a boast. |
| F. last-text artificial | Real CUAs are screenshot/a11y. | **Fair for B/C.** | Declared severe \(I\); not canonical. | Strawman if B/C are long. |
| G. no external replication | STOP. | **Fair for generality.** | Existence paper + honest STOP. | Venue competitiveness. |
| H. no new metric | We wanted a score. | **Not a scientific defect.** | Explicit refusal. | Some AAMAS reviewers still want a metric. |
| I. no leaderboard | Doesn’t change OSWorld ranking. | True. | Not the object. | “So what?” |
| J. no deployment | No safety case. | True; limitations say so. | — | Don’t overclaim impact. |
| K. P1/P2 unnecessary | Turk already did paired interventions in another domain; coverage tables are obvious. | **Mostly fair.** | Motivation that \(S\) is not \(Y\). | Dilution. |
| L. too many moving pieces | 13 sections. | **Fair.** | Compress. | This is the acceptance-probability issue. |
| M. not enough for a major venue | Incremental to Dong. | **Fair at NeurIPS/ICML oral; contestable at AAMAS methods.** | Residual is instrument-grain. | Do not submit as a “major empirical CUA” paper. |
| N. workshop / systems note | Parser postmortem. | **Too harsh if P3+repair+P4-D stay tight.** Too kind if the PDF stays as-is. | Tighten to methods note of record. | Current PDF is **between** workshop and full paper. |

This reviewer would **reject the current 16-page PDF** as unfocused, and might **accept a 9–11 page methods paper** of P3+P4 with compressed motivation.

They would **not** be convinced by more measurement vocabulary.

---

## 5. Should P1/P2 stay?

### Version A (current): P1+P2+P3+P4+P4-M

Tells a pipeline story. Pays for it with two small-n studies, two extra figures, Type A percentages a reviewer will quote against you, a 4-task “reversal,” and the feeling of a thesis, not a paper.

### Version B: P3+P4+P4-M

Opens on the instrument. Loses the pedagogical “score can be inert while the world moved.” A CUA reviewer who already believes Dong does not need P1. A reviewer who thinks scores *are* tracking might.

| Q | Answer |
|---|---|
| 1. P1 necessary for the central argument? | **No.** Central argument is discard+repair (+ identifiability). P1 is motivation that \(S\neq Y\). Dong/Turk already motivate distrust of scores. |
| 2. P2 necessary? | **No.** Eligibility is real but obvious once \(\lvert\mathcal{A}\rvert=1\) is on the table; the exploratory 4-task Δ is actively harmful. |
| 3. Do they make P3 more intelligible? | Slightly: “we looked inside the maps that produce \(S\).” One paragraph can do that. |
| 4. Progression score→eligibility→loss→ID? | Elegant in a grant. In a paper it reads as **four papers stapled**. |
| 5. Dilute the strongest contribution? | **Yes.** |
| 6. Extra small-n attack surfaces? | **Yes.** 24 pairs, 18 pairs, 4-task ∩, Claude n=1. |
| 7. Collection of studies? | **Yes.** |
| 8. Removing them cleaner? | **Yes**, if one short motivation paragraph remains. |
| 9. Keeping them more convincing? | Only for readers who have never seen a score–construct mismatch. Those readers are not the hostile CUA reviewer. |
| 10. 24-hour memory? | **M1a + +8/−18 + 30/0.** Not 0.857. |

**HARD RECOMMENDATION: COMPRESS** (not CUT, not KEEP as full sections).

Keep: 1 short supporting subsection (~0.5–0.75 page) that \(S\) can dissociate from tracking (existence; **no table of invariance rates**) and that selection/coverage can empty a comparison (\(\lvert\mathcal{A}\rvert=9/8/1\); selection not evaluated).  
Cut from main: Fig. gold/pairs, Table s1 CIs, exploratory bootstrap, retrieval-f009.

**MOVE TO APPENDIX:** P1 tables/figures; P2 4-task analysis.

---

## 6. Is P3 really the core?

**P3 only:** *In a frozen CUA text extractor, recoverable gold was missed after it had already entered the accumulator, and making aggregation more permissive released more wrong matches than correct ones.*

**P4 only:** *When we built an observation-grounded last-text protocol, completion did not yield evidence, a declared interface did not identify two-sided correspondence, and a competent 30/0 sample left \(I_{CC}=0\).*

**P3+P4:** *A frozen CUA instrument can throw away gold it already collected, and constructing a stricter observation-grounded protocol does not automatically yield an identifiable two-sided reliability claim.*

**Strongest novelty-to-evidence: P3+P4**, not P3 alone.

- P3 alone is a high-quality **instrument autopsy**. Easy to reject as a bug report.
- P4 alone is a **constructed negative**. Easy to reject as a strawman channel.
- Together: the existing instrument fails *after collection*; the constructed instrument fails *at identifiability even when HIT-rich*. That is one argument: **you cannot repair your way to a justified two-sided reliability claim by being sloppy or by being strict.**

P3 is the **empirical core**. P4 is the **bound**. P4 without P3 is unmotivated harshness. P3 without P4 is “fix your unique-match.”

---

## 7. M1a novelty audit

**What M1a adds beyond generic evaluator error**

| Prior | Error location | M1a |
|---|---|---|
| Dong | Published FAIL vs human/LLM relabel of the **episode** | Gold **in R**, then dropped by **A**, before Y |
| Xue / WebJudge | Last-frame / underspecified visual judge; screenshots never selected into \(I\) | Text gold **was selected into `found`** |
| Rosset | Last-frame vs overloaded full trajectory; top-K is *designed* discard of low-relevance frames | Fail-closed drop of **already-accepted gold**, including majority-gold 7/13 |
| Trajectory judges / AgentRewardBench | Judge vs human **verdict** | No judge in the extractor |
| Generic parser literature | Span never matched | Span matched, then aggregation killed it |

**Do not claim novelty for the name M1a.**  
**Do claim a distinct location:** post-collection, pre-decision, independently evidenced by accumulator state.

**Can the paper defend** “post-collection discard is a distinct instrument-level failure mode”?

**Not as a CUA-general law.** Transport STOP (`8680588`) forbids that.

**Defensible wording:**

> In this frozen extractor, post-collection discard is a distinct instrument-level failure mode from agent omission, screenshot omission, and verdict-level false negatives: gold was present in \(\tau\) and in the intermediate `found` set, then removed by fail-closed aggregation before the final match.

**Narrower if a reviewer refuses “distinct mode”:**

> We isolate a fail-closed aggregation step that discards gold the extractor has already collected; this location is invisible to verdict audits that only relabel PASS/FAIL.

---

## 8. Repair experiment audit

| Hypothesis | Defensible? |
|---|---|
| A. Parser bugs exist | Trivial. Do not use the table for this. |
| B. Permissive repair is not guaranteed to improve measurement | **Yes.** +8/−18; ALL 10 vs 20. **This instrument only.** |
| C. General theorem about parsers | **No.** Paper already disclaims this. |
| D. All CUA evaluators | **No.** |

**Placement:** **Main text, compact table** (`tab:repairs` + three sentences).  
Not appendix: without it, M1a is a bug report.  
Not a long subsection: C7, G2, 16/28 are appendix material.

---

## 9. P4 coherence audit

**Verdict: A. one coherent constructive sequence**, with redundancy.

Common logic: *If correspondence measurement is restricted to a declared last-text \(I\) and independent \(L\), then execution success, interface compliance, and even a HIT-only competent sample need not identify the two-sided claim one wanted.*

| Stage | Role | Keep? |
|---|---|---|
| P4-B | DONE ≠ determining \(E\) | Merge with C |
| P4-C | Natural last-text sparse | Merge with B (same lesson: \(I\) may be empty) |
| P4-C2 | Form ≠ two-sided ID | **Keep** — different lesson (dense interface, still unevaluable two-sided) |
| P4-D | HIT-rich, \(I_{CC}=0\) | **Keep** — different lesson (dense *and* competent, still no negatives) |

B and C are the same scientific sentence. D is not “the model succeeded so what.” C2 is the bridge: you can force coverage and still fail the two-sided floor.

Removing all but D (**V6**) loses the reason D exists (you got to 30/0 by adding an interface and still not manufacturing MISS). **Do not drop B/C entirely; collapse them.**

---

## 10. P4-D zero-MISS attack

**Attack:** *This is just because the model succeeded.*

**Fair.** G2 10/10 plus 30 HIT / 0 MISS **is** success on the scored channel. W1 says the **challenge was weak**. That is not a euphemism; it is the finding’s boundary.

**Does it establish** “two-sided correspondence was unidentifiable under the locked protocol”?

**Yes, tautologically, given \(I_{CC}=1\) iff n_HIT≥8 and n_MISS≥8, and n_MISS=0.** That is a **protocol+sample** result, not a discovery that two-sided CC is metaphysically unidentifiable for competent CUAs.

**Does it establish** “the sample happened to contain no errors”?

**Also yes.** Those are the same fact.

**Strongest defensible wording:**

> Under a pre-locked rule that a two-sided correspondence estimand is identifiable only if the sample contains at least eight HIT and eight MISS, this confirmatory Flash sample (30 HIT, 0 MISS, G2 10/10) left \(I_{CC}=0\). That is a statement about **this protocol and this sample**, not that the agent is perfectly reliable or that two-sided CC cannot be identified in some other design.

Do **not** rescue it by implying competence *causes* unidentifiability. Competence **coexisted** with zero negatives. Causal language is not licensed.

**Do not** call this FATAL. Call it **easy to overclaim**. The abstract currently overclaims slightly (“competence without negative variation” as one of “four things we show”).

---

## 11. Last-text strawman attack

**Legitimate protocol?** Yes, **as a declared severe \(I\)**: no silent screenshot/tool fallback, so HIT cannot be laundered from leaked channels. That is a measurement-design choice, not a claim about how CUAs should talk.

**Can it be defended without being canonical?** Yes. Limitations already do. The body still sounds surprised that agents don’t dump typed claims in last text.

**What P4 shows:**
- B/C: undeclared last-text often contains no determining span (**coverage**).
- C2: declaring an interface can raise Form without identifying two-sided CC.
- D: even when last-text is full of HIT, two-sided ID can fail.

**Is it “bad channel ⇒ bad coverage”?** **B/C yes. D no.**

**Fatal?** **No**, if B/C shrink and D stays. **Yes** if the constructive section is mostly abstention counts.

The sentence “Natural agents need not communicate determining evidence through an undeclared last-text channel” is **true and unsurprising**. It is not enough to carry P4. **P4-D’s sentence is enough.** B/C should be a setup, not a result of equal weight.

---

## 12. External STOP audit

Two STOPs, easy to conflate:

1. **`de66e0a` / PDF §11:** no public corpus for **frozen last-text typed \(I\)** of P4-M transport.  
2. **`8680588`:** no public evaluator+gold+R for **M1a analogue**. **Not in the PDF.**

**Is “no eligible public corpus” a weakness, neutral limitation, or evidence about reproducibility?**

- **Weakness for generality.**  
- **Neutral limitation for an existence paper**, if short.  
- **Not evidence** that CUA artifacts are unreproducible or “not measurement-ready.” The paper already forbids that sentence.

**Exact wording the paper should use (if it mentions it at all):**

> We did not identify a public trajectory dump satisfying this paper’s frozen last-text typed observation contract without changing \(I\) or the parser. That eligibility STOP is not a ranking of public benchmarks.

**Placement: COMPRESS into Limitations (3–4 sentences). Not a main-text section.**  
A whole §11 looks like a failed replication study. It is an eligibility audit of a **self-imposed** \(I\).

Do **not** add `8680588` to the PDF unless as one limitations clause (“a subsequent audit of other evaluators’ intermediate representations also found no jointly eligible public E2 corpus”). Optional. Not a contribution.

---

## 13. Small-n audit

| Study | n | Claim type | CI needed? | Prevalence? | Central conclusion depends on large-n? |
|---|---|---|---|---|---|
| P1 | 24 valid pairs; per-lane 9/8/1 | Existence | Paper reports CIs; they **hurt** (too wide to headline) | Forbidden; still looks like rates | **No** |
| P2 | 18 pairs; ∩=4 | Eligibility + exploratory | Bootstrap on 4 tasks is theatre | Forbidden | **No** |
| P3 | 134 rows; 59 R1; 13 M1a | Mechanism count in a frozen set | Optional Wilson on 13/39; not required for existence | Forbidden | **No** |
| P4-B | 40 | Existence of abstention under DONE | No | No | **No** |
| P4-C/C2/D | 30 | Gate outcomes | No | No | **No** |

**Can a reviewer honestly say the central conclusion depends on a large-n estimate?**  
**No.** The central conclusion is **not** a rate. It is: this extractor discarded collected gold; this repair was not net-correct; this locked two-sided rule was not identified in this sample.

**The problem** is that P1 **looks** like a rate study. That is a presentation bug, not a statistics bug.

---

## 14. Claim-density audit

| Class | Claims in the current PDF |
|---|---|
| **CORE (must be exactly one)** | M1a post-collection discard + signed repair non-dominance in frozen extractor **C-PRIM** |
| SUPPORTING | P1 Type A/B existence; P2 coverage/eligibility; P4-B/C coverage empty; P4-C2 Form≠ID; P4-D \(I_{CC}=0\) |
| FORMAL | \(\mathcal{M}\); Observable_τ ≠ Observable_I; HIT⇒parse (definitional) |
| METHODOLOGICAL CONSEQUENCE | 8-slot checklist |
| BACKGROUND | Score is a pipeline; Kane/Messick; Dong/Shao/Xue/Rosset |

**Independent scientific claims a reviewer can count: ~10+.**  
**CORE should be 1.** The PDF still *behaves* as if P4’s four boundaries were co-equal contributions (“we show four things,” abstract laundry list).

**The paper is trying to prove too much.** Not by inventing numbers — by **refusing to leave anything in the appendix.**

---

## 15. Novelty vs significance

**NOVELTY (what is new?): 3/5**  
New combination: freeze a CUA text extractor, read the accumulator, count post-collection discard, pre-specify signed repairs, then construct a last-text correspondence instrument until two-sided ID fails. Not a new theory. Not first evaluator error. Not first “scores are pipelines.”

**SIGNIFICANCE (why care?): 3/5**  
CUA researchers *should* care that a high score can be inert to world change (P1, supporting), that fail-closed aggregation can delete gold (P3), and that a HIT-only sample cannot identify two-sided CC (P4-D). They will care **less** than about Dong’s 15.3% wrong FAILs on public benches, because that number travels.

**Sentence that would make a reviewer want to read:**

> Gold was already in the extractor’s `found` set in 13 misses, and the pre-specified permissive fix released twice as many wrong matches as right ones.

Not: “reliability evaluation is a measurement problem.”  
Not: “we propose eight reporting slots.”

---

## 16. Venue fit (AAMAS / GAAI-style)

| Question | Answer |
|---|---|
| Within agent evaluation? | **Yes.** |
| Empirical contribution sufficient? | **Borderline** for a full paper; sufficient for a methods paper if compressed. |
| Methodological framing appropriate? | **Yes**, after v0.3 demotion. Still a bit heavy. |
| Lack of new metric acceptable? | **Yes** for AAMAS evaluation/methodology; some reviewers will still want one. Not a reason to add a metric. |
| Lack of public replication fatal? | **No** for existence; **hurts** relative to Dong/Shao. |
| Constructed P4 acceptable? | **Yes** as construction-until-bound; **no** as a substitute for OSWorld. |

**FIT = MODERATE.**

Not WEAK: the object is agent evaluation reliability, which is in-scope.  
Not STRONG: n, single instrument, no public analogue, 16-page sprawl vs AAMAS attention.

Do **not** recommend NeurIPS/ICML as a better fit; those are harsher on incremental eval audits. Do **not** recommend a different venue merely because AAMAS is imperfect. If this is aimed at AAMAS-style agent evaluation, **moderate fit after a cut**, not after adding studies.

The frozen 8-pager at `paper/aamas2027_reliability_score/` is a **different object** (P1–P3 only) and is not this PDF. Do not merge.

---

## 17. Kill-test matrix

| ID | Rejection | STATUS | Legitimate rebuttal from **current evidence only** |
|---|---|---|---|
| R1 | Already in Dong | **ANSWERED** as identity; **MAJOR** as significance | Dong relabels public FAIL verdicts. We freeze \(P\), count gold in `found` then dropped, and sign a pre-specified repair. |
| R2 | M1a is a parser bug | **MAJOR** | It is an instrument defect. We treat the defect as the object: independent gold, frozen hash, accumulator state, signed repair. Verdict audits cannot see this location. |
| R3 | Repairs are engineering | **ANSWERED** if table stays compact | The licensed claim is non-dominance (+8/−18; ALL worse), not a shipped parser. |
| R4 | Sample too small | **MAJOR** for P1/P2 rates; **ANSWERED** for C-PRIM as existence | Central claim is not a prevalence estimate. P1 CIs should not be in the main story. |
| R5 | Last-text strawman | **MAJOR** for P4-B/C length; **ANSWERED** for declared \(I\) + P4-D | Channel is frozen and non-canonical. P4-D is HIT-rich, not empty-channel. |
| R6 | P4-D is zero variance | **ANSWERED** with W1 caveat | Locked two-sided rule needs MISS; this sample had 0; G2 held; W1 = challenge weak. Not “Flash is perfect.” |
| R7 | P4-M definitional | **ANSWERED** | Demoted; still too long. |
| R8 | Three gaps not novel | **ANSWERED** | Organizing device; Dong overlap stated. |
| R9 | STOP means no generalization | **MAJOR** | STOP is eligibility under a frozen contract, not a finding that M1a is unique. Generality is **unshown**, not refuted. |
| R10 | No practical impact | **MINOR** | Practical claim is reporting \(I\), abstention, identifiability before interpreting \(S\). No deployment safety. |
| R11 | Too many studies | **MAJOR** | Valid. Compress. |
| R12 | Needs a new metric | **ANSWERED** | Refusing a metric is in-scope for evaluation methodology. |
| R13 | Needs external replication | **MAJOR** for a “CUA-wide” paper; **ANSWERED** for existence | Licensed claim does not require it. A stronger paper would. `8680588` says it is not sitting on disk. |
| R14 | Nothing about real-world CUA reliability | **ANSWERED** as scope | We do not measure agent reliability. We measure what a frozen protocol can justify. That *is* the point. |

**No FATAL** if the paper stays inside C-PRIM + P4 bounds and **shrinks**.  
**Several MAJOR** if submitted as the current 16-page PDF.

---

## 18. Paper-cut simulation

| Version | Coherence | Novelty clarity | Attack surface | Significance | Recommend? |
|---|---|---|---|---|---|
| **V0 current 16pp** | Medium (programme) | Low (four things) | Highest | Diluted | **No** |
| **V1 drop P1** | Better | Better | Still P2 4-task | Same core | Incomplete; P2 remains a barnacle |
| **V2 drop P2** | Better | Better | Still P1 CIs | Same core | Incomplete |
| **V3 drop P1+P2** | High | Highest | Lowest | Core intact | **Yes, if 0.5p motivation remains** |
| **V4 compress P1+P2 to 0.75p** | High | High | Low | Core + minimal motivation | **YES — primary** |
| **V5 P4-M → one paragraph** | High | High | Lower (definitional attack dies) | Unchanged | **YES — with V4** |
| **V6 only P4-D from P4** | Weaker (D unmotivated) | Mixed | Strawman “why this channel” | Loses C2 | **No** |

**FINAL STRUCTURAL RECOMMENDATION: V4 + V5**, plus: merge P4-B/C; move C7/G2/16/28 to appendix; fold §11 into Limitations; drop the second checklist enumeration.

Estimated: a **sharper 10–12 page methods paper** with the same licensed claims.

---

## 19. Final submission verdict

**Choose exactly one: B. ONE MORE REVISION**

Not A: authors unset; too many studies; abstract still a laundry list; §8 and §11 still look like extra papers; P1 rates still in main.

Not C: C-PRIM does not require new data. `8680588` already asked the transport question under a hard contract and stopped. Do not reopen P3/P4. Do not manufacture MISS.

Not D: residual vs Dong is real (accumulator location + signed repair). Incremental ≠ empty.

Not E: P3 and P4 are one argument. Splitting produces a bug-report workshop paper and an unmotivated construction paper.

### Only revisions that materially raise acceptance probability

1. **Compress P1+P2** to one supporting subsection; appendix the figures/CIs/4-task bootstrap.  
2. **Strip P3 main text** to M1a + causes table + repairs table + +8/−18 + ALL. Appendix C7, G2, comparative gate.  
3. **Merge P4-B and P4-C**; keep C2 and D.  
4. **Replace §8 with ≤1 paragraph** in §3 or end of §7.  
5. **Replace §11 with a Limitations paragraph.**  
6. **Shorten abstract** to M1a + repair + P4-D identifiability; drop the four-boundary laundry list.  
7. **Delete the second eight-slot “how we filled them” list.**

No new experiments. No new metric. No MISS factory. No parser relaxation.

After that cut, the paper is a **submitable AAMAS-style evaluation methods paper** with moderate fit and still-incremental novelty. It will not become Dong-scale by editing.

---

## 20. Process note

This audit did not modify `main.tex`, bibliography, figures, tables, or frozen artifacts.  
`8680588` is not in the PDF; the PDF’s §11 is the earlier last-text transport STOP (`de66e0a`).

---

ONE-SENTENCE VERDICT:  
"What I would tell the AAMAS area chair about this paper is: it is an honest, overlong methods paper whose real result is that a frozen CUA extractor discarded gold it had already collected and that loosening aggregation made measurement worse—worth considering after they cut the extra studies, not as a four-act theory of reliability."
