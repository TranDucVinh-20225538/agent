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

## 5b. Amendment, 2026-09-12 — the 0.1 corpus must be named, not discovered

The first 0.1 run is **void** and its output must not be used. It was pointed at
`/data2/hpcshared/Vinh/agent/results/paper2_exec` and the script discovered lanes by
listing that directory, which holds far more than the frozen Study 2 corpora. It
enumerated **262 legs across 8 directories**, mixing in:

| directory | legs | status |
|---|---:|---|
| `study2-gpt` | 57 | frozen, in scope |
| `study2-claude` | 57 | frozen, in scope |
| `study2-flash` | 27 | **stale**, not the freeze |
| `qwen38-flash` | 57 | 23 `DONE`, so not the freeze either (freeze has 29) |
| `qwen35-9b` | 57 | lane excluded before execution, §0.10 |
| `study2-flash.INVALIDATED_pre_repair_20260906T181448Z` | 2 | invalidated |
| `gate0a-flash-instrument` | 1 | instrument diagnostic |
| `gpt-5.5-invalid-openrouter-transport` | 4 | rejected transport |

The frozen Flash corpus is not under that root at all. Per `out/study2_flash_freeze.json`
it is `/data2/hpcshared/Vinh-/agent/results/paper2_exec/hpc-flash-small-gate0a-postpatch`
(57 legs, `DONE` 29, `|A| = 8`), under `Vinh-` rather than `Vinh`.

Two fixes, both in `scripts/p3_0_enumerate_legs.py`:

1. `--lane NAME=PATH`, repeatable, which names each corpus explicitly and allows lanes
   under different roots. Bare `ROOT` discovery still works but now prints a warning that
   discovery cannot distinguish a frozen corpus from a stale, invalidated, pre-patch, or
   out-of-scope one.
2. `--expect-legs N`, which validates every requested lane **before** anything is written
   or reported and exits 3 otherwise. A lane that yields zero legs is also an error. The
   original run should have stopped at `flash = 27`; instead every downstream count
   silently inherited it.

The canonical 0.1 invocation is therefore:

```
python3 scripts/p3_0_enumerate_legs.py \
  --lane gpt=/data2/hpcshared/Vinh/agent/results/paper2_exec/study2-gpt \
  --lane claude=/data2/hpcshared/Vinh/agent/results/paper2_exec/study2-claude \
  --lane flash=/data2/hpcshared/Vinh-/agent/results/paper2_exec/hpc-flash-small-gate0a-postpatch \
  --expect-legs 57 \
  --terminal scripts/paper2_traj_terminal.py \
  --lock out/study2_gold_path_lock.json \
  --jsonl out/p3_0_legs.jsonl
```

`qwen35-9b` and the pre-patch Flash corpus stay **out of scope**. 9B was excluded before
execution and the Flash freeze policy forbids merging pre-patch material; bringing either
into P3-0 would be a scope change requiring its own pre-registration, not a judgement call
made while reading output.

### What the void run nevertheless established

The two lanes that *were* the frozen corpora reproduce Paper 2 exactly, which validates the
script against independently computed numbers: GPT gives 14 excluded-`VALID_DONE` legs and
Claude 2, matching §6.1(e)'s 14 and 2; GPT gives 18 legs in `A` and Claude 2, matching
`2 x 9` and `2 x 1`; GPT gives 2 high-`S` non-`DONE` cells and Claude 1, matching 2 and 1.
The consistency check also came back clean: no cell has both legs `VALID_DONE` while
sitting outside `A`, so the pairing rule and the terminal channel agree.

### A second bug, found because the printed numbers did not add up

The cross-tab showed 7 keyed `G2` legs while the summary line showed
`G2_by_design: 4`. Cause: `gate0_measurable` was computed as
`valid_done and not cell_in_A and task_keyed`, but `cell_in_A` is a **cell**-level flag, so
a `G2` leg belonging to a cell that *did* form a valid pair was disqualified. A `G2` leg is
outside `A` by design no matter what its cell did. Corrected to disqualify on `cell_in_A`
only for `G0` and `G1`. On the void run this understated the measurable stratum as 16 when
the correct figure is 19, i.e. exactly the keyed excluded-`DONE` legs; the same undercount
would have occurred on the clean run.

### Matched dissociation cells — the most informative unit found so far

Cross-referencing the two output tables shows a structure the spec did not anticipate. For
GPT, two cells have **one leg `DONE` at `S = 100` and the partner leg non-`DONE` at
`S = 100`**, on keyed tasks:

| lane | task | `DONE` leg | non-`DONE` leg |
|---|---|---|---|
| gpt | `preference_inference-f010` | G1, `S = 100` | G0, `S = 100` |
| gpt | `retrieval-f010` | G0, `S = 100` | G1, `S = 100` |

Within one cell the task, the gold, and the agent are held fixed, and the only thing that
differs is whether the episode closed. The `DONE` leg is Gate 0 measurable and the
non-`DONE` leg is Gate 1 analysable, so a single cell feeds both gates with the task and
gold confounds removed. This is a stronger unit than either gate's population taken
separately, and 0.3 and 0.4 must report these cells as a named subgroup. The same shape
appears for `retrieval-f017` in the pre-patch Flash corpus, which suggests it is not a
one-off, though that corpus stays out of scope.

Note what this subgroup does **not** license. It is not a sealed control: the cells were
found by reading output, not designated in advance, and there is no external label on
either leg. It sharpens the descriptive contrast; it cannot validate a metric.

## 5c. Amendment, 2026-09-12 — pre-registered scope extension for 0.2

