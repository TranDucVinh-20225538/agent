#!/usr/bin/env bash
# Stage 4 Qwen3.5-35B-A3B via OpenRouter + qwen_cuabash on node30 QEMU.
# Distinct from HPC 27B (stage4-qwen35-*) and from Claude/OpenAI dirs.
# Default: f001 only after a vision+XML gate. Text "OK" is not that gate.
set -euo pipefail

A="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
H="$A/external/MyPCBench-main"
LOG="$A/results/stage4_${STAGE4_TAG:-qwen35a3b}_run.log"
FINAL="$H/tasks/final"
ONE_DIR="$H/tasks/cf_one"
mkdir -p "$A/results" "$H/results" "$ONE_DIR" "$A/out"

# Parent/CLI wins over .env. Otherwise MYPCBENCH_QWEN_MODEL=qwen/qwen3.5-35b-a3b
# in .env clobbers 9B / Flash lanes into the wrong model under the right TAG.
_SAVE_QWEN_MODEL="${MYPCBENCH_QWEN_MODEL:-}"
_SAVE_STAGE4_TAG="${STAGE4_TAG:-}"
_SAVE_STAGE4_QWEN_TASKS="${STAGE4_QWEN_TASKS:-}"
_SAVE_STAGE4_WRITE_TASKS="${STAGE4_WRITE_TASKS:-}"
_SAVE_STAGE4_REQUIRE_F001_DONE="${STAGE4_REQUIRE_F001_DONE:-}"
_SAVE_QWEN_AGENT="${MYPCBENCH_QWEN_AGENT:-}"

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
[ -n "$_SAVE_QWEN_MODEL" ] && export MYPCBENCH_QWEN_MODEL="$_SAVE_QWEN_MODEL"
[ -n "$_SAVE_STAGE4_TAG" ] && export STAGE4_TAG="$_SAVE_STAGE4_TAG"
[ -n "$_SAVE_STAGE4_QWEN_TASKS" ] && export STAGE4_QWEN_TASKS="$_SAVE_STAGE4_QWEN_TASKS"
[ -n "$_SAVE_STAGE4_WRITE_TASKS" ] && export STAGE4_WRITE_TASKS="$_SAVE_STAGE4_WRITE_TASKS"
[ -n "$_SAVE_STAGE4_REQUIRE_F001_DONE" ] && export STAGE4_REQUIRE_F001_DONE="$_SAVE_STAGE4_REQUIRE_F001_DONE"
[ -n "$_SAVE_QWEN_AGENT" ] && export MYPCBENCH_QWEN_AGENT="$_SAVE_QWEN_AGENT"

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
export PYTHONUNBUFFERED=1
export MYPCBENCH_SKIP_QCOW2_REFRESH=1
export MYPCBENCH_VM_READY_TIMEOUT=3600
export MYPCBENCH_CF_SCRIPT="$A/scripts/cf_inject.py"
export MYPCBENCH_VM_HOST=127.0.0.1
export MYPCBENCH_AGENT_ROOT="$A"
export STAGE4_TAG="${STAGE4_TAG:-qwen35a3b}"
STAGE4_QWEN_TASKS="${STAGE4_QWEN_TASKS:-f001}"
PREFIX="stage4-${STAGE4_TAG}-"
LOG="$A/results/stage4_${STAGE4_TAG}_run.log"

# Tag/model must match. .env default is 35B-A3B; do not silently swap.
case "$STAGE4_TAG" in
  qwen359b)
    if [[ "$AGENT_MODEL" != *qwen3.5-9b* ]]; then
      echo "FAIL: TAG=qwen359b but model=$AGENT_MODEL" >&2
      exit 2
    fi
    ;;
  qwen38flash)
    if [[ "$AGENT_MODEL" != *qwen3.8-flash* ]]; then
      echo "FAIL: TAG=qwen38flash but model=$AGENT_MODEL" >&2
      exit 2
    fi
    ;;
  qwen35a3b)
    if [[ "$AGENT_MODEL" != *qwen3.5-35b-a3b* ]]; then
      echo "FAIL: TAG=qwen35a3b but model=$AGENT_MODEL" >&2
      exit 2
    fi
    ;;
esac

