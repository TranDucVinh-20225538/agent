# P4-M validity theorem draft (paper only)

**Status: ACCEPT as Typed Correspondence Soundness (no-leakage lemma). Strong validity NOT CLAIMED. NL denotation OUT OF SCOPE. Empirical NOT STARTED.**  
**Question (locked):** When does P4-M correspondence preserve the
intended relation between a typed candidate and the independently
defined measurand?  
**Not asked:** Is P4-M a valid reliability estimator? Is \(\mathcal{M}\)
complete? Does DFC recover natural language?

After the draft: an AAMAS-style review of the same text.

---

## 1. Definitions inherited from §13

Fix interface \(\mathcal{I}\), specification-kind \(k\), value set
\(\mathrm{Val}_k\), parse \(\mathrm{parse}_k:\mathrm{String}\to
\mathrm{Val}_k\cup\{\bot\}\), match \(\leftrightarrow_k\subseteq
\mathrm{Val}_k\times\mathrm{Val}_k\), gold \(L\in\mathrm{Val}_k\),
trajectory \(\tau\).

- \(s=P(I(\tau))\) is a unique recovered span, or absent.
- \(E(s)=\mathrm{DETERMINING}\) iff \(s\) exists and
  \(\mathrm{parse}_k(s)=v\neq\bot\). Write \(v=\mathrm{parse}_k(s)\).
- If no unique \(s\): \(E,Y\) undefined (not `NONDETERMINING`).
- If unique \(s\) and \(\mathrm{parse}_k(s)=\bot\):
  \(E=\mathrm{NONDETERMINING}\), \(Y\) undefined.
- If \(E=\mathrm{DETERMINING}\) and \(L\) is not taken from the
  evidence channel:
  \(Y=\mathrm{HIT}\) iff \(v\leftrightarrow_k L\), else `MISS`.

**Intended relation, inside §13 scope.** \(v\in\mathrm{Val}_k\) is
the typed reading of \(s\), and \(\leftrightarrow_k\) is the
pre-declared match on \(\mathrm{Val}_k\). *Not* “\(s\) denotes \(L\)
in the world under English.”

**Reported HIT** means: the procedure outputs \(Y=\mathrm{HIT}\)
(Level 1 admissible). **Sound w.r.t. \(L\)** means:
\(v\leftrightarrow_k L\) with this independently locked \(L\).

---

## 2. Assumptions and audit

### 2.1 A1–A4 (from §13 review)

| Id | Statement |
|---|---|
| **A1** | \(\mathcal{I}\), \(P\), \(\mathrm{parse}_k\), \(E\) do not take \(\mathrm{value}(L)\) as input |
| **A2** | \(L\in\mathrm{Val}_k\) is locked from the world / gold spec, not from \(s\) |
| **A3** | The intended match on \(\mathrm{Val}_k\) *is* \(\leftrightarrow_k\) (same canonicalization as the gold lock) |
| **A4** | Spans whose reading requires world-dependent denotation are excluded; they never become \(E=\mathrm{DETERMINING}\) via this \(E\) |

### 2.2 Bucketed audit

**Measurement**

| Assumption | Class |
|---|---|
| \(\mathcal{I}\) reads only the declared channel of \(\tau\) (DFC: last-text `CLAIM:`), not \(\mathrm{value}(L)\), not \(A\) | **Design constraint.** Empirically auditable on an implementation (hash / no gold in parser). Not a semantic axiom. |
| \(P,E\) do not receive \(\mathrm{value}(L)\) (A1) | **Design constraint.** Can fail if code branches on gold. |
| Unique-span parse is a function of \(I(\tau)\) only | **Design constraint.** |

**Semantic**

| Assumption | Class |
|---|---|
| \(k\) and \(\mathrm{Val}_k\) are given by the task spec | **Definition / construction spec**, not estimated from \(\tau\) |
| \(\mathrm{parse}_k(s)=v\) is “\(s\) is a well-formed name in \(\mathrm{Val}_k\)” | **Definition** of typed candidate. Does *not* say \(v\) is the world denotation of a description |
| \(\leftrightarrow_k\) is frozen before \(\tau\) (A3) | **Definition** of the match. If gold lock uses a different canonicalizer, A3 fails as **construction error**, not as agent error |

**Construction**

| Assumption | Class |
|---|---|
| \(L\) is not generated from the evidence channel (A2) | **Design / construction constraint.** Circular twin is A2 failure |
| Observation / \(\mathcal{I}\) / \(\mathrm{parse}_k\) / \(\leftrightarrow_k\) not edited after seeing \(L\) or \(\tau\) | **Design constraint** (anti-retune). Empirical if someone patches `score_v2` on last-texts |
| Kind \(k\) is not chosen by looking at \(s\) to make \(E\) fire | **Design constraint.** If \(k\) is fit on \(\tau\), A1-adjacent leakage |

**Not assumed (and must not sneak into the proof):**

