# P3-0 — Recoverability Audit (pre-registration)

Written and committed **before** any leg outside `A` is extracted and before any
`per_step_scores` array is read. Nothing here may be revised after outcomes are seen; a
revision must be a new dated section that says what it changes and why.

No model run. No executor change. No re-judge. No metric. No threshold tuning. No
qualitative cherry-picking. Study 2 archives stay write-locked.

## 0. Question

Paper 2 established that `A` (both legs canonically `DONE`) is a **measurement gate**, not
the archive. P3-0 asks one falsifiable question about what the gate discarded:

> Do trajectories excluded from `A` carry observation-grounded, task-relevant evidence
> that the frozen instrument can already measure?

This is a diagnostic gate on existing data. It is not a claim that Paper 2 is wrong.
Paper 2 found a selection effect; P3-0 asks whether the selected-out region is measurable.

## 1. Terminology lock

The construct is **observation-grounded reliability**, or more precisely
**trajectory-level observability of task-relevant state**.

It is **not** "state transition reliability" and must never be written that way. The archive
records what the agent observed and reported. It does not record what state the agent
caused: `probe_before` / `probe_after` in each `*.guest.json` bracket the **intervention
patch** and carry `gold_moved`, so they certify the harness, not the agent. There is no
post-episode probe and no retained overlay or qcow2. Agent-caused state change is
unrecoverable from this archive, permanently, and no re-run recovers it.

Therefore the following substitution is prohibited in all P3 writing:

| may claim | may not claim |
|---|---|
| observable correctness | actual environment correctness |
| the agent reported the post-intervention value | the agent produced the correct world |

This constraint is survivable because the Study 2 task families (retrieval, aggregation,
preference inference, counterfactual, contradiction) are read-and-report tasks: correct
behaviour is to report state, not to change it.

## 2. What the frozen locks can and cannot reach

Determined by reading the locked artifacts, before running anything.

**The binding constraint is task keying, not leg name.** Both locks cover exactly the **13**
tasks that produced the 18 valid pairs, out of **19** tasks in the universe:

- `scripts/study2_hatd_extract.py` at `3242c30` keys parsers by `(task, component_id)` for 13 tasks.
- `out/study2_gold_path_lock.json` defines `components` for the same 13 tasks.

The 13: `aggregation-f020`, `aggregation-f037`, `contradiction-f004`, `contradiction-f006`,
`counterfactual-f005`, `counterfactual-f010`, `counterfactual-f013`,
`preference_inference-f010`, `preference_inference-f014`, `retrieval-f002`,
`retrieval-f009`, `retrieval-f010`, `retrieval-f017`.

Consequences, all load-bearing:

1. **Unkeyed tasks are not measurable and must not be reported as mismatches.**
   `extract_leg` reads `lock["components"][task]`, which is `{}` for the other 6 tasks, so
   `gold` and `reported` both come back empty. That is **vacuous**, not a negative result.
   Reporting it as "no component match" would manufacture a FAIL.
2. **G2 legs are measurable.** `canonicalize_guest` decides the leg's world by whether that
   leg's own guest file contains `probe_after`, never by leg name. The lock's prose mentions
   only G0 and G1, but the code generalises correctly by construction, so a G2 leg on a
   keyed task is readable with zero lock change.
3. **Extending either lock to the remaining 6 tasks creates a new instrument.** It is
   permitted for P3, but results from it may never be attached to Paper 2's `A`, its `Y=0`,
   or any Study 2 quantity, and it must be frozen by commit before outcomes are viewed.

## 3. Gate 0 — completion-filter recovery

Population: the **29** legs that reached canonical `VALID_DONE` but fall outside `A`
(GPT 14, Flash 13, Claude 2; mean `S` 81.2 / 94.4 / 100; 17 of the 29 have `S >= 90`).
These legs terminated, have a final answer, and have known gold. They were excluded by the
**pairing rule**, not for lack of information, and the extractor has never been run on them:
`out/study2_hatd_legs.jsonl` holds exactly 36 legs = 2 x (9 + 8 + 1), i.e. `A` only.

