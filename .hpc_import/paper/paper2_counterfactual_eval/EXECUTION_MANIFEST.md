# Paper 2 — execution manifest (freeze before cell 1/228)

**Status:** EXECUTION_FROZEN — design closed; agent failure is data.  
**Analysis universe:** `out/paper2_analysis_universe.md` (amended: f024 rejected pre-cell-1)  
**Spec:** `paper/paper2_counterfactual_eval/PAPER2_SPEC.md`  
**Do not** edit \(\mathcal{M}\), \(\mathcal{T}\), \(D\), or this file after cell 1 starts, except dated infra stop (below).

---

## Commitment

| Quantity | Value |
| --- | --- |
| \(\|\mathcal{M}\|\) | 4 |
| \(\|\mathcal{T}\|\) | 25 (seal 27 − f029 − f024) |
| Surviving variants | 32 |
| multi-I (I1+I2) | 7 |
| **Legs** | **228** = \(4\times25\times2 + 4\times7\) |

From cell 1 onward: stop only for **infrastructure** severe enough to halt the whole experiment (Control API dead, disk full, systematic harness bug). Not for “model looks bad / expensive / empty XML rate.”

---

## 0. API lane routing (operational — does not change \(\mathcal{M}\)/\(\mathcal{T}\)/\(D\))

Two OpenRouter-capable budget lanes. **No raw keys in repo/logs** — env vars only.

| Lane | Env (example) | Models |
| --- | --- | --- |
| `SMALL_KEY` | e.g. `OPENROUTER_API_KEY_SMALL` | `qwen/qwen3.5-9b`, `qwen/qwen3.8-flash` only |
| `LARGE_KEY` | e.g. `OPENROUTER_API_KEY_LARGE` / Anthropic+OpenAI native keys | `claude-opus-4-6`, `gpt-5.5` only |

**Model order (full universe per model, no interleaving):**  
1. Qwen 3.5-9B → 2. Qwen 3.8-Flash → 3. Claude Opus 4.6 → 4. GPT-5.5  

**57 legs/model** (\(25\times2+7\)); **228** total. Within a model lane, key assignment is immutable for **official matrix cells**. Exhausting `SMALL_KEY` mid-Qwen: checkpoint, stop, report — **no silent failover to `LARGE_KEY`** without an explicit dated operational amendment. Smoke/cost checks are **not** analysis legs.

Default official routing intent (pre-amendment baseline): Qwen on `SMALL_KEY`; Claude/GPT on native / `LARGE_KEY` lanes. **Do not** silently rebind Claude or GPT to `SMALL_KEY` to match chat assumptions — any such route requires a dated note below.

### Dated operational note — GPT HARD BLOCKED (2026-09-06)

Not a change to \(\mathcal{M}\)/\(\mathcal{T}\)/\(D\). Record only:

| Item | Status |
| --- | --- |
| GPT OpenRouter auto-chain (`paper2_exec_wait_flash_then_gpt_small.sh` → `paper2_exec_gpt_openrouter.sh`) | **Removed / kill-switched.** Waiter now: Flash complete → `FLASH_COMPLETE` → exit. Default `PAPER2_GPT_AUTOSTART=0`. On-disk `results/paper2_exec/gpt-5.5/DO_NOT_AUTO_START_GPT`. |
| Prior GPT-via-OpenRouter legs | **INVALID_INFRASTRUCTURE** (stateless Responses / `previous_response_id`; no client history adapter). Archived under `results/paper2_exec/gpt-5.5-invalid-openrouter-transport/`. Do not aggregate as agent `TERMINAL_FAIL`. |
| Current GPT official execution | **HARD BLOCKED** — no autostart, no retry, no “wiring-only” OpenRouter fix. Native OpenAI also not assumed available (proxy/billing separate). |
| Resume condition | Gate 0 (QEMU tool ownership) → frozen ResponseStateAdapter (or confirmed native path) → protocol/smoke/semantic validation → code review → commit/push → **this manifest amended with adapter freeze hash** → explicit human approval → GPT from leg 1. |

Claude routing changes (below) **do not** unstick GPT.

### Dated operational note — Claude OpenRouter SMALL compatibility smoke only (2026-09-06)

**Not** Claude matrix start. **Not** a change to \(\mathcal{M}\)/\(\mathcal{T}\)/\(D\). Human-approved **provisional** routing for a Gate-0-style tool-ownership smoke:

