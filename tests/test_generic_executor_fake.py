#!/usr/bin/env python3
"""Phase 1 Commit A — deterministic fake-model tests for generic executor.

Zero-API, zero-QEMU. Verifies frozen protocol behavior via FakeModel scripts.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from generic_executor.executor import (  # noqa: E402
    FREEZE_NOTE,
    PROTOCOL_SPEC,
    run_executor,
    system_prompt_has_frozen_markers,
)
from generic_executor.fake_model import (  # noqa: E402
    BASH_ONLY,
    BASH_THEN_CLICK,
    CLICK_ONCE,
    CLICK_THEN_TYPE,
    INFEASIBLE_TEXT,
    MALFORMED_XML,
    NOISE_EMPTY,
    TERMINATE_DONE,
    TERMINATE_FAIL,
    FakeModel,
)


class TestGenericExecutorFake(unittest.TestCase):
    def test_protocol_freeze_markers_in_system_prompt(self):
        fake = FakeModel(script=[TERMINATE_DONE])
        with tempfile.TemporaryDirectory() as td:
            run_executor(fake=fake, result_dir=Path(td), max_steps=5)
        m = system_prompt_has_frozen_markers(fake)
        self.assertTrue(m["has_computer_use"])
        self.assertTrue(m["has_xml_envelope"])
        self.assertTrue(m["has_1000x1000"])
        self.assertTrue(m["has_bash_addendum"])
        self.assertTrue(m["has_mypcbench_context"])
        self.assertTrue(m["has_response_format"])
        self.assertIn("Gate −2", FREEZE_NOTE)
        self.assertEqual(PROTOCOL_SPEC, "GENERIC_AGENT_PROTOCOL_SPEC.md")

    def test_single_tool_call_and_coord_scale(self):
        fake = FakeModel(script=[CLICK_ONCE, TERMINATE_DONE])
        with tempfile.TemporaryDirectory() as td:
            r = run_executor(fake=fake, result_dir=Path(td), max_steps=10)
        # relative 500,400 on 1280x800 → /999
        self.assertTrue(any("pyautogui.click(" in a for a in r.env_actions))
        click = next(a for a in r.env_actions if a.startswith("pyautogui.click("))
        # 500*1280/999 ≈ 640, 400*800/999 ≈ 320
        self.assertIn("640", click)
        self.assertIn("320", click)
        self.assertTrue(r.valid_done)
        self.assertEqual(r.terminal_status, "DONE")
        self.assertEqual(r.canonical_last_action, "DONE")

    def test_multi_tool_call_order(self):
        fake = FakeModel(script=[CLICK_THEN_TYPE, TERMINATE_DONE])
        with tempfile.TemporaryDirectory() as td:
            r = run_executor(fake=fake, result_dir=Path(td), max_steps=10)
        # First predict yields two GUI actions in order before DONE turn.
        gui_turn = next(t for t in r.turns if t.kind == "gui")
        self.assertGreaterEqual(len(gui_turn.actions), 2)
        self.assertTrue(gui_turn.actions[0].startswith("pyautogui.click"))
        # type uses clipboard paste helper — still a non-click second action
        self.assertNotEqual(gui_turn.actions[0], gui_turn.actions[1])
        # env recorded both before DONE
        self.assertGreaterEqual(len(r.env_actions), 3)  # click, type-ish, DONE
        self.assertEqual(r.env_actions[-1], "DONE")

    def test_bash_only_tool_call_round_and_injection(self):
        fake = FakeModel(script=[BASH_ONLY, TERMINATE_DONE])
        with tempfile.TemporaryDirectory() as td:
            r = run_executor(fake=fake, result_dir=Path(td), max_steps=10)
        self.assertEqual(r.bash_commands, ["echo hello_from_bash"])
        self.assertTrue(any(t.kind == "tool_call" for t in r.turns))
        self.assertTrue(any(t.traj_actions == ["TOOL_CALL"] for t in r.turns))
        # Second model call must see bash result inside Instruction via tool_response
        self.assertGreaterEqual(len(fake.calls), 2)
        second_msgs = fake.calls[1]["messages"]
        blob = str(second_msgs)
        self.assertIn("tool_response", blob)
        self.assertIn("FAKE_BASH_OK:echo hello_from_bash", blob)
        self.assertTrue(r.valid_done)

    def test_bash_plus_gui_same_response(self):
        fake = FakeModel(script=[BASH_THEN_CLICK, TERMINATE_DONE])
        with tempfile.TemporaryDirectory() as td:
            r = run_executor(fake=fake, result_dir=Path(td), max_steps=10)
        self.assertEqual(r.bash_commands[0], "pwd")
        self.assertTrue(any("pyautogui.click" in a for a in r.env_actions))
        # Bash staged for next turn even when GUI actions present
        self.assertGreaterEqual(len(fake.calls), 2)
        self.assertIn("FAKE_BASH_OK:pwd", str(fake.calls[1]["messages"]))

    def test_done_terminal(self):
        fake = FakeModel(script=[TERMINATE_DONE])
        with tempfile.TemporaryDirectory() as td:
            r = run_executor(fake=fake, result_dir=Path(td), max_steps=5)
        self.assertEqual(r.env_actions, ["DONE"])
        self.assertTrue(r.valid_done)
        self.assertEqual(r.terminal_status, "DONE")

    def test_fail_terminal_not_valid_done(self):
        fake = FakeModel(script=[TERMINATE_FAIL])
        with tempfile.TemporaryDirectory() as td:
            r = run_executor(fake=fake, result_dir=Path(td), max_steps=5)
        self.assertEqual(r.env_actions, ["FAIL"])
        self.assertFalse(r.valid_done)
        self.assertEqual(r.canonical_last_action, "FAIL")
        self.assertEqual(r.terminal_status, "TERMINAL_FAIL")

    def test_infeasible_text_fail_closed(self):
        fake = FakeModel(script=[INFEASIBLE_TEXT])
        with tempfile.TemporaryDirectory() as td:
            r = run_executor(fake=fake, result_dir=Path(td), max_steps=5)
        self.assertIn("FAIL", r.env_actions)
        self.assertFalse(r.valid_done)

    def test_malformed_xml_fail_closed_empty_retries(self):
        # Malformed then noise → EMPTY_XML path, never DONE
        fake = FakeModel(
            script=[MALFORMED_XML, NOISE_EMPTY, NOISE_EMPTY, NOISE_EMPTY, NOISE_EMPTY]
        )
        with tempfile.TemporaryDirectory() as td:
            r = run_executor(
                fake=fake, result_dir=Path(td), max_steps=10, empty_action_retries=3
            )
        self.assertFalse(r.valid_done)
        self.assertNotEqual(r.terminal_status, "DONE")
        self.assertTrue(any(t.kind == "empty_xml" for t in r.turns))
        self.assertNotIn("DONE", r.env_actions)

    def test_step_limit(self):
        # Endless clicks; max_steps=3 predict rounds with GUI
        fake = FakeModel(script=[CLICK_ONCE, CLICK_ONCE, CLICK_ONCE, CLICK_ONCE])
        with tempfile.TemporaryDirectory() as td:
            r = run_executor(fake=fake, result_dir=Path(td), max_steps=3)
        self.assertFalse(r.valid_done)
        self.assertEqual(r.stop_reason, "max_steps")
        self.assertEqual(r.fake_calls, 3)
        self.assertEqual(r.terminal_status, "TERMINAL_FAIL")

    def test_history_rebuild_screenshot_cadence_no_duplicate_stash(self):
        fake = FakeModel(script=[CLICK_ONCE, CLICK_ONCE, TERMINATE_DONE])
        with tempfile.TemporaryDirectory() as td:
            r = run_executor(fake=fake, result_dir=Path(td), max_steps=10)
        # One screenshot appended per predict; calls == predicts
        self.assertEqual(r.fake_calls, 3)
        # Message lists are rebuilt each call (not server-managed). Lengths
        # must be non-decreasing and include system + growing history.
        lengths = [c["n_messages"] for c in fake.calls]
        self.assertEqual(lengths[0], lengths[0])  # sanity
        self.assertGreaterEqual(lengths[1], lengths[0])
        self.assertGreaterEqual(lengths[2], lengths[1])
        # Each call starts with system role
        for c in fake.calls:
            self.assertEqual(c["messages"][0]["role"], "system")
        # Turns record increasing screenshot counts on the agent
        shot_counts = [t.n_screenshots_in_agent for t in r.turns if t.kind != "break"]
        self.assertEqual(shot_counts, sorted(shot_counts))
        self.assertEqual(shot_counts, list(range(1, len(shot_counts) + 1)))

    def test_traj_gate15_parity_valid_done(self):
        from paper2_traj_terminal import offline_classify_dir, runtime_classify_dir

        fake = FakeModel(script=[TERMINATE_DONE])
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            r = run_executor(fake=fake, result_dir=td_path, max_steps=5)
            rt = runtime_classify_dir(td_path)
            off = offline_classify_dir(td_path)
        self.assertEqual(rt["valid_done"], off["valid_done"])
        self.assertTrue(rt["valid_done"])
        self.assertEqual(r.valid_done, rt["valid_done"])


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
