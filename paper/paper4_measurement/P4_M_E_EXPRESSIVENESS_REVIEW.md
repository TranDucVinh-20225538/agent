# P4-M formal review: can \(E\) be non-circular and expressive?

**Status: E RULE ACCEPTED AS SCOPE-LIMITED. LOCALIZED, NOT DISSOLVED. Validity theorem NOT PROVEN.**  
**Empirical implementation: NOT STARTED. No experiment, corpus, code, API, commit.**  
**Do not modify P4-D, P4-C2, or frozen instruments.**

P4-M has shown an object other than the outcome:

\[
\mathcal{M}(\tau,\mathcal{I})\neq f(\Omega),\qquad
\mathcal{M}(\tau,\mathcal{I})\neq Y,
\]

with \(\Omega=(L,A)\). Circular counterexample: if the evidence channel
contains \(L\) because \(L\) was copied into it, Level 1 is refused even
when text and gold are identical. Evidence is a **candidate**, not “the
span that happens to be correct.”

This review asks the question that can still kill the framework:

> Can \(E\) be defined so that it is not circular *and* still expressive
> enough to represent determining evidence?

---

## 1. Where the tension actually sits

A tempting formulation:

- \(E\) must be **rich**, else all natural evidence becomes measurement
  loss;
- \(E\) must be **independent**, else “evidence = gold” disguises \(Y\).

That pairing **mislocates** richness. Measurement loss (Case B, D in
the non-triviality checkpoint) is a fact about

\[
\mathrm{Observable}_{\tau}(\tau)
\quad\text{vs}\quad
\mathrm{Observable}_{\mathcal{I}}(\tau).
\]

If last-text is `The balance is $38.35.` and \(\mathcal{I}\) is DFC,
the determining span is in \(\tau\) and not in \(I(\tau)\). Widening
**\(E\)** cannot recover a span **\(P\)** never produced. Treating that
as an \(E\)-problem would collapse the pipeline and reopen Attack 1 as
a parser hunt.

**Allocation (lock for this review, not an experiment):**

| Failure | Stage | Not solved by |
|---|---|---|
| Span present in \(\tau\), not extracted | \(\mathcal{I}/P\) → **measurement loss** | making \(E\) richer |
| Unique span recovered, not a candidate for \(L\) | \(E=\mathrm{NONDETERMINING}\) | calling it `MISS` |
| Candidate recovered, \(L\) copied from the channel | correspondence not computable | scoring HIT |
| Candidate recovered, independent \(L\), match | \(Y\in\{\mathrm{HIT},\mathrm{MISS}\}\) | — |

So the real \(E\) question is narrower:

> Given a unique recovered span \(s=P(\tau)\), when is
> \(E(s)=\mathrm{DETERMINING}\) **without using \(\mathrm{value}(L)\)**,
> and without leaving every non-canonical phrasing as
> `NONDETERMINING`?

---

## 2. What \(E\) may use

Let \(L\) have a **value** and a **kind** (in P4: `money_usd`,
`integer`, `entity`, `categorical`). Kind is part of the gold
*specification*, locked from the task/world schema, not from last-text.

| Input | For \(E\)? | Why |
|---|---|---|
| \(\mathrm{value}(L)\) | **No** | That is \(Y\). Using it makes \(E\) a disguise for match |
| \(\mathrm{kind}(L)\) | **Yes** | Scale/signature of the measurand, like knowing the outcome is in dollars |
| World dump / traces | **No** | Would evaluate denotation with the same oracle as \(L\); P4-B / Attack 2 |
| Frozen denylist (“finished”, “done”) | **Yes**, if locked before \(\tau\) | Independence; incomplete recall of non-determining talk |
| Span \(s\) itself | **Yes** | The candidate object |

**Restricted candidate rule (paper, not implemented):**

\[
E(s)=\mathrm{DETERMINING}
\iff
s\text{ parses as a value of }\mathrm{kind}(L).
\]

