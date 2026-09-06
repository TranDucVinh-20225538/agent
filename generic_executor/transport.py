#!/usr/bin/env python3
"""Transport seam for the generic executor (Phase 1B).

Contract (Gate −2):
  input  = frozen client-rebuilt ``messages`` (system + history + observation)
  output = raw assistant text for the frozen XML/prompt parser

Adapters MUST NOT:
  - change system prompt / XML grammar
  - send native ``tools=[...]``
  - use ``previous_response_id`` / server-managed state
  - execute tools provider-side
"""

from __future__ import annotations

from typing import Any, Dict, List, Protocol, runtime_checkable


@runtime_checkable
class Transport(Protocol):
    """Stateless completion: full history every call → plain text."""

    def complete(
        self,
        messages: List[Dict[str, Any]],
        *,
        model: str,
        generation: Dict[str, Any] | None = None,
    ) -> str:
        """Return assistant text. Fail closed on missing/malformed upstream data.

        ``generation`` holds optional sampling knobs (temperature, top_p, …).
        Implementations may omit non-portable keys per family config.
        """
        ...


def apply_system_addenda(
    messages: List[Dict[str, Any]],
    *,
    mypcbench_context: str = "",
    bash_tool_description: str = "",
) -> List[Dict[str, Any]]:
    """Same addenda injection as ``_Qwen35VLPatched.call_llm`` (frozen).

    Mutates and returns ``messages`` for transport serialization.
    """
    addendum_parts: List[str] = []
    if mypcbench_context:
        addendum_parts.append(mypcbench_context)
    if bash_tool_description:
        addendum_parts.append(bash_tool_description)
    if not messages or not addendum_parts:
        return messages
    if messages[0].get("role") != "system":
        return messages
    addendum = "\n\n" + "\n\n".join(addendum_parts)
    content = messages[0].get("content")
    if isinstance(content, list):
        messages[0]["content"] = content + [{"type": "text", "text": addendum}]
    elif isinstance(content, str):
        messages[0]["content"] = content + addendum
    return messages


def install_transport(inner_agent: Any, transport: Transport) -> None:
    """Replace vendored ``call_llm`` with a Transport while keeping addenda."""

    def call_llm(payload: Dict[str, Any], model: str) -> str:  # type: ignore[override]
        msgs = payload.get("messages") or []
        apply_system_addenda(
            msgs,
            mypcbench_context=getattr(inner_agent, "_mypcbench_context", "") or "",
            bash_tool_description=getattr(inner_agent, "_bash_tool_description", "") or "",
        )
        generation = {
            "max_tokens": payload.get("max_tokens"),
            "temperature": payload.get("temperature"),
            "top_p": payload.get("top_p"),
        }
        # Optional knobs from agent attrs (family config decides portability).
        for attr in ("presence_penalty", "top_k", "min_p", "repetition_penalty", "enable_thinking"):
            if hasattr(inner_agent, attr):
                generation[attr] = getattr(inner_agent, attr)
        return transport.complete(msgs, model=model, generation=generation)

    inner_agent.call_llm = call_llm  # type: ignore[method-assign]
