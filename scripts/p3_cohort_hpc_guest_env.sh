#!/usr/bin/env bash
# Resolve the HPC guest stack. Sourced by Wave B.
# Drops node30 leftovers from .env (/mnt/data2/Vinh/...) when the file
# is not on this host. Does not invent firmware. Does not start an agent.
#
# Required after this file returns 0:
#   qemu-img, qemu-system-x86_64, MYPCBENCH_QCOW2, MYPCBENCH_OVMF_CODE,
#   MYPCBENCH_OVMF_VARS — all existing files / executables.
set -euo pipefail

: "${A:?A (AGENT_ROOT) must be set before sourcing p3_cohort_hpc_guest_env.sh}"
H="${H:-$A/external/MyPCBench-main}"

_drop_if_missing() {
  local var="$1"
  local val="${!var:-}"
  if [ -n "$val" ] && [ ! -e "$val" ]; then
    echo "drop missing $var=$val"
    unset "$var"
  fi
}

_first_dir() {
  local d
  for d in "$@"; do
    if [ -n "$d" ] && [ -d "$d" ]; then
      printf '%s' "$d"
      return 0
    fi
  done
  return 1
}

_first_file() {
  local f
  for f in "$@"; do
    if [ -n "$f" ] && [ -f "$f" ]; then
      printf '%s' "$f"
      return 0
    fi
  done
  return 1
}

_first_ovmf_pair() {
  local d code vars
  for d in "$@"; do
    [ -n "$d" ] && [ -d "$d" ] || continue
    for code in "$d"/OVMF_CODE_4M.fd "$d"/OVMF_CODE.fd "$d"/OVMF_CODE*.fd; do
      [ -f "$code" ] || continue
      case "$(basename "$code")" in
        *secboot*|*snakeoil*|*.ms.*) continue ;;
      esac
      vars="${code/CODE/VARS}"
      if [ -f "$vars" ]; then
        printf '%s\t%s' "$code" "$vars"
        return 0
      fi
    done
  done
  return 1
}

# .env / env.sh on this tree still carry node30 absolute paths.
_drop_if_missing MYPCBENCH_QCOW2
_drop_if_missing MYPCBENCH_OVMF_CODE
_drop_if_missing MYPCBENCH_OVMF_VARS
_drop_if_missing MYPCBENCH_QEMU_EXTRACTED

if [ -z "${MYPCBENCH_QEMU_EXTRACTED:-}" ]; then
  MYPCBENCH_QEMU_EXTRACTED="$(_first_dir \
    /data2/cmdir/home/toandq/MyPCBench/.opt/qemu \
    "${HOME}/MyPCBench/.opt/qemu" \
    "$A/../MyPCBench/.opt/qemu" \
    "$H/.opt/qemu" || true)"
  export MYPCBENCH_QEMU_EXTRACTED
fi

if [ -z "${MYPCBENCH_QCOW2:-}" ]; then
  MYPCBENCH_QCOW2="$(_first_file \
    "$H/mypcbench-vm/mypcbench.qcow2" \
    "$A/external/MyPCBench-main/mypcbench-vm/mypcbench.qcow2" \
    /data2/hpcshared/Vinh-/agent/external/MyPCBench-main/mypcbench-vm/mypcbench.qcow2 \
    /data2/hpcshared/Vinh/agent/external/MyPCBench-main/mypcbench-vm/mypcbench.qcow2 || true)"
  export MYPCBENCH_QCOW2
fi

# If CODE is unset (dropped), discover a live pair. Do not keep a dead override:
# env.py treats a set-but-missing CODE as fatal and will not search EXTRACTED.
if [ -z "${MYPCBENCH_OVMF_CODE:-}" ] || [ ! -f "${MYPCBENCH_OVMF_CODE:-}" ]; then
  unset MYPCBENCH_OVMF_CODE MYPCBENCH_OVMF_VARS
  _pair="$(_first_ovmf_pair \
    "$H/mypcbench-vm" \
    "${MYPCBENCH_QEMU_EXTRACTED:-}/usr/share/edk2/ovmf" \
    "${MYPCBENCH_QEMU_EXTRACTED:-}/usr/share/OVMF" \
    "${MYPCBENCH_QEMU_EXTRACTED:-}/usr/share/edk2-ovmf/x64" \
    /usr/share/OVMF \
    /usr/share/edk2/ovmf \
    /usr/share/edk2-ovmf/x64 \
    /usr/share/qemu/ovmf || true)"
  if [ -n "${_pair:-}" ]; then
    MYPCBENCH_OVMF_CODE="${_pair%%	*}"
    MYPCBENCH_OVMF_VARS="${_pair#*	}"
    export MYPCBENCH_OVMF_CODE MYPCBENCH_OVMF_VARS
  fi
fi

# shellcheck disable=SC1091
source "$A/scripts/qemu_datadir_wrap.sh"

_missing=()
command -v qemu-img >/dev/null || _missing+=("qemu-img")
command -v qemu-system-x86_64 >/dev/null || _missing+=("qemu-system-x86_64")
[ -f "${MYPCBENCH_QCOW2:-}" ] || _missing+=("MYPCBENCH_QCOW2=${MYPCBENCH_QCOW2:-unset}")
[ -f "${MYPCBENCH_OVMF_CODE:-}" ] || _missing+=("MYPCBENCH_OVMF_CODE=${MYPCBENCH_OVMF_CODE:-unset}")
[ -f "${MYPCBENCH_OVMF_VARS:-}" ] || _missing+=("MYPCBENCH_OVMF_VARS=${MYPCBENCH_OVMF_VARS:-unset}")

echo "guest.env AGENT_ROOT=$A"
echo "guest.env QCOW2=${MYPCBENCH_QCOW2:-}"
echo "guest.env OVMF_CODE=${MYPCBENCH_OVMF_CODE:-}"
echo "guest.env OVMF_VARS=${MYPCBENCH_OVMF_VARS:-}"
echo "guest.env EXTRACTED=${MYPCBENCH_QEMU_EXTRACTED:-}"
echo "guest.env qemu-img=$(command -v qemu-img || echo MISSING)"
echo "guest.env qemu-system=$(command -v qemu-system-x86_64 || echo MISSING)"

if [ "${#_missing[@]}" -gt 0 ]; then
  echo "TECHNICAL_ABORT missing: ${_missing[*]}"
  return 2 2>/dev/null || exit 2
fi
