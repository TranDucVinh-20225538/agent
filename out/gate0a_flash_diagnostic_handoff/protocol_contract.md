# Protocol contract (as implemented — not a paraphrase)

## Action grammar expected by parser

Frozen Qwen XML protocol (from `Qwen35VLAgent` system prompt + `parse_response`):

1. Optional natural-language **Action:** line (short imperative).
2. A single `<tool_call>...</tool_call>` block.
3. Inside: `<function=NAME>` … `</function>` with `<parameter=KEY>value</parameter>` children.

### Accepted function names

| Function | Handled by | Resulting executor actions |
|----------|------------|----------------------------|
| `computer_use` | `parse_xml_tool_call` requires `function=computer_use` | pyautogui.* / WAIT / DONE / FAIL via terminate |
| `bash` | `qwen_cua._extract_bash_command` (separate from computer_use XML parse) | VM shell; traj often `TOOL_CALL`; stdout injected next turn |

### Valid single GUI action (minimal)

```
Action: Click the search box.
<tool_call>
<function=computer_use>
<parameter=action>
click
</parameter>
<parameter=coordinate>
[500, 200]
</parameter>
</function>
</tool_call>
```

### Valid bash

```
Action: List listening ports.
<tool_call>
<function=bash>
<parameter=command>
ss -ltnp | head
</parameter>
</function>
</tool_call>
```

### Valid terminate / DONE

`computer_use` with `action=terminate` and `status=success` maps to traj action `DONE`.
(Also some paths recognize literal DONE in code list.)

### Valid FAIL

`terminate` + `status=failure` → `FAIL`.

### Multi-action

Multiple `<tool_call>` blocks may be scanned by `re.finditer`; each `computer_use` block can append multiple pyautogui lines. Runner executes the returned action list sequentially in one step loop iteration.

## What becomes EMPTY_XML

In `run_mypcbench.run_single_example`, when `predict()` returns **empty `actions`** and the agent is **not** considered to have pending bash/tool state:

- Write traj row `action=EMPTY_XML` with `info.kind=empty_xml_retry`
- Retry until `MYPCBENCH_EMPTY_ACTION_RETRIES` (default 3)
- Then log `No actions returned` and **break** (no DONE)

Common model outputs that yield empty actions under frozen grammar:

- `<function=tool_call>` (function name literally `tool_call`)
- MCP-style names like `mcp__bash__execute`
- `<tool_call>` missing `<function=computer_use>` / `<function=bash>`
- Malformed nesting (`<parameter=computer_use>` instead of `<function=computer_use>`)
- Narrative-only / Action prose without a parseable tool_call

## Narrative before/after actions

System prompt says: optional reasoning **BEFORE** the function call, **NOT after**; order Action then `<tool_call>`; do not output anything else outside those parts.
Parser still extracts tool_calls via regex even if prose surrounds them; however wrong function names still yield empty GUI actions.

## Alternative function-call syntax

Native provider `tool_calls` / OpenAI function_call payloads are **rejected** by OpenRouter transport extract (`TransportError` fail-closed).
XML with non-`computer_use` function names is ignored by `parse_xml_tool_call` (returns None).

## Screenshot attachment

Each non-collapsed history turn attaches screenshot as `image_url` data URL in messages built inside the agent (not always preserved in archived `messages.json`, which often strips to assistant texts).

## Bash output insertion

On bash detect: execute in VM; store result in `_pending_bash_result`; on next `predict`, inject into instruction once; clear pending. Runner may record intermediate `TOOL_CALL` traj rows while `pending_items` / `_pending_bash_result` set.

## Exact stopping rules

1. `DONE` action → episode done → checkpoint **DONE** if canonical last action is `DONE`.
2. `FAIL` / infeasible → done path without VALID_DONE → typically **TERMINAL_FAIL**.
3. `max_steps` (80) reached without DONE → **TERMINAL_FAIL** (`STEP_LIMIT_NO_DONE`).
4. Empty actions × retry limit → abort → **TERMINAL_FAIL**.
5. `predict()` exception (e.g. exhausted HTTP 429) → traj `PREDICT_CRASH` → **TERMINAL_FAIL**.
6. App readiness TimeoutError before steps → `INFRA_FAIL` (not observed as dominant in this freeze).

## Observed model outputs the frozen parser rejected


### Example 1: `contradiction-f022/G1` step 1

```
I'll start by investigating the environment. The browser shows connection errors, so let me first check whether the local web services are actually running.

<tool_call>
<function=tool_call>
<parameter=action>
wait
</parameter>
<parameter=time>
1.0
</parameter>
</function>
</tool_call>
```

### Example 2: `aggregation-f036/G1` step 7

```
Let me click on the page to dismiss the dropdown, then try navigating to Gringotts.

<tool_call>
<parameter=computer_use>
<parameter=action>
left_click
</parameter>
<parameter=coordinate>
[500, 829]
</parameter>
</function>
</tool_call>
```

### Example 3: `contradiction-f014/G1` step 1

```
I'll start by checking whether these local services are actually running, since the page failed to load.

<tool_call>
<function=tool_call>
<parameter=action>
mcp__bash__execute
</parameter>
<parameter=command>
for p in 3001 3002 3003 3004 3005 3014 3015; do echo -n "port $p: "; curl -s -o /dev/null -w "%{http_code}" http://localhost:$p/ ; echo; done
</parameter>
</function>
</tool_call>
```

### Example 4: `counterfactual-f002/G1` step 2

```
All seven services return HTTP 307 — they're actually **up**; the redirect target is what matters. Let me trace where the 307 sends us so I can load them correctly in the browser.

<tool_call>
<parameter=command>
for p in 3001 3012 3016; do echo "== port $p =="; curl -s -D - -o /dev/null --max-time 5 http://localhost:$p/ | egrep -i "^(HTTP|location)"; done
</parameter>
</function>
</tool_call>
```

### Example 5: `preference_inference-f010/G0` step 2

```
Services respond with 307 redirects (normal auth behavior). Let me verify they're actually functional by following redirects, and inspect the local mail store.

<tool_call>
<parameter=bash>
<parameter=command>
echo "=== Follow redirects ==="; for p in 3004 3005 3016; do echo "--- $p ---"; curl -sL --max-time 8 http://localhost:$p/ | head -c 300; echo; done
echo "=== Maildir tree ==="; find /home/user/Maildir -maxdepth 2 -type d 2>/dev/null; echo "--- counts ---"; for d in $(find /home/user/Maildir -maxdepth 2 -type d 2>/dev/null); do echo "$d: $(ls -1 $d 2>/dev/null | wc -l)"; done
</parameter>
</function>
</tool_call>
```
