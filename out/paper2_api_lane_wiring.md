# Paper 2 API lane wiring (host-local — do not commit secrets)

Set on the run host shell / private `.env` (gitignored). **Never** paste values into git, manifest, logs, or chat.

## Required names

| Env var | Lane | Models |
| --- | --- | --- |
| `OPENROUTER_API_KEY_SMALL` | SMALL | `qwen/qwen3.5-9b`, `qwen/qwen3.8-flash` |
| `ANTHROPIC_API_KEY` | LARGE | `claude-opus-4-6` |
| `OPENAI_API_KEY` | LARGE | `gpt-5.5` |
| `OPENROUTER_API_KEY_LARGE` | optional LARGE only | unused by native Claude/GPT wrappers; do **not** feed Qwen |

## SMALL entrypoint

`scripts/paper2_exec_small_lane.sh` sources gitignored `.env`, binds `_SMALL` → `OPENROUTER_API_KEY`, unsets Anthropic / native OpenAI / `_LARGE`, then **exec**s `scripts/paper2_exec_run.sh` (walks frozen `out/paper2_cell_order.json`, 57 legs/model). No failover.

```bash
bash scripts/paper2_exec_small_lane.sh qwen/qwen3.5-9b
```

## LARGE (later)

```bash
# Claude / GPT native keys only — never OPENROUTER_API_KEY_SMALL
bash scripts/paper2_exec_large_lane.sh claude-opus-4-6   # still plan until wired+OK
```

**No silent failover** from SMALL → LARGE.

Verify names + routing (no agents / no QEMU): `bash scripts/paper2_exec_dry_run_routing.sh`
