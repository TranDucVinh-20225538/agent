# Stage 4 Qwen3.5-27B — frozen tasks, qwen_cuabash, cu129 vLLM

You are on the **HPC Qwen node** (node004 / driver 560.35.03). Find the
MyPCBench agent repo (likely `/mnt/data2/Vinh/agent` or the clone that
already has `results/model-ladder/qwen35-cu12-smoke/report.json`).
Branch: `phase-a-results` after `git pull`.

Smoke **57943 already passed**: vLLM `0.27.1+cu129`, torch `2.13.0+cu129`,
model `Qwen/Qwen3.5-27B`, real GPU (~67 GiB `VLLM::EngineCore`).

This session runs the **four frozen Stage 4 tasks** through
`qwen_cuabash`. Same SQL / rubric / DVs as Claude. Different model size
than the paper’s `Qwen3.5-35B-A3B`.

Label every artifact:

> Qwen3.5-27B via qwen_cuabash under the same frozen
> task/intervention protocol as Claude Stage 4. Same SQL and sample.
> Not paper 35B-A3B. Not Lane B Gemma. Not a CUDA-13 stack.

---

## Do not

- Do not use `.venv-vllm`, conda, or any **cu130** wheel.
- Do not use Ollama / Gemma / olmOCR.
- Do not overwrite `results/stage4-<task>/` (Claude) or
  `results/stage4-openai-*`.
- Do not write `results/stage4-qwen-p1-*` (use `stage4-qwen35-*`).
- Do not change eligibility, sample, SQL, rubric, or gold.
- Do not emulate a different tool XML than `qwen_cuabash`.
- Do not run Gemini as the agent.
- Do not expand beyond the four tasks.
- Do not start OpenAI or Claude jobs in this session.

---

## Stack (locked)

| | |
| --- | --- |
| venv | `.venv-qwen35-cu12-test` **only** for vLLM |
| vLLM | `0.27.1+cu129` |
| torch | `2.13.0+cu129` |
| Agent python | MyPCBench `external/MyPCBench-main/.venv` |
| Agent | `qwen_cuabash` |
| Model | `Qwen/Qwen3.5-27B` |
| Endpoint | `OPENAI_BASE_URL=http://127.0.0.1:8000/v1` |
| API key | `dummy` (local vLLM) |

Harness runner: `scripts/stage4_qwen_run.sh` after vLLM is healthy.

TCG is fine if `/dev/kvm` is not writable.

---

## Gate 0 — vLLM still on GPU

```bash
nvidia-smi
curl -s "$OPENAI_BASE_URL/models"
```

Must see `VLLM::EngineCore` with tens of GiB, **not** 4 MiB idle.
If the smoke server died, restart **only** from the cu129 venv that
passed 57943. Do not invent a new wheel.

If `/v1/models` is down, start vLLM then wait for
`Application startup complete`:

```bash
source .venv-qwen35-cu12-test/bin/activate
vllm serve Qwen/Qwen3.5-27B \
  --served-model-name Qwen/Qwen3.5-27B \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.90 \
  --max-model-len 12288 --max-num-seqs 1 \
  --port 8000 --trust-remote-code
```

Keep this process alive for the whole Stage 4 run.

---

## Gate 1 — screenshot, not text-only

Smoke 57943 proved **text**. `qwen_cuabash` sends **1280×800 screenshots**.

Before f001: one chat.completions call with a real MyPCBench screenshot
(or any 1280×800 PNG) through the same base URL. HTTP 200 and a non-empty
completion → continue. Image timeout / reject → **STOP**. Do not run the
four tasks. Record `blocked_no_vision`. Do not fall back to Gemma.

---

## DVs (same as Claude)

- Primary: **score invariant** if `gold_moved` and both cells complete.
- Separate: **tracking** from the final answer.
- No DONE / inject fail → `technical_failure`, not “P1 failed”.
- `counterfactual-f004`: no baseline DV → out of inference.

Locked SQL: `cf/stage4_locked.json`. f018 CF uses `status='settled'`.

Judge: `MYPCBENCH_JUDGE_FLAVOR=per_step`. Prefer Anthropic if
`ANTHROPIC_API_KEY` is already in MyPCBench `.env` (comparable to Claude
Stage 4). Do not switch the judge model after seeing scores.

---

## Run

```bash
cd <agent-repo>
git pull origin phase-a-results
export OPENAI_BASE_URL=http://127.0.0.1:8000/v1
export OPENAI_API_KEY=dummy
export MYPCBENCH_QWEN_MODEL=Qwen/Qwen3.5-27B
chmod +x scripts/stage4_qwen_run.sh
bash scripts/stage4_qwen_run.sh
```

Order (do not reorder):

1. `retrieval-f001`
2. `aggregation-f003`
3. `preference_inference-f018`
4. `counterfactual-f004`

Each: baseline (probe-only) then CF. If one pair technically fails,
record and continue. Do not substitute tasks.

---

## After all four pairs

Confirm:

- `out/evidence_stage4_qwen35_results.md`
- `out/evidence_stage4_qwen35_results.csv`
- `results/stage4-qwen35-<task>/{base,cf}/`

Report per task: completion, gold_moved, baseline DV, CF DV, score
base→CF, tracking, status.

Commit **results only** on `phase-a-results`. Do not commit venvs, wheels,
`.env`, keys, qcow2.

```
Record Qwen3.5-27B qwen_cuabash on the four frozen Stage 4 tasks.

cu129 vLLM; same SQL as Claude; dirs stage4-qwen35-*.
```

Push. Print `git rev-parse HEAD` and the four-row table.

---

## STOP

Do not launch Gemma, OpenAI, or a 35B job automatically.
Do not expand the benchmark.
End after the table is printed.
