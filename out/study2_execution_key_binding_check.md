# Study 2 — pre-execution funding-key binding check

**Status:** BINDING CHECK ONLY — no Phase 4 signature · no matrix open · no method/N/roster/protocol edit · no cost re-estimate  
**Checked at:** 2026-09-06T16:54:39Z  
**Funding assumption (conditional PASS):** Study 2 must bill **`sk-or-v1-008…9dd`** (`limit_remaining` ≈ **$1268.49**), **not** SMALL `sk-or-v1-c86…37a` (~$28.06).

---

## Verdict

| Gate | Result |
| --- | --- |
| Funding (money exists on 008…9dd) | **PASS (conditional)** — live remaining ≈ $1268.49 |
| **Execution binding (runtime will use 008…9dd)** | **FAIL** |
| Ready to sign Phase 4 / open 171-leg matrix | **No** — bind first |

**One-line:** The funded wallet is on disk as `OPENROUTER_API_KEY_LARGE`, but every documented OpenRouter Study 2 / Gate 0A entrypoint still binds **SMALL** and **scrubs LARGE** — so a run started today would charge the ~$28 key.

---

## 1. Live credential evidence (masked)

Source: `GET https://openrouter.ai/api/v1/key` for each slot (full secrets not recorded).

| Slot | Where found | Fingerprint | Live `label` | `limit` | **`limit_remaining`** | Funding key? |
| --- | --- | --- | --- | ---: | ---: | --- |
| `OPENROUTER_API_KEY_SMALL` | process env (+ same in MyPCBench `.env`) | `sk-or-v1-c86…37a` | `sk-or-v1-c86...37a` | $500 | **$28.06** | No |
| `OPENROUTER_API_KEY_LARGE` | **file only:** `external/MyPCBench-main/.env` | `sk-or-v1-008…9dd` | `sk-or-v1-008...9dd` | $1500 | **$1268.49** | **Yes** |

| Process env at check time | State |
| --- | --- |
| `OPENROUTER_API_KEY_LARGE` exported? | **No (UNSET)** |
| `OPENROUTER_API_KEY` / unbound runtime key | UNSET |
| Agent-root `.env` | missing |

Human-pasted balance for 008…9dd matches this live LARGE pull exactly (`limit_remaining=1268.486531707`).

---

## 2. What runtime would actually bind today

Documented OpenRouter paths (Gate 0A smokes + `paper2_exec_small_lane.sh`) do:

```text
OPENROUTER_API_KEY := OPENROUTER_API_KEY_SMALL
unset OPENROUTER_API_KEY_LARGE
```

Evidence pointers:

| Entrypoint / config | Bind rule |
| --- | --- |
| `scripts/paper2_gate0a_{flash,gpt,claude}_smoke.sh` | bind SMALL; `unset OPENROUTER_API_KEY_LARGE` |
| `generic_executor/gate0a_binding.py` | `key_env_source="OPENROUTER_API_KEY_SMALL"`; `forbid_env_keys` includes `OPENROUTER_API_KEY_LARGE` |
| `scripts/paper2_exec_small_lane.sh` | bind SMALL; scrub LARGE |

**Simulated bound credential under those rules:** `sk-or-v1-c86…37a` (SMALL, ~$28) — **not** 008…9dd.

There is **no** signed Study 2 matrix entrypoint in-tree that sets `OPENROUTER_API_KEY := OPENROUTER_API_KEY_LARGE` for the locked trio (Flash / GPT-5.5 / Claude Opus 4.6) under the generic OpenRouter transport.

---

## 3. Checklist vs required evidence

| Required evidence | Observed |
| --- | --- |
| Masked runtime fingerprint / label = `008…9dd` | **Fail** — runtime bind path → `c86…37a` |
| Live `limit_remaining` on **execution** credential ≈ $1.2k | **Fail for execution path** — execution path’s key has ~$28; 008’s ~$1268 is on **unbound** LARGE file slot |
| No fallback to SMALL | **Fail** — SMALL is the **primary** bind, not a fallback |
| No key rotation / config ambiguity | **Fail** — ambiguity: funded key lives in `*_LARGE` file slot while OpenRouter matrix scripts bind/forbid that slot |

---

## 4. Required bind before Phase 4 signature (ops only — not done here)

Order (as human specified):

1. **Bind** Study 2 execution so the process that runs the 171 legs uses credential fingerprint **`008…9dd`** (live remaining still ~$1.2k), with SMALL **not** charged for main-matrix OpenRouter calls.  
2. Re-run this binding check → expect **PASS**.  
3. **Then** sign Phase 4 lock block (record execution-funding assumption: key `008…9dd`).  
4. Freeze → open 171-leg matrix.

Suggested assumption text for the lock block (when human signs — **not applied now**):

> Study 2 Option L matrix bills OpenRouter key `sk-or-v1-008…9dd` only (`OPENROUTER_API_KEY_LARGE` / explicit Study 2 bind). `OPENROUTER_API_KEY_SMALL` (`c86…37a`) is forbidden for main-matrix legs.

---

## 5. Non-actions (confirmed)

- Phase 4 **not** signed  
- Matrix **not** opened  
- Method / N / roster / protocol **unchanged**  
- No additional cost-envelope pull beyond prior reviews  

---

## 6. Status board (post-check)

| Item | State |
| --- | --- |
| Method/design | PASS |
| Roster | LOCK |
| Option L | selected (`\|T\|=25`, \(N_{\mathrm{fam}}=57\), \(L=171\)) |
| Preregistration | updated, **unsigned** |
| Funding (wallet) | EXECUTABLE on 008…9dd |
| **Funding bind** | **FAIL — not yet plugged into the gun** |
| Matrix | closed |
