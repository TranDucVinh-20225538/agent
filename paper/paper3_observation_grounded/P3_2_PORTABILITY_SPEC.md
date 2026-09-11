# P3-2 — Instrument portability and cross-corpus validation

**Status: pre-registration, unfrozen draft. Nothing has been implemented or run.**

New work with its own pre-registration and its own kill criteria. **Not** a continuation of
P3-1's K4, and it must never be presented as one. P3-1 is closed at A-16; its four repairs,
six configurations and results are frozen inputs here and are not revisited.

---

## 1. The question P3-1 left open

P3-1 established the failure mechanisms and their downstream consequences on a development
corpus, and deliberately declined to claim cross-corpus generalisation. The open question
is the one a reviewer will ask:

> Does the repair family reduce measurement error on a corpus that did not produce the
> taxonomy?

P3-1 could not answer it because the frozen instrument had **zero label coverage** on the
intended validation corpus: 100% of Study 2's 31 components are covered by hand-written
`LABELS` or a bespoke branch, and 0% of the sealed corpus's 17 are (A-15).

## 2. Why the obvious fix is forbidden

Hand-authoring 17 labels for the target corpus and then running the six configurations
would replace the question above with a different one — *having seen the target corpus,
can I write an extractor good enough for it?* — and labels decide whether evidence is
visible at all, so they would dominate the result. A-15.4's prohibitions carry over
verbatim and are restated as binding on P3-2:

no hand-written per-task labels for the validation corpus; no labels derived from answer
text, trajectories, or hand-coded label prose; no edit to the frozen extractor that keeps
the name "frozen instrument"; no label chosen because it improves an outcome; no treating
the generic fallback as adequate; no running at zero coverage and reporting a verdict.

## 3. The design: derive labels by a frozen rule, do not author them

The object that must be validated is not a label set but a **label-derivation rule**: a
deterministic function from a task definition to a label set, applied uniformly to every
task, with no per-task discretion.

```
task definition (input-side)            frozen derivation rule R
  instruction + grading          ──R──▶   labels(task, component)
  184 tasks, agent-visible                 no per-task authoring
```

`external/MyPCBench-main/tasks/final/all_tasks_with_grading.json` holds 184 tasks with
`instruction` and `grading` fields. These are **inputs** — what the agent was asked to do
and what it is graded against — not agent outputs. §8 of P3-1 already established that
these task definitions are readable read-only, and R-CHAN's implementability check used
them.

This converts an unanswerable question into an answerable one. *Can I write good labels
for this corpus?* is not scientifically interesting and is not checkable. *Does a
corpus-independent derivation rule, calibrated where ground truth exists, transfer to a
corpus it was not calibrated on?* is both.

### 3.1 Calibration and freeze order, which is the whole protocol

1. `R` is authored and calibrated **only** against Study 2, where 30 hand-written `LABELS`
   entries exist as a reference and where every P3-1 result is already frozen.
2. `R` is frozen and hashed. Its output on all 184 tasks is materialised, hashed, and
   committed **before** it is applied to any validation task.
3. Coverage on the validation corpus is audited and reported **before** any configuration
   is run — the A-15 audit, now a pre-committed gate rather than a discovery.
4. One execution of the six frozen configurations. No re-derivation, no tuning, no second
   pass.

The ground truth is already frozen and hashed ahead of all of this: the A-14 transcription,
`386941d50defc21ce1955d5e5547789f2c081bea20003a640d3c337ebb633359`, committed at `c8e3a59`
before any derivation rule existed. That ordering is load-bearing and must be cited.

## 4. Contamination ledger, stated at its real strength

I have read the hand-coded `CLASS` prose for the 10 Paper 1 tasks, including reported
values, in order to build the A-14 transcription and to find the coverage defect. **That
cannot be undone** (A-15.6), and the following is what the design does and does not fix.

