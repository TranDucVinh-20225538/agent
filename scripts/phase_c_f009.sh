#!/usr/bin/env bash
# Phase C, slot 4 only: preference_inference-f009 count vs spend.
# Stops if the two winners coincide. Does not start any other task.
# A+B is not launched automatically.
set -euo pipefail

A=/mnt/data2/Vinh/agent
H="$A/external/MyPCBench-main"
LOG="$A/results/phase_c_f009.log"
TASKS="$H/tasks/cf_preference_f009"
mkdir -p "$A/results" "$H/results" "$TASKS"

cp "$A/cf/tasks/preference_inference-f009.json" "$TASKS/one.json"

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

echo "===== phase C slot 4 start $(date -Is) ====="

run_agent() {
  local result_dir="$1"
  local probe_dir="$2"
  echo "----- agent $(date -Is) result_dir=$result_dir CF_TASK=${MYPCBENCH_CF_TASK:-unset} PROBE_ONLY=${MYPCBENCH_CF_PROBE_ONLY:-unset} -----"
  mkdir -p "$result_dir" "$probe_dir"
  date -Is | tee "$result_dir/run_started.txt"
  python3 agent-harness/run_mypcbench.py --backend qemu \
    --qcow2_path "$MYPCBENCH_QCOW2" \
    --agent_type "${AGENT_TYPE:-claude_cuabash}" --model "${AGENT_MODEL:-claude-opus-4-6}" \
    --tasks_dir tasks/cf_preference_f009 --max_steps 80 --timeout 7200 \
    --result_dir "$result_dir"
}

archive_cell() {
  local src="$1"
  local dest="$2"
  mkdir -p "$dest"
  rsync -a "$src/" "$dest/"
  echo "archived $src -> $dest"
}

# 0. Cheap ranking dump. Dummy agent, probe only. No Opus.
export AGENT_TYPE=dummy
export AGENT_MODEL=dummy
export MYPCBENCH_CF_TASK=preference_inference-f009
export MYPCBENCH_CF_PROBE_ONLY=1
export MYPCBENCH_CF_OUT="$A/results/pref-f009-probe"
run_agent "$H/results/probe-preference_inference-f009" "$A/results/pref-f009-probe"

PROBE_JSON=$(ls "$A/results/pref-f009-probe"/*.guest.json 2>/dev/null | head -1 || true)
if [ -z "${PROBE_JSON}" ]; then
  PROBE_JSON=$(ls "$H/results/probe-preference_inference-f009"/*.guest.json 2>/dev/null | head -1 || true)
fi
if [ -z "${PROBE_JSON}" ]; then
  echo "FAILED: no guest probe json after dummy dump"
  exit 1
fi

set +e
python3 "$A/scripts/f009_gate.py" "$PROBE_JSON" "$A/results/preference_f009_probe.sql.txt"
GATE=$?
set -e
if [ "$GATE" -eq 2 ]; then
  echo "===== STOP: count winner == spend winner. No Opus. ====="
  echo "Minimal determining set: { unresolved: count and spend name the same store }"
  exit 0
fi

unset AGENT_TYPE AGENT_MODEL
unset MYPCBENCH_CF_PROBE_ONLY

# Condition 0
export MYPCBENCH_CF_TASK=preference_inference-f009
export MYPCBENCH_CF_PROBE_ONLY=1
export MYPCBENCH_CF_OUT="$A/results/pref-f009-0"
run_agent "$H/results/base-preference_inference-f009" "$A/results/pref-f009-0"
unset MYPCBENCH_CF_PROBE_ONLY
archive_cell "$H/results/base-preference_inference-f009" "$A/results/pref-f009-0"

# Condition A: count winner changes, spend winner held
export MYPCBENCH_CF_TASK=preference_inference-f009-A
export MYPCBENCH_CF_OUT="$A/results/pref-f009-A"
run_agent "$H/results/A-preference_inference-f009" "$A/results/pref-f009-A"
archive_cell "$H/results/A-preference_inference-f009" "$A/results/pref-f009-A"

# Condition B: spend winner changes, count winner held
export MYPCBENCH_CF_TASK=preference_inference-f009-B
export MYPCBENCH_CF_OUT="$A/results/pref-f009-B"
run_agent "$H/results/B-preference_inference-f009" "$A/results/pref-f009-B"
archive_cell "$H/results/B-preference_inference-f009" "$A/results/pref-f009-B"

export MYPCBENCH_JUDGE_FLAVOR=per_step
for d in \
  "$H/results/base-preference_inference-f009" \
  "$H/results/A-preference_inference-f009" \
  "$H/results/B-preference_inference-f009"
do
  echo "----- judge $(date -Is) $d -----"
  python3 agent-harness/judge_results.py --result_dir "$d" || true
done

archive_cell "$H/results/base-preference_inference-f009" "$A/results/pref-f009-0"
archive_cell "$H/results/A-preference_inference-f009" "$A/results/pref-f009-A"
archive_cell "$H/results/B-preference_inference-f009" "$A/results/pref-f009-B"

python3 "$A/scripts/write_preference_f009_basis.py"

echo "A+B was not launched. Launch only if A and B answers do not tell the bases apart:"
echo "  MYPCBENCH_CF_TASK=preference_inference-f009-AB ... result_dir=results/AB-preference_inference-f009"

echo "===== phase C slot 4 stop $(date -Is) ====="
echo "Then write exactly one line: Minimal determining set: { ... }"
echo "Commit and push to phase-a-results. Do not start another task."
