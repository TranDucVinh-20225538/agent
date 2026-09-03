#!/usr/bin/env bash
# Re-run Paper 2 Tier 1 units that hit technical failure (f020 lock / f040 restore).
set -euo pipefail

A="${AGENT_ROOT:-/mnt/data2/Vinh/agent}"
if [ ! -d "$A/cf" ] && [ -d "$(cd "$(dirname "$0")/.." && pwd)/cf" ]; then
  A="$(cd "$(dirname "$0")/.." && pwd)"
fi
H="$A/external/MyPCBench-main"
LOG="$A/results/paper2_tier1_probe_rerun.log"
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
echo "===== Paper 2 Tier 1 probe rerun start $(date -Is) ====="
python3 "$A/scripts/paper2_tier1_probe_rerun.py"
echo "===== Paper 2 Tier 1 probe rerun stop $(date -Is) ====="
echo "see $A/out/paper2_tier1_probe_gate.md"
