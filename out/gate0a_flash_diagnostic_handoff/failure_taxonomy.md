# Gate 0A Flash — failure taxonomy (raw mechanism)

Source run: Study-2-entry Flash matrix legs treated as **Gate 0A pilot diagnostic only**.

Do not collapse categories.


## MALFORMED_ACTION_SYNTAX

- **count:** 5

- affected: contradiction-f022/G1, aggregation-f036/G1, contradiction-f014/G1, counterfactual-f002/G1, preference_inference-f010/G0


### Representative: `contradiction-f022/G1`

- steps=2 canonical_last='EMPTY_XML' first_invalid_step=1

- traj: `/mnt/data2/Vinh/agent/results/paper2_exec/study2-flash/contradiction-f022/G1/contradiction-f022/traj.jsonl`

- raw response excerpt:

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

- parser result: no `computer_use`/`bash` function match → empty action list

- executor behavior: log `EMPTY_XML` retries (limit 3) then abort without DONE

- why: response contains `<tool_call>` but function name is `tool_call` / mcp-style / missing function=bash|computer_use


### Representative: `aggregation-f036/G1`

- steps=45 canonical_last='TOOL_CALL' first_invalid_step=7

- traj: `/mnt/data2/Vinh/agent/results/paper2_exec/study2-flash/aggregation-f036/G1/aggregation-f036/traj.jsonl`

- raw response excerpt:

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

- parser result: no `computer_use`/`bash` function match → empty action list

- executor behavior: log `EMPTY_XML` retries (limit 3) then abort without DONE

- why: response contains `<tool_call>` but function name is `tool_call` / mcp-style / missing function=bash|computer_use


## EMPTY_ACTION

- **count:** 1

- affected: preference_inference-f010/G1


### Representative: `preference_inference-f010/G1`

- steps=4 canonical_last='TOOL_CALL' first_invalid_step=1

- traj: `/mnt/data2/Vinh/agent/results/paper2_exec/study2-flash/preference_inference-f010/G1/preference_inference-f010/traj.jsonl`

- raw response excerpt:

```
I'll start by investigating the environment to understand what email data is available and how to analyze reply-time patterns.

<tool_call>
<function=computer_use>
<parameter=action>
screenshot
</parameter>
</function>
</tool_call>
```

- parser result: empty action list

- executor behavior: EMPTY_XML retry then stop

- why: no valid prior GUI/bash action; empty from start


## NO_ACTION_AFTER_VALID_ACTION

- **count:** 4

- affected: contradiction-f022/G0, counterfactual-f013/G0, aggregation-f036/G0, aggregation-f020/G0


### Representative: `contradiction-f022/G0`

- steps=3 canonical_last='TOOL_CALL' first_invalid_step=None

- traj: `/mnt/data2/Vinh/agent/results/paper2_exec/study2-flash/contradiction-f022/G0/contradiction-f022/traj.jsonl`

- raw response excerpt:

```
The curl output didn't render. Let me diagnose connectivity and the redirect loop properly.

<tool_call>
<function=bash>
<parameter=command>
echo "--- listening ports ---"; ss -ltnp 2>/dev/null | grep -E ':(30[0-1][0-9])' | sort; echo "--- env proxies ---"; env | grep -i proxy; echo "--- gsettings proxy mode ---"; gsettings get org.gnome.system.proxy mode 2>/dev/null; echo "--- firefox prefs proxy ---"; find ~/.mozilla -name prefs.js -exec grep -i "proxy" {} \; 2>/dev/null | head
</parameter>
</
```

- parser result: empty on a later turn after prior TOOL_CALL/GUI

- executor behavior: `No actions returned` → abort

- why: had prior valid/tool activity then empty prediction


### Representative: `counterfactual-f013/G0`

- steps=3 canonical_last='TOOL_CALL' first_invalid_step=None

- traj: `/mnt/data2/Vinh/agent/results/paper2_exec/study2-flash/counterfactual-f013/G0/counterfactual-f013/traj.jsonl`

- raw response excerpt:

```
I have the sequel notes context. Now let me investigate the three financial sources. First, let me check what's available locally and how the apps serve data.

<tool_call>
<function=bash>
<parameter=command>
echo "=== LISTENING PORTS ==="; ss -ltnp 2>/dev/null | grep -E ':30(0[1-9]|1[0-7])' ; echo; echo "=== FIND APP DATA DIRS ==="; find / -maxdepth 6 \( -iname "*.sqlite*" -o -iname "*.db" \) 2>/dev/null | grep -iE 'gringott|batbucks|odds|hooli|dinoco|app|server|data' | head -50
</parameter>
</f
```

- parser result: empty on a later turn after prior TOOL_CALL/GUI

- executor behavior: `No actions returned` → abort

- why: had prior valid/tool activity then empty prediction


