#!/usr/bin/env bash
# P4-B Phase 3 Flash observability pilot (HPC).
# B01–B03 only. Cap $30. SMALL OpenRouter lane. No GPT/Claude.
set -euo pipefail
A="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$A"

if [ -f "$A/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$A/.env"
  set +a
fi
if [ -f "$A/external/MyPCBench-main/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$A/external/MyPCBench-main/.env"
  set +a
fi

if [ -n "${OPENROUTER_API_KEY_SMALL:-}" ]; then
  export OPENROUTER_API_KEY="$OPENROUTER_API_KEY_SMALL"
fi

unset ANTHROPIC_API_KEY OPENAI_API_KEY OPENROUTER_API_KEY_LARGE || true

if [ -z "${OPENROUTER_API_KEY:-}" ]; then
  echo "FAIL: OPENROUTER_API_KEY / OPENROUTER_API_KEY_SMALL unset" >&2
  exit 2
fi
if [[ "${OPENROUTER_API_KEY}" == sk-proj-* ]]; then
  echo "FAIL: looks like a GPT key; SMALL OpenRouter required" >&2
  exit 2
fi

export PYTHONUNBUFFERED=1
python3 "$A/paper/paper4_measurement/instrument/p4b_flash_pilot.py" --check
python3 "$A/paper/paper4_measurement/instrument/p4b_flash_pilot.py"
