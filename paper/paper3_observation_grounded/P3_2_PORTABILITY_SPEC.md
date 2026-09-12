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

### 3.1 Derivability is not observability

These are two distinct failure modes and conflating them is what let A-15 go unnoticed:

```
task definition:  "Report the NEC 1099 amount."
        │
        ├─ R emits "NEC 1099 amount"        grounded    = 1   (G1 satisfied)
        │
agent answers:    "The filing reported $4,250."
        └─                                  observable  = 0   (G3 violated)
```

The instrument knows *what* it is looking for and still cannot recognise *how* the agent
expressed it. Groundedness is a property of the rule against the task definition;
observability is a property of the rule against the agent's language. A rule can be 100% of
the first and 0% of the second, which is precisely the shape of A-15 — and a rule gated
only on groundedness would relocate that failure rather than prevent it. Hence G1 and G3
are separate gates with separate thresholds.

### 3.2 Calibration and freeze order, which is the whole protocol

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

## 6. Gates, fixed before `R` is designed

Four separate conditions, deliberately **not** bundled. An earlier draft placed a single
80% floor on the calibration corpus; that was wrong twice over — it mixed a validity
constraint with a coverage measure, and on the calibration corpus it could never fire,
because G2 at tolerance 0 already forces 30 of 30. The numbers below are fixed here,
before `R` exists and before anything about `R` is measured.

### G1 — Groundedness: 100%, a validity constraint

Every label `R` emits for a `(task, component)` must occur as a literal substring of that
task's own `instruction` or `grading` text, under a normalisation limited to casefolding
and whitespace collapse, declared with `R` and frozen. Nothing else: no stemming, no
synonyms, no fuzzy matching.

A single ungrounded label is **contamination, not a coverage shortfall**, so there is no
percentage here. Violation aborts. This is the mechanism that makes §4's contamination
non-actionable: knowledge of the target corpus cannot be expressed except through terms the
task definition already contains.

### G1b — No memorisation: `R` may name no task and no component

`R`'s implementation may not contain any task identifier or component identifier as a
literal. Checkable mechanically against the 184 task ids and the component ids of both
corpora, and it is what makes "corpus-independent" a verified property rather than a
promise: without it, sufficient iteration on the calibration corpus would let `R` memorise
the 30 hand-written label lists, which is hand-authoring wearing a rule's clothes.

**What G1b forbids is literal memorisation, not receiving identifiers as data.** `R` may
take `task_id` and `component_id` as inputs and process them by the same rule as every
other task — tokenising `component_id`, splitting `snake_case`, and so on. What it may not
do is branch on or key off a specific value:

```python
R(task_id="retrieval-f010", component_id="host_name", instruction=..., grading=...)
    # allowed: identifiers are data, processed uniformly

if task_id == "retrieval-f010":           # G1b FAIL
    return [...]
LABELS = {"retrieval-f010": [...]}        # G1b FAIL
```

The loophole this closes is concrete: see a calibration task, add a branch for it, add its
label set, pass G2. That is formally a deterministic rule and substantively a hand-authored
lookup table, and it would defeat the entire purpose of P3-2.

`R`'s free parameters are declared in this spec **before** calibration. Calibration may
only choose values within that declared set — for example a tokenisation rule, a
`snake_case` split, punctuation-variant expansion, a task-side span extractor, a maximum
span length, a normalisation rule — and each must be written down with a value before
Study 2 is touched. Discovering mid-calibration that "this task needs an abbreviation" and
adding a parameter is an amendment, recorded as one. `R` may never learn *which labels are
correct* from Study 2; calibration only selects within a pre-declared space.

### G2 — Calibration fidelity: 100%, tolerance 0

With `R`'s labels substituted for the hand-written `LABELS`, `FROZEN` must reproduce
P3-1's frozen development result **exactly**: the 134-row categorisation, the cause
taxonomy, and A-10's per-configuration table. Study 2 has 30 label-sensitive components and
1 inert (`kind = state`, which returns `None` regardless), so the requirement is **30/30**,
not 80%.

Evaluated once, after freeze. `R` is **not** revised until it passes — G2 is not a loop and
not a loophole.

**If G2 fails, that is a pre-registered result, not a failure of the experiment.** A
corpus-independent rule that cannot reconstruct a hand-tuned instrument on the very corpus
that instrument was written for is direct evidence that the frozen instrument contains
task-specific authoring which an independent rule does not recover — i.e. that the
instrument itself is not portable. Reported in one sentence, with the shortfall counted
(`27/30` is reported as `27/30`). P3-2 stops there and the validation corpus is not
touched.

