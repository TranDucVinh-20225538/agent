#!/usr/bin/env bash
# Study 2 matrix runner — ONE family, 57 locked legs (Option L / cell_order).
# Requires: source scripts/study2_bind_execution_key.sh (008…9dd) beforehand
#           (or via scripts/study2_matrix_lane.sh).
# Transport: scripts/study2_run_mypcbench.py → qwen_cuabash + OpenRouter chat-completions.
# Does NOT use Gate 0A smoke, SMALL lane, or native Claude/GPT agents.
#
# Usage: STUDY2_FAMILY=flash MODEL=… SLUG=study2-flash LANE=STUDY2 \
#          bash scripts/study2_exec_run.sh
# Prefer: bash scripts/study2_matrix_lane.sh flash
set -euo pipefail

A="${AGENT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
H="$A/external/MyPCBench-main"
FINAL="$H/tasks/final"
ONE_DIR="$H/tasks/cf_one"
MODEL="${MODEL:?set MODEL}"
LANE="${LANE:?set LANE=STUDY2}"
SLUG="${SLUG:?set SLUG}"
STUDY2_FAMILY="${STUDY2_FAMILY:?set STUDY2_FAMILY=flash|gpt|claude}"
OUT_ROOT="${OUT_ROOT:-$A/results/paper2_exec/$SLUG}"
PREFIX="paper2-${SLUG}-"
LOG="${LOG:-$A/results/paper2_exec_${SLUG}.log}"
CKPT_JSONL="$OUT_ROOT/CHECKPOINT.jsonl"
PROGRESS_MD="$OUT_ROOT/PROGRESS.md"
CONTAINER="${STUDY2_CONTAINER:-mypcbench-${SLUG}}"

die() { echo "STUDY2_EXEC_FAIL: $*" >&2; exit 1; }

[[ "$LANE" == "STUDY2" ]] || die "LANE must be STUDY2 (got $LANE)"

case "$STUDY2_FAMILY/$MODEL/$SLUG" in
  flash/qwen/qwen3.8-flash/study2-flash) ;;
  gpt/openai/gpt-5.5/study2-gpt) ;;
  claude/anthropic/claude-opus-4.6/study2-claude) ;;
  *) die "locked trio mismatch: FAMILY=$STUDY2_FAMILY MODEL=$MODEL SLUG=$SLUG" ;;
esac

# --- Funding / path hygiene (fail closed) ---
: "${OPENROUTER_API_KEY:?OPENROUTER_API_KEY unset — source scripts/study2_bind_execution_key.sh}"
: "${STUDY2_EXECUTION_KEY_FINGERPRINT:?bind fingerprint unset — source study2_bind_execution_key.sh}"
[[ "$STUDY2_EXECUTION_KEY_FINGERPRINT" == *008* ]] || die "fingerprint not 008…: $STUDY2_EXECUTION_KEY_FINGERPRINT"
[[ "$OPENROUTER_API_KEY" == sk-or-v1-008* ]] || die "runtime key is not 008… funding credential"
[[ -z "${OPENROUTER_API_KEY_SMALL:-}" ]] || die "OPENROUTER_API_KEY_SMALL still set"
[[ -z "${ANTHROPIC_API_KEY:-}" ]] || die "ANTHROPIC_API_KEY set — refuse native diversion"
[[ -z "${GATE0A_FAMILY:-}" && -z "${GATE0A_OUT:-}" && -z "${GATE0A_MODEL:-}" ]] \
  || die "Gate 0A env still set — refuse smoke launcher contamination"
export OPENAI_API_KEY="$OPENROUTER_API_KEY"
export OPENAI_BASE_URL="${OPENAI_BASE_URL:-https://openrouter.ai/api/v1}"
[[ "$OPENAI_BASE_URL" == *openrouter.ai* ]] || die "OPENAI_BASE_URL not OpenRouter"

mkdir -p "$A/results" "$H/results" "$ONE_DIR" "$OUT_ROOT" "$A/out"
cd "$H"

export PATH="$H/.venv/bin:$PATH"
export PYTHONUNBUFFERED=1
export PYTHONPATH="$H/agent-harness:$A/scripts:$A${PYTHONPATH:+:$PYTHONPATH}"
export MYPCBENCH_SKIP_QCOW2_REFRESH=1
export MYPCBENCH_VM_READY_TIMEOUT=3600
export MYPCBENCH_CF_SCRIPT="$A/scripts/cf_inject.py"
export MYPCBENCH_VM_HOST=127.0.0.1
export MYPCBENCH_AGENT_ROOT="$A"
export PAPER2_EXEC_SEED=20260904
export MYPCBENCH_JUDGE_FLAVOR=per_step
export STUDY2_FAMILY

