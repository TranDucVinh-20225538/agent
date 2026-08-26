#!/usr/bin/env bash
# Stage 3: dummy/schema identifiability probes for the frozen 10 eligible tasks.
# One long-lived TCG guest. SELECT only. $0 Claude. No judge. No Stage 4.
set -euo pipefail

A=/mnt/data2/Vinh/agent
H="$A/external/MyPCBench-main"
LOG="$A/results/stage3_probe.log"
mkdir -p "$A/results" "$A/out"

cd "$H"
set -a
# shellcheck disable=SC1091
source .env
# shellcheck disable=SC1091
source ./mypcbench-vm/env.sh
set +a

# Probe session: never spend API credits, never inject an UPDATE.
unset ANTHROPIC_API_KEY OPENAI_API_KEY
unset MYPCBENCH_CF_TASK MYPCBENCH_CF_SCRIPT MYPCBENCH_CF_OUT

export PATH="$H/.venv/bin:$PATH"
export PYTHONPATH="$H/agent-harness${PYTHONPATH:+:$PYTHONPATH}"
export MYPCBENCH_SKIP_QCOW2_REFRESH=1
export MYPCBENCH_VM_READY_TIMEOUT=3600
export MYPCBENCH_CF_PROBE_ONLY=1
export MYPCBENCH_VM_HOST=127.0.0.1

exec > >(tee -a "$LOG") 2>&1
echo "===== Stage 3 probe start $(date -Is) ====="
echo "python3=$(which python3)"
echo "MYPCBENCH_QCOW2=$MYPCBENCH_QCOW2"
echo "ANTHROPIC_API_KEY set? ${ANTHROPIC_API_KEY+yes}"
echo "OPENAI_API_KEY set? ${OPENAI_API_KEY+yes}"

python3 "$A/scripts/stage3_eligible_probe.py"
echo "===== Stage 3 probe done $(date -Is) ====="
