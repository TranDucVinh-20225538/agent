#!/usr/bin/env bash
# Rebuild the working tree on a new machine. Nothing here is installed system-wide.
#
#   bash scripts/setup.sh            # upstream repo + task files
#   bash scripts/setup.sh --readers  # also the qcow2/ext4 readers for image inspection
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

UPSTREAM_TARBALL="https://codeload.github.com/ljang0/MyPCBench/tar.gz/refs/heads/main"
HF_TASKS="https://huggingface.co/datasets/ljang0/MyPCBench/resolve/main/data/tasks.jsonl"
HF_VARS="https://huggingface.co/datasets/ljang0/MyPCBench/resolve/main/data/variables.json"
IMAGE_REPO="https://huggingface.co/datasets/ljang0/mypcbench-qemu-baseline/resolve/main"

echo "==> upstream harness -> external/MyPCBench-main"
mkdir -p external
curl -sfL "$UPSTREAM_TARBALL" | tar -xz -C external
test -f external/MyPCBench-main/agent-harness/env.py

echo "==> task files -> data/mypcbench"
mkdir -p data/mypcbench
curl -sfL -o data/mypcbench/tasks.jsonl "$HF_TASKS"
curl -sfL -o data/mypcbench/variables.json "$HF_VARS"

echo "==> image-side metadata -> vm/"
mkdir -p vm
for f in VERSION.json SHA256SUMS all_tasks_with_grading.json; do
  curl -sfL -o "vm/hf_$f" "$IMAGE_REPO/$f"
done

if [ "${1:-}" = "--readers" ]; then
  echo "==> qcow2/ext4 readers -> vendor/"
  mkdir -p wheels vendor
  PYTHONPATH=tools/pipfix python3 -m pip download -q --no-deps --dest wheels \
    libqcow-python libfsext-python libvsgpt-python
  for w in wheels/*.whl; do
    python3 -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall('vendor')" "$w"
  done
  PYTHONPATH=vendor python3 -c "import pyfsext; print('readers ok')"
fi

echo
echo "done. Next: see REPRO.md"