f001_base_done=0
_f001_traj=$(find "$H/results/${PREFIX}retrieval-f001/base" -name 'traj.jsonl' -size +0c -print -quit 2>/dev/null || true)
if [ -n "${_f001_traj:-}" ] && grep -Eq '"action": "DONE"|"done": true' "$_f001_traj"; then
  f001_base_done=1
fi
if [ "${STAGE4_SKIP_VISION_GATE:-0}" = "1" ] || [ "$f001_base_done" = "1" ]; then
  echo "skip vision gate (STAGE4_SKIP_VISION_GATE=${STAGE4_SKIP_VISION_GATE:-0} f001_base_done=$f001_base_done model=$AGENT_MODEL)"
else
  python3 "$A/scripts/qwen_vision_gate.py"
fi

exec > >(tee -a "$LOG") 2>&1
echo "===== Stage 4 OpenRouter start $(date -Is) ====="
echo "python3=$(which python3) agent=$AGENT_TYPE model=$AGENT_MODEL"
echo "OPENAI_BASE_URL=$OPENAI_BASE_URL"
echo "OPENAI_API_KEY=sk-proj? no (OpenRouter process override)"
echo "STAGE4_TAG=$STAGE4_TAG STAGE4_QWEN_TASKS=$STAGE4_QWEN_TASKS"
echo "dirs ${PREFIX}* ; NOT Claude/OpenAI/HPC-27B overwrite; 35B-A3B only if TAG=qwen35a3b"

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
  cell_has_done "$H/results/${PREFIX}${task_id}/base" \
    && cell_has_done "$H/results/${PREFIX}${task_id}/cf"
}

stash_incomplete() {
  local dir="$1"
  local stamp="$2"
  if [ -d "$dir" ] && cell_has_step "$dir" && ! cell_has_done "$dir"; then
    local bak="${dir}-incomplete-${stamp}"
    echo "incomplete $dir -> $bak"
    mv "$dir" "$bak"
  fi
}

run_pair() {
  local task_id="$1"
  local src="$2"
  pin_task "$task_id" "$src"

  local base_h="$H/results/${PREFIX}${task_id}/base"
  local cf_h="$H/results/${PREFIX}${task_id}/cf"
  local base_a="$A/results/${PREFIX}${task_id}/base"
  local cf_a="$A/results/${PREFIX}${task_id}/cf"
  local stamp
  stamp="$(date +%Y%m%dT%H%M%S)"

  if cell_has_done "$base_h"; then
    echo "skip $task_id base (already DONE)"
  else
    stash_incomplete "$base_h" "$stamp"
    stash_incomplete "$base_a" "$stamp"
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
  fi

  if cell_has_done "$cf_h"; then
    echo "skip $task_id cf (already DONE)"
  else
    stash_incomplete "$cf_h" "$stamp"
    stash_incomplete "$cf_a" "$stamp"
    # Agent copy may only have sql-patch/guest.json (no traj yet).
    if [ -d "$cf_a" ] && ! cell_has_done "$cf_a"; then
      echo "incomplete $cf_a -> ${cf_a}-incomplete-${stamp}"
      mv "$cf_a" "${cf_a}-incomplete-${stamp}"
    fi
    unset MYPCBENCH_CF_PROBE_ONLY
    export MYPCBENCH_CF_TASK="$task_id"
    export MYPCBENCH_CF_OUT="$cf_a"
    run_agent "$cf_h"
    judge_dir "$cf_h"
    archive_cell "$cf_h" "$cf_a"
  fi
}

run_pair retrieval-f001 "$FINAL/dinoco_airlines/dinoco_airlines.rubrics.json"
if ! pair_complete retrieval-f001; then
  echo "STOP: f001 pair not complete (need DONE on base and CF)."
  if [ "${STAGE4_REQUIRE_F001_DONE:-1}" = "1" ]; then
    echo "Not a DV for later tasks."
    exit 1
  fi
  echo "STAGE4_REQUIRE_F001_DONE=0 — still running later tasks once."
fi
echo "f001 pair checked."

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
echo "===== Stage 4 ${STAGE4_TAG} OpenRouter stop $(date -Is) ====="
echo "wrote $A/out/evidence_stage4_${STAGE4_TAG}_results.md"
echo "STOP: Claude/OpenAI/HPC-27B/other-tag dirs untouched"