: "${MYPCBENCH_QCOW2:?MYPCBENCH_QCOW2 unset}"
test -f "$MYPCBENCH_QCOW2" || die "qcow2 missing: $MYPCBENCH_QCOW2"

AGENT_MODEL="$MODEL"

mapfile -t LEGS < <(AGENT_ROOT="$A" python3 - <<'PY'
import json, os
from pathlib import Path
root = Path(os.environ["AGENT_ROOT"])
au = json.loads((root / "out/paper2_analysis_universe.json").read_text())
co = json.loads((root / "out/paper2_cell_order.json").read_text())
order = co["order"]
multi = set(au["multi_i_both_pass"])
surv = set(au["surviving_variants"])
assert len(order) == 25 and set(order) == set(au["tasks"])
assert not any("f024" in t for t in order)
legs = []
for task in order:
    assert task in surv, task
    legs.append((task, "G0", task, "1"))
    legs.append((task, "G1", task, "0"))
    if task in multi:
        i2 = f"{task}-I2"
        assert i2 in surv, i2
        legs.append((task, "G2", i2, "0"))
assert len(legs) == 57, len(legs)
for task, leg, cf_task, probe in legs:
    print(f"{task}\t{leg}\t{cf_task}\t{probe}")
PY
)
# Optional partial rerun (execution plumbing only — does not change locked order).
# STUDY2_ONLY_TASK=retrieval-f010 STUDY2_ONLY_LEGS=G0,G1 STUDY2_ALLOW_PARTIAL_LEGS=1
if [[ -n "${STUDY2_ONLY_TASK:-}" ]]; then
  mapfile -t LEGS < <(printf '%s\n' "${LEGS[@]}" | awk -F'\t' -v t="$STUDY2_ONLY_TASK" '$1==t')
fi
if [[ -n "${STUDY2_ONLY_LEGS:-}" ]]; then
  IFS=',' read -r -a _only_legs <<< "$STUDY2_ONLY_LEGS"
  _filt=()
  for row in "${LEGS[@]}"; do
    _leg="${row#*$'\t'}"; _leg="${_leg%%$'\t'*}"
    for want in "${_only_legs[@]}"; do
      [[ "$_leg" == "$want" ]] && _filt+=("$row") && break
    done
  done
  LEGS=("${_filt[@]}")
fi
if [[ "${STUDY2_ALLOW_PARTIAL_LEGS:-0}" == "1" ]]; then
  [[ "${#LEGS[@]}" -ge 1 ]] || die "partial filter produced zero legs"
else
  [[ "${#LEGS[@]}" -eq 57 ]] || die "expected 57 legs, got ${#LEGS[@]}"
fi

exec > >(stdbuf -oL -eL tee -a "$LOG") 2>&1
echo "===== Study2 exec start $(date -Is) ====="
echo "HEAD=$(git -C "$A" rev-parse --short HEAD) LANE=$LANE FAMILY=$STUDY2_FAMILY MODEL=$MODEL"
echo "bridge=scripts/study2_run_mypcbench.py fingerprint=$STUDY2_EXECUTION_KEY_FINGERPRINT"
echo "OUT_ROOT=$OUT_ROOT PREFIX=$PREFIX CONTAINER=$CONTAINER qcow2=$MYPCBENCH_QCOW2"
echo "legs=${#LEGS[@]} (full=57 unless STUDY2_ALLOW_PARTIAL_LEGS) max_steps=80 timeout=7200 CKPT=$CKPT_JSONL"
echo "partial_filter: ONLY_TASK=${STUDY2_ONLY_TASK:-} ONLY_LEGS=${STUDY2_ONLY_LEGS:-} ALLOW_PARTIAL=${STUDY2_ALLOW_PARTIAL_LEGS:-0}"
echo "binding_check: SMALL=unset ANTHROPIC=unset GATE0A=unset OPENROUTER=set"

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

cell_has_done() {
  local dir="$1"
  local helper="$A/scripts/paper2_traj_terminal.py"
  "$H/.venv/bin/python" "$helper" has-done-dir "$dir" 2>/dev/null \
    || python3 "$helper" has-done-dir "$dir" 2>/dev/null
}

cell_has_step() {
  local dir="$1"
  local f
  f=$(find "$dir" -name 'traj.jsonl' -size +0c -print -quit 2>/dev/null || true)
  # INFRA_FAIL lines are not model/agent steps.
  [ -n "$f" ] && grep -q '"step_num"' "$f" && ! grep -q '"action": "INFRA_FAIL"' "$f"
}

cell_is_finished() {
  local dir="$1"
  [ -f "$dir/paper2_leg_finished.json" ] && return 0
  cell_has_done "$dir"
}

