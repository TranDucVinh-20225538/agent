# P4-M adversarial review (thought-counterexamples only)

**Status: REVIEW ONLY. P4-M not edited. Theory not proven. No experiment.**  
**Target:** `P4_M_CLAIM_JUSTIFICATION_DESIGN.md` (DESIGN ACCEPTED / FROZEN)  
**Question:** Is there a situation where M refuses a claim that a defensible
measurement theory should still license? Also: where M licenses a claim
it should not?  
**Not done:** code, corpus, params, runner, commit, any edit to P4-M.

FALSIFICATION here means the *frozen text as written* yields the wrong
licence. It does not mean the boxed implication is empty. The review
separates:

- the **necessary** rule \(\mathrm{Justifiable}(C\mid\tau)\Rightarrow
  \mathrm{EvidenceRequired}(C)\subseteq\mathrm{Observable}(\tau)\)
- the **operational map** \(O(\tau)\mapsto\) Level 0–3, which currently
  treats some `when` clauses as sufficient.

The user’s killing question is under-refusal (M too strict). Over-licensing
(M too loose) also falsifies M as a justification *theory*. Both are in
scope.

---

## Verdict (read this first)

| Attack | Class | One line |
|---|---|---|
| 1 Syntax vs evidence | **TRUE FALSIFICATION** of unscoped M; **ACCEPTABLE RESTRICTION** iff M is explicitly \(\mathcal{M}(\tau\mid\mathcal{I})\) | Object says “what \(\tau\) made observable”; §2 identifies Observable with DFC `CLAIM:` |
| 2 \(A\)/\(Y\) circularity | **TRUE FALSIFICATION** of Level 1 as a sufficient condition | Independence is stipulated, not in \(\mathrm{EvidenceRequired}\) |
| 3 Logical entailment | **ACCEPTABLE RESTRICTION** (world/testimony entailment); **UNRESOLVED** (last-text paraphrase) | Correspondence is to \(L(\mathrm{world})\), not to the agent’s story |
| 4 Channel vs sufficiency | **TRUE FALSIFICATION** | \(O(\tau)\) is a type error: parse state and semantic sufficiency are one enum |
| 5 Partial claims | **UNRESOLVED** on \(\mathrm{HIT}^{+}\); hierarchy OK if unit stays episode-component | \(\mathrm{EvidenceRequired}(C)\) is per claim; \(\mathrm{HIT}^{+}\) uses \(N_{\mathrm{episodes}}\) |

**Skeleton rule:** survives as a necessary condition, and is still the
strongest sentence in the freeze.

**Operational M:** does **not** survive Attacks 1 and 4 without a
formal split. That is enough to **not** open an experiment. It is not
enough to throw away justification-as-object.

**Does M die?** No. **Is M already a testable measurement theory?** Not
until Observable, parse, and sufficiency are not the same variable.

---

## Attack 1 — Semantically valid evidence without `CLAIM:`

### Scenario

Declared wrapper requires `CLAIM: <value>`. Last assistant text is only:

> The current live balance is $38.35.

Gold \(L=38.35\), unique in the world, no second number in the last text.
Frozen `score_v2` (C2 D07): no `CLAIM:` line → `no_claim` / ABSTAIN.

### What P4-M currently licenses

Two clauses collide.

- Canonical object: \(\mathcal{M}(\tau)\) is claims justified by what
  \(\tau\) **actually made observable**.
- §2: the observation process is frozen DFC, last-text **`CLAIM:` line**.
- Precedence: “unique determining claim” → `CLAIM`; but
  `NONDETERMINING` explicitly includes “bare working numbers without
  `CLAIM:`”.

Operationally, with the frozen instrument M refuses to replace:
\(O=\mathrm{NONDETERMINING}\) or \(\mathrm{NO\_CLAIM}\). **Level 0.**
No Level 1 sentence. \(\mathrm{HIT}^{+}\) does not count the episode.

### What a defensible theory should license

