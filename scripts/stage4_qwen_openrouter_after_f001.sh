#!/usr/bin/env bash
# Overnight continuation: after f001 pair DONE, run f003 → f018 → f004.
# Does not re-run f001. Dirs stage4-qwen35a3b-* only.
set -euo pipefail

A="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
H="$A/external/MyPCBench-main"
LOG="$A/results/stage4_qwen35a3b_run.log"
FINAL="$H/tasks/final"
ONE_DIR="$H/tasks/cf_one"
WAIT_PID="${WRAPPER_PID:-}"

cell_has_done() {
  local dir="$1"
  local f
  f=$(find "$dir" -name 'traj.jsonl' -size +0c -print -quit 2>/dev/null || true)
  [ -n "$f" ] && grep -Eq '"action": "DONE"|"done": true' "$f"
}

pair_complete() {
  local task_id="$1"
  cell_has_done "$H/results/stage4-qwen35a3b-${task_id}/base" \
    && cell_has_done "$H/results/stage4-qwen35a3b-${task_id}/cf"
}

if [ -n "$WAIT_PID" ]; then
  echo "===== overnight waiter start $(date -Is) pid=$WAIT_PID =====" | tee -a "$LOG"
  while kill -0 "$WAIT_PID" 2>/dev/null; do
    sleep 20
  done
  echo "===== wrapper $WAIT_PID exited $(date -Is) =====" | tee -a "$LOG"
  sleep 5
fi

if ! pair_complete retrieval-f001; then
  echo "STOP: f001 pair not DONE on base+CF. Not starting f003." | tee -a "$LOG"
  exit 1
fi
echo "f001 pair complete. Continuing f003 → f018 → f004." | tee -a "$LOG"

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

if [ -z "${MYPCBENCH_QCOW2:-}" ]; then
  echo "FAIL: MYPCBENCH_QCOW2 unset" >&2
  exit 1
fi
if [ -z "${OPENROUTER_API_KEY:-}" ]; then
  echo "FAIL: OPENROUTER_API_KEY unset" >&2
  exit 1
fi
if [[ "${OPENROUTER_API_KEY}" == sk-proj-* ]]; then
  echo "FAIL: OPENROUTER_API_KEY looks like the GPT key" >&2
  exit 1
fi

export OPENAI_BASE_URL="${OPENAI_BASE_URL:-https://openrouter.ai/api/v1}"
export OPENAI_API_KEY="$OPENROUTER_API_KEY"
AGENT_TYPE="${MYPCBENCH_QWEN_AGENT:-qwen_cuabash}"
AGENT_MODEL="${MYPCBENCH_QWEN_MODEL:-qwen/qwen3.5-35b-a3b}"
export MYPCBENCH_QWEN_MODEL="$AGENT_MODEL"
export PATH="$H/.venv/bin:$PATH"
export MYPCBENCH_SKIP_QCOW2_REFRESH=1
export MYPCBENCH_VM_READY_TIMEOUT=3600
export MYPCBENCH_CF_SCRIPT="$A/scripts/cf_inject.py"
export MYPCBENCH_VM_HOST=127.0.0.1
export MYPCBENCH_AGENT_ROOT="$A"
export STAGE4_TAG=qwen35a3b

exec > >(tee -a "$LOG") 2>&1
echo "===== Stage 4 Qwen3.5-35B-A3B rest start $(date -Is) ====="
echo "python3=$(which python3) agent=$AGENT_TYPE model=$AGENT_MODEL"
echo "OPENAI_BASE_URL=$OPENAI_BASE_URL"
echo "OPENAI_API_KEY=sk-proj? no (OpenRouter process override)"
echo "order: f003 → f018 → f004 (skip f001)"
echo "dirs stage4-qwen35a3b-* ; NOT HPC 27B ; NOT Claude/OpenAI"

