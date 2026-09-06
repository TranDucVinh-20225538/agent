#!/usr/bin/env python3
"""Per-family OpenRouter chat-completions generation configs.

Not a claim that GPT/Claude Gate 0 passed — only portable request shaping
for the frozen prompt/XML protocol (plain text in, plain text out).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, FrozenSet, Optional


@dataclass(frozen=True)
class FamilyConfig:
    """Maps logical family → OpenRouter model id + which gen knobs to send."""

    family: str
    openrouter_model: str
    # Keys from the agent generation dict that MAY be forwarded.
    allow_keys: FrozenSet[str] = field(
        default_factory=lambda: frozenset(
            {"max_tokens", "temperature", "top_p", "presence_penalty"}
        )
    )
    # Extra body keys for chat-completions (never tools / previous_response_id).
    extra_body: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""


# Candidates for later Gate 0 — configs only; no live calls in Phase 1B.
FAMILY_CONFIGS: Dict[str, FamilyConfig] = {
    "flash": FamilyConfig(
        family="flash",
        openrouter_model="qwen/qwen3.8-flash",
        allow_keys=frozenset(
            {
                "max_tokens",
                "temperature",
                "top_p",
                "presence_penalty",
                "top_k",
                "min_p",
                "repetition_penalty",
            }
        ),
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        notes="Qwen Flash via OpenRouter chat-completions; thinking off for Gate 0A default.",
    ),
    "qwen9b": FamilyConfig(
        family="qwen9b",
        openrouter_model="qwen/qwen3.5-9b",
        allow_keys=frozenset(
            {
                "max_tokens",
                "temperature",
                "top_p",
                "presence_penalty",
                "top_k",
            }
        ),
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        notes="Study-1 Qwen 9B id; same transport surface as Flash.",
    ),
    "gpt_family": FamilyConfig(
        family="gpt_family",
        openrouter_model="openai/gpt-5.5",
        allow_keys=frozenset({"max_tokens", "temperature", "top_p", "presence_penalty"}),
        extra_body={},
        notes=(
            "GPT-family candidate. top_k/min_p/chat_template_kwargs omitted "
            "(not portable). Still prompt/XML — no Responses computer-use tools."
        ),
    ),
    "claude_family": FamilyConfig(
        family="claude_family",
        openrouter_model="anthropic/claude-opus-4.6",
        allow_keys=frozenset({"max_tokens", "temperature", "top_p"}),
        extra_body={},
        notes=(
            "Claude-family candidate via OpenRouter OpenAI-style chat-completions "
            "skin. No Anthropic computer-use beta tools. presence_penalty omitted."
        ),
    ),
}


def filter_generation(cfg: FamilyConfig, generation: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Keep only portable keys; drop None values."""
    generation = generation or {}
    out: Dict[str, Any] = {}
    for k in cfg.allow_keys:
        if k in generation and generation[k] is not None:
            out[k] = generation[k]
    return out
