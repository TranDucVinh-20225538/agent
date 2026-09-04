#!/usr/bin/env bash
# Paper 2 — dry-run routing + shell plan (NO agent, NO keys printed).
# Usage: from repo root, after sourcing host env (names only checked).
set -euo pipefail

A="${AGENT_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
cd "$A"

die() { echo "FAIL: $*" >&2; exit 1; }
ok() { echo "OK: $*"; }

test -f out/paper2_analysis_universe.json || die "missing analysis universe"
test -f out/paper2_cell_order.json || die "missing cell order"
test -f paper/paper2_counterfactual_eval/EXECUTION_MANIFEST.md || die "missing manifest"
test -f cf/paper2_interventions.json || die "missing interventions"

python3 - <<'PY'
import json
from pathlib import Path

au = json.loads(Path("out/paper2_analysis_universe.json").read_text())
co = json.loads(Path("out/paper2_cell_order.json").read_text())
T = set(au["tasks"])
order = co["order"]
assert set(order) == T, (sorted(T - set(order)), sorted(set(order) - T))
assert len(order) == 25
assert au["legs"]["total"] == 228
assert not any("f024" in t for t in order), "f024 must be absent from cell_order"
multi = set(au["multi_i_both_pass"])
assert len(multi) == 7

# Expand to 57 legs/model: G0, G1, and G2 iff multi-I
legs = []
for task in order:
    legs.append((task, "G0"))
    legs.append((task, "G1"))
    if task in multi:
        legs.append((task, "G2"))
assert len(legs) == 57, len(legs)

models = [
    ("qwen/qwen3.5-9b", "SMALL"),
    ("qwen/qwen3.8-flash", "SMALL"),
    ("claude-opus-4-6", "LARGE"),
    ("gpt-5.5", "LARGE"),
]
total = 0
for m, lane in models:
    total += 57
print(f"dry-run cells/model=57 models=4 total_legs={total}")
assert total == 228
print(f"cell_order_first={order[0]} cell_order_last={order[-1]}")
print(f"multi_i={sorted(multi)}")
print("DRY_RUN_ROUTING_OK")
PY

echo "----- env var NAMES present (values never printed) -----"
for v in OPENROUTER_API_KEY_SMALL OPENROUTER_API_KEY_LARGE ANTHROPIC_API_KEY OPENAI_API_KEY OPENROUTER_API_KEY; do
  if [ -n "${!v:-}" ]; then
    ok "$v is set (len=${#v} name-only; value hidden)"
  else
    echo "MISS: $v not set"
  fi
done

echo "----- lane binding rules -----"
cat <<'EOF'
SMALL lane: export OPENROUTER_API_KEY="$OPENROUTER_API_KEY_SMALL"
            unset ANTHROPIC_API_KEY OPENAI_API_KEY OPENROUTER_API_KEY_LARGE
            models: qwen/qwen3.5-9b then qwen/qwen3.8-flash

LARGE lane: unset OPENROUTER_API_KEY_SMALL
            Claude: ANTHROPIC_API_KEY required; do not set OPENROUTER for Claude
            GPT:    OPENAI_API_KEY required
            optional OPENROUTER_API_KEY_LARGE only if a wrapper needs it — never for Qwen

NO silent failover: if SMALL exhausted → stop; do not export LARGE into SMALL jobs.
EOF

echo "----- suggested result roots -----"
echo "results/paper2_exec/qwen35-9b/"
echo "results/paper2_exec/qwen38-flash/"
echo "results/paper2_exec/claude-opus-4-6/"
echo "results/paper2_exec/gpt-5.5/"

echo "DRY_RUN_COMPLETE (no agent started)"
