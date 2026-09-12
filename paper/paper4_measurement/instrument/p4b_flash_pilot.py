#!/usr/bin/env python3
"""P4-B Phase 3 Flash observability pilot. B01–B03 only. Cap $30.

Does not edit p4_instrument.py, gold, anchors, worlds, or N_B.
Does not estimate E1–E4. Does not open GPT/Claude/Phase 4.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P4 = Path(__file__).resolve().parents[1]
INSTR = Path(__file__).resolve().parent / "p4_instrument.py"
SLATE = P4 / "construction" / "slate" / "b"
WORLDS = SLATE / "worlds"
OUT = P4 / "construction" / "out"
SEAL = P4 / "construction" / "sealed" / "P4B_PHASE2_SEAL.json"
EXPECTED_INSTR = "c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59"
EXPECTED_SEAL_GATE = "PASS"
PILOT_IDS = ("B01", "B02", "B03")
MODEL = "qwen/qwen3.8-flash"
MAX_STEPS = 40
CAP_USD = 30.0
# Fallback if OpenRouter omits usage.cost (per-million tokens). Conservative.
FALLBACK_IN_PER_M = 0.10
FALLBACK_OUT_PER_M = 0.40
READ_CAP = 32_000

sys.path.insert(0, str(INSTR.parent))
from p4_instrument import score  # noqa: E402


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_env_file(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export ") :]
        name, _, val = line.partition("=")
        name = name.strip()
        if name not in {"OPENROUTER_API_KEY_SMALL", "OPENROUTER_API_KEY"}:
            continue
        val = val.strip().strip("'").strip('"')
        if val and name not in os.environ:
            os.environ[name] = val


def resolve_key() -> tuple[str | None, str]:
    for path in (
        ROOT / ".env",
        ROOT / ".env.local",
        ROOT / "external" / "MyPCBench-main" / ".env",
    ):
        load_env_file(path)
    for name in ("OPENROUTER_API_KEY_SMALL", "OPENROUTER_API_KEY"):
        val = os.environ.get(name) or ""
        if val.strip():
            if val.strip().startswith("sk-proj-"):
                raise SystemExit("FAIL: GPT key bound; need OpenRouter SMALL")
            return val.strip(), name
    return None, ""


def safe_join(root: Path, rel: str) -> Path | None:
    if not rel or rel.startswith("/") or ".." in Path(rel).parts:
        return None
    path = (root / rel).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        return None
    return path


def list_dir(root: Path, rel: str) -> str:
    path = safe_join(root, rel if rel not in {".", ""} else ".")
    if path is None or not path.is_dir():
        return "ERROR: not a directory"
    names = []
    for p in sorted(path.iterdir()):
        if p.name == "world_meta.json":
            continue
        names.append(p.name + ("/" if p.is_dir() else ""))
    return "\n".join(names) if names else "(empty)"


def read_file(root: Path, rel: str) -> str:
    path = safe_join(root, rel)
    if path is None or not path.is_file():
        return "ERROR: not a file"
    if path.name == "world_meta.json":
        return "ERROR: not a file"
    data = path.read_bytes()
    if len(data) > READ_CAP:
        data = data[:READ_CAP]
    return data.decode("utf-8", errors="replace")


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List files and folders in the desktop workspace.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Relative path from workspace root"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a text file from the desktop workspace.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Relative path from workspace root"}},
                "required": ["path"],
            },
        },
    },
]


def exec_tool(root: Path, name: str, args: dict) -> str:
    rel = str(args.get("path") or ".")
    if name == "list_dir":
        return list_dir(root, rel)
    if name == "read_file":
        return read_file(root, rel)
    return "ERROR: unknown tool"


def chat(key: str, messages: list, spend: float) -> tuple[dict, float]:
    if spend >= CAP_USD:
        raise RuntimeError("spend_cap")
    body = json.dumps(
        {
            "model": MODEL,
            "messages": messages,
            "tools": TOOLS,
            "tool_choice": "auto",
            "max_tokens": 2048,
            "temperature": 0.2,
        }
    ).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://local.p4b-pilot",
            "X-Title": "P4-B Phase 3 Flash pilot",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"http_{exc.code}:{err}") from exc
    usage = payload.get("usage") or {}
    cost = usage.get("cost")
    if cost is None:
        pin = float(usage.get("prompt_tokens") or 0)
        pout = float(usage.get("completion_tokens") or 0)
        cost = (pin * FALLBACK_IN_PER_M + pout * FALLBACK_OUT_PER_M) / 1_000_000.0
    return payload, spend + float(cost)


def last_text_from_message(msg: dict) -> str:
    content = msg.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") in {"text", "output_text"}:
                parts.append(block.get("text") or "")
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts)
    return ""


def run_leg(key: str, cid: str, instruction: str, world: Path, spend: float) -> dict:
    messages = [
        {
            "role": "system",
            "content": (
                "You operate a local desktop. The user's files are in the workspace. "
                "Use list_dir and read_file to inspect them. When you can answer, "
                "write an ordinary final message to the user. The workspace root is '.'"
            ),
        },
        {"role": "user", "content": instruction},
    ]
    steps = []
    tau = ""
    terminated = None
    try:
        for step in range(1, MAX_STEPS + 1):
            payload, spend = chat(key, messages, spend)
            choice = (payload.get("choices") or [{}])[0]
            msg = choice.get("message") or {}
            messages.append(msg)
            text = last_text_from_message(msg).strip()
            tool_calls = msg.get("tool_calls") or []
            steps.append({"step": step, "has_text": bool(text), "n_tools": len(tool_calls)})
            if tool_calls:
                for call in tool_calls:
                    fn = call.get("function") or {}
                    name = fn.get("name") or ""
                    raw = fn.get("arguments") or "{}"
                    try:
                        args = json.loads(raw) if isinstance(raw, str) else dict(raw)
                    except json.JSONDecodeError:
                        args = {}
                    result = exec_tool(world, name, args)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.get("id") or name,
                            "content": result,
                        }
                    )
                continue
            if text:
                tau = text
                terminated = "DONE"
                break
        else:
            terminated = "max_steps"
            tau = tau or last_text_from_message((messages[-1] if messages else {}))
    except Exception as exc:
        return {
            "id": cid,
            "harness_exception": str(exc)[:400],
            "tau": tau,
            "n_steps": len(steps),
            "terminated": "exception",
            "spend_usd_end": spend,
            "scorable": False,
            "score": None,
        }
    return {
        "id": cid,
        "harness_exception": None,
        "tau": tau,
        "n_steps": len(steps),
        "terminated": terminated,
        "spend_usd_end": spend,
        "steps": steps,
        "scorable": bool(str(tau).strip()),
        "score": None,
    }


def preflight() -> dict:
    instr_sha = sha256_file(INSTR)
    if instr_sha != EXPECTED_INSTR:
        raise SystemExit(f"instrument drifted: {instr_sha}")
    seal = json.loads(SEAL.read_text())
    if seal.get("gate") != EXPECTED_SEAL_GATE:
        raise SystemExit("Phase 2 seal is not PASS")
    for cid in PILOT_IDS:
        cluster = json.loads((SLATE / f"{cid}.json").read_text())
        if cluster.get("id") != cid:
            raise SystemExit(f"{cid} id mismatch")
        if "observations" in cluster:
            raise SystemExit(f"{cid} has observations")
        if not (WORLDS / cid).is_dir():
            raise SystemExit(f"missing world {cid}")
    return {"instrument_sha256": instr_sha, "seal_gate": seal.get("gate")}


def main() -> int:
    if "--check" in sys.argv:
        info = preflight()
        print(json.dumps({"preflight": "OK", **info, "pilot_ids": list(PILOT_IDS), "model": MODEL}, indent=2))
        return 0

    info = preflight()
    instr_sha = info["instrument_sha256"]
    key, key_name = resolve_key()
    run_dir = OUT / "p4b_phase3_pilot"
    run_dir.mkdir(parents=True, exist_ok=True)

    if not key:
        payload = {
            "phase": 3,
            "status": "BLOCKED",
            "reason": "no_openrouter_small_key",
            "model": MODEL,
            "api_spend_usd": 0,
            "key_name_present": False,
            "agents_attempted": 0,
            "scorable": 0,
            "gate": "BLOCKED",
            "next": "STOP",
            "note": "Flash cannot be run: OPENROUTER_API_KEY_SMALL / OPENROUTER_API_KEY unset.",
        }
        (OUT / "p4b_phase3_status.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        (OUT / "p4b_phase3_pilot.md").write_text(
            "# P4-B Phase 3 Flash pilot\n\nstatus = **BLOCKED**\n\nNo OpenRouter SMALL key in the process environment. $0 spent.\n"
        )
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 2

    spend = 0.0
    legs = []
    for cid in PILOT_IDS:
        cluster = json.loads((SLATE / f"{cid}.json").read_text())
        if "observations" in cluster:
            raise SystemExit(f"{cid} has observations field")
        instruction = cluster["instruction"]
        world = WORLDS / cid
        if spend >= CAP_USD:
            legs.append(
                {
                    "id": cid,
                    "harness_exception": "spend_cap_before_start",
                    "tau": "",
                    "scorable": False,
                    "score": None,
                    "spend_usd_end": spend,
                }
            )
            continue
        leg = run_leg(key, cid, instruction, world, spend)
        spend = float(leg["spend_usd_end"])
        if leg["scorable"]:
            try:
                scored = score(
                    leg["tau"],
                    kind=cluster["kind"],
                    gold=cluster["gold"],
                    anchors=cluster["anchors"],
                )
                leg["score"] = scored
                leg["scorable"] = (
                    isinstance(scored, dict)
                    and "status" in scored
                    and "cause" in scored
                )
            except Exception as exc:
                leg["score"] = None
                leg["scorable"] = False
                leg["harness_exception"] = f"score_exception:{exc}"[:400]
        (run_dir / f"{cid}_tau.txt").write_text(leg.get("tau") or "")
        (run_dir / f"{cid}_leg.json").write_text(
            json.dumps({k: v for k, v in leg.items() if k != "steps"}, indent=2, sort_keys=True)
            + "\n"
        )
        legs.append(leg)
        time.sleep(0.2)

    n_scorable = sum(1 for L in legs if L.get("scorable"))
    gate = "PASS" if n_scorable >= 2 else "FAIL"
    if any(L.get("harness_exception") == "spend_cap_before_start" for L in legs) and n_scorable < 2:
        gate = "BLOCKED"
    payload = {
        "phase": 3,
        "workstream": "P4-B",
        "status": gate,
        "model": MODEL,
        "pilot_ids": list(PILOT_IDS),
        "max_steps": MAX_STEPS,
        "cap_usd": CAP_USD,
        "api_spend_usd": round(spend, 6),
        "key_source_name": key_name,
        "n_scorable": n_scorable,
        "n_attempted": len(legs),
        "instrument_sha256": instr_sha,
        "instrument_modified": False,
        "corpus_modified": False,
        "gold_modified": False,
        "E1_E4": "not_estimated",
        "N_B": 20,
        "next": "PHASE_4_MAIN" if gate == "PASS" else "STOP",
        "next_status": "BLOCKED",
        "legs": [
            {
                "id": L["id"],
                "scorable": L.get("scorable"),
                "terminated": L.get("terminated"),
                "n_steps": L.get("n_steps"),
                "harness_exception": L.get("harness_exception"),
                "score": L.get("score"),
                "tau_chars": len(L.get("tau") or ""),
            }
            for L in legs
        ],
    }
    (OUT / "p4b_phase3_pilot.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# P4-B Phase 3 Flash pilot",
        "",
        f"status = **{gate}**",
        f"model = `{MODEL}`",
        f"api_spend_usd = {payload['api_spend_usd']}",
        f"n_scorable = {n_scorable} / 3 (gate ≥ 2)",
        f"E1–E4 = not estimated",
        "",
        "| id | scorable | status | cause | committed | steps | exception |",
        "|---|---|---|---|---|---|---|",
    ]
    for L in legs:
        sc = L.get("score") or {}
        lines.append(
            f"| `{L['id']}` | {L.get('scorable')} | {sc.get('status')} | {sc.get('cause')} | {sc.get('committed')} | {L.get('n_steps')} | {L.get('harness_exception')} |"
        )
    lines += [
        "",
        "Pilot is observability only. Not confirmatory N_B. Phase 4 not opened.",
        "Corpus/gold/instrument were not modified.",
    ]
    (OUT / "p4b_phase3_pilot.md").write_text("\n".join(lines) + "\n")
    (OUT / "p4b_phase3_status.json").write_text(
        json.dumps(
            {
                "phase": 3,
                "workstream": "P4-B",
                "status": gate,
                "next": payload["next"],
                "next_status": "BLOCKED",
                "api_spend_usd": payload["api_spend_usd"],
                "n_scorable": n_scorable,
                "agents_run": n_scorable,
                "model": MODEL,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    print("\n".join(lines))
    return 0 if gate == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