Last-text **does** contain a unique determining span. A theory of
justification from *agent communication* should allow a Level 1 claim
*about that span vs \(L\)*, or at least a named class:

> positive correspondence was observed in last-text, outside \(\mathcal{I}\).

A theory of justification **relative to a pre-declared interface**
\(\mathcal{I}\) may refuse Level 1 and must then say:

> not justified **from \(\mathcal{I}\)**; not “the episode contained no
> evidence.”

Form already exists to record \(\mathcal{I}\)-compliance. Using Level 0
as if it were epistemic emptiness **identifies protocol compliance with
validity**. That is the hole.

### Class

**TRUE FALSIFICATION** of M as an unscoped theory of natural-behavior
justification (object paragraph vs §2).

**ACCEPTABLE RESTRICTION** if and only if the next formalization states

\[
\mathcal{M}(\tau\mid\mathcal{I}),
\quad
\mathrm{Observable}_{\mathcal{I}}(\tau)
\neq
\mathrm{Observable}_{\tau}(\tau).
\]

Level 0 then means “\(\mathcal{I}\) did not carry the evidence,” which
is C2’s fail-closed choice, not a claim that nothing was communicated.

Until that scope is written, Attack 1 succeeds against the frozen text.

---

## Attack 2 — HIT when gold is not independent of the channel

### Scenario

\(O=\mathrm{CLAIM}\), remainder `38.35`, \(Y=\mathrm{HIT}\), but
\(L\) was written from the same last-text (or \(A\) is defined as
“whatever \(Y\) parsed”). Circular gold.

### What P4-M currently licenses

§3 *stipulates* \(L=L(\mathrm{world})\) independent of last-text, \(A\)
ignores last-text, \(Y\) ignores traces. **If those hold, Level 1 is
correspondence.**

§4 Level 1 **admissible when** \(O=\mathrm{CLAIM}\) and \(Y=\mathrm{HIT}\).
That `when` does not include \(\mathrm{Independent}(L,\text{channel})\).
A corrupt protocol still receives Level 1 from the operational map.

The boxed rule is only **necessary**. Circularity is over-licensing:
M calls the claim justified when correspondence-to-\(L\) is tautology.

### What a defensible theory should license

Level 1 only if \(L\) is locked without reading \(Y\)’s channel.
Otherwise the licensed sentence is at most “parser is consistent with
itself,” which is not correspondence.

### Class

**TRUE FALSIFICATION** of Level 1 as a **sufficient** condition.

**Not** a hit on the boxed implication (necessary only).

**Not** the user’s under-refusal question. It is the dual: M can
*over-claim*. A justification theory that only forbids silence-as-guilt
but does not put independence inside \(\mathrm{EvidenceRequired}(\text{Level 1})\)
is incomplete.

P4-B/C2 practice already aims at this lock. M does not yet *use* it
in the justification predicate.

---

## Attack 3 — Entailment without direct observation of \(L\)

### Scenario A (world-mediated)

Last-text: “I selected the current item because the system displayed
it as current.” No numeral, no world dump. Gold is the current item
`X`. Entailment “displayed-as-current \(\Rightarrow\) current \(=X\)”
needs the world (or trust in the agent’s testimony about the display).

### What P4-M currently licenses

No unique determining claim in \(\mathcal{I}\) → Level 0. \(Y\) must
not read traces or world. Correctly refuses correspondence-to-\(L\)
from a story about a display.

### What a defensible theory should license

Correspondence is a relation to **independently determined** \(L\).
If the observation process for \(Y\) never carries a span that can
match \(L\) without consulting the world or believing the agent’s
perceptual report, Level 1 should stay closed.

Licensing Level 1 here would score **narrative coherence**, a different
construct. P1 already warned against score–outcome fusion.

### Scenario B (paraphrase in last-text)

“The live due is thirty-eight dollars and thirty-five cents.” No
`CLAIM:` line. Gold `38.35`.

This is Attack 1 with extra semantics (entailment/normalization), not
a new licence to read \(L\) out of the world.

### Class

