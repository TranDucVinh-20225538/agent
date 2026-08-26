#!/usr/bin/env bash
# Stage 3a: dummy-probe every pre-registered sample member.
# Does not call Claude. Does not drop a member that fails identifiability —
# it records the failure and continues to the next sampled id, in order.
set -euo pipefail

A=/mnt/data2/Vinh/agent
H="$A/external/MyPCBench-main"
LOG="$A/results/phase_d_sample_probe.log"

cd "$A"
python3 scripts/evidence_screen.py

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
echo "===== sample dummy-probe start $(date -Is) ====="

python3 - <<'PY'
import csv, json, pathlib
sample = json.loads(pathlib.Path("/mnt/data2/Vinh/agent/out/evidence_sample.json").read_text())
path = pathlib.Path("/mnt/data2/Vinh/agent/results/evidence_sample_ids.txt")
path.write_text("\n".join(r["id"] for r in sample["sample"]) + "\n")
print("sample", len(sample["sample"]))
PY

while read -r TID; do
  [ -z "$TID" ] && continue
  echo "----- probe $TID $(date -Is) -----"
  python3 - <<PY
import json, pathlib
tid = "$TID"
root = pathlib.Path("$A/external/MyPCBench-main/tasks/final")
src = None
for path in root.glob("*/*.rubrics.json"):
    data = json.loads(path.read_text())
    tasks = data if isinstance(data, list) else data.get("tasks", [])
    for t in tasks:
        if t.get("id") == tid:
            src = t
            break
    if src:
        break
if not src:
    raise SystemExit(f"no pinned rubric for {tid}")
d = pathlib.Path("$H/tasks/cf_one")
d.mkdir(parents=True, exist_ok=True)
(d / "one.json").write_text(json.dumps([src], indent=2) + "\n")
print("wrote", d / "one.json")
PY
  export AGENT_TYPE=dummy AGENT_MODEL=dummy
  export MYPCBENCH_CF_TASK="$TID"
  export MYPCBENCH_CF_PROBE_ONLY=1
  export MYPCBENCH_CF_OUT="$A/results/probe-$TID"
  mkdir -p "$MYPCBENCH_CF_OUT" "$H/results/probe-$TID"
  date -Is | tee "$H/results/probe-$TID/run_started.txt"
  python3 agent-harness/run_mypcbench.py --backend qemu \
    --qcow2_path "$MYPCBENCH_QCOW2" \
    --agent_type dummy --model dummy \
    --tasks_dir tasks/cf_one --max_steps 4 --timeout 7200 \
    --result_dir "$H/results/probe-$TID" || echo "WARN: dummy run exited non-zero for $TID"
  echo "$TID probe done"
done < "$A/results/evidence_sample_ids.txt"

echo "===== sample dummy-probe stop $(date -Is) ====="
echo "Record identifiability per id. Do not draw replacements."
echo "Claude is a separate step over the same sample list."
