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
if [ -f .env ]; then
  # shellcheck disable=SC1091
  source .env
fi
if [ -f ./mypcbench-vm/env.sh ]; then
  # shellcheck disable=SC1091
  source ./mypcbench-vm/env.sh
fi
set +a

# Same extracted QEMU Study 2 already used. Not a new install.
# shellcheck disable=SC1091
source "$A/scripts/qemu_datadir_wrap.sh"

if [ ! -f "${MYPCBENCH_QCOW2:-}" ]; then
  for cand in \
    "$A/external/MyPCBench-main/mypcbench-vm/mypcbench.qcow2" \
    /data2/hpcshared/Vinh-/agent/external/MyPCBench-main/mypcbench-vm/mypcbench.qcow2 \
    /data2/hpcshared/Vinh/agent/external/MyPCBench-main/mypcbench-vm/mypcbench.qcow2
  do
    if [ -f "$cand" ]; then
      export MYPCBENCH_QCOW2="$cand"
      break
    fi
  done
fi

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
echo "qemu-img=$(command -v qemu-img || true)"
if ! command -v qemu-img >/dev/null 2>&1; then
  echo "TECHNICAL_ABORT: qemu-img not on PATH after qemu_datadir_wrap.sh"
  echo '{"wave":"B","status":"TECHNICAL_ABORT","n_scored":0,"reason":"qemu-img missing after wrap"}' \
    > "$A/out/p3_cohort_probe/wave_b.json"
  echo "# Wave B TECHNICAL_ABORT — not scored" > "$A/out/p3_cohort_probe/wave_b.md"
  exit 2
fi
if [ ! -f "${MYPCBENCH_QCOW2:-}" ]; then
  echo "TECHNICAL_ABORT: qcow2 missing"
  echo '{"wave":"B","status":"TECHNICAL_ABORT","n_scored":0,"reason":"qcow2 missing"}' \
    > "$A/out/p3_cohort_probe/wave_b.json"
  echo "# Wave B TECHNICAL_ABORT — not scored" > "$A/out/p3_cohort_probe/wave_b.md"
  exit 2
fi
test -f "$A/paper/paper3_observation_grounded/p3_cohort_slate16_probes.json"
python3 "$A/scripts/p3_cohort_wave_b.py"
echo "===== P3 Wave B stop $(date -Is) ====="