stash_incomplete() {
  local dir="$1"
  local stamp="$2"
  if [ -d "$dir" ] && ! cell_is_finished "$dir"; then
    if cell_has_step "$dir" || [ -f "$dir/run_started.txt" ] || [ -d "$dir" ]; then
      if [ -n "$(find "$dir" -mindepth 1 -maxdepth 1 2>/dev/null | head -1)" ]; then
        local bak="${dir}-incomplete-${stamp}"
        echo "incomplete_stash $dir -> $bak"
        mv "$dir" "$bak"
        echo "{\"status\":\"INCOMPLETE_STASHED\",\"src\":\"$dir\",\"dest\":\"$bak\",\"at\":\"$(date -Is)\"}" \
          >"$bak/paper2_incomplete_marker.json" 2>/dev/null || true
      fi
    fi
  fi
}

archive_cell() {
  local src="$1"
  local dest="$2"
  mkdir -p "$dest"
  rsync -a "$src/" "$dest/"
  echo "archived $src -> $dest"
}

write_leg_checkpoint() {
  local task_id="$1" leg="$2" status="$3" result_dir="$4" archive_dir="$5" leg_i="$6"
  local steps=0 done=false
  local traj
  traj=$(find "$result_dir" -name 'traj.jsonl' -size +0c -print -quit 2>/dev/null || true)
  if [ -n "$traj" ]; then
    steps=$(grep -c '"step_num"' "$traj" || true)
    if python3 "$A/scripts/paper2_traj_terminal.py" has-done "$traj" 2>/dev/null; then
      done=true
    fi
  fi
  local finished_at
  finished_at=$(date -Is)
  python3 - "$result_dir" "$archive_dir" "$task_id" "$leg" "$status" "$steps" "$done" "$MODEL" "$LANE" "$leg_i" "$finished_at" "$CKPT_JSONL" "$PROGRESS_MD" <<'PY'
import json, sys
from pathlib import Path
result_dir, archive_dir, task, leg, status, steps, done, model, lane, leg_i, finished_at, ckpt, progress = sys.argv[1:]
payload = {
    "leg_index": int(leg_i),
    "legs_total": 57,
    "task": task,
    "leg": leg,
    "status": status,
    "steps": int(steps),
    "has_done_action": done.lower() == "true",
    "model": model,
    "lane": lane,
    "finished_at": finished_at,
    "result_dir": result_dir,
    "archive_dir": archive_dir,
}
text = json.dumps(payload, indent=2) + "\n"
for d in (Path(result_dir), Path(archive_dir)):
    d.mkdir(parents=True, exist_ok=True)
    (d / "paper2_leg_finished.json").write_text(text)
Path(ckpt).parent.mkdir(parents=True, exist_ok=True)
with Path(ckpt).open("a") as f:
    f.write(json.dumps(payload) + "\n")
    f.flush()
lines = []
if Path(ckpt).exists():
    for line in Path(ckpt).read_text().splitlines():
        if line.strip():
            lines.append(json.loads(line))
latest = {}
for o in lines:
    latest[(o["task"], o["leg"])] = o
done_n = sum(1 for o in latest.values() if o.get("status") == "DONE")
term_n = sum(1 for o in latest.values() if o.get("status") == "TERMINAL_FAIL")
md = [
    f"# Study2 progress — {model} ({lane})",
    "",
    f"- updated: {finished_at}",
    f"- checkpointed legs: {len(latest)}/57",
    f"- DONE (real): {done_n}",
    f"- TERMINAL_FAIL (complete run, no DONE action): {term_n}",
    f"- last: {task} {leg} → **{status}** (steps={steps})",
    "",
    "Partial/incomplete dirs use suffix `-incomplete-*` and are NOT counted here.",
    "",
]
Path(progress).write_text("\n".join(md) + "\n")
print(f"checkpoint status={status} task={task} leg={leg} steps={steps} done={done}")
PY
}

