# P4-M non-triviality checkpoint (paper only)

**Status: CHECKPOINT DONE. Structure-level non-triviality: YES. Theorem: NO.**  
**P4-M freeze not reopened as an experiment. No corpus, code, API, commit.**  
**Question asked:**

> Can two trajectories with identical outcome \(\Omega\) induce different
> justified reliability claims solely because their observable evidence
> differs, while two trajectories with identical observable evidence can
> remain unable to justify correspondence because the evidence is
> non-determining or circular?

If **no**, \(\mathcal{M}\) is a restatement of ground truth
(\(\Omega\Rightarrow\) claim justified, or \(Y\Rightarrow\) claim
justified). If **yes**, \(\mathcal{M}\) has an object other than the
outcome.

**Notation.** \(\Omega=(L,A)\) is the world/adjudicated outcome.
\(Y\) is correspondence **when defined**. The trap is to let
\(\mathrm{DETERMINING}\) mean “matches \(L\).” That would define
evidence from the outcome and collapse the checkpoint. Locked here:

\[
E=\mathrm{DETERMINING}
\iff
\text{the recovered span is a typed candidate for }L
\]

(same kind: money, entity, …). Match-to-\(L\) is \(Y\), a later stage.
`finished successfully` is `NONDETERMINING`. `10.00` when \(L=38.35\)
is `DETERMINING` then \(Y=\mathrm{MISS}\) if independence holds — not
`NONDETERMINING`.

Interface in the four cases is frozen DFC unless noted
(\(\mathcal{I}=\mathcal{I}_{\mathrm{DFC}}\)). Gold \(L=38.35\) is
independent except in the circular twin. \(A=\mathrm{SUCCESS}\) in all
rows (execution can be the same). So **\(\Omega\) is identical** across
A–D.

---

## Four trajectories, one \(\Omega\)

| Case | Agent output | In \(\mathrm{Observable}_{\tau}\) | Under \(\mathcal{I}_{\mathrm{DFC}}\) | \(E\) | \(Y\) | Justified claim |
|---|---|---|---|---|---|---|
| **A** | `CLAIM: 38.35` | determining span | unique span recovered | DETERMINING | HIT | **Level 1** |
| **B** | `The balance is $38.35.` | determining span | no `CLAIM:` → `NO_SPAN` | undefined | undefined | **measurement loss**, Level 0 under DFC; **not** “no claim” |
| **C** | `CLAIM: finished successfully` | completion talk | unique span recovered | NONDETERMINING | **undefined** | **not MISS**; no Level 1/2 |
| **D** | no last-text claim; tool trace contains `38.35` | determining span in traces | I does not extract | undefined | undefined | **measurement loss**; \(A\) may be SUCCESS; \(Y\neq A\) |

Case B under a **different** interface \(\mathcal{I}'\) that extracts a
unique last-text money span (not authorized, not implemented) could
reach Level 1. That is allowed by the freeze and is itself
non-triviality: \(\mathcal{M}(\tau,\mathcal{I})\neq\mathcal{M}(\tau,\mathcal{I}')\)
at fixed \(\tau,\Omega\). Under the frozen DFC that actually exists, B
is loss, not Level 1. Do not pretend DFC recovers prose.

None of the four rows is defined by working backwards from HIT. A and a
wrong `CLAIM: 10.00` share \(E=\mathrm{DETERMINING}\) and split only at
\(Y\). C does not become `MISS` because it failed to equal \(L\); it
never entered correspondence.

---

## Clause 1 — same \(\Omega\), different \(\mathcal{M}\)

A vs B vs C vs D share \(L=38.35\) and \(A=\mathrm{SUCCESS}\).

| Pair | Why \(\mathcal{M}\) differs |
|---|---|
| A vs B | Same communicative content about \(L\); DFC recovers only A. B is loss, not silence. |
| A vs C | Same interface success and unique parse; C’s span is not typed for \(L\). |
| A vs D | Determining span lives in traces; DFC last-text channel empty. Loss, not HIT via \(A\). |
| B vs C | B has determining content in last-text that I misses; C has I-success on non-determining talk. |
| C vs D | Parse success vs no span; neither yields computable \(Y\); reasons differ. |

If \(\mathcal{M}\) were a function of \(\Omega\) alone, these rows would
be the same claim. They are not. **Clause 1: yes.**

This is the measurement-theoretic distinction: a procedure can fail to
observe available evidence without the world-outcome changing, and
without that failure meaning “the agent said nothing.”

---

## Clause 2 — same observable evidence, correspondence still not justified

**Non-determining (identical \(\mathrm{Observable}_{\mathcal{I}}\)).**
Two last-texts `CLAIM: finished successfully`. Same \(I,P,E\).
\(Y\) stays undefined. Level 1/2 refused. Identical evidence, no
justified correspondence claim.

**Circular (identical \(\tau\), identical \(\mathcal{I}(\tau)\)).**
Twin of A: last-text still `CLAIM: 38.35`, but \(L\) was copied from
that line. \(\mathrm{Observable}_{\tau}\) and
\(\mathrm{Observable}_{\mathcal{I}}\) match A. Level 1 **refused**
because \(Y\) is not correspondence-computable. Same evidence in the
trajectory; different justification because independence failed.

If \(\mathcal{M}\) were “whatever \(Y_{\mathrm{DFC}}\) says,” circular
A would still look like HIT and be licensed. M forbids that. If
\(\mathcal{M}\) were “whatever \(\Omega\) says,” A and circular-A
would still both be “correct amount present.” M splits them.

**Clause 2: yes.**

---

## What this does *not* show

- Not a theorem that the pipeline is complete or unique.
- Not recall/precision of any \(\mathcal{I}\) (DFC Form=1 on P4-D is
  historical, not a proof that \(\mathcal{I}\) has useful coverage of
  \(\mathrm{Observable}_{\tau}\)).
- Not that `DETERMINING` is operationally easy; only that it must not
  be defined as match-to-\(L\).
- Not a licence to build \(\mathcal{I}'\) for Case B, nor to retune
  `score_v2`.
- Attack 5 / \(\mathrm{HIT}^{+}\) still UNRESOLVED.

**Potentially non-trivial structure: shown on paper.**  
**Theory of reliability measurement: not proven.**

Tautology would be: “a claim is justified when evidence supports it,”
or \(Y\Rightarrow\) justified claim. The pipeline is stronger because
each arrow can drop information or refuse a later stage, and because
\(\mathrm{Observable}_{\tau}\neq\mathrm{Observable}_{\mathcal{I}}\)
makes loss reportable without flipping \(\Omega\) or inventing `MISS`.

---

## Official reading

```
P4-D          FAIL / W1 / CLOSED
CC-natural    CLOSED
P4-M          DESIGN ACCEPTED / FORMALIZATION AMENDED
Non-trivial?  YES at structure (this checkpoint)
Theorem?      NO
Experiment    NOT IMPLIED
```

P4-M does not need to be “saved” by an experiment. The object of
measurement is not \(\Omega\) and is not DFC-status \(Y\). An
experiment would only be in play later if one asked whether a
*specific* \(\mathcal{I}\) implements the stages without smuggling
\(L\) into \(E\) — a different question, not authorized here.
