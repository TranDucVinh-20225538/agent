# GENERIC_AGENT_PROTOCOL_SPEC.md

**Gate:** −2 — Protocol Extraction and Freeze  
**Status:** EXTRACTION ONLY — generic agent loop **BLOCKED**  
**Host / tree:** node30 · `/mnt/data2/Vinh/agent` · branch `phase-a-results`  
**Freeze HEAD (Gate −1.5 closure pin):** `3f636dc` / pin tip `7bbeee9`  
**Instrument identity:** `EXECUTION_SOURCE_MANIFEST.md` + `out/paper2_harness_pin.json`

This document freezes the **behavioral protocol** of the provenance-pinned Paper-2
execution instrument (`agent_type=qwen_cuabash`). It does **not** authorize
implementation of a generic cross-provider loop.

Companion descriptive extract (pre–Gate −2): `GENERIC_AGENT_INVARIANTS.md`.  
Where they differ, **this Gate −2 spec + on-disk pinned sources win**.

---

## 0. Primary decision — frozen protocol vs allowed change

### Frozen behavioral protocol (Study 2 MUST preserve)

The Study-2 generic cross-provider loop must continue to use the **existing
prompt-mediated action protocol**:

- Natural-language `Action:` line + **XML** `<tool_call>` / `<function=…>` /
  `<parameter=…>` envelopes;
- Tool surface centered on **`computer_use`** (JSON schema embedded in the
  system prompt text) plus, for `qwen_cuabash`, a **text addendum** advertising
  **`bash`** in the same XML shape;
- Client-side parse → pyautogui / `DONE` / `FAIL` / `WAIT` sentinels;
- Client-side bash execution + `<tool_response>` reinjection;
- Client-owned conversation history rebuilt each `predict()` from
  screenshots / responses / actions arrays;
- Gate −1.5 terminal rule: `VALID_DONE ⇔ canonical_last_action == "DONE"`.

### Explicitly NOT automatic migrations

The loop must **not** silently migrate to:

- OpenAI Responses / Computer Use native tools;
- Anthropic computer-use beta native tools;
- Provider-server-managed conversation state (`previous_response_id`, etc.);
- Provider-specific structured tool protocols as a replacement for XML.

Those may exist later only as an **explicit, separately authorized** protocol
amendment — never as a silent transport swap.

### Distinction (must stay explicit in any future implementation ticket)

| Layer | Study 2 status |
| --- | --- |
| **Frozen behavioral protocol** (prompt text, XML grammar, parse→action map, obs cadence, bash XML, multi-action order, terminals, limits) | **FROZEN** |
| **Transport / serialization** (HTTP client, base URL, how messages JSON is POSTed, how history bytes are packed onto the wire) | **ALLOWED CHANGE** |
| **Provider endpoint / model id** | **ALLOWED CHANGE** |
| **Generation parameter mapping** onto a new backend | **ALLOWED CHANGE** (with portability table in §4) |

---

## 1. Source inventory (effective instrument)

Verified against `out/paper2_harness_pin.json` at Gate −1.5 closure (SHA256 prefixes):

| Role | Path | sha256 prefix |
| --- | --- | --- |
| React loop / traj writer | `external/…/run_mypcbench.py` | `9792f0ae2c25ffcc` |
| QEMU env step / screenshot | `external/…/env.py` | `d05d278802d4e834` |
| `qwen_cuabash` shim | `external/…/agents/qwen_cua.py` | `5a2bc727d5bcaa8e` |
| Prompt+parse core | `external/…/vendored_paper_results/qwen35vl_agent.py` | `f478ebe6cbdd5405` |
| Observation resize helper | `…/vendored_paper_results/utils/qwen_vl_utils.py` | `b8bf6e684dd36437` |
| MYPCBENCH_CONTEXT | `external/…/agents/prompts.py` | `212b5310a782ef48` |
| Paper-2 runner | `scripts/paper2_exec_run.sh` | `319e3be62e04b224` |
| Terminal SoT | `scripts/paper2_traj_terminal.py` | `8037548b58bba343` |

