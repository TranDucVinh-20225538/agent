#!/usr/bin/env bash
# Slot 5 only: situated_action-f009, modal Chili's item vs most-recent basket.
# Dummy-probe first. Stops if the modal cannot be flipped onto another observed item.
# Does not start A+B automatically. Does not start any other task.
set -euo pipefail

A=/mnt/data2/Vinh/agent
H="$A/external/MyPCBench-main"
LOG="$A/results/phase_d_sa009.log"
TASKS="$H/tasks/cf_situated_action_f009"
mkdir -p "$A/results" "$H/results" "$TASKS"

cp "$A/cf/tasks/situated_action-f009.json" "$TASKS/one.json"

cd "$H"
set -a
source .env
source ./mypcbench-vm/env.sh
set +a
export PATH="$H/.venv/bin:$PATH"
export MYPCBENCH_SKIP_QCOW2_REFRESH=1
export MYPCBENCH_VM_READY_TIMEOUT=3600
export MYPCBENCH_CF_SCRIPT="$A/scripts/cf_inject.py"

exec > >(tee -a "$LOG") 2>&1

echo "===== phase D slot 5 start $(date -Is) ====="

run_agent() {
  local result_dir="$1"
  local probe_dir="$2"
  echo "----- agent $(date -Is) result_dir=$result_dir CF_TASK=${MYPCBENCH_CF_TASK:-unset} PROBE_ONLY=${MYPCBENCH_CF_PROBE_ONLY:-unset} -----"
  mkdir -p "$result_dir" "$probe_dir"
  date -Is | tee "$result_dir/run_started.txt"
  python3 agent-harness/run_mypcbench.py --backend qemu \
    --qcow2_path "$MYPCBENCH_QCOW2" \
    --agent_type "${AGENT_TYPE:-claude_cuabash}" --model "${AGENT_MODEL:-claude-opus-4-6}" \
    --tasks_dir tasks/cf_situated_action_f009 --max_steps 80 --timeout 7200 \
    --result_dir "$result_dir"
}

archive_cell() {
  local src="$1"
  local dest="$2"
  mkdir -p "$dest"
  rsync -a "$src/" "$dest/"
  echo "archived $src -> $dest"
}

export AGENT_TYPE=dummy
export AGENT_MODEL=dummy
export MYPCBENCH_CF_TASK=situated_action-f009
export MYPCBENCH_CF_PROBE_ONLY=1
export MYPCBENCH_CF_OUT="$A/results/sa009-probe"
run_agent "$H/results/probe-situated_action-f009" "$A/results/sa009-probe"

PROBE_JSON=$(ls "$A/results/sa009-probe"/*.guest.json 2>/dev/null | head -1 || true)
if [ -z "${PROBE_JSON}" ]; then
  echo "FAILED: no guest probe json after dummy dump"
  exit 1
fi

set +e
python3 "$A/scripts/sa009_gate.py" "$PROBE_JSON" "$A/results/sa009_probe.sql.txt"
GATE=$?
set -e
if [ "$GATE" -eq 2 ]; then
  echo "===== STOP: modal cannot be flipped on this seed. No Opus. ====="
  echo "Minimal determining set: { unresolved: Chili's history has no second observed item }"
  exit 0
fi

unset AGENT_TYPE AGENT_MODEL
unset MYPCBENCH_CF_PROBE_ONLY

export MYPCBENCH_CF_TASK=situated_action-f009
export MYPCBENCH_CF_PROBE_ONLY=1
export MYPCBENCH_CF_OUT="$A/results/sa009-0"
run_agent "$H/results/base-situated_action-f009" "$A/results/sa009-0"
unset MYPCBENCH_CF_PROBE_ONLY
archive_cell "$H/results/base-situated_action-f009" "$A/results/sa009-0"

export MYPCBENCH_CF_TASK=situated_action-f009-A
export MYPCBENCH_CF_OUT="$A/results/sa009-A"
run_agent "$H/results/A-situated_action-f009" "$A/results/sa009-A"
archive_cell "$H/results/A-situated_action-f009" "$A/results/sa009-A"

export MYPCBENCH_CF_TASK=situated_action-f009-B
export MYPCBENCH_CF_OUT="$A/results/sa009-B"
set +e
run_agent "$H/results/B-situated_action-f009" "$A/results/sa009-B"
B_STATUS=$?
set -e
if [ "$B_STATUS" -ne 0 ]; then
  echo "Condition B refused or failed (likely recency flip would move the modal). Continuing without B."
else
  archive_cell "$H/results/B-situated_action-f009" "$A/results/sa009-B"
fi

export MYPCBENCH_JUDGE_FLAVOR=per_step
for d in \
  "$H/results/base-situated_action-f009" \
  "$H/results/A-situated_action-f009" \
  "$H/results/B-situated_action-f009"
do
  if [ -d "$d" ]; then
    echo "----- judge $(date -Is) $d -----"
    python3 agent-harness/judge_results.py --result_dir "$d" || true
  fi
done

archive_cell "$H/results/base-situated_action-f009" "$A/results/sa009-0"
archive_cell "$H/results/A-situated_action-f009" "$A/results/sa009-A"
[ -d "$H/results/B-situated_action-f009" ] && archive_cell "$H/results/B-situated_action-f009" "$A/results/sa009-B"

python3 "$A/scripts/write_sa009_basis.py"

echo "===== phase D slot 5 stop $(date -Is) ====="
echo "Then write exactly one line: Minimal determining set: { ... }"
echo "Commit and push to phase-a-results. Do not start another task."
echo "DV is the item in the trajectory, not checkout and not the judge score."
