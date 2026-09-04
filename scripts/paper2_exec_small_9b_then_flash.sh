#!/usr/bin/env bash
# Fresh SMALL chain: Qwen 9B then Flash (same host, sequential QEMU).
# Prefer wait script if 9B is already running: paper2_exec_wait_9b_then_flash.sh
set -euo pipefail
A="${AGENT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$A"
echo "===== SMALL chain 9B→Flash start $(date -Is) ====="
bash scripts/paper2_exec_small_lane.sh qwen/qwen3.5-9b
if [ -f "$A/results/paper2_exec/qwen35-9b/BUDGET_STOP.txt" ]; then
  echo "9B budget-stop — not starting Flash"
  exit 75
fi
bash scripts/paper2_exec_small_lane.sh qwen/qwen3.8-flash
echo "===== SMALL chain done $(date -Is) ====="
