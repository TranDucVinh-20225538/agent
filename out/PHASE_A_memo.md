# Phase A — analysis memo (frozen)

Status: **frozen**. Claude Opus 4.6 confirmatory cells are closed
(`667a971`). Do not add Opus runs to grow N. Do not run the full
benchmark yet.

This memo is a mini-study write-up, not a paper conclusion. Pilot cells
(`hard_app-f033`, `preference_inference-f009`, `situated_action-f028`)
stay in the pilot log. They are not the confirmatory sample.

## Claim the data actually support

Not: “agents fail to use personal data.”

The data support:

> Benchmark success scores can remain unchanged even when the personal
> evidence underlying the gold answer is counterfactually changed, and
> agents may or may not track that intervention.

That sentence is weaker than a universal failure claim, and harder for a
reviewer to knock down.

## Funnel (locked)

```
184 tasks
  → 10 eligible (A–E)
    → 8 confirmatory sample (seed 20260826, k≤3 per type)
      → 4 confounded (no Claude; remain in the sample)
      → 4 identifiable Claude
reserves retrieval-f003 / retrieval-f016: identifiable, not promoted
```

4/8 confounded is a screening result: on a rule-chosen sample, half the
tasks have gold pinned by the rubric or dual-channel Files+SQLite. That
stays in the paper. It is not a hole to fill by promoting reserves.

## Confirmatory Claude (Opus 4.6)

| task | evidence | gold moved | agent track D? | judge | status |
| --- | --- | --- | --- | ---: | --- |
| retrieval-f001 | point_field | Gold/38450 → Silver/8620 | yes | 100 → 100 | ok (confirmatory replication of the same pilot intervention) |
| aggregation-f003 | aggregation | combined 4871.70 → 400.00 | yes | 80 → 80 | ok |
| preference_inference-f018 | joint multi_record | GME 85→0 **and** OM YES 200/active → 0/settled | **partial** | 100 → 100 | null on the joint D |
| counterfactual-f004 | contradiction | 1099/income zeroed; tuition held | **out of inference** | 0 → 87 | failure |

### What “partial” means on f018

The locked intervention is the **whole** Stage-3 determining set, not a
2×2. Probe after retry (`status='settled'`, not the aborted `'closed'`):

- BatBucks GME shares: 85 → 0 (`gold_moved` on the primary probe)
- OddsMarket YES: 200/active → 0/settled

Baseline answer: GME 85 @ 42.12 **and** GameStop YES 200.

CF answer: GME **0 shares** (tracks BatBucks) **and** still lists
GameStop YES **200** as an active OddsMarket position (does not track the
OM conjunct). Rebalance still “leans into” GameStop via that YES line.

Do **not** write “the agent ignored personal data.” It read the live
BatBucks row. It did not track the joint D. Judge still 100. That is the
interesting cell: success without tracking the full determining set.

Attempt 1 (`status='closed'`) is `technical_failure`. It is not a
confirmatory cell.

### Why f004 is out of inference

Baseline hit `max_steps=80` with no DONE / no usable `contradiction_flag`.
Judge 0. No baseline DV ⇒ no attribution contrast. Failure is failure,
not a negative result. The CF answer still reports a $1,200 1099 after
the amount was zeroed; that is **not** entered as a confirmatory finding.

## Three questions

### Q1. Is the judge score invariant to the evidence intervention?

On cells we can read:

- f001: **yes** (tracks, score unchanged)
- f003: **yes** (tracks, score unchanged)
- f018: **yes**, with partial tracking
- f004: unknown

Signal: two different evidence structures (point field, aggregation)
both show gold-move → answer-move → **score-stay**. That is no longer a
single retrieval anecdote. f018 shows the same score-stay when tracking
is only partial. Hypothesis of Phase A is supported, not proven.

### Q2. Do all agents fail to track evidence?

Unknown. N=1 model (Claude Opus 4.6). Tracking **happened** on f001 and
f003. The result is not “agents don’t use personal records.”

### Q3. Does the intervention protocol generalize?

Starting to: point/field, aggregation, joint preference. Not enough
breadth, and contradiction is not yet a usable confirmatory cell.

## What we actually bought with the Opus spend

A protocol that can tell apart

1. the agent produced a successful task outcome, and
2. that outcome was produced by the personal evidence the rubric treats
   as gold.

That protocol is the asset. More Opus on the same four tasks does not
buy generalization.

## Predictions (locked before the next model is run)

Write these down **before** looking at a second model’s answers.

Replication set, same locked SQL, same DVs, no new tasks:

- **Must run:** `retrieval-f001`, `aggregation-f003`
  (the two clean confirmatory cells).
- **Do not run first:** `counterfactual-f004` (no baseline DV).
- **Optional later, not in the first replication:** `preference_inference-f018`
  (joint D; schema encoding of “not active” is `settled`).

**P1 — score invariance.** If both baseline and CF complete and the guest
probe shows `gold_moved`, the judge score will not detect the
intervention: `|score_CF − score_base|` will be small relative to the
gold change (f001/f003: we expect no change, as with Opus).

**P2 — tracking is a separate DV.** Score invariance does **not** predict
tracking. A second model may track f001/f003 (like Opus) or not. Either
outcome is compatible with P1. We will code tracking from the final
answer, not from the score.

**P3 — a GUI/step-limit abort is `technical_failure`, not a refutation.**
Same rule as f004.

**P4 — we will not claim model-generality from two models.** Two models
that both show P1 on f001+f003 justify a larger sample, not a full 184
sweep.

If P1 fails on a second model (score moves when gold moves, in the
direction of the new gold), that is a real negative for the
score-invariance claim and we stop before scaling.

## Next spend (not more Opus)

Prefer harness-native, local, A100:

1. `qwen_cuabash` / `Qwen/Qwen3.5-35B-A3B` via vLLM
   (`external/MyPCBench-main/docs/NO_DOCKER.md` §6). This is a paper
   agent, not an informal screenshot-VLM.
2. If VRAM allows a second local point: `Qwen/Qwen3.5-9B` as a smaller
   CUA, same two tasks, same SQL.
3. Do **not** buy Claude Sonnet or GPT to “increase N” of the same
   design. A paid second family is only worth it after local Qwen
   completes f001+f003 without technical failure.

After those two tasks × one local model (four cells: base+CF × f001+f003):
decide whether to (a) add f018 on that model, (b) add a second model, or
(c) enlarge the task sample. Full MyPCBench is not on the table until
P1 has been seen on more than one model class.

## What stays in the appendix / funnel, not the result table

- 4 confounded sample members (unrun Claude)
- 2 identifiable reserves (not promoted)
- f009 dummy probe (count winner = spend winner)
- f033 factorial (pilot; DV = Move/All-clear, not score)
- f028 GUI confound (control)
- f018 attempt-1 CHECK failure
- f004 baseline abort

## Stop

Phase A is enough to continue, not large enough to conclude generally.
The next artefact is a Qwen replication plan on f001+f003, written
against the predictions above, not another Opus prompt.
