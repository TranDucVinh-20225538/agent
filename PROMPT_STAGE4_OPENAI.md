# Stage 4 OpenAI — same frozen tasks as Claude, GPT CUA

You are on **node30**. Workdir: `/mnt/data2/Vinh/agent`. Branch: `phase-a-results`.
Guest: official MyPCBench QEMU image. TCG is fine.
Persona: `michael.scott@dundermifflin.com`.

This session spends **OpenAI**. It is exploratory cross-model transfer
under the **same frozen task/intervention protocol** as Claude Stage 4.

Label every artifact:

> Exploratory GPT CUA (`openai_cuabash`) under the same frozen
> tasks, SQL, rubric, and DVs as Claude Opus Stage 4. Different model
> and agent interface. Not confirmatory Qwen replication.

---

## Do not

- Do not print, log, or commit `OPENAI_API_KEY` / `.env`.
- Do not overwrite `results/stage4-retrieval-f001/` (Claude) or any
  `results/stage4-<task>/` without the `openai` infix.
- Do not write into `results/stage4-qwen-p1-*`.
- Do not change eligibility, sample, SQL, rubric, or gold.
- Do not emulate `qwen_cuabash` or XML `computer_use`.
- Do not run Gemini.
- Do not run Qwen, Gemma, olmOCR, or a fifth task.
- Do not promote reserves (`retrieval-f003`, `retrieval-f016`).
- Do not run confounded sample members (f029, f030, aggregation-f018,
  preference_inference-f004).
- Do not start another model after these four finish.

---

## Agent

- Type: `openai_cuabash`
- Model: `MYPCBENCH_OPENAI_MODEL` from `.env`, else **`gpt-5.5`**
- If `gpt-5.5` returns model-not-found, set `MYPCBENCH_OPENAI_MODEL=gpt-4o`
  in `.env` once, record the substitution, and continue. Do not shop
  other model ids.
- Unset `OPENAI_BASE_URL` so calls go to api.openai.com (the shell
  wrapper already unsets it).
- Judge: `MYPCBENCH_JUDGE_FLAVOR=per_step`. Use Anthropic if
  `ANTHROPIC_API_KEY` is present; otherwise OpenAI. Score is auxiliary.

DVs (unchanged from Claude Stage 4):

- Primary: **score invariant** if gold moved and both cells complete.
- Separate: **tracking** from the final answer, not from the score.
- `technical_failure` / no DONE is **not** a negative attribution result.
- `counterfactual-f004`: if baseline has no usable DV, leave it out of
  inference (same as Claude).

Locked SQL: `cf/stage4_locked.json` / `cf/interventions.json`.
f018 CF uses `status='settled'`, not `closed`.

---

## Before the run

```bash
cd /mnt/data2/Vinh/agent
git pull origin phase-a-results
cd external/MyPCBench-main
set -a && source .env && set +a
if [ -z "$OPENAI_API_KEY" ]; then echo FAIL: OPENAI_API_KEY empty; exit 1; fi
echo "OPENAI_API_KEY set? yes"
echo "model=${MYPCBENCH_OPENAI_MODEL:-gpt-5.5}"
# never echo the key
```

Confirm `scripts/stage4_openai_run.sh` exists. Do not re-run
`evidence_screen.py`.

---

## Run

```bash
cd /mnt/data2/Vinh/agent
chmod +x scripts/stage4_openai_run.sh
bash scripts/stage4_openai_run.sh
```

That wrapper already:

1. Pins each frozen rubric into `tasks/cf_one/one.json`
2. Baseline `MYPCBENCH_CF_PROBE_ONLY=1`, then CF with the locked patch
3. Archives to `results/stage4-openai-<task>/{base,cf}/`
4. Writes `out/evidence_stage4_openai_results.md`

Order (do not reorder):

1. `retrieval-f001`
2. `aggregation-f003`
3. `preference_inference-f018`
4. `counterfactual-f004`

If one pair technically fails, record it and continue to the next of
the four. Do not substitute another task.

---

## After all four pairs finish

Write/confirm:

- `out/evidence_stage4_openai_results.md`
- `out/evidence_stage4_openai_results.csv`

For each task report: episode completion, baseline DV, CF DV, whether
gold moved, score base→CF, tracking, status
(`ok` / `null` / `failure` / `technical_failure`).

Commit **results only** on `phase-a-results`. Do **not** stage `.env`,
keys, qcow2, or `__pycache__`.

```
Record exploratory OpenAI CUA on the four frozen Stage 4 tasks.

Same SQL and sample as Claude; result dirs are stage4-openai-*.
```

Push `phase-a-results`. Print `git rev-parse HEAD` and the four-row table.

---

## STOP

Do not launch Claude, Qwen, or Gemma.
Do not expand the benchmark.
End the session after the commit is pushed and the table is printed.
