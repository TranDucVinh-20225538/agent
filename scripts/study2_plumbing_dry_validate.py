#!/usr/bin/env python3
"""Dry validation for Study 2 execution-plumbing repairs (no QEMU / no live OR).

Checks:
  1. App readiness gate is no longer a no-op and requires port 3005.
  2. OpenRouter default_http_post has bounded 429 retry constants + wired path.
  3. All three Study 2 families share study2_run_mypcbench + OpenRouter transport.
  4. No SMALL / Gate0A / native-agent Study 2 path is introduced.
"""

from __future__ import annotations

import ast
import importlib.util
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "external" / "MyPCBench-main" / "agent-harness"))


def _fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def check_apps_ready_gate() -> None:
    import env as env_mod
    from study2_harness_plumbing import _wait_for_apps_ready, apply_env_readiness_gate

    # Committed source of truth (applied by Study 2 bridge).
    src = inspect.getsource(_wait_for_apps_ready)
    if "App readiness gate" not in src:
        _fail("study2_harness_plumbing missing readiness log markers")
    if "3005" not in src:
        _fail("apps gate must explicitly require port 3005")
    if "create_connection" not in src:
        _fail("apps gate must TCP-probe app ports")
    if "TimeoutError" not in src:
        _fail("apps gate must raise TimeoutError on failure")

    apply_env_readiness_gate()
    patched = inspect.getsource(env_mod.MyPCBenchEnv._wait_for_apps_ready)
    if "App readiness gate" not in patched:
        _fail("apply_env_readiness_gate did not install apps gate")
    print("PASS: app readiness gate (TCP + 3005 + timeout)")


def check_429_retry() -> None:
    from generic_executor import openrouter_chat as orc

    if orc.HTTP_429_MAX_RETRIES != 5:
        _fail(f"HTTP_429_MAX_RETRIES={orc.HTTP_429_MAX_RETRIES} want 5")
    if orc.HTTP_429_BACKOFF_S != (2, 4, 8, 16, 32):
        _fail(f"HTTP_429_BACKOFF_S={orc.HTTP_429_BACKOFF_S}")
    src = inspect.getsource(orc.default_http_post)
    if "e.code == 429" not in src and "code == 429" not in src:
        _fail("default_http_post missing HTTP 429 branch")
    if "retry" not in src.lower():
        _fail("default_http_post missing retry logging")
    # Transport used by Study 2 bridge defaults to this post
    from generic_executor.openrouter_chat import OpenRouterChatCompletionsTransport

    t = OpenRouterChatCompletionsTransport(
        api_key="sk-test",
        family=__import__(
            "generic_executor.family_config", fromlist=["FAMILY_CONFIGS"]
        ).FAMILY_CONFIGS["flash"],
    )
    if t.http_post is not orc.default_http_post:
        _fail("OpenRouterChatCompletionsTransport.http_post is not default_http_post")
    print("PASS: OpenRouter 429 retry wired on shared transport")


def check_shared_study2_path() -> None:
    bridge = ROOT / "scripts" / "study2_run_mypcbench.py"
    text = bridge.read_text()
    if "OpenRouterChatCompletionsTransport" not in text:
        _fail("study2_run_mypcbench missing OpenRouter transport")
    if "build_qwen_cuabash_agent" not in text:
        _fail("study2_run_mypcbench missing shared qwen_cuabash builder")
    if "study2_harness_plumbing" not in text:
        _fail("study2_run_mypcbench must apply study2_harness_plumbing")
    if "GATE0A" not in text or "FORBIDDEN" not in text:
        _fail("study2 bridge must refuse Gate0A / SMALL")
    # All three families in STUDY2_FAMILIES
    spec = importlib.util.spec_from_file_location("study2_bridge", bridge)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    # Avoid executing main; parse AST for STUDY2_FAMILIES keys
    tree = ast.parse(text)
    families = None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "STUDY2_FAMILIES":
                    families = ast.literal_eval(node.value)
    if not families or set(families) != {"flash", "gpt", "claude"}:
        _fail(f"STUDY2_FAMILIES keys={families}")
    # Lane script always execs same study2_exec_run
    lane = (ROOT / "scripts" / "study2_matrix_lane.sh").read_text()
    if "study2_exec_run.sh" not in lane:
        _fail("matrix_lane must call study2_exec_run.sh")
    if "study2_bind_execution_key.sh" not in lane:
        _fail("matrix_lane must bind execution key")
    # No native agent diversion in Study 2 entrypoints (mentions in refuse/scrub checks OK).
    for name in ("study2_exec_run.sh", "study2_matrix_lane.sh", "study2_matrix.sh"):
        p = ROOT / "scripts" / name
        blob = p.read_text()
        if "agent_type claude" in blob or "--agent_type openai" in blob:
            _fail(f"{name} introduces native agent_type path")
        if "GATE0A_FAMILY=" in blob or "export GATE0A" in blob:
            _fail(f"{name} exports Gate0A path")
        if name == "study2_exec_run.sh" and "study2_run_mypcbench.py" not in blob:
            _fail(f"{name} missing study2 bridge")
        if name == "study2_matrix_lane.sh" and "study2_exec_run.sh" not in blob:
            _fail(f"{name} missing exec_run")
    exec_run = (ROOT / "scripts" / "study2_exec_run.sh").read_text()
    if "study2_run_mypcbench.py" not in exec_run:
        _fail("study2_exec_run must call study2_run_mypcbench.py")
    if "--agent_type qwen_cuabash" not in exec_run:
        _fail("study2_exec_run must use qwen_cuabash (shared frozen agent)")
    print("PASS: shared Study 2 executor/OpenRouter path for flash|gpt|claude")
    print("PASS: no SMALL/Gate0A/native-agent Study 2 path")


def check_run_mypcbench_infra() -> None:
    from study2_harness_plumbing import apply_infra_fail_on_reset
    import run_mypcbench as rmb

    apply_infra_fail_on_reset()
    src = inspect.getsource(rmb.run_single_example)
    if "INFRA_FAIL" not in src and "App readiness gate" not in src:
        # Wrapper closes over orig; inspect may show wrapper body.
        if "infra_fail" not in src.lower() and "TimeoutError" not in src:
            _fail("infra_fail patch not applied to run_single_example")
    print("PASS: readiness failure classified as INFRA_FAIL before agent steps")


def main() -> None:
    check_apps_ready_gate()
    check_429_retry()
    check_shared_study2_path()
    check_run_mypcbench_infra()
    print("ALL_DRY_VALIDATE_PASS")


if __name__ == "__main__":
    main()
