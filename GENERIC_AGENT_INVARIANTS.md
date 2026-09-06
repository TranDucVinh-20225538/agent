# GENERIC_AGENT_INVARIANTS.md

**Purpose:** Extract behavioral invariants from the frozen Paper-2 `qwen_cuabash` stack **before** any generic-agent refactor. This document is descriptive, not normative redesign.

**Gate −2 freeze:** Prefer **`GENERIC_AGENT_PROTOCOL_SPEC.md`** for Study-2 invariant status (FROZEN vs ALLOWED CHANGE). This file remains a detailed companion extract.

**Status:** Extraction only — **no implementation changes** associated with this file.

**Repo HEAD at extraction:** `64054a1` (`phase-a-results`)

**Primary sources (sha256):**

| Path | sha256 |
| --- | --- |
| `external/MyPCBench-main/agent-harness/agents/qwen_cua.py` | `5a2bc727d5bcaa8e292f37630867b050485edce104df29a477d36330f2693c42` |
| `…/vendored_paper_results/qwen35vl_agent.py` | `f478ebe6cbdd54051d36d0e06814569ad33892dacd5710fc667a0e14e1f072c0` |
| `…/agents/prompts.py` (`build_mypcbench_context`) | `212b5310a782ef48fe97c7bb4884ffbf17d443880cc4385c2f0e1089e0c97621` |
| `…/run_mypcbench.py` (react loop) | `9792f0ae2c25ffcc5588af4190e3bdfcc414dcbe622d1c7b9c82db65d88a497a` |

**Agent identity:** `agent_type=qwen_cuabash` → `QwenOSWorldAgent(enable_bash=True)` wrapping `_Qwen35VLPatched` → vendored `Qwen35VLAgent`. Paper-2 runner: `scripts/paper2_exec_run.sh` with `--max_steps 80 --timeout 7200`.

---

## 0. Stack layers (what “qwen_cuabash” actually is)

```
run_mypcbench.run_single_example
        │  predict(instruction, obs) → (response_text, actions[])
        │  env.step(action) for each action
        ▼
QwenOSWorldAgent  (qwen_cua.py)          # MyPCBench shim
        │  optional <tool_response> bash prepend
        │  bash XML extract + env._execute_command
        │  scroll(x,y) patch after parse
        ▼
_Qwen35VLPatched                          # injects MYPCBENCH_CONTEXT + bash tool text into system
        ▼
Qwen35VLAgent (vendored_paper_results)    # OSWorld paper-results computer_use XML agent
```

Invariants below must say **which layer** owns them. A generic agent that only copies the vendored prompt but drops the shim will change Paper-2 Qwen semantics.

---

## 1. System prompt (exact composition)

System content is assembled **per `predict()` call** (not once at ctor). Order in the OpenAI `messages[0]` after shim injection:

### 1.1 Core system string (vendored `Qwen35VLAgent.predict`)

Built as:

1. Fixed persona opener:  
   `"You are a multi-purpose intelligent assistant. Based on my requests, you can use tools to help me complete various tasks."`
2. `# Tools` + `"You have access to the following functions:"` + `<tools>\n` + **`json.dumps(tools_def)`** + `\n</tools>`
3. Hard requirement: function calls **ONLY** in the XML envelope (`<tool_call>` / `<function=…>` / `<parameter=…>`).
4. `<IMPORTANT>` reminders (format, required params, reasoning **before** tool call only, date line, collapsed-screenshot text).
5. `# Response format`: every step must be  
   - `Action:` one short imperative sentence  
   - then **exactly one** `<tool_call>…</tool_call>`  
   - terminate success → `action=terminate` + `status=success`  
   - infeasible → `action=terminate` + `status=failure`

`tools_def` is a single function tool named **`computer_use`** whose `description` embeds the GUI rules (see §3). The description **explicitly claims** “You do not have access to a terminal or applications menu” — this remains in the JSON even for `qwen_cuabash`; bash is added only as a later text addendum (§1.3), so the model sees a **known contradiction** that the frozen run accepts.

Coordinate space advertised inside `tools_def.description` when `coordinate_type=="relative"` (Paper-2 default): **“The screen's resolution is 1000x1000.”**

Date line: `datetime.today().strftime('%A, %B %d, %Y')` at call time.

Collapsed placeholder: default `"This screenshot has been collapsed."`

### 1.2 `tools_def` action enum (frozen)

`key | type | mouse_move | left_click | left_click_drag | right_click | middle_click | double_click | triple_click | scroll | hscroll | wait | terminate | answer`

Parameters: `keys`, `text`, `coordinate`, `pixels`, `time`, `status∈{success,failure}`.

