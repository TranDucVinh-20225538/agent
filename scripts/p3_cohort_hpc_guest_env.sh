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

# Study 2 Flash: QEMU 8.2.2 TCG on node002/node004. The older
# .opt/qemu extract is incomplete (libvirglrenderer and more missing).
_QEMU82=/data2/cmdir/home/toandq/MyPCBench/.opt/qemu-8.2
if [ -d "$_QEMU82" ]; then
  export MYPCBENCH_QEMU_EXTRACTED="$_QEMU82"
elif [ -z "${MYPCBENCH_QEMU_EXTRACTED:-}" ]; then
  MYPCBENCH_QEMU_EXTRACTED="$(_first_dir \
    "${HOME}/MyPCBench/.opt/qemu-8.2" \
    "$A/../MyPCBench/.opt/qemu-8.2" || true)"
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

# Flash/env.py: -vnc :(PORT-5900). Display :1 is 5901 and is taken on
# node002. Pick a free display 20–90. Do not kill the Flash QEMU.
if [ -z "${MYPCBENCH_HOST_VNC_PORT:-}" ]; then
  MYPCBENCH_HOST_VNC_PORT="$(python3 - <<'PY'
import socket
import sys
for display in range(20, 91):
    port = 5900 + display
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("127.0.0.1", port))
    except OSError:
        s.close()
        continue
    s.close()
    print(port)
    sys.exit(0)
sys.exit(1)
PY
)" || MYPCBENCH_HOST_VNC_PORT=""
  export MYPCBENCH_HOST_VNC_PORT
fi

_missing=()
command -v qemu-img >/dev/null || _missing+=("qemu-img")
command -v qemu-system-x86_64 >/dev/null || _missing+=("qemu-system-x86_64")
[ -f "${MYPCBENCH_QCOW2:-}" ] || _missing+=("MYPCBENCH_QCOW2=${MYPCBENCH_QCOW2:-unset}")
[ -f "${MYPCBENCH_OVMF_CODE:-}" ] || _missing+=("MYPCBENCH_OVMF_CODE=${MYPCBENCH_OVMF_CODE:-unset}")
[ -f "${MYPCBENCH_OVMF_VARS:-}" ] || _missing+=("MYPCBENCH_OVMF_VARS=${MYPCBENCH_OVMF_VARS:-unset}")
[ -n "${MYPCBENCH_HOST_VNC_PORT:-}" ] || _missing+=("MYPCBENCH_HOST_VNC_PORT (no free display 20-90)")

_hn="$(hostname -s 2>/dev/null || hostname || echo unknown)"
echo "guest.env host=$_hn"
case "$_hn" in
  node002|node004) ;;
  *) _missing+=("host=$_hn (Study 2 QEMU 8.2 TCG is node002/node004 only; not bright92)") ;;
esac

_real="${MYPCBENCH_QEMU_EXTRACTED:-}/usr/bin/qemu-system-x86_64"
_ver=""
if [ -x "$_real" ]; then
  _ver="$("$_real" --version 2>&1 | head -n 1 || true)"
fi
echo "guest.env qemu-version=${_ver:-MISSING}"
case "${_ver}" in
  *8.2.2*) ;;
  *) _missing+=("qemu-version=${_ver:-MISSING} (need 8.2.2)") ;;
esac

if [ -x "$_real" ] && command -v ldd >/dev/null; then
  _nf="$(ldd "$_real" 2>&1 | grep 'not found' || true)"
  if [ -n "$_nf" ]; then
    echo "guest.env ldd-not-found:"
    echo "$_nf"
    _missing+=("ldd not found: $(printf '%s' "$_nf" | tr '\n' ';')")
  fi
fi

echo "guest.env AGENT_ROOT=$A"
echo "guest.env QCOW2=${MYPCBENCH_QCOW2:-}"
echo "guest.env OVMF_CODE=${MYPCBENCH_OVMF_CODE:-}"
echo "guest.env OVMF_VARS=${MYPCBENCH_OVMF_VARS:-}"
echo "guest.env EXTRACTED=${MYPCBENCH_QEMU_EXTRACTED:-}"
echo "guest.env qemu-img=$(command -v qemu-img || echo MISSING)"
echo "guest.env qemu-system=$(command -v qemu-system-x86_64 || echo MISSING)"
echo "guest.env VNC_PORT=${MYPCBENCH_HOST_VNC_PORT:-unset} (display $((${MYPCBENCH_HOST_VNC_PORT:-5900} - 5900)))"
echo "guest.env REAL_QEMU=${PREFIX:-$MYPCBENCH_QEMU_EXTRACTED}/usr/bin/qemu-system-x86_64"

if [ "${#_missing[@]}" -gt 0 ]; then
  echo "TECHNICAL_ABORT missing: ${_missing[*]}"
  return 2 2>/dev/null || exit 2
fi
