#!/usr/bin/env bash
# Stage 4 Qwen3.5-27B CUA: same 4 frozen tasks + same SQL as Claude.
# Requires a live vLLM at OPENAI_BASE_URL (cu129 smoke stack).
# Writes results/stage4-qwen35-* — does not touch Claude or OpenAI dirs.
set -euo pipefail

A="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
H="$A/external/MyPCBench-main"
LOG="$A/results/stage4_qwen35_run.log"
FINAL="$H/tasks/final"
ONE_DIR="$H/tasks/cf_one"
mkdir -p "$A/results" "$H/results" "$ONE_DIR" "$A/out"

cd "$H"
set -a
# HPC clones often have no .env (keys live in the SLURM environment).
# Missing file must not abort the job or trip a trap that kills vLLM.
if [ -f .env ]; then
  # shellcheck disable=SC1091
  source .env
else
  echo "WARN: $H/.env missing; using process env only"
fi
if [ -f ./mypcbench-vm/env.sh ]; then
  # shellcheck disable=SC1091
  source ./mypcbench-vm/env.sh
else
  echo "WARN: mypcbench-vm/env.sh missing; MYPCBENCH_QCOW2 must already be set"
fi
set +a

if [ -z "${MYPCBENCH_QCOW2:-}" ]; then
  echo "FAIL: MYPCBENCH_QCOW2 unset and no mypcbench-vm/env.sh" >&2
  exit 1
fi

export OPENAI_BASE_URL="${OPENAI_BASE_URL:-http://127.0.0.1:8000/v1}"
export OPENAI_API_KEY="${OPENAI_API_KEY:-dummy}"
AGENT_TYPE="${MYPCBENCH_QWEN_AGENT:-qwen_cuabash}"
AGENT_MODEL="${MYPCBENCH_QWEN_MODEL:-Qwen/Qwen3.5-27B}"

if ! python3 - <<PY
import json, os, urllib.request
url = os.environ["OPENAI_BASE_URL"].rstrip("/") + "/models"
try:
    with urllib.request.urlopen(url, timeout=10) as r:
        ids = [m.get("id") for m in json.load(r).get("data", [])]
except Exception as e:
    raise SystemExit(f"FAIL: vLLM not reachable at {url}: {e}")
print("vLLM models:", ids)
want = os.environ.get("MYPCBENCH_QWEN_MODEL", "Qwen/Qwen3.5-27B")
if want not in ids and ids:
    print("WARN: served ids do not contain", want)
PY
then
  echo "FAIL: start vLLM (cu129 / .venv-qwen35-cu12-test) before this script." >&2
  exit 1
fi

export PATH="$H/.venv/bin:$PATH"
export MYPCBENCH_SKIP_QCOW2_REFRESH=1
export MYPCBENCH_VM_READY_TIMEOUT=3600
export MYPCBENCH_CF_SCRIPT="$A/scripts/cf_inject.py"
export MYPCBENCH_VM_HOST=127.0.0.1
export MYPCBENCH_AGENT_ROOT="$A"
export STAGE4_TAG=qwen35

# HPC 57947: default SSH 16000 was already bound on node004. QEMU died
# immediately; 8 cells wrote empty traj. That is not a Stage 4 result.
# Override via env if these three are also taken.
export MYPCBENCH_HOST_SSH_PORT="${MYPCBENCH_HOST_SSH_PORT:-18700}"
export MYPCBENCH_HOST_VNC_PORT="${MYPCBENCH_HOST_VNC_PORT:-5917}"
export MYPCBENCH_HOST_API_PORT="${MYPCBENCH_HOST_API_PORT:-12800}"

python3 - <<'PY'
import os, socket

ports = [
    ("SSH", int(os.environ["MYPCBENCH_HOST_SSH_PORT"])),
    ("VNC", int(os.environ["MYPCBENCH_HOST_VNC_PORT"])),
    ("API", int(os.environ["MYPCBENCH_HOST_API_PORT"])),
]

def listening(port: int) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.3)
    try:
        return s.connect_ex(("127.0.0.1", port)) == 0
    finally:
        s.close()

busy = [(name, port) for name, port in ports if listening(port)]
print("QEMU hostfwd:", ", ".join(f"{n}={p}" for n, p in ports))
if busy:
    detail = ", ".join(f"{n} 127.0.0.1:{p}" for n, p in busy)
    raise SystemExit(f"FAIL: QEMU port already bound ({detail}). Not a Stage 4 run.")
print("QEMU ports free")
PY

exec > >(tee -a "$LOG") 2>&1
echo "===== Stage 4 Qwen3.5-27B start $(date -Is) ====="
echo "python3=$(which python3) agent=$AGENT_TYPE model=$AGENT_MODEL"
echo "OPENAI_BASE_URL=$OPENAI_BASE_URL"
echo "QEMU hostfwd SSH=$MYPCBENCH_HOST_SSH_PORT VNC=$MYPCBENCH_HOST_VNC_PORT API=$MYPCBENCH_HOST_API_PORT"
echo "label: Qwen3.5-27B qwen_cuabash; frozen SQL; dirs stage4-qwen35-*"
echo "NOT paper 35B-A3B. NOT Claude/OpenAI overwrite."
echo "57946/57947 are not Stage 4 cells (.env trap / bound port / empty traj)."

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

cell_has_traj() {
  local dir="$1"
  find "$dir" -name 'traj.jsonl' -size +0c -print -quit 2>/dev/null | grep -q .
}

run_pair() {
  local task_id="$1"
  local src="$2"
  local gate="${3:-}"
  pin_task "$task_id" "$src"

  local base_h="$H/results/stage4-qwen35-${task_id}/base"
  local cf_h="$H/results/stage4-qwen35-${task_id}/cf"
  local base_a="$A/results/stage4-qwen35-${task_id}/base"
  local cf_a="$A/results/stage4-qwen35-${task_id}/cf"

  unset MYPCBENCH_CF_PROBE_ONLY
  export MYPCBENCH_CF_TASK="$task_id"
  export MYPCBENCH_CF_PROBE_ONLY=1
  export MYPCBENCH_CF_OUT="$base_a"
  run_agent "$base_h"
  if [ "$gate" = "gate" ]; then
    if ! cell_has_traj "$base_h"; then
      echo "FAIL: $task_id base has no traj — QEMU/agent did not run." >&2
      echo "Empty traj is not a Stage 4 cell. Do not judge or continue." >&2
      exit 1
    fi
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

run_pair retrieval-f001 "$FINAL/dinoco_airlines/dinoco_airlines.rubrics.json" gate
run_pair aggregation-f003 "$FINAL/speedtax/speedtax.rubrics.json"
run_pair preference_inference-f018 "$FINAL/multi_app/multi_app.rubrics.json"
run_pair counterfactual-f004 "$FINAL/multi_app/multi_app.rubrics.json"

python3 "$A/scripts/write_stage4_results.py"
echo "===== Stage 4 Qwen3.5-27B stop $(date -Is) ====="
echo "wrote $A/out/evidence_stage4_qwen35_results.md"
echo "STOP: no extra tasks; Claude/OpenAI dirs untouched"