Written **after** 0.1 completed and **before** the extractor touches any Study 2 leg.
This is a **scope extension**: a new population under the *same* frozen instrument. It is
not an instrument change, and no code, lock, or inference setting is modified.

### What 0.1 established

The clean run (171 legs, three frozen lanes, `--expect-legs 57`) reproduced Paper 2
exactly: 29 excluded-`VALID_DONE` legs (GPT 14, Flash 13, Claude 2), 5 high-`S`
non-`DONE` cells (GPT 2, Flash 2, Claude 1), consistency check clean. Of the 29, **16** are
on keyed tasks and measurable, **13** are vacuous. Causes: 23 orphan, 6 `G2`.

### Gate 0's ceiling is structural

A cell with both `G0` and `G1` at `VALID_DONE` is in `A` **by definition**, and 0.1 found no
exception. So the 16 measurable legs are each the single terminating leg of a non-paired
cell, and Gate 0 as originally written can produce **leg-level** positives only. The
pair-level `Y = 0` question is not underpowered on this archive; it is closed, because the
extractor already ran on all 18 pairs in `A`.

### The implementation clarification that makes the extension possible

`out/study2_hatd_extractor_lock.md` reads "Last well-formed `traj.jsonl` row, field
`response`. **If that row's action is `DONE`**, that response is the candidate answer."
The frozen implementation does not do that. `final_answer_from_traj()` at `3242c30` takes
the last non-empty row's `response`, strips `<think>`, and never inspects the action;
unparseable content then fail-closes to `None`, which `matching.py` treats as a mismatch.

The frozen extractor is therefore already capable of reading a non-`DONE` leg, with no
change of any kind. This is recorded as an **implementation clarification of the existing
lock, not a modification of it**. Anyone reading only the lock prose would conclude the
opposite.

### Extraction population for 0.2

| stratum | id | legs | pooled with Gate 0? |
|---|---|---:|---|
| original Gate 0: excluded `VALID_DONE`, keyed | `gate0` | 16 | — (11 orphan + 5 `G2`) |
| non-`DONE` partner legs of the 4 matched dissociation cells | `dissoc_nondone` | 4 | no |
| unmatched high-`S` non-`DONE` leg (see below) | `unmatched_nondone` | 1 | no |
| **total legs extracted** | | **21** | |

The four `DONE` legs of the dissociation cells are **already inside the 16** — they are
keyed orphans — so only their four non-`DONE` partners are new. The four dissociation
*cells* thus involve 8 legs but contribute only 4 to the count; reporting the population as
24 would double-count. Gate 0's own rate is computed on its 16 legs alone, and the two
non-`DONE` strata are reported separately and never pooled into it.

The four matched dissociation cells, each `S = 100` on both legs, both on keyed tasks:

| lane | task | `DONE` leg | non-`DONE` leg |
|---|---|---|---|
| flash | `aggregation-f037` | G1 | G0 |
| flash | `counterfactual-f005` | G0 | G1 |
| gpt | `preference_inference-f010` | G1 | G0 |
| gpt | `retrieval-f010` | G0 | G1 |

**Within a cell, gold is not held fixed.** `G0` gold is that leg's `probe_before` and an
injected `G1`'s gold is its `probe_after`; the world differing is the intervention itself.
What is held fixed is the task, the component set, the agent, the rubric, and the
instrument. A non-`DONE` leg counts as matching only against **its own** post-intervention
gold, never the partner's.

The `unmatched_nondone` stratum is one leg: `claude` / `retrieval-f002` `G0`, non-`DONE`,
`S = 100`, on a keyed task, whose partner leg also failed to terminate, so the cell has no
terminating leg at all. It is included at this point precisely so that it is not added
later after the matched cells' results are known, which would be the post-hoc move this
spec exists to prevent. It cannot influence the matched-cell analysis because it is not
pooled with it.

### The new quantity, and what it is not

The quantity produced by the added stratum is

> **pair-level component match under terminal-independent extraction.**

It must be reported under that name. It is **not** `Y = 1` within `A`. The definition of
`Y` on `A` is unchanged and remains `0` on all 18 pairs. These four cells are outside `A`,
so no result here revises any Paper 2 quantity; what it can show is whether the pair-level
null is a consequence of the completion gate rather than of state tracking.

### Outcome criteria, fixed before extraction

- *leg-level match*: every positive-weight component of that leg matches that leg's own gold.
- *cell-level terminal-independent match*: both legs of one cell each match their own gold.

Patterns, not thresholds:

- **Terminal-independent pair evidence exists** — at least one of the four cells has both
  legs matching. Observable component evidence then does not require terminal `DONE`.
- **Completion-dependent** — the `DONE` legs match and all four non-`DONE` legs fail. This
  is a real qualification of the P3 thesis and must be reported as such, not explained away.
- **Uninformative** — the `DONE` legs also fail, in which case the extractor says nothing
  about these cells either way and the `S = 100` scores are the only evidence present.

### Reporting rule for 0.3

For all **11** keyed orphan legs, report the partner leg's score descriptively, whether high
or low. Partner score may **not** be used to select, order, or exclude cases. The four
matched cells were identified by terminal status, never by score, and the gradient among the
rest (for example `gpt` / `contradiction-f006` at `S = 64`, `flash` / `aggregation-f020` at
`S = 83`) is part of the description.

### Stop point

After 0.2 runs once on exactly these 21 legs, stop. Gate 1 / item timing is **not** run yet:
four of its five cells are the dissociation cells, so what the frozen extractor says about
their legs must be known before item timing is used to explain a mechanism. No other cell,
leg, or lane is added.

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
