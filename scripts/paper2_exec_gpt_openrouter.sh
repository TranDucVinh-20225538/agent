#!/usr/bin/env bash
# Paper 2 GPT via OpenRouter — HARD BLOCKED by default.
#
# Do not use for official Paper 2 GPT cells until:
#   Gate 0 PASS → ResponseStateAdapter frozen → validation → manifest amendment
#   → explicit human approval (PAPER2_GPT_AUTOSTART=1 AND remove DO_NOT_AUTO_START_GPT).
#
# Wiring note (even when unblocked later): agent reads OPENAI_API_KEY + OPENAI_BASE_URL;
# OPENROUTER_API_KEY alone is not enough (mirror Qwen OpenRouter pattern).
set -euo pipefail

A="${AGENT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
H="$A/external/MyPCBench-main"
KEY_SOURCE="${1:-SMALL}"  # SMALL | LARGE
MODEL=gpt-5.5
SLUG=gpt-5.5
OUT="$A/results/paper2_exec/$SLUG"
mkdir -p "$OUT"

case "$KEY_SOURCE" in
  SMALL|LARGE) ;;
  *) echo "usage: $0 SMALL|LARGE" >&2; exit 2 ;;
esac

# Kill-switch: default block. Require BOTH env enable AND absence of on-disk block.
PAPER2_GPT_AUTOSTART="${PAPER2_GPT_AUTOSTART:-0}"
if [ "$PAPER2_GPT_AUTOSTART" != "1" ] || [ -f "$OUT/DO_NOT_AUTO_START_GPT" ]; then
  echo "BLOCKED: GPT OpenRouter entrypoint." >&2
  echo "  PAPER2_GPT_AUTOSTART=${PAPER2_GPT_AUTOSTART} (need 1)" >&2
  echo "  DO_NOT_AUTO_START_GPT=$OUT/DO_NOT_AUTO_START_GPT (must be absent)" >&2
  echo "  See $OUT/PAUSE.md — Gate0 + adapter freeze required first." >&2
  date -Is >> "$OUT/GPT_LAUNCH_BLOCKED.txt"
  exit 78
fi

# Runner also refuses openrouter until adapter exists.
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
  export OPENAI_API_KEY="$OPENROUTER_API_KEY_SMALL"
  export OPENAI_BASE_URL="${OPENAI_BASE_URL:-https://openrouter.ai/api/v1}"
  unset OPENROUTER_API_KEY_LARGE OPENROUTER_API_KEY_SMALL ANTHROPIC_API_KEY || true
else
  : "${OPENROUTER_API_KEY_LARGE:?set OPENROUTER_API_KEY_LARGE}"
  export OPENROUTER_API_KEY="$OPENROUTER_API_KEY_LARGE"
  export OPENAI_API_KEY="$OPENROUTER_API_KEY_LARGE"
  export OPENAI_BASE_URL="${OPENAI_BASE_URL:-https://openrouter.ai/api/v1}"
  unset OPENROUTER_API_KEY_SMALL OPENROUTER_API_KEY_LARGE ANTHROPIC_API_KEY || true
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

echo "START GPT openrouter key_source=$KEY_SOURCE model=$MODEL out=$OUT"
echo "policy: budget-stop → halt; no auto failover"

export MODEL LANE=GPT SLUG
export OUT_ROOT="$OUT"
export LOG="$A/results/paper2_exec_${SLUG}_${KEY_SOURCE}.log"

# paper2_exec_run.sh currently dies on PAPER2_GPT_VIA=openrouter — intentional until adapter.
exec bash "$A/scripts/paper2_exec_run.sh"
