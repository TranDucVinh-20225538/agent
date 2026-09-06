#!/usr/bin/env bash
# Study 2 — full matrix entrypoint (171 legs).
# Order (locked): Flash → GPT-5.5 → Claude Opus 4.6 (57 each).
# Bind: scripts/study2_bind_execution_key.sh (008…9dd) inside each lane.
# Preflight (Round-57 plumbing): A balance + C universe/order (+ B evidence) before leg 1.
#
# Usage: bash scripts/study2_matrix.sh
# Does not modify prereg/protocol/roster. Sequential QEMU (shared hostfwd).
set -euo pipefail

A="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$A"

echo "===== Study2 matrix start $(date -Is) ====="
echo "schedule: flash → gpt → claude (57×3=171)"
echo "outs: results/paper2_exec/study2-{flash,gpt,claude}"

# Preflight bind once (lanes re-bind themselves).
# shellcheck disable=SC1091
source "$A/scripts/study2_bind_execution_key.sh"
echo "preflight fingerprint=$STUDY2_EXECUTION_KEY_FINGERPRINT"

# Round-57 integrity plumbing — fail closed before any Study 2 leg.
echo "===== Study2 Round-57 preflight $(date -Is) ====="
python3 "$A/scripts/study2_preflight_integrity.py"
echo "Round-57 preflight PASS — launching locked schedule"

for fam in flash gpt claude; do
  echo "===== Study2 family=$fam $(date -Is) ====="
  bash "$A/scripts/study2_matrix_lane.sh" "$fam"
done

echo "===== Study2 matrix complete $(date -Is) ====="
