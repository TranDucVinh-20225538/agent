#!/usr/bin/env bash
# Study 2 — one-family matrix lane (Flash | GPT | Claude).
# Sources funding bind (008…9dd), then study2_exec_run.sh (57 legs).
# Does not start Gate 0A smoke / SMALL / native LARGE lanes.
set -euo pipefail

A="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
H="$A/external/MyPCBench-main"
FAMILY="${1:?usage: $0 flash|gpt|claude}"

case "$FAMILY" in
  flash)
    MODEL="qwen/qwen3.8-flash"
    SLUG="study2-flash"
    ;;
  gpt)
    MODEL="openai/gpt-5.5"
    SLUG="study2-gpt"
    ;;
  claude)
    MODEL="anthropic/claude-opus-4.6"
    SLUG="study2-claude"
    ;;
  *)
    echo "usage: $0 flash|gpt|claude" >&2
    exit 2
    ;;
esac

cd "$H"
set -a
# shellcheck disable=SC1091
[ -f .env ] && source .env
# shellcheck disable=SC1091
source ./mypcbench-vm/env.sh
set +a

# Bind funded OpenRouter credential (scrubs SMALL).
# shellcheck disable=SC1091
source "$A/scripts/study2_bind_execution_key.sh"

export AGENT_ROOT="$A"
export STUDY2_FAMILY="$FAMILY"
export MODEL
export SLUG
export LANE=STUDY2
export OUT_ROOT="$A/results/paper2_exec/$SLUG"
export LOG="$A/results/paper2_exec_${SLUG}.log"
export STUDY2_CONTAINER="mypcbench-${SLUG}"

mkdir -p "$OUT_ROOT"
echo "START Study2 lane family=$FAMILY model=$MODEL out=$OUT_ROOT fingerprint=${STUDY2_EXECUTION_KEY_FINGERPRINT:-unset}"
echo "exec → scripts/study2_exec_run.sh (57 legs; generic OpenRouter bridge)"

exec bash "$A/scripts/study2_exec_run.sh"
