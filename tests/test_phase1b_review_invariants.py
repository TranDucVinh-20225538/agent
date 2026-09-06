#!/usr/bin/env python3
"""Phase 1B pre–Gate 0A review: prove the five required invariants (mock only)."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from generic_executor.executor import build_qwen_cuabash_agent  # noqa: E402
from generic_executor.family_config import (  # noqa: E402
    FAMILY_CONFIGS,
    assert_family_configs_transport_only,
)
from generic_executor.fake_env import FakeEnv  # noqa: E402
from generic_executor.fake_model import BASH_ONLY, TERMINATE_DONE  # noqa: E402
from generic_executor.flash_gate0_binding import (  # noqa: E402
    FLASH_GATE0A,
    assert_flash_family_matches_binding,
)
from generic_executor.openrouter_chat import (  # noqa: E402
    TransportError,
    OpenRouterChatCompletionsTransport,
)
from generic_executor.transport import install_transport  # noqa: E402


def _ok(text: str) -> Dict[str, Any]:
    return {
        "choices": [{"message": {"role": "assistant", "content": text}, "finish_reason": "stop"}]
    }


class MockHttp:
    def __init__(self, responses: List[Any]):
        self.responses = list(responses)
        self.calls: List[Tuple[str, Dict[str, str], Dict[str, Any]]] = []

    def __call__(self, url: str, headers: Dict[str, str], body: bytes, timeout: float):
        payload = json.loads(body.decode("utf-8"))
        self.calls.append((url, dict(headers), payload))
        if not self.responses:
            raise TransportError("mock exhausted")
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


class TestPhase1BReviewInvariants(unittest.TestCase):
    """Five review gates before Gate 0A Flash."""

    # ----- 1. Full-history semantics -----
    def test_1_full_history_bash_then_done(self):
        mock = MockHttp([_ok(BASH_ONLY), _ok(TERMINATE_DONE)])
        transport = OpenRouterChatCompletionsTransport(
            api_key="sk-or-test",
            family=FAMILY_CONFIGS["flash"],
            http_post=mock,
        )
        env = FakeEnv()
        agent = build_qwen_cuabash_agent(
            env=env, model_name=FLASH_GATE0A.model_id
        )
        install_transport(agent._inner, transport)
        agent.reset()
        instruction = "ORIGINAL_TASK_TOKEN_XYZ"
        obs = env._get_obs()

        # Turn 1: bash-only → TOOL_CALL semantics (pending bash)
        r1, actions1 = agent.predict(instruction, obs)
        self.assertEqual(actions1, [])
        self.assertTrue(agent._pending_bash_result)
        obs = env._get_obs()  # screenshot cadence refresh (runner TOOL_CALL path)

        # Turn 2: must continue with new obs + bash injection
        r2, actions2 = agent.predict(instruction, obs)
        self.assertEqual(actions2, ["DONE"])

        self.assertEqual(len(mock.calls), 2)
        body1 = mock.calls[0][2]
        body2 = mock.calls[1][2]
        msgs1 = body1["messages"]
        msgs2 = body2["messages"]

        # system prompt present both turns
        self.assertEqual(msgs1[0]["role"], "system")
        self.assertEqual(msgs2[0]["role"], "system")
        sys_blob = str(msgs2[0]["content"])
        self.assertIn("computer_use", sys_blob)
        self.assertIn("1000x1000", sys_blob)
        self.assertIn("<function=bash>", sys_blob)

        # original task in first user instruction window
        self.assertIn(instruction, str(msgs1))
        self.assertIn(instruction, str(msgs2))

        # turn-1 assistant response retained in turn-2 history (content may be
        # multipart text parts — match distinctive frozen fragments).
        blob2 = str(msgs2)
        self.assertTrue(any(m.get("role") == "assistant" for m in msgs2))
        self.assertIn("Inspect files via bash", blob2)
        self.assertIn("<function=bash>", blob2)
        self.assertIn("echo hello_from_bash", blob2)
        # exact bash result injection (frozen <tool_response> semantics)
        self.assertIn("tool_response", blob2)
        self.assertIn("FAKE_BASH_OK:echo hello_from_bash", blob2)
        # observation/screenshot cadence: turn 2 has more image parts than turn 1
        def count_images(msgs):
            n = 0
            for m in msgs:
                c = m.get("content")
                if isinstance(c, list):
                    for p in c:
                        if isinstance(p, dict) and p.get("type") == "image_url":
                            n += 1
            return n

        self.assertGreaterEqual(count_images(msgs1), 1)
        self.assertGreaterEqual(count_images(msgs2), count_images(msgs1))

        # request2 standalone: contains request1 context
        self.assertGreater(len(msgs2), len(msgs1))

    def test_1_transport_does_not_mutate_caller_history(self):
        mock = MockHttp([_ok("ok")])
        t = OpenRouterChatCompletionsTransport(
            api_key="k", family=FAMILY_CONFIGS["flash"], http_post=mock
        )
        messages = [
            {"role": "system", "content": [{"type": "text", "text": "sys"}]},
            {"role": "user", "content": "u"},
        ]
        snapshot = copy.deepcopy(messages)
        t.complete(messages, model=FLASH_GATE0A.model_id)
        self.assertEqual(messages, snapshot)

    # ----- 2. Family config transport-only -----
    def test_2_family_config_no_protocol_fields(self):
        assert_family_configs_transport_only()
        for name, cfg in FAMILY_CONFIGS.items():
            self.assertTrue(cfg.openrouter_model)
            self.assertNotIn("system", cfg.openrouter_model.lower() + cfg.notes.lower()[:0])
            # no prompt / schema keys in allow_keys or extra_body
            for k in cfg.allow_keys:
                self.assertNotIn(k, {"system_prompt", "tools", "parser"})
            self.assertNotIn("tools", cfg.extra_body)
            self.assertNotIn("system_prompt", cfg.extra_body)

    # ----- 3. Response extraction fail-closed -----
    def test_3_extraction_matrix(self):
        cases = [
            ({"choices": []}, "missing choices"),
            ({"choices": [{"message": None}]}, "missing message"),
            ({"choices": [{"message": {"role": "assistant", "content": None}}]}, "empty"),
            ({"choices": [{"message": {"role": "assistant", "content": "   "}}]}, "blank"),
            (
                {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": None,
                                "refusal": "I cannot help with that.",
                            }
                        }
                    ]
                },
                "refusal",
            ),
            (
                {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [{"id": "x", "type": "function"}],
                            }
                        }
                    ]
                },
                "tool_calls",
            ),
            (
                {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": "Action: ignore me",
                                "tool_calls": [{"id": "x"}],
                            }
                        }
                    ]
                },
                "tool_calls",  # even with content — must NOT silently accept
            ),
            ("not-a-dict", "not a JSON object"),
        ]
        for payload, needle in cases:
            with self.subTest(needle=needle):
                with self.assertRaises(TransportError) as ctx:
                    OpenRouterChatCompletionsTransport.extract_text(payload)
                self.assertIn("fail-closed", str(ctx.exception).lower())

    # ----- 4. Stateless complete requests -----
    def test_4_stateless_request2_self_contained(self):
        mock = MockHttp([_ok("a"), _ok("b")])
        t = OpenRouterChatCompletionsTransport(
            api_key="sk-or-test",
            family=FAMILY_CONFIGS["flash"],
            http_post=mock,
        )
        h1 = [
            {"role": "system", "content": "SYS"},
            {"role": "user", "content": "TASK"},
        ]
        h2 = h1 + [
            {"role": "assistant", "content": "A1"},
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url": "data:image/png;base64,xx"}}, {"type": "text", "text": "TASK"}]},
        ]
        t.complete(h1, model=FLASH_GATE0A.model_id)
        t.complete(h2, model=FLASH_GATE0A.model_id)
        b1 = mock.calls[0][2]
        b2 = mock.calls[1][2]
        for body in (b1, b2):
            for banned in (
                "previous_response_id",
                "conversation_id",
                "response_id",
                "tools",
            ):
                self.assertNotIn(banned, body)
        # request_2.history ⊇ request_1 context
        self.assertEqual(b2["messages"][0]["content"], "SYS")
        self.assertEqual(b2["messages"][1]["content"], "TASK")
        self.assertEqual(b2["messages"][2]["content"], "A1")
        self.assertGreater(len(b2["messages"]), len(b1["messages"]))

    # ----- 5. Flash binding matches Paper-2 SMALL candidate -----
    def test_5_flash_binding(self):
        assert_flash_family_matches_binding()
        self.assertEqual(FLASH_GATE0A.model_id, "qwen/qwen3.8-flash")
        self.assertEqual(
            FLASH_GATE0A.endpoint,
            "https://openrouter.ai/api/v1/chat/completions",
        )
        self.assertEqual(FLASH_GATE0A.lane, "SMALL")
        self.assertEqual(FLASH_GATE0A.key_env_source, "OPENROUTER_API_KEY_SMALL")
        self.assertEqual(FAMILY_CONFIGS["flash"].openrouter_model, FLASH_GATE0A.model_id)
        # small_lane.sh must still name the same model
        small = (ROOT / "scripts" / "paper2_exec_small_lane.sh").read_text()
        self.assertIn("qwen/qwen3.8-flash", small)
        self.assertIn("OPENROUTER_API_KEY_SMALL", small)
        run = (ROOT / "scripts" / "paper2_exec_run.sh").read_text()
        self.assertIn("https://openrouter.ai/api/v1", run)
        # Transport uses exact model id — no silent remap
        mock = MockHttp([_ok(TERMINATE_DONE)])
        t = OpenRouterChatCompletionsTransport(
            api_key="sk-or-test",
            family=FAMILY_CONFIGS["flash"],
            http_post=mock,
        )
        t.complete([{"role": "user", "content": "x"}], model=FLASH_GATE0A.model_id)
        self.assertEqual(mock.calls[0][2]["model"], "qwen/qwen3.8-flash")
        self.assertEqual(mock.calls[0][0], FLASH_GATE0A.endpoint)
        for other in FLASH_GATE0A.forbid_fallback_models:
            self.assertNotEqual(mock.calls[0][2]["model"], other)


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
