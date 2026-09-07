# Gate 0A Flash instrument — silent-death provenance

## Finding (not an uncaught Exception)

The silent `TERMINAL_FAIL` pattern (`contradiction-f022/G0`, `preference_inference-f010/G1`)
was **not** caused by an exception escaping `predict()`. Bash execution in
`qwen_cua._execute_bash` already catches `Exception` and returns an error string.

### Real provenance (control-flow gap)

In `run_mypcbench.run_single_example`:

1. Empty `actions` increments `consecutive_empty`.
2. If `has_pending` (e.g. `_pending_bash_result`) → write `TOOL_CALL`, `continue`
   **without resetting** `consecutive_empty`.
3. After ≥ `MYPCBENCH_EMPTY_ACTION_RETRIES` (default 3) empty rounds, when pending
   clears, the branch hits:

```text
logger.warning("No actions returned at step %d", ...)
break
```

4. Previously this `break` wrote **no terminal traj row**. Checkpoint logic then
   saw prior `TOOL_CALL` / step rows → `TERMINAL_FAIL` with no explaining action.

### Reproduction (fixture)

`tests/fixtures/gate0a_near_miss/silent_contradiction-f022_G0.json`:

- actions end with `TOOL_CALL`
- `has_predict_crash=false`, `has_empty_xml=false`

### Fix

Before that `break`, write traj action `NO_ACTION_ABORT` with
`info.kind=empty_action_limit` and provenance string.

Additionally wrap `env.step` / screenshot / traj-write in `try/except` →
`EXECUTOR_EXCEPTION` with traceback (covers true exceptions outside `predict()`).

### Traceback note

No historical traceback exists for the silent legs because **no exception was
raised**. The instrument now records explicit terminal rows so future silence
cannot reach `TERMINAL_FAIL` classification without a traj explanation.
