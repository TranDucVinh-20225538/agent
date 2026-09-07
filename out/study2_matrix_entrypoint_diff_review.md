# Study 2 matrix entrypoint — implementation diff / review

**Status:** IMPLEMENTED · dry-validated **PASS** · **matrix not launched**  
**Date (UTC):** 2026-09-06T17:23:46Z  
**Hierarchy:** canonical Paper 2 run path = generic OpenRouter executor (Gate 0A / native lanes = historical only)

---

## What was built (new files only)

| Path | Role |
| --- | --- |
| `scripts/study2_matrix.sh` | Full 171-leg entrypoint: Flash → GPT → Claude |
| `scripts/study2_matrix_lane.sh` | One family: `source` bind → `study2_exec_run.sh` |
| `scripts/study2_exec_run.sh` | 57-leg walker (cell_order / CF / judge / checkpoint); outs → `study2-*` |
| `scripts/study2_run_mypcbench.py` | Bridge: `build_qwen_cuabash_agent` + `OpenRouterChatCompletionsTransport` → `run_mypcbench` |
| `scripts/study2_matrix_dry_validate.py` | Inspect-only validation (no QEMU / no legs) |

**Touched (bind hygiene only):** `scripts/study2_bind_execution_key.sh` — also scrubs `GATE0A_*` so smoke namespace cannot leak into Study 2.

**Not modified:** signed Phase 4 prereg, protocol specs, roster, universe, N, seed, cell_order, model/family configs, Gate 0A scripts, Study 1 runners.

---

## Execution graph (canonical)

```text
bash scripts/study2_matrix.sh
  └─ source study2_bind_execution_key.sh   # 008…9dd; SMALL/Gate0A/Anthropic unset
  └─ for fam in flash gpt claude:
       study2_matrix_lane.sh $fam
         └─ source bind again
         └─ study2_exec_run.sh             # 57 legs, max_steps=80, timeout=7200
              └─ study2_run_mypcbench.py   # qwen_cuabash + OpenRouter transport
                   └─ run_mypcbench (QEMU / CF / traj / judge conventions)
```

Outputs only: `results/paper2_exec/study2-{flash,gpt,claude}`.

---

## Dry validation summary

Artifact: `out/study2_matrix_dry_validation.json` · **verdict: PASS**

| Check | Result |
| --- | --- |
| Runtime key | `sk-or-v1-008…9dd` via bind |
| SMALL / Gate0A / Anthropic | scrubbed / forbidden |
| Resolves to OpenRouter transport | `OpenRouterChatCompletionsTransport` × 3 |
| Agent factory | `build_qwen_cuabash_agent + install_transport` |
| Model IDs | Flash / GPT-5.5 / Claude Opus 4.6 match `FAMILY_CONFIGS` |
| Planned legs | **57 × 3 = 171** |
| Entrypoint scan (no Gate0A/SMALL/native launch) | clean |
| Study 2 result dirs | none (no legs run) |

---

## Launch command (not executed here)

```bash
cd /mnt/data2/Vinh/agent
bash scripts/study2_matrix.sh
```

---

## Non-actions (confirmed)

- No Study 2 matrix leg started  
- No prereg / protocol / roster / universe / N / seed edit  
- Gate 0A smoke not used  
