#!/usr/bin/env python3
"""Study 2 execution-plumbing patches for MyPCBench harness (gitignored under external/).

Applied by ``study2_run_mypcbench`` at process start so the readiness gate and
INFRA_FAIL classification live in the agent repo even though ``env.py`` /
``run_mypcbench.py`` themselves are under ``external/``.

Not a methodological change — deterministic bounded waits / classification only.
"""

from __future__ import annotations

import datetime
import json
import logging
import os
import socket
import time
from typing import Any, Dict

log = logging.getLogger("mypcbench.env")


def _wait_for_apps_ready(self, timeout: float = 120.0):
    """Wait until seeded web apps accept TCP before the agent acts.

    Control API ``/health`` alone is insufficient: Firefox can hit
    ``localhost:3005`` (workbuzz) while the service is still down, burning
    agent steps on an invalid environment. Failure raises TimeoutError (infra).
    """
    if timeout is None or timeout <= 0:
        timeout = float(os.environ.get("MYPCBENCH_APPS_READY_TIMEOUT", "300"))
    else:
        timeout = float(os.environ.get("MYPCBENCH_APPS_READY_TIMEOUT", str(timeout)))

    ports_env = os.environ.get("MYPCBENCH_REQUIRE_APP_PORTS", "").strip()
    if ports_env:
        required_ports = sorted({int(p) for p in ports_env.split(",") if p.strip()})
    else:
        required_ports = sorted({port for _, _, port, _ in self._LAZY_DB_WARMUPS})

    if 3005 not in required_ports:
        required_ports = sorted(set(required_ports) | {3005})

    def _port_open(port: int) -> bool:
        try:
            with socket.create_connection((self.vm_ip, port), timeout=2.0):
                return True
        except OSError:
            return False

    start = time.time()
    pending = set(required_ports)
    log.info(
        "App readiness gate: waiting for TCP on %s (timeout=%.0fs, host=%s)",
        sorted(pending),
        timeout,
        self.vm_ip,
    )
    while time.time() - start < timeout:
        still = set()
        for port in pending:
            if _port_open(port):
                log.info("App port ready: %s (elapsed=%.1fs)", port, time.time() - start)
            else:
                still.add(port)
        pending = still
        if not pending:
            if _port_open(3005):
                log.info(
                    "App readiness gate PASS (incl. localhost:3005) in %.1fs",
                    time.time() - start,
                )
                return
            pending.add(3005)
        time.sleep(2.0)
    raise TimeoutError(
        f"App readiness gate FAIL after {timeout:.0f}s — ports still closed: "
        f"{sorted(pending)}. Classify as infrastructure failure (do not start agent steps)."
    )


def apply_env_readiness_gate() -> None:
    """Replace MyPCBenchEnv._wait_for_apps_ready (idempotent)."""
    import env as env_mod

    cls = env_mod.MyPCBenchEnv
    if getattr(cls, "_study2_apps_ready_patched", False):
        return
    cls._wait_for_apps_ready = _wait_for_apps_ready

    # Ensure dedicated apps budget at the Control-API call site.
    orig_ready = cls._wait_for_ready

    def _wait_for_ready(self, timeout=None):
        # Run upstream readiness (Control API + whatever it calls). If upstream
        # still has a no-op apps stub, we already replaced the method. If
        # upstream passes a tiny leftover timeout, force a dedicated apps wait
        # afterward when 3005 is not yet open.
        orig_ready(self, timeout=timeout)
        try:
            with socket.create_connection((self.vm_ip, 3005), timeout=1.0):
                return
        except OSError:
            apps_timeout = float(os.environ.get("MYPCBENCH_APPS_READY_TIMEOUT", "300"))
            log.info(
                "Post-ready 3005 still closed — running dedicated apps gate (%.0fs)",
                apps_timeout,
            )
            self._wait_for_apps_ready(timeout=apps_timeout)

    cls._wait_for_ready = _wait_for_ready
    cls._study2_apps_ready_patched = True


def apply_infra_fail_on_reset() -> None:
    """Ensure readiness TimeoutError yields INFRA_FAIL marker (idempotent)."""
    import run_mypcbench as rmb

    if getattr(rmb, "_study2_infra_fail_patched", False):
        return

    # If in-tree run_single_example already writes infra_fail.json, keep it.
    # Still wrap so a raised TimeoutError always leaves the marker.
    orig = rmb.run_single_example

    def run_single_example(agent, env, task, max_steps, result_dir, sleep_after=1.0, timeout=3600):
        try:
            return orig(
                agent, env, task, max_steps, result_dir, sleep_after=sleep_after, timeout=timeout
            )
        except TimeoutError as e:
            msg = str(e)
            infra = (
                "App readiness gate" in msg
                or "Control API not ready" in msg
                or "Classify as infrastructure" in msg
            )
            if not infra:
                raise
            marker_path = os.path.join(result_dir, "infra_fail.json")
            if not os.path.exists(marker_path):
                marker = {
                    "status": "INFRA_FAIL",
                    "reason": msg,
                    "agent_steps_started": False,
                }
                rmb._fsync_write(marker_path, json.dumps(marker, indent=2) + "\n")
                traj_path = os.path.join(result_dir, "traj.jsonl")
                infra_line = (
                    json.dumps(
                        {
                            "step_num": 0,
                            "action_timestamp": datetime.datetime.now().strftime(
                                "%Y%m%d@%H%M%S%f"
                            ),
                            "action": "INFRA_FAIL",
                            "response": msg,
                            "reward": 0,
                            "done": True,
                            "info": {
                                "kind": "infrastructure",
                                "agent_steps_started": False,
                            },
                            "screenshot_file": "",
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                with open(traj_path, "a") as f:
                    f.write(infra_line)
            raise

    rmb.run_single_example = run_single_example
    rmb._study2_infra_fail_patched = True


def apply_all() -> Dict[str, Any]:
    apply_env_readiness_gate()
    apply_infra_fail_on_reset()
    return {
        "apps_ready_gate": True,
        "infra_fail_on_reset": True,
        "apps_ready_timeout_s": float(os.environ.get("MYPCBENCH_APPS_READY_TIMEOUT", "300")),
        "http_429_note": "handled in generic_executor.openrouter_chat.default_http_post",
    }
