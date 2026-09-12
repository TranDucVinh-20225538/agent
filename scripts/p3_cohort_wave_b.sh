#!/usr/bin/env bash
# Wave B dummy-guest SELECT-only. Not an experiment. No agent. No patch.
# Guest paths are resolved for THIS host. node30 .env leftovers are dropped.
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
if [ -f .env ]; then
  # shellcheck disable=SC1091
  source .env
fi
if [ -f ./mypcbench-vm/env.sh ]; then
  # shellcheck disable=SC1091
  source ./mypcbench-vm/env.sh
fi
set +a

unset ANTHROPIC_API_KEY OPENAI_API_KEY OPENROUTER_API_KEY
unset MYPCBENCH_CF_TASK MYPCBENCH_CF_SCRIPT MYPCBENCH_CF_OUT MYPCBENCH_CF_PROBE_ONLY

export A AGENT_ROOT="$A"
export PATH="$H/.venv/bin:${PATH:-}"
export PYTHONPATH="$H/agent-harness${PYTHONPATH:+:$PYTHONPATH}"
export MYPCBENCH_SKIP_QCOW2_REFRESH=1
export MYPCBENCH_VM_READY_TIMEOUT=3600
export MYPCBENCH_VM_HOST=127.0.0.1

_abort() {
  local reason="$1"
  printf '%s\n' "{\"wave\":\"B\",\"status\":\"TECHNICAL_ABORT\",\"n_scored\":0,\"n_survive\":null,\"reason\":$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$reason")}" \
    > "$A/out/p3_cohort_probe/wave_b.json"
  {
    echo "# Wave B TECHNICAL_ABORT — not scored"
    echo
    echo "$reason"
    echo
    echo "Do not run apply_gate on this file."
  } > "$A/out/p3_cohort_probe/wave_b.md"
  echo "TECHNICAL_ABORT: $reason"
  exit 2
}

exec > >(tee -a "$LOG") 2>&1
echo "===== P3 Wave B start $(date -Is) ====="
echo "AGENT_ROOT=$A"

# shellcheck disable=SC1091
if ! source "$A/scripts/p3_cohort_hpc_guest_env.sh"; then
  _abort "HPC guest stack incomplete (see log). node30 .env paths are not used when missing."
fi

test -f "$A/paper/paper3_observation_grounded/p3_cohort_slate16_probes.json"
python3 "$A/scripts/p3_cohort_wave_b.py"
echo "===== P3 Wave B stop $(date -Is) ====="
