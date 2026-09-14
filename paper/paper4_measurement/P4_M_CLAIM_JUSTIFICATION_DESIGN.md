# P4-M — Claim justification / measurability (design freeze)

**Status: THEORY CLOSED. §13 ACCEPT. Typed Soundness ACCEPT (no-leakage lemma, not strong validity). NL denotation OUT OF SCOPE. Empirical implementation NOT STARTED. Phase 1 NOT opened.**  
**File:** `P4_M_CLAIM_JUSTIFICATION_DESIGN.md` — **ACCEPTED**  
**Workstream:** `P4-M / Claim Justification`  
**This file is not P4-E, not Phase 5 of P4-D, and not a new reliability metric.**

```
P4-B     CLOSED   positive-but-incomplete          immutable
P4-C v1  CLOSED   Metric v1 FAIL                   immutable  (falsification)
P4-C2    CLOSED   DFC v2 FAIL                      immutable  (H3 NOT_EVALUABLE)
P4-D     CLOSED   FAIL / W1                        immutable  (G3; I_CC=0; 30 HIT / 0 MISS)
CC-nat   CLOSED   two-sided CC from natural τ      immutable  (not resurrected)
P4-M     ACCEPTED design + amended formalization   this file
                  kind-only E accepted; NL denotation out of Level 1
                  Non-triviality PASS
                  E-expressiveness LOCALIZED, NOT DISSOLVED
                  Validity theorem NOT PROVEN
                  Empirical implementation NOT STARTED
                  no corpus; no params; no runner; $0
                  experiment NOT implied
```

**Human lines recorded:** `ACCEPT P4-M DESIGN`; `AMEND P4-M FORMALIZATION ONLY`; kind-only \(E\) **ACCEPTED**.

Acceptance is of the **question and claim-justification object**, not of
a completed theory. The first operational taxonomy (four-label \(O(\tau)\))
did not survive adversarial review. This amendment replaces that taxonomy.
It does not reopen P4-D, CC-natural, C2, or any frozen instrument.

P4-D remains **FAIL / W1 / CLOSED**. CC-natural remains **CLOSED**.
Frozen `score_v2` + wrapper remain C2 hashes. DFC is **one** interface
\(\mathcal{I}\), not the definition of evidence.

**Authorization for this file.** Scientific design only. No Phase 1, no
worlds, no API, no corpus commit, no experiment implied.

Forbidden until a later, explicit authorization that names a *new*
question an experiment would answer:

- modify `p4_instrument.py`, `p4_instrument_v2.py`, or the C2 wrapper
- edit B/C/D/E/Q/CQ/DQ/EQ/V/R worlds, gold, seals, or \(\tau\)
- author a new slate, wordlist, or generator
- execute agents or spend API
- pool synthetic MISS into a natural two-sided claim
- resurrect CC-natural by renaming the fraction
- treat `I_{CC}=0` as “agent unreliable”
- treat `NONDETERMINING` as `MISS`
- change \(Y\) from traces, screenshots, or \(A\)
- treat “no `CLAIM:` line” as “agent made no claim”
- expand \(E\) to world-dependent denotation of English descriptions
- pre-schedule P4-M Phase 1/2/3/4 because budget remains

**Frozen scientific lock (canonical).**

- **Object.** Not \(R(\tau)\). The object is the set of reliability
  claims justified by available observations, **indexed by whether
  those observations are in \(\tau\) or in \(\mathcal{I}(\tau)\)**.
- **Question.** Under what observation conditions is a reliability
  claim justified from natural computer-use agent behavior?
- **Not the question.** Which agent is better? What is the scalar?
  How do we create MISS? How do we make D’s `I_{CC}` flip to 1?
- **Rule.** A claim is admissible only if the observation process
  *that claim names* contains the evidence that claim requires.
  Lack of justification is not the negation of the claim.
- **`CLAIM:` syntax is an interface constraint, not evidence.**
- **\(E\):** typed parse of the recovered span by \(\mathrm{kind}(L)\),
  never \(\mathrm{value}(L)\). Descriptions needing world denotation
  are out of Level 1 (scope, not a fix ticket).

---

## 0. Why this file exists (not a renamed P4-D)

Unchanged in substance. P4-D asked whether a controlled natural-agent
protocol could make correspondence **two-sided observable** without a
factory. Flash \(N=30\): Form 1.0000, HIT 30, MISS 0, \(I_{CC}=0\),
**W1**. Closed. Not a ticket to harder distractors.

P4-M asks:

> Given a (possibly lossy) observation interface, **which reliability
> claims are we permitted to infer from \(\tau\)?**

D’s 30/30 HIT remains closed evidence. This amendment does not try to
identify CC-natural.

C2/Q3 remain construct-validity for frozen DFC: a unique *determining*
wrong span, when \(\mathcal{I}\) recovers it, is `MISS`. That does not
licence calling completion-talk `MISS`, and does not licence treating
DFC non-recovery as “no evidence in \(\tau\).”

---

## 1. Scientific question

**Lock. Unchanged.**

> Under what observation conditions is a reliability claim justified
> from natural computer-use agent behavior?

\[
\mathcal{M}(\tau,\mathcal{I})
=\{\,C:\ \mathrm{Justifiable}(C\mid\tau,\mathcal{I})\,\}.
\]

Not \(R(\tau)=?\). Claims are now explicitly relative to an interface
\(\mathcal{I}\) when they depend on what \(\mathcal{I}\) recovers.

**FAIL shapes still rejected:** scalar hunt; \(\mathrm{HIT}^{+}=\)
reliability; \(I_{CC}=0\Rightarrow\) unreliable; synthetic MISS
opens natural Level 3; no HIT \(\Rightarrow\) task failure;
`CLAIM:` present \(\Rightarrow\) Level 1.

---

## 2. Two observables (Attack 1)

**Lock.** Do not write \(\mathrm{Observable}(\tau)\) unqualified.

\[
\mathrm{Observable}_{\tau}(\tau)
=\text{evidence actually present in the trajectory / communication.}
\]

\[
\mathrm{Observable}_{\mathcal{I}}(\tau)
=\text{evidence the declared instrument/interface }\mathcal{I}
\text{ actually extracts.}
\]

```
τ
│
├── evidence actually present
│         ↓
│   Observable_τ
│
└── evidence recoverable under instrument I
          ↓
    Observable_I
```

Frozen DFC (`CLAIM:` line, `score_v2`) is one \(\mathcal{I}\). It is
**not** the definition of what the agent communicated.

**Measurement loss (not Level-0 “no claim”):**

\[
e\in\mathrm{Observable}_{\tau}(\tau)
\quad\text{and}\quad
e\notin\mathrm{Observable}_{\mathcal{I}}(\tau).
\]

The licensed sentence is: *the interface did not expose evidence that
was present in \(\tau\).* Forbidden sentence: *the agent made no claim.*

Form / interface compliance records whether \(\mathcal{I}\) was used.
It is not epistemic emptiness of \(\tau\).

\(Y\) under a declared \(\mathcal{I}\) reads only
\(\mathrm{Observable}_{\mathcal{I}}\). Traces may sit in
\(\mathrm{Observable}_{\tau}\) and in \(A\); they still do not enter
\(Y\) (P4-B). Measurement loss may be *reported*. It must not be
scored HIT by reading traces into the scorer.

---

## 3. Pipeline: interface ≠ parse ≠ sufficiency ≠ correspondence (Attack 4)

**Lock.** The four-label enum

\[
O(\tau)\in\{\mathrm{FORM\_FAIL},\mathrm{NO\_CLAIM},\mathrm{NONDETERMINING},\mathrm{CLAIM}\}
\]

is **withdrawn** as a partition of “what was observable.” It mixed
channel parse with semantic sufficiency and silently dropped
\(\mathrm{Observable}_{\tau}\).

Replace with stages:

\[
\tau
\xrightarrow{\text{interface }\mathcal{I}}
I(\tau)
\xrightarrow{\text{parse}}
P(\tau)
\xrightarrow{\text{sufficiency}}
E(\tau)
\xrightarrow{\text{correspondence}}
Y.
\]

| Stage | Symbol | Asks | May be undefined |
|---|---|---|---|
| Interface | \(I(\tau)\) | Did \(\mathcal{I}\) run on this episode as specified? | — |
| Parse | \(P(\tau)\) | Did \(\mathcal{I}\) recover a unique span? | if interface not applicable |
| Sufficiency | \(E(\tau)\) | Is that span *determining* for \(L\)? | if no unique span |
| Correspondence | \(Y\) | Does the determining span match independently locked \(L\)? | if \(E\) is not determining, or \(L\) is not independent |

**Parse values (under a declared \(\mathcal{I}\)):**
`NO_SPAN`, `UNIQUE_SPAN`, `AMBIGUOUS`.

**Sufficiency values (only if `UNIQUE_SPAN`):**
`DETERMINING`, `NONDETERMINING`.