Procedure: run `scripts/study2_hatd_extract.py` at `3242c30` **unchanged**, one leg at a
time, with `out/study2_gold_path_lock.json` unchanged. Matching stays
`paper/paper2_counterfactual_eval/protocol/matching.py`, untouched. Legs in `A` are not
re-extracted; their existing 36 rows are reused byte-for-byte. Target: 36 -> 65 legs.

Stratification, fixed now, reported separately and never pooled:

| axis | levels |
|---|---|
| measurability | keyed task (measurable) / unkeyed task (vacuous, excluded from all rates) |
| exclusion cause | `G2` (excluded by design) / `G0`-or-`G1` orphan (partner leg did not reach `DONE`) |

Quantities to report, on the measurable stratum only:

- leg-level component match count, and full-component match count per leg;
- cells with **both** legs matching, cells with **exactly one** leg matching;
- whether positives concentrate in `G2` or in orphans;
- association between leg-level match and `S`.

**Logical constraint on interpretation.** A leg-level positive does **not** make pair-level
`Y = 1`. Paper 2's `Y` requires every positive-weight component to match on **both** legs of
one cell. Rebutting the pair-level null therefore requires a cell with both legs matching.
A single leg-level positive is still a new finding, because the frozen extractor has never
measured these legs, but it must be reported as leg-level and nothing more.

## 4. Gate 1 — item timing and max-reduce composition

Population: the **5** cells with `S >= 90` and no canonical `DONE` (GPT 2, Flash 2, Claude 1).
Coverage note: Gate 1 is unaffected by the task-keying constraint, because
`per_step_scores` is present in every `rubric_result.json` for every task and every terminal
state. Gate 1 therefore has full archive coverage where Gate 0 does not.

Input, already on disk, no re-judge: each `rubric_result.json` carries `per_step_scores`
(per step: `step_num`, `screenshot`, and a binary `scores` array aligned to `rubrics`),
plus `per_rubric_max` and per-item `weight`.

For item `i` at step `t`, let `I(i,t)` be that item's normalised binary score. Paper 2's
score is the max-reduce `S = 100 * sum_i w_i * max_t I(i,t)`, verified to reproduce exactly
on 94/94 cells in EXECUTION_MANIFEST §0.12.

Distinguish two mechanisms:

- **Co-firing / persistence** — there exists a single step `t` at which every
  positive-weight item fires simultaneously, i.e. the correct evidence was present in one
  observation.
- **Max-reduce composition** — every item fires at some step, but at pairwise distinct
  steps, and no single step carries them all. The aggregate is then assembled across time
  from observations that never coexisted.

Reported per cell: first-fire step per item; whether a co-firing step exists; whether it
persists to the last scored step; and the decisive scalar

```
gap = S_maxreduce - max_t ( 100 * sum_i w_i * I(i,t) )
```

`gap = 0` means the score was attainable in one observation. A large `gap` means the high
aggregate is assembled across time, which would establish the specific mechanism

> high aggregate `S` does not imply simultaneous observable correctness.

Self-check, mandatory before any interpretation: the script must reproduce the stored
`score` from weights and `per_step_scores` for every cell it reads. A cell that fails
reproduction is reported as unreadable and excluded, never silently approximated.

## 5. Outcome

P3-0 is a diagnostic gate. No numeric threshold is pre-set; the outcomes are defined by
pattern, and the patterns are fixed here, before the data is opened.

**PASS** — at least one of:

1. *Completion-filter recovery*: positive component match exists among the measurable
   excluded legs, most strongly if some cell has both `G0` and `G1` matching.
2. *Timing inflation*: at least one high-`S` non-`DONE` cell where the score is
   substantially composed across distinct steps with no co-firing step.

Either gives a measurable phenomenon concrete enough to build P3 on.

**WEAK** — leg-level signal or timing structure exists, but only in `G2`, or only in
orphans, or with co-firing so sparse or so inconsistent that no pattern holds. Do not build
a metric; refine the construct and design controls first.