| Item | Status |
| --- | --- |
| Scope | `scripts/paper2_claude_gate0_openrouter_small.sh` only |
| Key | Bind `OPENROUTER_API_KEY_SMALL` → `ANTHROPIC_API_KEY` (harness client). Scrub native Anthropic backup keys / refuse missing OpenRouter base URL. |
| Base URL | `ANTHROPIC_BASE_URL=https://openrouter.ai/api` (Anthropic Messages–compatible OpenRouter skin). No fallback to `api.anthropic.com`. |
| Matrix | Claude **57 legs remain unstarted** until smoke PASS is reviewed and a further explicit approval amends this file. Official matrix lane for Claude is still planned as native/`LARGE_KEY` unless that later amendment says otherwise. |
| GPT | Unchanged: **HARD BLOCKED**. |

Wiring freeze commit for this smoke is recorded in `out/paper2_api_lane_wiring.md` after push (hash filled on host).

### Dated operational note — Gate −1.5 measurement remediation (2026-09-06)

Not a change to \(\mathcal{M}\)/\(\mathcal{T}\)/\(D\). Measurement-layer fix only:

| Item | Status |
| --- | --- |
| False-DONE root cause | `cell_has_done` matched `"done": true` (also set by `FAIL` / `PREDICT_CRASH` in traj) |
| Canonical rule | `VALID_DONE ⇔ canonical_last_action == "DONE"` via tracked `scripts/paper2_traj_terminal.py` |
| Offline reclass | `scripts/canonical_audit_paper2.py` → `CHECKPOINT.canonical.jsonl` + `canonical_audit.*` (Flash: 27→23 DONE; 4 mismatches). **Original `CHECKPOINT.jsonl` retained** as historical |
| Future checkpoints | Patched `paper2_exec_run.sh` / `paper2_exec_resume_prep.sh` call the canonical helper |
| Harness pin | `out/paper2_harness_pin.json` — tracked patch SHA256 + gitignored upstream harness SHA256 |

Study 1 analysis MUST use `CHECKPOINT.canonical.jsonl` (or equivalent audit), not raw pre-remediation DONE counts.

---

## 1. Harness freeze

| Knob | Frozen value |
| --- | --- |
| Branch / analysis commit | `phase-a-results` @ `4f45faf` (or later **execution-only** commits that do not change \(\mathcal{M}\)/\(\mathcal{T}\)/\(D\)) |
| Models | `claude-opus-4-6` / `claude_cuabash` / Anthropic (`LARGE_KEY` lane) |
|  | `gpt-5.5` / `openai_cuabash` / OpenAI direct (`LARGE_KEY` lane) |
|  | `qwen/qwen3.8-flash` / `qwen_cuabash` / OpenRouter (`SMALL_KEY` lane) |
|  | `qwen/qwen3.5-9b` / `qwen_cuabash` / OpenRouter (`SMALL_KEY` lane) |
| Runner pattern | Paper 1 Stage-4 / Phase-B shells: `run_mypcbench.py --backend qemu` |
| `max_steps` | **80** |
| `timeout` | **7200** s |
| `MYPCBENCH_VM_READY_TIMEOUT` | **3600** |
| `MYPCBENCH_SKIP_QCOW2_REFRESH` | **1** |
| Inject | `scripts/cf_inject.py` + `cf/paper2_interventions.json` (PASS variants only) |
| Judge | `judge_results.py`, `MYPCBENCH_JUDGE_FLAVOR=per_step` (score only; not STS) |
| Persona | `michael.scott@dundermifflin.com` |
| Image | Record `MYPCBENCH_QCOW2` path + sha256 **before cell 1** on the run host (fill below) |

**Image (fill on run host before cell 1):**

```
MYPCBENCH_QCOW2=/mnt/data2/Vinh/agent/external/MyPCBench-main/mypcbench-vm/mypcbench.qcow2
sha256=7c2ddcf2c2e180d07af3a7971b97d45746605005040d74271fb3e494d2f43f59
recorded_at_utc=2026-09-04T07:55:32Z
host=node30
```

Pinned base qcow2 for all 228 cells (Paper 1 / Phase B image). Overlays are per-boot ephemeral; do not swap this base mid-run. `MYPCBENCH_SKIP_QCOW2_REFRESH=1` keeps the pin from auto-refresh.

