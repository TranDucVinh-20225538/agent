# Paper 3 — claim-to-evidence audit (path A)

**Status: writing lock for path A, plus one closed decision rule.** P3-2 is closed.
The paper story is not. Whether a main-track experiment exists is gated by
`P3_COMPARATIVE_GATE.md` (n ≥ 20 task-clusters, defined before effect). No B. No
G3. `R` is not revised. The 4-task support is not re-metric’d.

Working title:

> **The Measurement Pipeline Matters: Diagnosing Reliability Evaluation Failures
> in Computer-Use Agents**

This is a diagnostic methodology paper, not a benchmark paper.

---

## Thesis (one paragraph)

Reliability measurement for computer-use agents is itself a transformation
pipeline. Failures in that pipeline can discard observable evidence, and
interventions at different layers can have different — and sometimes signed —
effects on the resulting reliability measurement.

C10 is an independent diagnostic result. It does not lead the paper.

---

## Reviewer table

If a sentence is not in **Permitted wording**, it is not in the draft.

| Claim | Evidence | Unit | Effect | Limitation | Permitted wording |
|---|---|---|---|---|---|
| Measurement has distinguishable layers | C2–C6, C8 | 134 rows / 57 legs | Multiple failure modes (miss, discard, channel, inert later layer) | One benchmark corpus, one frozen instrument | “The measurement pipeline exhibits distinguishable failure modes” |
| Observable evidence is frequently missed | C2 | 59 R1-positive rows | 39 recall misses (39/59) | Not a false-negative rate of the agent; `text_present` is a recall ceiling | “Recoverable evidence was frequently missed” |
| Fail-closed aggregation discards recovered candidates | C3 | 39 recall misses | 13 M1a; gold was a strict majority in 7/13 | Category-specific; M1 is not specific to misses (also 25/61 ABSENT) | “Fail-closed aggregation discarded recoverable evidence” |
| Earlier-layer failure is inaccessible to later-layer repair | C6 | 134 rows, six configs | R-CMP bit-identical to FROZEN in §3 and §4 | One comparison rule, one archive | “A later-layer comparison repair could not recover upstream abstentions” |
| Layer-specific repairs are not monotonic | C5 | 134 rows, six configs | Signed changes; no config dominates (R-AGG +8 correct / +18 wrong; R-SCOPE destroys 14/20 MATCH) | Repair family fixed before A-10; not a search over repairs | “No tested repair dominated” |
| Measurement intervention can change an ordering statistic | C7 | 4 tasks (8 pairs) | Channel-layer inversion; flash bit-identical, gpt 0.250→0.042 | **n_eff = 1** for frozen ΔSTS; one-sided destruction, not prevalence | “Can change an ordering statistic” |
| This instrument is not recoverable by a locked grounded rule | C10 | 30 label-sensitive components | 9/30 reconstructed; MATCH 20→13; ABSENT unmoved | One locked rule family, one hand-written table; we did not ask whether `R` was better | “This instrument was not recoverable by the locked rule” |

Units: 134 rows = leg × component over 57 legs. 59 R1-positive = MATCH +
RECALL_MISS.

---

## Five contributions

1. Decompose CUA reliability evaluation into observable transformation stages.
2. Empirically diagnose evidence loss and aggregation-induced measurement failure.
3. Show non-monotonicity of layer-specific repairs.
4. Demonstrate, narrowly, that measurement intervention can alter comparative
   ordering.
5. Demonstrate non-reconstructibility of this frozen hand-written instrument
   under a locked corpus-independent grounded specification.

## Forbidden promotions

| Must not become |
|---|
| A new benchmark or a new metric |
| An agent error rate or false-negative estimate |
| A recommended repair to ship |
| Population-level leaderboard instability |
| The paper’s main result being C10, or a verdict on all hand-written instruments |
| A sealed-transfer claim, a G2 rescue, or inter-instrument “R vs frozen” quality |

C10’s defendable sentence, and no other:

> We did not ask whether `R` was better. We asked whether a pre-specified
> corpus-independent grounded rule could reconstruct the existing instrument.
> It could not.

---

## Closed

Gate 0 as a contribution. K4 transfer. G3 / sealed. Enlarging `R`. Path B
(inter-instrument disagreement). A winning repair. “Auditability” as the title
word.

Comparative scale gate: **FAIL** (n = 16 < 20). Wave A 9/12, Wave B 7/16.
Branch closed. C7 existence only. Write path A.