### 1.3 MyPCBench system addenda (`_Qwen35VLPatched.call_llm`)

Appended to system message **after** the core tools JSON (as an extra text part if content is a list):

1. **`build_mypcbench_context(has_bash=True)`** when `MYPCBENCH_QWEN_OSWORLD_INJECT_CONTEXT` is not disabled (default **on**). Contents (with `{CLIENT_PASSWORD}`, `{CURRENT_DATE}` formatted):
   - Persona: Michael Scott / `michael.scott@dundermifflin.com` (unless persona registry override)
   - Linux user `user` + sudo password when `has_bash`
   - Ubuntu 24.04 GNOME / Firefox / dock apps / Documents·Downloads·Maildir
   - Python 3.12 + LibreOffice CLI when `has_bash`
   - Web-app port table 3001–3017
   - Output: put final answer as plain text in last assistant turn before stop
2. **`_BASH_TOOL_DESCRIPTION`** (only if `enable_bash`): documents `<function=bash><parameter=command>…` XML, VM user `user`, sudo password, and that stdout/stderr return in next user turn as `<tool_response>…</tool_response>`. Guidance: bash for read-only data work; GUI for visible task actions.

**Not injected for Qwen:** `COMPLETION_DISCIPLINE`, `GUI_WORKFLOW_HINT`, Claude/OpenAI operator prompts. Those live in `prompts.py` but are **out of band** for `qwen_cuabash`.

### 1.4 Env knobs that alter system surface (must be recorded if changed)

| Env | Default (Paper-2 / ctor) | Effect |
| --- | --- | --- |
| `MYPCBENCH_QWEN_OSWORLD_INJECT_CONTEXT` | `1` | Drop MYPCBENCH_CONTEXT if `0` |
| `MYPCBENCH_QWEN_OSWORLD_ENABLE_BASH` | off unless `enable_bash` | Force bash text even for `qwen_cua` |
| `MYPCBENCH_QWEN_OSWORLD_SOURCE` | `vendored_paper_results` | Swap agent implementation |

---

## 2. Observation serialization

### 2.1 Env → agent

- `obs["screenshot"]`: raw PNG **bytes** from `MyPCBenchEnv._get_screenshot()` / `_get_obs()`.
- `observation_type` fixed to `"screenshot"` (a11y not used by this agent).
- Task `instruction` string is passed every `predict()` call unchanged by the runner (bash shim may prepend — §3.2).

### 2.2 Screenshot preprocessing (vendored `process_image`)

- Decode PNG → `smart_resize` with `factor=32`, defaults  
  `min_pixels = 16*16*4*16`, `max_pixels = 16*16*4*6400`  
  (overridable via ctor / `MYPCBENCH_QWEN_MIN_PIXELS` / `MYPCBENCH_QWEN_MAX_PIXELS`).
- Re-encode PNG → store **base64** in `self.screenshots[]`.
- Model sees `data:image/png;base64,{b64}` image_url parts.
- Coordinate remap uses **original** screenshot W×H vs processed W×H (absolute) or vs **999** (relative). Paper-2 uses **`coordinate_type="relative"`** → scale `x * original_w/999`, `y * original_h/999`.

### 2.3 History window & folding

- Append one screenshot per `predict`.
- Visible history steps: `start_step = max(1, total_steps - history_n)` with default **`history_n=100`**.
- Folding: while `(total_screenshots - folded_prefix_k) > image_max`, add **`fold_size`** (defaults **`image_max=20`**, **`fold_size=10`**). Collapsed steps replace image with text `collapse_text`.
- Message layout for each kept step:
  - **First turn in window:** image (or collapse text rules) + `instruction_prompt` text.
  - **Later turns:** user content wrapped as `<tool_response>\n` + image_or_collapse + `\n</tool_response>` (simulates “tool returned a new screenshot”).
  - After each historical user turn (except current): prior assistant message from `responses[]` (optional `reasoning` / `reasoning_content` if `preserve_reasoning_content`).

### 2.4 Per-turn user text (`instruction_prompt`)

```
Please generate the next move according to the UI screenshot, instruction and previous actions.

Instruction: {instruction}

Previous actions:
{Step k: <low_level_instruction> … | None}
```

`Previous actions` lists only steps **before** `start_step` (folded-out prefix summaries), not the full in-window Action lines.

### 2.5 Bash observation channel (shim)

When `_pending_bash_result` is set, next `predict` rewrites:

```
<tool_response>
{bash_stdout/stderr/exit}
</tool_response>

{original instruction}
```

