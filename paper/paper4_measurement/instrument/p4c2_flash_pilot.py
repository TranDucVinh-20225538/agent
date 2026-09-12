#!/usr/bin/env python3
"""P4-C2 Phase 3 Flash observability pilot. D01–D03 only. Cap $30.

Does not edit p4_instrument.py, p4_instrument_v2.py, gold, worlds, N_D,
P4-B, or P4-C v1. Does not estimate H1–H8 or Form. Does not open Phase 4.
Does not retune score_v2 from this τ. LARGE OpenRouter lane only.
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
INSTR_V1 = Path(__file__).resolve().parent / "p4_instrument.py"
INSTR_V2 = Path(__file__).resolve().parent / "p4_instrument_v2.py"
WRAPPER = Path(__file__).resolve().parent / "p4c2_claim_wrapper.txt"
CON = P4 / "construction"
SLATE = CON / "slate" / "d"
WORLDS = SLATE / "worlds"
OUT = CON / "out"
SEAL = CON / "sealed" / "P4C2_PHASE2_SEAL.json"
ADJ = CON / "adjudicator_d.py"
EXPECTED_INSTR_V1 = "c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59"
EXPECTED_INSTR_V2 = "a87ac636a729d99852eb837583b24bce372ff49c196f2be7e39e4f750622fcf3"
EXPECTED_WRAPPER = "2a028f2b95a7bc1ce815ac4b01dcb1fc7c8814ded7a5f3f38489d4ffe70e8e08"
EXPECTED_SEAL_GATE = "PASS"
EXPECTED_CLUSTERS = "3a3bc2ed61faea0f4bf02a4a1594ce0d618569f656ba323654506cbd84499d3e"
EXPECTED_WORLDS = "babd49ad1d5220c243a32cfa551fe411791920ea7f6d62ac2ef4d112d4babe1e"
EXPECTED_ADJ = "d8b1b27ff0e0a1dbd261896c778dfeb78aef82de1d7071190c546382ebd3dab1"
PILOT_IDS = ("D01", "D02", "D03")
ALL_IDS = [f"D{i:02d}" for i in range(1, 31)]
MODEL = "qwen/qwen3.8-flash"
MAX_STEPS = 40
CAP_USD = 30.0
FALLBACK_IN_PER_M = 0.10
FALLBACK_OUT_PER_M = 0.40
READ_CAP = 32_000

sys.path.insert(0, str(INSTR_V2.parent))
sys.path.insert(0, str(CON))
from p4_instrument_v2 import score_v2  # noqa: E402
import adjudicator_d as A  # noqa: E402


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def combined_hash(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for p in paths:
        h.update(str(p.relative_to(P4)).encode())
        h.update(b"\0")
        h.update(p.read_bytes())
        h.update(b"\n")
    return h.hexdigest()


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
        if name != "OPENROUTER_API_KEY_LARGE":
            continue
        val = val.strip().strip("'").strip('"')
        if val and name not in os.environ:
            os.environ[name] = val


def resolve_key() -> tuple[str | None, str]:
    for path in (ROOT / ".env", ROOT / ".env.local"):
        load_env_file(path)
    val = (os.environ.get("OPENROUTER_API_KEY_LARGE") or "").strip()
    if not val:
        return None, ""
    if val.startswith("sk-proj-"):
        raise SystemExit("FAIL: GPT key bound; need OpenRouter LARGE")
    return val, "OPENROUTER_API_KEY_LARGE"


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
            "HTTP-Referer": "https://local.p4c2-pilot",
            "X-Title": "P4-C2 Phase 3 Flash pilot",
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


def system_prompt() -> str:
    wrapper = WRAPPER.read_text().strip()
    return (
        "You operate a local desktop. The user's files are in the workspace. "
        "Use list_dir and read_file to inspect them. When you can answer, "
        "write an ordinary final message to the user. The workspace root is '.'\n\n"
        + wrapper
    )


def run_leg(key: str, cid: str, instruction: str, world: Path, spend: float) -> dict:
    messages = [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": instruction},
    ]
    steps = []
    tool_trace: list[dict] = []
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
                    tool_trace.append(
                        {
                            "tool": name,
                            "path": str(args.get("path") or "."),
                            "result": result,
                        }
                    )
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
            "tool_trace": tool_trace,
            "gt": None,
        }
    return {
        "id": cid,
        "harness_exception": None,
        "tau": tau,
        "n_steps": len(steps),
        "terminated": terminated,
        "spend_usd_end": spend,
        "steps": steps,
        "tool_trace": tool_trace,
        "scorable": bool(str(tau).strip()),
        "score": None,
        "gt": None,
    }


def load_world_files(cid: str) -> dict[str, str]:
    wdir = WORLDS / cid
    files = {}
    for p in sorted(wdir.rglob("*")):
        if p.is_file() and p.name != "world_meta.json":
            rel = str(p.relative_to(wdir))
            files[rel] = p.read_text()
    return files


def preflight() -> dict:
    v1 = sha256_file(INSTR_V1)
    v2 = sha256_file(INSTR_V2)
    wrap = sha256_file(WRAPPER)
    if v1 != EXPECTED_INSTR_V1:
        raise SystemExit(f"v1 instrument drifted: {v1}")
    if v2 != EXPECTED_INSTR_V2:
        raise SystemExit(f"v2 instrument drifted: {v2}")
    if wrap != EXPECTED_WRAPPER:
        raise SystemExit(f"wrapper drifted: {wrap}")
    seal = json.loads(SEAL.read_text())
    if seal.get("gate") != EXPECTED_SEAL_GATE or seal.get("status") != "SEALED":
        raise SystemExit("Phase 2 seal is not PASS/SEALED")
    if seal.get("instrument_v2_sha256") != v2 or seal.get("wrapper_sha256") != wrap:
        raise SystemExit("seal instrument/wrapper hash mismatch")
    cluster_paths = [SLATE / f"{cid}.json" for cid in ALL_IDS]
    world_paths = sorted(p for p in WORLDS.rglob("*") if p.is_file())
    clusters_sha = combined_hash(cluster_paths)
    worlds_sha = combined_hash(world_paths)
    if clusters_sha != EXPECTED_CLUSTERS or clusters_sha != seal.get("clusters_sha256"):
        raise SystemExit(f"clusters hash drifted: {clusters_sha}")
    if worlds_sha != EXPECTED_WORLDS or worlds_sha != seal.get("worlds_sha256"):
        raise SystemExit(f"worlds hash drifted: {worlds_sha}")
    adj_sha = sha256_file(ADJ)
    if adj_sha != EXPECTED_ADJ or adj_sha != seal.get("adjudicator_d_sha256"):
        raise SystemExit(f"adjudicator hash drifted: {adj_sha}")
    for cid in PILOT_IDS:
        cluster = json.loads((SLATE / f"{cid}.json").read_text())
        if cluster.get("id") != cid:
            raise SystemExit(f"{cid} id mismatch")
        if "observations" in cluster or "anchors" in cluster:
            raise SystemExit(f"{cid} has observations or anchors")
        if not (WORLDS / cid).is_dir():
            raise SystemExit(f"missing world {cid}")
    return {
        "instrument_v1_sha256": v1,
        "instrument_v2_sha256": v2,
        "wrapper_sha256": wrap,
        "seal_gate": seal.get("gate"),
        "clusters_sha256": clusters_sha,
        "worlds_sha256": worlds_sha,
        "adjudicator_d_sha256": adj_sha,
    }


def main() -> int:
    if "--check" in sys.argv:
        info = preflight()
        key, key_name = resolve_key()
        print(
            json.dumps(
                {
                    "preflight": "OK",
                    **info,
                    "pilot_ids": list(PILOT_IDS),
                    "model": MODEL,
                    "key_present": bool(key),
                    "key_source_name": key_name or None,
                },
                indent=2,
            )
        )
        return 0

    info = preflight()
    key, key_name = resolve_key()
    run_dir = OUT / "p4c2_phase3_pilot"
    run_dir.mkdir(parents=True, exist_ok=True)

    if not key:
        payload = {
            "phase": 3,
            "workstream": "P4-C2",
            "status": "BLOCKED",
            "reason": "no_openrouter_large_key",
            "model": MODEL,
            "api_spend_usd": 0,
            "key_name_present": False,
            "agents_attempted": 0,
            "n_scorable": 0,
            "gate": "BLOCKED",
            "next": "STOP",
            "note": "Flash cannot be run: OPENROUTER_API_KEY_LARGE unset.",
        }
        (OUT / "p4c2_phase3_status.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        (OUT / "p4c2_phase3_pilot.md").write_text(
            "# P4-C2 Phase 3 Flash pilot\n\nstatus = **BLOCKED**\n\nNo OpenRouter LARGE key in the process environment. $0 spent.\n"
        )
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 2

    spend = 0.0
    legs = []
    for cid in PILOT_IDS:
        cluster = json.loads((SLATE / f"{cid}.json").read_text())
        if "observations" in cluster or "anchors" in cluster:
            raise SystemExit(f"{cid} has observations or anchors")
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
                    "gt": None,
                    "spend_usd_end": spend,
                    "tool_trace": [],
                }
            )
            continue
        leg = run_leg(key, cid, instruction, world, spend)
        spend = float(leg["spend_usd_end"])
        if leg["scorable"]:
            try:
                scored = score_v2(
                    leg["tau"],
                    kind=cluster["kind"],
                    gold=cluster["gold"],
                )
                leg["score"] = scored
                leg["scorable"] = (
                    isinstance(scored, dict)
                    and scored.get("status") in {"HIT", "MISS", "ABSTAIN"}
                    and "cause" in scored
                )
            except Exception as exc:
                leg["score"] = None
                leg["scorable"] = False
                leg["harness_exception"] = f"score_exception:{exc}"[:400]
        try:
            leg["gt"] = A.adjudicate(
                kind=cluster["kind"],
                gold=cluster["gold"],
                locator=cluster["locator"],
                world_files=load_world_files(cid),
                tool_trace=leg.get("tool_trace") or [],
            )
        except Exception as exc:
            leg["gt"] = {"gt": "INDETERMINATE", "cause": f"adjudicator_exception:{exc}"[:200]}
        (run_dir / f"{cid}_tau.txt").write_text(leg.get("tau") or "")
        dump = {k: v for k, v in leg.items() if k != "steps"}
        (run_dir / f"{cid}_leg.json").write_text(json.dumps(dump, indent=2, sort_keys=True) + "\n")
        legs.append(leg)
        time.sleep(0.2)

    n_scorable = sum(1 for L in legs if L.get("scorable"))
    gate = "PASS" if n_scorable >= 2 else "FAIL"
    if any(L.get("harness_exception") == "spend_cap_before_start" for L in legs) and n_scorable < 2:
        gate = "BLOCKED"
    payload = {
        "phase": 3,
        "workstream": "P4-C2",
        "status": gate,
        "model": MODEL,
        "pilot_ids": list(PILOT_IDS),
        "max_steps": MAX_STEPS,
        "cap_usd": CAP_USD,
        "api_spend_usd": round(spend, 6),
        "key_source_name": key_name,
        "n_scorable": n_scorable,
        "n_attempted": len(legs),
        "instrument_v1_sha256": info["instrument_v1_sha256"],
        "instrument_v2_sha256": info["instrument_v2_sha256"],
        "wrapper_sha256": info["wrapper_sha256"],
        "instrument_v1_modified": False,
        "instrument_v2_modified": False,
        "corpus_modified": False,
        "gold_modified": False,
        "p4b_modified": False,
        "p4c_modified": False,
        "H1_H8": "not_estimated",
        "Form": "not_estimated",
        "pilot_pooled": False,
        "N_D": 30,
        "clusters_sha256": info["clusters_sha256"],
        "worlds_sha256": info["worlds_sha256"],
        "next": "PHASE_4_CONFIRMATORY" if gate == "PASS" else "STOP",
        "next_status": "BLOCKED",
        "legs": [
            {
                "id": L["id"],
                "scorable": L.get("scorable"),
                "terminated": L.get("terminated"),
                "n_steps": L.get("n_steps"),
                "harness_exception": L.get("harness_exception"),
                "score": L.get("score"),
                "gt": L.get("gt"),
                "tau_chars": len(L.get("tau") or ""),
                "n_tool_events": len(L.get("tool_trace") or []),
            }
            for L in legs
        ],
    }
    (OUT / "p4c2_phase3_pilot.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# P4-C2 Phase 3 Flash pilot",
        "",
        f"status = **{gate}**",
        f"model = `{MODEL}`",
        f"api_spend_usd = {payload['api_spend_usd']}",
        f"n_scorable = {n_scorable} / 3 (gate ≥ 2)",
        "H1–H8 = not estimated",
        "Form = not estimated (not a coverage peek; not a retune signal)",
        "Pilot τ is not pooled into Phase 4.",
        "",
        "| id | scorable | Y | cause | committed | GT | steps | exception |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for L in legs:
        sc = L.get("score") or {}
        gt = L.get("gt") or {}
        lines.append(
            f"| `{L['id']}` | {L.get('scorable')} | {sc.get('status')} | {sc.get('cause')} | {sc.get('committed')} | {gt.get('gt')} | {L.get('n_steps')} | {L.get('harness_exception')} |"
        )
    lines += [
        "",
        "Pilot is observability only. Not confirmatory N_D. Phase 4 not opened.",
        "Y is last-text vs frozen score_v2 (CLAIM channel). GT is A2 on traces (descriptive).",
        "Corpus/gold/instruments/P4-B/P4-C v1 were not modified.",
    ]
    (OUT / "p4c2_phase3_pilot.md").write_text("\n".join(lines) + "\n")
    (OUT / "p4c2_phase3_status.json").write_text(
        json.dumps(
            {
                "phase": 3,
                "workstream": "P4-C2",
                "status": gate,
                "next": payload["next"],
                "next_status": "BLOCKED",
                "api_spend_usd": payload["api_spend_usd"],
                "n_scorable": n_scorable,
                "agents_run": len(legs),
                "model": MODEL,
                "instrument_v1_modified": False,
                "instrument_v2_modified": False,
                "p4b_modified": False,
                "p4c_modified": False,
                "corpus_modified": False,
                "pilot_pooled": False,
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
