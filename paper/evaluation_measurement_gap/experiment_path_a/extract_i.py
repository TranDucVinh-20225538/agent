"""Path A observation extractor. Outcome-blind: no cum_reward, no human label."""

from __future__ import annotations

import ast
import re
from typing import Any, Optional

_ACTION_WRAP = re.compile(r"^<action>\s*|\s*</action>\s*$")
_SEND = re.compile(r"^send_msg_to_user\s*\((.*)\)\s*$", re.DOTALL)


def episode_status(traj: dict[str, Any]) -> str:
    """EXEC_FAIL or ELIGIBLE. Does not read V or L."""
    if traj.get("valid") is False:
        return "EXEC_FAIL"
    err = (traj.get("summary_info") or {}).get("err_msg")
    if isinstance(err, str) and err.strip():
        return "EXEC_FAIL"
    steps = traj.get("steps")
    if not isinstance(steps, list) or len(steps) == 0:
        return "EXEC_FAIL"
    return "ELIGIBLE"


def _strip_action_wrap(text: str) -> str:
    return _ACTION_WRAP.sub("", text.strip())


def parse_send_msg(action: Optional[str]) -> Optional[str]:
    """Message if this action is send_msg_to_user(...); None if it is some other action."""
    if not action or not str(action).strip():
        return None
    s = _strip_action_wrap(str(action))
    if not s.startswith("send_msg_to_user"):
        return None
    m = _SEND.match(s)
    if not m:
        return ""
    inner = m.group(1).strip()
    if inner == "":
        return ""
    try:
        val = ast.literal_eval(inner)
        if isinstance(val, tuple):
            val = val[0] if val else ""
        return "" if val is None else str(val)
    except (SyntaxError, ValueError):
        if len(inner) >= 2 and inner[0] == inner[-1] and inner[0] in "\"'":
            return inner[1:-1]
        return inner


def last_assistant_content(step: dict[str, Any]) -> Optional[str]:
    msgs = step.get("chat_messages") or []
    if not isinstance(msgs, list):
        return None
    for msg in reversed(msgs):
        if isinstance(msg, dict) and msg.get("role") == "assistant":
            content = msg.get("content")
            if content is None:
                content = msg.get("message")
            return str(content) if content is not None else ""
    return None


def extract_ans(traj: dict[str, Any]) -> Optional[str]:
    """Last send_msg_to_user argument. None if no such action exists."""
    steps = traj.get("steps") or []
    for step in reversed(steps):
        if not isinstance(step, dict):
            continue
        parsed = parse_send_msg(step.get("action"))
        if parsed is not None:
            return parsed
        content = last_assistant_content(step)
        if content:
            parsed = parse_send_msg(content)
            if parsed is not None:
                return parsed
    return None


def extract_url(traj: dict[str, Any]) -> Optional[str]:
    steps = traj.get("steps") or []
    for step in reversed(steps):
        if not isinstance(step, dict):
            continue
        url = step.get("url")
        if isinstance(url, str) and url.strip():
            return url.strip()
    return None


def classify_i(family: str, traj: dict[str, Any]) -> str:
    """ABSTAIN or DETERMINING. Caller must pass ELIGIBLE traj only."""
    need_ans = family in {"string", "string_url"}
    need_url = family in {"url", "string_url"}
    if need_ans:
        ans = extract_ans(traj)
        if ans is None or not str(ans).strip():
            return "ABSTAIN"
    if need_url:
        url = extract_url(traj)
        if url is None or not str(url).strip():
            return "ABSTAIN"
    return "DETERMINING"
