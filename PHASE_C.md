# Phase C: Slot 4 (Preference / Multi-basis)

Do NOT expand the benchmark.
Run exactly one new research slot.

Target:
preference_inference-f009

Research question
-----------------
Does the agent's answer depend on one preference basis (order count vs total spend),
or are multiple preference bases jointly determining the behavior?

This is an attribution experiment, not a benchmark run.

Before running anything
-----------------------

1. Reconstruct the determining set.

Do not assume.

Inspect the guest SQLite and the pinned task JSON.

Write ONE hypothesis only:

Determining set:
{ orders.store_id × {COUNT(*), SUM(total)} joined to stores.name }

Gold function candidates:
A = plurality(order count)
B = maximum(total spend)

Pinned task file: `cf/tasks/preference_inference-f009.json`
(from `tasks/final/kwik_e_mart/kwik_e_mart.rubrics.json` — the graded rubric
accepts both bases). Guest DB: `/data/kwik-e-mart.sqlite`.

2. Verify both bases independently by SQL probes.

Dump:

- store by order count
- store by total spend

before any intervention.

Stop if the two rankings are identical.
In that case report why the experiment cannot distinguish the bases.

Design
------

Run ONLY the minimum interventions needed.

Condition 0
baseline

Condition A
Change order-count winner.
Keep total-spend winner unchanged.

Condition B
Change total-spend winner.
Keep order-count winner unchanged.

Condition A+B
(Optional ONLY if needed.)
Run only if A and B alone do not distinguish the behavior.

Requirements
------------

Never modify:

- instruction
- rubric
- planner
- login
- GUI

Only modify the determining records.

Before every run verify by SQL that:

order-count winner =
...

total-spend winner =
...

Then launch the official Claude Opus pipeline.

Dependent variable
------------------

Primary:

- agent final answer

Secondary:

- trajectory
- evidence accessed
- judge score (for completeness only)

Do NOT use judge score for interpretation.

Outputs
-------

Produce:

results/preference_f009_basis.md

containing

Condition
Count winner
Spend winner
Agent answer
Judge score

and

results/preference_f009_probe.sql.txt

Archive:

- trajectories
- screenshots
- SQL patches
- probe outputs

After the experiment:

Write exactly one line:

Minimal determining set:
{ ... }

If the determining set cannot yet be identified,
state which evidence channel remains ambiguous.

Stop after this slot.

Do not continue to any other task.
Commit and push to branch phase-a-results.

---

## How to run this on node30

```bash
cd /mnt/data2/Vinh/agent
git fetch origin && git checkout phase-a-results && git pull origin phase-a-results
tmux new -s phase-c
bash scripts/phase_c_f009.sh
```

The script dumps rankings with the dummy agent first. If count and spend name
the same store it writes `results/preference_f009_probe.sql.txt` and exits
without calling Opus. Otherwise it runs baseline, A, then B. It does not start
A+B.

Hypothesis to write before the first Opus call, once the dump is in hand:

```
Determining set:
{ orders[*].store_id  (count) ,  orders[*].total  (spend) }
```
