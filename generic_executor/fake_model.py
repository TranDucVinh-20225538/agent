#!/usr/bin/env python3
"""Scripted fake model: returns canned assistant text in order (zero-API)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional  # FakeModel.complete uses List[Dict]


def _tool_call_computer(action: str, **params: Any) -> str:
    parts = [f"<parameter=action>\n{action}\n</parameter>"]
    for k, v in params.items():
        if isinstance(v, (list, dict)):
            import json

            val = json.dumps(v)
        else:
            val = str(v)
        parts.append(f"<parameter={k}>\n{val}\n</parameter>")
    body = "\n".join(parts)
    return (
        f"<tool_call>\n<function=computer_use>\n{body}\n</function>\n</tool_call>"
    )


def _tool_call_bash(command: str) -> str:
    return (
        "<tool_call>\n"
        "<function=bash>\n"
        f"<parameter=command>\n{command}\n</parameter>\n"
        "</function>\n"
        "</tool_call>"
    )


def response_action(action_line: str, *tool_xml: str) -> str:
    return f"Action: {action_line}\n" + "\n".join(tool_xml)


# --- Canned protocol-legal responses (prompt-mediated XML) ---

CLICK_ONCE = response_action(
    "Click the center.",
    _tool_call_computer("left_click", coordinate=[500, 400]),
)

CLICK_THEN_TYPE = response_action(
    "Click then type.",
    _tool_call_computer("left_click", coordinate=[100, 100]),
    _tool_call_computer("type", text="hello"),
)

BASH_ONLY = response_action(
    "Inspect files via bash.",
    _tool_call_bash("echo hello_from_bash"),
)

BASH_THEN_CLICK = response_action(
    "Bash then click.",
    _tool_call_bash("pwd"),
    _tool_call_computer("left_click", coordinate=[200, 200]),
)

TERMINATE_DONE = response_action(
    "Task finished.",
    _tool_call_computer("terminate", status="success"),
)

TERMINATE_FAIL = response_action(
    "Cannot complete.",
    _tool_call_computer("terminate", status="failure"),
)

INFEASIBLE_TEXT = (
    "Action: Give up.\n"
    "This task is infeasible given the available data."
)

MALFORMED_XML = (
    "Action: Broken call.\n"
    "<tool_call>\n"
    "<function=computer_use>\n"
    "NOT_A_PARAMETER"
    "</tool_call>"
)

MALFORMED_NESTED = (
    "Action: Nested junk.\n"
    "<tool_call>\n"
    "<function=computer_use>\n"
    "<parameter=action>\nleft_click\n</parameter>\n"
    "<parameter=coordinate>\n{not-json\n</parameter>\n"
    "</function>\n"
    "</tool_call>"
)

NOISE_EMPTY = "Action: Thinking only.\nI need more time."


@dataclass
class FakeModel:
    """Transport stand-in: pop scripted responses; record every call payload.

    Implements the Phase 1B ``Transport`` contract
    (``complete(messages, model=, generation=)``).
    """

    script: List[str]
    calls: List[Dict[str, Any]] = field(default_factory=list)
    default_when_exhausted: str = NOISE_EMPTY

    def complete(
        self,
        messages: List[Dict[str, Any]],
        *,
        model: str = "fake/model",
        generation: Optional[Dict[str, Any]] = None,
    ) -> str:
        self.calls.append(
            {
                "n_messages": len(messages or []),
                "messages": messages,
                "model": model,
                "generation": generation,
            }
        )
        if not self.script:
            return self.default_when_exhausted
        return self.script.pop(0)


def install_fake_llm(inner_agent: Any, fake: FakeModel) -> None:
    """Install FakeModel via the shared Transport seam (Phase 1A + 1B)."""
    from generic_executor.transport import install_transport

    install_transport(inner_agent, fake)
