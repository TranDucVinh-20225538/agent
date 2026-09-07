# Claude review prompt — Gate 0A Flash diagnostic

You are an independent reviewer. Cursor prepared evidence only and did **not** answer the questions below.

## Context

- Bundle: `out/gate0a_flash_diagnostic_handoff/`
- Git commit: `aa060b2f09a94e8dbe4fc31632f5adf4de93aa55`
- Model: `qwen/qwen3.8-flash` via OpenRouter stateless `/chat/completions`
- Freeze: 26 checkpointed legs; DONE=8; TERMINAL_FAIL=18
- **Gate 0A is pilot diagnostic data only and must not be used as Study 2 measurement data.**

## Required reading order

1. `README.md`
2. `protocol_contract.md`
3. `failure_summary.json` + `failure_taxonomy.md`
4. `representative_trajectories/*/transcript_sanitized.jsonl` (raw response → parsed action → executor decision)
5. `step_limit_cases.md`
6. `transport_evidence.md`
7. `executor_invariant_check.md`

## Critical evidence rule

For each failure class, ground claims in the **three layers** preserved in transcripts:

1. model raw response
2. parsed / executor-facing action
3. executor decision (EMPTY_XML / TOOL_CALL / execute / PREDICT_CRASH / stop)

Do **not** infer from checkpoint label `TERMINAL_FAIL` alone.
Do **not** treat rubric scores as task completion.

## Questions (answer independently)

1. What is the dominant failure mechanism?
2. Is there evidence of an executor bug?
3. Which failures are protocol/parser brittleness?
4. Which failures are stopping-semantics failures?
5. Which failures appear genuinely model/provider-related?
6. Is there enough evidence to stop Gate 0A early? Why?
7. What is the smallest model-neutral protocol revision worth considering?
8. Which proposed changes would constitute prohibited model-specific tuning?
9. Should Flash be rerun under a revised protocol before screening GPT/Claude families?

Also classify dominance among: (A) executor implementation, (B) parser/protocol brittleness, (C) stopping semantics, (D) model capability/behavior, (E) provider/infrastructure.

## Constraints on recommendations

- Prefer **model-neutral** protocol/executor clarifications.
- Flag any suggestion that is Flash-/Qwen-specific prompting as prohibited tuning for Gate 0.
