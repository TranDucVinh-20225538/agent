# Stage 4 Qwen3.5-27B — frozen tasks, qwen_cuabash, cu129 vLLM

You are on the **HPC Qwen node** (node004 / driver 560.35.03). Find the
MyPCBench agent repo (likely `/mnt/data2/Vinh/agent` or the clone that
already has `results/model-ladder/qwen35-cu12-smoke/report.json`).
Branch: `phase-a-results` after `git pull`.

Smoke **57943 already passed**: vLLM `0.27.1+cu129`, torch `2.13.0+cu129`,
model `Qwen/Qwen3.5-27B`, real GPU (~67 GiB `VLLM::EngineCore`).

This session proves the **QEMU datadir**, then runs **`retrieval-f001`
only** (baseline then CF). Same SQL / rubric / DVs as Claude. Do not
start f003 until f001 is a complete episode.

Different model size than the paper’s `Qwen3.5-35B-A3B`.

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
- Do not expand beyond the frozen four. This job is **f001 only**.
- Do not start f003/f018/f004 because vLLM is up.
- Do not treat 57946 / 57947 / 57951 empty dirs as Stage 4 cells.
- Do not start OpenAI or Claude jobs in this session.
- Do not `git pull` into a job that is already running.

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

`set -euo pipefail` + `source .env` must not abort if `.env` is absent
(HPC 57946 died there and a trap killed vLLM). `.env` is optional.

QEMU hostfwd on a shared node is not free by default. **57947 is not
Stage 4:** vLLM + image gate passed, then QEMU failed to bind
`127.0.0.1:16000`; eight cells crashed in ~50s with empty `traj`.

**57951 is not a failed experiment.** vLLM ready (371s), `/v1/models`
200, vision gate pass, QEMU process started, then died on:

`failed to find romfile "vgabios-virtio.bin"` (and `kvmvapic.bin`)

Those files exist under
`/data2/cmdir/home/toandq/MyPCBench/.opt/qemu/usr/share/qemu/`.
`env.py` launches `qemu-system-x86_64` with **no `-L`**, so a relocated
RPM extract cannot see its datadir. Empty `traj` / `no_bundle` / `0.0`
are not DVs.

The runner now wraps QEMU with `-L` (do not install a new QEMU, do not
touch KVM, do not change the model). TCG is fine.

```
MYPCBENCH_QEMU_EXTRACTED=/data2/cmdir/home/toandq/MyPCBench/.opt/qemu
QEMU_DATADIR=$MYPCBENCH_QEMU_EXTRACTED/usr/share/qemu
```

Runner defaults (override if still busy):

```
MYPCBENCH_HOST_SSH_PORT=18700
MYPCBENCH_HOST_VNC_PORT=5917
MYPCBENCH_HOST_API_PORT=12800
```

The script refuses to start if any of those three is already listening.
It also probes `-vga virtio` against that datadir, then a **dummy**
1-step boot. No first `traj` step → **STOP**. Do not start f001.

**This submit is f001 only** (`STAGE4_QWEN_TASKS=f001`). Do not start
f003/f018/f004 in the same job. If f001 baseline+CF both `DONE`, a later
job may set `STAGE4_QWEN_TASKS=f001,f003`. That is infrastructure
sequencing, not a sample shrink. Frozen four remain f001/f003/f018/f004.

---

## Gate 1 — screenshot, not text-only

Smoke 57943 proved **text**. `qwen_cuabash` sends **1280×800 screenshots**.

Before f001: one chat.completions call with a real MyPCBench screenshot
(or any 1280×800 PNG) through the same base URL. HTTP 200 and a non-empty
completion → continue. Image timeout / reject → **STOP**. Do not run
f001. Record `blocked_no_vision`. Do not fall back to Gemma.

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
export MYPCBENCH_QEMU_EXTRACTED=/data2/cmdir/home/toandq/MyPCBench/.opt/qemu
export STAGE4_QWEN_TASKS=f001
chmod +x scripts/stage4_qwen_run.sh scripts/qemu_datadir_wrap.sh
bash scripts/stage4_qwen_run.sh
```

Order for **this** job:

1. QEMU `-L` ROM probe
2. dummy 1-step smoke (`traj` has `step_num`)
3. `retrieval-f001` baseline then CF

**STOP** after f001. Do not start f003 in this allocation.

If f001 baseline has no traj step, **STOP** — boot/ROM/port, not a
task result. Do not `git pull` into a job that is already running.

---

## After f001

Confirm `results/stage4-qwen35-retrieval-f001/{base,cf}/` have non-empty
`traj.jsonl` with `DONE` on both cells, `gold_moved` on CF, and a judge
row. That is the pipeline proof (screenshot → action → traj → inject →
CF → judge).

Do **not** write a four-row `evidence_stage4_qwen35_results.md` from
f001 alone (missing tasks would look like failures).

If f001 is complete, a later job:

```
export STAGE4_QWEN_TASKS=f001,f003
```

f018/f004 stay in the frozen four; they are not this submit.

Commit **results only** on `phase-a-results`. Do not commit venvs, wheels,
`.env`, keys, qcow2.

```
Record Qwen3.5-27B qwen_cuabash f001 after QEMU -L datadir fix.

cu129 vLLM; same SQL as Claude; dirs stage4-qwen35-*. Not 57951.
```

---

## STOP

Do not launch Gemma, OpenAI, or a 35B job automatically.
Do not expand the benchmark.
End after the table is printed.
