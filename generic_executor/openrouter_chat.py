#!/usr/bin/env python3
"""OpenRouter Chat Completions transport (stateless, prompt/XML protocol).

Phase 1B: serialization + extraction only. Tests inject a mock HTTP client.
Live calls are intentionally not used here.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from generic_executor.family_config import FamilyConfig, filter_generation

DEFAULT_OPENROUTER_BASE = "https://openrouter.ai/api/v1"
CHAT_COMPLETIONS_PATH = "/chat/completions"

# Forbidden on this transport — would break Gate −2 frozen protocol / OR semantics.
_FORBIDDEN_BODY_KEYS = frozenset(
    {
        "previous_response_id",
        "tools",
        "tool_choice",
        "functions",
        "function_call",
    }
)


class TransportError(RuntimeError):
    """Fail-closed transport failure (malformed / missing upstream payload)."""


HttpPost = Callable[[str, Dict[str, str], bytes, float], Dict[str, Any]]


def default_http_post(url: str, headers: Dict[str, str], body: bytes, timeout: float) -> Dict[str, Any]:
    """Real urllib POST — not used by Phase 1B unit tests."""
    req = Request(url, data=body, headers=headers, method="POST")
    try:
        with urlopen(req, timeout=timeout) as resp:  # noqa: S310 — caller opts in
            raw = resp.read()
            return json.loads(raw.decode("utf-8"))
    except HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace") if e.fp else str(e)
        raise TransportError(f"HTTP {e.code}: {detail}") from e
    except URLError as e:
        raise TransportError(f"network error: {e}") from e
    except json.JSONDecodeError as e:
        raise TransportError(f"non-JSON response: {e}") from e


@dataclass
class OpenRouterChatCompletionsTransport:
    """Generic OpenRouter ``/chat/completions`` transport + family config.

    Every call sends the **full** ``messages`` array (client-rebuilt history).
    No server-side conversation id. No native tool schema.
    """

    api_key: str
    family: FamilyConfig
    base_url: str = DEFAULT_OPENROUTER_BASE
    timeout_s: float = 120.0
    http_referer: str = "https://github.com/TranDucVinh-20225538/agent"
    http_post: HttpPost = field(default=default_http_post)
    # Audit log for tests / debugging (never secrets).
    requests_log: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def endpoint(self) -> str:
        return self.base_url.rstrip("/") + CHAT_COMPLETIONS_PATH

    def build_request(
        self,
        messages: List[Dict[str, Any]],
        *,
        model: Optional[str] = None,
        generation: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not messages:
            raise TransportError("fail-closed: empty messages (would drop history)")
        # Deep-copy so transport never mutates caller-owned history objects.
        import copy

        msgs = copy.deepcopy(messages)
        if any(m is None for m in msgs):
            raise TransportError("fail-closed: None message in history")
        # Reject provider-state fields if a caller smuggled them into a message.
        for m in msgs:
            if not isinstance(m, dict):
                raise TransportError("fail-closed: non-dict message in history")
            for bad in ("previous_response_id", "conversation_id"):
                if bad in m:
                    raise TransportError(f"fail-closed: message carries {bad}")

        body: Dict[str, Any] = {
            "model": model or self.family.openrouter_model,
            "messages": msgs,
        }
        body.update(filter_generation(self.family, generation))
        if self.family.extra_body:
            # Merge extra_body carefully — never allow forbidden keys.
            for k, v in self.family.extra_body.items():
                if k in _FORBIDDEN_BODY_KEYS:
                    raise TransportError(f"forbidden extra_body key: {k}")
                body[k] = v

        for bad in _FORBIDDEN_BODY_KEYS:
            if bad in body:
                raise TransportError(f"forbidden request key: {bad}")

        return body

    def build_headers(self) -> Dict[str, str]:
        if not self.api_key:
            raise TransportError("fail-closed: missing api_key")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.http_referer,
            "X-Title": "paper2-generic-executor",
        }

    @staticmethod
    def extract_text(response_json: Any) -> str:
        """Extract plain assistant text for the frozen parser. Fail closed."""
        if not isinstance(response_json, dict):
            raise TransportError("fail-closed: response is not a JSON object")
        choices = response_json.get("choices")
        if not isinstance(choices, list) or not choices:
            raise TransportError("fail-closed: missing choices")
        choice0 = choices[0]
        if not isinstance(choice0, dict):
            raise TransportError("fail-closed: choices[0] malformed")
        message = choice0.get("message")
        if not isinstance(message, dict):
            raise TransportError("fail-closed: missing message")
        # Reject provider-pre-executed / native tool payloads even if content set.
        if message.get("tool_calls") or message.get("function_call"):
            raise TransportError(
                "fail-closed: provider tool_calls/function_call present "
                "(native tools not allowed on frozen XML protocol)"
            )
        content = message.get("content")
        refusal = message.get("refusal")
        if isinstance(refusal, str) and refusal.strip() and (
            content is None or (isinstance(content, str) and not content.strip())
        ):
            raise TransportError("fail-closed: refusal-only response")
        if content is None:
            reasoning = message.get("reasoning") or message.get("reasoning_content")
            if isinstance(reasoning, str) and reasoning.strip():
                return reasoning
            raise TransportError("fail-closed: empty message.content")
        if isinstance(content, str):
            if not content.strip():
                raise TransportError("fail-closed: blank message.content")
            return content
        if isinstance(content, list):
            parts: List[str] = []
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    parts.append(str(part.get("text") or ""))
                elif isinstance(part, str):
                    parts.append(part)
            text = "".join(parts)
            if not text.strip():
                raise TransportError("fail-closed: empty multipart content")
            return text
        raise TransportError("fail-closed: unsupported content type")

    def complete(
        self,
        messages: List[Dict[str, Any]],
        *,
        model: str,
        generation: Dict[str, Any] | None = None,
    ) -> str:
        body = self.build_request(messages, model=model or self.family.openrouter_model, generation=generation)
        headers = self.build_headers()
        raw = json.dumps(body).encode("utf-8")
        self.requests_log.append(
            {
                "url": self.endpoint,
                "model": body["model"],
                "n_messages": len(body["messages"]),
                "has_previous_response_id": "previous_response_id" in body,
                "has_tools": "tools" in body,
                "header_auth_prefix": headers["Authorization"][:12],
                "body_keys": sorted(body.keys()),
            }
        )
        resp = self.http_post(self.endpoint, headers, raw, self.timeout_s)
        return self.extract_text(resp)
