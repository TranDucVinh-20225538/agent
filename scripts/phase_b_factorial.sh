#!/usr/bin/env bash
# Phase B: remaining A×B cells for hard_app-f033.
# Condition B (description cleaned, times overlapping), then A+B (time shift + description cleaned).
# Does not rerun Baseline or A. Stops after A+B.
set -euo pipefail

A=/mnt/data2/Vinh/agent
H="$A/external/MyPCBench-main"
LOG="$A/results/phase_b_factorial.log"
mkdir -p "$A/results" "$H/results"

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

echo "===== phase B start $(date -Is) ====="
echo "python3=$(which python3)"
echo "model=claude-opus-4-6 max_steps=80 tasks_dir=tasks/cf_hard_app_f033"

run_agent() {
  local result_dir="$1"
  local probe_dir="$2"
  echo "----- agent $(date -Is) result_dir=$result_dir CF_TASK=${MYPCBENCH_CF_TASK:-unset} -----"
  mkdir -p "$result_dir" "$probe_dir"
  date -Is | tee "$result_dir/run_started.txt"
  python3 agent-harness/run_mypcbench.py --backend qemu \
    --qcow2_path "$MYPCBENCH_QCOW2" \
    --agent_type claude_cuabash --model claude-opus-4-6 \
    --tasks_dir tasks/cf_hard_app_f033 --max_steps 80 --timeout 7200 \
    --result_dir "$result_dir"
}

archive_cell() {
  local src="$1"
  local dest="$2"
  mkdir -p "$dest"
  rsync -a "$src/" "$dest/"
  echo "archived $src -> $dest"
}

# 1. Condition B: time overlap, description cleaned. No Patch A.
unset MYPCBENCH_CF_PROBE_ONLY
export MYPCBENCH_CF_TASK=hard_app-f033-B
export MYPCBENCH_CF_OUT="$A/results/hard_app-f033-B"
run_agent "$H/results/B-hard_app-f033" "$A/results/hard_app-f033-B"

export MYPCBENCH_JUDGE_FLAVOR=per_step
echo "----- judge B $(date -Is) -----"
python3 agent-harness/judge_results.py --result_dir "$H/results/B-hard_app-f033" || true
archive_cell "$H/results/B-hard_app-f033" "$A/results/hard_app-f033-B"
echo "===== condition B done $(date -Is) ====="

# 2. Condition A+B: Patch A time shift, then Patch B. Stop after this.
export MYPCBENCH_CF_TASK=hard_app-f033-AB
export MYPCBENCH_CF_OUT="$A/results/hard_app-f033-AB"
run_agent "$H/results/AB-hard_app-f033" "$A/results/hard_app-f033-AB"

echo "----- judge A+B $(date -Is) -----"
python3 agent-harness/judge_results.py --result_dir "$H/results/AB-hard_app-f033" || true
archive_cell "$H/results/AB-hard_app-f033" "$A/results/hard_app-f033-AB"
echo "===== condition A+B done $(date -Is) ====="

python3 "$A/scripts/write_hard_app_f033_factorial.py"

echo "===== phase B stop $(date -Is) ====="
echo "wrote $A/results/hard_app_f033_factorial.md"
for d in \
  "$H/results/B-hard_app-f033/scores.json" \
  "$H/results/AB-hard_app-f033/scores.json"
do
  echo "---- $d ----"
  if [ -f "$d" ]; then cat "$d"; else echo MISSING; fi
done
