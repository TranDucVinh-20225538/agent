# Study 2 plumbing repair — before/after execution audit

**Scope:** execution infrastructure only. Preregistration / universe / N / seed /
roster / cell order **unchanged**.

**Stop:** matrix PIDs killed; `STOPPED_OK` at 2026-09-06T18:14Z.
**Pre-repair archive (not overwritten):**
`results/paper2_exec/_audit/study2-flash-pre_repair_20260906T181448Z/`
plus `results/paper2_exec/study2-flash.INVALIDATED_pre_repair_20260906T181448Z/`.

## Before (invalidated Round-57 Flash attempt)

| Leg | Checkpoint | Evidence |
|-----|------------|----------|
| retrieval-f010 G0 | `TERMINAL_FAIL`, steps=3 | Control API ready → agent steps; later **HTTP 429** → `PREDICT_CRASH` (no retry) |
| retrieval-f010 G1 | `TERMINAL_FAIL`, steps=4 | Same; traj action `PREDICT_CRASH` from upstream Alibaba 429 |
| (started) retrieval-f017 G0 | aborted mid-boot | stopped on human plumbing-repair order |

Log pattern (pre-repair): `Control API ready` immediately then agent loop; **no**
`App readiness gate` lines; first 429 → immediate `TransportError` / `PREDICT_CRASH`.

`_wait_for_apps_ready` was a **no-op**.

## After (plumbing)

| Fix | Behavior |
|-----|----------|
| App readiness | TCP wait on seeded ports incl. **3005**; timeout `MYPCBENCH_APPS_READY_TIMEOUT=300`; fail → `INFRA_FAIL` (no model steps) |
| HTTP 429 | 5 retries, backoff 2/4/8/16/32s on shared `default_http_post`; log each retry |
| Path | Still `study2_run_mypcbench` + OpenRouter for flash/gpt/claude; no SMALL/Gate0A/native |

**Dry validation:** `scripts/study2_plumbing_dry_validate.py` → `ALL_DRY_VALIDATE_PASS`;
`TestHttp429Retry` → OK.

**Docs:** `out/study2_execution_plumbing.md`.

## Rerun plan (post-commit)

Only `retrieval-f010` **G0** then **G1** via
`STUDY2_ONLY_TASK=retrieval-f010 STUDY2_ONLY_LEGS=G0,G1 STUDY2_ALLOW_PARTIAL_LEGS=1`.
Do **not** continue to leg 3 until those results are reported.
Live logs must show `App readiness gate PASS (incl. localhost:3005)` before agent
steps, and `[openrouter] HTTP 429 retry…` if rate-limited.
