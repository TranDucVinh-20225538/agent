#!/usr/bin/env bash
# Stage 4 Qwen3.5-35B-A3B via OpenRouter + qwen_cuabash on node30 QEMU.
# Distinct from HPC 27B (stage4-qwen35-*) and from Claude/OpenAI dirs.
# Default: f001 only after a vision+XML gate. Text "OK" is not that gate.
set -euo pipefail

A="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
H="$A/external/MyPCBench-main"
LOG="$A/results/stage4_qwen35a3b_run.log"
FINAL="$H/tasks/final"
ONE_DIR="$H/tasks/cf_one"
mkdir -p "$A/results" "$H/results" "$ONE_DIR" "$A/out"

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

# After .env (GPT sk-proj). OpenRouter key is process-only; never write it to .env.
if [ -z "${OPENROUTER_API_KEY:-}" ]; then
  echo "FAIL: OPENROUTER_API_KEY unset. Export it in this process; do not put it in .env." >&2
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
STAGE4_QWEN_TASKS="${STAGE4_QWEN_TASKS:-f001}"

python3 "$A/scripts/qwen_vision_gate.py"

exec > >(tee -a "$LOG") 2>&1
echo "===== Stage 4 Qwen3.5-35B-A3B OpenRouter start $(date -Is) ====="
echo "python3=$(which python3) agent=$AGENT_TYPE model=$AGENT_MODEL"
echo "OPENAI_BASE_URL=$OPENAI_BASE_URL"
echo "OPENAI_API_KEY=sk-proj? no (OpenRouter process override)"
echo "STAGE4_QWEN_TASKS=$STAGE4_QWEN_TASKS"
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
    echo "FAIL: $task_id base has no traj step. Not a Stage 4 cell." >&2
    exit 1
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

run_pair retrieval-f001 "$FINAL/dinoco_airlines/dinoco_airlines.rubrics.json"
if ! pair_complete retrieval-f001; then
  echo "STOP: f001 pair not complete (need DONE on base and CF). Not a DV for later tasks."
  exit 1
fi
echo "f001 pair complete."

case ",$STAGE4_QWEN_TASKS," in
  *,f003,*|*,all,*)
    run_pair aggregation-f003 "$FINAL/speedtax/speedtax.rubrics.json"
    ;;
  *)
    echo "STOP after f001. Later: STAGE4_QWEN_TASKS=f001,f003"
    echo "Do not write a four-row table from f001 alone."
    echo "===== Stage 4 Qwen3.5-35B-A3B OpenRouter stop $(date -Is) ====="
    exit 0
    ;;
esac

case ",$STAGE4_QWEN_TASKS," in
  *,f018,*|*,all,*)
    run_pair preference_inference-f018 "$FINAL/multi_app/multi_app.rubrics.json"
    ;;
esac
case ",$STAGE4_QWEN_TASKS," in
  *,f004,*|*,all,*)
    run_pair counterfactual-f004 "$FINAL/multi_app/multi_app.rubrics.json"
    ;;
esac

python3 "$A/scripts/write_stage4_results.py"
echo "===== Stage 4 Qwen3.5-35B-A3B OpenRouter stop $(date -Is) ====="
echo "wrote $A/out/evidence_stage4_qwen35a3b_results.md"
echo "STOP: Claude/OpenAI/HPC-27B dirs untouched"