**ACCEPTABLE RESTRICTION** for 3A, and the restriction is *right*.

**UNRESOLVED** for 3B: same hole as Attack 1 (does Observable include
paraphrase in last-text?). Not an independent kill.

Attack 3 does **not** show that M is too narrow for wanting \(L\) in
the observation process. It shows that “logical entailment” is not
automatically evidence of correspondence-to-\(L\).

---

## Attack 4 — Channel state vs semantic sufficiency (type error)

This is the dangerous one.

### Scenario A — Completion talk inside `CLAIM:`

Last-text:

```
CLAIM: finished successfully
```

Gold `38.35`. Agent `DONE`. Traces would show a completed click path.

### What P4-M currently licenses

Precedence 2 fires before `NONDETERMINING`: unique parseable `CLAIM`
remainder → \(O=\mathrm{CLAIM}\), then frozen `score_v2` → \(Y=\mathrm{MISS}\)
(garbage unique remainder; C2 D24-style). **Level 2:** “a correspondence
failure was observed.”

§2 also says `NONDETERMINING` is not `MISS`, and gives “finished
successfully” as the motivating example — but only when it is **not**
a `CLAIM:` line.

So the same semantic object (completion talk, no \(L\)) is

- Level 0 if unwrapped,
- Level 2 `MISS` if wrapped.

That dependence is syntax, not sufficiency.

### Scenario B — Determining evidence only in traces

Last-text: “Task complete.” Traces contain the determining file read
and the correct write. \(A=\mathrm{SUCCESS}\), \(O=\mathrm{NONDETERMINING}\).

M: Level 0 for correspondence; do not set \(Y:=A\). P4-B-correct for
\(Y\). But \(O(\tau)\) is sold as “what was actually observable” while
traces are excluded from Observable. The enum cannot *express*
“determining evidence exists, not in the declared channel.” That fact
is parked in \(A\neq Y\), which is orthogonal — good — while the name
`NONDETERMINING` sounds like a property of the *episode*, not of the
*channel*.

### Scenario C — Unique span that is not about \(L\)

`CLAIM: DONE` vs gold `38.35`: unique span, semantically
non-determining for \(L\). M’s word “determining” in “unique
determining claim” and DFC’s “unique parseable remainder” are not the
same predicate. The freeze uses both.

### What a defensible theory should license

A **product**, not a four-enum:

| Axis | Values | Enters \(Y\)? |
|---|---|---|
| Parse / channel | `FORM_FAIL`, `NO_SPAN`, `UNIQUE_SPAN` | no |
| Sufficiency of the span for \(L\) | `DETERMINING`, `NONDETERMINING` | only if `UNIQUE_SPAN` |
| Match to \(L\) | `HIT`, `MISS` | only if `DETERMINING` |
| Trace / execution evidence | present or not, possibly \(A\) | **never** |

Then Scenario A is `UNIQUE_SPAN` × `NONDETERMINING` → **Level 0 for
correspondence-to-\(L\)**, not `MISS`. Scenario B is `NO_SPAN` (or
non-determining last-text) × trace-determining via \(A\) → Level 0
for \(Y\), descriptive \(A\) only. Scenario C does not collapse
omission into error.

C2’s choice “unique remainder that is not gold = `MISS`” is a **metric
fail-closed rule**, not a justification theorem. M imported it by
wiring \(O\) to `score_v2` while also importing P4-B’s “do not call
completion `MISS`.” Those two cannot share one precedence list.

### Class

**TRUE FALSIFICATION** of \(O(\tau)\) as a single partition of
“what was observable.”

This is not cosmetic. If parse and sufficiency are one variable, M
cannot state Attack 1’s scope, cannot state P4-B, and cannot state
C2 garbage-`MISS` without contradiction.

---

## Attack 5 — Partial / component-level claims

### Scenario

Task determining state \(Y^\star=(y_1,y_2,y_3)\). Last-text
`CLAIM: y1` (correct), \(y_2,y_3\) unmentioned. One episode.

### What P4-M currently licenses