**FAIL** — no appreciable component match among the measurable excluded legs, no timing
inflation among the 5 high-`S` non-`DONE` cells, and no other clearly observable structure.
Then the hypothesis is dropped. Paper 3 is not rescued from this branch.

A fourth outcome is possible and must be reported honestly rather than forced into the
three above: **UNDERPOWERED**, if the measurable stratum of Gate 0 turns out to be too small
to say anything, in which case Gate 1 stands alone and Gate 0 is reported as not reached.

## 5a. Amendment, 2026-09-12 — third PASS pattern

Added **before any Study 2 leg outside `A` was opened**, on evidence from the Paper 1
archive, which is a different corpus and is not the Gate 0 or Gate 1 population. Recorded
here rather than folded silently into §5, per the revision rule at the top.

Running `scripts/p3_0_item_timing.py` over the 94 Paper 1 cells reproduces the stored score
on 94/94 and finds **`gap = 0` on every cell**: max-reduce composition never occurs there,
and all 36 cells with `S >= 90` have a co-firing step that persists to the last scored step.
Long episodes (58, 83, 151 steps) behave the same.

The single Paper 1 cell that matches the Gate 1 profile — Qwen3.8-Flash `retrieval-f016`
base, `S = 100`, `last_action = EMPTY_XML`, hence not `DONE` — shows all four
positive-weight items firing **for the first time at the same step (10)**, which is also the
last scored step, with `gap = 0`.

So the expected mechanism is the opposite of timing inflation: the score was not assembled
across time, it was genuinely simultaneous, and only the terminal handshake failed
afterwards. Pattern 2 of §5 would record that as *not met* while the observation is in fact
stronger evidence for the P3 thesis, because it is positive evidence of recoverable
simultaneous correctness rather than evidence that a score is hollow. Pattern 2 stays as
written; a third is added.

**PASS pattern 3 — protocol-terminal dissociation.** A cell with `S >= 90` and no canonical
`DONE` in which a co-firing step exists, persists to the last scored step, and `gap = 0`.
The correct task-relevant evidence was present in a single observation and the episode
nonetheless failed to close.

Patterns 2 and 3 are mutually exclusive by construction and jointly exhaust the high-`S`
non-`DONE` cells that are readable, so Gate 1 now has no outcome that is silently
uninformative: each such cell resolves to composed-across-time, dissociation, or
unreadable. If every cell lands on pattern 3, Gate 1 passes on dissociation and the
timing-inflation hypothesis is reported as **not supported** — which is a finding to state,
not a gap to hide.

## 6. Order of work

```
0.1  enumerate all 171 legs; classify terminal, in-A, keyed/unkeyed, G2/orphan
0.2  run frozen extractor 3242c30 on the measurable excluded legs only
0.3  leg-level and pair-level recovery counts, by stratum
0.4  per_step_scores audit on the 5 non-DONE, S >= 90 cells
0.5  PASS / WEAK / FAIL / UNDERPOWERED
```

Only on PASS or WEAK does anything downstream begin, and in this order: define the
construct, build positive and negative controls, seal a validation universe, and only then
a metric. Controls are what give the word "signal" an external referent; with `Y = 0`
everywhere in `A`, the archive supplies no positive label, so P3-0's criteria are internal
consistency and nothing more.

## 7. Where the data is

The Study 2 archive is host-side and read-only:
`/data2/hpcshared/Vinh-/agent/results/paper2_exec/study2-{gpt,flash,claude}/<task>/<leg>/`.
Steps 0.1--0.4 must run there. The local checkout holds only the 71 Paper 1 and probe cells
under `results/`, which share the same cell layout and are therefore usable to test the
scripts before they touch Study 2.

Terminal status must be read by calling `scripts/paper2_traj_terminal.py` (canonical,
fail-closed, does not consult `rubric_bundle.json`). P3-0 must not reimplement `DONE`
detection; every `|A|` and every count here inherits its fail-closed lower-bound property.
