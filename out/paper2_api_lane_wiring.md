# Paper 2 API lane wiring (host-local — do not commit secrets)

Set on the run host shell / private `.env` (gitignored). **Never** paste values into git, manifest, logs, or chat.

## Required names

| Env var | Lane | Models |
| --- | --- | --- |
| `OPENROUTER_API_KEY_SMALL` | SMALL | `qwen/qwen3.5-9b`, `qwen/qwen3.8-flash` |
| `ANTHROPIC_API_KEY` | LARGE | `claude-opus-4-6` |
| `OPENAI_API_KEY` | LARGE | `gpt-5.5` |
| `OPENROUTER_API_KEY_LARGE` | optional LARGE only | unused by native Claude/GPT wrappers; do **not** feed Qwen |

Legacy single `OPENROUTER_API_KEY` must **not** remain the process env for SMALL jobs once `_SMALL` exists — bind explicitly:

```bash
# Host-local only: add the SMALL / LARGE name bindings in gitignored .env yourself.
# Do not commit that file. Do not paste values into chat or git.

export OPENROUTER_API_KEY="$OPENROUTER_API_KEY_SMALL"
unset OPENROUTER_API_KEY_LARGE ANTHROPIC_API_KEY OPENAI_API_KEY
# then: bash scripts/paper2_exec_small_lane.sh qwen/qwen3.5-9b
```
LARGE Claude/GPT:

```bash
unset OPENROUTER_API_KEY OPENROUTER_API_KEY_SMALL OPENROUTER_API_KEY_LARGE
# Claude: ANTHROPIC_API_KEY only → scripts/paper2_exec_large_lane.sh claude-opus-4-6
# GPT:    OPENAI_API_KEY only    → scripts/paper2_exec_large_lane.sh gpt-5.5
```

**No silent failover** from SMALL → LARGE.

Verify names + routing (no agents): `bash scripts/paper2_exec_dry_run_routing.sh`
