# Transport evidence

## Request shape

`OpenRouterChatCompletionsTransport.build_request`:

- `model`: OpenRouter model id
- `messages`: full client-rebuilt history (stateless)
- generation keys filtered by family config
- **Forbidden** body keys: `previous_response_id`, `tools`, `tool_choice`, `functions`, `function_call`

Auth: `Authorization: Bearer <OPENROUTER_API_KEY>` (Study2 bind fingerprint `sk-or-v1-008…`).

## Response shape

Expect JSON with `choices[0].message.content` (string or multipart text).
Transport extracts plain text for frozen XML parser.
Presence of provider `tool_calls` / `function_call` → `TransportError` fail-closed.

## Retry behavior (429)

From `generic_executor/openrouter_chat.py`:

- `HTTP_429_MAX_RETRIES = 5`
- backoff seconds `(2, 4, 8, 16, 32)`
- logs: `[openrouter] HTTP 429 retry i/5 sleep=…s`
- non-429 HTTP errors: no retry
- exhausted 429 → `TransportError` → runner `PREDICT_CRASH`

## 429 / provider errors observed in this freeze

- Log lines containing `HTTP 429 retry`: **361** (log duplicated by tee in places)
- Predict crash lines (sample last 15):

```
generic_executor.openrouter_chat.TransportError: HTTP 429: {"error":{"message":"Provider returned error","code":429,"metadata":{"raw":"qwen/qwen3.8-flash is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations","provider_name":"Alibaba","is_byok":false,"limit_source":"upstream_provider_shared_pool",
```
```
2026-09-06 18:03:31,107 mypcbench.run ERROR Agent predict crashed at step 3: HTTP 429: {"error":{"message":"Provider returned error","code":429,"metadata":{"raw":"qwen/qwen3.8-flash is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations","provider_name":"Alibaba","is_byok":false,"limit_source":"ups
```
```
generic_executor.openrouter_chat.TransportError: HTTP 429: {"error":{"message":"Provider returned error","code":429,"metadata":{"raw":"qwen/qwen3.8-flash is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations","provider_name":"Alibaba","is_byok":false,"limit_source":"upstream_provider_shared_pool",
```
```
2026-09-07 01:08:59,232 mypcbench.run ERROR Agent predict crashed at step 0: HTTP 429: {"error":{"message":"Provider returned error","code":429,"metadata":{"raw":"qwen/qwen3.8-flash is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations","provider_name":"Alibaba","is_byok":false,"limit_source":"ups
```
```
generic_executor.openrouter_chat.TransportError: HTTP 429: {"error":{"message":"Provider returned error","code":429,"metadata":{"raw":"qwen/qwen3.8-flash is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations","provider_name":"Alibaba","is_byok":false,"limit_source":"upstream_provider_shared_pool",
```
```
2026-09-07 01:08:59,232 mypcbench.run ERROR Agent predict crashed at step 0: HTTP 429: {"error":{"message":"Provider returned error","code":429,"metadata":{"raw":"qwen/qwen3.8-flash is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations","provider_name":"Alibaba","is_byok":false,"limit_source":"ups
```
```
generic_executor.openrouter_chat.TransportError: HTTP 429: {"error":{"message":"Provider returned error","code":429,"metadata":{"raw":"qwen/qwen3.8-flash is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations","provider_name":"Alibaba","is_byok":false,"limit_source":"upstream_provider_shared_pool",
```
```
2026-09-07 04:33:58,639 mypcbench.run ERROR Agent predict crashed at step 17: HTTP 429: {"error":{"message":"Provider returned error","code":429,"metadata":{"raw":"qwen/qwen3.8-flash is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations","provider_name":"Alibaba","is_byok":false,"limit_source":"up
```
```
generic_executor.openrouter_chat.TransportError: HTTP 429: {"error":{"message":"Provider returned error","code":429,"metadata":{"raw":"qwen/qwen3.8-flash is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations","provider_name":"Alibaba","is_byok":false,"limit_source":"upstream_provider_shared_pool",
```
```
2026-09-07 04:33:58,639 mypcbench.run ERROR Agent predict crashed at step 17: HTTP 429: {"error":{"message":"Provider returned error","code":429,"metadata":{"raw":"qwen/qwen3.8-flash is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations","provider_name":"Alibaba","is_byok":false,"limit_source":"up
```
```
generic_executor.openrouter_chat.TransportError: HTTP 429: {"error":{"message":"Provider returned error","code":429,"metadata":{"raw":"qwen/qwen3.8-flash is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations","provider_name":"Alibaba","is_byok":false,"limit_source":"upstream_provider_shared_pool",
```
```
2026-09-07 05:06:55,494 mypcbench.run ERROR Agent predict crashed at step 41: HTTP 429: {"error":{"message":"Provider returned error","code":429,"metadata":{"raw":"qwen/qwen3.8-flash is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations","provider_name":"Alibaba","is_byok":false,"limit_source":"up
```
```
generic_executor.openrouter_chat.TransportError: HTTP 429: {"error":{"message":"Provider returned error","code":429,"metadata":{"raw":"qwen/qwen3.8-flash is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations","provider_name":"Alibaba","is_byok":false,"limit_source":"upstream_provider_shared_pool",
```
```
2026-09-07 05:06:55,494 mypcbench.run ERROR Agent predict crashed at step 41: HTTP 429: {"error":{"message":"Provider returned error","code":429,"metadata":{"raw":"qwen/qwen3.8-flash is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations","provider_name":"Alibaba","is_byok":false,"limit_source":"up
```
```
generic_executor.openrouter_chat.TransportError: HTTP 429: {"error":{"message":"Provider returned error","code":429,"metadata":{"raw":"qwen/qwen3.8-flash is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations","provider_name":"Alibaba","is_byok":false,"limit_source":"upstream_provider_shared_pool",
```

## Could provider error be mistaken for model behavior?

Yes if reviewer only looks at `TERMINAL_FAIL` without traj action:
- Exhausted 429 → `PREDICT_CRASH` with HTTP body in `response` (provider), not model XML.
- Successful HTTP 200 with malformed XML → model/protocol path (EMPTY_XML), **not** provider failure.

## Malformed outputs as successful HTTP?

Yes. EMPTY_XML / MALFORMED_ACTION_SYNTAX cases arrived as normal completions (200) with assistant text that failed frozen parse — see `protocol_contract.md` examples and representative transcripts.
