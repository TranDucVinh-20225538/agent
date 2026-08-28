# Phase B.1 — validate the 10 frozen interventions, $0 agent

You are on **node30**. Workdir: `/mnt/data2/Vinh/agent`.
Branch: `phase-a-results`. Guest: official MyPCBench QEMU image. TCG is fine.
Persona: `michael.scott@dundermifflin.com`.

This session is **intervention validation**. It is not an experiment run.

```bash
cd /mnt/data2/Vinh/agent
git fetch origin
git checkout phase-a-results
git pull origin phase-a-results
git log -1 --oneline
# expect: 29f3eda Freeze the Phase B 10-task registry...
```

If HEAD is not `29f3eda` or a descendant that still contains
`scripts/phase_b_validate.sh`, stop and report. Do not invent files.

Then:

```bash
tmux new -s phase-b-validate   # or attach if it exists
bash scripts/phase_b_validate.sh
```

That script: dummy guest, one boot, snapshot `/data` + Tax_2025, restore
between tasks, apply each frozen $I$, write `out/phase_b_validate.md`.
It unsets Anthropic / OpenAI / OpenRouter keys. Do not export them back.

## Do

- Run all 10 frozen tasks, in registry order, via that script only.
- Leave `cf/phase_b_registry.json`, `cf/phase_b_interventions.json`, and
  `cf/stage4_locked.json` untouched.
- Record QEMU/tooling failures as failed execution.
- When the script exits, paste `out/phase_b_validate.md` and
  `results/phase_b_validate.log` tail (last ~80 lines).

## Do not

- SSH to HPC, submit Slurm, or use the abandoned Qwen 27B path.
- Run Claude / GPT / Qwen / Flash / 9B. That is Phase B.2, later.
- Call `judge_results.py`.
- Rewrite SQL, file replacements, or `f004_hd_rank_flip` because a
  task failed or $\Delta S$ would look nicer.
- Hand-edit HangryDash rankings in the UI then write a one-off UPDATE.
- Drop, add, or reorder tasks.
- Start B.2 even if 9/10 pass. Need **10/10 ok** in
  `out/phase_b_validate.md`.
- Commit unless the human asks. Validation artifacts stay on disk.

## Frozen universe (n=10)

1. `retrieval-f001`
2. `retrieval-f003`
3. `retrieval-f016`
4. `retrieval-f029` — dual-channel: sqlite **and** `w2_summary.txt`
5. `retrieval-f030` — Type B: charitable sqlite-only; 1099+file held
6. `aggregation-f003`
7. `aggregation-f018` — Type B: charitable + home-office sqlite-only
8. `preference_inference-f004` — `f004_hd_rank_flip`; TableFind held
9. `preference_inference-f018`
10. `counterfactual-f004`

Protocol: `out/PHASE_B.md`. Ledger: `cf/phase_b_freeze.json`.

If inject/tooling is broken, fix **inject code** only if the frozen $I$
is unchanged, then re-run the validate script. Do not change $I$.
