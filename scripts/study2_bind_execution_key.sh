#!/usr/bin/env bash
# Study 2 — bind execution OpenRouter credential for main-matrix process trees.
#
# Funding gate: bill sk-or-v1-008…9dd only (OPENROUTER_API_KEY_LARGE in MyPCBench .env).
# SMALL (c86…37a) is forbidden for Study 2 main-matrix OpenRouter calls.
#
# Usage:
#   source scripts/study2_bind_execution_key.sh          # export into current shell
#   bash scripts/study2_bind_execution_key.sh verify     # bind in subshell + live check → exit 0/1
#
# Does not start matrix legs. Does not print full secrets.
set -euo pipefail

A="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
H="$A/external/MyPCBench-main"
ENV_FILE="${STUDY2_ENV_FILE:-$H/.env}"
REQUIRED_PREFIX3="008"
FORBIDDEN_SMALL_PREFIX3="c86"

_study2_die() { echo "STUDY2_BIND_FAIL: $*" >&2; return 1 2>/dev/null || exit 1; }

_study2_mask() {
  local k="$1"
  [[ "$k" == sk-or-v1-* ]] || { echo "invalid"; return; }
  local body="${k#sk-or-v1-}"
  echo "sk-or-v1-${body:0:3}…${body: -3}"
}

_study2_prefix3() {
  local k="$1"
  local body="${k#sk-or-v1-}"
  echo "${body:0:3}"
}

_study2_load_and_bind() {
  [[ -f "$ENV_FILE" ]] || _study2_die "missing env file: $ENV_FILE"

  # Load file without polluting unrelated exports into caller until we bind.
  # shellcheck disable=SC1090
  set -a
  # shellcheck disable=SC1091
  source "$ENV_FILE"
  set +a

  : "${OPENROUTER_API_KEY_LARGE:?OPENROUTER_API_KEY_LARGE unset in $ENV_FILE}"

  local large="$OPENROUTER_API_KEY_LARGE"
  [[ "$large" == sk-or-v1-* ]] || _study2_die "LARGE is not an OpenRouter sk-or-v1 key"
  local p3
  p3="$(_study2_prefix3 "$large")"
  [[ "$p3" == "$REQUIRED_PREFIX3" ]] || _study2_die "LARGE prefix3=$p3 want $REQUIRED_PREFIX3 (funding key)"

  # Bind runtime slots used by OpenRouter chat-completions transport / generic executor.
  export OPENROUTER_API_KEY="$large"
  export OPENAI_API_KEY="$large"
  export OPENAI_BASE_URL="${OPENAI_BASE_URL:-https://openrouter.ai/api/v1}"
  export STUDY2_EXECUTION_KEY_SOURCE="OPENROUTER_API_KEY_LARGE"
  export STUDY2_EXECUTION_KEY_FINGERPRINT="$(_study2_mask "$large")"
  export STUDY2_EXECUTION_LANE="OPENROUTER_FUNDED"
  export AGENT_ROOT="$A"

  # Hygiene: remove SMALL and the named LARGE slot so children cannot "accidentally"
  # re-bind SMALL; only OPENROUTER_API_KEY / OPENAI_API_KEY remain.
  unset OPENROUTER_API_KEY_SMALL OPENROUTER_API_KEY_LARGE || true
  # Native Anthropic must not silently divert Claude Study 2 OpenRouter traffic.
  unset ANTHROPIC_API_KEY ANTHROPIC_API_KEY_BACKUP || true
  # Scrub Gate 0A smoke namespace — historical/qualification only; not Study 2 matrix.
  unset GATE0A_FAMILY GATE0A_OUT GATE0A_MODEL GATE0A_TOKEN GATE0A_TOKEN_PATH \
        GATE0A_CONTAINER GATE0A_MAX_STEPS GATE0A_VERSION GATE0A_FREEZE_SHA \
        GATE0A_HTTP_TIMEOUT || true

  # Refuse if SMALL somehow still equals runtime key (should be unset).
  if [[ -n "${OPENROUTER_API_KEY_SMALL:-}" ]]; then
    _study2_die "OPENROUTER_API_KEY_SMALL still set after bind"
  fi
  if [[ -n "${GATE0A_FAMILY:-}" || -n "${GATE0A_OUT:-}" || -n "${GATE0A_MODEL:-}" ]]; then
    _study2_die "Gate 0A env still set after bind scrub"
  fi
  local rt_p3
  rt_p3="$(_study2_prefix3 "$OPENROUTER_API_KEY")"
  [[ "$rt_p3" != "$FORBIDDEN_SMALL_PREFIX3" ]] || _study2_die "runtime key is SMALL ($FORBIDDEN_SMALL_PREFIX3)"
  [[ "$rt_p3" == "$REQUIRED_PREFIX3" ]] || _study2_die "runtime key prefix3=$rt_p3 want $REQUIRED_PREFIX3"

  echo "STUDY2_BIND_OK fingerprint=$STUDY2_EXECUTION_KEY_FINGERPRINT source=$STUDY2_EXECUTION_KEY_SOURCE SMALL=unset"
}