- \(\mathcal{I}\) extracts “the right” span (recall / completeness).
- \(v\) denotes the world object that English speakers would pick.
- \(A=\mathrm{SUCCESS}\).
- DFC `CLAIM:` is the only possible \(\mathcal{I}\).
- \(\mathrm{HIT}^{+}\) or CC-natural.

---

## 3. Theorem candidate and proof attempt

**Proposition (Typed Correspondence Soundness).**  
Assume A1–A4. Suppose the procedure reports \(Y=\mathrm{HIT}\). Then
there exists \(v=\mathrm{parse}_k(s)\in\mathrm{Val}_k\) with
\(v\leftrightarrow_k L\), where \(L\) is the independently locked
measurand. In particular, a reported HIT is sound with respect to
\(L\) *under \(\leftrightarrow_k\)*.

**Not claimed.** Completeness (MISS whenever the “true” relation
fails; recovery of every typed fragment in \(\tau\)). Soundness of
DFC garbage-`MISS` on `NONDETERMINING` text. Reliability of the
agent. Identity of \(Y\) with world denotation.

### Proof attempt

1. Report \(Y=\mathrm{HIT}\) is defined only when
   \(E=\mathrm{DETERMINING}\) and \(L\) is not taken from the
   evidence channel (§13.6). So A2 holds in this branch (else \(Y\)
   undefined, not HIT).
2. \(E=\mathrm{DETERMINING}\) ⇒ unique \(s\) and
   \(\mathrm{parse}_k(s)=v\neq\bot\) (§13.5). So \(v\in\mathrm{Val}_k\).
   By A1 this parse did not receive \(\mathrm{value}(L)\).
3. \(Y=\mathrm{HIT}\) ⇒ \(v\leftrightarrow_k L\) (§13.6).
4. A3: \(\leftrightarrow_k\) *is* the intended match on
   \(\mathrm{Val}_k\). Therefore HIT is sound w.r.t. independent
   \(L\) under that match.
5. A4 is used only negatively: no other path injects a
   world-denoting description into \(E=\mathrm{DETERMINING}\). If A4
   were dropped, step 2 could hold for a description whose
   \(\mathrm{parse}_k\) was faked by world lookup — forbidden.

**What the proof did *not* use:** that \(s\) is the span a human
would pick; that \(v\) is the amount in the guest file; that
\(\mathcal{I}\) has high recall.

**Boundary of validity (the point of the attempt).**  
The proof **does not need** “the parser extracts the right thing”
for *soundness of HIT*. It **does** need A1 (parser not gold-aware)
and A3 (\(\leftrightarrow_k\) is the intended \(\mathrm{Val}_k\)
match). It **cannot** get “the typed candidate really denotes the
world value” without a denotation function \(d(\cdot,\mathrm{world})\).
That function is **out of scope** (A4). So:

- Soundness under \(\leftrightarrow_k\): proof goes through, and is
  **thin**.
- Soundness under world denotation: **not proved**; requiring it
  would smuggle world/\(\mathrm{value}(L)\) into \(E\).

Dual (same hypotheses): if \(Y=\mathrm{MISS}\), then
\(\neg(v\leftrightarrow_k L)\). Same thinness. Completeness relative
to fragments in \(\tau\) that \(\mathcal{I}\) did not recover is
**not** proved (measurement loss).

---

## 4. Counterexample search / failure conditions

Goal: \(\tau\) with \(E(s)=\mathrm{DETERMINING}\) such that the
proposition wants HIT to be sound, but correspondence is “really”
wrong.

### 4.1 Does not kill

| \(\tau\) | Why it fails to kill |
|---|---|
| \(L=38.35\), \(s=\texttt{38.35}\), \(k=\mathrm{money}\) | If \(\leftrightarrow_k\) is the frozen money match, HIT is correctly sound |
| \(L=X\), \(s=Y\), \(k=\mathrm{entity}\), \(X\neq Y\) | \(E=\mathrm{DETERMINING}\), \(Y=\mathrm{MISS}\). Proposition talks about **HIT** soundness. MISS is the right output |
| \(s=\texttt{finished successfully}\) | \(\mathrm{parse}_k=\bot\), \(E=\mathrm{NONDETERMINING}\), \(Y\) undefined. Antecedent “reports HIT” is false |
| Prose `The balance is $38.35.` under DFC | No unique DFC span (typical). \(Y\) undefined; loss flag possible. No HIT to be unsound |
| Circular \(L:=s\) | A2 fails; \(Y\) not computable; no HIT |

### 4.2 Kind mismatch

\(L=38.35\) (money), but \(k\) declared `integer`. Then
\(\mathrm{parse}_{\mathrm{integer}}(\texttt{38.35})=\bot\) (or truncates,
if a bad parser). If \(\bot\): not DETERMINING, theorem idle. If a
leaky integer parser yields \(38\) and someone reports HIT vs money
\(L\): **A3 or construction of \(k\)** failed (kind of \(L\) is not
the kind used by \(E\)). Not a counterexample *under* A1–A4.

