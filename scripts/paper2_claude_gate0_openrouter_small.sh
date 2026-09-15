#!/usr/bin/env bash
# Claude Gate 0 — OpenRouter SMALL tool-ownership smoke ONLY.
# Does NOT start Claude 57-leg matrix. Does NOT touch GPT policy.
set -euo pipefail

A="${AGENT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
H="$A/external/MyPCBench-main"
OUT="${GATE0_OUT:-$A/results/paper2_exec/claude-opus-4-6-gate0-or-small}"

cd "$H"
set -a
# shellcheck disable=SC1091
[ -f .env ] && source .env
# shellcheck disable=SC1091
source ./mypcbench-vm/env.sh
set +a

: "${OPENROUTER_API_KEY_SMALL:?set OPENROUTER_API_KEY_SMALL}"

# --- Explicit OpenRouter Anthropic-skin binding (no native Anthropic fallback) ---
export OPENROUTER_API_KEY="$OPENROUTER_API_KEY_SMALL"
export ANTHROPIC_API_KEY="$OPENROUTER_API_KEY_SMALL"
export ANTHROPIC_BASE_URL="${ANTHROPIC_BASE_URL:-https://openrouter.ai/api}"
unset ANTHROPIC_API_KEY_BACKUP ANTHROPIC_AUTH_TOKEN || true
# Scrub other lanes so smoke cannot silently bill elsewhere.
unset OPENAI_API_KEY OPENAI_BASE_URL OPENROUTER_API_KEY_LARGE || true
# Keep SMALL name unset after bind (same hygiene as Qwen SMALL lane).
unset OPENROUTER_API_KEY_SMALL || true

case "$ANTHROPIC_BASE_URL" in
  *openrouter.ai*) ;;
  *)
    echo "FAIL: ANTHROPIC_BASE_URL must be OpenRouter Anthropic skin, got: $ANTHROPIC_BASE_URL" >&2
    exit 2
    ;;
esac
case "$ANTHROPIC_API_KEY" in
  sk-or-*) ;;
  *)
    echo "FAIL: ANTHROPIC_API_KEY must be OpenRouter sk-or-* for this smoke (no native Anthropic)." >&2
    exit 2
    ;;
esac

export AGENT_ROOT="$A"
export PATH="$H/.venv/bin:$PATH"
export PYTHONPATH="$H/agent-harness${PYTHONPATH:+:$PYTHONPATH}"
export MYPCBENCH_SKIP_QCOW2_REFRESH=1
export MYPCBENCH_VM_READY_TIMEOUT="${MYPCBENCH_VM_READY_TIMEOUT:-3600}"
export MYPCBENCH_VM_HOST=127.0.0.1
export GATE0_OUT="$OUT"
export GATE0_CONTAINER="${GATE0_CONTAINER:-mypcbench-claude-gate0}"
export MYPCBENCH_CLAUDE_MODEL="${MYPCBENCH_CLAUDE_MODEL:-claude-opus-4-6}"
export PAPER2_CLAUDE_VIA=openrouter_small_smoke
export PAPER2_WIRING_FREEZE_COMMIT="${PAPER2_WIRING_FREEZE_COMMIT:-$(cd "$A" && git rev-parse HEAD)}"

if [ -f "$H/mypcbench-vm/mypcbench.qcow2" ]; then
  export MYPCBENCH_QCOW2="$H/mypcbench-vm/mypcbench.qcow2"
fi

mkdir -p "$OUT"
LOG="$OUT/gate0_run.log"
{
  echo "START Claude Gate0 OR-SMALL smoke"
  echo "model=$MYPCBENCH_CLAUDE_MODEL"
  echo "ANTHROPIC_BASE_URL=$ANTHROPIC_BASE_URL"
  echo "ANTHROPIC_API_KEY=sk-or-*** (bound from SMALL)"
  echo "wiring_freeze_commit=$PAPER2_WIRING_FREEZE_COMMIT"
  echo "out=$OUT"
  echo "policy: smoke only — no Claude matrix"
} | tee "$LOG"

cd "$A"
exec "$H/.venv/bin/python" -u "$A/scripts/paper2_claude_gate0_tool_ownership.py" 2>&1 | tee -a "$LOG"
