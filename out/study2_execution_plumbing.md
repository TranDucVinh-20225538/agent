# Study 2 — execution plumbing (not methodology)

Signed preregistration, task universe, interventions, prompts, model roster,
N, seed, analysis rules, and cell order are **unchanged**. This document
covers only runtime execution infrastructure.

## 1. QEMU / application readiness gate

**Before (bug):** `_wait_for_apps_ready` was a no-op. Agent step budget could
start after Control API `/health` alone, while guest apps (e.g. workbuzz on
`localhost:3005`) were not yet accepting TCP — observed as Firefox → 3005
before the service was reachable.

**After:** After Control API ready, `_wait_for_apps_ready`:

- TCP-probes required app ports via hostfwd (`vm_ip:port`), always including **3005**
- Optional override: `MYPCBENCH_REQUIRE_APP_PORTS=comma,list`
- Bounded timeout: `MYPCBENCH_APPS_READY_TIMEOUT` (default **300s**), dedicated
  budget (not leftover Control-API remainder)
- Logs: `App readiness gate: waiting…`, per-port ready, `PASS (incl. localhost:3005)`
- Failure → `TimeoutError` → `infra_fail.json` + traj `INFRA_FAIL` with
  `agent_steps_started: false` (checkpoint status `INFRA_FAIL`)

Agent predict loop does **not** start until the gate passes (and post-gate
`_prewarm_lazy_dbs` still runs as before).

## 2. OpenRouter transient-provider handling

**Before:** First HTTP 429 from OpenRouter/upstream became `TransportError` →
traj `PREDICT_CRASH` with no retry (false “model” failure under rate limit).

**Current frozen instrument policy:** `generic_executor.openrouter_chat.default_http_post`
(shared by all Study 2 families via `OpenRouterChatCompletionsTransport`):

| Parameter | Value |
|-----------|--------|
| Retryable failures | HTTP **429**, HTTP **5xx**, network timeout |
| Maximum attempts | **15 total**, including the initial request |
| Wall-clock bound | **600s**, including request time and sleeps |
| Backoff | Exponential from **5s**, capped at **60s**, + 0–20% jitter (final delay also capped at 60s) |
| Request semantics | Retry the identical serialized request inside the same predict turn |
| Logging | `[openrouter] transient retry i/14 …`; exhaustion → `provider unavailable` `TransportError` |

The retry does not restart a leg, advance an agent step, mutate history, or
touch QEMU state. A recovered request therefore resumes the same trajectory
turn. Non-transient HTTP errors and malformed responses still fail immediately.
Exhaustion remains fail-closed after the bounded policy.

The superseded 5-retry policy (2/4/8/16/32s, 429 only) was stopped after one
Gate 0A instrument leg and archived as invalidated; it is not combinable with
the fresh run.

## 3. Shared path (invariant)

All three families (`flash` / `gpt` / `claude`) continue to use:

`study2_bind_execution_key.sh` → `study2_matrix_lane.sh` → `study2_exec_run.sh`
→ `study2_run_mypcbench.py` → `build_qwen_cuabash_agent` +
`OpenRouterChatCompletionsTransport` → `run_mypcbench`.

No SMALL key, Gate 0A, or provider-native agent path for the Study 2 matrix.

## 4. Partial rerun filter (ops only)

`STUDY2_ONLY_TASK` / `STUDY2_ONLY_LEGS` / `STUDY2_ALLOW_PARTIAL_LEGS=1` filter
the locked cell order without rewriting it — used for post-repair G0+G1 only.
