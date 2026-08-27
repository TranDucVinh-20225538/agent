#!/usr/bin/env bash
# After 35B-A3B: size-ablation 9B then exploratory Qwen3.8-Flash.
# Each is f001 then f003, base then CF. One shot. Do not overwrite 35B-A3B dirs.
set -euo pipefail
A="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
H="$A/external/MyPCBench-main"
cd "$A"

set -a
# shellcheck disable=SC1091
source "$H/.env"
set +a

export STAGE4_QWEN_TASKS=f001,f003
export STAGE4_WRITE_TASKS=f001,f003
export STAGE4_REQUIRE_F001_DONE=0
export OPENAI_BASE_URL=https://openrouter.ai/api/v1

run_lane() {
  local tag="$1"
  local model="$2"
  echo "===== lane $tag model=$model start $(date -Is) ====="
  export STAGE4_TAG="$tag"
  export MYPCBENCH_QWEN_MODEL="$model"
  set +e
  bash "$A/scripts/stage4_qwen_openrouter_run.sh"
  local rc=$?
  set -e
  echo "===== lane $tag exit=$rc $(date -Is) ====="
  return 0
}

run_lane qwen359b qwen/qwen3.5-9b
run_lane qwen38flash qwen/qwen3.8-flash
echo "===== 9B then Flash stop $(date -Is) ====="
echo "35B-A3B dirs untouched. Flash is exploratory; no extra retries."