### 1.1 Provenance coverage — `base.py` vs `qwen_vl_utils.py` (Gate −2 verify)

| File | Used on `qwen_cuabash` path? | Protocol surface impact |
| --- | --- | --- |
| `agents/base.py` | **No.** Not imported by `qwen_cua.py` or `qwen35vl_agent.py`. `BaseAgent` / `encode_image` are used by OpenAI/Claude agents only. | **Plumbing only for other agents.** Does **not** own parsing, `adjust_coordinates`, terminal detection, or Qwen observation/tool serialization. Still SHA-pinned (Gate −1 inventory) as a harness dependency, not as a Study-2 invariant owner. |
| `…/utils/qwen_vl_utils.py` | **Yes — `smart_resize` only** (imported by `qwen35vl_agent.process_image`). `convert_bbox_format` / `convert_point_format` are **unused** on this path. | **Observation preprocessing:** `smart_resize` sets resized H×W of the PNG base64 the model sees (`process_image` → `self.screenshots[]`). **Not** the owner of relative coordinate transform: Paper-2 `coordinate_type=relative` uses `adjust_coordinates` in `qwen35vl_agent.parse_response` (`× original_w/999`), which does **not** call `qwen_vl_utils` point converters. Absolute-mode scaling would use `processed_width/height` from `process_image` (hence indirectly `smart_resize`); Study-2 freezes **relative**, so that path is out of band. No role in XML parse or VALID_DONE. |

Invariant owners (do not relocate to `base.py`):

- Parse / XML / terminate→DONE|FAIL → `qwen35vl_agent.parse_response`
- Relative coords → `adjust_coordinates` in same file
- Screenshot bytes on the wire → `process_image` (**calls** `smart_resize`)
- VALID_DONE → `scripts/paper2_traj_terminal.py`

Stack:

```
paper2_exec_run.sh
  → run_mypcbench.run_single_example
      → QwenOSWorldAgent.predict  (qwen_cua.py, enable_bash=True)
          → _Qwen35VLPatched.call_llm / parse_response
              → Qwen35VLAgent.predict / parse_response / call_llm
      → env.step(action) × N
  → paper2_traj_terminal VALID_DONE
```

---

## 2. Protocol extraction

### A. Prompting

**Owner:** `Qwen35VLAgent.predict` (system + tools JSON + response format) +
`_Qwen35VLPatched.call_llm` (MYPCBENCH_CONTEXT + bash addendum).

#### A.1 Core system prompt (literal structure)

Assembled **every** `predict()` in `qwen35vl_agent.py` (~L402–441):

1. Persona opener:  
   `"You are a multi-purpose intelligent assistant. Based on my requests, you can use tools to help me complete various tasks."`
2. `# Tools` + `"You have access to the following functions:"` + `<tools>\n` +
   `json.dumps(tools_def)` + `\n</tools>`
3. Function-call **XML-only** instruction (exact envelope example in source).
4. `<IMPORTANT>` block (format, required params, reasoning **before** tool call
   only, current date via `datetime.today()`, collapsed-screenshot text).
5. `# Response format` rules, including:
   - `Action:` one short imperative;
   - **a single** `<tool_call>…</tool_call>`;
   - success → `action=terminate` + `status=success`;
   - infeasible → `action=terminate` + `status=failure`.

`tools_def` is a single function named **`computer_use`**. Its `description`
embeds GUI rules and the line:

> `You do not have access to a terminal or applications menu.`

(Paper-2 still appends a bash tool addendum — known contradiction, frozen.)

Coordinate advertisement when `coordinate_type=="relative"` (Paper-2 default):

> `* The screen's resolution is 1000x1000.`

#### A.2 Operator / task prompt (per turn)

`instruction_prompt` (~L443–447):

```
Please generate the next move according to the UI screenshot, instruction and previous actions.

Instruction: {instruction}

Previous actions:
{Step k: … | None}
```

`instruction` is the task string from the runner, optionally prefixed by a
pending bash `<tool_response>` (shim).