System prompt / tool config: whatever each `*_cuabash` agent ships in this checkout at the tagged execution commit — do not edit agent wrappers mid-run.

---

## 2. Seed freeze

| Seed | Value | Role |
| --- | --- | --- |
| `PAPER2_EXEC_SEED` | **20260904** | Master seed (new; not `20260826`, not multi-I inventory seed alone) |
| Task order | `Random(PAPER2_EXEC_SEED).shuffle(sorted(T))` once, written to `out/paper2_cell_order.json` **before** cell 1 | Fixed schedule |
| Multi-I order | For each multi-I task: legs `G0` → `G1`(I1) → `G2`(I2) in that order; tasks still follow cell order | No fishing I2 first |
| Episode / env RNG | If harness exposes a seed, set from `PAPER2_EXEC_SEED` + `(model, task, leg)` hash; if not, record “harness-default” per leg | No silent mid-run change |

Write `out/paper2_cell_order.json` and this filled image block **before** the first agent call.

---

## 3. Cell execution policy

| Rule | Frozen choice |
| --- | --- |
| Runs per cell | **1** (one trajectory per `(M, T, leg)`) |
| Legs per task | Base: `G0` then `G1` (I1). Multi-I: then `G2` (I2). Clean guest / snapshot restore between legs (same hygiene as inject-probe) |
| Infra retry (Control API down, QEMU won’t boot, disk I/O) | **At most 1** retry, **same** seed / same cell id; log `infra_retry=1` |
| Agent failure (EMPTY_XML, STEP_LIMIT, AGENT_FAIL, non-DONE) | **No retry** — record as execution failure; not tracking miss; not a reason to drop model |
| API 429 / transient provider error | Treat as infra: ≤1 retry same seed; if still fail → technical failure for that leg |
| Interrupted mid-leg | **Rerun from start** of that leg on clean guest; do not resume mid-trajectory |
| Partial schedule | Do not drop remaining models/tasks to “finish faster.” Pause whole experiment if needed; resume same cell order |

Valid pair (analysis): both legs of a scheduled pair `DONE` (Paper 1 definition). Incomplete ≠ \(Y=0\).

---

## 4. Workflow

1. Tag: `paper2-exec-freeze` on the commit that contains this file + filled image sha + `paper2_cell_order.json`.  
2. Run all **228** legs (or pause only for infra stop).  
3. Collect raw artifacts under a single tree (e.g. `results/paper2_exec/`).  
4. Classify valid pairs / coverage.  
5. **Then** open Layer A / Layer B.

Allowed mid-run monitors: API health, disk, QEMU, corrupted artifacts.  
Forbidden mid-run: STS, \(\Delta S\), ranks, swapping models, rewriting \(D\) or interventions.

---

## 5. Infra stop (only halt condition)

Stop the full experiment if and only if continuing would invalidate comparability (wrong image, wrong inject file, systematic harness corruption). File a dated note; do not quietly change \(\mathcal{M}\) or \(\mathcal{T}\).

### Dated infra stop — Gate 0A Flash parser/protocol defect (2026-09-08)

Not a change to \(\mathcal{M}\)/\(\mathcal{T}\)/\(D\). Not a “model looks bad / empty XML rate” stop (`§` commitment paragraph).

| Item | Status |
| --- | --- |
| Job | Slurm **58337** `hpc-flash-small` on node002 — **CANCELLED** 2026-09-08T04:00:34Z (29/57 checkpointed). Do not continue to 57. |
| Evidence class | **Systematic harness bug:** model emitted semantically unambiguous bash/computer_use XML that the runner dropped (`ImportError` fallback: `generic_executor.near_miss_xml` not on `PYTHONPATH`). Inventory: `out/gate0a_flash_prepatch_parser_inventory.md`. |
| Corpus | Frozen diagnostic only: `results/paper2_exec/_audit/gate0a_flash_prepatch_diagnostic_partial_29of57_20260908T040034Z/`. **Not Study 2 measurement.** Do not merge with post-patch cells. |
| Pre-patch SHA | `e8f628916d0a3e8a23d4af65a23dad296a36f6af` |
| QCOW2 | `sha256=7c2ddcf2c2e180d07af3a7971b97d45746605005040d74271fb3e494d2f43f59` |
| Seed / matrix | `PAPER2_EXEC_SEED=20260904`; `out/paper2_cell_order.json` |
| 9B/GPT | Full-hook replay of archived 9B (57 traj / 480 steps) and archived GPT: **0** `NEAR_MISS_CANONICALIZED`. No 9B rerun. |
| Resume | After review of the validation package only. Fresh OUT_ROOT. Same 57-cell matrix. Parser wire is the only intended instrument change. |

