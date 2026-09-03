#!/usr/bin/env bash
# Paper 2 §7 Tier 1 inject-probe gate (READY_RELATIVE only).
# No Claude/GPT/Qwen. No judge. Do not touch sealed registry / D.
set -euo pipefail

A="${AGENT_ROOT:-/mnt/data2/Vinh/agent}"
if [ ! -d "$A/cf" ] && [ -d "$(cd "$(dirname "$0")/.." && pwd)/cf" ]; then
  A="$(cd "$(dirname "$0")/.." && pwd)"
fi
H="$A/external/MyPCBench-main"
LOG="$A/results/paper2_tier1_probe_gate.log"
mkdir -p "$A/results" "$A/out"

cd "$H"
set -a
# shellcheck disable=SC1091
source .env
# shellcheck disable=SC1091
source ./mypcbench-vm/env.sh
set +a

unset ANTHROPIC_API_KEY OPENAI_API_KEY OPENROUTER_API_KEY
unset MYPCBENCH_CF_TASK MYPCBENCH_CF_SCRIPT MYPCBENCH_CF_OUT MYPCBENCH_CF_PROBE_ONLY

export AGENT_ROOT="$A"
export PATH="$H/.venv/bin:$PATH"
export PYTHONPATH="$H/agent-harness${PYTHONPATH:+:$PYTHONPATH}"
export MYPCBENCH_SKIP_QCOW2_REFRESH=1
export MYPCBENCH_VM_READY_TIMEOUT=3600
export MYPCBENCH_VM_HOST=127.0.0.1

exec > >(tee -a "$LOG") 2>&1
echo "===== Paper 2 Tier 1 probe gate start $(date -Is) ====="
echo "python3=$(which python3)"
echo "AGENT_ROOT=$A"
echo "MYPCBENCH_QCOW2=$MYPCBENCH_QCOW2"
echo "HEAD_hint=$(cd "$A" && git rev-parse --short HEAD 2>/dev/null || true)"
test -f "$A/cf/paper2_interventions.json"
python3 "$A/scripts/paper2_tier1_probe_gate.py"
echo "===== Paper 2 Tier 1 probe gate stop $(date -Is) ====="
echo "see $A/out/paper2_tier1_probe_gate.md"