#### A.3 MyPCBench context (shim, default ON)

`build_mypcbench_context(has_bash=True)` from `prompts.py` when
`MYPCBENCH_QWEN_OSWORLD_INJECT_CONTEXT` ≠ `0`. Literal sections: Persona,
Environment, Web apps port table 3001–3017, Output (final answer as plain text
before stop). Rendered with `{CLIENT_PASSWORD}` / date substitutions in the
shim ctor path.

**Not injected for Qwen:** `COMPLETION_DISCIPLINE`, `OPENAI_CUA_OPERATOR_PROMPT`,
`CLAUDE_CUA_SYSTEM_PROMPT`, `GUI_WORKFLOW_HINT` (those strings exist in
`prompts.py` for other agents only).

#### A.4 Bash tool text (shim, `enable_bash=True`)

Literal `_BASH_TOOL_DESCRIPTION` in `qwen_cua.py` (~L79–98): same XML shape as
`computer_use`, `function=bash`, `parameter=command`; stdout/stderr appear next
turn in `<tool_response>`; guidance = bash for read-only data, GUI for visible
task actions.

#### A.5 Infeasible / refusal (parser, not prompt-only)

If parse yields no pyautogui codes and free text matches
`INFEASIBLE_VERDICT_PATTERNS` → emit `FAIL`
(`qwen35vl_agent.py` ~L755–757).

---

### B. Action protocol

**Owner:** `Qwen35VLAgent.parse_response` + `_Qwen35VLPatched.parse_response`
(`_scroll_at_pointer`).

| Property | Actual behavior | Source |
| --- | --- | --- |
| Envelope | `<tool_call>…<function=NAME>…<parameter=K>V</parameter>…</function>…</tool_call>` | parse + system prompt |
| Grammar | Regex extract all `<tool_call>` blocks; only `function=computer_use` → params | `parse_xml_tool_call` |
| Supported `action` enum | `key, type, mouse_move, left_click, left_click_drag, right_click, middle_click, double_click, triple_click, scroll, hscroll, wait, terminate, answer` | `tools_def` |
| Required fields | Schema marks `action` required; missing action → no-op for that call | `process_tool_call_params` |
| Coordinates | Relative: model 1000-grid; scale `x * orig_w/999`, `y * orig_h/999` | `adjust_coordinates` |
| Multiple actions / response | **Parser accepts multiple** `<tool_call>` blocks (ordered). Prompt text says “a single” — see §6 ambiguity. | `re.finditer` over tool_calls |
| Execution order | Runner `for action in actions: env.step(action)` in list order | `run_mypcbench.py` |
| Parser failure | Empty / no XML → empty `actions` (not DONE). Infeasible text → `FAIL`. | parse + runner EMPTY_XML |
| Terminate map | `terminate`+`failure`→`FAIL`; else/`answer`→`DONE`; `wait`→`WAIT` | parse |
| Quirks (frozen) | `triple_click`→`doubleClick`; `hscroll`→vertical `scroll`; `wait` **ignores** `time` param | parse |
| Scroll patch | Bare `scroll(N)` → `scroll(N, x=…, y=…)` last `moveTo` else `(640,444)` | `_scroll_at_pointer` |

---

### C. Observation protocol

| Property | Actual behavior | Source |
| --- | --- | --- |
| Screenshot timing | After each `env.step`; also `_get_obs()` on TOOL_CALL / EMPTY_XML retries; initial obs before loop | `run_mypcbench` / `env` |
| Format | PNG bytes → `process_image` → base64 PNG in history | `process_image` |
| Screen resolution (VM) | Runner/env default **1280×800** (`--screen_width/height`) | `run_mypcbench` / `env.DEFAULT_SCREEN_SIZE` |
| Coord system (model) | Advertised **1000×1000** relative | system `tools_def` description |
| When sent | Each kept history step: image_url (or collapse text) | `predict` message build |
| Text / bash injection | Bash output prepended into `Instruction:` via `<tool_response>` once | `QwenOSWorldAgent.predict` |
| Post multi-action obs | Each sub-action saves its own traj screenshot; **next `predict` uses final `obs` after last sub-action** | react loop |
| History folding | `history_n=100`, `image_max=20`, `fold_size=10`; collapsed → `collapse_text` | agent fields |
| Later-turn wrap | Non-first window turns wrap image as `<tool_response>…</tool_response>` | `_wrap_tool_response` |