### Dated operational note — §0.15 Flash freeze (2026-09-11)

Not a change to \(\mathcal{M}\)/\(\mathcal{T}\)/\(D\). Post-patch Gate 0A Flash `LANE_COMPLETE` 57/57.

| Item | Status |
| --- | --- |
| Canonical archive | `/data2/hpcshared/Vinh-/agent/results/paper2_exec/hpc-flash-small-gate0a-postpatch` |
| Freeze | `out/study2_flash_freeze.json` + `FLASH_FROZEN.txt`; CHECKPOINT sha256 `663503acfc50faea0745b1e4ff39b06067e070a00f88ea8f62ebf1dcbe06907d` |
| Cells | 57/57 · VALID_DONE 29 / TERMINAL_FAIL 28 (`paper2_traj_terminal.py`) |
| \|A\| (G0∧G1 VALID_DONE; G2 ignored) | Flash **8** · GPT **9** · Claude **1** (report, not rank) |
| n_min | 3 (unchanged). Flash ≥3 → exploratory ranked roster **{GPT, Flash}** |
| Layer B | **NOT confirmatory** (§6.1(c): Claude coverage-only; roster size 2) |
| Pre-patch | Not merged (`hpc-flash-small/`, `_audit/gate0a_flash_prepatch_*`) |
| One-tree copy to `Vinh/agent/.../study2-flash` | Skipped (dest not writable; do not overwrite invalidated `Vinh-` `study2-flash/`) |
| GPT/Claude | Unchanged freeze on `/data2/hpcshared/Vinh/agent` |
| STS / Y | Extractor locked `3242c30`. Exploratory STS/Y on A: `out/study2_sts_pairs.md`, `out/study2_selection_g_sts.md`. Y=0 on all pairs. Layer B still NOT confirmatory |
| Judge | Existing on-disk `rubric_result.json`; **no re-judge** |

### Dated operational note — §0.16 write-up freeze (2026-09-11)

Not a change to \(\mathcal{M}\)/\(\mathcal{T}\)/\(D\). Execution + STS closed. Extractor not retuned.

| Item | Number (must match tables) |
| --- | --- |
| Ranked roster | GPT, Flash. Claude coverage-only |
| \|A\| | GPT **9** · Flash **8** · Claude **1** |
| DONE / 57 | GPT 32 (rate 0.561) · Flash 29 (0.509) · Claude 4 (0.070) |
| Y on A | **0 / 9 · 0 / 8 · 0 / 1** (calibration degenerate) |
| mean \(S^0\) on A | GPT 69.333 · Flash 95.750 · Claude 100 |
| mean pair-STS on A | GPT 0.130 · Flash 0.229 · Claude 0 |
| Common 4 mean \(S^0\) | GPT 49.5 · Flash 96.0 → \(\arg\max S^0\) Flash |
| Common 4 mean STS | GPT 0.250 · Flash 0.208 → \(\arg\max\) STS GPT |
| Bootstrap \(\Delta S^0\) Flash−GPT | +46.5 (CI 21.0–72.0), seed 20260904, n=5000 |
| Bootstrap \(\Delta\)STS Flash−GPT | −0.042 (CI −0.125–0.0) |
| Sign disagree / LOPO | 4/4 tasks; LOPO **fragile** |
| Full-A vs \(\mathcal{A}_\cap\) STS | Flash higher on full A; GPT higher on common 4 (**support flip**; both reported) |
| §6.1(e) excluded S≥90 and not DONE | GPT 2 · Flash 2 · Claude 1 |
| §0.11 | `out/study2_gate011_nearmiss_dual.md` (Flash \|A\| 8 vs rescue-as-rejected 7). Not redone |
| §0.12 | `out/study2_judge_frame_audit.md` — 0 missing rubric on VALID_DONE |
| Layer B | **NOT confirmatory**. Label **EXPLORATORY**. Do not claim GPT more reliable than Flash |
| Hat-D | `3242c30` locked. Apply `71a405d`. No extractor/matching change |

Write-up: `out/study2_layerA.md`, `out/study2_completion_conditional.md`, `out/study2_selection_g.md`, `out/paper_results.md`.