pin_task() {
  local task_id="$1"
  local src="$2"
  python3 - "$src" "$task_id" "$ONE_DIR/one.json" <<'PY'
import json, sys
src, task_id, dest = sys.argv[1:]
data = json.loads(open(src).read())
items = data if isinstance(data, list) else data.get("tasks") or []
hit = [t for t in items if isinstance(t, dict) and t.get("id") == task_id]
if not hit:
    raise SystemExit(f"no pinned rubric for {task_id} in {src}")
open(dest, "w").write(json.dumps(hit, indent=2) + "\n")
print(f"pinned {task_id} <- {src} ({len(hit)} object)")
PY
}

run_agent() {
  local result_dir="$1"
  echo "----- agent $(date -Is) result_dir=$result_dir CF_TASK=${MYPCBENCH_CF_TASK:-unset} PROBE_ONLY=${MYPCBENCH_CF_PROBE_ONLY:-unset} -----"
  mkdir -p "$result_dir"
  date -Is | tee "$result_dir/run_started.txt"
  set +e
  python3 agent-harness/run_mypcbench.py --backend qemu \
    --qcow2_path "$MYPCBENCH_QCOW2" \
    --agent_type "$AGENT_TYPE" --model "$AGENT_MODEL" \
    --tasks_dir tasks/cf_one --max_steps 80 --timeout 7200 \
    --result_dir "$result_dir"
  local rc=$?
  set -e
  echo "agent_exit=$rc result_dir=$result_dir"
  return 0
}

judge_dir() {
  local result_dir="$1"
  export MYPCBENCH_JUDGE_FLAVOR=per_step
  echo "----- judge $(date -Is) $result_dir -----"
  python3 agent-harness/judge_results.py --result_dir "$result_dir" || true
}

archive_cell() {
  local src="$1"
  local dest="$2"
  mkdir -p "$dest"
  rsync -a "$src/" "$dest/"
  echo "archived $src -> $dest"
}

cell_has_step() {
  local dir="$1"
  local f
  f=$(find "$dir" -name 'traj.jsonl' -size +0c -print -quit 2>/dev/null || true)
  [ -n "$f" ] && grep -q '"step_num"' "$f"
}

run_pair() {
  local task_id="$1"
  local src="$2"
  pin_task "$task_id" "$src"

  local base_h="$H/results/stage4-qwen35a3b-${task_id}/base"
  local cf_h="$H/results/stage4-qwen35a3b-${task_id}/cf"
  local base_a="$A/results/stage4-qwen35a3b-${task_id}/base"
  local cf_a="$A/results/stage4-qwen35a3b-${task_id}/cf"

  unset MYPCBENCH_CF_PROBE_ONLY
  export MYPCBENCH_CF_TASK="$task_id"
  export MYPCBENCH_CF_PROBE_ONLY=1
  export MYPCBENCH_CF_OUT="$base_a"
  run_agent "$base_h"
  if ! cell_has_step "$base_h"; then
    echo "FAIL: $task_id base has no traj step. Skip CF. Continue next task."
    return 0
  fi
  judge_dir "$base_h"
  archive_cell "$base_h" "$base_a"

  unset MYPCBENCH_CF_PROBE_ONLY
  export MYPCBENCH_CF_TASK="$task_id"
  export MYPCBENCH_CF_OUT="$cf_a"
  run_agent "$cf_h"
  judge_dir "$cf_h"
  archive_cell "$cf_h" "$cf_a"
}

run_pair aggregation-f003 "$FINAL/speedtax/speedtax.rubrics.json"
run_pair preference_inference-f018 "$FINAL/multi_app/multi_app.rubrics.json"
run_pair counterfactual-f004 "$FINAL/multi_app/multi_app.rubrics.json"

python3 "$A/scripts/write_stage4_results.py"
echo "===== Stage 4 Qwen3.5-35B-A3B rest stop $(date -Is) ====="
echo "wrote $A/out/evidence_stage4_qwen35a3b_results.md"
echo "STOP: Claude/OpenAI/HPC-27B dirs untouched"
