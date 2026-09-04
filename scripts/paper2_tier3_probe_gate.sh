#!/usr/bin/env bash
set -euo pipefail
A="${AGENT_ROOT:-/mnt/data2/Vinh/agent}"
H="$A/external/MyPCBench-main"
LOG="$A/results/paper2_tier3_probe_gate.log"
mkdir -p "$A/results" "$A/out"
cd "$H"
set -a
source .env
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
export PAPER2_INVENTORY_TIER=3
exec > >(tee -a "$LOG") 2>&1
echo "===== Paper 2 Tier 3 probe gate start $(date -Is) ====="
python3 "$A/scripts/paper2_tier1_probe_gate.py"
echo "===== Paper 2 Tier 3 probe gate stop $(date -Is) ====="
echo "see $A/out/paper2_tier3_probe_gate.md"
