#!/usr/bin/env bash
# Wave B dummy-guest SELECT-only. Not an experiment. No agent. No patch.
set -euo pipefail

A="${AGENT_ROOT:-/data2/hpcshared/Vinh-/agent}"
if [ ! -d "$A/cf" ] && [ -d "$(cd "$(dirname "$0")/.." && pwd)/cf" ]; then
  A="$(cd "$(dirname "$0")/.." && pwd)"
fi
H="$A/external/MyPCBench-main"
LOG="$A/out/p3_cohort_probe/wave_b.log"
mkdir -p "$A/out/p3_cohort_probe"

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
echo "===== P3 Wave B start $(date -Is) ====="
echo "AGENT_ROOT=$A"
echo "MYPCBENCH_QCOW2=${MYPCBENCH_QCOW2:-}"
test -f "$A/paper/paper3_observation_grounded/p3_cohort_slate16_probes.json"
python3 "$A/scripts/p3_cohort_wave_b.py"
echo "===== P3 Wave B stop $(date -Is) ====="
