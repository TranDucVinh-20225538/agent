# Gate 0A v1.1 lock

**Status:** locked for clean Flash rerun  
**Sole execution change vs v1.0:** `max_steps` **4 → 10** (Gate 0A smoke only)

## Explicitly unchanged

- task instruction text
- `GENERIC_AGENT_PROTOCOL_SPEC.md` §3 instruction/protocol
- QEMU environment
- token planting / isolation
- stateless transport
- history construction
- provider/model (`qwen/qwen3.8-flash`, SMALL)
- all ownership checks (P1–P3)

## PASS criterion (both required)

1. Agent emits canonical **DONE** within the allowed **ten** agent turns (predict rounds).
2. Agent-reported token (client bash tool path) matches the planted token **byte-exactly**.

P4 is therefore: complete the task, confirm correct state, then self-terminate in budget — not merely “knows how to stop.”

## Step-budget semantics

`max_steps=10` means **10 predict rounds** (agent turns), 1-indexed rounds `1..10`.

PASS requires successful task completion and explicit DONE within those ten turns; **reaching turn 10 is permitted** if DONE is produced on that turn before budget exhaustion.

Implementation loop: `while not done and step_idx < max_steps`.

## Study 1 clarification

The max_steps change from 4 to 10 applies only to Gate 0A smoke execution under the generic agent loop. It does **not** modify the frozen `max_steps=80` / `timeout=7200` invariants for Study 1 instrument execution (`paper2_exec_run.sh` / legacy `qwen_cuabash` configuration).

## Falsification reading

| Outcome | Interpretation |
| --- | --- |
| PASS at ≤10 | v1.0 FAIL is compatible with “4 steps insufficient to settle completion/termination” |
| FAIL again despite correct token via client bash | stronger evidence for persistent completion-recognition / tool-output utilization failure |

Gate decision does not require reading the reasoning transcript; transcript is qualitative taxonomy evidence only.

## Cross-family (after Flash PASS)

Same v1.1 criteria for GPT then Claude, sequentially (separate artifact +
QEMU container namespace; shared hostfwd ports → do not parallelize).

Do not retune protocol/budget/instruction between families.

