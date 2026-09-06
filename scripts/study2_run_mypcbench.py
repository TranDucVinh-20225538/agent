#!/usr/bin/env python3
"""Study 2 — thin bridge: frozen qwen_cuabash + OpenRouter transport → run_mypcbench.

Does not change protocol, tasks, or Study 1 runners. Used only by Study 2
matrix entrypoints after ``source scripts/study2_bind_execution_key.sh``.

Refuses SMALL / Gate 0A smoke / native Anthropic diversion.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_AGENT_ROOT = Path(__file__).resolve().parents[1]
_HARNESS = _AGENT_ROOT / "external" / "MyPCBench-main" / "agent-harness"
for p in (_HARNESS, _AGENT_ROOT / "scripts", _AGENT_ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# Family key → (FAMILY_CONFIGS key, locked OpenRouter model id, out slug)
STUDY2_FAMILIES = {
    "flash": ("flash", "qwen/qwen3.8-flash", "study2-flash"),
    "gpt": ("gpt_family", "openai/gpt-5.5", "study2-gpt"),
    "claude": ("claude_family", "anthropic/claude-opus-4.6", "study2-claude"),
}

REQUIRED_KEY_PREFIX = "sk-or-v1-008"
FORBIDDEN_ENV = (
    "OPENROUTER_API_KEY_SMALL",
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_API_KEY_BACKUP",
    "GATE0A_FAMILY",
    "GATE0A_OUT",
    "GATE0A_MODEL",
)


def resolve_family(family: str | None = None) -> tuple[str, str, str, str]:
    """Return (family_slug, config_key, model_id, out_slug)."""
    slug = (family or os.environ.get("STUDY2_FAMILY") or "").strip().lower()
    if slug not in STUDY2_FAMILIES:
        raise SystemExit(
            f"STUDY2_BRIDGE_FAIL: STUDY2_FAMILY={slug!r}; want one of {sorted(STUDY2_FAMILIES)}"
        )
    cfg_key, model_id, out_slug = STUDY2_FAMILIES[slug]
    return slug, cfg_key, model_id, out_slug


def assert_study2_runtime_binding() -> dict:
    """Fail closed unless funded OpenRouter key 008… is bound and SMALL scrubbed."""
    for bad in FORBIDDEN_ENV:
        if os.environ.get(bad):
            raise SystemExit(f"STUDY2_BRIDGE_FAIL: {bad} still set (forbidden for Study 2 matrix)")

    key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY") or ""
    if not key.startswith(REQUIRED_KEY_PREFIX):
        raise SystemExit(
            "STUDY2_BRIDGE_FAIL: runtime key must be OpenRouter "
            f"{REQUIRED_KEY_PREFIX}… (got prefix {key[:12]!r})"
        )
    if key != (os.environ.get("OPENAI_API_KEY") or ""):
        raise SystemExit("STUDY2_BRIDGE_FAIL: OPENAI_API_KEY must mirror OPENROUTER_API_KEY")
    base = os.environ.get("OPENAI_BASE_URL") or ""
    if "openrouter.ai" not in base:
        raise SystemExit(f"STUDY2_BRIDGE_FAIL: OPENAI_BASE_URL not OpenRouter: {base!r}")

    fp = os.environ.get("STUDY2_EXECUTION_KEY_FINGERPRINT") or ""
    if "008" not in fp:
        raise SystemExit(
            f"STUDY2_BRIDGE_FAIL: STUDY2_EXECUTION_KEY_FINGERPRINT missing 008 ({fp!r}); "
            "source scripts/study2_bind_execution_key.sh first"
        )
    body = key[len("sk-or-v1-") :]
    return {
        "fingerprint_masked": f"sk-or-v1-{body[:3]}…{body[-3:]}",
        "base_url": base,
        "key_source": os.environ.get("STUDY2_EXECUTION_KEY_SOURCE"),
    }


def install_study2_agent_factory(expected_model: str, cfg_key: str) -> None:
    """Patch run_mypcbench.get_agent → frozen qwen_cuabash + OpenRouter transport."""
    import run_mypcbench as rmb
    from generic_executor.executor import build_qwen_cuabash_agent
    from generic_executor.family_config import FAMILY_CONFIGS
    from generic_executor.openrouter_chat import OpenRouterChatCompletionsTransport
    from generic_executor.transport import install_transport

    family_cfg = FAMILY_CONFIGS[cfg_key]
    if family_cfg.openrouter_model != expected_model:
        raise SystemExit(
            f"STUDY2_BRIDGE_FAIL: config model {family_cfg.openrouter_model} "
            f"!= locked {expected_model}"
        )

    api_key = os.environ["OPENROUTER_API_KEY"]
    base = os.environ.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
    timeout_s = float(os.environ.get("STUDY2_HTTP_TIMEOUT", "180"))

    def get_agent_study2(agent_type, model, screen_size, client_password, **kwargs):
        del agent_type  # Study 2 always uses frozen qwen_cuabash protocol
        if model != expected_model:
            raise RuntimeError(
                f"STUDY2_BRIDGE_FAIL: silent model remap {model!r} != {expected_model!r}"
            )
        env = kwargs.get("env")
        if env is None:
            raise RuntimeError("STUDY2_BRIDGE_FAIL: env required for qwen_cuabash")
        agent = build_qwen_cuabash_agent(env=env, model_name=expected_model)
        transport = OpenRouterChatCompletionsTransport(
            api_key=api_key,
            family=family_cfg,
            base_url=base,
            timeout_s=timeout_s,
        )
        install_transport(agent._inner, transport)
        print(
            f"[study2_bridge] agent=qwen_cuabash+OpenRouterChatCompletions "
            f"model={expected_model} family={cfg_key} base={base}",
            flush=True,
        )
        return agent

    rmb.get_agent = get_agent_study2  # type: ignore[assignment]


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    slug, cfg_key, model_id, _out = resolve_family()
    binding = assert_study2_runtime_binding()
    # Force CLI model to locked id if caller omitted / mismatched
    if "--model" in argv:
        i = argv.index("--model")
        if i + 1 >= len(argv) or argv[i + 1] != model_id:
            raise SystemExit(
                f"STUDY2_BRIDGE_FAIL: --model must be {model_id} for STUDY2_FAMILY={slug}"
            )
    else:
        argv = ["--model", model_id, *argv]
    # Always request qwen_cuabash; factory ignores type and installs OR transport
    if "--agent_type" in argv:
        i = argv.index("--agent_type")
        argv[i + 1] = "qwen_cuabash"
    else:
        argv = ["--agent_type", "qwen_cuabash", *argv]

    print(
        f"[study2_bridge] family={slug} model={model_id} "
        f"fingerprint={binding['fingerprint_masked']}",
        flush=True,
    )
    # Execution plumbing (apps readiness + INFRA_FAIL) — must run before rmb.main.
    from study2_harness_plumbing import apply_all as apply_study2_harness_plumbing

    plumbing = apply_study2_harness_plumbing()
    print(f"[study2_bridge] harness_plumbing={plumbing}", flush=True)

    install_study2_agent_factory(model_id, cfg_key)

    import run_mypcbench as rmb

    sys.argv = [sys.argv[0], *argv]
    rmb.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