so the vendored agent embeds bash output inside the first-turn `Instruction:` field. Cleared after one use (exactly-once). Bash output truncated at **10000** chars.

---

## 3. Tool / action semantics

### 3.1 Computer (`computer_use` XML → pyautogui list)

Vendored `parse_response` only parses `<function=computer_use>` inside `<tool_call>`. Mapping (invariant):

| XML `action` | Emitted code / sentinel |
| --- | --- |
| `left_click` (+ optional `text` modifiers) | `pyautogui.click(x,y)` or `click()` |
| `right_click` / `middle_click` / `double_click` | corresponding pyautogui |
| `triple_click` | **`doubleClick`** (documented simulation) |
| `type` | clipboard-paste helper (`pyperclip` + ctrl+v; fallback typewrite) after `\n/\r/\t` decode |
| `key` | `hotkey(...)` if >1 key else `press(...)` |
| `scroll` / `hscroll` | `pyautogui.scroll(pixels)` (+ optional modifiers) |
| `wait` | literal **`WAIT`** |
| `terminate` + `status=failure` | **`FAIL`** |
| `terminate` otherwise / `answer` | **`DONE`** |
| `mouse_move` | `moveTo(x,y)` (default 0,0) |
| `left_click_drag` | `dragTo(x,y, duration=…)` |

Low-level instruction string: first `Action:` line in the response, else synthesized from first code.

**Shim post-parse (`_scroll_at_pointer`):** bare `pyautogui.scroll(N)` rewritten to `pyautogui.scroll(N, x=…, y=…)` using last `moveTo` in the same turn, else **`(640, 444)`**.

Multiple `<tool_call>` blocks in one response: all `computer_use` calls are processed in order into one `actions` list.

### 3.2 Bash (`qwen_cuabash` only)

- Advertised only via system addendum; **not** in `tools_def` JSON.
- Shim regex extracts first `<function=bash><parameter=command>…` inside any `<tool_call>`.
- Executes `env._execute_command(command, shell=True)` as VM user.
- Does **not** append bash into `actions` (no pyautogui). Runner treats empty `actions` + `_pending_bash_result` as a **TOOL_CALL** round (§5).
- Vendored parser ignores bash XML for pyautogui (returns empty if only bash).

### 3.3 Env execution (`MyPCBenchEnv.step`)

- String actions: `WAIT` → sleep `pause` (runner `sleep_after`, default 1.0s); `DONE` / `FAIL` → episode `done=True` with info flags.
- Other strings: pyautogui via guest controller (`FAILSAFE=False`, `PAUSE=0` preamble in env).
- After action: sleep `pause`, then fresh screenshot obs.

---

## 4. Terminal semantics

| Signal | How produced | Env / runner effect |
| --- | --- | --- |
| **DONE** | `terminate` status≠failure, or `answer`, or explicit | `env.step("DONE")` → `done=True`, `info.done` |
| **FAIL** | `terminate` status=failure, **or** free-text matches `INFEASIBLE_VERDICT_PATTERNS` when no tool code | `env.step("FAIL")` → `done=True`, `info.fail` |
| **WAIT** | `action=wait` | sleep only; episode continues |
| **Infeasible text patterns** | `\binfeasible\b`, `\bunfeasible\b`, `\bimpossible\b`, `\bnot feasible\b`, `\bnot possible\b`, `\bcannot be (done|completed|…)\b` | Force `FAIL` if no pyautogui codes |
| No XML / empty actions | — | Not auto-DONE; see empty-action retries (§5) |
| Step / wall-clock exhaustion | — | Loop exits **without** forcing DONE/FAIL; task still gets `result.txt` completion marker from runner (completed=1.0 means “ran”, not rubric success) |

Paper-2 / MyPCBench **do not** require the Qwen model to emit Markdown ` ```DONE``` ` fences; termination is the **pyautogui sentinel strings** above. (Claude/OpenAI agents use different stop tokens — out of scope here.)

---

## 5. Max-step, timeout, and retry behavior

### 5.1 Paper-2 frozen outer loop (`paper2_exec_run.sh` → `run_mypcbench.py`)

| Knob | Paper-2 value | Notes |
| --- | --- | --- |
| `max_steps` | **80** | Manifest + runner CLI |
| `timeout` | **7200** s | Global wall clock per task; abort mid-loop |
| `sleep_after` | default **1.0** | Passed to `env.step` |
| Post-boot settle | **5** s | Before first predict |
| Predict crash | log `PREDICT_CRASH`, break | No auto-retry of crash |

Loop: `while not done and step_idx < max_steps`. Each outer iteration may execute **multiple** actions from one predict; `step_idx` increments once per predict round (not per sub-action).