---

### D. Bash / shell semantics

| Step | Behavior | Source |
| --- | --- | --- |
| Request | XML `<function=bash><parameter=command>…` inside `<tool_call>` | `_BASH_TOOL_DESCRIPTION` + `_extract_bash_command` |
| Execute | `env._execute_command(command, shell=True)` as VM user | `_execute_bash` |
| Represent | stdout + optional `stderr:` + `(exit code N)`; truncate **10000** chars | `_execute_bash` |
| Next turn | Staged in `_pending_bash_result`; drained once into `instruction` as `<tool_response>…` | `predict` |
| GUI list | Bash **not** appended to pyautogui `actions` | `predict` post-process |
| Runner | Empty `actions` + pending bash → traj `TOOL_CALL`, refresh obs, continue | `run_mypcbench` |

Do **not** redesign bash into a native provider tool-result channel without a
new Gate amendment.

---

### E. Multi-action semantics (exact)

```
model response
  → parse → actions[]   (0..N pyautogui/DONE/FAIL/WAIT strings)
  → [optional] extract+execute bash → stage _pending_bash_result
  → for action in actions:
        env.step(action) → obs, reward, done, info
        append traj row (per action) with post-step screenshot
        break if done
  → step_idx += 1   (once per predict round)
  → next predict(instruction, obs_final)
```

Screenshot after **each** executed GUI action is stored on traj; the model’s
**next** turn receives only the **last** obs (plus history images already in
`self.screenshots`). Bash-only turns take the TOOL_CALL path (no GUI step)
then refresh obs before the next predict.

---

### F. Turn / history semantics

Logical state lives **client-side** on the agent object (not provider-managed):

| Retained across turns | Cleared / rebuilt |
| --- | --- |
| `screenshots[]` (processed b64) | Message list rebuilt every `predict()` |
| `responses[]` / `actions[]` / reasonings | System prompt rebuilt every call |
| Folding cursor `folded_prefix_k` | Wire payload is a fresh `messages` array |
| `_pending_bash_result` (at most one turn) | Cleared when drained into instruction |

Each turn sends: system (tools JSON + addenda) + windowed user/assistant turns
from `start_step … total_steps`, with the current screenshot as the latest user
turn. Transport may change how this array is serialized; **logical contents**
are frozen.

---

### G. Terminal semantics (Gate −1.5)

**Do not redefine.** Reference Gate −1.5:

```
VALID_DONE ⇔ canonical_last_action == "DONE"
```

(`scripts/paper2_traj_terminal.py` — last well-formed **string** `action` only;
fail closed on missing/malformed/unreadable.)

| Outcome | How it arises | Checkpoint (Paper-2) |
| --- | --- | --- |
| DONE | Last traj action string `DONE` | `status=DONE` |
| FAIL | `env.step("FAIL")` / traj `FAIL` | `TERMINAL_FAIL` (not VALID_DONE) |
| PREDICT_CRASH | predict exception row | `TERMINAL_FAIL` |
| EMPTY_XML / TOOL_CALL | runner empty-action paths | usually continue; if final → not DONE |
| BOOT_NO_RESULT | no usable traj / no steps | `BOOT_NO_RESULT` |
| Step/timeout exhaust | loop exit without DONE | `TERMINAL_FAIL` if steps else boot |
| `result.txt=1.0` | “react returned” marker | **≠** VALID_DONE |
| `rubric_bundle.json` | judge packaging | **≠** VALID_DONE |

---

### H. Execution limits and retries

