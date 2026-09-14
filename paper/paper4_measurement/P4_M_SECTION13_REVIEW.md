# P4-M §13 harsh review

**Role.** Reviewer, not advocate. §13 is **ACCEPT** as a
definition/proposition boundary. This file asks whether that
statement is self-consistent, non-vacuous, and theorem-izable.
It does not prove a validity theorem. No experiment.

The intended object:

\[
\mathcal{M}(\tau,\mathcal{I})
=\{\text{claims whose required evidence is recoverable and non-circular}\}.
\]

Not claimed by §13: completeness; \(\mathcal{M}\) as a reliability
estimator; uniqueness vs an external justification notion.

---

## Self-consistency

**Bugs in the first §13 text (corrected in the freeze, recorded here).**

1. **`else NONDETERMINING`.** The original step 4 mixed “no span”
   with “span that fails kind-parse.” That reopened Attack 4’s type
   error. Correct: no unique \(s\) ⇒ \(E,Y\) **undefined**; unique
   \(s\) that fails \(\mathrm{parse}_k\) ⇒ `NONDETERMINING`.

2. **Measurement loss was not well-defined.** “Typed candidate in
   \(\mathrm{Observable}_{\tau}\)” assumed \(\mathrm{Observable}_{\tau}\)
   already carried \(E\)-objects. Loss is now: some fragment \(u\) of
   \(\tau\) satisfies \(\mathrm{parse}_k(u)\), and \(u\) is not
   \(I(\tau)\). That uses \(k\) and \(\tau\), not \(\mathrm{value}(L)\).
   Residual risk: \(\mathrm{parse}_k\) on all of \(\tau\) is a *second*
   extractor. It must not become a silent \(\mathcal{I}'\) used for
   \(Y\). It is only a **loss flag**.

3. **\(A\) was unused.** It is orthogonal (\(A\neq Y\)), not a
   pipeline input. If a reader treats \(A\) as a hidden argument of
   \(E\) or \(Y\), circularity returns.

4. **\(\leftrightarrow\) was unnamed.** Correspondence is
   \(\leftrightarrow_k\) on the value set of kind \(k\) (canonical
   match for that kind). It must not consult the world beyond \(L\)
   already locked.

After those repairs, the pipeline questions do not coincide:
\(I/P\) recover; \(E\) types; \(Y\) matches independent \(L\).

**Remaining softness (not fatal, not patched into a theorem).**
\(\mathrm{Observable}_{\tau}\) as “content present” is still a
bag of bytes, not a semantics. That is acceptable if no Level 1
claim is licensed from it except via \(\mathcal{I}\) or the loss
flag. If someone scores HIT from \(\mathrm{Observable}_{\tau}\)
directly, §13 is violated.

---

## Non-vacuous?

If “required evidence” *means* “whatever \(\mathcal{I}\) recovered,”
\(\mathcal{M}\) would be a tautology: justified iff the instrument
output a span. §13 is stronger because it can **refuse**:

- recovered non-kind span (`NONDETERMINING`, no \(Y\));
- recovered kind-span when \(L\) was copied from the channel
  (not correspondence-computable);
- HIT-shaped last-text that \(\mathcal{I}\) did not extract (loss,
  not Level 1 under that \(\mathcal{I}\)).

Those refusals can disagree with \(\Omega\) and with raw DFC
status. That is the non-triviality already PASSed. Vacuity would
be \(Y\Rightarrow\) Level 1. Circular twin blocks that.

The set-builder “claims whose required evidence is recoverable
and non-circular” is still close to the central rule. Substance
lives in **what counts as required evidence** (typed candidate,
not “the true value”) and in **which channel** must contain it
(\(\mathcal{I}\), not \(\tau\)).

---

## Theorem-izable?

Do **not** ask “is P4-M valid?” Ask:

> Under what assumptions does the correspondence relation computed
> by P4-M preserve the intended semantic relation between a typed
> candidate and the independently defined measurand?

**Intended relation, inside scope:** \(s\) is a canonical name of
a value in \(\mathrm{Val}_k\), and that value is \(L\).

**Assumptions that do not put \(\mathrm{value}(L)\) into \(I,P,E\):**

| Id | Assumption |
|---|---|
| A1 | \(\mathcal{I},P,\mathrm{parse}_k,E\) do not take \(\mathrm{value}(L)\) as input |
| A2 | \(L\in\mathrm{Val}_k\) is locked from the world, not from \(s\) |
| A3 | Intended match on \(\mathrm{Val}_k\) *is* \(\leftrightarrow_k\) (same canonicalization as the gold lock) |
| A4 | Descriptions requiring world denotation are excluded (scope) |

**Then, when \(E=\mathrm{DETERMINING}\):**
\(Y=\mathrm{HIT}\iff \mathrm{parse}_k(s)\leftrightarrow_k L\).

That biconditional is **almost definitional** given A3 and the
definition of \(Y\). It is a validity theorem only insofar as A1
can **fail** (leakage of \(L\) into parse/accept) and A3 can
**fail** (gold lock and \(\leftrightarrow_k\) disagree). Those are
assumptions about a *procedure*, not about Flash.

It is **not** a theorem that \(Y\) tracks denotation of English in
the world. A4 says that relation is out of scope. If one insists
on that intended semantics, a validity theorem is **impossible
here** without smuggling world/value(\(L\)) into \(E\).

**Verdict.** Theorem-izable as a **thin representation /
no-leakage proposition** under A1–A4. Not theorem-izable as
“justified CUA reliability in general.” Validity theorem remains
**OPEN**: the question is well-posed; existence of a non-thin
theorem is not shown; a theorem that needs NL denotation is
ruled out by scope.

Empirical implementation would only follow **after** A1–A4 are
accepted as the theorem’s assumptions — and would test leakage
(A1) or canonicalization disagreement (A3), not “is the agent
reliable?” That path is **not started** and **not authorized**.

---

## Official reading

```
§13                   ACCEPT (boundary statement)
Self-consistent?      after stated repairs: yes enough to freeze
Non-vacuous?          YES (refusals ≠ Ω, ≠ Y)
Theorem-izable?       only as no-leakage / Val_k representation
                      under A1–A4; otherwise OPEN or impossible
Validity theorem      OPEN
Empirical impl.       NOT STARTED
```