### 4.3 Attacks that kill the *intended-denotation* reading, not the proposition

| Attack | Effect |
|---|---|
| \(s=\texttt{38.35}\) names a *different* world amount than the file’s live due, but \(L\) was locked as `38.35` from that file incorrectly | A2 (gold lock) failed. Theorem’s \(L\) is whatever was locked, not “true world” |
| \(s\) is a homoglyph / extra zero that \(\leftrightarrow_k\) treats as equal to \(L\) | If that is the frozen \(\leftrightarrow_k\), HIT is sound *under A3*. If a stricter intended match disagrees, **A3 failed** (two canonicalizers) |
| Description “the current due” scored DETERMINING by looking up the world | **A4 / A1 failed.** This is the fundamental limit, not a hole *in* the proposition |

### 4.4 What would actually falsify the proposition

A procedure that outputs \(Y=\mathrm{HIT}\) while
\(\neg(v\leftrightarrow_k L)\) or while \(v\) was chosen using
\(\mathrm{value}(L)\). That is an **implementation leak** (A1) or a
**mis-coded \(Y\)** (not computing \(\leftrightarrow_k\)). It is not
a natural-language counterexample inside A1–A4.

**Search result.** No counterexample inside A1–A4 to *Typed
Correspondence Soundness* as stated. Counterexamples to “HIT means
the world denotation is \(L\)” exist as soon as A4 is dropped.
That is **failure condition C**, not a failed proof of the thin
proposition.

---

## 5. AAMAS-style review

**Summary.** The draft proves that a HIT, *as defined*, coincides
with \(\leftrightarrow_k\) on an independently locked \(L\). A
reviewer will call this close to definitional. That objection is
**correct** and should be owned. The contribution, if any, is the
**boundary**: what must *not* be used (value of \(L\), world
denotation, recall of \(\mathcal{I}\)) for even this much to hold,
and the explicit **non-theorem** that P4-M does not validate
arbitrary NL evidence.

**Strengths.**

- Question is specific; not “is the metric valid?”
- A1–A4 are sorted (design vs definition vs construction).
- Proof does not smuggle “parser found the right span.”
- Kill search separates MISS, NONDETERMINING, loss, circularity
  from HIT-unsoundness.
- Finding C is stated as a feature of scope, not a TODO for NLP.

**Weaknesses / likely reviewer kills.**

1. **Triviality.** HIT \(\Rightarrow v\leftrightarrow_k L\) follows
   from the definition of \(Y\) plus A3. A1–A2 only exclude extra
   paths to HIT. Call it a *sanity / no-leakage lemma*, not a
   validity theorem of CUA reliability.
2. **A3 is the intended relation.** Then “preserves the intended
   relation” is true by naming \(\leftrightarrow_k\) the intended
   relation. The interesting content is A1 (no gold in \(I,P,E\)).
3. **No completeness.** Measurement loss and DFC non-recovery are
   untouched. A reliability paper’s reviewers will ask for that
   and must be answered with “out of theorem, in scope of
   \(\mathcal{I}\).”
4. **\(\mathrm{parse}_k\) on all of \(\tau\) for loss** is a second
   extractor. Fine if it never feeds \(Y\); poisonous if it does.
5. Frozen DFC `score_v2` may emit `MISS` on `CLAIM: finished`.
   The proposition does not license that as P4-M Level 2. Dual
   papers (C2 vs M) will confuse readers unless kept apart.

**Recommendation.** Do **not** sell this as “P4-M is valid.” Sell
as: *under A1–A4, HIT is a sound \(\mathrm{Val}_k\)-match to
independent \(L\); it is not a denotation theorem.* If the
community needs denotation, P4-M **refuses** (finding C), which
is the result.

---

## 6. Decision on experiment (not authorized)

| Path | Reading | Experiment? |
|---|---|---|
| **A** | Thin soundness proof **passes** | Only later, for implementability / A1 audit of a *specific* \(\mathcal{I}\). Not to “prove the framework exists.” |
| **B** | Proof fails because recovery/\(I,P\) underspecified | Formalize \(I,P\) more. Not reached: soundness did not need recall |
| **C** | Proof cannot reach NL denotation | **Fundamental scope limit.** P4-M guarantees correspondence only on explicitly typed candidate spaces |

**This draft: A for the stated proposition, C for the stronger
intended-semantics many readers will want.** C is the scientifically
honest “boss” outcome. Do not widen \(E\) to kill C.

```
Typed Correspondence Soundness   ACCEPT (thin; no-leakage lemma)
Denotation validity              OUT OF SCOPE (finding C)
Strong validity                  NOT CLAIMED
P4-M theory                      CLOSED
Empirical implementation         NOT STARTED
Phase 1                          NOT OPENED
```