### G3 — Validation observability: ≥ 80%, the gate A-15 earned

After `R` is frozen, hashed, and materialised over all 184 tasks, and **only** then, answer
text from the validation corpus is read for the first time. For each validation
`(task, component)` with non-null gold, ask whether at least one label `R` emitted for it
occurs — same frozen normalisation — in the agent's answer text on at least one leg.
Observability is the fraction of such components.

Below **80%** the sealed comparison is **NOT EVALUABLE**. Not PASS, not FAIL, and the six
configurations are not run. 79% does not become "K4 failed".

This is the distinction of §3.2 doing work: G1 asks whether the instrument knows what it is
looking for, G3 asks whether it can recognise how the agent expressed it. The hand-written
labels score **0%** here (A-15), and that figure is the reference `R` is reported against.

### G4 — Negatives floor: ≥ 20, independent of coverage

The validation corpus must supply at least 20 negative observations — human-coded wrong
with a stated wrong value — eligible for precision assessment. This is an auditability
requirement, not a statistical threshold, and it is independent of G3: coverage asks
whether `R` sees evidence, G4 asks whether there is enough counter-evidence to tell whether
`R` over-generates.

**G4 is already evaluable and already fails.** It is a property of the corpus, not of `R`:
A-14's transcription supplies **5** negatives against a floor of 20. Recorded here, before
`R` exists, with its pre-committed consequence: precision is **not claimed** as adequately
audited on this corpus, and any precision figure is reported together with its structural
floor `1 − 5/|match|` — at 30 matches, ≥ 0.833 whatever the instrument does. Sensitivity
remains evaluable. No negatives may be added after seeing any result.

### G5 — Leakage

No configuration may recover an observation whose gold is absent. Any recovery voids the
run, as in P3-1's K3.

### P2-K4 — the generalisation test

Only reachable if G1, G1b, G2, G3 and G5 hold. If no repair improves sensitivity over
`FROZEN` on the validation corpus, the repair family does not generalise: report as failed
in one sentence and do not weaken it to a contributing factor. Given G4, the verdict is on
sensitivity alone and says so.

**If any gate before the sealed execution fails, K4 is not run and no K4 verdict exists.**
As in P3-1 §7, a negative outcome is publishable and the paper must be written so that it
is.

## 7. Out of scope

No new model runs. No LLM judge, semantic similarity, screenshots, or manual qualitative
reading. No change to the four repairs, the six configurations, or any P3-1 frozen
quantity. No modification of Paper 1's or Paper 2's submission directories, the frozen
extractor, `matching.py`, the gold lock, or any archive or trajectory. No re-running or
re-interpreting the development corpus.

## 8. Order of work and hard stops

```
                          R  (algorithm + declared parameters)
                          │
                calibrate on Study 2 only
                          │
        ┌─────────────────┼─────────────────┐
      G1 grounded      G1b no task/         G2 fidelity
        = 100%         component literals     = 30/30, tolerance 0
        └─────────────────┼─────────────────┘
                          │
                   FREEZE + HASH R
                          │
              materialise R over all 184 tasks, hash
                          │
        ┌─────────────────┴─────────────────┐
   G3 observability                    G4 negatives
      ≥ 80%  (first read of                ≥ 20  — already FAILS at 5
      validation answer text)               precision not claimed
        └─────────────────┬─────────────────┘
                          │
                 one sealed execution
                          │
                        P2-K4
```

Each number means one thing and they no longer overlap: groundedness is a 100% validity
constraint, calibration fidelity is exact reconstruction at tolerance 0, and 80% is *only*
the pre-registered minimum validation observability required for the sealed comparison to
be evaluable — not a claim that `R` must reach 80% everywhere.

## 9. The one question the sealed run may answer

G4's failure makes P3-2's validation objective deliberately **asymmetric**. The sealed run
may answer exactly one question:

> Does the independently generated measurement instrument retain **sensitivity** when
> transferred to the validation corpus?

It may **not** answer "the instrument has good precision". With 5 negatives against a floor
of 20, precision is not audited, and the shortfall is not to be dressed up as a nuisance
statistic or absorbed into a limitations paragraph — it is a stated boundary on what the
experiment measures.

| property | status |
|---|---|
| groundedness | 100%, hard gate |
| calibration fidelity | exact, tolerance 0 |
| validation observability | ≥ 80% |
| precision negatives | **FAIL** — 5 < 20 |
| sensitivity | evaluable |

