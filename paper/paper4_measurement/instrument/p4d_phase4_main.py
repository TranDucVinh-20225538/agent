#!/usr/bin/env python3
"""P4-D Phase 4 confirmatory validation. 30 clusters × 2 models = 60 legs.

Does not edit p4_instrument.py, p4_instrument_v2.py, wrapper, P4-B, P4-C v1,
or P4-C2. Does not pool Phase-3 pilot τ into N. Does not run Claude. Primary
gates use Flash confirmatory legs. GPT is paired/descriptive. Form is
interface compliance, never named coverage. No minus MISS quota. No CC>=0.90
gate. LARGE OpenRouter lane only.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P4 = Path(__file__).resolve().parents[1]
INSTR_V1 = Path(__file__).resolve().parent / "p4_instrument.py"
INSTR_V2 = Path(__file__).resolve().parent / "p4_instrument_v2.py"
WRAPPER = Path(__file__).resolve().parent / "p4c2_claim_wrapper.txt"
CON = P4 / "construction"
SLATE = CON / "slate" / "e"
EQDIR = CON / "slate" / "eq"
WORLDS = SLATE / "worlds"
OUT = CON / "out"
SEAL = CON / "sealed" / "P4D_PHASE2_SEAL.json"
TRANS = CON / "transforms_d.py"
ADJ = CON / "adjudicator_d.py"
GEN = CON / "generate_e.py"
PARAMS = CON / "params_e.json"
GOLD_SPEC = OUT / "p4d_gold_spec.json"
PHASE3 = OUT / "p4d_phase3_status.json"
RUN = OUT / "p4d_phase4"
EXPECTED_INSTR_V1 = "c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59"
EXPECTED_INSTR_V2 = "a87ac636a729d99852eb837583b24bce372ff49c196f2be7e39e4f750622fcf3"
EXPECTED_WRAPPER = "2a028f2b95a7bc1ce815ac4b01dcb1fc7c8814ded7a5f3f38489d4ffe70e8e08"
EXPECTED_SEAL_GATE = "PASS"
EXPECTED_CLUSTERS = "ba8dd52f29128400b0854f0c0ae7a0a3f7bbd25331aec993e6252a652e7b9562"
EXPECTED_WORLDS = "591fa942685b70f5305faded0d65fee441aab6b72b25fb151f51551b4d81f783"
EXPECTED_GOLD = "283487a2e1ed62a912b08497db1eb1d64a71ebf33c13c551c3602096b0878313"
EXPECTED_TRANS = "bb4a216bfba2f8bb5c914941c9b5d8faf4dd776c8ca30b40a8d3a3dfe9abaf9c"
EXPECTED_ADJ = "d8b1b27ff0e0a1dbd261896c778dfeb78aef82de1d7071190c546382ebd3dab1"
EXPECTED_GEN = "4442e427b273f93a477d326ce7b4346b1f21c4bc02a89dbbf34cc1abfe50cabb"
EXPECTED_PARAMS = "499949c13279c222fdd81660d37fc33370d629bbdfe10bb0d133d90e5b25c6ff"
IDS = [f"E{i:02d}" for i in range(1, 31)]
EQ_IDS = [f"EQ{i:02d}" for i in range(1, 7)]
BANNED_PREFIXES = ("B", "C", "D", "Q", "CQ", "DQ", "V", "R")
FLASH = "qwen/qwen3.8-flash"
GPT = "openai/gpt-5.5"
MODELS = (("flash", FLASH), ("gpt", GPT))
MAX_STEPS = 40
N_E = 30
N_SLOTS = 60
CAP_USD = 400.0
PHASE3_SPEND = 0.001398
FLASH_BURN_PER_LEG = PHASE3_SPEND / 3.0
GPT_QUOTE_MULT = 5.0
READ_CAP = 32_000
FALLBACK_IN_PER_M = 0.10
FALLBACK_OUT_PER_M = 0.40
PLUS_N_FLOOR = 10
PLUS_HIT_GATE = 0.90
HIT_OBS_FLOOR = 8
MISS_OBS_FLOOR = 8
FORM_GATE = 0.80
TRAP_PHRASES = (
    "avoid decoys",
    "ignore the decoy",
    "this is a trap",
    "not the first number",
    "the answer is not",
    "do not use the stale",
    "not the stale",
)
CLAIM_LINE = re.compile(r"^\s*CLAIM\s*:", re.I)

sys.path.insert(0, str(INSTR_V2.parent))
sys.path.insert(0, str(CON))
from p4_instrument_v2 import score_v2, v1_clean, v3_match  # noqa: E402
import generate_d as g  # noqa: E402
import transforms_d as T  # noqa: E402
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


def chat(key: str, model: str, messages: list, spend: float) -> tuple[dict, float]:
    if spend >= CAP_USD:
        raise RuntimeError("spend_cap")
    body = json.dumps(
        {
            "model": model,
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
            "HTTP-Referer": "https://local.p4d-phase4",
            "X-Title": "P4-D Phase 4 confirmatory",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
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


def run_leg(key: str, model: str, instruction: str, world: Path, spend: float) -> dict:
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
            payload, spend = chat(key, model, messages, spend)
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
                        {"tool": name, "path": str(args.get("path") or "."), "result": result}
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
            tau = tau or last_text_from_message(messages[-1] if messages else {})
    except Exception as exc:
        return {
            "harness_exception": str(exc)[:400],
            "tau": tau,
            "n_steps": len(steps),
            "terminated": "exception",
            "spend_usd_end": spend,
            "scorable": False,
            "score": None,
            "steps": steps,
            "tool_trace": tool_trace,
        }
    return {
        "harness_exception": None,
        "tau": tau,
        "n_steps": len(steps),
        "terminated": terminated,
        "spend_usd_end": spend,
        "scorable": bool(str(tau).strip()),
        "score": None,
        "steps": steps,
        "tool_trace": tool_trace,
    }


def parse_disk(path: Path) -> list[dict]:
    text = path.read_text()
    suf = path.suffix.casefold()
    if suf == ".csv":
        return g.parse_csv(text)
    if suf == ".ics":
        return g.parse_ics(text)
    if suf == ".html":
        return g.parse_html(text)
    return g.parse_kv(text)


def load_tables(cid: str) -> dict[str, list[dict]]:
    wdir = WORLDS / cid
    tables = {}
    for p in sorted(wdir.rglob("*")):
        if p.is_file() and p.name != "world_meta.json":
            rel = str(p.relative_to(wdir)).replace("\\", "/")
            tables[rel] = parse_disk(p)
    return tables


def load_world_files(cid: str) -> dict[str, str]:
    wdir = WORLDS / cid
    files = {}
    for p in sorted(wdir.rglob("*")):
        if p.is_file() and p.name != "world_meta.json":
            rel = str(p.relative_to(wdir)).replace("\\", "/")
            files[rel] = p.read_text()
    return files


def probe_value(kind: str, canon: str):
    if kind == "money_usd":
        return Decimal(canon)
    if kind == "integer":
        return int(canon)
    return canon


def same_kind_values(kind: str, gold: str, tables: dict[str, list[dict]]) -> list[str]:
    found = []
    for rows in tables.values():
        for row in rows:
            for raw in row.values():
                s = str(raw).strip()
                if not s:
                    continue
                try:
                    canon = g.format_gold(kind, s)
                except Exception:
                    continue
                if canon == gold:
                    continue
                try:
                    if v3_match(kind, probe_value(kind, canon), gold):
                        continue
                except Exception:
                    pass
                if kind in {"entity", "categorical"}:
                    if canon.casefold() == gold.casefold():
                        continue
                if canon not in found:
                    found.append(canon)
    return found


def distractor_line(val: str) -> str:
    line = f"alt-value {val}"
    if CLAIM_LINE.match(line):
        line = f"working-note {val}"
    return line


def gold_in_clean(tau: str, gold: str) -> bool:
    cleaned, _cause = v1_clean(tau)
    if cleaned is None:
        return False
    return gold in cleaned


def h4_on_tau(tau: str, kind: str, gold: str, d1: str, d2: str, alt_val: str) -> dict:
    base = score_v2(tau, kind=kind, gold=gold)
    c5 = score_v2(T.working_irr(tau, d1), kind=kind, gold=gold)
    t6a, t6b = T.c6_working_pair(tau, d1, d2)
    c6a = score_v2(t6a, kind=kind, gold=gold)
    c6b = score_v2(t6b, kind=kind, gold=gold)
    changed = []
    for name, sc in (("working_irr", c5), ("c6_working_a", c6a), ("c6_working_b", c6b)):
        if sc.get("status") != base.get("status") or sc.get("committed") != base.get("committed"):
            changed.append(name)
    claim_after = score_v2(T.replace_claim(tau, alt_val), kind=kind, gold=gold)
    claim_changed = claim_after.get("status") != base.get("status") or claim_after.get(
        "committed"
    ) != base.get("committed")
    return {
        "base": base,
        "changed": changed,
        "pass": not changed,
        "claim_span_named": {
            "after": claim_after,
            "changed": claim_changed,
            "note": "CLAIM-span C6 may change Y; not a G4 failure",
        },
    }


def h1_transforms_on_tau(tau: str, kind: str, gold: str) -> dict:
    c3 = score_v2(T.c3_drop_claim(tau), kind=kind, gold=gold)
    c4 = score_v2(T.c4_markup(tau, gold), kind=kind, gold=gold)
    hits = []
    if c3.get("status") == "HIT":
        hits.append("c3_drop_claim")
    if c4.get("status") == "HIT":
        hits.append("c4_markup")
    return {"c3": c3, "c4": c4, "hits": hits}


def slots() -> list[tuple[str, str, str]]:
    out = []
    for lane, model in MODELS:
        for cid in IDS:
            out.append((cid, lane, model))
    return out


def designed_c3_c4() -> dict:
    hits = []
    rows = {}
    for cid in EQ_IDS:
        cluster = json.loads((EQDIR / f"{cid}.json").read_text())
        for ctrl in ("C3_NO_CLAIM", "C4_MARKUP"):
            sc = score_v2(
                cluster["observations"][ctrl],
                kind=cluster["kind"],
                gold=cluster["gold"],
            )
            rows[f"{cid}:{ctrl}"] = sc
            if sc.get("status") == "HIT":
                hits.append(f"{cid}:{ctrl}")
    return {"n_hit": len(hits), "hits": hits, "controls": rows}


def h7_instrument_ok(src: str) -> tuple[bool, list[str]]:
    errors: list[str] = []
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "p4_instrument":
            names = {a.name for a in node.names}
            if "score" in names:
                errors.append("G0: score_v2 imports v1 score")
        if isinstance(node, ast.FunctionDef) and node.name == "score_v2":
            args = [a.arg for a in node.args.args] + [a.arg for a in node.args.kwonlyargs]
            if "anchors" in args or "task_id" in args:
                errors.append("G0: score_v2 takes anchors or task_id")
    lowered = src.casefold()
    for tok in ("screenshot", "tool_trace", "world_files"):
        if tok in lowered:
            errors.append(f"G0: instrument mentions {tok}")
    return not errors, errors


def h8_ids_ok() -> tuple[bool, list[str]]:
    errors: list[str] = []
    for cid in IDS:
        if not re.fullmatch(r"E\d{2}", cid):
            errors.append(f"G8: confirmatory id {cid} is not E*")
        if cid.startswith(BANNED_PREFIXES) or cid[0] in "BCDQVR":
            errors.append(f"G8: confirmatory id {cid} collides with banned prefix")
    return not errors, errors


def committed_designed_miss(kind: str, committed, competitors: list) -> bool:
    if committed is None:
        return False
    for comp in competitors or []:
        try:
            if v3_match(kind, probe_value(kind, str(committed)), str(comp)):
                return True
        except Exception:
            if str(committed).strip() == str(comp).strip():
                return True
    return False


def factory_f2_f5() -> dict:
    errors_f2: list[str] = []
    errors_f5: list[str] = []
    wrapper = WRAPPER.read_text()
    tool_blob = json.dumps(TOOLS)
    for cid in IDS:
        cluster = json.loads((SLATE / f"{cid}.json").read_text())
        instr = cluster["instruction"]
        gold = str(cluster["gold"])
        blob = "\n".join([instr, wrapper, tool_blob])
        if gold and gold in blob:
            errors_f2.append(f"{cid}: gold in instruction/wrapper/tools")
        for comp in cluster.get("competitors") or []:
            if comp and str(comp) in blob:
                errors_f2.append(f"{cid}: competitor {comp} in instruction/wrapper/tools")
        low = instr.casefold()
        for phrase in TRAP_PHRASES:
            if phrase in low:
                errors_f5.append(f"{cid}: trap phrase {phrase!r}")
    src = Path(__file__).read_text()
    analyze_src = src.split("def analyze", 1)[-1].split("def write_report", 1)[0]
    f3_fail = "miss_rate >= 0.90" in analyze_src or "C2" + "_FLOOR =" in analyze_src
    return {
        "F2": "PASS" if not errors_f2 else "FAIL",
        "F2_errors": errors_f2,
        "F3": "FAIL" if f3_fail else "PASS",
        "F5": "PASS" if not errors_f5 else "FAIL",
        "F5_errors": errors_f5,
    }


def lane_condition_counts(legs: list[dict], lane: str) -> dict[str, dict]:
    out = {c: {"HIT": 0, "MISS": 0, "ABSTAIN": 0, "unscored": 0, "n": 0} for c in ("plus", "minus", "pm")}
    for row in legs:
        if row.get("lane") != lane:
            continue
        cluster = json.loads((SLATE / f"{row['id']}.json").read_text())
        cond = cluster["condition"]
        cell = out[cond]
        cell["n"] += 1
        sc = row.get("score")
        if not row.get("scorable") or not isinstance(sc, dict):
            cell["unscored"] += 1
            continue
        st = sc.get("status")
        if st in {"HIT", "MISS", "ABSTAIN"}:
            cell[st] += 1
        else:
            cell["unscored"] += 1
    for cond, cell in out.items():
        n = cell["n"] or 1
        hit, miss, abstain = cell["HIT"], cell["MISS"], cell["ABSTAIN"]
        cell["Form"] = (hit + miss) / n
        cell["CC"] = (hit / (hit + miss)) if (hit + miss) else None
        cell["Abs"] = abstain / n
        cell["I_CC"] = int(hit >= HIT_OBS_FLOOR and miss >= MISS_OBS_FLOOR)
    return out


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
    p3 = json.loads(PHASE3.read_text())
    if p3.get("status") != "PASS":
        raise SystemExit("Phase 3 is not PASS")
    if p3.get("pilot_pooled"):
        raise SystemExit("Phase 3 status claims pilot_pooled")
    cluster_paths = [SLATE / f"{cid}.json" for cid in IDS]
    world_paths = sorted(p for p in WORLDS.rglob("*") if p.is_file())
    clusters_sha = combined_hash(cluster_paths)
    worlds_sha = combined_hash(world_paths)
    gold_sha = sha256_file(GOLD_SPEC)
    trans_sha = sha256_file(TRANS)
    adj_sha = sha256_file(ADJ)
    gen_sha = sha256_file(GEN)
    params_sha = sha256_file(PARAMS)
    if clusters_sha != EXPECTED_CLUSTERS or clusters_sha != seal["clusters_sha256"]:
        raise SystemExit(f"clusters hash mismatch: {clusters_sha}")
    if worlds_sha != EXPECTED_WORLDS or worlds_sha != seal["worlds_sha256"]:
        raise SystemExit(f"worlds hash mismatch: {worlds_sha}")
    if gold_sha != EXPECTED_GOLD or gold_sha != seal["gold_spec_sha256"]:
        raise SystemExit(f"gold spec hash mismatch: {gold_sha}")
    if trans_sha != EXPECTED_TRANS or trans_sha != seal["transforms_d_sha256"]:
        raise SystemExit(f"transforms hash mismatch: {trans_sha}")
    if adj_sha != EXPECTED_ADJ or adj_sha != seal["adjudicator_d_sha256"]:
        raise SystemExit(f"adjudicator hash mismatch: {adj_sha}")
    if gen_sha != EXPECTED_GEN or gen_sha != seal["generate_e_sha256"]:
        raise SystemExit(f"generate_e hash mismatch: {gen_sha}")
    if params_sha != EXPECTED_PARAMS or params_sha != seal["params_e_sha256"]:
        raise SystemExit(f"params_e hash mismatch: {params_sha}")
    h7_ok, h7_err = h7_instrument_ok(INSTR_V2.read_text())
    if not h7_ok:
        raise SystemExit("G0 anti-recovery failed: " + "; ".join(h7_err))
    h8_ok, h8_err = h8_ids_ok()
    if not h8_ok:
        raise SystemExit("G8 failed: " + "; ".join(h8_err))
    for cid in IDS:
        cluster = json.loads((SLATE / f"{cid}.json").read_text())
        if cluster.get("id") != cid:
            raise SystemExit(f"{cid} id mismatch")
        if "observations" in cluster:
            raise SystemExit(f"{cid} has observations")
        if "anchors" in cluster:
            raise SystemExit(f"{cid} has anchors")
        if not (WORLDS / cid).is_dir():
            raise SystemExit(f"missing world {cid}")
    remaining = CAP_USD - PHASE3_SPEND
    projected = 30 * FLASH_BURN_PER_LEG + 30 * FLASH_BURN_PER_LEG * GPT_QUOTE_MULT
    if projected > remaining:
        raise SystemExit(f"preflight projection {projected:.6f} exceeds remaining {remaining:.6f}")
    return {
        "instrument_v1_sha256": v1,
        "instrument_v2_sha256": v2,
        "wrapper_sha256": wrap,
        "clusters_sha256": clusters_sha,
        "worlds_sha256": worlds_sha,
        "gold_spec_sha256": gold_sha,
        "transforms_d_sha256": trans_sha,
        "adjudicator_d_sha256": adj_sha,
        "generate_e_sha256": gen_sha,
        "params_e_sha256": params_sha,
        "seal_gate": seal.get("gate"),
        "phase3_spend_usd": PHASE3_SPEND,
        "projected_phase4_usd": round(projected, 6),
        "remaining_cap_usd": round(remaining, 6),
        "flash_model": FLASH,
        "gpt_model": GPT,
        "n_slots": N_SLOTS,
        "N_E": N_E,
        "pilot_pooled": False,
        "form_is_not_coverage": True,
        "G0": "PASS",
        "G8": "PASS",
    }


def load_progress() -> dict[str, dict]:
    path = RUN / "legs.jsonl"
    done = {}
    if not path.is_file():
        return done
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        done[f"{row['id']}:{row['lane']}"] = row
    return done


def append_leg(row: dict) -> None:
    RUN.mkdir(parents=True, exist_ok=True)
    with (RUN / "legs.jsonl").open("a") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")


def lane_counts(legs: list[dict], lane: str) -> dict:
    n_hit = n_miss = n_abstain = n_unscored = 0
    for row in legs:
        if row.get("lane") != lane:
            continue
        sc = row.get("score")
        if not row.get("scorable") or not isinstance(sc, dict):
            n_unscored += 1
            continue
        st = sc.get("status")
        if st == "HIT":
            n_hit += 1
        elif st == "MISS":
            n_miss += 1
        elif st == "ABSTAIN":
            n_abstain += 1
        else:
            n_unscored += 1
    n = n_hit + n_miss + n_abstain
    form = (n_hit + n_miss) / N_E
    cc = (n_hit / (n_hit + n_miss)) if (n_hit + n_miss) else None
    abs_ = n_abstain / N_E
    dh = n_hit / N_E
    return {
        "HIT": n_hit,
        "MISS": n_miss,
        "ABSTAIN": n_abstain,
        "unscored": n_unscored,
        "n_scorable": n,
        "Form": form,
        "CC": cc,
        "Abs": abs_,
        "DH": dh,
    }


def analyze(legs: list[dict]) -> dict:
    by_cluster: dict[str, dict] = {cid: {} for cid in IDS}
    g1_false = []
    g1_transform_hits = []
    g4_fail = []
    plus_elig = []
    designed = designed_c3_c4()
    claim_span_named = []
    n_miss_designed = 0
    miss_designed_ids = []

    for row in legs:
        cid = row["id"]
        lane = row["lane"]
        cluster = json.loads((SLATE / f"{cid}.json").read_text())
        kind, gold = cluster["kind"], cluster["gold"]
        cond = cluster["condition"]
        tables = load_tables(cid)
        vals = same_kind_values(kind, gold, tables)
        d1 = distractor_line(vals[0] if vals else "0")
        d2 = distractor_line(vals[1] if len(vals) > 1 else "1")
        alt_val = vals[0] if vals else "0"
        sc = row.get("score")
        tau = row.get("tau") or ""
        try:
            gt = A.adjudicate(
                kind=kind,
                gold=gold,
                locator=cluster["locator"],
                world_files=load_world_files(cid),
                tool_trace=row.get("tool_trace") or [],
            )
        except Exception as exc:
            gt = {"gt": "INDETERMINATE", "cause": f"adjudicator_exception:{exc}"[:200]}
        row = dict(row)
        row["gt"] = gt
        if row.get("scorable") and isinstance(sc, dict) and tau.strip():
            gic = gold_in_clean(tau, gold)
            if lane == "flash" and (not gic) and sc.get("status") == "HIT":
                g1_false.append({"id": cid, "lane": lane, "committed": sc.get("committed")})
            h1t = h1_transforms_on_tau(tau, kind, gold)
            row["g1_transforms"] = {"hits": h1t["hits"]}
            if lane == "flash" and h1t["hits"]:
                g1_transform_hits.append({"id": cid, "hits": h1t["hits"]})
            inv = h4_on_tau(tau, kind, gold, d1, d2, alt_val)
            row["g4"] = {
                "pass": inv["pass"],
                "changed": inv["changed"],
                "claim_span_named": inv["claim_span_named"],
            }
            if lane == "flash":
                claim_span_named.append(
                    {
                        "id": cid,
                        "changed": inv["claim_span_named"]["changed"],
                        "after_status": (inv["claim_span_named"]["after"] or {}).get("status"),
                    }
                )
                if not inv["pass"]:
                    g4_fail.append({"id": cid, "changed": inv["changed"]})
            gt_lab = gt.get("gt")
            y = sc.get("status")
            committed = y in {"HIT", "MISS"}
            if lane == "flash":
                if cond == "plus" and gt_lab == "SUCCESS" and committed:
                    plus_elig.append({"id": cid, "status": y, "gt": gt_lab, "condition": cond})
                if y == "MISS" and committed_designed_miss(kind, sc.get("committed"), cluster.get("competitors") or []):
                    n_miss_designed += 1
                    miss_designed_ids.append(cid)
        by_cluster[cid][lane] = row

    flash_m = lane_counts(legs, "flash")
    gpt_m = lane_counts(legs, "gpt")
    strata = lane_condition_counts(legs, "flash")
    plus = strata["plus"]
    n_plus_elig = len(plus_elig)
    plus_hits = sum(1 for r in plus_elig if r["status"] == "HIT")
    plus_rate = (plus_hits / n_plus_elig) if n_plus_elig else None

    g0_ok = (
        sha256_file(INSTR_V2) == EXPECTED_INSTR_V2
        and sha256_file(WRAPPER) == EXPECTED_WRAPPER
        and sha256_file(INSTR_V1) == EXPECTED_INSTR_V1
    )
    h7_ok, h7_err = h7_instrument_ok(INSTR_V2.read_text())
    g0_gate = "PASS" if (g0_ok and h7_ok) else "FAIL"

    designed_ok = designed["n_hit"] == 0
    g1_gate = "PASS" if (not g1_false and designed_ok and not g1_transform_hits) else "FAIL"

    if n_plus_elig < PLUS_N_FLOOR:
        g2_gate = "NOT_EVALUABLE"
    else:
        g2_gate = "PASS" if (plus_rate is not None and plus_rate >= PLUS_HIT_GATE) else "FAIL"

    i_cc = int(flash_m["HIT"] >= HIT_OBS_FLOOR and flash_m["MISS"] >= MISS_OBS_FLOOR)
    g3_gate = "PASS" if i_cc == 1 else "FAIL"
    w1 = g3_gate == "FAIL" and g2_gate == "PASS" and flash_m["MISS"] < MISS_OBS_FLOOR

    g4_gate = "PASS" if not g4_fail else "FAIL"

    plus_form = plus["Form"]
    g5_gate = "PASS" if (flash_m["Form"] >= FORM_GATE and plus_form >= FORM_GATE) else "FAIL"

    cc_interp = bool(i_cc) and flash_m["CC"] is not None
    g6_gate = "PASS"
    if flash_m["CC"] is None and flash_m["HIT"] + flash_m["MISS"] > 0:
        g6_gate = "FAIL"

    fac = factory_f2_f5()
    f4_gate = "PASS" if plus_form >= FORM_GATE else "FAIL"
    g7_gate = "PASS" if all(fac[k] == "PASS" for k in ("F2", "F3", "F5")) and f4_gate == "PASS" else "FAIL"

    h8_ok, h8_err = h8_ids_ok()
    scored_ids = [r["id"] for r in legs]
    if any(not re.fullmatch(r"E\d{2}", i) for i in scored_ids):
        h8_ok = False
        h8_err = list(h8_err) + ["G8: scored id not in E01–E30"]
    banned_scored = [i for i in scored_ids if i[0] in "BCDQVR" or i.startswith(BANNED_PREFIXES)]
    if banned_scored:
        h8_ok = False
        h8_err = list(h8_err) + [f"G8: scored banned id {banned_scored}"]
    g8_gate = "PASS" if h8_ok else "FAIL"

    gates = {
        "G0": g0_gate,
        "G1": g1_gate,
        "G2": g2_gate,
        "G3": g3_gate,
        "G4": g4_gate,
        "G5": g5_gate,
        "G6": g6_gate,
        "G7": g7_gate,
        "G8": g8_gate,
    }
    protocol = "PASS" if all(v == "PASS" for v in gates.values()) else "FAIL"
    first_fail = next((k for k, v in gates.items() if v != "PASS"), None)

    cluster_rows = []
    for cid in IDS:
        cluster = json.loads((SLATE / f"{cid}.json").read_text())
        flash = by_cluster[cid].get("flash") or {}
        gpt = by_cluster[cid].get("gpt") or {}
        cluster_rows.append(
            {
                "id": cid,
                "family": cluster["family"],
                "family_id": cluster.get("family_id"),
                "kind": cluster["kind"],
                "condition": cluster["condition"],
                "flash_execution": flash.get("execution_status") or flash.get("terminated"),
                "gpt_execution": gpt.get("execution_status") or gpt.get("terminated"),
                "flash": (flash.get("score") or {}).get("status"),
                "flash_cause": (flash.get("score") or {}).get("cause"),
                "flash_committed": (flash.get("score") or {}).get("committed"),
                "gpt": (gpt.get("score") or {}).get("status"),
                "gpt_cause": (gpt.get("score") or {}).get("cause"),
                "flash_gt": (flash.get("gt") or {}).get("gt"),
                "gpt_gt": (gpt.get("gt") or {}).get("gt"),
            }
        )

    dh_flash = None
    if flash_m["CC"] is not None and i_cc == 1:
        dh_flash = {
            "DH": flash_m["DH"],
            "Form": flash_m["Form"],
            "CC": flash_m["CC"],
            "I_CC": i_cc,
            "display": f"DH={flash_m['DH']:.4f} (Form={flash_m['Form']:.4f}, CC={flash_m['CC']:.4f}, I_CC=1)",
        }

    return {
        "n_legs": len(legs),
        "N_E": N_E,
        "note_unit": (
            "N=30 Flash clusters E01–E30. Conditions are construction factors, not N. "
            "Phase-3 pilot τ not pooled. Form is interface compliance, not coverage. "
            "CC interpretable iff I_CC=1. n_MISS_designed is descriptive only."
        ),
        "flash": flash_m,
        "gpt": gpt_m,
        "strata_flash": strata,
        "primary_public": {
            "Form": flash_m["Form"],
            "CC": flash_m["CC"],
            "Abs": flash_m["Abs"],
            "I_CC": i_cc,
            "CC_interpretable": cc_interp,
        },
        "DH_with_form": dh_flash,
        "n_MISS_designed": n_miss_designed,
        "n_MISS_designed_ids": miss_designed_ids,
        "n_MISS_designed_note": "descriptive only; never a gate",
        "cluster_table": cluster_rows,
        "G0": {
            "gate": g0_gate,
            "instrument_v2_ok": sha256_file(INSTR_V2) == EXPECTED_INSTR_V2,
            "wrapper_ok": sha256_file(WRAPPER) == EXPECTED_WRAPPER,
            "anti_recovery": "PASS" if h7_ok else "FAIL",
            "errors": h7_err,
        },
        "G1": {
            "gate": g1_gate,
            "false_hit": g1_false,
            "n_false_hit": len(g1_false),
            "designed_c3_c4_hit": designed["hits"],
            "transform_hits": g1_transform_hits,
        },
        "G2": {
            "gate": g2_gate,
            "n_eligible": n_plus_elig,
            "floor": PLUS_N_FLOOR,
            "n_hit": plus_hits,
            "hit_rate": plus_rate,
            "eligible": plus_elig,
            "rule": "plus AND A2=SUCCESS AND Y!=ABSTAIN; HIT>=0.90; n>=10",
        },
        "G3": {
            "gate": g3_gate,
            "I_CC": i_cc,
            "n_HIT": flash_m["HIT"],
            "n_MISS": flash_m["MISS"],
            "HIT_floor": HIT_OBS_FLOOR,
            "MISS_floor": MISS_OBS_FLOOR,
            "W1": w1,
            "W1_label": "challenge weak / correspondence remains unobservable" if w1 else None,
            "rule": "I_CC=1 iff n_HIT>=8 and n_MISS>=8; not a minus MISS quota",
        },
        "G4": {
            "gate": g4_gate,
            "n_changed": len(g4_fail),
            "failures": g4_fail,
            "claim_span_named": claim_span_named,
        },
        "G5": {
            "gate": g5_gate,
            "Form": flash_m["Form"],
            "plus_Form": plus_form,
            "threshold": FORM_GATE,
            "named": "interface_compliance_not_coverage",
        },
        "G6": {
            "gate": g6_gate,
            "published": "M=(Form, CC, Abs, I_CC); cells; strata; CC interpretable iff I_CC; ABSTAIN shown",
            "ABSTAIN_hidden": False,
            "form_called_coverage": False,
            "CC_interpretable": cc_interp,
        },
        "G7": {
            "gate": g7_gate,
            "F2": fac["F2"],
            "F2_errors": fac["F2_errors"],
            "F3": fac["F3"],
            "F4": f4_gate,
            "F5": fac["F5"],
            "F5_errors": fac["F5_errors"],
            "no_minus_miss_quota": True,
        },
        "G8": {"gate": g8_gate, "errors": h8_err},
        "P4D_protocol": protocol,
        "first_failing_gate": first_fail,
        "gates": gates,
    }


def write_report(info: dict, legs: list[dict], analysis: dict, spend: float, stopped: str | None) -> None:
    payload = {
        "phase": 4,
        "workstream": "P4-D",
        "models": {"flash": FLASH, "gpt": GPT},
        "N_E": N_E,
        "n_slots": N_SLOTS,
        "n_completed": len(legs),
        "api_spend_usd_phase4": round(spend, 6),
        "api_spend_usd_phase3_not_pooled": PHASE3_SPEND,
        "api_spend_usd_cumulative": round(spend + PHASE3_SPEND, 6),
        "cap_usd": CAP_USD,
        "stopped": stopped,
        "instrument_v1_sha256": info["instrument_v1_sha256"],
        "instrument_v2_sha256": info["instrument_v2_sha256"],
        "wrapper_sha256": info["wrapper_sha256"],
        "instrument_v1_modified": False,
        "instrument_v2_modified": False,
        "wrapper_modified": False,
        "corpus_modified": False,
        "gold_modified": False,
        "p4b_modified": False,
        "p4c_modified": False,
        "p4c2_modified": False,
        "pilot_pooled": False,
        "claude_run": False,
        "form_is_not_coverage": True,
        "no_miss_quota": True,
        "no_cc_threshold": True,
        **analysis,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "p4d_phase4_results.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    flash = analysis["flash"]
    cc_s = "undefined" if flash["CC"] is None else f"{flash['CC']:.4f}"
    if not analysis["primary_public"]["CC_interpretable"] and flash["CC"] is not None:
        cc_s = f"{flash['CC']:.4f} (descriptive, not interpretable; I_CC=0)"
    dh = analysis["DH_with_form"]
    dh_s = dh["display"] if dh else "not reported (requires I_CC=1)"
    i_cc = analysis["primary_public"]["I_CC"]
    strata = analysis["strata_flash"]
    lines = [
        "# P4-D Phase 4 confirmatory validation",
        "",
        f"N = 30 Flash clusters E01–E30; confirmatory episodes = {len(legs)} / 60",
        f"models = Flash `{FLASH}` (primary) + GPT `{GPT}` (paired, not gated)",
        f"api_spend_usd_phase4 = {payload['api_spend_usd_phase4']}",
        f"api_spend_usd_cumulative = {payload['api_spend_usd_cumulative']} / {CAP_USD}",
        f"stopped = {stopped}",
        "Phase-3 pilot τ not pooled. Claude not run. P4-B / P4-C v1 / P4-C2 not modified.",
        "Measurement channel = last assistant text, CLAIM line only. Execution status is not HIT/MISS.",
        "ABSTAIN is missing correspondence measurement, not task failure.",
        "Form is interface compliance (parseable unique CLAIM). Never named coverage.",
        "No minus MISS quota. No CC ≥ 0.90 gate. n_MISS_designed is descriptive only.",
        "",
        "## Primary public profile (Flash confirmatory, N = 30)",
        "",
        f"- Form = **{flash['Form']:.4f}**  ({flash['HIT']}+{flash['MISS']})/{N_E}",
        f"- CC = **{cc_s}**",
        f"- Abs = {flash['Abs']:.4f}  ({flash['ABSTAIN']}/{N_E})",
        f"- I_CC = **{i_cc}**",
        f"- DH = {dh_s}",
        "",
        "## Flash episode counts (not N)",
        "",
        f"- HIT = {flash['HIT']}",
        f"- MISS = {flash['MISS']}",
        f"- ABSTAIN = {flash['ABSTAIN']}",
        f"- unscored = {flash['unscored']}",
        f"- n_MISS_designed = {analysis['n_MISS_designed']} (descriptive only)",
        "",
        "## Strata by condition (construction factors, not N)",
        "",
    ]
    for cond in ("plus", "minus", "pm"):
        cell = strata[cond]
        cc_cell = "undefined" if cell["CC"] is None else f"{cell['CC']:.4f}"
        lines.append(
            f"- {cond}: HIT={cell['HIT']} MISS={cell['MISS']} ABSTAIN={cell['ABSTAIN']} "
            f"unscored={cell['unscored']} Form={cell['Form']:.4f} CC={cc_cell}"
        )
    lines += [
        "",
        "## GPT paired (descriptive, not gated)",
        "",
        f"- HIT/MISS/ABSTAIN/unscored = {analysis['gpt']['HIT']}/{analysis['gpt']['MISS']}/{analysis['gpt']['ABSTAIN']}/{analysis['gpt']['unscored']}",
        f"- Form = {analysis['gpt']['Form']:.4f}",
        f"- CC = {analysis['gpt']['CC']}",
        "",
        "## Gates (Flash confirmatory unless noted)",
        "",
        f"- G0 frozen DFC = **{analysis['G0']['gate']}**",
        f"- G1 false HIT = **{analysis['G1']['gate']}** (n_false_hit={analysis['G1']['n_false_hit']}; designed C3/C4 HIT={analysis['G1']['designed_c3_c4_hit']}; transform HIT={analysis['G1']['transform_hits']})",
        f"- G2 plus sensitivity = **{analysis['G2']['gate']}** (eligible={analysis['G2']['n_eligible']}, floor={PLUS_N_FLOOR}, hit_rate={analysis['G2']['hit_rate']})",
        f"- G3 two-sided observability = **{analysis['G3']['gate']}** (I_CC={analysis['G3']['I_CC']}, n_HIT={analysis['G3']['n_HIT']}, n_MISS={analysis['G3']['n_MISS']}, W1={analysis['G3']['W1']})",
        f"- G4 working-span invariance = **{analysis['G4']['gate']}** (n_changed={analysis['G4']['n_changed']}; CLAIM-span named, not gated)",
        f"- G5 Form = **{analysis['G5']['gate']}** (overall={analysis['G5']['Form']:.4f}, plus={analysis['G5']['plus_Form']:.4f}, gate≥{FORM_GATE}; not coverage)",
        f"- G6 honesty = **{analysis['G6']['gate']}**",
        f"- G7 anti-factory = **{analysis['G7']['gate']}** (F2={analysis['G7']['F2']}, F3={analysis['G7']['F3']}, F4={analysis['G7']['F4']}, F5={analysis['G7']['F5']})",
        f"- G8 anti-circularity = **{analysis['G8']['gate']}**",
        f"- P4-D protocol = **{analysis['P4D_protocol']}**",
        f"- first_failing_gate = {analysis['first_failing_gate']}",
        "",
        "## Per cluster (Flash primary / GPT pair)",
        "",
        "| id | family_id | condition | flash_exec | flash_Y | flash_cause | flash_GT | gpt_Y | gpt_cause |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for c in analysis["cluster_table"]:
        lines.append(
            f"| `{c['id']}` | {c.get('family_id')} | {c['condition']} | {c.get('flash_execution')} | {c['flash']} | {c['flash_cause']} | {c.get('flash_gt')} | {c['gpt']} | {c['gpt_cause']} |"
        )
    lines += [
        "",
        "G2 floor is plus ∩ A=SUCCESS ∩ committed on Flash, n≥10. G3 is I_CC on Flash N=30.",
        "NOT_EVALUABLE on a required floor fails P4-D. Corpus/gold/instruments/P4-B/P4-C/P4-C2 were not modified.",
        "Do not retune score_v2, wrapper, distractors, or floors after seeing τ.",
        "If G3 fails with plus competence held, the result is W1 — do not amp distractors.",
    ]
    (OUT / "p4d_phase4_results.md").write_text("\n".join(lines) + "\n")
    complete = len(legs) == N_SLOTS and not (stopped and str(stopped).startswith("G1"))
    status = analysis["P4D_protocol"] if len(legs) == N_SLOTS else "INCOMPLETE"
    (OUT / "p4d_phase4_status.json").write_text(
        json.dumps(
            {
                "phase": 4,
                "workstream": "P4-D",
                "status": status,
                "n_completed": len(legs),
                "api_spend_usd": payload["api_spend_usd_phase4"],
                "G0": analysis["G0"]["gate"],
                "G1": analysis["G1"]["gate"],
                "G2": analysis["G2"]["gate"],
                "G3": analysis["G3"]["gate"],
                "G4": analysis["G4"]["gate"],
                "G5": analysis["G5"]["gate"],
                "G6": analysis["G6"]["gate"],
                "G7": analysis["G7"]["gate"],
                "G8": analysis["G8"]["gate"],
                "first_failing_gate": analysis["first_failing_gate"],
                "Form": flash["Form"],
                "CC": flash["CC"],
                "Abs": flash["Abs"],
                "I_CC": i_cc,
                "W1": analysis["G3"]["W1"],
                "form_is_not_coverage": True,
                "no_miss_quota": True,
                "next": "STOP" if status != "PASS" else "PHASE_5_BLOCKED",
                "next_status": "BLOCKED",
                "instrument_v1_modified": False,
                "instrument_v2_modified": False,
                "corpus_modified": False,
                "p4b_modified": False,
                "p4c_modified": False,
                "p4c2_modified": False,
                "pilot_pooled": False,
                "complete": complete,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    print("\n".join(lines))
    print(f"\nP4D_PHASE4_DONE status={status} protocol={analysis['P4D_protocol']} first_fail={analysis['first_failing_gate']}")


def main() -> int:
    score_only = "--score-only" in sys.argv
    info = preflight()
    if "--check" in sys.argv:
        key, key_name = resolve_key()
        print(
            json.dumps(
                {"preflight": "OK", **info, "key_present": bool(key), "key_source_name": key_name or None},
                indent=2,
            )
        )
        return 0

    RUN.mkdir(parents=True, exist_ok=True)
    done = load_progress()
    spend = 0.0
    if done:
        spend = max(float(v.get("spend_usd_end") or 0) for v in done.values())

    if not score_only:
        key, key_name = resolve_key()
        if not key:
            print("FAIL: OPENROUTER_API_KEY_LARGE unset", file=sys.stderr)
            return 2
        (RUN / "key_source.txt").write_text(key_name + "\n")
        stopped = None
        planned = slots()
        for i, (cid, lane, model) in enumerate(planned, start=1):
            sk = f"{cid}:{lane}"
            if sk in done:
                continue
            if spend >= CAP_USD:
                stopped = "spend_cap"
                break
            remain_slots = N_SLOTS - len(done)
            if remain_slots > 0 and done:
                avg = spend / max(len(done), 1)
                if spend + avg * remain_slots > CAP_USD:
                    stopped = "projected_over_cap"
                    break
            cluster = json.loads((SLATE / f"{cid}.json").read_text())
            print(f"LEG {i}/{N_SLOTS} {cid} {lane} {model} spend={spend:.6f}", flush=True)
            leg = run_leg(key, model, cluster["instruction"], WORLDS / cid, spend)
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
                gt = A.adjudicate(
                    kind=cluster["kind"],
                    gold=cluster["gold"],
                    locator=cluster["locator"],
                    world_files=load_world_files(cid),
                    tool_trace=leg.get("tool_trace") or [],
                )
            except Exception as exc:
                gt = {"gt": "INDETERMINATE", "cause": f"adjudicator_exception:{exc}"[:200]}
            row = {
                "id": cid,
                "lane": lane,
                "model": model,
                "tau": leg.get("tau") or "",
                "n_steps": leg.get("n_steps"),
                "execution_status": leg.get("terminated"),
                "terminated": leg.get("terminated"),
                "harness_exception": leg.get("harness_exception"),
                "spend_usd_end": spend,
                "scorable": leg.get("scorable"),
                "p4_measurement": leg.get("score"),
                "score": leg.get("score"),
                "gt": gt,
                "tool_trace": leg.get("tool_trace") or [],
                "phase3_pilot": False,
                "channel": "last_assistant_text_claim_line",
                "trajectory_used_for_p4": False,
            }
            (RUN / f"{cid}_{lane}_tau.txt").write_text(row["tau"])
            slim = {k: v for k, v in row.items() if k not in {"tau"}}
            (RUN / f"{cid}_{lane}_leg.json").write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n")
            append_leg(row)
            done[sk] = row
            if i % 5 == 0:
                print(f"SPEND_CHECKPOINT legs={len(done)} usd={spend:.6f}", flush=True)
            if lane == "flash" and row.get("scorable") and row.get("score") and row["tau"].strip():
                if not gold_in_clean(row["tau"], cluster["gold"]) and row["score"].get("status") == "HIT":
                    stopped = f"G1_false_hit_prefix:{cid}:{lane}"
                    break
                tables = load_tables(cid)
                vals = same_kind_values(cluster["kind"], cluster["gold"], tables)
                d1 = distractor_line(vals[0] if vals else "0")
                d2 = distractor_line(vals[1] if len(vals) > 1 else "1")
                alt_val = vals[0] if vals else "0"
                inv = h4_on_tau(row["tau"], cluster["kind"], cluster["gold"], d1, d2, alt_val)
                if not inv["pass"]:
                    stopped = f"G4_fail_prefix:{cid}:{lane}"
                    break
                h1t = h1_transforms_on_tau(row["tau"], cluster["kind"], cluster["gold"])
                if h1t["hits"]:
                    stopped = f"G1_transform_hit_prefix:{cid}:{lane}"
                    break
            time.sleep(0.2)
    else:
        stopped = None

    legs = [done[f"{cid}:{lane}"] for cid, lane, _ in slots() if f"{cid}:{lane}" in done]
    if not legs:
        print("no legs recorded", file=sys.stderr)
        return 1
    if len(legs) < N_SLOTS and not stopped:
        stopped = "incomplete"
    analysis = analyze(legs)
    write_report(
        info,
        legs,
        analysis,
        spend if not score_only else max((float(x.get("spend_usd_end") or 0) for x in legs), default=0.0),
        stopped,
    )
    if stopped and str(stopped).startswith("G1"):
        return 1
    if stopped and str(stopped).startswith("G4"):
        return 1
    if len(legs) != N_SLOTS:
        return 1
    return 0 if analysis["P4D_protocol"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