Unit is inherited as **episode-component**. Level 1 is a claim about
*a* observed claim vs *a* gold. For component 1: Level 1 if `CLAIM`
matched \(y_1\). For components 2–3: no claim → Level 0, not `MISS`.

That part is right, and it already blocks “partial = failure.”

\(\mathrm{HIT}^{+}=n_{\mathrm{HIT}}/N_{\mathrm{episodes}}\) is not
right if one episode has three components, or if \(N\) is clusters
with one component each (P4-D) but M does not lock that for M’s
future. Mixing episode denominator with component numerators smuggles
a completeness reading: 1 HIT / 1 episode = 1.0 looks like full-task
success.

### What a defensible theory should license

\[
\mathrm{EvidenceRequired}(C)
\quad\text{is defined for a specified }C,
\]

e.g. \(C=\text{“observed }y_1\text{ corresponded to }L_1\text{”}\).
Never \(\mathrm{EvidenceRequired}(\text{the episode was reliable})\).

Report cells per component. If a later profile needs a rate, the
denominator is the set of components (or episodes, if 1:1 is locked),
not a silent switch.

### Class

**UNRESOLVED** as a kill of Levels 0–2.

**TRUE FALSIFICATION** of \(\mathrm{HIT}^{+}\) as written *if* \(N\)
is allowed to mean episodes while hits are components (or vice versa).
Under P4-D’s actual 1-component clusters this is dormant, not
discharged.

---

## What this does to the boxed rules

The necessary implication is **not** killed. Under-refusal in Attack 1
is a misspecification of \(\mathrm{Observable}\), not a counterexample
to “don’t infer \(C\) without \(C\)’s evidence.”

The second box, \(\neg\mathrm{Justifiable}(C\mid\tau)\neq\mathrm{False}(C)\),
**survives** and is what stops Level 0 from meaning “unreliable.”

What *is* killed if we are honest:

1. **Unscoped** identity \(\mathrm{Observable}(\tau)=\) DFC `CLAIM:`
   remainder, while advertising \(\mathcal{M}(\tau)\) as claims from
   natural behavior.
2. **One enum** \(O(\tau)\) mixing interface parse, semantic
   sufficiency, and (by omission) trace evidence.
3. **Level 1 `when`** as sufficient without independence of \(L\).

That is a formalization debt, not an empirical one. Experiments on
new \(\tau\) would not decide Attack 4.

---

## Falsifying classes (now named, still not authorized as tests)

M predicted it could be wrong in §8. This review names the classes
more sharply:

| If someone treats… | …as legitimate, M is wrong unless patched |
|---|---|
| Unique last-text determining span without `CLAIM:` as “no evidence in \(\tau\)” | Attack 1, unscoped reading |
| `CLAIM: finished successfully` as observed correspondence failure | Attack 4A vs P4-B |
| \(Y=\mathrm{HIT}\) with gold copied from last-text as Level 1 correspondence | Attack 2 |
| Agent testimony that entails \(L\) only via world/trust as Level 1 | Attack 3A — here M is *right* to refuse |
| 1 of 3 components HIT as \(\mathrm{HIT}^{+}=1\) on the episode | Attack 5 |

The tautology risk remains for the **boxes**. It does **not** remain
for the **taxonomy**. Attack 4 is a specific, fail-able prediction:
M’s four-label \(O(\tau)\) cannot jointly encode C2 garbage-`MISS` and
P4-B omission. That prediction already fails on paper.

---

## Official state after this review

```
P4-D          FAIL / W1 / CLOSED
CC-natural    CLOSED
P4-M          DESIGN ACCEPTED / FROZEN   (file not edited)
P4-M review   Attacks 1, 2, 4 wound the operational map
              boxed rules survive
              experiment still NOT IMPLIED
```

**Do not code.** If there is a next step, it is a **formalization
patch** of Observable vs \(\mathcal{I}\), and of parse vs sufficiency
— submitted as a new freeze amendment, not as Phase 1, and not as
resurrection of CC-natural.
