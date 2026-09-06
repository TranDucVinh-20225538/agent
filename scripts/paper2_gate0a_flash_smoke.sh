#!/usr/bin/env bash
# Gate 0A — Flash controlled smoke (OpenRouter SMALL only).
# One smoke. No matrix. No GPT/Claude. No LARGE.
set -euo pipefail
A="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$A"

FREEZE_SHA="${GATE0A_FREEZE_SHA:-dd43cbea0150772a804c22cec1c9ddcdb6c94789}"
HEAD="$(git rev-parse HEAD)"
if [ "$HEAD" != "$FREEZE_SHA" ] && ! git merge-base --is-ancestor "$FREEZE_SHA" HEAD; then
  echo "FAIL: freeze tip $FREEZE_SHA not ancestor of HEAD=$HEAD" >&2
  exit 2
fi
echo "freeze_pin=$FREEZE_SHA HEAD=$(git rev-parse --short HEAD)"

: "${OPENROUTER_API_KEY_SMALL:?set OPENROUTER_API_KEY_SMALL}"

# Bind SMALL only; scrub other providers (same hygiene as paper2_exec_small_lane.sh).
export OPENROUTER_API_KEY="$OPENROUTER_API_KEY_SMALL"
export OPENAI_API_KEY="$OPENROUTER_API_KEY_SMALL"
export OPENAI_BASE_URL="${OPENAI_BASE_URL:-https://openrouter.ai/api/v1}"
unset OPENROUTER_API_KEY_LARGE ANTHROPIC_API_KEY OPENAI_ORG_ID || true
unset OPENROUTER_API_KEY_SMALL || true

export MYPCBENCH_QCOW2="${MYPCBENCH_QCOW2:-$A/external/MyPCBench-main/mypcbench-vm/mypcbench.qcow2}"
test -f "$MYPCBENCH_QCOW2" || { echo "qcow2 missing: $MYPCBENCH_QCOW2" >&2; exit 2; }

export GATE0A_OUT="${GATE0A_OUT:-$A/results/paper2_exec/gate0a-flash}"
export GATE0A_FREEZE_SHA="$FREEZE_SHA"
export GATE0A_MODEL="qwen/qwen3.8-flash"
export GATE0A_MAX_STEPS="${GATE0A_MAX_STEPS:-4}"
export PYTHONPATH="$A/external/MyPCBench-main/agent-harness:$A/scripts:$A:${PYTHONPATH:-}"

mkdir -p "$GATE0A_OUT"
echo "START Gate0A Flash smoke out=$GATE0A_OUT model=$GATE0A_MODEL max_steps=$GATE0A_MAX_STEPS"
echo "binding: SMALL=set LARGE=unset ANTHROPIC=unset (values hidden)"
echo "qcow2=$MYPCBENCH_QCOW2"

# Prefer harness venv if present
PY=python3
[ -x "$A/external/MyPCBench-main/.venv/bin/python" ] && PY="$A/external/MyPCBench-main/.venv/bin/python"

exec "$PY" "$A/scripts/paper2_gate0a_flash_smoke.py"
