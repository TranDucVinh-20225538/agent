# Study 2 — execution-key binding recheck (PASS)

**Status:** PASS · pre-launch · no matrix legs started  
**Checked at:** 2026-09-06T16:58:10.766858Z  
**Bind entrypoint:** `scripts/study2_bind_execution_key.sh verify`  
**Env source file:** `external/MyPCBench-main/.env` → slot `OPENROUTER_API_KEY_LARGE`

---

## Verdict: **PASS**

| Criterion | Result |
| --- | --- |
| Runtime fingerprint = `sk-or-v1-008…9dd` | PASS |
| Live `label` = `sk-or-v1-008...9dd` | PASS |
| Live `limit_remaining` ≈ $1.2k | PASS (**$1268.49**; limit $1500) |
| `OPENROUTER_API_KEY_SMALL` unset after bind | PASS |
| `OPENAI_API_KEY` mirrors `OPENROUTER_API_KEY` | PASS |
| Runtime key is not SMALL `c86…37a` | PASS |

---

## Bind semantics (execution path)

```text
OPENROUTER_API_KEY  := OPENROUTER_API_KEY_LARGE   # must be 008…
OPENAI_API_KEY      := same
OPENAI_BASE_URL     := https://openrouter.ai/api/v1
unset OPENROUTER_API_KEY_SMALL OPENROUTER_API_KEY_LARGE ANTHROPIC_API_KEY
```

Main-matrix process trees must **`source scripts/study2_bind_execution_key.sh`** (or run under a launcher that does). Gate 0A smoke scripts that re-bind SMALL are **out of scope** for Study 2 main matrix and must not be used to launch the 171 legs.

---

## Non-actions

- Matrix not started  
- Protocol / roster / universe / N / seed / model IDs unchanged by this check  
