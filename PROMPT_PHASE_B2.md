# Phase B.2 — six new tasks; Qwen/GPT first, Claude last

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

Stage 4 already has Claude / GPT / Qwen 35B-A3B (and 9B/Flash on f001+f003) on:

- `retrieval-f001`
- `aggregation-f003`
- `preference_inference-f018`
- `counterfactual-f004`

**Do not re-run those four.** Do not overwrite `results/stage4-*`,
`results/stage4-openai-*`, `results/stage4-qwen35a3b-*`,
`results/stage4-qwen359b-*`, or `results/stage4-qwen38flash-*`.

Run only the six unrun IDs, each as baseline (probe-only) + CF (inject):

1. `retrieval-f003`
2. `retrieval-f016`
3. `retrieval-f029`
4. `retrieval-f030`
5. `aggregation-f018`
6. `preference_inference-f004`

## Lane order (strict)

Claude is **last**. Anthropic is not billed enough yet. Do **not** start
`PHASEB_LANE=claude` in this session.

tmux `phase-b2`:

```bash
export OPENROUTER_API_KEY='sk-or-...'   # process only; never echo; never write .env

PHASEB_LANE=qwen35a3b bash scripts/phase_b_run.sh
PHASEB_LANE=openai bash scripts/phase_b_run.sh
PHASEB_LANE=qwen359b bash scripts/phase_b_run.sh
PHASEB_LANE=qwen38flash bash scripts/phase_b_run.sh
```

Then **STOP**. Do not run Claude until the human says the Anthropic
account is billed.

Writes `results/phaseb-qwen35a3b-*`, `results/phaseb-openai-*`,
`results/phaseb-qwen359b-*`, `results/phaseb-qwen38flash-*` only.

Judge is existing Anthropic `per_step` (uses `.env` ANTHROPIC key for
scoring, not for the CUA agent). If judge fails, keep the trajectory.
Do not run Gemini.

9B and Flash are **ablation / exploratory**, same as Stage 4. Do not
pool them with 35B-A3B / GPT as the primary matrix.

## Do not

- Rewrite SQL / file patches / `f004_hd_rank_flip` after seeing an answer.
- Drop a task because it failed or $\Delta S$ moved.
- Require every cell DONE. Not-DONE is a row (`DONE` = last `traj.jsonl`
  action `== "DONE"`).
- Use HPC / Slurm / abandoned 27B.
- Re-run Stage 4 cells to fish a prettier score.
- Start `PHASEB_LANE=claude` before the human says so.

## When a lane finishes

Paste, per task, base/CF: DONE or not, judge scores if present. Do not
classify Type A/B yourself beyond tracking vs score.
