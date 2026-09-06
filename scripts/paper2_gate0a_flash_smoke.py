#!/usr/bin/env python3
"""Gate 0A v1.1 — QEMU smoke for generic executor + OpenRouter transport.

Proves P1 tool ownership, P2 multi-turn, P3 stateless transport, P4 terminal
with content correctness. Family selected via GATE0A_FAMILY=flash|gpt|claude.

v1.1 vs v1.0 — sole execution change: max_steps 4 → 10 (Gate 0A smoke only).
PASS requires DONE within the ten agent-turn budget AND agent-reported token
byte-exact match to the planted token. Task/protocol/instruction unchanged
across families (only model id + artifact/QEMU namespace differ).

Step-budget semantics: max_steps=N means N predict rounds (agent turns).
DONE on turn N is allowed if produced during that turn (before the loop
refuses a further predict). Turns are 1-indexed; with N=10, rounds 1..10 inclusive.

Clarification: this smoke budget does NOT modify frozen Study 1
max_steps=80 / timeout=7200 (paper2_exec_run.sh / legacy qwen_cuabash).

One controlled smoke per family. No matrix. Sequential families only unless
each run has a fully separate QEMU + artifact namespace.
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

_AGENT_ROOT = Path(__file__).resolve().parents[1]
_HARNESS = _AGENT_ROOT / "external" / "MyPCBench-main" / "agent-harness"
for p in (_HARNESS, _AGENT_ROOT / "scripts", _AGENT_ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from env import MyPCBenchEnv  # noqa: E402

from generic_executor.executor import build_qwen_cuabash_agent  # noqa: E402
from generic_executor.family_config import FAMILY_CONFIGS  # noqa: E402
from generic_executor.gate0a_binding import get_gate0a_binding  # noqa: E402
from generic_executor.openrouter_chat import (  # noqa: E402
    OpenRouterChatCompletionsTransport,
    TransportError,
    default_http_post,
)
from generic_executor.transport import install_transport  # noqa: E402
from paper2_traj_terminal import inspect_last_action  # noqa: E402

FAMILY_SLUG = os.environ.get("GATE0A_FAMILY", "flash").strip().lower()
BINDING = get_gate0a_binding(FAMILY_SLUG)
OUT_DIR = Path(
    os.environ.get("GATE0A_OUT") or (_AGENT_ROOT / BINDING.default_out_rel)
)
MODEL = os.environ.get("GATE0A_MODEL", BINDING.model_id)
# v1.1 default: 10 agent turns (predict rounds). Study 1 stays at 80.
MAX_STEPS = int(os.environ.get("GATE0A_MAX_STEPS", "10"))
GATE_VERSION = os.environ.get("GATE0A_VERSION", "v1.1")
FREEZE_SHA = os.environ.get(
    "GATE0A_FREEZE_SHA", "dd43cbea0150772a804c22cec1c9ddcdb6c94789"
)
TOKEN = os.environ.get("GATE0A_TOKEN") or (
    f"{BINDING.token_prefix.rstrip('-')}-{uuid.uuid4().hex[:16]}"
)
TOKEN_PATH = os.environ.get("GATE0A_TOKEN_PATH", BINDING.token_path)
TOKEN_PREFIX = BINDING.token_prefix
CONTAINER = os.environ.get("GATE0A_CONTAINER", BINDING.container_name)
FAMILY_CFG = FAMILY_CONFIGS[BINDING.family_key]


def _token_byteexact_in(text: str, token: str) -> bool:
    """True iff ``token`` appears as a contiguous UTF-8 substring of ``text``."""
    if not text or not token:
        return False
    return token.encode("utf-8") in text.encode("utf-8")


def _extract_agent_reported_token(bash_outputs: List[str], prefix: str) -> Optional[str]:
    """Token the agent obtained via client-owned bash (tool path), not prose invention.

    Prefers a full line equal to ``prefix…``; else contiguous ``prefix…`` match.
    Task instruction is unchanged — agent is not required to echo the token in
    assistant text; content correctness is tool-mediated.
    """
    for b in bash_outputs:
        for line in b.splitlines():
            s = line.strip()
            if s.startswith(prefix) and re.fullmatch(re.escape(prefix) + r"[0-9a-fA-F]+", s):
                return s
    for b in bash_outputs:
        m = re.search(re.escape(prefix) + r"[0-9a-fA-F]+", b)
        if m:
            return m.group(0)
    return None


def _prose_token_candidates(texts: List[str], prefix: str) -> List[str]:
    found: List[str] = []
    for t in texts:
        for m in re.finditer(re.escape(prefix) + r"[0-9a-fA-F]+", t or ""):
            found.append(m.group(0))
    return found


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
        "gate_version": GATE_VERSION,
        "family": FAMILY_SLUG,
        "family_config_key": BINDING.family_key,
        "model": MODEL,
        "freeze_sha": FREEZE_SHA,
        "started_at": _utc(),
        "token_prefix": TOKEN_PREFIX,
        "token_sha256": hashlib.sha256(TOKEN.encode()).hexdigest(),
        "max_steps": MAX_STEPS,
        "container_name": CONTAINER,
        "step_budget_semantics": (
            f"max_steps={MAX_STEPS} means {MAX_STEPS} predict rounds (agent turns). "
            f"DONE on turn {MAX_STEPS} is permitted if produced during that turn "
            "before budget exhaustion (loop: while not done and step_idx < max_steps)."
        ),
        "study1_clarification": (
            "The max_steps change from 4 to 10 applies only to Gate 0A smoke "
            "execution under the generic agent loop. It does not modify the frozen "
            "max_steps=80 / timeout=7200 invariants for Study 1 instrument execution "
            "(paper2_exec_run.sh / legacy qwen_cuabash configuration)."
        ),
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
                    f"# Gate 0A {FAMILY_SLUG} smoke report ({GATE_VERSION})",
                    "",
                    f"- verdict: **{report['verdict']}**",
                    f"- family: `{FAMILY_SLUG}`",
                    f"- failure_class: `{report.get('failure_class')}`",
                    f"- stop_reason: {report.get('stop_reason')}",
                    f"- model: `{report['model']}`",
                    f"- max_steps: `{report['max_steps']}`",
                    f"- freeze: `{report['freeze_sha']}`",
                    f"- pillars: `{json.dumps(report.get('pillars'))}`",
                    f"- checks: `{json.dumps(report['checks'])}`",
                    "",
                ]
            )
            + "\n"
        )

    # --- Guardrails ---
    if MODEL != BINDING.model_id:
        report["stop_reason"] = f"model mismatch: {MODEL} != {BINDING.model_id}"
        report["failure_class"] = "transport"
        report["verdict"] = "FAIL"
        write_report()
        return 2
    if not TOKEN.startswith(TOKEN_PREFIX):
        report["stop_reason"] = (
            f"token prefix mismatch: expected {TOKEN_PREFIX!r}, got {TOKEN[:32]!r}"
        )
        report["failure_class"] = "QEMU ownership"
        report["verdict"] = "FAIL"
        write_report()
        return 2
    if MODEL in BINDING.forbid_fallback_models:
        report["stop_reason"] = f"model is a forbidden fallback: {MODEL}"
        report["failure_class"] = "transport"
        report["verdict"] = "FAIL"
        write_report()
        return 2
    for bad_key in BINDING.forbid_env_keys:
        if os.environ.get(bad_key):
            report["stop_reason"] = f"{bad_key} still set"
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
        "lane": BINDING.lane,
        "family": FAMILY_SLUG,
    }

    qcow2 = os.environ.get("MYPCBENCH_QCOW2") or str(
        _AGENT_ROOT / "external/MyPCBench-main/mypcbench-vm/mypcbench.qcow2"
    )
    screen = (1280, 800)
    env = MyPCBenchEnv(
        container_name=CONTAINER,
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
            task_config={"id": f"gate0a-{FAMILY_SLUG}", "instruction": "gate0a"},
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
            family=FAMILY_CFG,
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
            f"Expected token prefix: {TOKEN_PREFIX}"
        )

        step_idx = 0
        done = False
        done_round: Optional[int] = None
        consecutive_empty = 0
        turn_actions: List[List[str]] = []
        bash_outputs: List[str] = []
        response_texts: List[str] = []
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

            response_texts.append(response or "")

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
                "response_has_token": _token_byteexact_in(response or "", TOKEN),
                "actions": list(actions),
                "pending_bash": bool(agent._pending_bash_result),
                "n_screenshots": len(agent._inner.screenshots),
            }

            # Bash executed client-side inside predict when XML present.
            if agent._pending_bash_result:
                bash_outputs.append(agent._pending_bash_result)
                turn_rec["bash_result_head"] = agent._pending_bash_result[:500]
                turn_rec["bash_has_token"] = _token_byteexact_in(
                    agent._pending_bash_result, TOKEN
                )

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
                    done_round = step_idx + 1
                    break
            turn_rec["kind"] = "gui"
            turn_rec["executed"] = executed
            turn_rec["produced_done"] = bool(done and done_round == step_idx + 1)
            turn_actions.append(executed)
            report["turns"].append(turn_rec)
            step_idx += 1

        report["http_requests"] = http_log
        report["shot_hashes"] = shot_hashes
        report["n_predict_rounds"] = step_idx
        report["done_round"] = done_round
        report["bash_outputs_token_flags"] = [
            _token_byteexact_in(b, TOKEN) for b in bash_outputs
        ]

        reported = _extract_agent_reported_token(bash_outputs, TOKEN_PREFIX)
        report["agent_reported_token"] = reported
        report["agent_reported_token_sha256"] = (
            hashlib.sha256(reported.encode()).hexdigest() if reported else None
        )
        prose_cands = _prose_token_candidates(response_texts, TOKEN_PREFIX)
        report["prose_token_candidates"] = prose_cands

        # --- Score P1–P4 ---
        checks = report["checks"]
        checks["p1_no_token_in_turn1_provider_response"] = not any(
            (t.get("round") == 1 and t.get("response_has_token")) for t in report["turns"]
        )
        # Prefer: token seen in client bash result
        checks["p1_token_via_client_bash"] = any(
            _token_byteexact_in(b, TOKEN) for b in bash_outputs
        )
        # Or in traj after client path
        traj_text = traj_path.read_text() if traj_path.exists() else ""
        checks["p1_token_in_traj_after_client"] = (
            _token_byteexact_in(traj_text, TOKEN) and checks["p1_token_via_client_bash"]
        )

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

        # P4 v1.1: DONE within budget (turns 1..MAX_STEPS inclusive) + token byte-exact.
        checks["p4_done_within_budget"] = bool(
            checks.get("p4_valid_done")
            and checks.get("p4_not_heuristic")
            and done_round is not None
            and 1 <= done_round <= MAX_STEPS
        )
        checks["p4_token_byteexact"] = reported == TOKEN
        checks["p4_token_via_client_bash_byteexact"] = any(
            _token_byteexact_in(b, TOKEN) for b in bash_outputs
        )
        # If assistant prose invents a different candidate token, fail closed.
        checks["p4_no_conflicting_prose_token"] = all(c == TOKEN for c in prose_cands)
        first_bash_token_round = next(
            (t["round"] for t in report["turns"] if t.get("bash_has_token")),
            None,
        )
        checks["p4_done_after_token_observed"] = bool(
            first_bash_token_round is not None
            and done_round is not None
            and done_round >= first_bash_token_round
        )
        report["first_bash_token_round"] = first_bash_token_round

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
        p4 = bool(
            checks.get("p4_done_within_budget")
            and checks.get("p4_token_byteexact")
            and checks.get("p4_token_via_client_bash_byteexact")
            and checks.get("p4_no_conflicting_prose_token")
            and checks.get("p4_done_after_token_observed")
        )

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
