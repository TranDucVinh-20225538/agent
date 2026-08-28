#!/usr/bin/env bash
# Phase B.1: validate the 10 frozen interventions on one dummy guest.
# No Claude/GPT/Qwen. No judge. Do not start B.2 from this script.
set -euo pipefail

A="${AGENT_ROOT:-/mnt/data2/Vinh/agent}"
if [ ! -d "$A/cf" ] && [ -d "$(cd "$(dirname "$0")/.." && pwd)/cf" ]; then
  A="$(cd "$(dirname "$0")/.." && pwd)"
fi
H="$A/external/MyPCBench-main"
LOG="$A/results/phase_b_validate.log"
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
echo "===== Phase B.1 validate start $(date -Is) ====="
echo "python3=$(which python3)"
echo "AGENT_ROOT=$A"
echo "MYPCBENCH_QCOW2=$MYPCBENCH_QCOW2"
python3 "$A/scripts/test_phase_b_inject.py"
python3 "$A/scripts/phase_b_validate.py"
echo "===== Phase B.1 validate stop $(date -Is) ====="
echo "see $A/out/phase_b_validate.md"
echo "STOP: do not start B.2 unless that file says 10/10"