Then `CLAIM: 38.35` is DETERMINING; `CLAIM: 10.00` is also DETERMINING
(match is \(Y\)); `CLAIM: finished successfully` is NONDETERMINING;
prose not recovered by \(P\) never reaches \(E\).

This \(E\) is **non-circular** for P4’s actual construct: gold is a
canonical typed value, not a description. It is **expressive enough
for recovered canonical spans**. It is **not** a recall theorem for
natural language.

---

## 3. The kill regime

\(E\) dies as a justification primitive if determining evidence in
\(\tau\) is **only** a description whose denotation needs the world:

> “I posted the current live bombard due.”
> “I selected the item the system marked current.”

To mark those DETERMINING one must compute what “current live bombard
due” *is*. That computation uses the same world as \(L\). Then

\[
E(s,\mathrm{world})\approx
\mathbf{1}[\mathrm{denotation}(s,\mathrm{world})=L]
\]

which is \(Y\) with extra steps. Independence of \(E\) from
\(\mathrm{value}(L)\) is lost even if \(L\) was not literally copied
into last-text.

Refusing all such descriptions keeps \(E\) independent and dumps them
to measurement loss or `NONDETERMINING`. That is **acceptable** as a
restriction of the *construct* (correspondence of a typed span to
canonical \(L\)). It is **fatal** if P4-M claims to justify
correspondence for every semantically adequate English sentence.

**P4-M’s object, honestly scoped:** justified claims about
**recovered typed candidates** vs independently locked canonical \(L\),
plus reporting of measurement loss when \(\mathcal{I}\) is narrower
than \(\tau\). Not: a general theory of meaning in CUA traces.

---

## 4. Does this solve the tension?

**For the P4 construct (canonical \(L\), frozen DFC as one
\(\mathcal{I}\)): tension is *localized*, not dissolved.**

- Non-circular \(E\): yes, if \(E\) is typed parse of \(s\) using
  \(\mathrm{kind}(L)\) only.
- Expressive \(E\): yes for spans \(P\) actually returns; **no**
  obligation for \(E\) to see prose or traces. That is \(\mathcal{I}\).
- Natural prose/descriptions: remain loss or `NONDETERMINING`, not
  HIT-by-oracle. That is a **scope limit**, not a validity theorem.

**Validity theorem still NOT PROVEN.** We have not shown that this \(E\)
is the unique non-circular rule, nor that any implemented \(\mathcal{I}\)
has useful coverage of \(\mathrm{Observable}_{\tau}\), nor that kind-from-
spec cannot leak value in some schemas.

What would kill P4-M on paper next:

1. Any \(E\) that must consult \(\mathrm{value}(L)\) or world denotation
   to classify DETERMINING; or
2. Expanding \(E\) to read \(\mathrm{Observable}_{\tau}\) directly so
   that Case B becomes Level 1 without a new, pre-declared
   \(\mathcal{I}\) — that smuggles parser retune into sufficiency.

Neither is authorized. Frozen `score_v2` stays the DFC instance of
\(\mathcal{I}\), not a definition of \(E\). C2 may still emit metric
`MISS` on `CLAIM: finished`; M still treats that as
`NONDETERMINING`, \(Y\) undefined.

---

## 5. Official state

```
P4-D                    FAIL / W1 / CLOSED
CC-natural              CLOSED
P4-M / Design           ACCEPTED / FORMALIZATION AMENDED
P4-M / Non-triviality   PASS
P4-M / Validity theorem NOT PROVEN
P4-M / Empirical impl.  NOT STARTED
E-tension               LOCALIZED (typed candidate vs denotation)
                        not solved as a general NL theory
Experiment              NOT IMPLIED
```

Next theoretical question, if any: whether **kind-only \(E\)** is
accepted as the construct’s sufficiency rule, with description-like
spans explicitly out of Level 1. That is still a freeze amendment,
not Phase 1.
