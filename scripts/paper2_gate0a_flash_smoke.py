#!/usr/bin/env python3
"""Gate 0A — Flash QEMU smoke for generic executor + OpenRouter transport.

Proves P1 tool ownership, P2 multi-turn, P3 stateless transport, P4 terminal.
One controlled smoke. No matrix.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_AGENT_ROOT = Path(__file__).resolve().parents[1]
_HARNESS = _AGENT_ROOT / "external" / "MyPCBench-main" / "agent-harness"
for p in (_HARNESS, _AGENT_ROOT / "scripts", _AGENT_ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from env import MyPCBenchEnv  # noqa: E402

from generic_executor.executor import build_qwen_cuabash_agent  # noqa: E402
from generic_executor.family_config import FAMILY_CONFIGS  # noqa: E402
from generic_executor.flash_gate0_binding import FLASH_GATE0A  # noqa: E402
from generic_executor.openrouter_chat import (  # noqa: E402
    OpenRouterChatCompletionsTransport,
    TransportError,
    default_http_post,
)
from generic_executor.transport import install_transport  # noqa: E402
from paper2_traj_terminal import inspect_last_action  # noqa: E402

OUT_DIR = Path(os.environ.get("GATE0A_OUT") or (_AGENT_ROOT / "results/paper2_exec/gate0a-flash"))
MODEL = os.environ.get("GATE0A_MODEL", FLASH_GATE0A.model_id)
MAX_STEPS = int(os.environ.get("GATE0A_MAX_STEPS", "4"))
FREEZE_SHA = os.environ.get("GATE0A_FREEZE_SHA", "dd43cbea0150772a804c22cec1c9ddcdb6c94789")
TOKEN = os.environ.get("GATE0A_TOKEN") or f"FLASHGATE0A-{uuid.uuid4().hex[:16]}"
TOKEN_PATH = "/tmp/GATE0A_FLASH_TOKEN.txt"


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha(b: Optional[bytes]) -> Optional[str]:
    return hashlib.sha256(b).hexdigest() if b else None


def _redact_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for m in messages:
        role = m.get("role")
        content = m.get("content")
        if isinstance(content, list):
            parts = []
            for p in content:
                if isinstance(p, dict) and p.get("type") == "image_url":
                    url = ((p.get("image_url") or {}).get("url") or "")
                    parts.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": url[:48] + f"...(len={len(url)})"},
                        }
                    )
                else:
                    parts.append(p)
            out.append({"role": role, "content": parts})
        else:
            out.append({"role": role, "content": content})
    return out


def plant_token(env: MyPCBenchEnv, token: str) -> Dict[str, Any]:
    safe = token.replace("'", "")
    cmd = f"printf '%s\\n' '{safe}' > {TOKEN_PATH} && cat {TOKEN_PATH}"
    result = env._execute_command(cmd, shell=True)
    return {"path": TOKEN_PATH, "result": result}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    traj_path = OUT_DIR / "traj.jsonl"
    if traj_path.exists():
        traj_path.unlink()

    report: Dict[str, Any] = {
        "gate": "0A",
        "model": MODEL,
        "freeze_sha": FREEZE_SHA,
        "started_at": _utc(),
        "token_prefix": TOKEN.split("-")[0] + "-",
        "token_sha256": hashlib.sha256(TOKEN.encode()).hexdigest(),
        "max_steps": MAX_STEPS,
        "checks": {},
        "turns": [],
        "http_requests": [],
        "stop_reason": "",
        "verdict": "INCOMPLETE",
        "failure_class": None,
    }

    def write_report() -> None:
        report["finished_at"] = _utc()
        (OUT_DIR / "gate0a_report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        )
        (OUT_DIR / "gate0a_report.md").write_text(
            "\n".join(
                [
                    "# Gate 0A Flash smoke report",
                    "",
                    f"- verdict: **{report['verdict']}**",
                    f"- failure_class: `{report.get('failure_class')}`",
                    f"- stop_reason: {report.get('stop_reason')}",
                    f"- model: `{report['model']}`",
                    f"- freeze: `{report['freeze_sha']}`",
                    f"- checks: `{json.dumps(report['checks'])}`",
                    "",
                ]
            )
            + "\n"
        )

    # --- Guardrails ---
    if MODEL != FLASH_GATE0A.model_id:
        report["stop_reason"] = f"model mismatch: {MODEL} != {FLASH_GATE0A.model_id}"
        report["failure_class"] = "transport"
        report["verdict"] = "FAIL"
        write_report()
        return 2
    if os.environ.get("OPENROUTER_API_KEY_LARGE"):
        report["stop_reason"] = "OPENROUTER_API_KEY_LARGE still set"
        report["failure_class"] = "transport"
        report["verdict"] = "FAIL"
        write_report()
        return 2
    if os.environ.get("ANTHROPIC_API_KEY"):
        report["stop_reason"] = "ANTHROPIC_API_KEY still set"
        report["failure_class"] = "transport"
        report["verdict"] = "FAIL"
        write_report()
        return 2
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENROUTER_API_KEY") or ""
    if not api_key.startswith("sk-or-"):
        report["stop_reason"] = "OPENAI/OPENROUTER key missing or not OpenRouter sk-or-"
        report["failure_class"] = "transport"
        report["verdict"] = "FAIL"
        write_report()
        return 2
    base = os.environ.get("OPENAI_BASE_URL", "")
    if "openrouter.ai" not in base:
        report["stop_reason"] = f"OPENAI_BASE_URL not OpenRouter: {base}"
        report["failure_class"] = "transport"
        report["verdict"] = "FAIL"
        write_report()
        return 2

    report["routing"] = {
        "OPENAI_BASE_URL": base,
        "key_prefix": api_key[:7] + "***",
        "model": MODEL,
        "lane": "SMALL",
    }

    qcow2 = os.environ.get("MYPCBENCH_QCOW2") or str(
        _AGENT_ROOT / "external/MyPCBench-main/mypcbench-vm/mypcbench.qcow2"
    )
    screen = (1280, 800)
    env = MyPCBenchEnv(
        container_name=os.environ.get("GATE0A_CONTAINER", "mypcbench-gate0a-flash"),
        screen_size=screen,
        client_password=os.environ.get("MYPCBENCH_CLIENT_PASSWORD", "password"),
        backend="qemu",
        qcow2_path=qcow2,
    )

    http_log: List[Dict[str, Any]] = []

    def capturing_http_post(url: str, headers: Dict[str, str], body: bytes, timeout: float):
        payload = json.loads(body.decode("utf-8"))
        entry = {
            "url": url,
            "model": payload.get("model"),
            "n_messages": len(payload.get("messages") or []),
            "body_keys": sorted(payload.keys()),
            "has_previous_response_id": "previous_response_id" in payload,
            "has_conversation_id": "conversation_id" in payload,
            "has_tools": "tools" in payload,
            "auth_prefix": (headers.get("Authorization") or "")[:12],
            "messages_redacted": _redact_messages(payload.get("messages") or []),
        }
        http_log.append(entry)
        print(
            f"[gate0a] HTTP POST model={entry['model']} n_messages={entry['n_messages']} "
            f"tools={entry['has_tools']} prev_id={entry['has_previous_response_id']}",
            flush=True,
        )
        if entry["model"] != MODEL:
            raise TransportError(f"silent model remap: {entry['model']} != {MODEL}")
        resp = default_http_post(url, headers, body, timeout)
        # Ownership: first model response must not contain planted token.
        try:
            text_probe = json.dumps(resp)
        except Exception:
            text_probe = ""
        entry["response_contains_planted_token"] = TOKEN in text_probe
        entry["response_has_tool_calls"] = bool(
            (((resp.get("choices") or [{}])[0].get("message") or {}).get("tool_calls"))
        )
        return resp

    try:
        print(f"[gate0a] boot QEMU qcow2={qcow2}", flush=True)
        obs = env.reset(
            task_config={"id": "gate0a-flash", "instruction": "gate0a"},
            soft=False,
        )
        shot0 = obs.get("screenshot")
        report["shot0_sha256"] = _sha(shot0)
        print(f"[gate0a] shot0={report['shot0_sha256']}", flush=True)

        plant = plant_token(env, TOKEN)
        out = (plant["result"] or {}).get("output") or ""
        report["plant"] = {
            "path": TOKEN_PATH,
            "returncode": (plant["result"] or {}).get("returncode"),
            "output_has_token": TOKEN in out,
        }
        report["checks"]["plant_token_on_qemu"] = TOKEN in out
        if not report["checks"]["plant_token_on_qemu"]:
            report["stop_reason"] = "failed to plant token on QEMU"
            report["failure_class"] = "QEMU ownership"
            report["verdict"] = "FAIL"
            write_report()
            return 3
        print("[gate0a] planted token OK", flush=True)

        # Prove token not already known to "provider" channel before any model call:
        # (we only check model responses later; plant is local.)
        transport = OpenRouterChatCompletionsTransport(
            api_key=api_key,
            family=FAMILY_CONFIGS["flash"],
            base_url=base.rstrip("/"),
            timeout_s=float(os.environ.get("GATE0A_HTTP_TIMEOUT", "180")),
            http_post=capturing_http_post,
        )
        agent = build_qwen_cuabash_agent(env=env, model_name=MODEL)
        install_transport(agent._inner, transport)
        agent.reset()

        instruction = (
            "You are controlling a real Linux desktop VM via the local harness. "
            "Prove tool ownership:\n"
            f"1) Use the bash tool to run exactly: cat {TOKEN_PATH}\n"
            "2) After you see the file contents in <tool_response>, emit "
            "computer_use terminate with status=success.\n"
            "Do not invent the token. Do not claim success before bash output.\n"
            f"Expected token prefix: {TOKEN.split('-')[0]}-"
        )

        step_idx = 0
        done = False
        consecutive_empty = 0
        turn_actions: List[List[str]] = []
        bash_outputs: List[str] = []
        shot_hashes: List[Optional[str]] = [_sha(shot0)]

        while not done and step_idx < MAX_STEPS:
            print(f"[gate0a] predict round {step_idx + 1}/{MAX_STEPS}", flush=True)
            try:
                response, actions = agent.predict(instruction, obs)
            except Exception as e:
                report["turns"].append(
                    {"round": step_idx + 1, "error": str(e)[:1500], "traceback": traceback.format_exc()[-2000:]}
                )
                report["stop_reason"] = f"predict error: {e}"
                report["failure_class"] = "transport" if "HTTP" in str(e) or "Transport" in str(e) else "model behavior"
                report["verdict"] = "FAIL"
                report["http_requests"] = http_log
                write_report()
                return 4

            # P1: first HTTP response must not contain planted token before client exec
            if http_log:
                last_http = http_log[-1]
                if step_idx == 0 and last_http.get("response_contains_planted_token"):
                    report["checks"]["p1_provider_preexec_token"] = True
                    report["stop_reason"] = "planted token appeared in provider response before QEMU client exec"
                    report["failure_class"] = "QEMU ownership"
                    report["verdict"] = "FAIL"
                    report["http_requests"] = http_log
                    write_report()
                    return 5
                if last_http.get("response_has_tool_calls"):
                    report["checks"]["p3_provider_tool_calls"] = True
                    report["stop_reason"] = "provider returned tool_calls (native tools)"
                    report["failure_class"] = "transport"
                    report["verdict"] = "FAIL"
                    report["http_requests"] = http_log
                    write_report()
                    return 5

            turn_rec: Dict[str, Any] = {
                "round": step_idx + 1,
                "response_head": (response or "")[:800],
                "response_has_token": TOKEN in (response or ""),
                "actions": list(actions),
                "pending_bash": bool(agent._pending_bash_result),
                "n_screenshots": len(agent._inner.screenshots),
            }

            # Bash executed client-side inside predict when XML present.
            if agent._pending_bash_result:
                bash_outputs.append(agent._pending_bash_result)
                turn_rec["bash_result_head"] = agent._pending_bash_result[:500]
                turn_rec["bash_has_token"] = TOKEN in agent._pending_bash_result

            if not actions:
                consecutive_empty += 1
                kind = "tool_call" if agent._pending_bash_result else "empty"
                with traj_path.open("a") as f:
                    f.write(
                        json.dumps(
                            {
                                "step_num": step_idx + 1,
                                "action": "TOOL_CALL" if agent._pending_bash_result else "EMPTY_XML",
                                "response": response,
                                "done": False,
                            }
                        )
                        + "\n"
                    )
                turn_rec["kind"] = kind
                report["turns"].append(turn_rec)
                obs = env._get_obs()
                shot_hashes.append(_sha(obs.get("screenshot")))
                step_idx += 1
                if consecutive_empty >= 3 and not agent._pending_bash_result:
                    report["stop_reason"] = "empty_xml limit"
                    report["failure_class"] = "protocol/parser"
                    break
                continue

            consecutive_empty = 0
            executed: List[str] = []
            for action in actions:
                obs, reward, done_flag, info = env.step(action, pause=0.5)
                executed.append(action if isinstance(action, str) else str(action))
                with traj_path.open("a") as f:
                    f.write(
                        json.dumps(
                            {
                                "step_num": step_idx + 1,
                                "action": executed[-1],
                                "response": response,
                                "reward": reward,
                                "done": done_flag,
                                "info": info,
                            }
                        )
                        + "\n"
                    )
                shot_hashes.append(_sha(obs.get("screenshot")))
                if done_flag:
                    done = True
                    break
            turn_rec["kind"] = "gui"
            turn_rec["executed"] = executed
            turn_actions.append(executed)
            report["turns"].append(turn_rec)
            step_idx += 1

        report["http_requests"] = http_log
        report["shot_hashes"] = shot_hashes
        report["bash_outputs_token_flags"] = [TOKEN in b for b in bash_outputs]

        # --- Score P1–P4 ---
        checks = report["checks"]
        checks["p1_no_token_in_turn1_provider_response"] = not any(
            (t.get("round") == 1 and t.get("response_has_token")) for t in report["turns"]
        )
        # Prefer: token seen in client bash result
        checks["p1_token_via_client_bash"] = any(TOKEN in b for b in bash_outputs)
        # Or in traj after client path
        traj_text = traj_path.read_text() if traj_path.exists() else ""
        checks["p1_token_in_traj_after_client"] = TOKEN in traj_text and checks["p1_token_via_client_bash"]

        checks["p2_at_least_two_model_turns"] = len(http_log) >= 2
        checks["p2_screenshot_changed"] = (
            len(set(h for h in shot_hashes if h)) >= 2 if len(shot_hashes) >= 2 else False
        )
        if len(http_log) >= 2:
            n1 = http_log[0]["n_messages"]
            n2 = http_log[1]["n_messages"]
            checks["p2_turn2_more_history"] = n2 > n1
            blob2 = json.dumps(http_log[1].get("messages_redacted"))
            checks["p2_turn2_has_tool_response_or_prior_assistant"] = (
                "tool_response" in blob2 or '"role": "assistant"' in blob2 or "'role': 'assistant'" in blob2
            )
        else:
            checks["p2_turn2_more_history"] = False
            checks["p2_turn2_has_tool_response_or_prior_assistant"] = False

        checks["p3_no_previous_response_id"] = all(
            not r.get("has_previous_response_id") for r in http_log
        )
        checks["p3_no_conversation_id"] = all(not r.get("has_conversation_id") for r in http_log)
        checks["p3_no_tools"] = all(not r.get("has_tools") for r in http_log)
        checks["p3_exact_model"] = all(r.get("model") == MODEL for r in http_log)
        checks["p3_endpoint_openrouter"] = all(
            "openrouter.ai" in (r.get("url") or "") for r in http_log
        )

        if traj_path.exists() and traj_path.stat().st_size > 0:
            info = inspect_last_action(traj_path)
            report["terminal"] = {
                "canonical_last_action": info.get("canonical_last_action"),
                "valid_done": info.get("valid_done"),
                "evidence_kind": info.get("evidence_kind"),
            }
            checks["p4_valid_done"] = bool(info.get("valid_done"))
            checks["p4_not_heuristic"] = info.get("canonical_last_action") == "DONE"
        else:
            report["terminal"] = None
            checks["p4_valid_done"] = False
            checks["p4_not_heuristic"] = False

        p1 = (
            checks.get("plant_token_on_qemu")
            and checks.get("p1_no_token_in_turn1_provider_response")
            and checks.get("p1_token_via_client_bash")
        )
        p2 = (
            checks.get("p2_at_least_two_model_turns")
            and checks.get("p2_turn2_more_history")
            and (checks.get("p2_screenshot_changed") or checks.get("p2_turn2_has_tool_response_or_prior_assistant"))
        )
        p3 = (
            checks.get("p3_no_previous_response_id")
            and checks.get("p3_no_conversation_id")
            and checks.get("p3_no_tools")
            and checks.get("p3_exact_model")
            and checks.get("p3_endpoint_openrouter")
        )
        p4 = checks.get("p4_valid_done") and checks.get("p4_not_heuristic")

        report["pillars"] = {"P1": p1, "P2": p2, "P3": p3, "P4": p4}

        if p1 and p2 and p3 and p4:
            report["verdict"] = "PASS"
            report["stop_reason"] = "all Gate 0A pillars passed"
            report["failure_class"] = None
            write_report()
            print("[gate0a] PASS", flush=True)
            return 0

        # Classify failure
        if not p3:
            report["failure_class"] = "transport"
        elif not p1:
            report["failure_class"] = "QEMU ownership"
        elif not p2:
            report["failure_class"] = "history/observation"
        elif not p4:
            report["failure_class"] = "model behavior"
        else:
            report["failure_class"] = "protocol/parser"
        report["verdict"] = "FAIL"
        report["stop_reason"] = report["stop_reason"] or f"pillars={report['pillars']}"
        write_report()
        print(f"[gate0a] FAIL class={report['failure_class']} pillars={report['pillars']}", flush=True)
        return 1

    except Exception as e:
        report["stop_reason"] = f"uncaught: {e}"
        report["failure_class"] = "QEMU ownership" if "qemu" in str(e).lower() else "transport"
        report["verdict"] = "FAIL"
        report["traceback"] = traceback.format_exc()[-3000:]
        report["http_requests"] = http_log
        write_report()
        print(f"[gate0a] FAIL uncaught: {e}", flush=True)
        return 10
    finally:
        try:
            env.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
