#!/usr/bin/env bash
# Stage 4 OpenAI CUA: same 4 frozen tasks + same SQL as Claude Opus.
# Does not overwrite results/stage4-<task>/ (Claude). Writes stage4-openai-*.
# Exploratory cross-model transfer, not confirmatory Qwen replication.
set -euo pipefail

A="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
H="$A/external/MyPCBench-main"
LOG="$A/results/stage4_openai_run.log"
FINAL="$H/tasks/final"
ONE_DIR="$H/tasks/cf_one"
mkdir -p "$A/results" "$H/results" "$ONE_DIR" "$A/out"

cd "$H"
set -a
# shellcheck disable=SC1091
source .env
# shellcheck disable=SC1091
source ./mypcbench-vm/env.sh
set +a

# Must hit api.openai.com, not a leftover local vLLM/Ollama.
unset OPENAI_BASE_URL

if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "FAIL: OPENAI_API_KEY empty. Put it in $H/.env then re-run." >&2
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

exec > >(tee -a "$LOG") 2>&1
echo "===== Stage 4 OpenAI start $(date -Is) ====="
echo "python3=$(which python3) agent=$AGENT_TYPE model=$AGENT_MODEL"
echo "OPENAI_API_KEY set? yes"
echo "OPENAI_BASE_URL=${OPENAI_BASE_URL:-unset}"
echo "label: exploratory GPT CUA; same frozen SQL as Claude; dirs stage4-openai-*"

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

run_pair() {
  local task_id="$1"
  local src="$2"
  pin_task "$task_id" "$src"

  local base_h="$H/results/stage4-openai-${task_id}/base"
  local cf_h="$H/results/stage4-openai-${task_id}/cf"
  local base_a="$A/results/stage4-openai-${task_id}/base"
  local cf_a="$A/results/stage4-openai-${task_id}/cf"

  unset MYPCBENCH_CF_PROBE_ONLY
  export MYPCBENCH_CF_TASK="$task_id"
  export MYPCBENCH_CF_PROBE_ONLY=1
  export MYPCBENCH_CF_OUT="$base_a"
  run_agent "$base_h"
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
run_pair aggregation-f003 "$FINAL/speedtax/speedtax.rubrics.json"
run_pair preference_inference-f018 "$FINAL/multi_app/multi_app.rubrics.json"
run_pair counterfactual-f004 "$FINAL/multi_app/multi_app.rubrics.json"

python3 "$A/scripts/write_stage4_results.py"
echo "===== Stage 4 OpenAI stop $(date -Is) ====="
echo "wrote $A/out/evidence_stage4_openai_results.md"
echo "STOP: Claude dirs untouched; no extra tasks"
