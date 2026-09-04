#!/usr/bin/env bash
# Paper 2 execution runner — walks out/paper2_cell_order.json for ONE model.
# Legs: G0 (probe-only) → G1 (I1) → G2 (I2 if multi-I). No model failover.
# Resume-safe: skips paper2_leg_finished.json / real DONE; stashes incomplete crashes only.
# Usage: MODEL=qwen/qwen3.5-9b LANE=SMALL bash scripts/paper2_exec_run.sh
# Prefer: bash scripts/paper2_exec_small_lane.sh qwen/qwen3.5-9b
set -euo pipefail

A="${AGENT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
H="$A/external/MyPCBench-main"
FINAL="$H/tasks/final"
ONE_DIR="$H/tasks/cf_one"
MODEL="${MODEL:?set MODEL}"
LANE="${LANE:?set LANE=SMALL|LARGE}"
SLUG="${SLUG:?set SLUG}"
OUT_ROOT="${OUT_ROOT:-$A/results/paper2_exec/$SLUG}"
PREFIX="paper2-${SLUG}-"
LOG="${LOG:-$A/results/paper2_exec_${SLUG}.log}"
CKPT_JSONL="$OUT_ROOT/CHECKPOINT.jsonl"
PROGRESS_MD="$OUT_ROOT/PROGRESS.md"

die() { echo "FAIL: $*" >&2; exit 1; }

case "$LANE" in
  SMALL)
    case "$MODEL" in
      qwen/qwen3.5-9b|qwen/qwen3.8-flash) ;;
      *) die "SMALL lane rejects MODEL=$MODEL" ;;
    esac
    ;;
  LARGE)
    case "$MODEL" in
      claude-opus-4-6|gpt-5.5) ;;
      *) die "LARGE lane rejects MODEL=$MODEL" ;;
    esac
    ;;
  *) die "LANE must be SMALL or LARGE" ;;
esac

mkdir -p "$A/results" "$H/results" "$ONE_DIR" "$OUT_ROOT" "$A/out"
cd "$H"

export PATH="$H/.venv/bin:$PATH"
export PYTHONUNBUFFERED=1
export MYPCBENCH_SKIP_QCOW2_REFRESH=1
export MYPCBENCH_VM_READY_TIMEOUT=3600
export MYPCBENCH_CF_SCRIPT="$A/scripts/cf_inject.py"
export MYPCBENCH_VM_HOST=127.0.0.1
export MYPCBENCH_AGENT_ROOT="$A"
export PAPER2_EXEC_SEED=20260904
export MYPCBENCH_JUDGE_FLAVOR=per_step

: "${MYPCBENCH_QCOW2:?MYPCBENCH_QCOW2 unset}"
test -f "$MYPCBENCH_QCOW2" || die "qcow2 missing: $MYPCBENCH_QCOW2"

