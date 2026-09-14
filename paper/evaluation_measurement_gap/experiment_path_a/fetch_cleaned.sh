#!/usr/bin/env bash
# Download AgentRewardBench cleaned JSON + annotations. No screenshots.
# Does not classify ABSTAIN. Run only after reading PROTOCOL.md.
set -euo pipefail
DEST="${1:-./data/agent_reward_bench}"
mkdir -p "$DEST"
python3 - <<PY
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="McGill-NLP/agent-reward-bench",
    repo_type="dataset",
    local_dir="$DEST",
    allow_patterns=[
        "data/annotations.csv",
        "cleaned/**/*.json",
        "README.md",
    ],
    ignore_patterns=["screenshots/**", "judgments/**"],
)
print("downloaded to $DEST")
PY
