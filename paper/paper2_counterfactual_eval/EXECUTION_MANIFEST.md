# Paper 2 — execution manifest (freeze before cell 1/236)

**Status:** EXECUTION_FROZEN — design closed; agent failure is data.  
**Analysis universe:** `out/paper2_analysis_universe.md` (`4f45faf`)  
**Spec:** `paper/paper2_counterfactual_eval/PAPER2_SPEC.md`  
**Do not** edit \(\mathcal{M}\), \(\mathcal{T}\), \(D\), or this file after cell 1 starts, except dated infra stop (below).

---

## Commitment

| Quantity | Value |
| --- | --- |
| \(\|\mathcal{M}\|\) | 4 |
| \(\|\mathcal{T}\|\) | 26 |
| Surviving variants | 33 |
| multi-I (I1+I2) | 7 |
| **Legs** | **236** = \(4\times26\times2 + 4\times7\) |

From cell 1 onward: stop only for **infrastructure** severe enough to halt the whole experiment (Control API dead, disk full, systematic harness bug). Not for “model looks bad / expensive / empty XML rate.”

---

## 0. API lane routing (operational — does not change \(\mathcal{M}\)/\(\mathcal{T}\)/\(D\))

Two OpenRouter-capable budget lanes. **No raw keys in repo/logs** — env vars only.

| Lane | Env (example) | Models |
| --- | --- | --- |
| `SMALL_KEY` | e.g. `OPENROUTER_API_KEY_SMALL` | `qwen/qwen3.5-9b`, `qwen/qwen3.8-flash` only |
| `LARGE_KEY` | e.g. `OPENROUTER_API_KEY_LARGE` / Anthropic+OpenAI native keys | `claude-opus-4-6`, `gpt-5.5` only |

**Model order (full universe per model, no interleaving):**  
1. Qwen 3.5-9B → 2. Qwen 3.8-Flash → 3. Claude Opus 4.6 → 4. GPT-5.5  

**59 legs/model** (\(26\times2+7\)); **236** total. Within a model lane, key assignment is immutable. Claude/GPT never use `SMALL_KEY`. Exhausting `SMALL_KEY` mid-Qwen: checkpoint, stop, report — **no silent failover to `LARGE_KEY`** without an explicit dated operational amendment. Smoke/cost checks are **not** analysis legs.

---

## 1. Harness freeze

| Knob | Frozen value |
| --- | --- |
| Branch / analysis commit | `phase-a-results` @ `4f45faf` (or later **execution-only** commits that do not change \(\mathcal{M}\)/\(\mathcal{T}\)/\(D\)) |
| Models | `claude-opus-4-6` / `claude_cuabash` / Anthropic (`LARGE_KEY` lane) |
|  | `gpt-5.5` / `openai_cuabash` / OpenAI direct (`LARGE_KEY` lane) |
|  | `qwen/qwen3.8-flash` / `qwen_cuabash` / OpenRouter (`SMALL_KEY` lane) |
|  | `qwen/qwen3.5-9b` / `qwen_cuabash` / OpenRouter (`SMALL_KEY` lane) |
| Runner pattern | Paper 1 Stage-4 / Phase-B shells: `run_mypcbench.py --backend qemu` |
| `max_steps` | **80** |
| `timeout` | **7200** s |
| `MYPCBENCH_VM_READY_TIMEOUT` | **3600** |
| `MYPCBENCH_SKIP_QCOW2_REFRESH` | **1** |
| Inject | `scripts/cf_inject.py` + `cf/paper2_interventions.json` (PASS variants only) |
| Judge | `judge_results.py`, `MYPCBENCH_JUDGE_FLAVOR=per_step` (score only; not STS) |
| Persona | `michael.scott@dundermifflin.com` |
| Image | Record `MYPCBENCH_QCOW2` path + sha256 **before cell 1** on the run host (fill below) |

**Image (fill on run host before cell 1):**

```
MYPCBENCH_QCOW2=
sha256=
recorded_at_utc=
host=
```

System prompt / tool config: whatever each `*_cuabash` agent ships in this checkout at the tagged execution commit — do not edit agent wrappers mid-run.

---

## 2. Seed freeze

| Seed | Value | Role |
| --- | --- | --- |
| `PAPER2_EXEC_SEED` | **20260904** | Master seed (new; not `20260826`, not multi-I inventory seed alone) |
| Task order | `Random(PAPER2_EXEC_SEED).shuffle(sorted(T))` once, written to `out/paper2_cell_order.json` **before** cell 1 | Fixed schedule |
| Multi-I order | For each multi-I task: legs `G0` → `G1`(I1) → `G2`(I2) in that order; tasks still follow cell order | No fishing I2 first |
| Episode / env RNG | If harness exposes a seed, set from `PAPER2_EXEC_SEED` + `(model, task, leg)` hash; if not, record “harness-default” per leg | No silent mid-run change |

Write `out/paper2_cell_order.json` and this filled image block **before** the first agent call.

---

## 3. Cell execution policy

| Rule | Frozen choice |
| --- | --- |
| Runs per cell | **1** (one trajectory per `(M, T, leg)`) |
| Legs per task | Base: `G0` then `G1` (I1). Multi-I: then `G2` (I2). Clean guest / snapshot restore between legs (same hygiene as inject-probe) |
| Infra retry (Control API down, QEMU won’t boot, disk I/O) | **At most 1** retry, **same** seed / same cell id; log `infra_retry=1` |
| Agent failure (EMPTY_XML, STEP_LIMIT, AGENT_FAIL, non-DONE) | **No retry** — record as execution failure; not tracking miss; not a reason to drop model |
| API 429 / transient provider error | Treat as infra: ≤1 retry same seed; if still fail → technical failure for that leg |
| Interrupted mid-leg | **Rerun from start** of that leg on clean guest; do not resume mid-trajectory |
| Partial schedule | Do not drop remaining models/tasks to “finish faster.” Pause whole experiment if needed; resume same cell order |

Valid pair (analysis): both legs of a scheduled pair `DONE` (Paper 1 definition). Incomplete ≠ \(Y=0\).

---

## 4. Workflow

1. Tag: `paper2-exec-freeze` on the commit that contains this file + filled image sha + `paper2_cell_order.json`.  
2. Run all **236** legs (or pause only for infra stop).  
3. Collect raw artifacts under a single tree (e.g. `results/paper2_exec/`).  
4. Classify valid pairs / coverage.  
5. **Then** open Layer A / Layer B.

Allowed mid-run monitors: API health, disk, QEMU, corrupted artifacts.  
Forbidden mid-run: STS, \(\Delta S\), ranks, swapping models, rewriting \(D\) or interventions.

---

## 5. Infra stop (only halt condition)

Stop the full experiment if and only if continuing would invalidate comparability (wrong image, wrong inject file, systematic harness corruption). File a dated note; do not quietly change \(\mathcal{M}\) or \(\mathcal{T}\).
