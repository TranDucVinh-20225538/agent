# Phase 1B review — five invariants before Gate 0A

**Base:** `96415d5` (+ review hardening commit)  
**Scope:** mock HTTP only — no API, no QEMU, no Gate 0  
**Tests:** `python3 -m unittest tests.test_phase1b_review_invariants` (+ full Phase 1 suite = 29 OK)

## Verdict

| # | Invariant | Result |
| --- | --- | --- |
| 1 | Full-history semantics | **PASS** |
| 2 | Family config transport-only | **PASS** |
| 3 | OpenRouter extraction fail-closed | **PASS** |
| 4 | Stateless complete requests | **PASS** |
| 5 | Flash Gate 0A binding exactness | **PASS** |

**Phase 1B review: PASS.** Eligible for Gate 0A Flash after independent ack — not auto-started here.

---

### 1. Full-history semantics

Evidence: `test_1_full_history_bash_then_done`

Turn-2 OpenRouter body contains:

- system with frozen `computer_use` + `1000x1000` + bash addendum;
- original task token;
- turn-1 assistant bash XML (`<function=bash>`, `echo hello_from_bash`);
- frozen bash injection `<tool_response>…FAKE_BASH_OK…`;
- ≥1 screenshot `image_url` on turn 1; turn 2 image count ≥ turn 1.

Also: `test_1_transport_does_not_mutate_caller_history` — `complete()` deep-copies messages.

### 2. Family config does not change protocol

Evidence: `assert_family_configs_transport_only` + `test_2_*`

`FamilyConfig` fields only: `family`, `openrouter_model`, `allow_keys`, `extra_body`, `notes`.  
Forbidden in config: system prompt, action schema, parser, stopping rule, observation cadence, `tools`, `previous_response_id`.  
`extra_body` for Flash is only `chat_template_kwargs.enable_thinking` (generation knob).

### 3. Response extraction fail-closed

Evidence: `test_3_extraction_matrix`

Fails closed on: `choices=[]`, missing message, `content=None`, blank content, refusal-only, `tool_calls` (with or without content), non-object payload.  
Provider `tool_calls` are **never** converted into XML actions.

### 4. Stateless request completeness

Evidence: `test_4_stateless_request2_self_contained`

Request 2 embeds request-1 context (SYS + TASK + A1 + new obs).  
Absent: `previous_response_id`, `conversation_id`, `response_id`, `tools`.

### 5. Flash candidate binding

Evidence: `flash_gate0_binding.py` + `test_5_flash_binding`

| Item | Value |
| --- | --- |
| Model | `qwen/qwen3.8-flash` (= `FAMILY_CONFIGS["flash"]` = `paper2_exec_small_lane.sh`) |
| Endpoint | `https://openrouter.ai/api/v1/chat/completions` |
| Lane | `SMALL` |
| Key source | `OPENROUTER_API_KEY_SMALL` → bind `OPENROUTER_API_KEY` / `OPENAI_API_KEY` |
| No failover | request model ≠ 9b / gpt / claude ids |

---

## Hardening applied in this review commit

- Deep-copy messages in `build_request`
- Refusal-only + blank content + `tool_calls` even with content → fail-closed
- `FLASH_GATE0A` binding constants
- Review invariant test module

## Explicit non-start

Gate 0A Flash **not** launched. Awaits approval after this freeze.