_study2_live_verify() {
  python3 - <<'PY'
import json, os, urllib.request, sys
from datetime import datetime, timezone

key = os.environ.get("OPENROUTER_API_KEY") or ""
fp = os.environ.get("STUDY2_EXECUTION_KEY_FINGERPRINT") or ""
if not key.startswith("sk-or-v1-008"):
    print("VERIFY_FAIL: OPENROUTER_API_KEY does not start with sk-or-v1-008", file=sys.stderr)
    sys.exit(2)
if os.environ.get("OPENROUTER_API_KEY_SMALL"):
    print("VERIFY_FAIL: OPENROUTER_API_KEY_SMALL still set (SMALL fallback risk)", file=sys.stderr)
    sys.exit(2)
if key != (os.environ.get("OPENAI_API_KEY") or ""):
    print("VERIFY_FAIL: OPENAI_API_KEY != OPENROUTER_API_KEY after bind", file=sys.stderr)
    sys.exit(2)

req = urllib.request.Request(
    "https://openrouter.ai/api/v1/key",
    headers={"Authorization": f"Bearer {key}"},
)
with urllib.request.urlopen(req, timeout=45) as resp:
    data = json.load(resp).get("data", {})

body = key[len("sk-or-v1-"):]
mask = f"sk-or-v1-{body[:3]}…{body[-3:]}"
remaining = float(data.get("limit_remaining") or 0)
out = {
    "checked_at_utc": datetime.now(timezone.utc).isoformat(),
    "verdict": "PASS" if remaining >= 100.0 and body[:3] == "008" else "FAIL",
    "runtime_fingerprint": mask,
    "env_fingerprint": fp,
    "live_label": data.get("label"),
    "limit": data.get("limit"),
    "limit_remaining": data.get("limit_remaining"),
    "usage": data.get("usage"),
    "OPENROUTER_API_KEY_SMALL_set": bool(os.environ.get("OPENROUTER_API_KEY_SMALL")),
    "STUDY2_EXECUTION_KEY_SOURCE": os.environ.get("STUDY2_EXECUTION_KEY_SOURCE"),
    "criteria": {
        "fingerprint_008": body[:3] == "008",
        "remaining_ge_100": remaining >= 100.0,
        "no_small_env": not bool(os.environ.get("OPENROUTER_API_KEY_SMALL")),
        "openai_mirrors_openrouter": True,
    },
}
print(json.dumps(out, indent=2))
if out["verdict"] != "PASS":
    sys.exit(1)
PY
}

MODE="${1:-}"
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  # Executed as script
  if [[ "${MODE}" == "verify" ]]; then
    _study2_load_and_bind
    _study2_live_verify
  elif [[ -z "${MODE}" ]]; then
    echo "usage: source $0   OR   bash $0 verify" >&2
    exit 2
  else
    echo "unknown mode: $MODE" >&2
    exit 2
  fi
else
  # Sourced
  _study2_load_and_bind
fi