**Accepted \(E\) rule.** \(\mathrm{kind}(L)\) is specification-level
(task schema), never \(\mathrm{value}(L)\).

\[
E(s)=\mathrm{DETERMINING}
\iff
s\text{ parses as a value of }\mathrm{kind}(L).
\]

Examples under \(\mathrm{kind}=\mathrm{money\_usd}\): `38.35` and
`10.00` are both DETERMINING. `finished successfully` does not parse
as that kind → NONDETERMINING, and **does not create \(Y\)**.

**Correspondence** (only if \(E=\mathrm{DETERMINING}\) and \(L\) is
independent of the evidence channel):

\[
Y(s,L)=
\begin{cases}
\mathrm{HIT}  & s\leftrightarrow L\\
\mathrm{MISS} & s\not\leftrightarrow L.
\end{cases}
\]

Stages do not share a question:

\[
I/P:\ \text{was a span recovered?}
\quad
E:\ \text{is it a typed candidate?}
\quad
Y:\ \text{does the candidate correspond to independent }L?
\]

Case B (`The balance is $38.35.` without `CLAIM:` under DFC) stays at
\(I/P\): measurement loss. \(E\) is not a semantic NLP oracle.

**Scope (not a bug).** P4-M justifies correspondence claims only in
the class

> typed, recoverable, independently correspondent evidence.

Natural-language descriptions whose denotation requires the world
(“the current live bombard due”) are **outside Level 1**. Do not
enlarge \(E\) to cover them: that turns P4-M into a semantic
evaluator and circularity returns. This is a **scope condition**.

**`NONDETERMINING` \(\neq\) `MISS`.** If \(E=\mathrm{NONDETERMINING}\),
\(Y\) is **undefined**. Do not fail-close completion talk into
correspondence failure.

C2’s fail-closed `score_v2` may still map a unique remainder that is
not gold to status `MISS`. That is a **property of frozen DFC as a
metric instrument**, recorded as C2 evidence. It is **not** M’s
justification theorem. M may *describe* what DFC output, and must
still classify `CLAIM: finished successfully` as parse success +
`NONDETERMINING` + \(Y\) undefined.

Five distinguishable reports (Attack 4’s demand):

| Situation | Report |
|---|---|
| Agent didn’t say it (nothing about \(L\) in \(\mathrm{Observable}_{\tau}\)) | no communicative evidence of \(L\) |
| Agent said something that is not determining for \(L\) | \(E=\mathrm{NONDETERMINING}\); \(Y\) undefined; not `MISS` |
| Determining evidence existed in \(\tau\), \(\mathcal{I}\) did not recover it | **measurement loss** |
| Determining span recovered, \(L\) not independently established | correspondence **not computable**; not Level 1 |
| Determining span recovered, \(L\) independent, match computed | \(Y\in\{\mathrm{HIT},\mathrm{MISS}\}\) |

---

## 4. Orthogonal layer: \(A \neq Y\) (Attack 2)

**Lock. Strengthened, not reversed.**

| Symbol | Reads | Answers |
|---|---|---|
| \(Y\) | \(\mathrm{Observable}_{\mathcal{I}}\) only, and only if \(E=\mathrm{DETERMINING}\) | Correspondence of a determining span to \(L\) |
| \(A\) | Traces + world; ignores last-text; does not call `score_v2` | Independent, conservative call on determining state / execution |
| \(L\) | World, locked without reading \(Y\)’s channel | Independently determined gold |

- Do not set \(Y := A\).
- Do not set \(A := Y\).
- Do not set \(L\) from last-text / \(\mathcal{I}(\tau)\).
- Do not treat \(A=\mathrm{SUCCESS}\) as HIT.
- Do not treat measurement loss as HIT by copying traces into \(Y\).

The gap is the object. Closing it is a repair ticket, forbidden.

---

## 5. Claim hierarchy

**Lock.** Higher levels require their own evidence. Silence is not a
negative verdict. **`CLAIM:` observed \(\not\Rightarrow\) Level 1.**

### Level 0 — No correspondence claim

**Admissible when:** \(E(\tau)\) is not `DETERMINING`, or \(Y\) is
undefined (including circular \(L\)), or \(\mathcal{I}\) recovered
no unique span.

**May say:** correspondence-to-\(L\) is not justified from
\(\mathrm{Observable}_{\mathcal{I}}\). If a determining span sits in
\(\mathrm{Observable}_{\tau}\) only, may additionally say
**measurement loss**.

