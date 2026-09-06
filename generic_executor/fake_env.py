#!/usr/bin/env python3
"""Fake QEMU env implementing the MyPCBenchEnv step contract used by qwen_cuabash.

No network, no QEMU. Records actions for deterministic tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from generic_executor.pngutil import solid_png


@dataclass
class FakeEnv:
    """Subset of MyPCBenchEnv used by the frozen Qwen path + react loop."""

    screen_size: Tuple[int, int] = (1280, 800)
    instruction: str = "test task"
    action_history: List[Any] = field(default_factory=list)
    bash_history: List[str] = field(default_factory=list)
    step_no: int = 0
    # Incrementing pixel channel so screenshots are distinct across steps.
    _shot_i: int = 0

    def _execute_command(self, command: str, shell: bool = True) -> Dict[str, Any]:
        self.bash_history.append(command)
        return {
            "output": f"FAKE_BASH_OK:{command}",
            "error": "",
            "returncode": 0,
        }

    def _get_screenshot(self) -> bytes:
        self._shot_i += 1
        # Distinct RGB so history/screenshot placement tests can detect cadence.
        v = self._shot_i % 200
        return solid_png(self.screen_size[0], self.screen_size[1], (v, 40, 80))

    def _get_obs(self) -> Dict[str, Any]:
        return {
            "screenshot": self._get_screenshot(),
            "accessibility_tree": None,
            "terminal": None,
            "instruction": self.instruction,
        }

    def step(self, action, pause: float = 0.0) -> Tuple[Dict, float, bool, Dict]:
        # pause ignored (deterministic / zero-API tests).
        self.step_no += 1
        self.action_history.append(action)
        done = False
        info: Dict[str, Any] = {}
        reward = 0.0
        if isinstance(action, str):
            upper = action.strip().upper()
            if upper == "WAIT":
                return self._get_obs(), reward, False, info
            if upper == "DONE":
                return self._get_obs(), reward, True, {"done": True}
            if upper == "FAIL":
                return self._get_obs(), reward, True, {"fail": True}
        # GUI / pyautogui string — record only.
        return self._get_obs(), reward, done, info
