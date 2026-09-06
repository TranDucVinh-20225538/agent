#!/usr/bin/env python3
"""Claude Gate 0 — OpenRouter SMALL tool ownership vs local QEMU.

Pass only if:
  Turn1 response → tool_use only (no provider tool_result)
  → harness executes on QEMU node30
  → tool_result + screenshot from harness/QEMU
  → Turn2 receives/uses those client outputs

Fail if provider pre-executes tools or ownership is ambiguous.
Smoke only — does not start Claude matrix.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from agents.claude_cuabash import ClaudeCUAAgent
from env import MyPCBenchEnv


OUT_DIR = Path(
    os.environ.get(
        "GATE0_OUT",
        str(
            Path(__file__).resolve().parents[1]
            / "results"
            / "paper2_exec"
            / "claude-opus-4-6-gate0-or-small"
        ),
    )
)
MODEL = os.environ.get("MYPCBENCH_CLAUDE_MODEL", "claude-opus-4-6")
TOKEN = os.environ.get("GATE0_TOKEN") or f"CLAUDEGATE0-{uuid.uuid4().hex[:16]}"


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_bytes(b: Optional[bytes]) -> Optional[str]:
    if not b:
        return None
    return hashlib.sha256(b).hexdigest()


def _block_type(block: Any) -> str:
    if isinstance(block, dict):
        return str(block.get("type") or "?")
    return str(getattr(block, "type", type(block).__name__))


def _content_types(response: Any) -> List[str]:
    content = getattr(response, "content", None) or []
    return [_block_type(b) for b in content]


def _routing_evidence() -> Dict[str, Any]:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    base = os.environ.get("ANTHROPIC_BASE_URL", "")
    return {
        "ANTHROPIC_BASE_URL": base,
        "ANTHROPIC_API_KEY_prefix": (key[:6] + "***") if key else "",
        "ANTHROPIC_API_KEY_is_openrouter": key.startswith("sk-or-"),
        "ANTHROPIC_API_KEY_BACKUP_set": bool(os.environ.get("ANTHROPIC_API_KEY_BACKUP")),
        "OPENAI_API_KEY_set": bool(os.environ.get("OPENAI_API_KEY")),
        "PAPER2_CLAUDE_VIA": os.environ.get("PAPER2_CLAUDE_VIA"),
        "wiring_freeze_commit": os.environ.get("PAPER2_WIRING_FREEZE_COMMIT"),
        "base_url_is_openrouter": "openrouter.ai" in base,
    }


def plant_token(env: MyPCBenchEnv, token: str) -> Dict[str, Any]:
    path = "/tmp/CLAUDE_GATE0_TOKEN.txt"
    safe = token.replace("'", "")
    cmd = f"printf '%s\\n' '{safe}' > {path} && cat {path} && hostname && uname -a"
    result = env._execute_command(cmd, shell=True)
    return {"path": path, "cmd": cmd, "result": result}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report: Dict[str, Any] = {
        "gate": "0",
        "title": "claude_tool_ownership_qemu_vs_provider",
        "scope": "openrouter_small_smoke_only_not_matrix",
        "started_at": _utc(),
        "model": MODEL,
        "token": TOKEN,
        "routing": _routing_evidence(),
        "checks": {},
        "turns": [],
        "verdict": "FAIL",
        "stop_reason": None,
    }

    def write_report() -> None:
        report["finished_at"] = _utc()
        (OUT_DIR / "GATE0_REPORT.json").write_text(
            json.dumps(report, indent=2, default=str) + "\n"
        )
        (OUT_DIR / "GATE0_VERDICT.txt").write_text(
            f"{report['verdict']}\n{report.get('stop_reason') or ''}\n"
        )

    # Preflight routing — fail closed before spending QEMU boot if miswired.
    r = report["routing"]
    if not r["base_url_is_openrouter"] or not r["ANTHROPIC_API_KEY_is_openrouter"]:
        report["stop_reason"] = f"routing preflight failed: {r}"
        write_report()
        return 2
    if r["ANTHROPIC_API_KEY_BACKUP_set"]:
        report["stop_reason"] = "ANTHROPIC_API_KEY_BACKUP set — native fallback risk"
        write_report()
        return 2

    qcow2 = os.environ.get("MYPCBENCH_QCOW2") or str(
        Path(__file__).resolve().parents[1]
        / "external"
        / "MyPCBench-main"
        / "mypcbench-vm"
        / "mypcbench.qcow2"
    )
    screen = (1920, 1080)
    env = MyPCBenchEnv(
        container_name=os.environ.get("GATE0_CONTAINER", "mypcbench-claude-gate0"),
        screen_size=screen,
        client_password=os.environ.get("MYPCBENCH_CLIENT_PASSWORD", "password"),
        backend="qemu",
        qcow2_path=qcow2,
    )

    captured: List[Dict[str, Any]] = []

    try:
        print(f"[claude-gate0] reset/boot QEMU qcow2={qcow2}", flush=True)
        obs = env.reset(task_config={"id": "claude-gate0", "instruction": "gate0"}, soft=False)
        shot0 = obs.get("screenshot")
        report["shot0_sha256"] = _sha256_bytes(shot0)
        print(f"[claude-gate0] shot0_sha256={report['shot0_sha256']}", flush=True)

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
            return 3
        print("[claude-gate0] planted token on guest OK", flush=True)

        agent = ClaudeCUAAgent(
            model=MODEL,
            screen_size=screen,
            client_password=os.environ.get("MYPCBENCH_CLIENT_PASSWORD", "password"),
            env=env,
            api_retry_times=3,
        )
        # Evidence: client base_url after construction
        client_base = str(getattr(agent.client, "base_url", "") or "")
        report["routing"]["client_base_url"] = client_base
        report["checks"]["client_base_url_openrouter"] = "openrouter.ai" in client_base
        if not report["checks"]["client_base_url_openrouter"]:
            report["stop_reason"] = f"Anthropic client base_url not OpenRouter: {client_base}"
            write_report()
            return 4

        # Capture raw API responses (content types) before/as agent parses them.
        create = agent.client.beta.messages.create

        def _capturing_create(**kwargs):
            resp = create(**kwargs)
            types = _content_types(resp)
            captured.append(
                {
                    "content_types": types,
                    "model": getattr(resp, "model", None),
                    "id": getattr(resp, "id", None),
                    "has_tool_result_in_response": "tool_result" in types,
                    "has_tool_use": "tool_use" in types,
                    "request_model": kwargs.get("model"),
                }
            )
            print(f"[claude-gate0] API content_types={types}", flush=True)
            return resp

        agent.client.beta.messages.create = _capturing_create  # type: ignore[method-assign]

        instruction = (
            "You are on a real Linux desktop VM controlled by the local harness. "
            "Prove tool ownership:\n"
            "1) Use the bash tool to run exactly: cat /tmp/CLAUDE_GATE0_TOKEN.txt\n"
            "2) Then use the computer tool to click once near the desktop center.\n"
            "Do not claim a provider sandbox or GUI-less jail unless tool output proves it.\n"
            f"Expected token prefix: CLAUDEGATE0-"
        )

        # --- Turn 1 ---
        print("[claude-gate0] Turn 1 predict …", flush=True)
        obs1 = {"screenshot": shot0}
        try:
            resp_text, actions = agent.predict(instruction, obs1)
        except Exception as e:
            report["turns"].append({"turn": 1, "error": str(e)[:1200]})
            report["stop_reason"] = f"turn1 predict error: {e}"
            write_report()
            return 5

        if not captured:
            report["stop_reason"] = "turn1: no API response captured"
            write_report()
            return 6

        api1 = captured[-1]
        turn1_rec = {
            "turn": 1,
            "api": api1,
            "actions_n": len(actions or []),
            "response_text_head": (resp_text or "")[:800],
            "messages_roles": [m.get("role") for m in agent.messages],
        }
        report["turns"].append(turn1_rec)

        report["checks"]["turn1_has_tool_use"] = bool(api1.get("has_tool_use"))
        report["checks"]["turn1_no_provider_tool_result"] = not api1.get(
            "has_tool_result_in_response"
        )
        if not report["checks"]["turn1_has_tool_use"]:
            report["stop_reason"] = f"turn1 missing tool_use; types={api1.get('content_types')}"
            write_report()
            return 7
        if not report["checks"]["turn1_no_provider_tool_result"]:
            report["stop_reason"] = (
                f"turn1 response already contains tool_result (provider exec?): "
                f"{api1.get('content_types')}"
            )
            write_report()
            return 8

        # Inspect harness-appended tool_results in agent.messages (client-side).
        tool_results_text = []
        for msg in agent.messages:
            if msg.get("role") != "user":
                continue
            content = msg.get("content")
            if not isinstance(content, list):
                continue
            for item in content:
                if not isinstance(item, dict) or item.get("type") != "tool_result":
                    continue
                raw = item.get("content")
                if isinstance(raw, str):
                    tool_results_text.append(raw)
                elif isinstance(raw, list):
                    for part in raw:
                        if isinstance(part, dict) and part.get("type") == "text":
                            tool_results_text.append(part.get("text") or "")
                        elif isinstance(part, str):
                            tool_results_text.append(part)

        blob_tr = "\n".join(tool_results_text)
        shell_saw_token = TOKEN in blob_tr
        report["checks"]["harness_tool_result_present"] = bool(tool_results_text)
        report["checks"]["shell_returned_planted_token"] = shell_saw_token
        report["harness_tool_result_head"] = blob_tr[:800]

        if not tool_results_text:
            report["stop_reason"] = "harness did not append tool_result after turn1"
            write_report()
            return 9
        if not shell_saw_token:
            # Model may have used computer-only; require bash token path for ownership.
            report["stop_reason"] = (
                "planted QEMU token not in harness tool_result — bash may not have "
                "run on our guest (or model skipped bash)"
            )
            write_report()
            return 10

        # Execute any pending GUI actions on QEMU.
        shot1 = shot0
        if actions:
            step_obs = None
            for code in actions:
                step_obs, _, _, _ = env.step(code)
            shot1 = (step_obs or {}).get("screenshot") or env._get_screenshot()
        else:
            shot1 = env._get_screenshot() or shot0
        report["shot1_sha256"] = _sha256_bytes(shot1)
        report["computer_actions_n"] = len(actions or [])

        verify = env._execute_command("cat /tmp/CLAUDE_GATE0_TOKEN.txt", shell=True)
        report["checks"]["qemu_token_still_present"] = TOKEN in (
            (verify or {}).get("output") or ""
        )

        # --- Turn 2 ---
        print("[claude-gate0] Turn 2 predict …", flush=True)
        n_captured_before = len(captured)
        obs2 = {"screenshot": shot1}
        try:
            resp2_text, actions2 = agent.predict(instruction, obs2)
            turn2_err = None
        except Exception as e:
            resp2_text, actions2, turn2_err = "", [], e

        if turn2_err is not None:
            report["turns"].append({"turn": 2, "error": str(turn2_err)[:1200]})
            report["checks"]["turn2_api_ok"] = False
            report["stop_reason"] = f"turn2 predict error: {turn2_err}"
            write_report()
            return 11

        if len(captured) <= n_captured_before:
            report["stop_reason"] = "turn2: no new API response captured"
            write_report()
            return 12

        api2 = captured[-1]
        report["turns"].append(
            {
                "turn": 2,
                "api": api2,
                "actions_n": len(actions2 or []),
                "response_text_head": (resp2_text or "")[:800],
            }
        )
        report["checks"]["turn2_api_ok"] = True
        report["checks"]["turn2_no_provider_tool_result"] = not api2.get(
            "has_tool_result_in_response"
        )

        # Continuity: messages should include prior assistant tool_use + user tool_result.
        has_assistant_tool_use = False
        has_user_tool_result = False
        for msg in agent.messages:
            content = msg.get("content")
            if not isinstance(content, list):
                continue
            for item in content:
                if not isinstance(item, dict):
                    continue
                if msg.get("role") == "assistant" and item.get("type") == "tool_use":
                    has_assistant_tool_use = True
                if msg.get("role") == "user" and item.get("type") == "tool_result":
                    has_user_tool_result = True
        report["checks"]["turn2_history_has_tool_use"] = has_assistant_tool_use
        report["checks"]["turn2_history_has_client_tool_result"] = has_user_tool_result

        blob2 = (resp2_text or "").lower()
        sandbox_claim = bool(
            re.search(
                r"(provider sandbox|no gui|gui-less|not a real (desktop|vm)|"
                r"shell sandbox does not include)",
                blob2,
            )
        )
        report["checks"]["turn2_no_provider_sandbox_claim"] = not sandbox_claim

        required = [
            "plant_token_on_qemu",
            "client_base_url_openrouter",
            "turn1_has_tool_use",
            "turn1_no_provider_tool_result",
            "harness_tool_result_present",
            "shell_returned_planted_token",
            "qemu_token_still_present",
            "turn2_api_ok",
            "turn2_no_provider_tool_result",
            "turn2_history_has_tool_use",
            "turn2_history_has_client_tool_result",
            "turn2_no_provider_sandbox_claim",
        ]
        failed = [k for k in required if not report["checks"].get(k)]
        if failed:
            report["verdict"] = "FAIL"
            report["stop_reason"] = f"failed checks: {failed}"
            write_report()
            return 13

        report["verdict"] = "PASS"
        report["stop_reason"] = (
            "Claude Gate 0 PASS: client tool_use → QEMU harness tool_result; "
            "turn2 continuity OK. NOT matrix start."
        )
        write_report()
        print(f"[claude-gate0] PASS — {OUT_DIR / 'GATE0_REPORT.json'}", flush=True)
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
