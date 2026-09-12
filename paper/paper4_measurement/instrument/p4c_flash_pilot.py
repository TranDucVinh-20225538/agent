#!/usr/bin/env python3
"""P4-C Phase 3 Flash observability pilot. C01–C03 only. Cap $30.

Does not edit p4_instrument.py, gold, anchors, worlds, N_C, or P4-B.
Does not estimate G1–G6. Does not open GPT/Claude/Phase 4.
LARGE OpenRouter lane only (P4-C licence). No silent SMALL failover.
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
CON = P4 / "construction"
SLATE = CON / "slate" / "c"
WORLDS = SLATE / "worlds"
OUT = CON / "out"
SEAL = CON / "sealed" / "P4C_PHASE2_SEAL.json"
ADJ = CON / "adjudicator_c.py"
EXPECTED_INSTR = "c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59"
EXPECTED_SEAL_GATE = "PASS"
EXPECTED_CLUSTERS = "bd30104becac546169ce62f921e6079a3df758a9a0fccf95106f9aa59060352f"
EXPECTED_WORLDS = "b39c1e082a21c18f4a2b105e94586b3d0584b57af6c3a6904e50fa903ef75c4b"
EXPECTED_ADJ = "595b02f50a2ad968b56051bb4d0b8d8686697a29a94ac39afaf2e1d53b97a8b2"
PILOT_IDS = ("C01", "C02", "C03")
ALL_IDS = [f"C{i:02d}" for i in range(1, 31)]
MODEL = "qwen/qwen3.8-flash"
MAX_STEPS = 40
CAP_USD = 30.0
FALLBACK_IN_PER_M = 0.10
FALLBACK_OUT_PER_M = 0.40
READ_CAP = 32_000

sys.path.insert(0, str(INSTR.parent))
sys.path.insert(0, str(CON))
from p4_instrument import score  # noqa: E402
import adjudicator_c as A  # noqa: E402


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
            "HTTP-Referer": "https://local.p4c-pilot",
            "X-Title": "P4-C Phase 3 Flash pilot",
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
    instr_sha = sha256_file(INSTR)
    if instr_sha != EXPECTED_INSTR:
        raise SystemExit(f"instrument drifted: {instr_sha}")
    seal = json.loads(SEAL.read_text())
    if seal.get("gate") != EXPECTED_SEAL_GATE or seal.get("status") != "SEALED":
        raise SystemExit("Phase 2 seal is not PASS/SEALED")
    cluster_paths = [SLATE / f"{cid}.json" for cid in ALL_IDS]
    world_paths = sorted(p for p in WORLDS.rglob("*") if p.is_file())
    clusters_sha = combined_hash(cluster_paths)
    worlds_sha = combined_hash(world_paths)
    if clusters_sha != EXPECTED_CLUSTERS or clusters_sha != seal.get("clusters_sha256"):
        raise SystemExit(f"clusters hash drifted: {clusters_sha}")
    if worlds_sha != EXPECTED_WORLDS or worlds_sha != seal.get("worlds_sha256"):
        raise SystemExit(f"worlds hash drifted: {worlds_sha}")
    adj_sha = sha256_file(ADJ)
    if adj_sha != EXPECTED_ADJ or adj_sha != seal.get("adjudicator_c_sha256"):
        raise SystemExit(f"adjudicator hash drifted: {adj_sha}")
    for cid in PILOT_IDS:
        cluster = json.loads((SLATE / f"{cid}.json").read_text())
        if cluster.get("id") != cid:
            raise SystemExit(f"{cid} id mismatch")
        if "observations" in cluster:
            raise SystemExit(f"{cid} has observations")
        if not (WORLDS / cid).is_dir():
            raise SystemExit(f"missing world {cid}")
    return {
        "instrument_sha256": instr_sha,
        "seal_gate": seal.get("gate"),
        "clusters_sha256": clusters_sha,
        "worlds_sha256": worlds_sha,
        "adjudicator_c_sha256": adj_sha,
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
    instr_sha = info["instrument_sha256"]
    key, key_name = resolve_key()
    run_dir = OUT / "p4c_phase3_pilot"
    run_dir.mkdir(parents=True, exist_ok=True)

    if not key:
        payload = {
            "phase": 3,
            "workstream": "P4-C",
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
        (OUT / "p4c_phase3_status.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        (OUT / "p4c_phase3_pilot.md").write_text(
            "# P4-C Phase 3 Flash pilot\n\nstatus = **BLOCKED**\n\nNo OpenRouter LARGE key in the process environment. $0 spent.\n"
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
                scored = score(
                    leg["tau"],
                    kind=cluster["kind"],
                    gold=cluster["gold"],
                    anchors=cluster["anchors"],
                )
                leg["score"] = scored
                leg["scorable"] = (
                    isinstance(scored, dict) and "status" in scored and "cause" in scored
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
        "workstream": "P4-C",
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
        "p4b_modified": False,
        "G1_G6": "not_estimated",
        "N_C": 30,
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
    (OUT / "p4c_phase3_pilot.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# P4-C Phase 3 Flash pilot",
        "",
        f"status = **{gate}**",
        f"model = `{MODEL}`",
        f"api_spend_usd = {payload['api_spend_usd']}",
        f"n_scorable = {n_scorable} / 3 (gate ≥ 2)",
        f"G1–G6 = not estimated",
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
        "Pilot is observability only. Not confirmatory N_C. Phase 4 not opened.",
        "Y is last-text vs frozen instrument. GT is adjudicator A on traces (descriptive).",
        "Corpus/gold/instrument/P4-B were not modified.",
    ]
    (OUT / "p4c_phase3_pilot.md").write_text("\n".join(lines) + "\n")
    (OUT / "p4c_phase3_status.json").write_text(
        json.dumps(
            {
                "phase": 3,
                "workstream": "P4-C",
                "status": gate,
                "next": payload["next"],
                "next_status": "BLOCKED",
                "api_spend_usd": payload["api_spend_usd"],
                "n_scorable": n_scorable,
                "agents_run": len(legs),
                "model": MODEL,
                "instrument_modified": False,
                "p4b_modified": False,
                "corpus_modified": False,
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