| Knob | Paper-2 value | Source |
| --- | --- | --- |
| `max_steps` | **80** | `paper2_exec_run.sh` → `run_mypcbench` |
| `timeout` | **7200** s | same |
| `sleep_after` | **1.0** s default | `env.step` pause |
| EMPTY_XML retries | **3** (`MYPCBENCH_EMPTY_ACTION_RETRIES`) | runner |
| Consecutive API-looking empty | abort after **3** | runner |
| LLM HTTP retries | `OSWORLD_MAX_RETRY_TIMES` default **5** (SSL/timeout/rate/5xx) | `call_llm` |
| Predict crash | write `PREDICT_CRASH`, break (no retry) | runner |
| Infra boot retry | one re-`run_agent` if no step and no DONE | `paper2_exec_run.sh` |
| Resume / checkpoint | `cell_has_done` / `write_leg_checkpoint` via traj helper; incomplete dirs stashed | runner + resume_prep |

---

## 3. Invariant table

| Property | Current behavior | Source | Study 2 status |
| --- | --- | --- | --- |
| System prompt (tools JSON + response format) | §A.1 | `qwen35vl_agent.predict` | **FROZEN** |
| MYPCBENCH_CONTEXT + bash addendum | §A.3–A.4 | `prompts.py` / `qwen_cua.py` | **FROZEN** |
| XML grammar / `computer_use` | §B | `parse_response` | **FROZEN** |
| Coordinate convention (relative /999) | §B–C | parse + tools_def | **FROZEN** |
| Screenshot preprocess + history fold | §C | `process_image` / predict | **FROZEN** |
| VM resolution 1280×800 default | §C | `env` / runner CLI | **FROZEN** |
| Observation cadence (post-step; final obs to next predict) | §C–E | react loop | **FROZEN** |
| Bash XML + pending `<tool_response>` | §D | shim | **FROZEN** |
| Multi-action ordering | §E | runner + parse | **FROZEN** |
| Terminal semantics / VALID_DONE | §G | Gate −1.5 | **FROZEN** |
| Max steps 80 / timeout 7200 / empty retries | §H | runner | **FROZEN** |
| Scroll-at-pointer patch | §B | `_scroll_at_pointer` | **FROZEN** |
| Prompt-mediated protocol (not native CU tools) | §0 | decision | **FROZEN** |
| Transport (HTTP client / wire encoding) | OpenAI-compatible chat.completions today | `call_llm` | **ALLOWED CHANGE** |
| Provider endpoint / model id | env `OPENAI_BASE_URL` + model string | runner / env | **ALLOWED CHANGE** |
| History serialization on the wire | rebuilt `messages` JSON each call | `predict`/`call_llm` | **ALLOWED CHANGE** |
| Generation parameter mapping | §4 | `call_llm` / shim env | **ALLOWED CHANGE** |

---

## 4. Provider-specific parameter mapping (Qwen / vLLM today)

Defaults from `QwenOSWorldAgent` ctor + env overrides (`MYPCBENCH_QWEN_*`):

| Parameter | Current (Paper-2) | Classification for other providers |
| --- | --- | --- |
| `temperature` | `0.0` | **Frozen behavior** intent (greedy); map if API supports |
| `top_p` | `0.9` | **Best-effort provider mapping** |
| `max_tokens` | `32768` (env-overridable) | **Best-effort** (clamp to provider max) |
| `presence_penalty` | `1.5` | **Best-effort** if API supports; else **omit** with note |
| `top_k` | `20` via `extra_body` | **Not portable / omitted** unless backend documents equivalent |
| `min_p` | ctor/env | **Not portable / omitted** by default |
| `repetition_penalty` | ctor/env | **Not portable / omitted** by default |
| `enable_thinking` | `True` → `extra_body.chat_template_kwargs.enable_thinking` | **Not portable** as vLLM/Qwen template knob; thinking salvage may need provider-specific handling |
| `chat_template_kwargs` | see above | **Not portable / omitted** |
| `keep_reasoning` / `<think>` wrap | tied to thinking | **Best-effort** only if provider returns reasoning channels |
| OpenRouter XML salvage (concat reasoning into parse text) | shim `parse_response` | **Frozen behavior** for hosts that split thinking/content; implement as client-side salvage, not a new tool protocol |

