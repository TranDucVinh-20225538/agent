# Phase B.2 — six new tasks × three primary agents

You are on **node30**. Workdir: `/mnt/data2/Vinh/agent`. Branch: `phase-a-results`.

B.1 passed **10/10** (`out/phase_b_validate.md`). Frozen $I$ does not change.
`retrieval-f030` `gold_moved=False` is correct (Type B).

This session **runs agents**. It does not redesign tasks.

```bash
cd /mnt/data2/Vinh/agent
git fetch origin && git checkout phase-a-results && git pull origin phase-a-results
```

Need `PROMPT_PHASE_B2.md` and `scripts/phase_b_run.sh` on HEAD.

## What to run

Stage 4 already has Claude / GPT / Qwen 35B-A3B on:

- `retrieval-f001`
- `aggregation-f003`
- `preference_inference-f018`
- `counterfactual-f004`

**Do not re-run those four.** Do not overwrite `results/stage4-*`,
`results/stage4-openai-*`, or `results/stage4-qwen35a3b-*`.

Run only the six unrun IDs, each as baseline (probe-only) + CF (inject):

1. `retrieval-f003`
2. `retrieval-f016`
3. `retrieval-f029`
4. `retrieval-f030`
5. `aggregation-f018`
6. `preference_inference-f004`

Lanes, in this order, tmux `phase-b2`:

```bash
PHASEB_LANE=claude bash scripts/phase_b_run.sh
PHASEB_LANE=openai bash scripts/phase_b_run.sh
export OPENROUTER_API_KEY='sk-or-...'   # process only; never echo; never write .env
PHASEB_LANE=qwen35a3b bash scripts/phase_b_run.sh
```

Writes `results/phaseb-claude-*`, `results/phaseb-openai-*`,
`results/phaseb-qwen35a3b-*` only.

Judge is existing Anthropic `per_step`. Do not run Gemini.

## Do not

- Rewrite SQL / file patches / `f004_hd_rank_flip` after seeing an answer.
- Drop a task because it failed or $\Delta S$ moved.
- Require 18/18 DONE. Not-DONE is a row in the table (`DONE` = last
  `traj.jsonl` action `== "DONE"`).
- Start 9B or Flash (B.3 later).
- Use HPC / Slurm / abandoned 27B.
- Re-run Stage 4 cells to fish a prettier score.

## When a lane finishes

Paste, per task, base/CF: DONE or not, judge scores if present, and do
not classify Type A/B yourself beyond tracking vs score. Leave
attribution to the frozen DVs.
