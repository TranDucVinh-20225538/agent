#!/usr/bin/env bash
# Paper 2 LARGE lane — shell plan only (do not execute until human OK).
# Claude: ANTHROPIC_API_KEY. GPT: OPENAI_API_KEY. Never SMALL OpenRouter key.
set -euo pipefail
A="${AGENT_ROOT:-/mnt/data2/Vinh/agent}"
H="$A/external/MyPCBench-main"
MODEL="${1:?usage: $0 claude-opus-4-6|gpt-5.5}"
case "$MODEL" in
  claude-opus-4-6)
    : "${ANTHROPIC_API_KEY:?set ANTHROPIC_API_KEY}"
    unset OPENROUTER_API_KEY OPENROUTER_API_KEY_SMALL OPENAI_API_KEY || true
    AGENT=claude_cuabash
    ;;
  gpt-5.5)
    : "${OPENAI_API_KEY:?set OPENAI_API_KEY}"
    unset OPENROUTER_API_KEY OPENROUTER_API_KEY_SMALL ANTHROPIC_API_KEY || true
    AGENT=openai_cuabash
    ;;
  *) echo "LARGE lane rejects $MODEL" >&2; exit 2 ;;
esac
# Optional: OPENROUTER_API_KEY_LARGE must not leak into Qwen; leave unset for native agents.
unset OPENROUTER_API_KEY_LARGE || true
cd "$H"
set -a
# shellcheck disable=SC1091
source ./mypcbench-vm/env.sh
set +a
export AGENT_ROOT="$A"
export PATH="$H/.venv/bin:$PATH"
export PYTHONPATH="$H/agent-harness${PYTHONPATH:+:$PYTHONPATH}"
export MYPCBENCH_SKIP_QCOW2_REFRESH=1
export MYPCBENCH_VM_READY_TIMEOUT=3600
export MYPCBENCH_VM_HOST=127.0.0.1
export MYPCBENCH_JUDGE_FLAVOR=per_step
export PAPER2_EXEC_SEED=20260904
slug=$(echo "$MODEL" | tr '/.' '--')
OUT="$A/results/paper2_exec/$slug"
mkdir -p "$OUT"
echo "PLAN LARGE model=$MODEL agent=$AGENT out=$OUT qcow2=$MYPCBENCH_QCOW2"
echo "NEXT: runner walks cell_order — not started by this script."
