#!/usr/bin/env bash
# Paper 2 GPT via OpenRouter — burn OPENROUTER_API_KEY_SMALL first.
# Same OUT_ROOT as later native/LARGE GPT (results/paper2_exec/gpt-5.5) so resume continues matrix.
# On BUDGET_STOP: exit; do NOT auto-switch to LARGE (human starts large later).
set -euo pipefail

A="${AGENT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
H="$A/external/MyPCBench-main"
KEY_SOURCE="${1:-SMALL}"  # SMALL | LARGE
MODEL=gpt-5.5
SLUG=gpt-5.5

case "$KEY_SOURCE" in
  SMALL|LARGE) ;;
  *) echo "usage: $0 SMALL|LARGE" >&2; exit 2 ;;
esac

cd "$H"
set -a
# shellcheck disable=SC1091
[ -f .env ] && source .env
# shellcheck disable=SC1091
source ./mypcbench-vm/env.sh
set +a

if [ "$KEY_SOURCE" = SMALL ]; then
  : "${OPENROUTER_API_KEY_SMALL:?set OPENROUTER_API_KEY_SMALL}"
  export OPENROUTER_API_KEY="$OPENROUTER_API_KEY_SMALL"
  unset OPENROUTER_API_KEY_LARGE OPENROUTER_API_KEY_SMALL ANTHROPIC_API_KEY || true
  # Scrub native OpenAI so billing cannot silently jump off SMALL.
  unset OPENAI_API_KEY || true
else
  : "${OPENROUTER_API_KEY_LARGE:?set OPENROUTER_API_KEY_LARGE}"
  export OPENROUTER_API_KEY="$OPENROUTER_API_KEY_LARGE"
  unset OPENROUTER_API_KEY_SMALL OPENROUTER_API_KEY_LARGE ANTHROPIC_API_KEY || true
  unset OPENAI_API_KEY || true
fi

export AGENT_ROOT="$A"
export PATH="$H/.venv/bin:$PATH"
export PYTHONPATH="$H/agent-harness${PYTHONPATH:+:$PYTHONPATH}"
export MYPCBENCH_SKIP_QCOW2_REFRESH=1
export MYPCBENCH_VM_READY_TIMEOUT=3600
export MYPCBENCH_VM_HOST=127.0.0.1
export MYPCBENCH_JUDGE_FLAVOR=per_step
export PAPER2_EXEC_SEED=20260904
export PAPER2_GPT_VIA=openrouter
export PAPER2_GPT_KEY_SOURCE="$KEY_SOURCE"

OUT="$A/results/paper2_exec/$SLUG"
mkdir -p "$OUT"
echo "START GPT openrouter key_source=$KEY_SOURCE model=$MODEL out=$OUT"
echo "policy: budget-stop → halt; no auto failover to the other key"
echo "note: operational amendment — GPT temporarily on OpenRouter $KEY_SOURCE before native/LARGE resume"

export MODEL LANE=GPT SLUG
export OUT_ROOT="$OUT"
export LOG="$A/results/paper2_exec_${SLUG}_${KEY_SOURCE}.log"

exec bash "$A/scripts/paper2_exec_run.sh"
