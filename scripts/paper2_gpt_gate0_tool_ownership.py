#!/usr/bin/env python3
"""Gate 0 — OpenRouter GPT computer/shell tool ownership vs local QEMU.

Pass criteria (all required):
  1. Turn 1 response contains client-executable tool items (shell_call and/or
     computer_call), NOT provider-pre-executed results.
  2. Shell (if emitted) runs via env._execute_command on OUR guest and returns
     a pre-planted unique token that only exists in our QEMU.
  3. Computer (if emitted) actions are executed by the harness against OUR
     guest; post-action screenshot differs from pre-action (when action is
     non-noop) OR call_id linkage is preserved for screenshot-only.
  4. Turn 2 request omits previous_response_id and sends reconstructed
     structured history (throwaway inline reconstruct — NOT the frozen
     adapter). Turn 2 must accept our QEMU screenshot / tool outputs
     without 400 previous_response_id, and must not invent a provider
     sandbox that contradicts the token we planted.

Fail → stop; do not implement ResponseStateAdapter.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Harness on PYTHONPATH
from agents.base import encode_image
from agents.openai_cuabash import COMPUTER_TOOL, SHELL_TOOL, OpenAICUAToolsAgent
from env import MyPCBenchEnv


OUT_DIR = Path(os.environ.get(
    "GATE0_OUT",
    str(Path(__file__).resolve().parents[1] / "results" / "paper2_exec" / "gpt-5.5-gate0"),
))
MODEL = os.environ.get("MYPCBENCH_OPENAI_MODEL", "openai/gpt-5.5")
TOKEN = os.environ.get("GATE0_TOKEN") or f"GATE0-{uuid.uuid4().hex[:16]}"
MAX_TURNS = int(os.environ.get("GATE0_MAX_TURNS", "2"))


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_bytes(b: Optional[bytes]) -> Optional[str]:
    if not b:
        return None
    return hashlib.sha256(b).hexdigest()


def _item_to_dict(item: Any) -> Dict[str, Any]:
    if hasattr(item, "model_dump"):
        return item.model_dump()
    if isinstance(item, dict):
        return item
    return {"repr": repr(item), "type": getattr(item, "type", None)}


def _serialize_output_items(response: Any) -> List[Dict[str, Any]]:
    """Preserve structured output items for client-managed replay."""
    out: List[Dict[str, Any]] = []
    for item in getattr(response, "output", None) or []:
        d = _item_to_dict(item)
        # Drop huge binary blobs if any sneak in; keep protocol fields.
        out.append(d)
    return out


def _types_in_output(response: Any) -> List[str]:
    types = []
    for item in getattr(response, "output", None) or []:
        types.append(getattr(item, "type", type(item).__name__))
    return types


def _redact_images(obj: Any) -> Any:
    """Shrink log payloads: replace data:image… with sha16 markers."""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in ("image_url", "image") and isinstance(v, str) and v.startswith("data:"):
                raw = v.split(",", 1)[-1] if "," in v else v
                out[k] = f"<data_image sha16={hashlib.sha256(raw.encode()).hexdigest()[:16]} len={len(v)}>"
            else:
                out[k] = _redact_images(v)
        return out
    if isinstance(obj, list):
        return [_redact_images(x) for x in obj]
    return obj


def plant_token(env: MyPCBenchEnv, token: str) -> Dict[str, Any]:
    """Write unique token only onto our guest filesystem."""
    path = "/tmp/GATE0_TOKEN.txt"
    # Quote-safe: token is hex-ish; still escape.
    safe = token.replace("'", "")
    cmd = f"printf '%s\\n' '{safe}' > {path} && cat {path} && hostname && uname -a"
    result = env._execute_command(cmd, shell=True)
    return {"path": path, "cmd": cmd, "result": result}


def build_turn1_input(screenshot: bytes, instruction: str) -> List[Dict[str, Any]]:
    content: List[Dict[str, Any]] = [
        {
            "type": "input_text",
            "text": (
                "You are operating a real Linux desktop VM controlled by the "
                "local harness. Your tools are `computer` (GUI) and `shell` "
                "(commands on that same VM).\n\n"
                f"Task: {instruction}\n\n"
                "Rules:\n"
                "1) First use `shell` to run: cat /tmp/GATE0_TOKEN.txt\n"
                "2) Then use `computer` to take a screenshot action OR click "
                "once near the center of the desktop (x=960,y=540).\n"
                "3) Do not claim the environment is a provider sandbox, "
                "localhost-only jail, or GUI-less shell unless the tool "
                "output literally proves that.\n"
            ),
        }
    ]
    if screenshot:
        content.append({
            "type": "input_image",
            "image_url": f"data:image/png;base64,{encode_image(screenshot)}",
        })
    return [{"role": "user", "content": content}]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report: Dict[str, Any] = {
        "gate": "0",
        "title": "tool_ownership_qemu_vs_provider",
        "started_at": _utc(),
        "model": MODEL,
        "token": TOKEN,
        "checks": {},
        "turns": [],
        "verdict": "FAIL",
        "stop_reason": None,
    }

    def write_report() -> None:
        report["finished_at"] = _utc()
        path = OUT_DIR / "GATE0_REPORT.json"
        path.write_text(json.dumps(report, indent=2, default=str) + "\n")
        (OUT_DIR / "GATE0_VERDICT.txt").write_text(
            f"{report['verdict']}\n{report.get('stop_reason') or ''}\n"
        )

    qcow2 = os.environ.get("MYPCBENCH_QCOW2") or str(
        Path(__file__).resolve().parents[1]
        / "external"
        / "MyPCBench-main"
        / "mypcbench-vm"
        / "mypcbench.qcow2"
    )
    screen = (1920, 1080)
    env = MyPCBenchEnv(
        container_name=os.environ.get("GATE0_CONTAINER", "mypcbench-gate0"),
        screen_size=screen,
        client_password=os.environ.get("MYPCBENCH_CLIENT_PASSWORD", "password"),
        backend="qemu",
        qcow2_path=qcow2,
    )
    try:
        print(f"[gate0] reset/boot QEMU qcow2={qcow2}", flush=True)
        obs = env.reset(task_config={"id": "gate0", "instruction": "gate0"}, soft=False)
        shot0 = obs.get("screenshot")
        report["shot0_sha256"] = _sha256_bytes(shot0)
        print(f"[gate0] shot0_sha256={report['shot0_sha256']}", flush=True)

        plant = plant_token(env, TOKEN)
        report["plant"] = {
            "path": plant["path"],
            "returncode": (plant["result"] or {}).get("returncode"),
            "output_head": ((plant["result"] or {}).get("output") or "")[:500],
            "error_head": ((plant["result"] or {}).get("error") or "")[:300],
        }
        plant_ok = TOKEN in ((plant["result"] or {}).get("output") or "")
        report["checks"]["plant_token_on_qemu"] = plant_ok
        if not plant_ok:
            report["stop_reason"] = "failed to plant token on QEMU guest"
            write_report()
            return 2
        print(f"[gate0] planted token on guest OK", flush=True)

        # Agent only for local tool execution helpers (shell/computer→pyautogui).
        agent = OpenAICUAToolsAgent(
            model=MODEL,
            screen_size=screen,
            client_password=os.environ.get("MYPCBENCH_CLIENT_PASSWORD", "password"),
            env=env,
            max_output_tokens=int(os.environ.get("GATE0_MAX_OUTPUT_TOKENS", "1500")),
            reasoning_effort=os.environ.get("MYPCBENCH_OPENAI_REASONING_EFFORT", "medium"),
            api_retry_times=3,
        )

        # --- Turn 1 ---
        instruction = (
            "Prove you are on the harness VM: cat /tmp/GATE0_TOKEN.txt via shell, "
            "then perform one computer action on the desktop."
        )
        turn1_input = build_turn1_input(shot0, instruction)
        req1: Dict[str, Any] = {
            "model": MODEL,
            "input": turn1_input,
            "tools": [COMPUTER_TOOL, SHELL_TOOL],
            "truncation": "auto",
            "max_output_tokens": agent.max_output_tokens,
            "reasoning": {"effort": agent.reasoning_effort, "summary": "auto"},
        }
        # Explicitly no previous_response_id
        assert "previous_response_id" not in req1

        print("[gate0] Turn 1 responses.create …", flush=True)
        t0 = time.time()
        try:
            resp1 = agent.client.responses.create(**req1)
        except Exception as e:
            report["turns"].append({
                "turn": 1,
                "error": str(e)[:800],
                "elapsed_s": round(time.time() - t0, 2),
            })
            report["stop_reason"] = f"turn1 API error: {e}"
            write_report()
            return 3

        types1 = _types_in_output(resp1)
        out1 = _serialize_output_items(resp1)
        (OUT_DIR / "turn1_output.json").write_text(
            json.dumps(_redact_images(out1), indent=2, default=str) + "\n"
        )
        turn1_rec = {
            "turn": 1,
            "response_id": getattr(resp1, "id", None),
            "elapsed_s": round(time.time() - t0, 2),
            "output_types": types1,
            "has_previous_response_id_in_request": False,
        }
        report["turns"].append(turn1_rec)

        client_tool_types = {"shell_call", "computer_call", "function_call"}
        has_client_tools = bool(set(types1) & client_tool_types)
        # Provider-pre-executed smell: shell_call_output / computer_call_output
        # appearing in model output without us sending them.
        provider_exec_smell = bool(
            set(types1) & {"shell_call_output", "computer_call_output", "function_call_output"}
        )
        report["checks"]["turn1_has_client_tool_calls"] = has_client_tools
        report["checks"]["turn1_no_provider_preexecuted_outputs"] = not provider_exec_smell

        if not has_client_tools:
            report["stop_reason"] = (
                f"turn1 produced no client-executable tool calls; types={types1}"
            )
            write_report()
            return 4
        if provider_exec_smell:
            report["stop_reason"] = (
                f"turn1 output already contains tool_*_output items (provider exec?): {types1}"
            )
            write_report()
            return 5

        # Execute tools locally on QEMU (same semantics as harness).
        pending: List[Dict[str, Any]] = []
        actions: List[str] = []
        shell_saw_token = False
        shell_cmds: List[str] = []
        computer_calls = 0

        for item in resp1.output:
            itype = getattr(item, "type", None)
            if itype == "shell_call":
                action = getattr(item, "action", None)
                commands = list(getattr(action, "commands", None) or []) if action else []
                timeout_ms = getattr(action, "timeout_ms", None) if action else None
                max_out = getattr(action, "max_output_length", None) if action else None
                outputs = []
                for cmd in commands:
                    shell_cmds.append(cmd)
                    stdout, stderr, outcome = agent._execute_shell_command(
                        cmd, timeout_ms=timeout_ms, max_output_length=max_out
                    )
                    if TOKEN in (stdout or "") or TOKEN in (stderr or ""):
                        shell_saw_token = True
                    outputs.append({
                        "stdout": stdout,
                        "stderr": stderr,
                        "outcome": outcome,
                    })
                    print(f"[gate0] shell exec: {cmd[:100]!r} -> {outcome}", flush=True)
                pending.append({
                    "type": "shell_call_output",
                    "call_id": item.call_id,
                    "output": outputs,
                })
            elif itype == "computer_call":
                computer_calls += 1
                agent._last_computer_call_id = item.call_id
                raw_checks = getattr(item, "pending_safety_checks", None) or []
                pending_checks = []
                for chk in raw_checks:
                    if hasattr(chk, "model_dump"):
                        pending_checks.append(chk.model_dump())
                    elif isinstance(chk, dict):
                        pending_checks.append(chk)
                agent._pending_safety_checks = pending_checks
                raw_actions = item.actions or ([item.action] if item.action else [])
                for a in raw_actions:
                    code = agent._action_to_pyautogui(a)
                    if code:
                        actions.append(code)
                        print(f"[gate0] computer action code: {code[:120]!r}", flush=True)

        report["checks"]["shell_call_present"] = bool(shell_cmds)
        report["checks"]["shell_returned_planted_token"] = shell_saw_token
        report["shell_commands"] = shell_cmds
        report["computer_calls"] = computer_calls
        report["computer_actions_n"] = len(actions)

        # Apply computer actions on guest (one pyautogui string per step).
        shot1 = shot0
        if actions:
            step_obs = None
            for code in actions:
                step_obs, _, _, _ = env.step(code)
            shot1 = (step_obs or {}).get("screenshot") or env._get_screenshot()
        elif computer_calls:
            # screenshot-only computer_call — still capture post state
            shot1 = env._get_screenshot() or shot0

        report["shot1_sha256"] = _sha256_bytes(shot1)
        report["checks"]["screenshot_changed_after_actions"] = (
            report["shot0_sha256"] != report["shot1_sha256"]
            if actions
            else None
        )

        # Direct re-read of token from guest (independent of model).
        verify = env._execute_command("cat /tmp/GATE0_TOKEN.txt", shell=True)
        report["checks"]["qemu_token_still_present"] = TOKEN in (
            (verify or {}).get("output") or ""
        )

        if shell_cmds and not shell_saw_token:
            report["stop_reason"] = (
                "shell_call executed but planted QEMU token not in stdout/stderr "
                "— shell likely not our guest (or wrong command)"
            )
            write_report()
            return 6

        if not shell_cmds and computer_calls == 0:
            report["stop_reason"] = "no shell or computer calls to validate"
            write_report()
            return 7

        # Build computer_call_output from OUR screenshot for turn 2.
        if agent._last_computer_call_id and shot1:
            output_item: Dict[str, Any] = {
                "type": "computer_call_output",
                "call_id": agent._last_computer_call_id,
                "output": {
                    "type": "computer_screenshot",
                    "image_url": f"data:image/png;base64,{encode_image(shot1)}",
                    "detail": "original",
                },
            }
            if agent._pending_safety_checks:
                output_item["acknowledged_safety_checks"] = agent._pending_safety_checks
            pending.append(output_item)

        # --- Turn 2: client-managed history (throwaway reconstruct) ---
        # committed = initial + R1.output + tool outputs (each once)
        history: List[Any] = list(turn1_input)
        history.extend(out1)
        history.extend(pending)

        req2: Dict[str, Any] = {
            "model": MODEL,
            "input": history,
            "tools": [COMPUTER_TOOL, SHELL_TOOL],
            "truncation": "auto",
            "max_output_tokens": agent.max_output_tokens,
            "reasoning": {"effort": agent.reasoning_effort, "summary": "auto"},
        }
        # Must NOT send previous_response_id
        print("[gate0] Turn 2 responses.create (full history, no previous_response_id) …", flush=True)
        t1 = time.time()
        try:
            resp2 = agent.client.responses.create(**req2)
            turn2_err = None
        except Exception as e:
            resp2 = None
            turn2_err = e

        turn2_rec: Dict[str, Any] = {
            "turn": 2,
            "elapsed_s": round(time.time() - t1, 2),
            "previous_response_id_sent": False,
            "history_item_count": len(history),
        }
        if turn2_err is not None:
            turn2_rec["error"] = str(turn2_err)[:1200]
            report["turns"].append(turn2_rec)
            report["checks"]["turn2_api_ok"] = False
            report["stop_reason"] = f"turn2 API error (history reconstruct): {turn2_err}"
            write_report()
            return 8

        types2 = _types_in_output(resp2)
        out2 = _serialize_output_items(resp2)
        (OUT_DIR / "turn2_output.json").write_text(
            json.dumps(_redact_images(out2), indent=2, default=str) + "\n"
        )
        turn2_rec["response_id"] = getattr(resp2, "id", None)
        turn2_rec["output_types"] = types2
        report["turns"].append(turn2_rec)
        report["checks"]["turn2_api_ok"] = True
        report["checks"]["turn2_no_previous_response_id_required"] = True

        # Semantic smell: model invents provider sandbox / no GUI despite token.
        msg_bits: List[str] = []
        for item in resp2.output:
            if getattr(item, "type", None) == "message":
                for part in getattr(item, "content", None) or []:
                    if getattr(part, "type", None) == "output_text":
                        msg_bits.append(getattr(part, "text", "") or "")
            if getattr(item, "type", None) == "reasoning":
                summary = getattr(item, "summary", None)
                if isinstance(summary, list):
                    for block in summary:
                        text = getattr(block, "text", None) or (
                            block.get("text") if isinstance(block, dict) else None
                        )
                        if text:
                            msg_bits.append(text)
        blob = "\n".join(msg_bits).lower()
        sandbox_claims = bool(
            re.search(
                r"(provider sandbox|no gui|gui-less|localhost.*(refus|block|deny)|"
                r"cannot access (the )?desktop|not a real (desktop|vm)|"
                r"shell sandbox does not include",
                blob,
            )
        )
        token_mentioned = TOKEN.lower() in blob or TOKEN in "\n".join(msg_bits)
        report["checks"]["turn2_no_provider_sandbox_claim"] = not sandbox_claims
        report["checks"]["turn2_mentions_token_or_continues_tools"] = bool(
            token_mentioned or (set(types2) & client_tool_types)
        )
        report["turn2_message_head"] = ("\n".join(msg_bits))[:1500]

        # --- Verdict ---
        required = [
            "plant_token_on_qemu",
            "turn1_has_client_tool_calls",
            "turn1_no_provider_preexecuted_outputs",
            "qemu_token_still_present",
            "turn2_api_ok",
            "turn2_no_provider_sandbox_claim",
        ]
        if shell_cmds:
            required.append("shell_returned_planted_token")

        failed = [k for k in required if not report["checks"].get(k)]
        if failed:
            report["verdict"] = "FAIL"
            report["stop_reason"] = f"failed checks: {failed}"
            write_report()
            return 9

        report["verdict"] = "PASS"
        report["stop_reason"] = (
            "Gate 0 passed: client-executed tools on local QEMU; "
            "turn2 accepted structured history without previous_response_id"
        )
        write_report()
        print(f"[gate0] PASS — report {OUT_DIR / 'GATE0_REPORT.json'}", flush=True)
        return 0

    except Exception:
        report["stop_reason"] = "exception: " + traceback.format_exc()[-2000:]
        write_report()
        print(report["stop_reason"], file=sys.stderr)
        return 1
    finally:
        try:
            env.close()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