**What it fixes.** Per-task discretion is removed. `R` applies uniformly to all 184 tasks,
so knowledge of those 10 cannot be expressed as a per-task label choice — the mechanism by
which contamination would otherwise act.

**What it does not fix.** `R` itself could in principle be shaped by that knowledge. The
mitigations are that `R` is calibrated against Study 2 only, that its quality is measured
on Study 2 before it is applied to any validation task, and that its full output over all
184 tasks is hashed before application. None of these is a proof of blindness.

**What is not claimed.** That the validation corpus is blind to the label designer. It is
not. The claim available is narrower and must be written that way: *the label vocabulary
was produced by a rule frozen before application, calibrated on a disjoint corpus, and
applied without per-task intervention.*

If a genuinely blind validation is required, the only clean routes are a corpus whose
hand-coded labels the rule's author has never read, or a rule authored by someone who has
not read this one. Both are recorded as preferable and neither is currently available
without new labelling effort.

## 5. Validation corpus

Selection criteria, fixed here before selection:

* Hand-coded, component-level ground truth with stated values, including negatives.
* Disjoint from the corpus that produced the taxonomy.
* Ground truth frozen and hashed before the derivation rule exists.
* Transcribability failure rate at or below 20% (P3-1's K5 rule, unchanged).

The only set presently meeting all four is Paper 1's Stage 4 corpus: 24 cells, 48 legs,
46/48 transcribable under STRICT, ground truth frozen at `c8e3a59`. Its limitation is §4's
ledger, and the precision limitation of A-13.3 — **5 negatives** — carries over unchanged
and is a pre-stated reason the precision half of any verdict will be weak.

## 6. Kill criteria

Pre-committed, each with a consequence that is not "weaken the claim and continue".

* **P2-K0 — the derived instrument must be the same instrument.** With `R`'s labels
  substituted for the hand-written ones, `FROZEN` must reproduce P3-1's development-corpus
  taxonomy exactly. If it does not, `R` is a *different* instrument and any cross-corpus
  difference confounds two changes at once. Report both taxonomies side by side and do not
  attribute anything to the repairs.
* **P2-K1 — coverage floor, pre-committed rather than discovered.** Run the A-15 coverage
  audit before any configuration. Coverage below a floor fixed at freeze time returns
  **NOT EVALUABLE**, never PASS or FAIL. This is A-15 institutionalised: a null from an
  instrument that cannot see is not a null.
* **P2-K2 — negatives floor.** Precision is floored at `1 − n_neg/|match|` by corpus
  composition. Report the floor alongside every precision figure, and if the corpus cannot
  separate configurations differing by fewer than two false positives, say so in the result
  rather than in a limitations section.
* **P2-K3 — leakage.** No configuration may recover an observation whose gold is absent.
  Any recovery voids the run, as in P3-1's K3.
* **P2-K4 — the generalisation test.** If no repair improves sensitivity over `FROZEN` on
  the validation corpus at adequate coverage, the repair family does not generalise.
  Report as failed in one sentence; do not weaken it to a contributing factor.

As in P3-1 §7, a negative outcome here is publishable and the paper must be written so that
it is. A repair family that does not transfer, measured with an instrument whose
transportability was audited first, is a result.

## 7. Out of scope

No new model runs. No LLM judge, semantic similarity, screenshots, or manual qualitative
reading. No change to the four repairs, the six configurations, or any P3-1 frozen
quantity. No modification of Paper 1's or Paper 2's submission directories, the frozen
extractor, `matching.py`, the gold lock, or any archive or trajectory. No re-running or
re-interpreting the development corpus.

## 8. Open before freezing

1. The derivation rule `R` — its exact algorithm, and the coverage and negatives floors of
   P2-K1 and P2-K2. These are numbers, and they must be fixed before `R` is calibrated, not
   after its Study 2 coverage is known.
2. Whether P2-K0's "exactly" admits any tolerance. The default is none.
3. Whether a blind validation route in §4 can be obtained. If one can, it supersedes §5.
