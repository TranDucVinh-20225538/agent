#!/usr/bin/env bash
# Retry ONLY OpenAI preference_inference-f018 (baseline + CF).
# Attempt 1 ended with empty actions / no DONE; keep those dirs as attempt1.
# Does not touch Claude results/stage4-preference_inference-f018/.
set -euo pipefail

A=/mnt/data2/Vinh/agent
H="$A/external/MyPCBench-main"
LOG="$A/results/stage4_openai_f018_retry.log"
TASKS="$H/tasks/cf_openai_f018_retry"
FINAL="$H/tasks/final/multi_app/multi_app.rubrics.json"
mkdir -p "$A/results" "$H/results" "$TASKS" "$A/out"

cd "$H"
set -a
# shellcheck disable=SC1091
source .env
# shellcheck disable=SC1091
source ./mypcbench-vm/env.sh
set +a

unset OPENAI_BASE_URL
if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "FAIL: OPENAI_API_KEY empty." >&2
  exit 1
fi

AGENT_TYPE="${MYPCBENCH_OPENAI_AGENT:-openai_cuabash}"
AGENT_MODEL="${MYPCBENCH_OPENAI_MODEL:-gpt-5.5}"
export PATH="$H/.venv/bin:$PATH"
export MYPCBENCH_SKIP_QCOW2_REFRESH=1
export MYPCBENCH_VM_READY_TIMEOUT=3600
export MYPCBENCH_CF_SCRIPT="$A/scripts/cf_inject.py"
export MYPCBENCH_VM_HOST=127.0.0.1
export MYPCBENCH_AGENT_ROOT="$A"
export STAGE4_TAG=openai

# Stay off default :5000 in case another Stage 4 QEMU starts.
export MYPCBENCH_HOST_API_PORT=15000
export MYPCBENCH_HOST_VNC_PORT=5902
export MYPCBENCH_HOST_SSH_PORT=12222
for p in $(seq 3001 3018); do
  export "MYPCBENCH_HOST_APP_PORT_${p}=$((p + 20000))"
done

exec > >(tee -a "$LOG") 2>&1
echo "===== OpenAI f018 retry start $(date -Is) ====="
echo "python3=$(which python3) agent=$AGENT_TYPE model=$AGENT_MODEL"
echo "OPENAI_API_KEY set? yes OPENAI_BASE_URL=${OPENAI_BASE_URL:-unset}"
echo "API=http://127.0.0.1:${MYPCBENCH_HOST_API_PORT}"

python3 - "$FINAL" preference_inference-f018 "$TASKS/one.json" <<'PY'
import json, sys
src, task_id, dest = sys.argv[1:]
data = json.loads(open(src).read())
items = data if isinstance(data, list) else data.get("tasks") or []
hit = [t for t in items if isinstance(t, dict) and t.get("id") == task_id]
if not hit:
    raise SystemExit(f"no pinned rubric for {task_id} in {src}")
open(dest, "w").write(json.dumps(hit, indent=2) + "\n")
print(f"pinned {task_id} <- {src}")
PY

run_cell() {
  local which="$1"
  local harness="$H/results/stage4-openai-preference_inference-f018/${which}-retry2"
  local dest="$A/results/stage4-openai-preference_inference-f018/${which}"
  mkdir -p "$harness"
  date -Is | tee "$harness/run_started.txt"
  echo "----- agent $(date -Is) $which result_dir=$harness CF_TASK=$MYPCBENCH_CF_TASK PROBE_ONLY=${MYPCBENCH_CF_PROBE_ONLY:-unset} -----"
  set +e
  python3 agent-harness/run_mypcbench.py --backend qemu \
    --qcow2_path "$MYPCBENCH_QCOW2" \
    --container_name "mypcbench-openai-f018-${which}-r2" \
    --agent_type "$AGENT_TYPE" --model "$AGENT_MODEL" \
    --tasks_dir tasks/cf_openai_f018_retry --max_steps 80 --timeout 7200 \
    --result_dir "$harness"
  echo "agent_exit=$? $which"
  set -e
  export MYPCBENCH_JUDGE_FLAVOR=per_step
  echo "----- judge $(date -Is) $harness -----"
  python3 agent-harness/judge_results.py --result_dir "$harness" || true
  if [ ! -f "$harness/preference_inference-f018/traj.jsonl" ]; then
    echo "RETRY $which produced no traj; leaving attempt-1 in $dest"
    return 0
  fi
  mkdir -p "$dest"
  rsync -a "$harness/" "$dest/"
  echo "archived $harness -> $dest"
}

# Baseline: probe only
unset MYPCBENCH_CF_PROBE_ONLY
export MYPCBENCH_CF_TASK=preference_inference-f018
export MYPCBENCH_CF_PROBE_ONLY=1
export MYPCBENCH_CF_OUT="$A/results/stage4-openai-preference_inference-f018/base-retry2-inject"
run_cell base

# CF: locked joint patch (status=settled)
unset MYPCBENCH_CF_PROBE_ONLY
export MYPCBENCH_CF_TASK=preference_inference-f018
export MYPCBENCH_CF_OUT="$A/results/stage4-openai-preference_inference-f018/cf-retry2-inject"
run_cell cf

python3 "$A/scripts/write_stage4_results.py"
echo "===== OpenAI f018 retry stop $(date -Is) ====="
echo "wrote $A/out/evidence_stage4_openai_results.md"
echo "STOP: only f018 retried; Claude dirs untouched"
