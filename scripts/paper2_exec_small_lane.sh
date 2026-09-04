#!/usr/bin/env bash
# Paper 2 SMALL lane entrypoint → scripts/paper2_exec_run.sh
# Qwen only. Bind OPENROUTER_API_KEY from _SMALL; scrub LARGE / Anthropic / native OpenAI.
# No failover. Never print key values.
set -euo pipefail

A="${AGENT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
H="$A/external/MyPCBench-main"
MODEL="${1:?usage: $0 qwen/qwen3.5-9b|qwen/qwen3.8-flash}"

case "$MODEL" in
  qwen/qwen3.5-9b) SLUG=qwen35-9b ;;
  qwen/qwen3.8-flash) SLUG=qwen38-flash ;;
  *) echo "SMALL lane rejects $MODEL" >&2; exit 2 ;;
esac

cd "$H"
set -a
# shellcheck disable=SC1091
[ -f .env ] && source .env
# shellcheck disable=SC1091
source ./mypcbench-vm/env.sh
set +a

: "${OPENROUTER_API_KEY_SMALL:?set OPENROUTER_API_KEY_SMALL in host .env}"

# Bind OpenRouter to SMALL only; scrub other provider keys for this process tree.
export OPENROUTER_API_KEY="$OPENROUTER_API_KEY_SMALL"
unset OPENROUTER_API_KEY_LARGE ANTHROPIC_API_KEY OPENAI_API_KEY OPENAI_BASE_URL || true
unset OPENROUTER_API_KEY_SMALL  # after bind — child sees OPENROUTER_API_KEY only

export AGENT_ROOT="$A"
export PATH="$H/.venv/bin:$PATH"
export PYTHONPATH="$H/agent-harness${PYTHONPATH:+:$PYTHONPATH}"
export MYPCBENCH_SKIP_QCOW2_REFRESH=1
export MYPCBENCH_VM_READY_TIMEOUT=3600
export MYPCBENCH_VM_HOST=127.0.0.1
export MYPCBENCH_JUDGE_FLAVOR=per_step
export PAPER2_EXEC_SEED=20260904

OUT="$A/results/paper2_exec/$SLUG"
mkdir -p "$OUT"

echo "START SMALL model=$MODEL slug=$SLUG out=$OUT qcow2=${MYPCBENCH_QCOW2:-unset}"
echo "binding: OPENROUTER_API_KEY=set ANTHROPIC=unset LARGE=unset (values hidden)"
echo "exec → scripts/paper2_exec_run.sh (57 legs max for this model; no failover)"

export MODEL LANE=SMALL SLUG
export OUT_ROOT="$OUT"
export LOG="$A/results/paper2_exec_${SLUG}.log"

exec bash "$A/scripts/paper2_exec_run.sh"
