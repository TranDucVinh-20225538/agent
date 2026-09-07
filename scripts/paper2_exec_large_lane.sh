#!/usr/bin/env bash
# Paper 2 LARGE lane → scripts/paper2_exec_run.sh
# Claude: ANTHROPIC_API_KEY only. GPT: native OPENAI_API_KEY only (no OpenRouter).
set -euo pipefail

A="${AGENT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
H="$A/external/MyPCBench-main"
MODEL="${1:?usage: $0 claude-opus-4-6|gpt-5.5}"

cd "$H"
set -a
# shellcheck disable=SC1091
[ -f .env ] && source .env
# shellcheck disable=SC1091
source ./mypcbench-vm/env.sh
set +a

case "$MODEL" in
  claude-opus-4-6)
    : "${ANTHROPIC_API_KEY:?set ANTHROPIC_API_KEY}"
    unset OPENROUTER_API_KEY OPENROUTER_API_KEY_SMALL OPENROUTER_API_KEY_LARGE OPENAI_API_KEY OPENAI_BASE_URL || true
    SLUG=claude-opus-4-6
    ;;
  gpt-5.5)
    : "${OPENAI_API_KEY:?set OPENAI_API_KEY (native OpenAI — not OpenRouter)}"
    # Hard scrub OpenRouter so GPT cannot silently hit openrouter.ai
    unset OPENROUTER_API_KEY OPENROUTER_API_KEY_SMALL OPENROUTER_API_KEY_LARGE ANTHROPIC_API_KEY OPENAI_BASE_URL || true
    export PAPER2_GPT_VIA=native
    export PAPER2_GPT_KEY_SOURCE=NATIVE_OPENAI
    unset MYPCBENCH_OPENAI_MODEL || true  # use gpt-5.5 native id, not openai/gpt-5.5
    SLUG=gpt-5.5
    ;;
  *) echo "LARGE lane rejects $MODEL" >&2; exit 2 ;;
esac

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

# Refuse to start if official tree still contains OpenRouter invalid markers mixed in
if [ -f "$OUT/INVALID_INFRASTRUCTURE.md" ]; then
  echo "FAIL: $OUT looks like invalid archive; official tree must be clean" >&2
  exit 2
fi

echo "START LARGE model=$MODEL slug=$SLUG out=$OUT qcow2=${MYPCBENCH_QCOW2:-unset}"
echo "binding: OpenRouter=unset; GPT uses native OPENAI_API_KEY only (values hidden)"
echo "exec → scripts/paper2_exec_run.sh (57 legs; no OpenRouter fallback)"

export MODEL LANE=LARGE SLUG
export OUT_ROOT="$OUT"
export LOG="$A/results/paper2_exec_${SLUG}_native.log"

exec bash "$A/scripts/paper2_exec_run.sh"
