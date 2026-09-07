#!/usr/bin/env bash
# Preflight: native OpenAI GPT Responses API multi-turn + tool shape + QEMU pin.
# Does NOT spend a Paper2 analysis cell. No secrets printed.
set -euo pipefail
A="${AGENT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
H="$A/external/MyPCBench-main"
cd "$H"
set -a
# shellcheck disable=SC1091
[ -f .env ] && source .env
# shellcheck disable=SC1091
source ./mypcbench-vm/env.sh
set +a

: "${OPENAI_API_KEY:?OPENAI_API_KEY required for native GPT preflight}"
# Ensure we are NOT pointed at OpenRouter
unset OPENROUTER_API_KEY OPENROUTER_API_KEY_SMALL OPENROUTER_API_KEY_LARGE OPENAI_BASE_URL || true
if [[ "${OPENAI_API_KEY}" == sk-or-* ]]; then
  echo "FAIL: OPENAI_API_KEY looks like OpenRouter — refuse native preflight" >&2
  exit 2
fi

export PATH="$H/.venv/bin:$PATH"
export PYTHONPATH="$H/agent-harness${PYTHONPATH:+:$PYTHONPATH}"

echo "===== Paper2 GPT native preflight $(date -Is) ====="
echo "OPENAI_API_KEY=set OPENAI_BASE_URL=unset (native)"
echo "qcow2=${MYPCBENCH_QCOW2:-unset}"
test -f "${MYPCBENCH_QCOW2:?}" || { echo "FAIL: qcow2 missing"; exit 2; }

python3 - <<'PY'
"""2-turn Responses API smoke: previous_response_id must work; tools accepted."""
import os, sys
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])  # no base_url → native
model = os.environ.get("MYPCBENCH_OPENAI_MODEL", "gpt-5.5")
tools = [
    {"type": "computer"},
    {"type": "shell", "environment": {"type": "local"}},
]

print(f"smoke model={model} tools={[t['type'] for t in tools]}")

# Turn 1
r1 = client.responses.create(
    model=model,
    tools=tools,
    input=[{
        "role": "user",
        "content": [{"type": "input_text", "text": "Reply with exactly: PING1. Do not call tools."}],
    }],
    store=True,
)
assert getattr(r1, "id", None), "turn1 missing response.id"
print(f"turn1_ok id={r1.id[:16]}…")

# Turn 2 — must accept previous_response_id (OpenRouter fails here)
r2 = client.responses.create(
    model=model,
    tools=tools,
    previous_response_id=r1.id,
    input=[{
        "role": "user",
        "content": [{"type": "input_text", "text": "Reply with exactly: PING2. Do not call tools."}],
    }],
    store=True,
)
assert getattr(r2, "id", None), "turn2 missing response.id"
print(f"turn2_ok id={r2.id[:16]}… previous_response_id ACCEPTED")

# Inspect output item types (harness reads message/output_text, computer_call, etc.)
types = []
for item in getattr(r2, "output", None) or []:
    types.append(getattr(item, "type", type(item).__name__))
print(f"turn2_output_types={types}")
print("SMOKE_RESPONSES_OK")
PY

# QEMU accessibility: confirm overlay create works (no full agent)
python3 - <<'PY'
import os, subprocess, tempfile
from pathlib import Path
qcow = Path(os.environ["MYPCBENCH_QCOW2"])
assert qcow.is_file(), qcow
# qemu-img info (no boot) — proves tooling + image readable
r = subprocess.run(
    ["qemu-img", "info", str(qcow)],
    capture_output=True, text=True, timeout=60,
)
print(r.stdout.splitlines()[0] if r.stdout else r.stderr[:200])
assert r.returncode == 0, r.stderr
print("SMOKE_QCOW2_OK")
PY

echo "===== PREFLIGHT_OK $(date -Is) ====="