### 5.2 Empty / tool-only action policy (runner)

When `actions == []`:

1. **API-looking errors** (`response` starts with `Error code:` or contains `BadRequestError`): count consecutive; **abort after 3**.
2. Else if **tool pending**: `_pending_bash_result` non-empty (Qwen) or `pending_items` (other agents) → write traj `action=TOOL_CALL`, refresh obs, `step_idx++`, **continue** (does not consume empty-retry budget as a hard fail).
3. Else **EMPTY_XML retry**: `MYPCBENCH_EMPTY_ACTION_RETRIES` default **3**. While `consecutive_empty < limit`, write traj `EMPTY_XML`, refresh obs, continue. At limit → **break** (no FAIL sentinel forced).

Important: for Qwen, empty Action-prose without XML used to be confused with “has messages”; runner **must not** treat `messages` alone as pending when `hasattr(agent, "_inner")` (Qwen path). Frozen code implements that guard.

### 5.3 LLM HTTP retries (vendored `call_llm`)

- `MAX_RETRY_TIMES = int(OSWORLD_MAX_RETRY_TIMES or 5)`.
- Retries only: SSLError, APIConnectionError, APITimeoutError, RateLimitError, InternalServerError.
- Backoff: `sleep(min(5.0 * attempt, 30.0))`.
- Non-retryable errors propagate; empty content after retries returns `""`.
- Endpoint: `OPENAI_BASE_URL` (Paper-2 OpenRouter) + `OPENAI_API_KEY`.
- Sampling defaults from shim: `temperature=0.0`, `top_p=0.9`, `max_tokens=32768` (overridable `MYPCBENCH_QWEN_MAX_TOKENS`), `presence_penalty=1.5`, `top_k=20`, `enable_thinking=True`, `keep_reasoning` defaults to thinking-on, `extra_body.chat_template_kwargs.enable_thinking`.

### 5.4 OpenRouter thinking ↔ XML salvage (shim)

If latest reasoning contains `<tool_call>` but content does not, `_Qwen35VLPatched.parse_response` concatenates reasoning into the parse text before vendored parse. Separately, `call_llm` may wrap reasoning in `<think>` when `keep_reasoning`.

---

## 6. Sampling / history defaults (Paper-2 ctor)

From `QwenOSWorldAgent` / OSWorld args.json comments (env overrides allowed):

| Parameter | Default |
| --- | --- |
| `history_n` | 100 |
| `image_max` | 20 |
| `fold_size` | 10 |
| `temperature` | 0.0 |
| `top_p` | 0.9 |
| `max_tokens` | 32768 |
| `coordinate_type` | `relative` |
| `add_thought_prefix` | False |
| `presence_penalty` | 1.5 |
| `top_k` | 20 |
| `enable_thinking` | True |
| `platform` | `ubuntu` |
| `action_space` | `pyautogui` |

Screen size: runner/Paper-2 VM (typically 1920×1080 after xrandr fix; agent receives whatever screenshot bytes the env returns).

---

## 7. Non-invariants / known frozen quirks (do not “fix” silently)

1. System `computer_use` description denies terminal access while bash addendum grants it.
2. `triple_click` → `doubleClick`.
3. `hscroll` maps to vertical `scroll`.
4. `wait` ignores XML `time` parameter (always sentinel `WAIT` + env pause).
5. `COMPLETION_DISCIPLINE` not in Qwen system prompt.
6. Bash results appear inside **Instruction:** text, not as a separate multimodal tool schema.
7. Debug dumps under `./draft/message_cache/` may be written by vendored agent during predict.
8. Changing any env listed in §§1.4 / 5.2–5.3 without a dated amendment changes the agent.

---

## 8. Checklist for a future “generic agent” (still no implementation)

Any replacement that claims Qwen-parity for Paper-2 must preserve, or explicitly amend:

- [ ] System prompt = vendored tools JSON + response-format rules + MYPCBENCH_CONTEXT(has_bash) + bash tool XML docs  
- [ ] Observation = resized screenshot history with image_max/fold_size/history_n and `<tool_response>` screenshot wrapping  
- [ ] Relative coords on 1000-grid → scale by /999  
- [ ] computer_use ↔ pyautogui table including DONE/FAIL/WAIT  
- [ ] Bash via XML + pending `<tool_response>` exactly once  
- [ ] Scroll coordinate patch  
- [ ] Runner: max_steps=80, timeout=7200, EMPTY_XML retries=3, TOOL_CALL rounds for bash-only, API-error abort×3  
- [ ] Thinking/XML salvage behavior under OpenRouter  

**End of extraction. No code changes.**
