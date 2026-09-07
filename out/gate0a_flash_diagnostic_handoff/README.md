# Gate 0A Flash — diagnostic handoff (for independent Claude review)

**Gate 0A is pilot diagnostic data only and must not be used as Study 2 measurement data.**

This bundle freezes evidence from the Flash generic-executor run that reached
**26/57** checkpointed legs with approximately **8 DONE / 18 TERMINAL_FAIL**.
The run entered via Study 2 entrypoints (`study2_run_mypcbench` + OpenRouter) but is
**reclassified here as Gate 0A pilot diagnostic only** — not a Study 2 cell for analysis.

## Run identity

| Field | Value |
|-------|-------|
| Git commit | `aa060b2f09a94e8dbe4fc31632f5adf4de93aa55` |
| Git branch | `generic-executor-phase1` |
| Executor tip | `scripts/study2_run_mypcbench.py` → `generic_executor` `build_qwen_cuabash_agent` + `OpenRouterChatCompletionsTransport` → MyPCBench `run_mypcbench` |
| Model ID | `qwen/qwen3.8-flash` |
| Provider | OpenRouter (upstream Alibaba for this model) |
| API endpoint | `https://openrouter.ai/api/v1/chat/completions` |
| Transport | **Stateless** `/chat/completions` — full `messages` array rebuilt client-side each turn (no `previous_response_id`, no native tools schema) |
| Legs started (checkpointed) | 26 |
| Legs completed (terminal checkpoint) | 26 |
| Legs remaining in locked 57-order | 31 (not run after diagnostic stop) |
| DONE | 8 |
| TERMINAL_FAIL | 18 |
| Preliminary provider/rate-limit class | 3 (see `failure_summary.json`; may overlap TERMINAL_FAIL) |
| Stop reason | Human stop for Gate 0A diagnostic handoff after 26/57 checkpointed Flash legs (matrix resume PID terminated; no further legs). Earlier LANE_COMPLETE file from partial f010-only rerun is stale and not this freeze. |
| Freeze UTC | 2026-09-07T07:21:24.434123+00:00 |
| Artifact root | `results/paper2_exec/study2-flash/` |
| Log | `results/paper2_exec_study2-flash.log` |

## Frozen protocol identifiers (hashes)

| Artifact | sha256 |
|----------|--------|
| `GENERIC_AGENT_PROTOCOL_SPEC.md` | `5f4c31677f9f79daa924f5df1d7d46ff95736c34ec6d98df71e1de1be6e2ba98` |
| `GENERIC_AGENT_INVARIANTS.md` | `ac54b2515deb6d25a391498cb0ec789f790b353ed087d8592889dfb0d092bb14` |
| `qwen35vl_agent.py` | `f478ebe6cbdd54051d36d0e06814569ad33892dacd5710fc667a0e14e1f072c0` |
| `qwen_cua.py` | `5a2bc727d5bcaa8e292f37630867b050485edce104df29a477d36330f2693c42` |
| `run_mypcbench.py` | `571b2ee39ea123689be08125fb88a5782a1c8d552935d4e335fa22f398f87c25` |
| `generic_executor/executor.py` | `af62a129559cfc7c5ba8b1536a3fad67a4fed26c38d506dd094359b0637ecbde` |
| `generic_executor/openrouter_chat.py` | `f345f88da9fe05a1b818f7a46ed23459823a915ae32d5aded11bad90514a6f9d` |
| `paper2_traj_terminal.py` | `8037548b58bba343c566f871f2a59d702dceda54767b2c1809cf7af208eaea1a` |

### Protocol parameters (as executed)

| Parameter | Value |
|-----------|--------|
| System prompt source | Built in `qwen35vl_agent.py` (`system_prompt` string with `<tools>` JSON + XML format rules) + bash addendum from `qwen_cua.py` `_BASH_TOOL_DESCRIPTION` when `enable_bash=True` |
| System prompt hash | hash of vendored builder file above (`qwen35vl_agent.py`); runtime also injects **current date** into prompt (non-constant) |
| Action grammar source/hash | Same `qwen35vl_agent.py` `parse_response` + `qwen_cua._extract_bash_command` |
| Parser source/hash | `qwen35vl_agent.py` sha256 above; bash path `qwen_cua.py` sha256 above |
| Terminal semantics | Canonical DONE ⇔ last traj action string exactly `DONE` (`paper2_traj_terminal.py`). Checkpoint DONE only if `has-done`; else steps present → `TERMINAL_FAIL` |
| Max step budget | **80** (`--max_steps 80`) |
| Screenshot cadence | Every executed GUI/tool-round step attempts screenshot via env; traj records `screenshot_file` |
| Coordinate convention | Relative **`/999`** (`original_width/999`, `original_height/999`) when `coordinate_type` not absolute |
| Bash-output injection | Bash tool result staged in `_pending_bash_result`, prepended once into next-turn instruction as tool response; traj may show `action=TOOL_CALL` for bash-only rounds |
| EMPTY_XML policy | `MYPCBENCH_EMPTY_ACTION_RETRIES` default **3**; then abort |
| HTTP 429 policy | `HTTP_429_MAX_RETRIES=5`, backoff 2/4/8/16/32s in `openrouter_chat.default_http_post` |

## Bundle contents

See sibling files. **Do not treat rubric Perfect scores as DONE.**

## Reviewer instruction

Answer questions only in the sense of reviewing this evidence pack.
Cursor did **not** answer the dominance / protocol-revision questions — see `CLAUDE_REVIEW_PROMPT.md`.
