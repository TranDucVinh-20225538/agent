#!/usr/bin/env bash
# Retry Qwen3.5-35B-A3B aggregation-f003 CF only (baseline already DONE).
# Does not touch Claude / OpenAI / HPC 27B / f001 / f018 / f004.
set -euo pipefail

A="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
H="$A/external/MyPCBench-main"
LOG="$A/results/stage4_qwen35a3b_f003_cf_retry.log"
FINAL="$H/tasks/final/speedtax/speedtax.rubrics.json"
ONE_DIR="$H/tasks/cf_one"
TASK=aggregation-f003

mkdir -p "$A/results" "$H/results" "$ONE_DIR" "$A/out"
cd "$H"
set -a
# shellcheck disable=SC1091
source .env
# shellcheck disable=SC1091
source ./mypcbench-vm/env.sh
set +a

if [ -z "${OPENROUTER_API_KEY:-}" ]; then
  echo "FAIL: OPENROUTER_API_KEY unset" >&2
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
echo "===== Qwen35a3b f003 CF retry3 start $(date -Is) ====="
echo "python3=$(which python3) agent=$AGENT_TYPE model=$AGENT_MODEL"
echo "OPENAI_BASE_URL=$OPENAI_BASE_URL"
echo "OPENAI_API_KEY=sk-proj? no (OpenRouter process override)"

python3 - "$FINAL" "$TASK" "$ONE_DIR/one.json" <<'PY'
import json, sys
src, task_id, dest = sys.argv[1:]
data = json.loads(open(src).read())
items = data if isinstance(data, list) else data.get("tasks") or []
hit = [t for t in items if isinstance(t, dict) and t.get("id") == task_id]
if not hit:
    raise SystemExit(f"no pinned rubric for {task_id}")
open(dest, "w").write(json.dumps(hit, indent=2) + "\n")
print(f"pinned {task_id}")
PY

base_a="$A/results/stage4-qwen35a3b-${TASK}/cf"
harness="$H/results/stage4-qwen35a3b-${TASK}/cf-retry3"
mkdir -p "$harness"
date -Is | tee "$harness/run_started.txt"

unset MYPCBENCH_CF_PROBE_ONLY
export MYPCBENCH_CF_TASK="$TASK"
export MYPCBENCH_CF_OUT="$base_a"
echo "----- agent $(date -Is) CF_TASK=$TASK -----"
set +e
python3 agent-harness/run_mypcbench.py --backend qemu \
  --qcow2_path "$MYPCBENCH_QCOW2" \
  --agent_type "$AGENT_TYPE" --model "$AGENT_MODEL" \
  --tasks_dir tasks/cf_one --max_steps 80 --timeout 7200 \
  --result_dir "$harness"
echo "agent_exit=$?"
set -e

export MYPCBENCH_JUDGE_FLAVOR=per_step
python3 agent-harness/judge_results.py --result_dir "$harness" || true
mkdir -p "$base_a"
rsync -a "$harness/" "$base_a/"
echo "archived $harness -> $base_a"
python3 "$A/scripts/write_stage4_results.py"
echo "===== Qwen35a3b f003 CF retry3 stop $(date -Is) ====="