## STEP_LIMIT_NO_DONE

- **count:** 5

- affected: counterfactual-f002/G0, retrieval-f005/G0, retrieval-f005/G1, contradiction-f003/G0, contradiction-f017/G1


### Representative: `counterfactual-f002/G0`

- steps=81 canonical_last='pyautogui.scroll(-3, x=640, y=444)' first_invalid_step=45

- traj: `/mnt/data2/Vinh/agent/results/paper2_exec/study2-flash/counterfactual-f002/G0/counterfactual-f002/traj.jsonl`

- raw response excerpt:

```
I found the data stores under `/data/vms/michael_scott/`. Let me query the financial databases directly.

<tool_call>
<parameter=bash>
<parameter=command>
cd /data/vms/michael_scott; echo "===== VAULTBANK tables ====="; sqlite3 vaultbank.sqlite ".tables" 2>/dev/null; echo "===== ODDSMARKET tables ====="; sqlite3 oddsmarket.sqlite ".tables" 2>/dev/null; echo "===== find batbucks ====="; ls /data | grep -i bat; ls /opt/apps/batbucks 2>/dev/null; find /data -iname "*batbucks*" 2>/dev/null
</paramet
```

- parser result: usually still producing pyautogui/WAIT

- executor behavior: hit max_steps=80; checkpoint TERMINAL_FAIL (no canonical DONE)

- why: steps≥80 and never emitted DONE


### Representative: `retrieval-f005/G0`

- steps=82 canonical_last='pyautogui.click(804, 52)' first_invalid_step=None

- traj: `/mnt/data2/Vinh/agent/results/paper2_exec/study2-flash/retrieval-f005/G0/retrieval-f005/traj.jsonl`

- raw response excerpt:

```
Let me open a new tab and navigate to HooliMail to search for subscription emails.

<tool_call>
<function=computer_use>
<parameter=action>
left_click
</parameter>
<parameter=coordinate>
[628, 65]
</parameter>
</function>
</tool_call>
```

- parser result: usually still producing pyautogui/WAIT

- executor behavior: hit max_steps=80; checkpoint TERMINAL_FAIL (no canonical DONE)

- why: steps≥80 and never emitted DONE


## EXPLICIT_FAIL

- **count:** 0

- affected: _(none in this freeze)_

- why assigned: category reserved; no legs matched mechanical rules below.


## PROVIDER_RATE_LIMIT

- **count:** 3

- affected: counterfactual-f002/G2, contradiction-f003/G1, contradiction-f017/G0


### Representative: `counterfactual-f002/G2`

- steps=1 canonical_last='PREDICT_CRASH' first_invalid_step=1

- traj: `/mnt/data2/Vinh/agent/results/paper2_exec/study2-flash/counterfactual-f002/G2/counterfactual-f002/traj.jsonl`

- raw response excerpt:

```
HTTP 429: {"error":{"message":"Provider returned error","code":429,"metadata":{"raw":"qwen/qwen3.8-flash is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations","provider_name":"Alibaba","is_byok":false,"limit_source":"upstream_provider_shared_pool","remedy_hint":"Retry shortly, add your own provider key (https://openrouter.ai/settings/integrations), or route to another provider with provider rou
```

- parser result: N/A (transport raised before parse)

- executor behavior: after 429 retries exhausted → traj `PREDICT_CRASH`

- why: HTTP 429 from OpenRouter/upstream in response


### Representative: `contradiction-f003/G1`

- steps=18 canonical_last='PREDICT_CRASH' first_invalid_step=3

- traj: `/mnt/data2/Vinh/agent/results/paper2_exec/study2-flash/contradiction-f003/G1/contradiction-f003/traj.jsonl`

- raw response excerpt:

```
The Dinoco dashboard has loaded. Note an important discrepancy already: the profile shows **Silver Voyager**, not Gold Voyager as you mentioned, with a **19,225 mile** balance and **32,100 MQMs** this year. Let me examine your trips in detail by clicking "My Trips".

<tool_call>
<parameter=computer_use>
<parameter=action>
left_click
</parameter>
<parameter=coordinate>
[477, 224]
</parameter>
</function>
</tool_call>
```

- parser result: N/A (transport raised before parse)

- executor behavior: after 429 retries exhausted → traj `PREDICT_CRASH`

- why: HTTP 429 from OpenRouter/upstream in response


## PROVIDER_CRASH

- **count:** 0

- affected: _(none in this freeze)_

- why assigned: category reserved; no legs matched mechanical rules below.


## EXECUTOR_EXCEPTION

- **count:** 0

- affected: _(none in this freeze)_

- why assigned: category reserved; no legs matched mechanical rules below.


## OTHER

- **count:** 0

- affected: _(none in this freeze)_

- why assigned: category reserved; no legs matched mechanical rules below.

