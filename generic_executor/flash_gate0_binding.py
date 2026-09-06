#!/usr/bin/env python3
"""Flash Gate 0A binding constants — must match Paper-2 SMALL lane.

Source of truth for Study-1 Flash runs:
  scripts/paper2_exec_small_lane.sh
  scripts/paper2_exec_run.sh (LANE=SMALL)

Phase 1B documents these for Gate 0A; no live calls here.
"""

from __future__ import annotations

from dataclasses import dataclass

from generic_executor.family_config import FAMILY_CONFIGS
from generic_executor.openrouter_chat import DEFAULT_OPENROUTER_BASE


@dataclass(frozen=True)
class FlashGate0Binding:
    """Exact smoke target for Gate 0A — no silent model/provider failover."""

    model_id: str
    endpoint: str
    lane: str
    key_env_source: str  # host env name before bind
    key_env_runtime: str  # name seen by child after small_lane bind
    base_url_env: str
    agent_type: str
    forbid_fallback_models: tuple
    forbid_env_keys: tuple


FLASH_GATE0A = FlashGate0Binding(
    model_id="qwen/qwen3.8-flash",
    endpoint=f"{DEFAULT_OPENROUTER_BASE}/chat/completions",
    lane="SMALL",
    key_env_source="OPENROUTER_API_KEY_SMALL",
    key_env_runtime="OPENROUTER_API_KEY",  # bound; also mirrored to OPENAI_API_KEY by run.sh
    base_url_env="OPENAI_BASE_URL",  # default https://openrouter.ai/api/v1
    agent_type="qwen_cuabash",
    forbid_fallback_models=(
        "qwen/qwen3.5-9b",
        "openai/gpt-5.5",
        "anthropic/claude-opus-4.6",
    ),
    forbid_env_keys=(
        "OPENROUTER_API_KEY_LARGE",
        "ANTHROPIC_API_KEY",
    ),
)


def assert_flash_family_matches_binding() -> None:
    cfg = FAMILY_CONFIGS["flash"]
    if cfg.openrouter_model != FLASH_GATE0A.model_id:
        raise AssertionError(
            f"family_config flash model {cfg.openrouter_model!r} != "
            f"Gate0A binding {FLASH_GATE0A.model_id!r}"
        )
