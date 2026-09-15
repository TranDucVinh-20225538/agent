#!/usr/bin/env bash
# Wait for Flash lane completion, then STOP.
#
# Does NOT launch GPT. Default: PAPER2_GPT_AUTOSTART=0.
# Historical name kept so old tmux/nohup invocations still hit this script and
# cannot resurrect paper2_exec_gpt_openrouter.sh.
#
# Policy (2026-09-06): GPT HARD BLOCKED until Gate 0 + frozen ResponseStateAdapter
# + EXECUTION_MANIFEST amendment + explicit human approval.
set -euo pipefail

A="${AGENT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
FLASH_OUT="$A/results/paper2_exec/qwen38-flash"
GPT_OUT="$A/results/paper2_exec/gpt-5.5"
CHAIN_LOG="$A/results/paper2_exec_flash_then_gpt_small.log"
POLL_SEC="${PAPER2_CHAIN_POLL_SEC:-60}"
# Kill-switch: must be explicitly "1" to even consider GPT (still blocked below).
PAPER2_GPT_AUTOSTART="${PAPER2_GPT_AUTOSTART:-0}"

mkdir -p "$FLASH_OUT" "$GPT_OUT" "$A/results"
# Persistent on-disk block (survives env forgetting the kill-switch).
touch "$GPT_OUT/DO_NOT_AUTO_START_GPT"

exec > >(stdbuf -oL -eL tee -a "$CHAIN_LOG") 2>&1

echo "===== wait Flash → (no GPT autostart) $(date -Is) ====="
echo "PAPER2_GPT_AUTOSTART=$PAPER2_GPT_AUTOSTART (default 0; GPT launch removed from this script)"

flash_complete() {
  if [ -f "$FLASH_OUT/LANE_COMPLETE" ]; then return 0; fi
  local n=0
  if [ -f "$FLASH_OUT/CHECKPOINT.jsonl" ]; then
    n=$(FLASH_OUT="$FLASH_OUT" python3 - <<'PY'
import json, os
from pathlib import Path
p = Path(os.environ["FLASH_OUT"]) / "CHECKPOINT.jsonl"
latest = {}
for line in p.read_text().splitlines():
    if line.strip():
        o = json.loads(line)
        latest[(o["task"], o["leg"])] = o
print(len(latest))
PY
)
  fi
  # Avoid matching unrelated cmdline text: require the runner path as its own argv token.
  if [ "$n" -ge 57 ] && ! pgrep -f '(^|/)scripts/paper2_exec_run\.sh( |$)' >/dev/null 2>&1; then
    return 0
  fi
  return 1
}

while true; do
  if [ -f "$FLASH_OUT/BUDGET_STOP.txt" ]; then
    echo "ABORT: Flash BUDGET_STOP $(date -Is)"
    exit 75
  fi
  if flash_complete; then
    echo "Flash complete $(date -Is)"
    break
  fi
  n=0
  [ -f "$FLASH_OUT/CHECKPOINT.jsonl" ] && n=$(wc -l < "$FLASH_OUT/CHECKPOINT.jsonl" | tr -d ' ')
  echo "waiting Flash… ckpt_lines=$n $(date -Is)"
  sleep "$POLL_SEC"
done

date -Is > "$FLASH_OUT/FLASH_COMPLETE"
echo "wrote $FLASH_OUT/FLASH_COMPLETE"
if [ ! -f "$FLASH_OUT/LANE_COMPLETE" ]; then
  # Soft marker — Flash runner may also write LANE_COMPLETE; do not overwrite if present.
  date -Is > "$FLASH_OUT/LANE_COMPLETE" || true
fi

echo "===== Flash done; GPT NOT started (HARD BLOCK) $(date -Is) ====="
echo "  DO_NOT_AUTO_START_GPT=$GPT_OUT/DO_NOT_AUTO_START_GPT"
echo "  To run GPT later: Gate0 → adapter freeze → manifest amendment → explicit approval"
echo "  Then: PAPER2_GPT_AUTOSTART is irrelevant here — launch GPT manually after unblocking."

# Even if someone sets PAPER2_GPT_AUTOSTART=1, this script must not launch GPT.
if [ "$PAPER2_GPT_AUTOSTART" = "1" ]; then
  echo "NOTE: PAPER2_GPT_AUTOSTART=1 ignored — launch path excised; use a future approved entrypoint." >&2
fi
exit 0
