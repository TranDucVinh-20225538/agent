#!/usr/bin/env bash
# Phase B.2: six unrun tasks. Default order is Qwen 35B → GPT → 9B → Flash.
# Claude is last (not billed yet). Reuses Stage 4 dirs for the four already-run IDs.
# Does not overwrite those dirs. Does not rewrite I.
set -euo pipefail

A="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
H="$A/external/MyPCBench-main"
FINAL="$H/tasks/final"
ONE_DIR="$H/tasks/cf_one"
LANE="${PHASEB_LANE:-}"

usage() {
  echo "usage: PHASEB_LANE=qwen35a3b|openai|qwen359b|qwen38flash|claude bash scripts/phase_b_run.sh" >&2
  exit 2
}

case "$LANE" in
  claude|openai|qwen35a3b|qwen359b|qwen38flash) ;;
  *) usage ;;
esac

_SAVE_QWEN_MODEL="${MYPCBENCH_QWEN_MODEL:-}"

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
[ -n "$_SAVE_QWEN_MODEL" ] && export MYPCBENCH_QWEN_MODEL="$_SAVE_QWEN_MODEL"

if [ -z "${MYPCBENCH_QCOW2:-}" ]; then
  echo "FAIL: MYPCBENCH_QCOW2 unset" >&2
  exit 1
fi

PREFIX="phaseb-${LANE}-"
LOG="$A/results/phase_b_${LANE}_run.log"

setup_openrouter() {
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
}

case "$LANE" in
  claude)
    echo "WARN: Claude lane. Only run if Anthropic is billed." >&2
    AGENT_TYPE="${MYPCBENCH_CLAUDE_AGENT:-claude_cuabash}"
    AGENT_MODEL="${MYPCBENCH_CLAUDE_MODEL:-claude-opus-4-6}"
    if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
      echo "FAIL: ANTHROPIC_API_KEY empty" >&2
      exit 1
    fi
    ;;
  openai)
    unset OPENAI_BASE_URL
    AGENT_TYPE="${MYPCBENCH_OPENAI_AGENT:-openai_cuabash}"
    AGENT_MODEL="${MYPCBENCH_OPENAI_MODEL:-gpt-5.5}"
    if [ -z "${OPENAI_API_KEY:-}" ]; then
      echo "FAIL: OPENAI_API_KEY empty" >&2
      exit 1
    fi
    ;;
  qwen35a3b)
    setup_openrouter
    if [ -n "$_SAVE_QWEN_MODEL" ]; then
      AGENT_MODEL="$_SAVE_QWEN_MODEL"
    else
      AGENT_MODEL="qwen/qwen3.5-35b-a3b"
    fi
    if [[ "$AGENT_MODEL" != *qwen3.5-35b-a3b* ]]; then
      echo "FAIL: LANE=qwen35a3b but model=$AGENT_MODEL" >&2
      exit 2
    fi
    export MYPCBENCH_QWEN_MODEL="$AGENT_MODEL"
    ;;
  qwen359b)
    setup_openrouter
    if [ -n "$_SAVE_QWEN_MODEL" ]; then
      AGENT_MODEL="$_SAVE_QWEN_MODEL"
    else
      AGENT_MODEL="qwen/qwen3.5-9b"
    fi
    if [[ "$AGENT_MODEL" != *qwen3.5-9b* ]]; then
      echo "FAIL: LANE=qwen359b but model=$AGENT_MODEL" >&2
      exit 2
    fi
    export MYPCBENCH_QWEN_MODEL="$AGENT_MODEL"
    ;;
  qwen38flash)
    setup_openrouter
    if [ -n "$_SAVE_QWEN_MODEL" ]; then
      AGENT_MODEL="$_SAVE_QWEN_MODEL"
    else
      AGENT_MODEL="qwen/qwen3.8-flash"
    fi
    if [[ "$AGENT_MODEL" != *qwen3.8-flash* ]]; then
      echo "FAIL: LANE=qwen38flash but model=$AGENT_MODEL" >&2
      exit 2
    fi
    export MYPCBENCH_QWEN_MODEL="$AGENT_MODEL"
    ;;
esac

export PATH="$H/.venv/bin:$PATH"
export PYTHONUNBUFFERED=1
export MYPCBENCH_SKIP_QCOW2_REFRESH=1
export MYPCBENCH_VM_READY_TIMEOUT=3600
export MYPCBENCH_CF_SCRIPT="$A/scripts/cf_inject.py"
export MYPCBENCH_VM_HOST=127.0.0.1
export MYPCBENCH_AGENT_ROOT="$A"

# Six IDs Stage 4 never ran. The other four stay in results/stage4-*.
TASKS=(
  retrieval-f003
  retrieval-f016
  retrieval-f029
  retrieval-f030
  aggregation-f018
  preference_inference-f004
)

exec > >(tee -a "$LOG") 2>&1
echo "===== Phase B.2 $LANE start $(date -Is) ====="
echo "python3=$(which python3) agent=$AGENT_TYPE model=$AGENT_MODEL"
echo "PREFIX=$PREFIX"
echo "tasks: ${TASKS[*]}"
echo "do not touch results/stage4-* ; do not rewrite I"

pin_task() {
  local task_id="$1"
  python3 - "$FINAL" "$task_id" "$ONE_DIR/one.json" <<'PY'
import json, sys
from pathlib import Path
root, task_id, dest = sys.argv[1:]
hit = None
src = None
for path in sorted(Path(root).glob("*/*.rubrics.json")):
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else data.get("tasks") or []
    for t in items:
        if isinstance(t, dict) and t.get("id") == task_id:
            hit = t
            src = path
            break
    if hit:
        break
if not hit:
    raise SystemExit(f"no pinned rubric for {task_id} under {root}")
Path(dest).write_text(json.dumps([hit], indent=2) + "\n")
print(f"pinned {task_id} <- {src}")
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
  pin_task "$task_id"

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
    judge_dir "$base_h"
    archive_cell "$base_h" "$base_a"
  fi

  if cell_has_done "$cf_h"; then
    echo "skip $task_id cf (already DONE)"
  else
    stash_incomplete "$cf_h" "$stamp"
    stash_incomplete "$cf_a" "$stamp"
    unset MYPCBENCH_CF_PROBE_ONLY
    export MYPCBENCH_CF_TASK="$task_id"
    export MYPCBENCH_CF_OUT="$cf_a"
    run_agent "$cf_h"
    judge_dir "$cf_h"
    archive_cell "$cf_h" "$cf_a"
  fi
}

for tid in "${TASKS[@]}"; do
  echo "===== pair $tid ($LANE) ====="
  run_pair "$tid"
done

echo "===== Phase B.2 $LANE stop $(date -Is) ====="
echo "wrote $LOG"
echo "STOP: Stage 4 dirs untouched. Claude not required this session. Not-DONE cells stay in the table."
