#!/usr/bin/env bash
# Wait for Paper2 Qwen 9B SMALL lane to finish, then start Qwen 3.8-Flash (same SMALL key).
# Does not interrupt a live 9B run. Does NOT start Flash after BUDGET_STOP.
# No Claude/GPT. No LARGE key.
set -euo pipefail

A="${AGENT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
NINE_OUT="$A/results/paper2_exec/qwen35-9b"
FLASH_OUT="$A/results/paper2_exec/qwen38-flash"
CHAIN_LOG="$A/results/paper2_exec_small_9b_then_flash.log"
POLL_SEC="${PAPER2_CHAIN_POLL_SEC:-60}"

mkdir -p "$NINE_OUT" "$FLASH_OUT" "$A/results"
exec > >(stdbuf -oL -eL tee -a "$CHAIN_LOG") 2>&1

echo "===== paper2 SMALL chain waiter start $(date -Is) ====="
echo "wait: $NINE_OUT/LANE_COMPLETE or CHECKPOINT 57/57; then Flash"
echo "policy: SMALL only; no Flash on BUDGET_STOP; no Claude/GPT"

nine_budget_stop() {
  [ -f "$NINE_OUT/BUDGET_STOP.txt" ]
}

nine_complete() {
  if [ -f "$NINE_OUT/LANE_COMPLETE" ]; then
    return 0
  fi
  # Fallback if older runner finished without marker: 57 unique checkpoint rows + no live runner.
  local n=0
  if [ -f "$NINE_OUT/CHECKPOINT.jsonl" ]; then
    n=$(NINE_OUT="$NINE_OUT" python3 - <<'PY'
import json, os
from pathlib import Path
p = Path(os.environ["NINE_OUT"]) / "CHECKPOINT.jsonl"
latest = {}
for line in p.read_text().splitlines():
    if not line.strip():
        continue
    o = json.loads(line)
    latest[(o["task"], o["leg"])] = o
print(len(latest))
PY
)
  fi
  if [ "$n" -ge 57 ]; then
    if ! pgrep -f 'scripts/paper2_exec_run.sh' >/dev/null 2>&1 \
      && ! pgrep -f 'run_mypcbench.py --backend qemu' >/dev/null 2>&1; then
      return 0
    fi
  fi
  return 1
}

nine_runner_alive() {
  # Current 9B tmux uses paper2_exec_run.sh with SLUG qwen35-9b in env / log activity.
  pgrep -af 'paper2_exec_run.sh' 2>/dev/null | grep -q . || return 1
  return 0
}

while true; do
  if nine_budget_stop; then
    echo "ABORT: 9B BUDGET_STOP present — not starting Flash (no failover) $(date -Is)"
    exit 75
  fi
  if nine_complete; then
    echo "9B complete detected $(date -Is)"
    break
  fi
  ckpt_n=0
  [ -f "$NINE_OUT/CHECKPOINT.jsonl" ] && ckpt_n=$(wc -l < "$NINE_OUT/CHECKPOINT.jsonl" | tr -d ' ')
  echo "waiting 9B… ckpt_lines=$ckpt_n runner=$(nine_runner_alive && echo yes || echo no) $(date -Is)"
  sleep "$POLL_SEC"
done

if [ -f "$FLASH_OUT/LANE_COMPLETE" ]; then
  echo "Flash already LANE_COMPLETE — nothing to do"
  exit 0
fi

# Ensure 9B processes are gone before taking QEMU ports.
for _ in 1 2 3 4 5 6 7 8 9 10; do
  if pgrep -f 'run_mypcbench.py --backend qemu' >/dev/null 2>&1; then
    echo "QEMU/agent still up — wait 30s"
    sleep 30
  else
    break
  fi
done

echo "===== start Flash SMALL $(date -Is) ====="
cd "$A"
bash scripts/paper2_exec_small_lane.sh qwen/qwen3.8-flash
echo "===== Flash wrapper returned $? $(date -Is) ====="
