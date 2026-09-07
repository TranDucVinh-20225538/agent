#!/usr/bin/env python3
"""Gate 0A instrument fixes — near-miss XML + silent-abort markers (test-first).

Fixtures are byte-derived from Flash diagnostic trajs under
``tests/fixtures/gate0a_near_miss/``.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "external" / "MyPCBench-main" / "agent-harness"))

from generic_executor.near_miss_xml import (  # noqa: E402
    near_miss_shapes_applied,
    normalize_near_miss_xml,
)

FIX = ROOT / "tests" / "fixtures" / "gate0a_near_miss"


def _load(name: str) -> str:
    return (FIX / name).read_text()


def _parse_codes(response: str):
    from agents.vendored_paper_results.qwen35vl_agent import Qwen35VLAgent

    agent = Qwen35VLAgent(enable_thinking=False, temperature=0.0)
    _instr, codes = agent.parse_response(
        response, original_width=1280, original_height=800
    )
    return codes


def _extract_bash(response: str):
    from agents.qwen_cua import _extract_bash_command

    return _extract_bash_command(response)


def _extract_bash_pristine(response: str):
    """Pre-instrument bash extractor (no near-miss normalize) for BEFORE baselines."""
    import re

    for tc in re.finditer(r"<tool_call>(.*?)</tool_call>", response or "", re.DOTALL):
        body = tc.group(1)
        if "<function=bash>" not in body:
            continue
        m = re.search(r"<parameter=command>\s*(.*?)\s*</parameter>", body, re.DOTALL)
        if m:
            return m.group(1).strip()
    return None


class TestBeforePatchBaseline(unittest.TestCase):
    """Document pre-patch failure: raw fixtures parse to empty / no bash."""

    def test_before_shape1_wait_empty(self):
        raw = _load("shape1_tool_call_wait.txt")
        self.assertIn("<function=tool_call>", raw)
        codes = _parse_codes(raw)
        self.assertEqual(codes, [], msg="BEFORE: shape1 must fail closed on frozen parser")

    def test_before_shape2_parameter_computer_use_empty(self):
        raw = _load("shape2_parameter_computer_use.txt")
        self.assertIn("<parameter=computer_use>", raw)
        codes = _parse_codes(raw)
        self.assertEqual(codes, [])

    def test_before_shape3_mcp_bash_no_extract(self):
        raw = _load("shape3_tool_call_mcp_bash.txt")
        self.assertIsNone(_extract_bash_pristine(raw))

    def test_before_shape4_orphan_command_no_extract(self):
        raw = _load("shape4_orphan_command.txt")
        self.assertIsNone(_extract_bash_pristine(raw))

    def test_before_shape5_parameter_bash_no_extract(self):
        raw = _load("shape5_parameter_bash.txt")
        self.assertIsNone(_extract_bash_pristine(raw))

    def test_before_screenshot_empty(self):
        raw = _load("screenshot_noop.txt")
        codes = _parse_codes(raw)
        self.assertEqual(codes, [], msg="BEFORE: screenshot action yields empty codes")


class TestNearMissNormalizeAfter(unittest.TestCase):
    def test_shape1_wait_becomes_WAIT(self):
        raw = _load("shape1_tool_call_wait.txt")
        self.assertIn("shape1_function_tool_call_computer_use", near_miss_shapes_applied(raw))
        fixed = normalize_near_miss_xml(raw)
        self.assertIn("<function=computer_use>", fixed)
        self.assertNotIn("<function=tool_call>", fixed)
        codes = _parse_codes(fixed)
        self.assertEqual(codes, ["WAIT"])

    def test_shape1_key_becomes_hotkey(self):
        raw = _load("shape1_tool_call_key.txt")
        fixed = normalize_near_miss_xml(raw)
        codes = _parse_codes(fixed)
        self.assertTrue(codes and codes[0].startswith("pyautogui."))

    def test_shape2_parameter_computer_use_click(self):
        raw = _load("shape2_parameter_computer_use.txt")
        self.assertIn("shape2_parameter_computer_use", near_miss_shapes_applied(raw))
        fixed = normalize_near_miss_xml(raw)
        self.assertIn("<function=computer_use>", fixed)
        codes = _parse_codes(fixed)
        self.assertTrue(any("pyautogui.click" in c for c in codes))

    def test_shape3_mcp_bash_extract(self):
        raw = _load("shape3_tool_call_mcp_bash.txt")
        self.assertIn("shape3_function_tool_call_bash", near_miss_shapes_applied(raw))
        fixed = normalize_near_miss_xml(raw)
        cmd = _extract_bash(fixed)
        self.assertIsNotNone(cmd)
        self.assertIn("for p in 3001", cmd)

    def test_shape4_orphan_command(self):
        raw = _load("shape4_orphan_command.txt")
        self.assertIn("shape4_orphan_command", near_miss_shapes_applied(raw))
        fixed = normalize_near_miss_xml(raw)
        cmd = _extract_bash(fixed)
        self.assertIsNotNone(cmd)
        self.assertIn("port $p", cmd)

    def test_shape5_parameter_bash(self):
        raw = _load("shape5_parameter_bash.txt")
        self.assertIn("shape5_parameter_bash", near_miss_shapes_applied(raw))
        fixed = normalize_near_miss_xml(raw)
        self.assertIn("<function=bash>", fixed)
        cmd = _extract_bash(fixed)
        self.assertIsNotNone(cmd)
        self.assertIn("Follow redirects", cmd)

    def test_clean_computer_use_untouched(self):
        clean = (
            "<tool_call>\n<function=computer_use>\n"
            "<parameter=action>\nwait\n</parameter>\n"
            "</function>\n</tool_call>"
        )
        self.assertEqual(normalize_near_miss_xml(clean), clean)
        self.assertEqual(near_miss_shapes_applied(clean), [])

    def test_screenshot_maps_to_WAIT_noop_via_helper(self):
        # Instrument maps screenshot → WAIT after normalize+parse (see qwen_cua hook).
        from generic_executor.near_miss_xml import _COMPUTER_USE_ACTIONS

        self.assertIn("screenshot", _COMPUTER_USE_ACTIONS)
        raw = _load("screenshot_noop.txt")
        fixed = normalize_near_miss_xml(raw)
        # Still empty under vendored parser until screenshot branch added in wrapper.
        codes = _parse_codes(fixed)
        # After instrument: apply_screenshot_noop
        from generic_executor.near_miss_xml import apply_screenshot_noop

        codes2 = apply_screenshot_noop(fixed, codes)
        self.assertEqual(codes2, ["WAIT"])

    def test_screenshot_noop_does_not_swallow_click(self):
        from generic_executor.near_miss_xml import apply_screenshot_noop

        raw = (
            "<tool_call>\n<function=computer_use>\n"
            "<parameter=action>\nleft_click\n</parameter>\n"
            "<parameter=coordinate>\n[100, 200]\n</parameter>\n"
            "</function>\n</tool_call>\n"
            "<tool_call>\n<function=computer_use>\n"
            "<parameter=action>\nscreenshot\n</parameter>\n"
            "</function>\n</tool_call>"
        )
        codes = _parse_codes(raw)
        self.assertTrue(any("click" in c for c in codes))
        out = apply_screenshot_noop(raw, codes)
        self.assertTrue(any("click" in c for c in out))
        # screenshot alone would add WAIT only when codes empty
        self.assertFalse(out == ["WAIT"])


class TestSilentDeathMarkerSemantics(unittest.TestCase):
    def test_silent_legs_had_no_terminal_marker(self):
        for name in ("silent_contradiction-f022_G0.json", "silent_preference_inference-f010_G1.json"):
            meta = json.loads((FIX / name).read_text())
            self.assertFalse(meta["has_predict_crash"])
            self.assertFalse(meta["has_executor_exception"])
            # G0 ended on TOOL_CALL without EMPTY_XML abort row
            if meta["leg"].endswith("/G0"):
                self.assertEqual(meta["last_action"], "TOOL_CALL")
                self.assertFalse(meta["has_empty_xml"])


if __name__ == "__main__":
    raise SystemExit(unittest.main(verbosity=2))
