# Stage 4 Qwen3.5-35B-A3B — OpenRouter, qwen_cuabash, node30 QEMU

You are on **node30**. Workdir: `/mnt/data2/Vinh/agent`. Branch: `phase-a-results`.

HPC Qwen (node004 / 27B / vLLM) is **abandoned**. Do not wait for
57948/57951. `scancel` any leftover job. This OpenRouter path is the
Qwen lane.

Text smoke (`"OK"`, ~$0.00014) already passed. That is **not** Stage 4.
Next is a **vision + CUA XML** gate, then **`retrieval-f001` only**.

Label:

> Qwen3.5-35B-A3B (paper id) via OpenRouter + `qwen_cuabash` under
> the same frozen SQL as Claude. Hosted weights, local QEMU.
> Not HPC 27B. Not `qwen-plus` chat. Not GPT.

---

## Do not

- Do not start all four tasks because text smoke returned `"OK"`.
- Do not put the OpenRouter key in `external/MyPCBench-main/.env`
  (that file has the GPT `sk-proj-` key). Export `OPENROUTER_API_KEY`
  in this process only. After `source .env`, the wrapper **overrides**
  `OPENAI_API_KEY`.
- Do not overwrite Claude `results/stage4-<task>/`, GPT
  `results/stage4-openai-*`, or HPC `results/stage4-qwen35-*`.
- Write `results/stage4-qwen35a3b-*` only.
- Do not use `scripts/stage4_qwen_run.sh` (HPC `-L` wrap).
- Do not echo keys.

---

## Gate (must pass before f001)

```bash
cd /mnt/data2/Vinh/agent
git pull origin phase-a-results
export OPENROUTER_API_KEY='sk-or-...'   # process only; never echo
export OPENAI_BASE_URL=https://openrouter.ai/api/v1
export OPENAI_API_KEY="$OPENROUTER_API_KEY"
export MYPCBENCH_QWEN_MODEL=qwen/qwen3.5-35b-a3b
python3 scripts/qwen_vision_gate.py
```

Need HTTP 200 and a reply containing `<tool_call>` / `computer_use` /
`bash`. Caption-only or `"OK"` → **STOP** (`blocked_no_vision`).

---

## Run f001 only

```bash
export OPENROUTER_API_KEY='sk-or-...'
export STAGE4_QWEN_TASKS=f001
chmod +x scripts/stage4_qwen_openrouter_run.sh
bash scripts/stage4_qwen_openrouter_run.sh
```

The wrapper sources `.env` (GPT key + Anthropic judge) then replaces
`OPENAI_API_KEY` with OpenRouter. GPT `sk-proj-` stays on disk.

If f001 base+CF both `DONE`, a later job may set
`STAGE4_QWEN_TASKS=f001,f003`. Frozen four remain four; this is the
same sequencing as HPC, not a sample shrink.

---

## STOP

Do not launch Gemma, a 27B mix-in, or f018/f004 in this job.
Do not `git pull` into a running job.
