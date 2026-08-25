#!/usr/bin/env bash
# Phase A: Claude agent + per_step Anthropic judge.
# retrieval-f001 already completed; this runs hard_app-f033 (base+cf)
# and situated_action-f028 (control, no SQL patch).
set -euo pipefail

A=/mnt/data2/Vinh/agent
H="$A/external/MyPCBench-main"
LOG="$A/results/phase_a_claude.log"
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

echo "===== phase A start $(date -Is) ====="
echo "python3=$(which python3)"

run_agent() {
  local result_dir="$1"
  local probe_dir="$2"
  local tasks_dir="$3"
  echo "----- agent $(date -Is) result_dir=$result_dir CF_TASK=${MYPCBENCH_CF_TASK:-unset} PROBE_ONLY=${MYPCBENCH_CF_PROBE_ONLY:-unset} -----"
  mkdir -p "$result_dir" "$probe_dir"
  date -Is | tee "$result_dir/run_started.txt"
  python3 agent-harness/run_mypcbench.py --backend qemu \
    --qcow2_path "$MYPCBENCH_QCOW2" \
    --agent_type claude_cuabash --model claude-opus-4-6 \
    --tasks_dir "$tasks_dir" --max_steps 80 --timeout 7200 \
    --result_dir "$result_dir"
}

# 1. hard_app-f033 baseline (probe only)
export MYPCBENCH_CF_TASK=hard_app-f033
export MYPCBENCH_CF_PROBE_ONLY=1
export MYPCBENCH_CF_OUT="$A/results/base-hard_app-f033"
run_agent "$H/results/base-hard_app-f033" "$A/results/base-hard_app-f033" tasks/cf_hard_app_f033

# 2. hard_app-f033 counterfactual (UPDATE)
unset MYPCBENCH_CF_PROBE_ONLY
export MYPCBENCH_CF_TASK=hard_app-f033
export MYPCBENCH_CF_OUT="$A/results/cf-hard_app-f033"
run_agent "$H/results/cf-hard_app-f033" "$A/results/cf-hard_app-f033" tasks/cf_hard_app_f033

# 3. situated_action-f028 control — no intervention
unset MYPCBENCH_CF_TASK MYPCBENCH_CF_PROBE_ONLY MYPCBENCH_CF_OUT
run_agent "$H/results/control-situated_action-f028" "$A/results/control-situated_action-f028" tasks/cf_situated_action_f028

# Judge (Anthropic per_step fallback; not paper Gemini)
export MYPCBENCH_JUDGE_FLAVOR=per_step
for d in \
  "$H/results/base-hard_app-f033" \
  "$H/results/cf-hard_app-f033" \
  "$H/results/control-situated_action-f028"
do
  echo "----- judge $(date -Is) $d -----"
  python3 agent-harness/judge_results.py --result_dir "$d" || true
done

echo "===== phase A done $(date -Is) ====="
for d in \
  "$H/results/base-retrieval-f001/scores.json" \
  "$H/results/cf-retrieval-f001/scores.json" \
  "$H/results/base-hard_app-f033/scores.json" \
  "$H/results/cf-hard_app-f033/scores.json" \
  "$H/results/control-situated_action-f028/scores.json"
do
  echo "---- $d ----"
  if [ -f "$d" ]; then cat "$d"; else echo MISSING; fi
done
