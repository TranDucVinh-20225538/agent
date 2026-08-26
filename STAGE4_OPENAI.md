# Stage 4 — OpenAI CUA (same frozen tasks as Claude)

Exploratory GPT run. Same 4 tasks, same SQL, same rubrics as Claude Opus
Stage 4. Result dirs are `results/stage4-openai-*` so Claude tables stay
untouched. This is not Qwen replication.

## 1. Put the key in (do not commit)

On the run host:

```bash
cd /mnt/data2/Vinh/agent   # or wherever the repo is
cp external/MyPCBench-main/.env.example external/MyPCBench-main/.env
# edit: OPENAI_API_KEY=sk-...
```

`external/MyPCBench-main/.env` is gitignored. Do not paste the key into
any tracked file.

If the account does not have `gpt-5.5`, set in that same `.env`:

```bash
MYPCBENCH_OPENAI_MODEL=gpt-4o
```

Paper default is `openai_cuabash` / `gpt-5.5`. Leave `OPENAI_BASE_URL`
unset (the runner unsets it so a leftover vLLM/Ollama URL cannot steal
the call).

## 2. Run

```bash
chmod +x scripts/stage4_openai_run.sh
bash scripts/stage4_openai_run.sh
```

Order (same as Claude): f001 → f003 → f018 → f004. Each is baseline then
counterfactual. Judge is Anthropic `per_step` if `ANTHROPIC_API_KEY` is
still in `.env`; otherwise OpenAI `per_step`.

## 3. After it stops

```
out/evidence_stage4_openai_results.md
results/stage4-openai-retrieval-f001/{base,cf}/
results/stage4-openai-aggregation-f003/{base,cf}/
results/stage4-openai-preference_inference-f018/{base,cf}/
results/stage4-openai-counterfactual-f004/{base,cf}/
```

f004: if baseline has no DONE, record `technical_failure` / `failure` and
do not use it for attribution (same rule as Claude).
