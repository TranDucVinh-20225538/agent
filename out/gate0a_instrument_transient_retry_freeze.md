# Gate 0A instrument transient-retry freeze

**Decision:** allowed execution plumbing; not a Gate −2 protocol change.

Gate −2 / Phase 1B freezes the full-history, stateless chat-completions
semantics, request schema, family binding, XML protocol, parser/stopping rules,
and absence of provider-native tools/state. It does not freeze HTTP retry
timing or attempt counts. `out/phase1b_review_invariants.md` contains no retry
policy invariant, while `out/study2_execution_plumbing.md` explicitly classifies
provider retry/backoff as execution plumbing.

## Frozen policy for the fresh run

- Retry only transient failures: HTTP 429, HTTP 5xx, and network timeout.
- At most 15 total HTTP attempts and at most 600 seconds wall-clock per logical
  request, including request duration and sleeps.
- Exponential backoff from 5 seconds, capped at 60 seconds, with bounded
  positive jitter of 0–20%.
- Reuse the identical URL, headers, and serialized request body inside the
  original `default_http_post` invocation.
- Do not return to the executor, increment the predict/step counter, restart the
  leg, mutate conversation history, or reset QEMU between retry attempts.
- Non-transient HTTP errors and malformed JSON remain immediate fail-closed
  transport errors.
- Exhaustion becomes `provider unavailable` / `PREDICT_CRASH`; no model or
  provider failover.

## Run boundary

The retry=5 candidate was stopped after checkpointing 1/57 legs and archived
under `results/paper2_exec/_audit/gate0a-flash-instrument_retry5_*`. Its
checkpoint and trajectory are invalid for combination with the fresh run.
The fresh output starts empty at leg 1 under this single frozen policy.
