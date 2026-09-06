#!/usr/bin/env python3
"""Gate 0A v1.1 family bindings — Flash / GPT / Claude on the same protocol.

Same task shape, max_steps=10, ownership checks, and OpenRouter SMALL lane.
Only model id + artifact namespace differ per family.
"""

from __future__ import annotations

from dataclasses import dataclass

from generic_executor.family_config import FAMILY_CONFIGS
from generic_executor.openrouter_chat import DEFAULT_OPENROUTER_BASE


@dataclass(frozen=True)
class Gate0AFamilyBinding:
    family_key: str  # key in FAMILY_CONFIGS
    slug: str  # artifact / container slug
    model_id: str
    endpoint: str
    lane: str
    key_env_source: str
    token_prefix: str
    token_path: str
    default_out_rel: str
    container_name: str
    forbid_fallback_models: tuple
    forbid_env_keys: tuple


_ENDPOINT = f"{DEFAULT_OPENROUTER_BASE}/chat/completions"
_FORBID_KEYS = ("OPENROUTER_API_KEY_LARGE", "ANTHROPIC_API_KEY")

GATE0A_FAMILIES: dict[str, Gate0AFamilyBinding] = {
    "flash": Gate0AFamilyBinding(
        family_key="flash",
        slug="flash",
        model_id=FAMILY_CONFIGS["flash"].openrouter_model,
        endpoint=_ENDPOINT,
        lane="SMALL",
        key_env_source="OPENROUTER_API_KEY_SMALL",
        token_prefix="FLASHGATE0A-",
        token_path="/tmp/GATE0A_FLASH_TOKEN.txt",
        default_out_rel="results/paper2_exec/gate0a-flash",
        container_name="mypcbench-gate0a-flash",
        forbid_fallback_models=(
            "qwen/qwen3.5-9b",
            "openai/gpt-5.5",
            "anthropic/claude-opus-4.6",
        ),
        forbid_env_keys=_FORBID_KEYS,
    ),
    "gpt": Gate0AFamilyBinding(
        family_key="gpt_family",
        slug="gpt",
        model_id=FAMILY_CONFIGS["gpt_family"].openrouter_model,
        endpoint=_ENDPOINT,
        lane="SMALL",
        key_env_source="OPENROUTER_API_KEY_SMALL",
        token_prefix="GPTGATE0A-",
        token_path="/tmp/GATE0A_GPT_TOKEN.txt",
        default_out_rel="results/paper2_exec/gate0a-gpt",
        container_name="mypcbench-gate0a-gpt",
        forbid_fallback_models=(
            "qwen/qwen3.8-flash",
            "qwen/qwen3.5-9b",
            "anthropic/claude-opus-4.6",
        ),
        forbid_env_keys=_FORBID_KEYS,
    ),
    "claude": Gate0AFamilyBinding(
        family_key="claude_family",
        slug="claude",
        model_id=FAMILY_CONFIGS["claude_family"].openrouter_model,
        endpoint=_ENDPOINT,
        lane="SMALL",
        key_env_source="OPENROUTER_API_KEY_SMALL",
        token_prefix="CLAUDEGATE0A-",
        token_path="/tmp/GATE0A_CLAUDE_TOKEN.txt",
        default_out_rel="results/paper2_exec/gate0a-claude",
        container_name="mypcbench-gate0a-claude",
        forbid_fallback_models=(
            "qwen/qwen3.8-flash",
            "qwen/qwen3.5-9b",
            "openai/gpt-5.5",
        ),
        forbid_env_keys=_FORBID_KEYS,
    ),
}

# Back-compat alias used by Phase 1B Flash review tests.
FLASH_GATE0A = GATE0A_FAMILIES["flash"]


def get_gate0a_binding(family: str) -> Gate0AFamilyBinding:
    key = (family or "flash").strip().lower()
    if key not in GATE0A_FAMILIES:
        raise KeyError(f"unknown Gate 0A family {family!r}; want {sorted(GATE0A_FAMILIES)}")
    return GATE0A_FAMILIES[key]


def assert_binding_matches_family_config(binding: Gate0AFamilyBinding) -> None:
    cfg = FAMILY_CONFIGS[binding.family_key]
    if cfg.openrouter_model != binding.model_id:
        raise AssertionError(
            f"{binding.slug}: family_config model {cfg.openrouter_model!r} != "
            f"Gate0A binding {binding.model_id!r}"
        )
