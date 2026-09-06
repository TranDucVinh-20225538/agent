#!/usr/bin/env python3
"""Phase 1B — OpenRouter chat-completions transport tests (mock HTTP, zero API)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from generic_executor.executor import run_executor  # noqa: E402
from generic_executor.family_config import FAMILY_CONFIGS, filter_generation  # noqa: E402
from generic_executor.fake_model import TERMINATE_DONE  # noqa: E402
from generic_executor.openrouter_chat import (  # noqa: E402
    TransportError,
    OpenRouterChatCompletionsTransport,
)
from generic_executor.transport import install_transport  # noqa: E402


def _ok_response(text: str) -> Dict[str, Any]:
    return {
        "id": "gen-test",
        "choices": [{"message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
    }


class MockHttp:
    def __init__(self, responses: List[Any]):
        self.responses = list(responses)
        self.calls: List[Tuple[str, Dict[str, str], Dict[str, Any]]] = []

    def __call__(
        self, url: str, headers: Dict[str, str], body: bytes, timeout: float
    ) -> Dict[str, Any]:
        payload = json.loads(body.decode("utf-8"))
        self.calls.append((url, headers, payload))
        if not self.responses:
            raise TransportError("mock exhausted")
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


class TestOpenRouterChatTransport(unittest.TestCase):
    def _transport(self, family: str, mock: MockHttp, key: str = "sk-test-key"):
        return OpenRouterChatCompletionsTransport(
            api_key=key,
            family=FAMILY_CONFIGS[family],
            http_post=mock,
        )

    def test_endpoint_and_auth(self):
        mock = MockHttp([_ok_response(TERMINATE_DONE)])
        t = self._transport("flash", mock)
        text = t.complete(
            [{"role": "user", "content": "hi"}],
            model=FAMILY_CONFIGS["flash"].openrouter_model,
            generation={"temperature": 0.0, "max_tokens": 128},
        )
        self.assertEqual(text, TERMINATE_DONE)
        url, headers, body = mock.calls[0]
        self.assertEqual(url, "https://openrouter.ai/api/v1/chat/completions")
        self.assertEqual(headers["Authorization"], "Bearer sk-test-key")
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertNotIn("previous_response_id", body)
        self.assertNotIn("tools", body)
        self.assertIn("messages", body)

    def test_stateless_full_history_each_turn(self):
        mock = MockHttp([_ok_response("r1"), _ok_response("r2")])
        t = self._transport("gpt_family", mock)
        hist1 = [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "u1"},
        ]
        hist2 = hist1 + [
            {"role": "assistant", "content": "a1"},
            {"role": "user", "content": "u2"},
        ]
        t.complete(hist1, model="openai/gpt-5.5")
        t.complete(hist2, model="openai/gpt-5.5")
        self.assertEqual(len(mock.calls), 2)
        _, _, b1 = mock.calls[0]
        _, _, b2 = mock.calls[1]
        self.assertEqual(len(b1["messages"]), 2)
        self.assertEqual(len(b2["messages"]), 4)
        # Turn 2 still carries system + full prior turns (no silent drop).
        self.assertEqual(b2["messages"][0]["content"], "sys")
        self.assertEqual(b2["messages"][1]["content"], "u1")
        self.assertEqual(b2["messages"][2]["content"], "a1")
        self.assertNotIn("previous_response_id", b1)
        self.assertNotIn("previous_response_id", b2)
        self.assertTrue(t.requests_log[0]["has_previous_response_id"] is False)
        self.assertTrue(t.requests_log[0]["has_tools"] is False)

    def test_no_tools_even_if_family_extra_tries(self):
        from generic_executor.family_config import FamilyConfig

        bad = FamilyConfig(
            family="bad",
            openrouter_model="x",
            extra_body={"tools": [{"type": "function"}]},
        )
        mock = MockHttp([])
        t = OpenRouterChatCompletionsTransport(api_key="k", family=bad, http_post=mock)
        with self.assertRaises(TransportError) as ctx:
            t.build_request([{"role": "user", "content": "x"}])
        self.assertIn("forbidden", str(ctx.exception))

    def test_fail_closed_empty_messages(self):
        mock = MockHttp([])
        t = self._transport("flash", mock)
        with self.assertRaises(TransportError):
            t.complete([], model="qwen/qwen3.8-flash")

    def test_fail_closed_missing_api_key(self):
        mock = MockHttp([])
        t = self._transport("flash", mock, key="")
        with self.assertRaises(TransportError):
            t.build_headers()

    def test_fail_closed_malformed_response(self):
        mock = MockHttp([{"choices": []}])
        t = self._transport("claude_family", mock)
        with self.assertRaises(TransportError):
            t.complete([{"role": "user", "content": "x"}], model="anthropic/claude-opus-4.6")

    def test_fail_closed_provider_tool_calls(self):
        mock = MockHttp(
            [
                {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [{"id": "1", "type": "function"}],
                            }
                        }
                    ]
                }
            ]
        )
        t = self._transport("gpt_family", mock)
        with self.assertRaises(TransportError) as ctx:
            t.complete([{"role": "user", "content": "x"}], model="openai/gpt-5.5")
        self.assertIn("tool_calls", str(ctx.exception))

    def test_fail_closed_empty_content(self):
        mock = MockHttp([{"choices": [{"message": {"role": "assistant", "content": None}}]}])
        t = self._transport("flash", mock)
        with self.assertRaises(TransportError):
            t.complete([{"role": "user", "content": "x"}], model="qwen/qwen3.8-flash")

    def test_family_generation_filter_omits_nonportable(self):
        cfg = FAMILY_CONFIGS["claude_family"]
        filtered = filter_generation(
            cfg,
            {
                "temperature": 0.0,
                "top_p": 0.9,
                "top_k": 20,
                "presence_penalty": 1.5,
                "max_tokens": 1024,
            },
        )
        self.assertIn("temperature", filtered)
        self.assertIn("max_tokens", filtered)
        self.assertNotIn("top_k", filtered)
        self.assertNotIn("presence_penalty", filtered)

    def test_raw_text_reaches_frozen_parser_via_executor(self):
        """Mocked OpenRouter → install_transport → DONE parse (no real HTTP)."""
        mock = MockHttp([_ok_response(TERMINATE_DONE)])
        transport = self._transport("flash", mock)

        # Monkeypatch build path: run_executor uses FakeModel; here we
        # exercise transport through a thin agent install like Phase 1A.
        from generic_executor.executor import build_qwen_cuabash_agent
        from generic_executor.fake_env import FakeEnv
        from paper2_traj_terminal import inspect_last_action
        import json as _json

        env = FakeEnv()
        agent = build_qwen_cuabash_agent(env=env, model_name=FAMILY_CONFIGS["flash"].openrouter_model)
        install_transport(agent._inner, transport)
        agent.reset()
        obs = env._get_obs()
        response, actions = agent.predict("finish", obs)
        self.assertEqual(response, TERMINATE_DONE)
        self.assertEqual(actions, ["DONE"])
        # Full history was POSTed once
        self.assertEqual(len(mock.calls), 1)
        _, _, body = mock.calls[0]
        self.assertGreaterEqual(len(body["messages"]), 2)
        self.assertEqual(body["messages"][0]["role"], "system")
        # System still has frozen computer_use / 1000x1000 markers
        sys_blob = str(body["messages"][0]["content"])
        self.assertIn("computer_use", sys_blob)
        self.assertIn("1000x1000", sys_blob)
        self.assertIn("<function=bash>", sys_blob)

    def test_executor_multi_turn_history_not_dropped(self):
        from generic_executor.fake_model import CLICK_ONCE, TERMINATE_DONE

        mock = MockHttp([_ok_response(CLICK_ONCE), _ok_response(TERMINATE_DONE)])
        transport = OpenRouterChatCompletionsTransport(
            api_key="sk-test",
            family=FAMILY_CONFIGS["flash"],
            http_post=mock,
        )

        # Custom run: reuse executor loop by swapping install after build —
        # simplest path: subclass FakeModel style via run_executor replacement.
        from generic_executor.executor import build_qwen_cuabash_agent, _append_traj
        from generic_executor.fake_env import FakeEnv
        from pathlib import Path

        with tempfile.TemporaryDirectory() as td:
            env = FakeEnv()
            agent = build_qwen_cuabash_agent(
                env=env, model_name=FAMILY_CONFIGS["flash"].openrouter_model
            )
            install_transport(agent._inner, transport)
            agent.reset()
            traj = Path(td) / "traj.jsonl"
            instruction = "task"
            obs = env._get_obs()
            # turn 1
            response, actions = agent.predict(instruction, obs)
            for a in actions:
                obs, _, done, info = env.step(a, 0.0)
                _append_traj(
                    traj,
                    {"step_num": 1, "action": a, "response": response, "done": done, "info": info},
                )
            # turn 2
            response2, actions2 = agent.predict(instruction, obs)
            for a in actions2:
                obs, _, done, info = env.step(a, 0.0)
                _append_traj(
                    traj,
                    {"step_num": 2, "action": a, "response": response2, "done": done, "info": info},
                )
            self.assertEqual(len(mock.calls), 2)
            n1 = len(mock.calls[0][2]["messages"])
            n2 = len(mock.calls[1][2]["messages"])
            self.assertGreater(n2, n1)
            # No conversation id / previous_response_id across turns
            for _, _, body in mock.calls:
                self.assertNotIn("previous_response_id", body)
                self.assertNotIn("tools", body)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