case "$MODEL" in
  qwen/*)
    AGENT_TYPE="${MYPCBENCH_QWEN_AGENT:-qwen_cuabash}"
    export MYPCBENCH_QWEN_MODEL="$MODEL"
    : "${OPENROUTER_API_KEY:?OPENROUTER_API_KEY unset (bind from _SMALL first)}"
    export OPENAI_BASE_URL="${OPENAI_BASE_URL:-https://openrouter.ai/api/v1}"
    export OPENAI_API_KEY="$OPENROUTER_API_KEY"
    if [ "$LANE" = SMALL ]; then
      if [ -n "${ANTHROPIC_API_KEY:-}" ] || [ -n "${OPENROUTER_API_KEY_LARGE:-}" ]; then
        die "SMALL lane still has ANTHROPIC or OPENROUTER_API_KEY_LARGE in env"
      fi
    fi
    ;;
  claude-opus-4-6)
    AGENT_TYPE="${MYPCBENCH_CLAUDE_AGENT:-claude_cuabash}"
    : "${ANTHROPIC_API_KEY:?ANTHROPIC_API_KEY unset}"
    unset OPENROUTER_API_KEY OPENROUTER_API_KEY_SMALL OPENAI_API_KEY OPENAI_BASE_URL || true
    ;;
  gpt-5.5)
    AGENT_TYPE="${MYPCBENCH_OPENAI_AGENT:-openai_cuabash}"
    : "${OPENAI_API_KEY:?OPENAI_API_KEY unset}"
    unset OPENROUTER_API_KEY OPENROUTER_API_KEY_SMALL OPENAI_BASE_URL ANTHROPIC_API_KEY || true
    ;;
esac
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
assert au["legs"]["total"] == 228
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

# Line-buffered log so a dead tmux still leaves a usable trail.
exec > >(stdbuf -oL -eL tee -a "$LOG") 2>&1
echo "===== Paper2 exec start $(date -Is) ====="
echo "HEAD=$(git -C "$A" rev-parse --short HEAD) LANE=$LANE MODEL=$MODEL AGENT=$AGENT_TYPE"
echo "OUT_ROOT=$OUT_ROOT PREFIX=$PREFIX qcow2=$MYPCBENCH_QCOW2"
echo "legs=${#LEGS[@]} (expect 57) CKPT=$CKPT_JSONL"
echo "binding_check: ANTHROPIC=$([ -n "${ANTHROPIC_API_KEY:-}" ] && echo SET || echo UNSET) LARGE=$([ -n "${OPENROUTER_API_KEY_LARGE:-}" ] && echo SET || echo UNSET) OPENROUTER=$([ -n "${OPENROUTER_API_KEY:-}" ] && echo SET || echo UNSET)"

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
  local f
  f=$(find "$dir" -name 'traj.jsonl' -size +0c -print -quit 2>/dev/null || true)
  [ -n "$f" ] && grep -Eq '"action": "DONE"|"done": true' "$f"
}

cell_has_step() {
  local dir="$1"
  local f
  f=$(find "$dir" -name 'traj.jsonl' -size +0c -print -quit 2>/dev/null || true)
  [ -n "$f" ] && grep -q '"step_num"' "$f"
}

cell_is_finished() {
  # Terminal only if explicit finished marker or real DONE action.
  # Partial traj without marker is NOT completed.
  local dir="$1"
  [ -f "$dir/paper2_leg_finished.json" ] && return 0
  cell_has_done "$dir"
}

stash_incomplete() {
  local dir="$1"
  local stamp="$2"
  if [ -d "$dir" ] && ! cell_is_finished "$dir"; then
    # stash boot-only or mid-crash dirs so they are never counted as completed
    if cell_has_step "$dir" || [ -f "$dir/run_started.txt" ] || [ -d "$dir" ]; then
      # only stash non-empty
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
  # status: DONE | TERMINAL_FAIL | BUDGET_STOP | BOOT_NO_RESULT
  local task_id="$1" leg="$2" status="$3" result_dir="$4" archive_dir="$5" leg_i="$6"
  local steps=0 done=false
  local traj
  traj=$(find "$result_dir" -name 'traj.jsonl' -size +0c -print -quit 2>/dev/null || true)
  if [ -n "$traj" ]; then
    steps=$(grep -c '"step_num"' "$traj" || true)
    if grep -Eq '"action": "DONE"|"done": true' "$traj"; then done=true; fi
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
# rewrite progress snapshot
lines = []
if Path(ckpt).exists():
    for line in Path(ckpt).read_text().splitlines():
        if line.strip():
            lines.append(json.loads(line))
# keep last record per (task,leg)
latest = {}
for o in lines:
    latest[(o["task"], o["leg"])] = o
done_n = sum(1 for o in latest.values() if o.get("status") == "DONE")
term_n = sum(1 for o in latest.values() if o.get("status") == "TERMINAL_FAIL")
md = [
    f"# Paper2 progress — {model} ({lane})",
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
  echo "lane=$LANE model=$MODEL leg_meta=${PAPER2_LEG_META:-}" | tee "$result_dir/paper2_leg_meta.txt"
  set +e
  python3 agent-harness/run_mypcbench.py --backend qemu \
    --qcow2_path "$MYPCBENCH_QCOW2" \
    --agent_type "$AGENT_TYPE" --model "$AGENT_MODEL" \
    --tasks_dir tasks/cf_one --max_steps 80 --timeout 7200 \
    --result_dir "$result_dir"
  local rc=$?
  set -e
  echo "agent_exit=$rc result_dir=$result_dir"
  if [ "$rc" -ne 0 ]; then
    if grep -REiq 'insufficient_quota|quota.?exceeded|credit.?exhausted|billing|429 Too Many|401 Unauthorized|403 Forbidden' \
        "$result_dir" "$LOG" 2>/dev/null; then
      echo "BUDGET_OR_AUTH_STOP rc=$rc — refusing failover to another model/key" | tee -a "$OUT_ROOT/BUDGET_STOP.txt"
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
    # ensure archive + finished marker exist on both sides
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

  # Resume path: stash crash/partial so it cannot be mistaken for completed.
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
  elif cell_has_step "$local_h"; then
    write_leg_checkpoint "$task_id" "$leg" "TERMINAL_FAIL" "$local_h" "$local_a" "$leg_i"
  else
    write_leg_checkpoint "$task_id" "$leg" "BOOT_NO_RESULT" "$local_h" "$local_a" "$leg_i"
  fi
done

echo "===== Paper2 exec stop $(date -Is) MODEL=$MODEL ====="
echo "wrote $LOG"
echo "OUT_ROOT=$OUT_ROOT CKPT=$CKPT_JSONL PROGRESS=$PROGRESS_MD"
# Marker for chain scripts (9b → flash). Not written on BUDGET_STOP (exit 75 above).
date -Is | tee "$OUT_ROOT/LANE_COMPLETE"
echo "lane_complete model=$MODEL slug=$SLUG legs=57" | tee -a "$OUT_ROOT/LANE_COMPLETE"
