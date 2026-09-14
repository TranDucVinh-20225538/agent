#!/usr/bin/env bash
# Autonomous evidence-slot search. Probe (dummy) always precedes Claude.
# Stops at 8 completed evidence types, or when the queue is empty.
set -euo pipefail

A=/mnt/data2/Vinh/agent
H="$A/external/MyPCBench-main"
LOG="$A/results/phase_d_search.log"
MAX_TYPES=8
mkdir -p "$A/results" "$H/results"

cd "$A"
python3 scripts/evidence_scan.py

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
echo "===== phase D search start $(date -Is) ====="

done_types() {
  python3 -c "
import csv
from pathlib import Path
p=Path('$A/results/evidence_coverage.csv')
s=set()
for row in csv.DictReader(p.open()):
    if row['status']=='done':
        s.add(row['evidence_type'])
print(len(s))
"
}

next_id() {
  python3 -c "
import json
from pathlib import Path
q=json.loads(Path('$A/out/evidence_queue.json').read_text())
print(q['runnable'][0]['id'] if q['runnable'] else '')
"
}

run_agent() {
  local result_dir="$1"
  local tasks_dir="$2"
  mkdir -p "$result_dir"
  date -Is | tee "$result_dir/run_started.txt"
  python3 agent-harness/run_mypcbench.py --backend qemu \
    --qcow2_path "$MYPCBENCH_QCOW2" \
    --agent_type "${AGENT_TYPE:-claude_cuabash}" --model "${AGENT_MODEL:-claude-opus-4-6}" \
    --tasks_dir "$tasks_dir" --max_steps 80 --timeout 7200 \
    --result_dir "$result_dir"
}

while true; do
  n=$(done_types)
  if [ "$n" -ge "$MAX_TYPES" ]; then
    echo "stop: $n evidence types completed"
    break
  fi
  python3 "$A/scripts/evidence_scan.py"
  TID=$(next_id)
  if [ -z "$TID" ]; then
    echo "stop: no runnable candidate with a known probe"
    break
  fi
  echo "----- candidate $TID $(date -Is) -----"
  python3 -c "
import json, pathlib
from scripts.evidence_scan import load_pinned
" 2>/dev/null || true
  python3 << PY
import json, pathlib, sys
sys.path.insert(0, "$A")
q = json.loads(pathlib.Path("$A/out/evidence_queue.json").read_text())
c = q["runnable"][0]
assert c["id"] == "$TID"
# write pinned one-task file
src = None
root = pathlib.Path("$A/external/MyPCBench-main/tasks/final")
for path in root.glob("*/*.rubrics.json"):
    data = json.loads(path.read_text())
    tasks = data if isinstance(data, list) else data.get("tasks", [])
    for t in tasks:
        if t.get("id") == "$TID":
            src = t
            break
    if src:
        break
if not src:
    raise SystemExit("no pinned rubric for $TID")
d = pathlib.Path("$H/tasks/cf_one")
d.mkdir(parents=True, exist_ok=True)
(d / "one.json").write_text(json.dumps([src], indent=2) + "\n")
print("wrote", d / "one.json")
PY

  export AGENT_TYPE=dummy AGENT_MODEL=dummy
  export MYPCBENCH_CF_TASK="$TID"
  export MYPCBENCH_CF_PROBE_ONLY=1
  export MYPCBENCH_CF_OUT="$A/results/probe-$TID"
  run_agent "$H/results/probe-$TID" tasks/cf_one || true
  unset AGENT_TYPE AGENT_MODEL
  PROBE_JSON=$(ls "$A/results/probe-$TID"/*.guest.json 2>/dev/null | head -1 || true)
  if [ -z "$PROBE_JSON" ]; then
    echo "$TID: no probe json — reject"
    echo "x,$TID,unknown,,,n/a,n/a,n/a,rejected_no_probe" >> "$A/results/evidence_coverage.csv"
    # mark so scan will not pick it again: append skip by adding a dummy done? use rejected status
    python3 -c "
import json, pathlib
p=pathlib.Path('$A/out/evidence_queue.json')
" 
    # rotate: write a skip file
    echo "$TID" >> "$A/results/evidence_skip.txt"
    # evidence_scan doesn't read skip yet
    break
  fi
  set +e
  python3 "$A/scripts/evidence_gate.py" "$PROBE_JSON" "$TID"
  GATE=$?
  set -e
  if [ "$GATE" -ne 0 ]; then
    echo "$TID: not identifiable — \$0 reject"
    printf '%s\n' "x,$TID,$(python3 -c "import json;print(json.load(open('$A/out/evidence_queue.json'))['runnable'][0]['evidence_type'])"),n/a,none,n/a,n/a,n/a,rejected_not_identifiable" >> "$A/results/evidence_coverage.csv"
    echo "$TID" >> "$A/results/evidence_skip.txt"
    # prevent infinite loop: remove probe template by recording skip in coverage as rejected
    python3 -c "
from pathlib import Path
p = Path('$A/scripts/evidence_scan.py')
" 
    break
  fi

  unset MYPCBENCH_CF_PROBE_ONLY
  export MYPCBENCH_CF_TASK="$TID"
  export MYPCBENCH_CF_OUT="$A/results/base-$TID"
  run_agent "$H/results/base-$TID" tasks/cf_one
  export MYPCBENCH_CF_TASK="${TID}-CF"
  export MYPCBENCH_CF_OUT="$A/results/cf-$TID"
  run_agent "$H/results/cf-$TID" tasks/cf_one

  export MYPCBENCH_JUDGE_FLAVOR=per_step
  python3 agent-harness/judge_results.py --result_dir "$H/results/base-$TID" || true
  python3 agent-harness/judge_results.py --result_dir "$H/results/cf-$TID" || true
  rsync -a "$H/results/base-$TID/" "$A/results/base-$TID/"
  rsync -a "$H/results/cf-$TID/" "$A/results/cf-$TID/"
  echo "append coverage row by hand from traj if the writer is missing"
  break
done

echo "===== phase D search stop $(date -Is) ====="
echo "Re-run evidence_scan after recording skip/done so the next candidate can proceed."
echo "Commit and push to phase-a-results. Do not run the full benchmark."
