#!/usr/bin/env python3
"""Generic executor core — frozen qwen_cuabash protocol, pluggable transport.

Phase 1 Commit A: FakeModel only. Behavioral protocol is NOT redesigned;
we reuse QwenOSWorldAgent (prompt/parse/bash) + a react loop mirroring
run_mypcbench.run_single_example.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Harness on sys.path (gitignored vendor; identity via paper2_harness_pin.json)
_AGENT_ROOT = Path(__file__).resolve().parents[1]
_HARNESS = _AGENT_ROOT / "external" / "MyPCBench-main" / "agent-harness"
if str(_HARNESS) not in sys.path:
    sys.path.insert(0, str(_HARNESS))
if str(_AGENT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_AGENT_ROOT / "scripts"))
if str(_AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(_AGENT_ROOT))

from agents.qwen_cua import QwenOSWorldAgent  # noqa: E402
from paper2_traj_terminal import (  # noqa: E402
    canonical_last_action,
    has_done_action,
    inspect_last_action,
)

from generic_executor.fake_env import FakeEnv  # noqa: E402
from generic_executor.fake_model import FakeModel, install_fake_llm  # noqa: E402

PROTOCOL_SPEC = "GENERIC_AGENT_PROTOCOL_SPEC.md"
FREEZE_NOTE = (
    "Behavioral protocol frozen at Gate −2. Transport is the only "
    "intentional generic seam (FakeModel in Phase 1)."
)


@dataclass
class TurnRecord:
    predict_round: int
    response: str
    actions: List[str]
    traj_actions: List[str]
    kind: str  # gui | tool_call | empty_xml | done | fail | predict_crash | break
    n_messages_sent: int
    n_screenshots_in_agent: int
    pending_bash_after: str


@dataclass
class RunResult:
    traj_path: Path
    turns: List[TurnRecord] = field(default_factory=list)
    env_actions: List[Any] = field(default_factory=list)
    bash_commands: List[str] = field(default_factory=list)
    fake_calls: int = 0
    terminal_status: str = "BOOT_NO_RESULT"
    valid_done: bool = False
    canonical_last_action: Optional[str] = None
    evidence_kind: Optional[str] = None
    stop_reason: str = ""


def _append_traj(traj_path: Path, row: Dict[str, Any]) -> None:
    traj_path.parent.mkdir(parents=True, exist_ok=True)
    with traj_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_qwen_cuabash_agent(*, env: FakeEnv, model_name: str = "fake/model") -> QwenOSWorldAgent:
    """Construct the frozen Paper-2 agent (enable_bash=True) against FakeEnv."""
    # Keep thinking off for deterministic parse (no reasoning salvage needed).
    os.environ.setdefault("MYPCBENCH_QWEN_ENABLE_THINKING", "0")
    os.environ.setdefault("MYPCBENCH_QWEN_KEEP_REASONING", "0")
    agent = QwenOSWorldAgent(
        model=model_name,
        screen_size=env.screen_size,
        client_password="password",
        enable_bash=True,
        env=env,
        enable_thinking=False,
        keep_reasoning=False,
        temperature=0.0,
    )
    return agent


def run_executor(
    *,
    fake: FakeModel,
    instruction: str = "Complete the synthetic task.",
    max_steps: int = 80,
    empty_action_retries: int = 3,
    result_dir: Optional[Path] = None,
    sleep_after: float = 0.0,
) -> RunResult:
    """React loop aligned with run_mypcbench.run_single_example (frozen semantics)."""
    if result_dir is None:
        result_dir = _AGENT_ROOT / "out" / "generic_executor_runs" / datetime.now().strftime(
            "%Y%m%dT%H%M%S"
        )
    result_dir = Path(result_dir)
    result_dir.mkdir(parents=True, exist_ok=True)
    traj_path = result_dir / "traj.jsonl"
    if traj_path.exists():
        traj_path.unlink()

    env = FakeEnv(instruction=instruction)
    agent = build_qwen_cuabash_agent(env=env)
    install_fake_llm(agent._inner, fake)
    agent.reset()

    obs = env._get_obs()
    step_idx = 0
    consecutive_empty = 0
    consecutive_api_errors = 0
    done = False
    turns: List[TurnRecord] = []
    stop_reason = "max_steps"

    while not done and step_idx < max_steps:
        try:
            response, actions = agent.predict(instruction, obs)
        except Exception as e:
            _append_traj(
                traj_path,
                {
                    "step_num": step_idx + 1,
                    "action": "PREDICT_CRASH",
                    "response": str(e),
                    "done": True,
                    "info": {"error": str(e)},
                },
            )
            turns.append(
                TurnRecord(
                    predict_round=step_idx,
                    response=str(e),
                    actions=[],
                    traj_actions=["PREDICT_CRASH"],
                    kind="predict_crash",
                    n_messages_sent=len(fake.calls[-1]["messages"]) if fake.calls else 0,
                    n_screenshots_in_agent=len(agent._inner.screenshots),
                    pending_bash_after=agent._pending_bash_result,
                )
            )
            stop_reason = "predict_crash"
            break

        n_msgs = len(fake.calls[-1]["messages"]) if fake.calls else 0
        n_shots = len(agent._inner.screenshots)
        pending = agent._pending_bash_result

        if not actions:
            consecutive_empty += 1
            resp_str = response if isinstance(response, str) else str(response)
            if resp_str.startswith("Error code:") or "BadRequestError" in resp_str:
                consecutive_api_errors += 1
                if consecutive_api_errors >= 3:
                    stop_reason = "api_errors"
                    turns.append(
                        TurnRecord(
                            predict_round=step_idx,
                            response=resp_str,
                            actions=[],
                            traj_actions=[],
                            kind="break",
                            n_messages_sent=n_msgs,
                            n_screenshots_in_agent=n_shots,
                            pending_bash_after=pending,
                        )
                    )
                    break
            else:
                consecutive_api_errors = 0

            has_pending = bool(pending)
            if has_pending and consecutive_empty < max_steps:
                _append_traj(
                    traj_path,
                    {
                        "step_num": step_idx + 1,
                        "action": "TOOL_CALL",
                        "response": resp_str,
                        "done": False,
                        "info": {"kind": "tool_call_round"},
                    },
                )
                turns.append(
                    TurnRecord(
                        predict_round=step_idx,
                        response=resp_str,
                        actions=[],
                        traj_actions=["TOOL_CALL"],
                        kind="tool_call",
                        n_messages_sent=n_msgs,
                        n_screenshots_in_agent=n_shots,
                        pending_bash_after=pending,
                    )
                )
                obs = env._get_obs()
                step_idx += 1
                continue

            if consecutive_empty < empty_action_retries:
                _append_traj(
                    traj_path,
                    {
                        "step_num": step_idx + 1,
                        "action": "EMPTY_XML",
                        "response": resp_str,
                        "done": False,
                        "info": {
                            "kind": "empty_xml_retry",
                            "empty": consecutive_empty,
                            "limit": empty_action_retries,
                        },
                    },
                )
                turns.append(
                    TurnRecord(
                        predict_round=step_idx,
                        response=resp_str,
                        actions=[],
                        traj_actions=["EMPTY_XML"],
                        kind="empty_xml",
                        n_messages_sent=n_msgs,
                        n_screenshots_in_agent=n_shots,
                        pending_bash_after=pending,
                    )
                )
                obs = env._get_obs()
                step_idx += 1
                continue
            stop_reason = "empty_xml_limit"
            turns.append(
                TurnRecord(
                    predict_round=step_idx,
                    response=resp_str,
                    actions=[],
                    traj_actions=[],
                    kind="break",
                    n_messages_sent=n_msgs,
                    n_screenshots_in_agent=n_shots,
                    pending_bash_after=pending,
                )
            )
            break

        consecutive_empty = 0
        traj_actions: List[str] = []
        kind = "gui"
        for action in actions:
            obs, reward, done, info = env.step(action, sleep_after)
            act_s = action if isinstance(action, str) else str(action)
            traj_actions.append(act_s)
            _append_traj(
                traj_path,
                {
                    "step_num": step_idx + 1,
                    "action": act_s,
                    "response": response if isinstance(response, str) else str(response),
                    "reward": reward,
                    "done": done,
                    "info": info,
                },
            )
            if done:
                kind = "done" if info.get("done") else ("fail" if info.get("fail") else "gui")
                break

        turns.append(
            TurnRecord(
                predict_round=step_idx,
                response=response if isinstance(response, str) else str(response),
                actions=list(actions),
                traj_actions=traj_actions,
                kind=kind,
                n_messages_sent=n_msgs,
                n_screenshots_in_agent=n_shots,
                pending_bash_after=agent._pending_bash_result,
            )
        )
        step_idx += 1
        if done:
            stop_reason = kind
            break

    # Gate −1.5 terminal classification
    if traj_path.exists() and traj_path.stat().st_size > 0:
        info = inspect_last_action(traj_path)
        valid = bool(info["valid_done"])
        last = info["canonical_last_action"]
        if valid:
            status = "DONE"
        elif info["has_steps"] or info["row_count"] > 0:
            status = "TERMINAL_FAIL"
        else:
            status = "BOOT_NO_RESULT"
    else:
        valid = False
        last = None
        info = {"evidence_kind": "NO_TRAJ"}
        status = "BOOT_NO_RESULT"

    return RunResult(
        traj_path=traj_path,
        turns=turns,
        env_actions=list(env.action_history),
        bash_commands=list(env.bash_history),
        fake_calls=len(fake.calls),
        terminal_status=status,
        valid_done=valid,
        canonical_last_action=last,
        evidence_kind=info.get("evidence_kind"),
        stop_reason=stop_reason,
    )


def system_prompt_has_frozen_markers(fake: FakeModel) -> Dict[str, bool]:
    """Inspect first fake call's system message for frozen protocol markers."""
    if not fake.calls:
        return {"has_call": False}
    msgs = fake.calls[0]["messages"]
    sys_msg = msgs[0]
    texts: List[str] = []
    content = sys_msg.get("content")
    if isinstance(content, str):
        texts.append(content)
    elif isinstance(content, list):
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                texts.append(part.get("text") or "")
    blob = "\n".join(texts)
    return {
        "has_call": True,
        "has_computer_use": "computer_use" in blob and "<tools>" in blob,
        "has_xml_envelope": "<tool_call>" in blob and "<function=" in blob,
        "has_1000x1000": "1000x1000" in blob,
        "has_bash_addendum": "<function=bash>" in blob,
        "has_mypcbench_context": "Gringotts" in blob or "Michael Scott" in blob,
        "has_response_format": "action=terminate" in blob,
    }
