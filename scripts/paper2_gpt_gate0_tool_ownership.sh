#!/usr/bin/env bash
# Gate 0: OpenRouter GPT tool ownership on local QEMU.
# Do NOT start GPT matrix from this script.
set -euo pipefail

A="${AGENT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
H="$A/external/MyPCBench-main"
OUT="${GATE0_OUT:-$A/results/paper2_exec/gpt-5.5-gate0}"

cd "$H"
set -a
# shellcheck disable=SC1091
[ -f .env ] && source .env
# shellcheck disable=SC1091
source ./mypcbench-vm/env.sh
set +a

: "${OPENROUTER_API_KEY_SMALL:?set OPENROUTER_API_KEY_SMALL}"
export OPENROUTER_API_KEY="$OPENROUTER_API_KEY_SMALL"
export OPENAI_API_KEY="$OPENROUTER_API_KEY_SMALL"
export OPENAI_BASE_URL="${OPENAI_BASE_URL:-https://openrouter.ai/api/v1}"
export MYPCBENCH_OPENAI_MODEL="${MYPCBENCH_OPENAI_MODEL:-openai/gpt-5.5}"
unset OPENROUTER_API_KEY_LARGE OPENAI_ORG_ID || true

export AGENT_ROOT="$A"
export PATH="$H/.venv/bin:$PATH"
export PYTHONPATH="$H/agent-harness${PYTHONPATH:+:$PYTHONPATH}"
export MYPCBENCH_SKIP_QCOW2_REFRESH=1
export MYPCBENCH_VM_READY_TIMEOUT="${MYPCBENCH_VM_READY_TIMEOUT:-3600}"
export MYPCBENCH_VM_HOST=127.0.0.1
export GATE0_OUT="$OUT"
export GATE0_CONTAINER="${GATE0_CONTAINER:-mypcbench-gate0}"

mkdir -p "$OUT"
LOG="$OUT/gate0_run.log"
echo "START Gate0 tool-ownership model=$MYPCBENCH_OPENAI_MODEL out=$OUT" | tee "$LOG"

# Prefer pinned image if present
if [ -f "$H/mypcbench-vm/mypcbench.qcow2" ]; then
  export MYPCBENCH_QCOW2="$H/mypcbench-vm/mypcbench.qcow2"
fi

cd "$A"
# QEMU needs host device access; run outside tight sandbox.
exec "$H/.venv/bin/python" -u "$A/scripts/paper2_gpt_gate0_tool_ownership.py" 2>&1 | tee -a "$LOG"
