# Study 2 preflight — Gate 0A closed; roster LOCK

**Date:** 2026-09-06  
**Protocol freeze ancestry:** `dd43cbe` (Phase 1B) · Gate 0A v1.1 lock `a7c7a45`+  
**Cross-family tip (Claude wrapper):** `22831c9`  
**Gate 0A status:** COMPLETE — do not retune budget / prompt / model selection.

## Roster LOCK

| Family | Candidate | Status |
| --- | --- | --- |
| Qwen | `qwen/qwen3.8-flash` | **Qualified** |
| OpenAI | `openai/gpt-5.5` | **Qualified** |
| Anthropic | `anthropic/claude-opus-4.6` | **Qualified** |

Rules:

- Do **not** rank by DONE@ turn count.
- Do **not** drop a family after Gate 0A PASS.
- Do **not** retest Gate 0A to optimize turn count.
- Gate 0A does not choose Study 2 analysis winners; it only qualifies the substrate.

## Remaining gates before Study 2 main legs

| # | Gate | Artifact |
| --- | --- | --- |
| 1 | P1 sha-match consistency audit | `out/gate0a_p1_consistency_audit.md` |
| 2 | Task separation (Gate 0A ∉ Study 2 pool) | `out/gate0a_task_separation.md` |
| 3 | Phase 4 preregistration (method lock) | `out/study2_phase4_preregistration.md` |
| 4 | Cost-per-leg → lock N | `out/study2_cost_per_leg.md` |

Then: lock prereg + N/matrix → start Study 2 pipeline.

**Not next:** Gate 0A v1.2, prompt/budget/model churn, matrix start.
