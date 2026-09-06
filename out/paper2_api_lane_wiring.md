# Paper 2 API lane wiring (host-local — do not commit secrets)

Set on the run host shell / private `.env` (gitignored). **Never** paste values into git, manifest, logs, or chat.

## Required names

| Env var | Lane | Models |
| --- | --- | --- |
| `OPENROUTER_API_KEY_SMALL` | SMALL | `qwen/qwen3.5-9b`, `qwen/qwen3.8-flash`; **Claude Gate-0 smoke only** (see below) |
| `ANTHROPIC_API_KEY` | LARGE (official matrix intent) | `claude-opus-4-6` native Anthropic |
| `OPENAI_API_KEY` | LARGE | `gpt-5.5` (official; currently HARD BLOCKED) |
| `OPENROUTER_API_KEY_LARGE` | optional LARGE only | unused by native Claude/GPT wrappers; do **not** feed Qwen |

## SMALL entrypoint (Qwen matrix)

`scripts/paper2_exec_small_lane.sh` sources gitignored `.env`, binds `_SMALL` → `OPENROUTER_API_KEY`, unsets Anthropic / native OpenAI / `_LARGE`, then **exec**s `scripts/paper2_exec_run.sh` (walks frozen `out/paper2_cell_order.json`, 57 legs/model). No failover.

```bash
bash scripts/paper2_exec_small_lane.sh qwen/qwen3.5-9b
```

## LARGE (Claude / GPT matrix — later)

```bash
# Official matrix intent: native Anthropic / OpenAI — not OPENROUTER_API_KEY_SMALL
bash scripts/paper2_exec_large_lane.sh claude-opus-4-6   # matrix not started until smoke+approval
```

**No silent failover** from SMALL → LARGE.

Verify names + routing (no agents / no QEMU): `bash scripts/paper2_exec_dry_run_routing.sh`

## Auto chain

While 9B is live: `tmux` session runs `scripts/paper2_exec_wait_9b_then_flash.sh` (poll → Flash). Fresh host: `scripts/paper2_exec_small_9b_then_flash.sh`. No Flash after `BUDGET_STOP`.

Flash → GPT waiter: **does not launch GPT** (`PAPER2_GPT_AUTOSTART` default 0; launch path excised). See GPT HARD BLOCK below.

## Claude OpenRouter SMALL — compatibility smoke ONLY (2026-09-06)

Human-approved **provisional** routing for tool-ownership Gate 0. **Not** Claude 57-leg matrix start. Does **not** change GPT policy.

Wiring (smoke entrypoint only — `scripts/paper2_claude_gate0_openrouter_small.sh`):

| Knob | Value |
| --- | --- |
| Key source | `OPENROUTER_API_KEY_SMALL` |
| Harness key | `ANTHROPIC_API_KEY` ← SMALL OpenRouter key (`sk-or-…`) |
| Base URL | `ANTHROPIC_BASE_URL=https://openrouter.ai/api` (Anthropic Messages–compatible skin) |
| Native fallback | Forbidden: unset `ANTHROPIC_API_KEY_BACKUP`; refuse if base URL is not OpenRouter |
| Model | default `claude-opus-4-6` (override with `MYPCBENCH_CLAUDE_MODEL` if OR requires `anthropic/…` id) |
| Artifact root | `results/paper2_exec/claude-opus-4-6-gate0-or-small/` |

```bash
# After wiring freeze commit is pushed:
bash scripts/paper2_claude_gate0_openrouter_small.sh
```

Pass Gate 0 ≠ start matrix. Review smoke report, then further human approval before any Claude matrix.

**Wiring freeze commit (filled after push):** `WIRING_FREEZE_COMMIT=0ae55b417dfc17a0ec5252c2a73dac7439227f26`

## GPT HARD BLOCKED

OpenRouter GPT attempt archived at `results/paper2_exec/gpt-5.5-invalid-openrouter-transport/` (`INVALID_INFRASTRUCTURE`). Gate 0 GPT FAIL: provider-pre-executed `shell_call_output`. Do not aggregate those legs as agent `TERMINAL_FAIL`. Kill-switch: `PAPER2_GPT_AUTOSTART=0`, `DO_NOT_AUTO_START_GPT`. Claude OR smoke does **not** unstick GPT.
