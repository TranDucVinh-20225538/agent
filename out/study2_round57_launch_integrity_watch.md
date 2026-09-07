# Study 2 Round-57 — launch + early integrity watch

**Status:** Matrix **RUNNING** after Round-57 preflight **PASS**  
**Launch (UTC):** 2026-09-06T17:36:59Z  
**Entrypoint:** `bash scripts/study2_matrix.sh` (via `study2_matrix_detached_launch.sh`)  
**Log:** `results/paper2_exec_study2_matrix.log`

## Preflight (before leg 1)

| Check | Result |
| --- | --- |
| A live balance `008…9dd` | PASS — `limit_remaining≈$1268.49` |
| B shared executor evidence | Recorded (not a gate) — all 3 families → `study2_run_mypcbench` → `build_qwen_cuabash_agent` + `OpenRouterChatCompletionsTransport` |
| C universe/order vs locked manifest | PASS — prereg sha `6803c643…`, T=25, multiI=7, N_fam=57, L=171, seed `20260904`, first=`retrieval-f010` |

Artifacts: `out/study2_round57_preflight.{json,md}`

## Early integrity (leg 1 start)

| Signal | Observed |
| --- | --- |
| Bind | `sk-or-v1-008…9dd`; SMALL/Gate0A/Anthropic unset |
| Model | `qwen/qwen3.8-flash` |
| Bridge | `study2_run_mypcbench.py` → `qwen_cuabash+OpenRouterChatCompletions` |
| Task | `retrieval-f010` G0 (probe) |
| Out | `results/paper2_exec/study2-flash` |
| QEMU | started (`mypcbench-study2-flash`, TCG — slow boot expected) |
| Hard fail | none as of watch |
| Schedule | continues Flash → GPT → Claude automatically if integrity holds |

Prior incomplete attempt (17:26, no Round-57) archived under `*.pre_round57_*` / `*-incomplete-pre-round57-*`.

## Policy

Monitor integrity only for first 1–2 task units; continue locked schedule if healthy. Stop only on infra/protocol failure. No outcome interpretation / method retune.
