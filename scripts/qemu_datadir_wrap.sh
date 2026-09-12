#!/usr/bin/env bash
# Point a relocated QEMU at its datadir (-L) and bundled libs.
# Study 2 Flash on HPC used .opt/qemu-8.2 + LD_LIBRARY_PATH, not the
# incomplete RPM extract at .opt/qemu (missing libvirglrenderer etc.).
#
# Source from guest/stage scripts. Do not source on node30 (system QEMU).
set -euo pipefail

_qemu82=/data2/cmdir/home/toandq/MyPCBench/.opt/qemu-8.2
_qemu_old=/data2/cmdir/home/toandq/MyPCBench/.opt/qemu

if [ -z "${MYPCBENCH_QEMU_EXTRACTED:-}" ]; then
  for cand in \
    "$_qemu82" \
    "$_qemu_old" \
    "${HOME}/MyPCBench/.opt/qemu-8.2" \
    "${HOME}/MyPCBench/.opt/qemu" \
    "${A:-}/../MyPCBench/.opt/qemu-8.2" \
    "${A:-}/../MyPCBench/.opt/qemu"
  do
    if [ -d "$cand/usr/share/qemu" ] || [ -x "$cand/wrap/qemu-system-x86_64" ]; then
      export MYPCBENCH_QEMU_EXTRACTED="$cand"
      break
    fi
  done
fi

PREFIX="${MYPCBENCH_QEMU_EXTRACTED:-}"
export LD_LIBRARY_PATH="${PREFIX}/usr/lib/x86_64-linux-gnu:${PREFIX}/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export QEMU_MODULE_DIR="${PREFIX}/usr/lib/x86_64-linux-gnu/qemu"

if [ -z "${QEMU_DATADIR:-}" ] && [ -n "$PREFIX" ]; then
  QEMU_DATADIR="$PREFIX/usr/share/qemu"
fi
export QEMU_DATADIR="${QEMU_DATADIR:-}"

if [ -z "$QEMU_DATADIR" ] || [ ! -f "$QEMU_DATADIR/vgabios-virtio.bin" ]; then
  echo "FAIL: QEMU datadir missing vgabios-virtio.bin (QEMU_DATADIR=${QEMU_DATADIR:-unset})" >&2
  return 1 2>/dev/null || exit 1
fi
if [ ! -f "$QEMU_DATADIR/kvmvapic.bin" ]; then
  echo "FAIL: $QEMU_DATADIR/kvmvapic.bin missing" >&2
  return 1 2>/dev/null || exit 1
fi

# Binary only. The 8.2 wrap/ script remaps VNC, but if we exec it
# after already injecting -L it skips that remap and keeps -vnc :1.
REAL_QEMU="${PREFIX}/usr/bin/qemu-system-x86_64"
if [ ! -x "$REAL_QEMU" ]; then
  echo "FAIL: qemu-system-x86_64 not found at $REAL_QEMU" >&2
  return 1 2>/dev/null || exit 1
fi

WRAP="${A:-.}/results/.qemu-wrap"
mkdir -p "$WRAP"
cat > "$WRAP/qemu-system-x86_64" <<EOF
#!/usr/bin/env bash
# Study 2 QEMU 8.2: bundled libs, -L datadir, VNC → unix socket.
# Remap VNC even when -L is already on the command line.
export LD_LIBRARY_PATH='${PREFIX}/usr/lib/x86_64-linux-gnu:${PREFIX}/lib/x86_64-linux-gnu'"\${LD_LIBRARY_PATH:+:\$LD_LIBRARY_PATH}"
export QEMU_MODULE_DIR='${PREFIX}/usr/lib/x86_64-linux-gnu/qemu'
real='$REAL_QEMU'
datadir='$QEMU_DATADIR'
has_L=0
skip=
args=()
for a in "\$@"; do
  if [ -n "\$skip" ]; then
    if [ "\$skip" = vnc ]; then
      sock="/tmp/mypcbench-waveb-vnc-\$\$.sock"
      rm -f "\$sock"
      args+=("unix:\$sock")
    else
      args+=("\$a")
    fi
    skip=
    continue
  fi
  case "\$a" in
    -L) has_L=1; args+=("\$a"); skip=L ;;
    -vnc) args+=("\$a"); skip=vnc ;;
    *) args+=("\$a") ;;
  esac
done
if [ "\$has_L" = 0 ]; then
  args+=(-L "\$datadir")
fi
exec "\$real" "\${args[@]}"
EOF
chmod +x "$WRAP/qemu-system-x86_64"

if [ -x "$PREFIX/usr/bin/qemu-img" ]; then
  export PATH="$WRAP:$PREFIX/usr/bin:$PATH"
else
  export PATH="$WRAP:$PATH"
fi

echo "QEMU wrap: real=$REAL_QEMU"
echo "QEMU -L $QEMU_DATADIR"
echo "QEMU PREFIX=$PREFIX"
echo "QEMU which=$(command -v qemu-system-x86_64)"
