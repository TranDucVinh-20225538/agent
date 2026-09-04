# Paper 2 — API lane routing prompts (verify-only)

**Commit:** `7cb434f` (`phase-a-results`)  
**Analysis universe:** amended pre-cell-1 (f024 rejected); `out/paper2_analysis_universe.md`  
**Manifest:** `paper/paper2_counterfactual_eval/EXECUTION_MANIFEST.md`  
**Cell order:** `out/paper2_cell_order.json` (seed `20260904`, |T|=25, set-equal to analysis T; **no f024**)

**Cursor scope until human OK:** freeze / verify / fill image block only.  
**Do not** start any agent cell, smoke that spends analysis budget, or edit \(\mathcal{M}\)/\(\mathcal{T}\)/\(D\).

---

## Preflight verify (node30 @ `7cb434f`)

| Check | Result |
| --- | --- |
| HEAD | `7cb434f` |
| `paper2_cell_order.json` ↔ analysis T | set-equal, n=25 |
| Legs | 228 = 4×25×2 + 4×7 |
| Legs/model | 57 = 25×2+7 |
| multi-I (both PASS) | 7 tasks |
| `contradiction-f024` | rejected; **absent** from T and cell_order |
| Image block | filled: `mypcbench.qcow2` sha256 `7c2ddcf2…2f43f59` @ node30 |
| SMALL/LARGE split | wire `OPENROUTER_API_KEY_SMALL` / `_LARGE` (names only in git); no silent failover |

Model order (immutable): **9B → Flash → Claude → GPT**.

---

## Prompt A — `SMALL_KEY` lane

```text
You are on the Paper 2 run host at 7cb434f (phase-a-results).

READ ONLY / VERIFY PLAN — do not run any agent until I explicitly OK after reviewing your diff.

Sources of truth:
- paper/paper2_counterfactual_eval/EXECUTION_MANIFEST.md
- out/paper2_analysis_universe.md
- out/paper2_cell_order.json  (|T|=25, no f024)
- cf/paper2_interventions.json (PASS / READY_* variants only)

Your lane: SMALL_KEY only.
- Models in order: (1) qwen/qwen3.5-9b  (2) qwen/qwen3.8-flash
- Env: OPENROUTER_API_KEY_SMALL → bind as OPENROUTER_API_KEY for the process.
  unset ANTHROPIC_API_KEY OPENAI_API_KEY OPENROUTER_API_KEY_LARGE
- 57 legs/model (25×2+7). Full universe per model; no interleaving with Claude/GPT.
- Task order: out/paper2_cell_order.json. Per multi-I: G0 → G1(I1) → G2(I2).
- Harness freeze: max_steps=80, timeout=7200, MYPCBENCH_VM_READY_TIMEOUT=3600,
  MYPCBENCH_SKIP_QCOW2_REFRESH=1, clean guest/snapshot between legs.
- On SMALL_KEY exhaustion: checkpoint, stop, report — no silent failover to LARGE_KEY.

Deliverable now (diff for me to OK):
1) Confirm HEAD + cell_order set-equal to analysis T (25, no f024, 228 legs).
2) Fill EXECUTION_MANIFEST image block: path, sha256, recorded_at_utc, host.
3) Show shell/env plan for model 1 (9B) — names not values — no execution.
4) Do not start cell 1.
```

---

## Prompt B — `LARGE_KEY` lane

```text
You are on the Paper 2 run host at 7cb434f (phase-a-results).

READ ONLY / VERIFY PLAN — do not run any agent until I explicitly OK after reviewing your diff.

Sources of truth: same as SMALL lane (|T|=25, 228 legs, no f024).

Your lane: LARGE_KEY only.
- Models after SMALL finishes (or separate host / no shared QEMU ports):
  (3) claude-opus-4-6  (4) gpt-5.5
- Env: ANTHROPIC_API_KEY for Claude; OPENAI_API_KEY for GPT.
  Never OPENROUTER_API_KEY_SMALL. Optional OPENROUTER_API_KEY_LARGE never for Qwen.
- 57 legs/model. Same cell_order.json. Multi-I: G0 → G1 → G2.
- Same harness freeze as manifest. Clean guest between legs.

Deliverable now:
1) Confirm image sha256 matches SMALL-lane record (same qcow2).
2) Show shell/env plan for Claude first — no execution.
3) Do not start any Claude/GPT cell until I OK.
```

---

## Human gate

1. Review image SHA + routing diff.  
2. Reply **OK** (or amend).  
3. Only then: start SMALL lane cell 1 / LARGE lane.
