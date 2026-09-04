#!/usr/bin/env bash
# Paper 2 SMALL lane — shell plan only (do not execute until human OK).
# Keys: OPENROUTER_API_KEY_SMALL only. Never print key values.
set -euo pipefail
A="${AGENT_ROOT:-/mnt/data2/Vinh/agent}"
H="$A/external/MyPCBench-main"
MODEL="${1:?usage: $0 qwen/qwen3.5-9b|qwen/qwen3.8-flash}"
case "$MODEL" in
  qwen/qwen3.5-9b|qwen/qwen3.8-flash) ;;
  *) echo "SMALL lane rejects $MODEL" >&2; exit 2 ;;
esac
: "${OPENROUTER_API_KEY_SMALL:?set OPENROUTER_API_KEY_SMALL}"
# Bind OpenRouter to SMALL only; scrub other provider keys for this process.
export OPENROUTER_API_KEY="$OPENROUTER_API_KEY_SMALL"
unset OPENROUTER_API_KEY_LARGE ANTHROPIC_API_KEY OPENAI_API_KEY || true
unset OPENROUTER_API_KEY_SMALL  # after bind — child sees only OPENROUTER_API_KEY
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
# Results slug from model id
slug=$(echo "$MODEL" | tr '/.' '--')
OUT="$A/results/paper2_exec/$slug"
mkdir -p "$OUT"
echo "PLAN SMALL model=$MODEL out=$OUT qcow2=$MYPCBENCH_QCOW2"
echo "NEXT: runner must walk out/paper2_cell_order.json with G0/G1/(G2) — not started by this script."
echo "This file is a plan wrapper; invoke the Paper-1-style Stage4/Phase-B runner only after human OK."