run_agent() {
  local result_dir="$1"
  echo "----- agent $(date -Is) result_dir=$result_dir CF_TASK=${MYPCBENCH_CF_TASK:-unset} PROBE_ONLY=${MYPCBENCH_CF_PROBE_ONLY:-unset} -----"
  mkdir -p "$result_dir"
  date -Is | tee "$result_dir/run_started.txt"
  echo "lane=$LANE family=$STUDY2_FAMILY model=$MODEL bridge=study2_run_mypcbench leg_meta=${PAPER2_LEG_META:-}" \
    | tee "$result_dir/paper2_leg_meta.txt"
  set +e
  # Thin bridge: generic OpenRouter executor (not Gate 0A smoke; not native agents).
  python3 "$A/scripts/study2_run_mypcbench.py" --backend qemu \
    --qcow2_path "$MYPCBENCH_QCOW2" \
    --container_name "$CONTAINER" \
    --agent_type qwen_cuabash --model "$AGENT_MODEL" \
    --tasks_dir tasks/cf_one --max_steps 80 --timeout 7200 \
    --result_dir "$result_dir"
  local rc=$?
  set -e
  echo "agent_exit=$rc result_dir=$result_dir"
  if [ "$rc" -ne 0 ]; then
    if grep -REiq 'insufficient_quota|quota.?exceeded|credit.?exhausted|billing|429 Too Many|401 Unauthorized|403 Forbidden' \
        "$result_dir" "$LOG" 2>/dev/null; then
      echo "BUDGET_OR_AUTH_STOP rc=$rc — refusing failover" | tee -a "$OUT_ROOT/BUDGET_STOP.txt"
      write_leg_checkpoint "$task_id" "$leg" "BUDGET_STOP" "$result_dir" "$local_a" "$leg_i" || true
      exit 75
    fi
  fi
  return 0
}

judge_dir() {
  local result_dir="$1"
  export MYPCBENCH_JUDGE_FLAVOR=per_step
  echo "----- judge $(date -Is) $result_dir -----"
  python3 agent-harness/judge_results.py --result_dir "$result_dir" || true
}

leg_i=0
for row in "${LEGS[@]}"; do
  IFS=$'\t' read -r task_id leg cf_task probe <<<"$row"
  leg_i=$((leg_i + 1))
  echo "===== leg $leg_i/57 $task_id $leg cf=$cf_task probe=$probe ====="
  pin_task "$task_id"

  local_h="$H/results/${PREFIX}${task_id}/${leg}"
  local_a="$OUT_ROOT/${task_id}/${leg}"
  stamp="$(date +%Y%m%dT%H%M%S)"
  export PAPER2_LEG_META="model=$MODEL task=$task_id leg=$leg cf_task=$cf_task"

  if cell_is_finished "$local_h" || cell_is_finished "$local_a"; then
    echo "skip $task_id $leg (terminal checkpoint or DONE — not re-run)"
    if [ -d "$local_h" ]; then
      archive_cell "$local_h" "$local_a"
      if cell_has_done "$local_h"; then
        write_leg_checkpoint "$task_id" "$leg" "DONE" "$local_h" "$local_a" "$leg_i"
      elif [ ! -f "$local_h/paper2_leg_finished.json" ]; then
        write_leg_checkpoint "$task_id" "$leg" "TERMINAL_FAIL" "$local_h" "$local_a" "$leg_i"
      fi
    fi
    continue
  fi

  stash_incomplete "$local_h" "$stamp"
  stash_incomplete "$local_a" "$stamp"

  unset MYPCBENCH_CF_PROBE_ONLY || true
  export MYPCBENCH_CF_TASK="$cf_task"
  export MYPCBENCH_CF_OUT="$local_a"
  if [ "$probe" = "1" ]; then
    export MYPCBENCH_CF_PROBE_ONLY=1
  fi

  run_agent "$local_h"
  if ! cell_has_step "$local_h" && ! cell_has_done "$local_h"; then
    echo "infra_retry=1 same cell $task_id $leg"
    echo "infra_retry=1" | tee -a "$local_h/infra_retry.txt"
    run_agent "$local_h"
  fi

  judge_dir "$local_h"
  archive_cell "$local_h" "$local_a"

  if cell_has_done "$local_h"; then
    write_leg_checkpoint "$task_id" "$leg" "DONE" "$local_h" "$local_a" "$leg_i"
  elif [ -f "$local_h/infra_fail.json" ]; then
    write_leg_checkpoint "$task_id" "$leg" "INFRA_FAIL" "$local_h" "$local_a" "$leg_i"
  elif cell_has_step "$local_h"; then
    write_leg_checkpoint "$task_id" "$leg" "TERMINAL_FAIL" "$local_h" "$local_a" "$leg_i"
  else
    write_leg_checkpoint "$task_id" "$leg" "BOOT_NO_RESULT" "$local_h" "$local_a" "$leg_i"
  fi
done

echo "===== Study2 exec stop $(date -Is) MODEL=$MODEL ====="
echo "wrote $LOG"
echo "OUT_ROOT=$OUT_ROOT CKPT=$CKPT_JSONL PROGRESS=$PROGRESS_MD"
date -Is | tee "$OUT_ROOT/LANE_COMPLETE"
echo "lane_complete study2 model=$MODEL slug=$SLUG legs=57" | tee -a "$OUT_ROOT/LANE_COMPLETE"
