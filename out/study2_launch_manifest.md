# Study 2 — launch manifest / execution snapshot

**Status:** `READY_TO_LAUNCH` — pre-launch complete · **matrix not started**  
**Created at (UTC):** 2026-09-06T16:59:38.744767Z  
**Machine-readable twin:** `out/study2_launch_manifest.json`

---

## 1. Freeze pointers

| Item | Value |
| --- | --- |
| Git commit | `9847d814f867e6c059869d4ce819c267db632cf8` (`9847d81`) |
| Branch | `generic-executor-phase1` |
| Phase 4 prereg | `out/study2_phase4_preregistration.md` — **LOCKED / SIGNED** |
| Locked prereg SHA-256 | `6803c6439af8ec579d6c74e3597bee5d3a3743bcd21b23b0145d7f4d33542a33` |
| Roster lock | `out/study2_roster_lock.md` |
| Binding recheck | `out/study2_execution_key_binding_recheck.md` — **PASS** @ 2026-09-06T16:58:10Z |
| Bind script | `scripts/study2_bind_execution_key.sh` |

---

## 2. Roster / model IDs

| Family | Model ID | Output directory (reserved) |
| --- | --- | --- |
| Qwen | `qwen/qwen3.8-flash` | `results/paper2_exec/study2-flash` |
| OpenAI | `openai/gpt-5.5` | `results/paper2_exec/study2-gpt` |
| Anthropic | `anthropic/claude-opus-4.6` | `results/paper2_exec/study2-claude` |

---

## 3. Fixed matrix (Option L)

| Quantity | Value |
| --- | ---: |
| \|T\| | **25** |
| multiI | **7** |
| \(N_{\mathrm{fam}}\) | **57** |
| \|M\| | **3** |
| Total legs | **171** |
| Cell order | `out/paper2_cell_order.json` |
| Seed (carry-forward) | `20260904` |

---

## 4. Execution funding (bound runtime)

| Field | Value |
| --- | --- |
| Fingerprint (masked) | `sk-or-v1-008…9dd` |
| Live label | `sk-or-v1-008...9dd` |
| Source slot (pre-bind) | `OPENROUTER_API_KEY_LARGE` |
| Starting `limit` | $1500 |
| Starting `limit_remaining` | **$1268.486531707** |
| Starting `usage` | $231.513468293 |
| Balance timestamp (UTC) | 2026-09-06T16:58:10.766858Z |
| SMALL (`c86…37a`) for main matrix | **Forbidden** |

Launch rule: every main-matrix process tree must bind via `source scripts/study2_bind_execution_key.sh` before any OpenRouter call. Do **not** use Gate 0A smoke entrypoints (they re-bind SMALL).

---

## 5. Pre-launch confirmation — no main-matrix legs yet

| Check | Result |
| --- | --- |
| `results/paper2_exec/study2*` dirs | **none** |
| Study 2 CHECKPOINT*.jsonl | **none** |
| Reserved out dirs exist | **no** (created at launch) |
| `matrix_started` | **false** |

Study 1 / Gate 0A / invalid-transport artifacts under other `results/paper2_exec/*` paths are **not** Study 2 main-matrix legs.

---

## 6. What this manifest authorizes next

Pre-launch sequence is complete. **This artifact does not start the matrix.**  
Next human/agent step (separate): open the 171-leg Study 2 matrix under the bind script + these output paths, without changing protocol, roster, universe, N, seed, or model configuration.
