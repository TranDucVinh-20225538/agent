"""Gate 0A instrument: rewrite only the five evidenced near-miss XML shapes.

Does NOT change the frozen system prompt or open-ended lenient parsing.
Each transform is tied to a documented Flash failure transcript shape.

Shapes (see out/gate0a_flash_diagnostic_handoff/protocol_contract.md):
  1. ``<function=tool_call>`` + computer_use ``action=`` verb
  2. ``<parameter=computer_use>`` used where ``<function=computer_use>`` belongs
  3. ``<function=tool_call>`` + bash-like action (``bash`` / ``mcp__bash__execute``) + ``command``
  4. orphan ``<parameter=command>`` inside ``<tool_call>`` (no function tag)
  5. ``<parameter=bash>`` used where ``<function=bash>`` belongs
"""

from __future__ import annotations

import re
from typing import List, Tuple

# Verbs accepted by vendored process_tool_call_params (computer_use).
_COMPUTER_USE_ACTIONS = frozenset(
    {
        "left_click",
        "right_click",
        "middle_click",
        "double_click",
        "triple_click",
        "type",
        "key",
        "scroll",
        "hscroll",
        "wait",
        "terminate",
        "answer",
        "mouse_move",
        "left_click_drag",
        "screenshot",  # instrument no-op (recurring Flash/Study1 output)
    }
)

_BASH_ACTION_ALIASES = frozenset({"bash", "mcp__bash__execute"})

_TOOL_CALL_RE = re.compile(r"<tool_call>(.*?)</tool_call>", re.DOTALL)
_FUNC_TOOL_CALL_RE = re.compile(r"<function=tool_call>", re.IGNORECASE)
_PARAM_ACTION_RE = re.compile(
    r"<parameter=action>\s*(.*?)\s*</parameter>", re.DOTALL | re.IGNORECASE
)
_PARAM_COMMAND_RE = re.compile(
    r"<parameter=command>\s*(.*?)\s*</parameter>", re.DOTALL | re.IGNORECASE
)


def _rewrite_tool_call_body(body: str) -> Tuple[str, List[str]]:
    """Return (new_body, list of shape ids applied)."""
    applied: List[str] = []
    out = body

    # Shape 2: <parameter=computer_use> … </function>  (opening tag wrong)
    if re.search(r"<parameter=computer_use>", out, re.IGNORECASE) and not re.search(
        r"<function=computer_use>", out, re.IGNORECASE
    ):
        out2 = re.sub(
            r"<parameter=computer_use>", "<function=computer_use>", out, count=1, flags=re.IGNORECASE
        )
        if out2 != out:
            out = out2
            applied.append("shape2_parameter_computer_use")

    # Shape 5: <parameter=bash> … where function=bash belongs
    if re.search(r"<parameter=bash>", out, re.IGNORECASE) and not re.search(
        r"<function=bash>", out, re.IGNORECASE
    ):
        out2 = re.sub(r"<parameter=bash>", "<function=bash>", out, count=1, flags=re.IGNORECASE)
        if out2 != out:
            out = out2
            applied.append("shape5_parameter_bash")

    # Shape 1 / 3: <function=tool_call> + action=
    if _FUNC_TOOL_CALL_RE.search(out):
        am = _PARAM_ACTION_RE.search(out)
        action = (am.group(1).strip() if am else "").lower()
        has_command = bool(_PARAM_COMMAND_RE.search(out))
        if action in _COMPUTER_USE_ACTIONS:
            out = _FUNC_TOOL_CALL_RE.sub("<function=computer_use>", out, count=1)
            applied.append("shape1_function_tool_call_computer_use")
        elif action in _BASH_ACTION_ALIASES and has_command:
            out = _FUNC_TOOL_CALL_RE.sub("<function=bash>", out, count=1)
            # Drop the misleading action= parameter so bash extractor sees clean bash form.
            out = _PARAM_ACTION_RE.sub("", out, count=1)
            applied.append("shape3_function_tool_call_bash")

    # Shape 4: orphan <parameter=command> with no function=bash / computer_use / tool_call
    has_fn = bool(
        re.search(r"<function=(bash|computer_use|tool_call)>", out, re.IGNORECASE)
    )
    if (not has_fn) and _PARAM_COMMAND_RE.search(out):
        # Inject function=bash wrapper around existing parameters.
        out = "<function=bash>\n" + out.strip() + "\n"
        # Ensure a closing </function> exists (examples often already have one).
        if not re.search(r"</function>", out, re.IGNORECASE):
            out = out + "</function>\n"
        applied.append("shape4_orphan_command")

    return out, applied


def normalize_near_miss_xml(response: str) -> str:
    """Apply only the five evidenced near-miss rewrites. Idempotent for clean XML."""
    if not response or "<tool_call>" not in response:
        return response

    def _sub(match: re.Match) -> str:
        body = match.group(1)
        new_body, _ = _rewrite_tool_call_body(body)
        return "<tool_call>" + new_body + "</tool_call>"

    return _TOOL_CALL_RE.sub(_sub, response)


def near_miss_shapes_applied(response: str) -> List[str]:
    """Diagnostic: which shape ids would fire (does not mutate)."""
    shapes: List[str] = []
    for match in _TOOL_CALL_RE.finditer(response or ""):
        _, applied = _rewrite_tool_call_body(match.group(1))
        shapes.extend(applied)
    return shapes


_SCREENSHOT_ACTION_RE = re.compile(
    r"<parameter=action>\s*screenshot\s*</parameter>", re.IGNORECASE | re.DOTALL
)


def apply_screenshot_noop(response: str, codes: List[str]) -> List[str]:
    """If the only computer_use intent is ``screenshot``, map to WAIT.

    Screenshot is already attached every turn by the harness. Recurring in
    Flash + Study-1 trajs (corpus count reported in instrument notes).
    Does not replace non-empty action lists (won't swallow a real click).
    """
    if codes:
        return codes
    if response and _SCREENSHOT_ACTION_RE.search(response):
        return ["WAIT"]
    return codes