## 10. The claim, worded exactly

> The label vocabulary was generated by a frozen, corpus-independent rule from task-side
> specifications, calibrated on a separate corpus, and applied uniformly without
> task-specific manual intervention.

Not claimed, and not to be written: that the validation corpus is blind to the label
designer. It is not, per §4.

## 11. Open before freezing

1. `R`'s algorithm and its declared parameter set. Everything in §6 is fixed first, and
   `R` is designed against those gates rather than the gates against `R`.
2. Whether a blind validation route per §4 can be obtained. If one can, it supersedes §5,
   and it would also resolve G4, which the current corpus fails.

---

## 12. Pre-design audit — G1 ↔ G2 compatibility (2026-09-12)

Run before `R` was designed, on the reasoning that two invariants which contradict each
other must be caught before any algorithm exists — the A-15 lesson applied to the
protocol itself rather than to an instrument. `scripts/p3_2_k0_g1_compat_audit.py`,
read-only over task definitions and the frozen label table, no answer text, exits 5.

### 12.1 First, a tension that does not exist

G2 as frozen compares *results* — the 134-row categorisation, the cause taxonomy, A-10's
table — not label strings. Frozen regex spelling such as `avg(erage)? cost` is therefore
already an implementation detail, and a literal label is not required to equal it. No
amendment is needed on that point.

### 12.2 What the audit does test, and what it found

Using the frozen label patterns themselves as matchers against each task's own
`instruction`/`grading`, so the audit invents no regex-stripping rule of its own:

| | |
|---|---|
| label-sensitive calibration components | 30 |
| with ≥1 **groundable** frozen label | **26** |
| with none | **4** |

```
aggregation-f037/top_sender            labels `top (inbox )?sender`, `most (emails|messages)`
aggregation-f037/top_sender_count      labels `top_sender_count`, `message count`, `email count`
contradiction-f004/batbucks_gme_shares only `batbucks.*gme` matched, via a `.*` wildcard
counterfactual-f005/gme_avg_cost       label `avg(erage)? cost`
```

A pattern containing `.*` is excluded from feasibility because its match is whatever lies
between two anchors — here roughly 900 characters of rubric text — and cannot license a
literal label. That is a structural exclusion, not a length threshold chosen to suit the
outcome. Note the same component id `gme_avg_cost` is groundable under
`contradiction-f004` (`'average cost'` occurs) and not under `counterfactual-f005`: the
obstruction is a property of the task text, not of the component name.

### 12.3 The limit of this audit, stated rather than glossed

The audit proves the **frozen labels** are not groundable for those four, so G2 cannot be
met by reproducing them. It does **not** prove that no other task-side-grounded phrase
selects the same extraction windows and so reproduces the behaviour G2 actually tests.
Settling that requires reading calibration answer text, which this audit deliberately does
not do.

So the finding is a determinate obstruction to one route to G2, and a risk flag on the
other. It is **not** yet a proof that G1 and G2 contradict each other, and must not be
written as one.

### 12.4 Stage 2, implemented and pending execution

`scripts/p3_2_stage2_reachability.py` settles the open half by **exhaustion**. For each of
the four it enumerates every literal substring of the task-side text up to 6 tokens — 786
to 1117 candidates per task — and asks whether any of them, used as the sole label,
reproduces the frozen extracted value on every calibration leg of that task. Every
candidate is a literal substring taken by offset, so it is G1-compliant by construction.

Exhaustiveness is the point: if no grounded span works, no grounded rule can work, however
written. The 6-token bound is deliberately generous, because a negative result at 6 is
stronger than at 2.

It also tests a possibility stage 1 could not see: if a frozen label extracts **nothing**
on every leg, the component constrains G2 only to also extract nothing, and the stage-1
obstruction is **vacuous** rather than binding. That is reported as `VACUOUS`.

Two things it is not. It is not calibration — it declares no parameter and produces no
`R`. And a surviving span may **not** be adopted as a label: that would be hand-authoring
by search, which is exactly what G1b forbids. The only output is reachability.

Verdicts: `UNREACHABLE` on any component means G1 and G2 genuinely contradict, G2 at 30/30
is unattainable by any grounded rule, and the resolution is an amendment rather than a
quietly weakened gate. `REACHABLE` or `VACUOUS` everywhere means G2 at 30/30 remains
attainable in principle.

`R` remains undesigned, and no parameter set has been declared.
