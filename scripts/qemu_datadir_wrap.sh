#!/usr/bin/env bash
# Point a relocated QEMU at its extracted datadir via -L.
# env.py launches `qemu-system-x86_64` with no -L; HPC 57951 died on
# romfile vgabios-virtio.bin even though the file lived under
# .opt/qemu/usr/share/qemu/.
#
# Source from stage4_qwen_run.sh. Do not source on node30 (system QEMU).
set -euo pipefail

_qemu_extracted_default=/data2/cmdir/home/toandq/MyPCBench/.opt/qemu

if [ -z "${MYPCBENCH_QEMU_EXTRACTED:-}" ]; then
  for cand in \
    "$_qemu_extracted_default" \
    "${HOME}/MyPCBench/.opt/qemu" \
    "${A:-}/../MyPCBench/.opt/qemu"
  do
    if [ -d "$cand/usr/share/qemu" ]; then
      export MYPCBENCH_QEMU_EXTRACTED="$cand"
      break
    fi
  done
fi

if [ -z "${QEMU_DATADIR:-}" ] && [ -n "${MYPCBENCH_QEMU_EXTRACTED:-}" ]; then
  QEMU_DATADIR="$MYPCBENCH_QEMU_EXTRACTED/usr/share/qemu"
fi
export QEMU_DATADIR="${QEMU_DATADIR:-}"

if [ -z "$QEMU_DATADIR" ] || [ ! -f "$QEMU_DATADIR/vgabios-virtio.bin" ]; then
  echo "FAIL: QEMU datadir missing vgabios-virtio.bin (QEMU_DATADIR=${QEMU_DATADIR:-unset})" >&2
  echo "Set QEMU_DATADIR or MYPCBENCH_QEMU_EXTRACTED to the extracted RPM root." >&2
  return 1 2>/dev/null || exit 1
fi
if [ ! -f "$QEMU_DATADIR/kvmvapic.bin" ]; then
  echo "FAIL: $QEMU_DATADIR/kvmvapic.bin missing" >&2
  return 1 2>/dev/null || exit 1
fi

REAL_QEMU=""
for cand in \
  "${MYPCBENCH_QEMU_EXTRACTED:-}/usr/bin/qemu-system-x86_64" \
  "${MYPCBENCH_QEMU_EXTRACTED:-}/usr/libexec/qemu-kvm" \
  "$(command -v qemu-system-x86_64 2>/dev/null || true)"
do
  if [ -n "$cand" ] && [ -x "$cand" ]; then
    REAL_QEMU="$cand"
    break
  fi
done
if [ -z "$REAL_QEMU" ]; then
  echo "FAIL: qemu-system-x86_64 not found" >&2
  return 1 2>/dev/null || exit 1
fi

WRAP="${A:-.}/results/.qemu-wrap"
mkdir -p "$WRAP"
cat > "$WRAP/qemu-system-x86_64" <<EOF
#!/usr/bin/env bash
# Auto-generated: inject -L so relocated QEMU finds ROM files.
real='$REAL_QEMU'
datadir='$QEMU_DATADIR'
for a in "\$@"; do
  if [ "\$a" = "-L" ]; then
    exec "\$real" "\$@"
  fi
done
exec "\$real" -L "\$datadir" "\$@"
EOF
chmod +x "$WRAP/qemu-system-x86_64"

if [ -n "${MYPCBENCH_QEMU_EXTRACTED:-}" ] && [ -x "$MYPCBENCH_QEMU_EXTRACTED/usr/bin/qemu-img" ]; then
  export PATH="$WRAP:$MYPCBENCH_QEMU_EXTRACTED/usr/bin:$PATH"
else
  export PATH="$WRAP:$PATH"
fi

echo "QEMU wrap: real=$REAL_QEMU"
echo "QEMU -L $QEMU_DATADIR"
echo "QEMU which=$(command -v qemu-system-x86_64)"