**Do not invent false one-to-one equivalents.** Prefer omit + document over fake mapping.

---

## 5. Explicit non-goals (Gate −2)

- Implement the generic loop  
- Choose final GPT/Claude models  
- Perform Gate 0 / spend API budget  
- Change prompts, action space, terminals, or QEMU config  
- Migrate to native structured computer-use tools  

---

## 6. Protocol ambiguities (could affect implementation)

These are **source facts**, not license to “fix” silently:

1. **Single vs multi `tool_call`:** prompt says “a single `<tool_call>`”; parser
   processes **all** matches. Study 2 must preserve parser behavior (multi OK)
   unless a dated amendment changes both prompt and parser together.
2. **Terminal denied vs bash granted:** `computer_use` description denies
   terminal; bash addendum grants it. Frozen contradiction.
3. **`wait` time ignored:** XML `time` does not set sleep; env uses `sleep_after`.
4. **Bash + GUI in one response:** bash is executed/staged **and** GUI actions
   still run if present; order is parse GUI list then runner steps (bash is
   side-channel, not in `actions[]`).
5. **`step_idx` vs sub-actions:** one predict round with N GUI actions increments
   `step_idx` by 1 after the whole for-loop.
6. **Screen size vs coord grid:** VM 1280×800 vs prompt 1000×1000 relative grid.

---

## 7. Behaviors that could not be fully literalized here

| Item | Why | Mitigation |
| --- | --- | --- |
| Exact `tools_def` JSON bytes | Built at runtime (`json.dumps` of Python dict); date line changes daily | Treat structure + field set as frozen; pin file SHA for code |
| Exact MYPCBENCH_CONTEXT password/date substitution | Depends on env/`CLIENT_PASSWORD` and clock | Freeze template in `prompts.py` / `_BASH_TOOL_DESCRIPTION` |
| Guest `_execute_command` internals beyond return dict shape | Deep QEMU/controller path | Residual vendor pin; output contract in §D is the protocol surface |
| Live OpenRouter response shape variants | Transport ALLOWED CHANGE | Salvage rules in shim are the frozen client behavior |

No critical VALID_DONE or XML→action mapping was left ambiguous relative to pinned sources.

---

## 8. Required follow-up notes (non-blocking)

### A. Fallback-trap test

**Status after this Gate −2 ticket:** **ADDED**.

Fixture `tests/fixtures/paper2_terminal/10_fallback_trap_done_then_malformed/`:

- Step N−1: `{"action": "DONE"}`
- Step N: malformed action object

Expected (verified): `canonical_last_action=None`, `valid_done=false`,
status `TERMINAL_FAIL` — proves **no back-scan** to an earlier DONE.

### B. Vendor provenance classification

| Goal | SHA256 pin | Human patch/diff vs upstream |
| --- | --- | --- |
| Runtime identity | **sufficient** (Gate −1 CLOSED) | not required |
| Drift detection | **sufficient** (`verify_paper2_harness_pin.py`) | not required |
| Reconstruct instrument identity | **sufficient** if on-disk snapshot recoverable | nicer with tagged snapshot |
| Review changes vs upstream OSWorld | **not** closed by SHA alone | **OPTIONAL FOLLOW-UP** |

**Verdict:** Gate −1 provenance for **measurement / execution identity** is
**CLOSED**. Vendor delta reviewability is an **optional follow-up**, not a
Gate −1 failure and **not** a Study-2 blocker. Do not vendor the whole
`external/` tree for this.

---

## 9. STOP

Gate −2 extraction complete.

**Await independent review before any generic-loop implementation.**

Report checklist for reviewers:

1. Frozen invariants — §3 table (**FROZEN** rows)  
2. Allowed changes — transport / endpoint / history serialization / param mapping  
3. Ambiguities — §6  
4. Unextractable literals — §7  
