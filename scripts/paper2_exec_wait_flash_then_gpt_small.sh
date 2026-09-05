#!/usr/bin/env bash
# After Flash LANE_COMPLETE → GPT on OpenRouter SMALL until budget-stop.
# Does not auto-start LARGE/native GPT.
set -euo pipefail

A="${AGENT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
FLASH_OUT="$A/results/paper2_exec/qwen38-flash"
GPT_OUT="$A/results/paper2_exec/gpt-5.5"
CHAIN_LOG="$A/results/paper2_exec_flash_then_gpt_small.log"
POLL_SEC="${PAPER2_CHAIN_POLL_SEC:-60}"

mkdir -p "$FLASH_OUT" "$GPT_OUT" "$A/results"
exec > >(stdbuf -oL -eL tee -a "$CHAIN_LOG") 2>&1

echo "===== wait Flash → GPT(SMALL openrouter) $(date -Is) ====="
echo "no auto LARGE; stop on BUDGET_STOP"

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
  if [ "$n" -ge 57 ] && ! pgrep -f 'scripts/paper2_exec_run.sh' >/dev/null 2>&1; then
    return 0
  fi
  return 1
}

while true; do
  if [ -f "$FLASH_OUT/BUDGET_STOP.txt" ]; then
    echo "ABORT: Flash BUDGET_STOP — not starting GPT $(date -Is)"
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

# Wait for QEMU from Flash to release ports
for _ in 1 2 3 4 5 6 7 8 9 10; do
  if pgrep -f 'run_mypcbench.py --backend qemu' >/dev/null 2>&1; then
    echo "QEMU still up — wait 30s"
    sleep 30
  else
    break
  fi
done

if [ -f "$GPT_OUT/LANE_COMPLETE" ]; then
  echo "GPT already LANE_COMPLETE — done"
  exit 0
fi

echo "===== start GPT OpenRouter SMALL $(date -Is) ====="
cd "$A"
set +e
bash scripts/paper2_exec_gpt_openrouter.sh SMALL
rc=$?
set -e
if [ -f "$GPT_OUT/BUDGET_STOP.txt" ] || [ "$rc" -eq 75 ]; then
  echo "GPT SMALL budget-stop rc=$rc — NOT starting LARGE. Resume later with native/LARGE when you OK." | tee -a "$GPT_OUT/RESUME_WITH_LARGE_LATER.txt"
  date -Is | tee -a "$GPT_OUT/RESUME_WITH_LARGE_LATER.txt"
  exit 75
fi
echo "===== GPT SMALL wrapper returned $rc $(date -Is) ====="
exit "$rc"
