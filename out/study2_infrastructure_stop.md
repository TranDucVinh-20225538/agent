# Study 2 — INFRASTRUCTURE STOP (matrix not started)

**Status:** **STOPPED before any main-matrix leg**  
**Time (UTC):** 2026-09-06T17:07:11Z  
**Rule applied:** stop on transport/runtime/**infrastructure** failure — do not silently invent method, retry, or retune  

---

## Stop reason

The locked pre-launch path defines **what** to run (manifest + cell order + bind script) but does **not** provide a Study 2 **matrix execution entrypoint** that:

1. sources `scripts/study2_bind_execution_key.sh` (008…9dd), and  
2. walks the frozen 57-leg schedule into `results/paper2_exec/study2-{flash,gpt,claude}`, and  
3. drives the Gate −2 / generic-executor OpenRouter substrate for **all three** locked model IDs.

**Observed:** the only `scripts/study2*.sh` file is `study2_bind_execution_key.sh` (bind/verify only; explicitly “Does not start matrix legs”).

**Not used (per lock / human rule):**

- Gate 0A smoke launchers (`paper2_gate0a_*`) — SMALL bind  
- `paper2_exec_small_lane.sh` — SMALL bind  
- Ad-hoc reuse of `paper2_exec_run.sh` / `paper2_exec_large_lane.sh` without a locked Study 2 wrapper — LARGE lane is native Anthropic/OpenAI, not the OpenRouter 008 path proven at Gate 0A for GPT/Claude

---

## Integrity checks performed (no legs)

| Check | Result |
| --- | --- |
| Bind `008…9dd` | PASS |
| SMALL unset after bind | PASS |
| `results/paper2_exec/study2*` present | none |
| Main-matrix CHECKPOINT | none |
| Matrix legs started | **0** |
| Preregistration / schedule / protocol edited | **No** |

---

## What was not done

- No QEMU Study 2 leg  
- No model outcome interpretation  
- No schedule/prereg/protocol change  
- No silent substitute launcher  

---

## Required unblocking action (ops — human/agent follow-up)

Provide or authorize a **Study 2 matrix launcher** that is explicitly the locked execution path (bind → Flash 57 → GPT 57 → Claude 57, outs under `study2-*`, max_steps/timeout = Study 1 confirmatory settings, OpenRouter transport for all three). Until that entrypoint exists and is designated as the launch script, the matrix remains **READY_TO_LAUNCH in intent** but **not executable without inventing infrastructure**.

Companion order report: `out/study2_locked_execution_order_report.md`

---

## Explore confirmation (post-stop)

[Explore Study 2 matrix run path](77857390-b467-4093-9184-0d581a773679) independently confirmed the same blocker: no in-tree Study 2 matrix runner; reuse Study 1 `paper2_exec_run.sh` leg walk (`max_steps=80`, `timeout=7200`) only after a **new** bind→generic-executor+OpenRouter bridge exists; Gate 0A smoke remains SMALL + plant-token only. No change to stop disposition.
