# Gate 0A — task separation from Study 2 pool

**Status:** PASS  
**Date:** 2026-09-06

## Explicit exclusion (locked wording)

> **plant-token-terminate is a qualification-only smoke task and is excluded from the preregistered Study 2 task pool.**

Gate 0A exists to prove client-owned tool execution + terminal correctness on the generic substrate. It must **not** create prior exposure / contamination for confirmatory Study 2 tasks.

## What Gate 0A is

- Synthetic instruction: plant a unique token under `/tmp/GATE0A_*_TOKEN.txt`, `cat` via bash XML, then `computer_use terminate`.
- Not a MyPCBench sealed task ID.
- Not scored with Paper 2 STS / rubric \(S\).
- Not part of \(\mathcal{T}\).

## Checks performed

Against:

- `out/paper2_analysis_universe.json` (|T|=25)
- `out/paper2_cell_order.json` (order set-equal to analysis T)
- `paper/paper2_counterfactual_eval/registry/sealed_tasks.json` (seal |T|=27 before rejects)

| Needle | In analysis \(\mathcal{T}\) | In cell order | In sealed task blob |
| --- | --- | --- | --- |
| `gate0a` / `GATE0A` | no | no | no |
| `plant-token` / `plant_token` | no | no | no |
| `FLASHGATE` / `GPTGATE` / `CLAUDEGATE` | no | no | no |
| `prove tool ownership` | — | — | no |
| `/tmp/gate0a` | — | — | no |

Analysis \(\mathcal{T}\) IDs are MyPCBench families only (`aggregation-*`, `contradiction-*`, `counterfactual-*`, `preference_inference-*`, `retrieval-*`).

## Decision

- Task separation: **PASS**
- Study 2 preregistration must restate the exclusion above
- Do not add Gate 0A plant-token-terminate to any future confirmatory sample
