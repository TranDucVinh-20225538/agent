#!/usr/bin/env python3
"""P4-C2 Phase 4 confirmatory validation. 30 clusters × 2 models = 60 legs.

Does not edit p4_instrument.py, p4_instrument_v2.py, wrapper, gold, worlds,
transforms_d, N_D, P4-B, or P4-C v1. Does not pool Phase-3 pilot τ into N_D.
Does not run Claude. Primary gates use Flash confirmatory legs. GPT is
paired/descriptive. Form is interface compliance, never named coverage.
LARGE OpenRouter lane only.
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
SLATE = CON / "slate" / "d"
DQDIR = CON / "slate" / "dq"
WORLDS = SLATE / "worlds"
OUT = CON / "out"
SEAL = CON / "sealed" / "P4C2_PHASE2_SEAL.json"
TRANS = CON / "transforms_d.py"
ADJ = CON / "adjudicator_d.py"
GEN = CON / "generate_d.py"
PARAMS = CON / "params_d.json"
GOLD_SPEC = OUT / "p4c2_gold_spec.json"
PHASE3 = OUT / "p4c2_phase3_status.json"
RUN = OUT / "p4c2_phase4"
EXPECTED_INSTR_V1 = "c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59"
EXPECTED_INSTR_V2 = "a87ac636a729d99852eb837583b24bce372ff49c196f2be7e39e4f750622fcf3"
EXPECTED_WRAPPER = "2a028f2b95a7bc1ce815ac4b01dcb1fc7c8814ded7a5f3f38489d4ffe70e8e08"
EXPECTED_SEAL_GATE = "PASS"
EXPECTED_CLUSTERS = "3a3bc2ed61faea0f4bf02a4a1594ce0d618569f656ba323654506cbd84499d3e"
EXPECTED_WORLDS = "babd49ad1d5220c243a32cfa551fe411791920ea7f6d62ac2ef4d112d4babe1e"
EXPECTED_GOLD = "4ab761090209dfba04251da6c23fc5b945e1f927576ebab89cd5d556403b201d"
EXPECTED_TRANS = "bb4a216bfba2f8bb5c914941c9b5d8faf4dd776c8ca30b40a8d3a3dfe9abaf9c"
EXPECTED_ADJ = "d8b1b27ff0e0a1dbd261896c778dfeb78aef82de1d7071190c546382ebd3dab1"
EXPECTED_GEN = "bf2f52ee6242c2fa8552f84b197ce12fecaaaf8db9e10f35a4b850187547fb47"
EXPECTED_PARAMS = "e0be495b2b28cb69de03ec51fe5131fd57bd0ad9de2a71f1510a1a43b4e56e97"
IDS = [f"D{i:02d}" for i in range(1, 31)]
DQ_IDS = [f"DQ{i:02d}" for i in range(1, 7)]
BANNED_PREFIXES = ("B", "C", "Q", "CQ", "V", "R")
FLASH = "qwen/qwen3.8-flash"
GPT = "openai/gpt-5.5"
MODELS = (("flash", FLASH), ("gpt", GPT))
MAX_STEPS = 40
N_D = 30
N_SLOTS = 60
CAP_USD = 400.0
PHASE3_SPEND = 0.001577
FLASH_BURN_PER_LEG = PHASE3_SPEND / 3.0
GPT_QUOTE_MULT = 5.0
READ_CAP = 32_000
FALLBACK_IN_PER_M = 0.10
FALLBACK_OUT_PER_M = 0.40
C1_FLOOR = 10
C2_FLOOR = 10
FORM_GATE = 0.80
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
            "HTTP-Referer": "https://local.p4c2-phase4",
            "X-Title": "P4-C2 Phase 4 confirmatory",
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
            "note": "CLAIM-span C6 may change Y; not an H4 failure",
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
    for cid in DQ_IDS:
        cluster = json.loads((DQDIR / f"{cid}.json").read_text())
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
                errors.append("H7: score_v2 imports v1 score")
        if isinstance(node, ast.FunctionDef) and node.name == "score_v2":
            args = [a.arg for a in node.args.args] + [a.arg for a in node.args.kwonlyargs]
            if "anchors" in args or "task_id" in args:
                errors.append("H7: score_v2 takes anchors or task_id")
    lowered = src.casefold()
    for tok in ("screenshot", "tool_trace", "world_files"):
        if tok in lowered:
            errors.append(f"H7: instrument mentions {tok}")
    return not errors, errors


def h8_ids_ok() -> tuple[bool, list[str]]:
    errors: list[str] = []
    for cid in IDS:
        if not re.fullmatch(r"D\d{2}", cid):
            errors.append(f"H8: confirmatory id {cid} is not D*")
        if cid.startswith(BANNED_PREFIXES) or cid[0] in "BCQVR":
            errors.append(f"H8: confirmatory id {cid} collides with banned prefix")
    p4c_tau = OUT / "p4c_phase4"
    if p4c_tau.is_dir():
        for p in p4c_tau.glob("*_tau.txt"):
            if p.name.startswith("D"):
                errors.append(f"H8: unexpected D τ in P4-C run dir {p.name}")
    return not errors, errors


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
    if gen_sha != EXPECTED_GEN or gen_sha != seal["generate_d_sha256"]:
        raise SystemExit(f"generate_d hash mismatch: {gen_sha}")
    if params_sha != EXPECTED_PARAMS or params_sha != seal["params_d_sha256"]:
        raise SystemExit(f"params_d hash mismatch: {params_sha}")
    h7_ok, h7_err = h7_instrument_ok(INSTR_V2.read_text())
    if not h7_ok:
        raise SystemExit("H7 failed: " + "; ".join(h7_err))
    h8_ok, h8_err = h8_ids_ok()
    if not h8_ok:
        raise SystemExit("H8 failed: " + "; ".join(h8_err))
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
        "generate_d_sha256": gen_sha,
        "params_d_sha256": params_sha,
        "seal_gate": seal.get("gate"),
        "phase3_spend_usd": PHASE3_SPEND,
        "projected_phase4_usd": round(projected, 6),
        "remaining_cap_usd": round(remaining, 6),
        "flash_model": FLASH,
        "gpt_model": GPT,
        "n_slots": N_SLOTS,
        "N_D": N_D,
        "pilot_pooled": False,
        "form_is_not_coverage": True,
        "H7": "PASS",
        "H8": "PASS",
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
    form = (n_hit + n_miss) / N_D
    cc = (n_hit / (n_hit + n_miss)) if (n_hit + n_miss) else None
    abs_ = n_abstain / N_D
    dh = n_hit / N_D
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
    h1_false = []
    h1_transform_hits = []
    h4_fail = []
    c1_elig = []
    c2_elig = []
    designed = designed_c3_c4()
    claim_span_named = []

    for row in legs:
        cid = row["id"]
        lane = row["lane"]
        cluster = json.loads((SLATE / f"{cid}.json").read_text())
        kind, gold = cluster["kind"], cluster["gold"]
        slot = cluster["slot"]
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
                h1_false.append({"id": cid, "lane": lane, "committed": sc.get("committed")})
            h1t = h1_transforms_on_tau(tau, kind, gold)
            row["h1_transforms"] = {"hits": h1t["hits"]}
            if lane == "flash" and h1t["hits"]:
                h1_transform_hits.append({"id": cid, "hits": h1t["hits"]})
            inv = h4_on_tau(tau, kind, gold, d1, d2, alt_val)
            row["h4"] = {
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
                    h4_fail.append({"id": cid, "changed": inv["changed"]})
            gt_lab = gt.get("gt")
            y = sc.get("status")
            committed = y in {"HIT", "MISS"}
            if lane == "flash":
                if slot == "C1-intended" and gt_lab == "SUCCESS" and committed:
                    c1_elig.append({"id": cid, "status": y, "gt": gt_lab, "slot": slot})
                if slot == "C2-intended" and committed:
                    c2_elig.append({"id": cid, "status": y, "gt": gt_lab, "slot": slot})
        by_cluster[cid][lane] = row

    flash_m = lane_counts(legs, "flash")
    gpt_m = lane_counts(legs, "gpt")

    n_c1 = len(c1_elig)
    n_c2 = len(c2_elig)
    c1_hits = sum(1 for r in c1_elig if r["status"] == "HIT")
    c2_miss = sum(1 for r in c2_elig if r["status"] == "MISS")
    c1_rate = (c1_hits / n_c1) if n_c1 else None
    c2_rate = (c2_miss / n_c2) if n_c2 else None

    h1_designed_ok = designed["n_hit"] == 0
    h1_gate = "PASS" if (not h1_false and h1_designed_ok and not h1_transform_hits) else "FAIL"
    if n_c1 < C1_FLOOR:
        h2_gate = "NOT_EVALUABLE"
    else:
        h2_gate = "PASS" if (c1_rate is not None and c1_rate >= 0.90) else "FAIL"
    if n_c2 < C2_FLOOR:
        h3_gate = "NOT_EVALUABLE"
    else:
        h3_gate = "PASS" if (c2_rate is not None and c2_rate >= 0.90) else "FAIL"
    h4_gate = "PASS" if not h4_fail else "FAIL"
    h5_gate = "PASS" if flash_m["Form"] >= FORM_GATE else "FAIL"
    h6_gate = "PASS"
    if flash_m["CC"] is None and flash_m["HIT"] + flash_m["MISS"] > 0:
        h6_gate = "FAIL"
    h7_ok, h7_err = h7_instrument_ok(INSTR_V2.read_text())
    h7_gate = "PASS" if h7_ok else "FAIL"
    h8_ok, h8_err = h8_ids_ok()
    scored_ids = [r["id"] for r in legs]
    if any(not re.fullmatch(r"D\d{2}", i) for i in scored_ids):
        h8_ok = False
        h8_err = list(h8_err) + ["H8: scored id not in D01–D30"]
    h8_gate = "PASS" if h8_ok else "FAIL"

    metric = "FAIL"
    gates = {
        "H1": h1_gate,
        "H2": h2_gate,
        "H3": h3_gate,
        "H4": h4_gate,
        "H5": h5_gate,
        "H6": h6_gate,
        "H7": h7_gate,
        "H8": h8_gate,
    }
    if all(v == "PASS" for v in gates.values()):
        metric = "PASS"

    cluster_rows = []
    for cid in IDS:
        cluster = json.loads((SLATE / f"{cid}.json").read_text())
        flash = by_cluster[cid].get("flash") or {}
        gpt = by_cluster[cid].get("gpt") or {}
        cluster_rows.append(
            {
                "id": cid,
                "family": cluster["family"],
                "kind": cluster["kind"],
                "slot": cluster["slot"],
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
    if flash_m["CC"] is not None:
        dh_flash = {
            "DH": flash_m["DH"],
            "Form": flash_m["Form"],
            "CC": flash_m["CC"],
            "display": f"DH={flash_m['DH']:.4f} (Form={flash_m['Form']:.4f}, CC={flash_m['CC']:.4f})",
        }

    return {
        "n_legs": len(legs),
        "N_D": N_D,
        "note_unit": (
            "N_D=30 clusters. 60 episodes are paired observations, not 60 clusters. "
            "Phase-3 pilot τ not pooled. Form is interface compliance, not coverage."
        ),
        "flash": flash_m,
        "gpt": gpt_m,
        "primary_public": {"Form": flash_m["Form"], "CC": flash_m["CC"]},
        "DH_with_form": dh_flash,
        "cluster_table": cluster_rows,
        "H1": {
            "gate": h1_gate,
            "false_hit": h1_false,
            "n_false_hit": len(h1_false),
            "designed_c3_c4_hit": designed["hits"],
            "transform_hits": h1_transform_hits,
        },
        "H2": {
            "gate": h2_gate,
            "n_eligible": n_c1,
            "floor": C1_FLOOR,
            "n_hit": c1_hits,
            "hit_rate": c1_rate,
            "eligible": c1_elig,
            "rule": "C1-intended AND A2=SUCCESS AND Y!=ABSTAIN",
        },
        "H3": {
            "gate": h3_gate,
            "n_eligible": n_c2,
            "floor": C2_FLOOR,
            "n_miss": c2_miss,
            "miss_rate": c2_rate,
            "eligible": c2_elig,
            "rule": "C2-intended AND committed value (Y in HIT/MISS)",
        },
        "H4": {
            "gate": h4_gate,
            "n_changed": len(h4_fail),
            "failures": h4_fail,
            "claim_span_named": claim_span_named,
        },
        "H5": {
            "gate": h5_gate,
            "Form": flash_m["Form"],
            "threshold": FORM_GATE,
            "named": "interface_compliance_not_coverage",
        },
        "H6": {
            "gate": h6_gate,
            "published": "(Form, CC) and optional DH (Form, CC); HIT/MISS/ABSTAIN shown",
            "ABSTAIN_hidden": False,
            "form_called_coverage": False,
        },
        "H7": {"gate": h7_gate, "errors": h7_err},
        "H8": {"gate": h8_gate, "errors": h8_err},
        "P4C2_metric": metric,
        "gates": gates,
    }


def write_report(info: dict, legs: list[dict], analysis: dict, spend: float, stopped: str | None) -> None:
    payload = {
        "phase": 4,
        "workstream": "P4-C2",
        "models": {"flash": FLASH, "gpt": GPT},
        "N_D": N_D,
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
        "pilot_pooled": False,
        "claude_run": False,
        "form_is_not_coverage": True,
        **analysis,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "p4c2_phase4_results.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    flash = analysis["flash"]
    cc_s = "undefined" if flash["CC"] is None else f"{flash['CC']:.4f}"
    dh = analysis["DH_with_form"]
    dh_s = dh["display"] if dh else "undefined (CC undefined)"
    lines = [
        "# P4-C2 Phase 4 confirmatory validation",
        "",
        f"N_D = 30 clusters; confirmatory episodes = {len(legs)} / 60",
        f"models = Flash `{FLASH}` (primary) + GPT `{GPT}` (paired, not gated)",
        f"api_spend_usd_phase4 = {payload['api_spend_usd_phase4']}",
        f"api_spend_usd_cumulative = {payload['api_spend_usd_cumulative']} / {CAP_USD}",
        f"stopped = {stopped}",
        "Phase-3 pilot τ not pooled. Claude not run. P4-B and P4-C v1 not pooled.",
        "Measurement channel = last assistant text, CLAIM line only. Execution status is not HIT/MISS.",
        "ABSTAIN is missing correspondence measurement, not task failure.",
        "Form is interface compliance (parseable unique CLAIM). Never named coverage.",
        "",
        "## Primary public report (Flash confirmatory, N_D = 30)",
        "",
        f"- Form = **{flash['Form']:.4f}**  ({flash['HIT']}+{flash['MISS']})/{N_D}",
        f"- CC = **{cc_s}**",
        f"- Abs = {flash['Abs']:.4f}  ({flash['ABSTAIN']}/{N_D})",
        f"- DH (Form, CC) = {dh_s}",
        "",
        "## Flash episode counts (not N)",
        "",
        f"- HIT = {flash['HIT']}",
        f"- MISS = {flash['MISS']}",
        f"- ABSTAIN = {flash['ABSTAIN']}",
        f"- unscored = {flash['unscored']}",
        "",
        "## GPT paired (descriptive, not gated)",
        "",
        f"- HIT/MISS/ABSTAIN/unscored = {analysis['gpt']['HIT']}/{analysis['gpt']['MISS']}/{analysis['gpt']['ABSTAIN']}/{analysis['gpt']['unscored']}",
        f"- Form = {analysis['gpt']['Form']:.4f}",
        f"- CC = {analysis['gpt']['CC']}",
        "",
        "## Gates (Flash confirmatory unless noted)",
        "",
        f"- H1 false HIT = **{analysis['H1']['gate']}** (n_false_hit={analysis['H1']['n_false_hit']}; designed C3/C4 HIT={analysis['H1']['designed_c3_c4_hit']}; transform HIT={analysis['H1']['transform_hits']})",
        f"- H2 C1 sensitivity = **{analysis['H2']['gate']}** (eligible={analysis['H2']['n_eligible']}, floor={C1_FLOOR}, hit_rate={analysis['H2']['hit_rate']})",
        f"- H3 C2 discrimination = **{analysis['H3']['gate']}** (eligible={analysis['H3']['n_eligible']}, floor={C2_FLOOR}, miss_rate={analysis['H3']['miss_rate']})",
        f"- H4 invariance = **{analysis['H4']['gate']}** (n_changed={analysis['H4']['n_changed']}; CLAIM-span named, not gated)",
        f"- H5 interface compliance = **{analysis['H5']['gate']}** (Form={analysis['H5']['Form']:.4f}, gate≥{FORM_GATE}; not coverage)",
        f"- H6 scalar honesty = **{analysis['H6']['gate']}**",
        f"- H7 anti-recovery = **{analysis['H7']['gate']}**",
        f"- H8 anti-circularity = **{analysis['H8']['gate']}**",
        f"- P4-C2-Metric v2 = **{analysis['P4C2_metric']}**",
        "",
        "## Per cluster (Flash primary / GPT pair)",
        "",
        "| id | family | slot | flash_exec | flash_Y | flash_cause | flash_GT | gpt_Y | gpt_cause |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for c in analysis["cluster_table"]:
        lines.append(
            f"| `{c['id']}` | {c['family']} | {c['slot']} | {c.get('flash_execution')} | {c['flash']} | {c['flash_cause']} | {c.get('flash_gt')} | {c['gpt']} | {c['gpt_cause']} |"
        )
    lines += [
        "",
        "H2/H3 floors are on distinct Flash-eligible clusters, not 60 episodes.",
        "NOT EVALUABLE on a required floor fails P4-C2. Corpus/gold/instruments were not modified.",
        "Do not retune score_v2, wrapper, or H5 after seeing Form.",
    ]
    (OUT / "p4c2_phase4_results.md").write_text("\n".join(lines) + "\n")
    complete = len(legs) == N_SLOTS and not (stopped and str(stopped).startswith("H1"))
    status = analysis["P4C2_metric"] if len(legs) == N_SLOTS else "INCOMPLETE"
    (OUT / "p4c2_phase4_status.json").write_text(
        json.dumps(
            {
                "phase": 4,
                "workstream": "P4-C2",
                "status": status,
                "n_completed": len(legs),
                "api_spend_usd": payload["api_spend_usd_phase4"],
                "H1": analysis["H1"]["gate"],
                "H2": analysis["H2"]["gate"],
                "H3": analysis["H3"]["gate"],
                "H4": analysis["H4"]["gate"],
                "H5": analysis["H5"]["gate"],
                "H6": analysis["H6"]["gate"],
                "H7": analysis["H7"]["gate"],
                "H8": analysis["H8"]["gate"],
                "Form": flash["Form"],
                "CC": flash["CC"],
                "form_is_not_coverage": True,
                "next": "STOP",
                "next_status": "BLOCKED",
                "instrument_v1_modified": False,
                "instrument_v2_modified": False,
                "corpus_modified": False,
                "p4b_modified": False,
                "p4c_modified": False,
                "pilot_pooled": False,
                "complete": complete,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    print("\n".join(lines))
    print(f"\nP4C2_PHASE4_DONE status={status} metric={analysis['P4C2_metric']}")


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
                    stopped = f"H1_false_hit_prefix:{cid}:{lane}"
                    break
                tables = load_tables(cid)
                vals = same_kind_values(cluster["kind"], cluster["gold"], tables)
                d1 = distractor_line(vals[0] if vals else "0")
                d2 = distractor_line(vals[1] if len(vals) > 1 else "1")
                alt_val = vals[0] if vals else "0"
                inv = h4_on_tau(row["tau"], cluster["kind"], cluster["gold"], d1, d2, alt_val)
                if not inv["pass"]:
                    stopped = f"H4_fail_prefix:{cid}:{lane}"
                    break
                h1t = h1_transforms_on_tau(row["tau"], cluster["kind"], cluster["gold"])
                if h1t["hits"]:
                    stopped = f"H1_transform_hit_prefix:{cid}:{lane}"
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
    if stopped and str(stopped).startswith("H1"):
        return 1
    if stopped and str(stopped).startswith("H4"):
        return 1
    if len(legs) != N_SLOTS:
        return 1
    return 0 if analysis["P4C2_metric"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
