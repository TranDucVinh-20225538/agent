#!/usr/bin/env bash
# Retry ONLY preference_inference-f018 CF after attempt-1 CHECK failure.
# Parallel-safe: remapped hostfwd. Does not touch f004's :5000 VM. No baseline rerun.
set -euo pipefail

A=/mnt/data2/Vinh/agent
H="$A/external/MyPCBench-main"
LOG="$A/results/stage4_f018_cf_retry.log"
TASKS="$H/tasks/cf_f018_retry"
FINAL="$H/tasks/final/multi_app/multi_app.rubrics.json"
mkdir -p "$A/results" "$H/results" "$TASKS"

cd "$H"
set -a
# shellcheck disable=SC1091
source .env
# shellcheck disable=SC1091
source ./mypcbench-vm/env.sh
set +a
export PATH="$H/.venv/bin:$PATH"
export MYPCBENCH_SKIP_QCOW2_REFRESH=1
export MYPCBENCH_VM_READY_TIMEOUT=3600
export MYPCBENCH_CF_SCRIPT="$A/scripts/cf_inject.py"
export MYPCBENCH_VM_HOST=127.0.0.1

# Do not collide with stage4_run.sh f004 on :5000 / :5901 / :3001-3018 / :2222
# 13011 is already taken on this host; use 23001-23018.
export MYPCBENCH_HOST_API_PORT=15000
export MYPCBENCH_HOST_VNC_PORT=5902
export MYPCBENCH_HOST_SSH_PORT=12222
for p in $(seq 3001 3018); do
  export "MYPCBENCH_HOST_APP_PORT_${p}=$((p + 20000))"
done

unset MYPCBENCH_CF_PROBE_ONLY
export MYPCBENCH_CF_TASK=preference_inference-f018
export MYPCBENCH_CF_OUT="$A/results/stage4-preference_inference-f018/cf-retry-inject"

exec > >(tee -a "$LOG") 2>&1
echo "===== f018 CF retry start $(date -Is) ====="
echo "API=http://127.0.0.1:${MYPCBENCH_HOST_API_PORT} (parallel; f004 keeps :5000)"

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

SRC="$H/results/stage4-preference_inference-f018/cf-retry2"
DST="$A/results/stage4-preference_inference-f018/cf"
mkdir -p "$SRC"
date -Is | tee "$SRC/run_started.txt"

set +e
python3 agent-harness/run_mypcbench.py --backend qemu \
  --qcow2_path "$MYPCBENCH_QCOW2" \
  --container_name mypcbench-f018cf2 \
  --agent_type claude_cuabash --model claude-opus-4-6 \
  --tasks_dir tasks/cf_f018_retry --max_steps 80 --timeout 7200 \
  --result_dir "$SRC"
echo "agent_exit=$?"
set -e

export MYPCBENCH_JUDGE_FLAVOR=per_step
echo "----- judge $(date -Is) $SRC -----"
python3 agent-harness/judge_results.py --result_dir "$SRC" || true

GUEST="$A/results/stage4-preference_inference-f018/cf-retry-inject/preference_inference-f018.guest.json"
if [ ! -f "$SRC/preference_inference-f018/traj.jsonl" ]; then
  echo "RETRY DID NOT PRODUCE A TRAJECTORY; leaving attempt-1 CF artifacts in place"
  echo "===== f018 CF retry stop $(date -Is) ====="
  exit 1
fi
if [ -f "$GUEST" ] && grep -q '"gold_moved": false' "$GUEST"; then
  echo "WARNING: inject ran but primary probe did not move"
fi
mkdir -p "$DST"
rsync -a "$SRC/" "$DST/"
echo "archived $SRC -> $DST"
echo "===== f018 CF retry stop $(date -Is) ====="