**May not say:** the agent is unreliable; the agent is reliable; the
task failed; the task succeeded; `MISS`; “the agent made no claim”
when \(\mathrm{Observable}_{\tau}\) contains a determining span.

### Level 1 — Positive correspondence

**Admissible only if all of the following hold**, and \(Y=\mathrm{HIT}\):

\[
\mathrm{Level}_1
\ \Rightarrow\
\begin{cases}
E(\tau)\text{ is DETERMINING (sufficient for }L\text{)}\\
A\text{ / }L\text{ independently determine the target}\\
E(\tau)\text{ is not derived from }A\text{ or from }L\text{'s lock}\\
Y\text{ is correspondence-computable}
\end{cases}
\]

**May say:** the recovered determining span corresponded to the
independently locked determining state.

**May not say:** agent reliability \(=X\); two-sided CC; therefore
execution was correct; therefore \(\mathcal{I}\) captured everything
in \(\tau\).

### Level 2 — Negative correspondence

**Admissible only if** the same independence and sufficiency
conditions as Level 1 hold, and \(Y=\mathrm{MISS}\).

**May say:** a correspondence failure was observed on a determining
span.

**May not say:** `NONDETERMINING` is a correspondence failure;
measurement loss is a correspondence failure; the agent is globally
unreliable; DFC `MISS` on completion-talk is M’s Level 2.

### Level 3 — Two-sided correspondence (sample-level)

**Admissible when:** the **natural** sample contains both polarities
of *correspondence-computable* \(Y\) (HIT and MISS under §5), not
DFC-garbage and not `NONDETERMINING`.

**May say:** two-sided correspondence may be examined on that sample.

**May not say:** the agent passed a metric; `CC \ge 0.90`; D’s W1 is
reversed. Numeric floors are **not** copied from D. Until a later
protocol pre-specifies a floor, the only Level-3 rule is: no
two-sided claim without two-sided *computable* natural evidence.

\(I_{CC}=1\) remains permission, not a verdict on the agent.

---

## 6. Natural profile coordinates

Form remains **interface compliance** under a declared \(\mathcal{I}\),
never named coverage.

\(\mathrm{HIT}^{+}\) and its denominator are **UNRESOLVED**.
Adversarial Attack 5 (partial / component-level claims) is not patched
here. Do not decide

\[
\mathrm{HIT}^{+}
=\frac{n_{\mathrm{HIT}}}{N_{\mathrm{episodes}}}
\]

versus a component-eligible rate until partial-observation semantics
are locked. If a rate is printed in a later protocol, it remains
**not reliability** and **not CC**.

Always report pipeline cells, not a collapsed \(O(\tau)\):

interface, parse, \(E\), \(Y\) if defined, measurement-loss flag,
\(A\) vs \(Y\) descriptive.

\[
\frac{n_{\mathrm{HIT}}}{n_{\mathrm{HIT}}+n_{\mathrm{MISS}}}
\]

opens only if Level 3 is admissible. If not, the fraction is not
named, not published as CC, and not renamed to smuggle CC.

`Abs` / undefined-\(Y\) is missing correspondence measurement, never
converted to HIT or MISS.

---

## 7. Natural vs synthetic (never pool)

**Lock. Unchanged in force.**

**Natural:** \(\tau \rightarrow \mathrm{Observable}_{\tau},\mathrm{Observable}_{\mathcal{I}} \rightarrow \mathcal{M}(\tau,\mathcal{I})\).

**Synthetic:** controlled claim \(\rightarrow\) frozen instrument \(\rightarrow\)
HIT/MISS/ABSTAIN as **instrument discrimination**, not natural
prevalence.

C2/Q3 do not move natural \(I_{CC}\), do not open Level 3, do not
enter \(N\), and do not decide \(E=\mathrm{NONDETERMINING}\) cases.

---

## 8. Central rule

**Lock.** Indexed, so Attack 1 cannot hide in an unqualified Observable.

\[
\mathrm{Justifiable}(C_{\mathcal{I}}\mid\tau,\mathcal{I})
\ \Rightarrow\
\mathrm{EvidenceRequired}(C)
\subseteq
\mathrm{Observable}_{\mathcal{I}}(\tau).
\]

\[
\mathrm{Justifiable}(C_{\tau}\mid\tau)
\ \Rightarrow\
\mathrm{EvidenceRequired}(C)
\subseteq
\mathrm{Observable}_{\tau}(\tau).
\]

If the inclusion fails:

\[
\neg\mathrm{Justifiable}(C\mid\tau,\mathcal{I})
\ \neq\
\mathrm{False}(C).
\]

A Level-0 report under \(\mathcal{I}\) is not “\(C\) is false” and
not “\(\tau\) contained no evidence.”

Still locked:

\[
\text{unobserved failure}\neq\text{observed success},\quad
\text{observed success}\neq\text{identified reliability},\quad
\text{unobserved correspondence}\neq\text{unreliability}.
\]

Plus the amendment’s extra distinction:

\[
\text{instrument non-recovery}
\neq
\text{absence of communication}.
\]

---

## 9. Locked counterexamples (from adversarial review)

These are part of the freeze. They are thought-counterexamples, not
new \(\tau\).

### Attack 1 — measurement loss, not “no claim”

Last-text: `The current live balance is $38.35.` Gold \(L=38.35\).
No `CLAIM:` line. Frozen DFC: `NO_SPAN` / ABSTAIN.

**M now:** \(\mathrm{Observable}_{\tau}\) contains the determining
span; \(\mathrm{Observable}_{\mathcal{I}}\) does not. Report
**measurement loss**. Level 0 *under DFC*. Forbidden: “the agent
made no claim.”

### Attack 2 — CLAIM is not Level 1

\(P=\mathrm{UNIQUE\_SPAN}\), \(E=\mathrm{DETERMINING}\), DFC status
HIT, but \(L\) was copied from last-text.

**M now:** \(Y\) not correspondence-computable. Level 1 **refused**.
Parser-consistency is not correspondence.

### Attack 4 — `CLAIM: finished successfully`

Interface valid, parse `UNIQUE_SPAN`, \(E=\mathrm{NONDETERMINING}\),
\(Y\) **undefined**. Not `MISS`. DFC may emit metric-status `MISS`;
that emission is not M’s Level 2.

Same words without `CLAIM:`: possible DFC interface/parse noncompliance
**and** \(\mathrm{Observable}_{\tau}\) still non-empty. Not semantic
zero.

Attack 3 remains an **acceptable restriction**: testimony that entails
\(L\) only via world/trust is not correspondence-to-\(L\). Attack 5
remains **UNRESOLVED**.

---

## 10. What this freeze still does *not* decide

Experiment is **not** implied. This amendment may still be a dressed-up
tautology; that is the **next checkpoint**, not Phase 1.

Not opened: P4-M Phase 1/2/3/4; new corpus; numeric Level-3 floor;
third model; OSWorld; any edit to frozen instrument hashes
(`a87ac636…fcf3`, `2a028f2b…e8e08`); \(\mathrm{HIT}^{+}\) denominator;
treating DFC `MISS` on `NONDETERMINING` as M’s Level 2.

If an experiment is ever proposed, it must try to **break the pipeline
distinctions** (e.g. a protocol that cannot express measurement loss
without calling the agent silent; a protocol that scores
`NONDETERMINING` as `MISS` and calls that justification). It must not
be “produce natural MISS to identify CC.”

---

## 11. Programme position

```
P1     score ↔ outcome can dissociate
P2     score ↛ selection/triage validity
P3     trajectory → evidence → decision can lose determining content
P4-B   execution ≠ observable evidence
P4-C   declared interface can carry Form
P4-C2  Form high; DFC correspondence high on determining spans; MISS quota fails
P4-D   controlled competitors still yield no natural MISS (W1)
P4-M   which claims are justified — relative to τ vs I, after sufficiency
```

Pipeline (object of this amendment):

\[
\tau
\rightarrow
\text{available evidence}
\rightarrow
\text{instrument-observable evidence}
\rightarrow
\text{semantic sufficiency}
\rightarrow
\text{independent correspondence}
\rightarrow
\text{justified claim.}
\]

---

## 12. Official state

```
P4-D                         FAIL / W1 / CLOSED
CC-natural                   CLOSED
P4-M / Design                ACCEPTED
P4-M / Formalization         AMENDED + ACCEPTED
P4-M / §13                   ACCEPT
P4-M / Non-triviality        PASS
P4-M / E-expressiveness      LOCALIZED, NOT DISSOLVED
P4-M / Typed Soundness       ACCEPT (no-leakage / definitional lemma)
P4-M / NL denotation         OUT OF SCOPE
P4-M / Strong validity       NOT CLAIMED
P4-M / Empirical impl.       NOT STARTED
P4-M / Theory                CLOSED
Experiment                   NOT IMPLIED
Phase 1                      NOT OPENED
```

No code. No corpus. No params. No runner. No commit. No Phase 1.

P4-M theory is **closed**. Empirical implementation does **not**
follow from Typed Soundness. If ever opened, it would ask whether a
concrete \(\mathcal{I}\) instantiates \(I\to P\to E\) under
non-leakage and typed-candidate constraints — a new authorization,
not a continuation of C2/D.

---

## 13. Compact definition (statement, not a theorem)

**Status: ACCEPT as a definition/proposition boundary. Not a validity theorem.**

Chain:

\[
\text{Measurand}
\rightarrow
\text{Observable evidence}
\rightarrow
\text{Typed candidate }E
\rightarrow
\text{Independent correspondence }Y.
\]

\[
\mathcal{M}(\tau,\mathcal{I})
=\{\text{claims whose required evidence is recoverable under }\mathcal{I}
\text{ and non-circular}\}.
\]

§13 does **not** assert that \(\mathcal{M}\) is complete, that
\(\mathcal{M}\) is a valid reliability estimator, or that
\(\mathcal{M}\) is unique/correct relative to an external notion
of justification. Those would be a validity theorem. They are
**OPEN**, not implied by this definition.

**Definition (measurand).** Fix a declared interface \(\mathcal{I}\),
an independently locked gold \(L\) of specification-kind \(k\), a
match \(\leftrightarrow_k\) on the value set of \(k\), and an
adjudicator \(A\) that does not read \(Y\)’s channel. \(A\) is not
an input to \(I,P,E,Y\); it is the orthogonal execution/state call
(\(A\neq Y\)). For a trajectory \(\tau\):

1. \(\mathrm{Observable}_{\tau}(\tau)\): content present in
   last-text and traces (unparsed).
2. \(\mathrm{Observable}_{\mathcal{I}}(\tau)\): what \(\mathcal{I}\)
   extracts. DFC `CLAIM:` is one \(\mathcal{I}\). \(\mathcal{I}\)
   does not take \(\mathrm{value}(L)\).
3. \(P(\tau)\): unique span \(s\) from
   \(\mathrm{Observable}_{\mathcal{I}}\), or none.
4. If no unique \(s\): \(E\) and \(Y\) are **undefined** (not
   `NONDETERMINING`, not `MISS`).
5. If unique \(s\): \(E(s)=\mathrm{DETERMINING}\) iff \(s\) parses
   as a value of \(k\); otherwise \(E=\mathrm{NONDETERMINING}\) and
   \(Y\) is undefined.
6. If \(E=\mathrm{DETERMINING}\) and \(L\) was not taken from the
   evidence channel:
   \(Y(s,L)=\mathrm{HIT}\) iff \(s\leftrightarrow_k L\), else `MISS`.
7. **Measurement loss:** some fragment \(u\) of \(\tau\) parses as
   kind \(k\), and \(u\) is not the span recovered by \(\mathcal{I}\).
   Loss uses \(\mathrm{parse}_k\) and \(\tau\), not \(\mathrm{value}(L)\).

**Definition (justified correspondence).** Level 1 [resp. 2] is
admissible only if \(E=\mathrm{DETERMINING}\), \(Y\) is computable
under independent \(L\), and \(Y=\mathrm{HIT}\) [resp. `MISS`].
`CLAIM:` existence is not sufficient. `NONDETERMINING` is not
`MISS`. No span is not `NONDETERMINING`. Loss is not “no claim.”

**Scope.** Typed \(\wedge\) recoverable \(\wedge\) independently
correspondent evidence. World-dependent descriptions are outside
Level 1.

**Proposition (non-triviality, paper).** \(\mathcal{M}\) is not a
function of \(\Omega=(L,A)\) and is not identical to \(Y\). Shown
by the four-trajectory checkpoint plus the circular twin; not a
general uniqueness theorem.

**Validity question (CLOSED as a thin lemma, not a strong theorem).**

Accepted proposition (**Typed Correspondence Soundness**), to be
named a no-leakage / definitional soundness lemma, not “P4-M is
valid”:

\[
Y=\mathrm{HIT}
\ \Rightarrow\
\bigl[
\mathrm{parse}_k(s)=v\in\mathrm{Val}_k
\ \land\
v\leftrightarrow_k L
\bigr]
\]

with \(L\) independently locked (A1–A4). It does **not** say \(v\)
denotes the true world state. Natural-language denotation is
**out of scope** (finding C): correspondence is guaranteed only
over explicitly typed candidate spaces. Strong validity is
**not claimed**. Draft: `P4_M_VALIDITY_THEOREM_DRAFT.md`.

