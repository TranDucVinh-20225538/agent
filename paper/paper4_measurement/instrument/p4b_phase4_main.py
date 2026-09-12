#!/usr/bin/env python3
"""P4-B Phase 4 confirmatory validation. 20 clusters × 2 models = 40 legs.

Does not edit p4_instrument.py, gold, anchors, worlds, transforms, or N_B.
Does not pool Phase-3 pilot τ into N_B. Does not run Claude.
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
SLATE = CON / "slate" / "b"
WORLDS = SLATE / "worlds"
OUT = CON / "out"
SEAL = CON / "sealed" / "P4B_PHASE2_SEAL.json"
TRANS = CON / "transforms_b.py"
GOLD_SPEC = OUT / "p4b_gold_spec.json"
RUN = OUT / "p4b_phase4"
EXPECTED_INSTR = "c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59"
EXPECTED_SEAL_GATE = "PASS"
EXPECTED_CLUSTERS = "8c061c093185787cf98919ac14590064025e7f41283df11a9b0cb0285df0bed5"
EXPECTED_WORLDS = "9db6cbb94b933d0c7098dfcc0e257042e58a2c021870561966b5fe91e0e626b3"
EXPECTED_GOLD = "0e334b2c9a8ecae0998abd91476fc7ece67f2c732790ab4c987c25a745d1004f"
EXPECTED_TRANS = "7a5ee93261d067d140681a8c539809d52725880ecd7f97c25e0749ef5af15ae6"
IDS = [f"B{i:02d}" for i in range(1, 21)]
FLASH = "qwen/qwen3.8-flash"
GPT = "openai/gpt-5.5"
MODELS = (("flash", FLASH), ("gpt", GPT))
MAX_STEPS = 40
CAP_USD = 400.0
PHASE3_SPEND = 0.001305
FLASH_BURN_PER_LEG = PHASE3_SPEND / 3.0
GPT_QUOTE_MULT = 5.0
READ_CAP = 32_000
FALLBACK_IN_PER_M = 0.10
FALLBACK_OUT_PER_M = 0.40

sys.path.insert(0, str(INSTR.parent))
sys.path.insert(0, str(CON))
from p4_instrument import (  # noqa: E402
    extract_candidates,
    locate_lines,
    score,
    v1_clean,
    v3_match,
)
import generate_b as g  # noqa: E402
import transforms_b as T  # noqa: E402


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
        if name not in {
            "OPENROUTER_API_KEY_LARGE",
            "OPENROUTER_API_KEY_SMALL",
            "OPENROUTER_API_KEY",
        }:
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
    for name in (
        "OPENROUTER_API_KEY_LARGE",
        "OPENROUTER_API_KEY_SMALL",
        "OPENROUTER_API_KEY",
    ):
        val = os.environ.get(name) or ""
        if val.strip():
            if val.strip().startswith("sk-proj-"):
                raise SystemExit("FAIL: sk-proj key bound; need OpenRouter")
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
                "properties": {"path": {"type": "string"}},
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
                "properties": {"path": {"type": "string"}},
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
            "HTTP-Referer": "https://local.p4b-phase4",
            "X-Title": "P4-B Phase 4 confirmatory",
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


def run_leg(key: str, model: str, instruction: str, world: Path, spend: float) -> dict:
    # Ordinary CUA-style tool loop. Do not mention P4, anchors, gold, or scoring.
    messages = [
        {
            "role": "system",
            "content": (
                "You are a desktop agent. Workspace files are available through "
                "the list_dir and read_file tools. Complete the user's task. "
                "The workspace root is '.'"
            ),
        },
        {"role": "user", "content": instruction},
    ]
    steps = []
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
                if kind in {"money_usd", "integer"}:
                    try:
                        if not v3_match(kind, g.format_gold(kind, s) if kind != "integer" else int(canon), gold):
                            if canon not in found:
                                found.append(canon)
                    except Exception:
                        if canon not in found:
                            found.append(canon)
                else:
                    if canon.casefold() != gold.casefold() and canon not in found:
                        found.append(canon)
    return found


def distractor_line(val: str, anchors: list[str]) -> str:
    line = f"alt-value {val}"
    blob = line.casefold()
    if any(a.casefold() in blob for a in anchors):
        line = f"other-record {val}"
    return line


def gold_in_clean(tau: str, gold: str) -> bool:
    cleaned, cause = v1_clean(tau)
    if cleaned is None:
        return False
    return gold in cleaned


def natural_c1(tau: str, kind: str, gold: str, anchors: list[str]) -> bool:
    cleaned, cause = v1_clean(tau)
    if cleaned is None or cause:
        return False
    located = locate_lines(cleaned, anchors)
    if not located:
        return False
    if not any(gold in line for line in located):
        return False
    found = extract_candidates(kind, located, anchors)
    if not found:
        return False
    others = []
    for val in found:
        try:
            if not v3_match(kind, val, gold):
                others.append(val)
        except Exception:
            others.append(val)
    return not others


def natural_c2(tau: str, kind: str, gold: str, anchors: list[str]) -> bool:
    cleaned, cause = v1_clean(tau)
    if cleaned is None or cause:
        return False
    if gold in cleaned:
        return False
    located = locate_lines(cleaned, anchors)
    if not located:
        return False
    found = extract_candidates(kind, located, anchors)
    if not found:
        return False
    classes = []
    for val in found:
        try:
            if v3_match(kind, val, gold):
                return False
        except Exception:
            pass
        key = str(val)
        if key not in classes:
            classes.append(key)
    return len(classes) == 1


def e2_on_tau(tau: str, kind: str, gold: str, anchors: list[str], d1: str, d2: str) -> dict:
    base = score(tau, kind=kind, gold=gold, anchors=anchors)
    c5 = score(T.c5_irr(tau, d1), kind=kind, gold=gold, anchors=anchors)
    t6a, t6b = T.c6_pair(tau, d1, d2)
    c6a = score(t6a, kind=kind, gold=gold, anchors=anchors)
    c6b = score(t6b, kind=kind, gold=gold, anchors=anchors)
    changed = []
    for name, sc in (("c5", c5), ("c6a", c6a), ("c6b", c6b)):
        if sc.get("status") != base.get("status") or sc.get("committed") != base.get("committed"):
            changed.append(name)
    return {
        "base": base,
        "c5": c5,
        "c6a": c6a,
        "c6b": c6b,
        "changed": changed,
        "pass": not changed,
    }


def slots() -> list[tuple[str, str, str]]:
    out = []
    for cid in IDS:
        for lane, model in MODELS:
            out.append((cid, lane, model))
    return out


def preflight() -> dict:
    instr_sha = sha256_file(INSTR)
    if instr_sha != EXPECTED_INSTR:
        raise SystemExit(f"instrument drifted: {instr_sha}")
    seal = json.loads(SEAL.read_text())
    if seal.get("gate") != EXPECTED_SEAL_GATE:
        raise SystemExit("Phase 2 seal is not PASS")
    cluster_paths = [SLATE / f"{cid}.json" for cid in IDS]
    world_paths = sorted(p for p in WORLDS.rglob("*") if p.is_file())
    clusters_sha = combined_hash(cluster_paths)
    worlds_sha = combined_hash(world_paths)
    gold_sha = sha256_file(GOLD_SPEC)
    trans_sha = sha256_file(TRANS)
    if clusters_sha != EXPECTED_CLUSTERS or clusters_sha != seal["clusters_sha256"]:
        raise SystemExit(f"clusters hash mismatch: {clusters_sha}")
    if worlds_sha != EXPECTED_WORLDS or worlds_sha != seal["worlds_sha256"]:
        raise SystemExit(f"worlds hash mismatch: {worlds_sha}")
    if gold_sha != EXPECTED_GOLD or gold_sha != seal["gold_spec_sha256"]:
        raise SystemExit(f"gold spec hash mismatch: {gold_sha}")
    if trans_sha != EXPECTED_TRANS or trans_sha != seal["transforms_b_sha256"]:
        raise SystemExit(f"transforms hash mismatch: {trans_sha}")
    if seal.get("instrument_sha256") != EXPECTED_INSTR:
        raise SystemExit("seal instrument hash mismatch")
    for cid in IDS:
        cluster = json.loads((SLATE / f"{cid}.json").read_text())
        if cluster.get("id") != cid:
            raise SystemExit(f"{cid} id mismatch")
        if "observations" in cluster:
            raise SystemExit(f"{cid} has observations")
        if not (WORLDS / cid).is_dir():
            raise SystemExit(f"missing world {cid}")
    remaining = CAP_USD - PHASE3_SPEND
    projected = 20 * FLASH_BURN_PER_LEG + 20 * FLASH_BURN_PER_LEG * GPT_QUOTE_MULT
    if projected > remaining:
        raise SystemExit(f"preflight projection {projected:.6f} exceeds remaining {remaining:.6f}")
    return {
        "instrument_sha256": instr_sha,
        "clusters_sha256": clusters_sha,
        "worlds_sha256": worlds_sha,
        "gold_spec_sha256": gold_sha,
        "transforms_b_sha256": trans_sha,
        "seal_gate": seal.get("gate"),
        "phase3_spend_usd": PHASE3_SPEND,
        "projected_phase4_usd": round(projected, 6),
        "remaining_cap_usd": round(remaining, 6),
        "flash_model": FLASH,
        "gpt_model": GPT,
        "n_slots": 40,
        "N_B": 20,
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


def analyze(legs: list[dict]) -> dict:
    by_cluster: dict[str, dict] = {cid: {} for cid in IDS}
    n_hit = n_miss = n_abstain = n_unscored = 0
    e1_false = []
    e2_fail = []
    e3_tau = []
    e4_tau = []
    for row in legs:
        cid = row["id"]
        lane = row["lane"]
        cluster = json.loads((SLATE / f"{cid}.json").read_text())
        kind, gold, anchors = cluster["kind"], cluster["gold"], cluster["anchors"]
        tables = load_tables(cid)
        vals = same_kind_values(kind, gold, tables)
        d1 = distractor_line(vals[0] if vals else "0", anchors)
        d2 = distractor_line(vals[1] if len(vals) > 1 else "1", anchors)
        sc = row.get("score")
        tau = row.get("tau") or ""
        if not row.get("scorable") or not isinstance(sc, dict):
            n_unscored += 1
            by_cluster[cid][lane] = row
            continue
        st = sc.get("status")
        if st == "HIT":
            n_hit += 1
        elif st == "MISS":
            n_miss += 1
        elif st == "ABSTAIN":
            n_abstain += 1
        gic = gold_in_clean(tau, gold)
        if not gic and st == "HIT":
            e1_false.append({"id": cid, "lane": lane})
        if tau.strip():
            inv = e2_on_tau(tau, kind, gold, anchors, d1, d2)
            row = dict(row)
            row["e2"] = {"pass": inv["pass"], "changed": inv["changed"]}
            if not inv["pass"]:
                e2_fail.append({"id": cid, "lane": lane, "changed": inv["changed"]})
            if natural_c1(tau, kind, gold, anchors):
                e3_tau.append({"id": cid, "lane": lane, "status": st})
            if natural_c2(tau, kind, gold, anchors):
                e4_tau.append({"id": cid, "lane": lane, "status": st})
        by_cluster[cid][lane] = row

    def cluster_ids(rows: list[dict]) -> list[str]:
        seen = []
        for r in rows:
            if r["id"] not in seen:
                seen.append(r["id"])
        return seen

    e3_clusters = cluster_ids(e3_tau)
    e4_clusters = cluster_ids(e4_tau)
    e3_all_hit = all(r["status"] == "HIT" for r in e3_tau) if e3_tau else False
    e4_all_miss = all(r["status"] == "MISS" for r in e4_tau) if e4_tau else False
    if len(e3_clusters) < 5:
        e3_gate = "NOT_EVALUABLE"
    else:
        e3_gate = "PASS" if e3_all_hit else "FAIL"
    if len(e4_clusters) < 5:
        e4_gate = "NOT_EVALUABLE"
    else:
        e4_gate = "PASS" if e4_all_miss else "FAIL"
    e1_gate = "PASS" if not e1_false else "FAIL"
    e2_clusters = sorted({r["id"] for r in e2_fail})
    e2_gate = "PASS" if not e2_fail else "FAIL"
    p4b = "PASS" if e1_gate == "PASS" and e2_gate == "PASS" and e3_gate == "PASS" else "FAIL"
    if e3_gate == "NOT_EVALUABLE":
        p4b = "NULL_E3_NOT_EVALUABLE" if e1_gate == "PASS" and e2_gate == "PASS" else "FAIL"
    if e4_gate == "FAIL":
        p4b = "FAIL"

    cluster_rows = []
    for cid in IDS:
        flash = by_cluster[cid].get("flash") or {}
        gpt = by_cluster[cid].get("gpt") or {}
        fs = (flash.get("score") or {}).get("status")
        gs = (gpt.get("score") or {}).get("status")
        statuses = [s for s in (fs, gs) if s]
        n_ab = sum(s == "ABSTAIN" for s in statuses)
        n_h = sum(s == "HIT" for s in statuses)
        n_m = sum(s == "MISS" for s in statuses)
        hm = n_h + n_m
        cluster_rows.append(
            {
                "id": cid,
                "flash_execution": flash.get("execution_status") or flash.get("terminated"),
                "gpt_execution": gpt.get("execution_status") or gpt.get("terminated"),
                "flash": fs,
                "flash_cause": (flash.get("score") or {}).get("cause"),
                "gpt": gs,
                "gpt_cause": (gpt.get("score") or {}).get("cause"),
                "n_hit": n_h,
                "n_miss": n_m,
                "n_abstain": n_ab,
                "abstention": (n_ab / len(statuses)) if statuses else None,
                "sensitivity": (n_h / hm) if hm else None,
            }
        )
    defined_sens = [c["sensitivity"] for c in cluster_rows if c["sensitivity"] is not None]
    defined_abs = [c["abstention"] for c in cluster_rows if c["abstention"] is not None]
    return {
        "n_legs": len(legs),
        "n_scorable": n_hit + n_miss + n_abstain,
        "n_unscored": n_unscored,
        "episode_counts": {
            "HIT": n_hit,
            "MISS": n_miss,
            "ABSTAIN": n_abstain,
            "unscored": n_unscored,
        },
        "N_B": 20,
        "note_unit": "N_B=20 clusters; 40 episodes are paired observations, not 40 clusters. Phase-3 pilot τ not pooled.",
        "cluster_table": cluster_rows,
        "cluster_mean_sensitivity": (sum(defined_sens) / len(defined_sens)) if defined_sens else None,
        "cluster_mean_abstention": (sum(defined_abs) / len(defined_abs)) if defined_abs else None,
        "E1": {
            "gate": e1_gate,
            "false_hit": e1_false,
            "n_false_hit": len(e1_false),
        },
        "E2": {
            "gate": e2_gate,
            "n_changed_episodes": len(e2_fail),
            "changed_clusters": e2_clusters,
            "failures": e2_fail,
        },
        "E3": {
            "gate": e3_gate,
            "eligible_tau": e3_tau,
            "n_eligible_tau": len(e3_tau),
            "n_eligible_clusters": len(e3_clusters),
            "floor": 5,
            "all_eligible_hit": e3_all_hit,
        },
        "E4": {
            "gate": e4_gate,
            "eligible_tau": e4_tau,
            "n_eligible_tau": len(e4_tau),
            "n_eligible_clusters": len(e4_clusters),
            "floor": 5,
            "all_eligible_miss": e4_all_miss,
        },
        "P4B_constructive_transfer": p4b,
    }


def write_report(info: dict, legs: list[dict], analysis: dict, spend: float, stopped: str | None) -> None:
    payload = {
        "phase": 4,
        "workstream": "P4-B",
        "models": {"flash": FLASH, "gpt": GPT},
        "N_B": 20,
        "n_slots": 40,
        "n_completed": len(legs),
        "api_spend_usd_phase4": round(spend, 6),
        "api_spend_usd_phase3_not_pooled": PHASE3_SPEND,
        "api_spend_usd_cumulative": round(spend + PHASE3_SPEND, 6),
        "cap_usd": CAP_USD,
        "stopped": stopped,
        "instrument_sha256": info["instrument_sha256"],
        "instrument_modified": False,
        "corpus_modified": False,
        "gold_modified": False,
        "pilot_pooled": False,
        "claude_run": False,
        **analysis,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "p4b_phase4_results.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# P4-B Phase 4 confirmatory validation",
        "",
        f"N_B = 20 clusters; confirmatory episodes = {len(legs)} / 40",
        f"models = Flash `{FLASH}` + GPT `{GPT}`",
        f"api_spend_usd_phase4 = {payload['api_spend_usd_phase4']}",
        f"api_spend_usd_cumulative = {payload['api_spend_usd_cumulative']} / {CAP_USD}",
        f"stopped = {stopped}",
        "Phase-3 pilot τ not pooled. Claude not run.",
        "Measurement channel = last assistant text only. Execution status is not HIT/MISS.",
        "",
        "## Episode counts (40 paired observations, not N)",
        "",
        f"- HIT = {analysis['episode_counts']['HIT']}",
        f"- MISS = {analysis['episode_counts']['MISS']}",
        f"- ABSTAIN = {analysis['episode_counts']['ABSTAIN']}",
        f"- unscored = {analysis['episode_counts']['unscored']}",
        "",
        f"cluster-mean sensitivity (defined clusters) = {analysis['cluster_mean_sensitivity']}",
        f"cluster-mean abstention = {analysis['cluster_mean_abstention']}",
        "",
        "## Gates",
        "",
        f"- E1 false HIT = **{analysis['E1']['gate']}** (n_false_hit={analysis['E1']['n_false_hit']})",
        f"- E2 invariance = **{analysis['E2']['gate']}** (changed_clusters={analysis['E2']['changed_clusters']})",
        f"- E3 natural C1 = **{analysis['E3']['gate']}** (eligible_clusters={analysis['E3']['n_eligible_clusters']}, eligible_tau={analysis['E3']['n_eligible_tau']}, floor=5)",
        f"- E4 natural C2 = **{analysis['E4']['gate']}** (eligible_clusters={analysis['E4']['n_eligible_clusters']}, eligible_tau={analysis['E4']['n_eligible_tau']}, floor=5)",
        f"- P4-B constructive transfer = **{analysis['P4B_constructive_transfer']}**",
        "",
        "## Per cluster × model (execution vs P4 measurement)",
        "",
        "| id | flash_exec | flash_P4 | flash_cause | gpt_exec | gpt_P4 | gpt_cause | cluster_sens | cluster_abs |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for c in analysis["cluster_table"]:
        lines.append(
            f"| `{c['id']}` | {c.get('flash_execution')} | {c['flash']} | {c['flash_cause']} | {c.get('gpt_execution')} | {c['gpt']} | {c['gpt_cause']} | {c['sensitivity']} | {c['abstention']} |"
        )
    lines += [
        "",
        "E3/E4 floor is on distinct clusters, not 40 episodes.",
        "Corpus/gold/instrument were not modified.",
    ]
    (OUT / "p4b_phase4_results.md").write_text("\n".join(lines) + "\n")
    (OUT / "p4b_phase4_status.json").write_text(
        json.dumps(
            {
                "phase": 4,
                "workstream": "P4-B",
                "status": analysis["P4B_constructive_transfer"] if len(legs) == 40 else "INCOMPLETE",
                "n_completed": len(legs),
                "api_spend_usd": payload["api_spend_usd_phase4"],
                "E1": analysis["E1"]["gate"],
                "E2": analysis["E2"]["gate"],
                "E3": analysis["E3"]["gate"],
                "E4": analysis["E4"]["gate"],
                "next": "PHASE_5_CLAUDE" if analysis["P4B_constructive_transfer"] == "PASS" else "STOP",
                "next_status": "BLOCKED",
                "instrument_modified": False,
                "corpus_modified": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    print("\n".join(lines))


def main() -> int:
    score_only = "--score-only" in sys.argv
    info = preflight()
    if "--check" in sys.argv:
        print(json.dumps({"preflight": "OK", **info}, indent=2))
        return 0

    RUN.mkdir(parents=True, exist_ok=True)
    done = load_progress()
    spend = 0.0
    if done:
        spend = max(float(v.get("spend_usd_end") or 0) for v in done.values())

    if not score_only:
        key, key_name = resolve_key()
        if not key:
            print("FAIL: no OpenRouter key (LARGE/SMALL/OPENROUTER_API_KEY)", file=sys.stderr)
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
            remain_slots = 40 - len(done)
            if remain_slots > 0:
                avg = FLASH_BURN_PER_LEG * (GPT_QUOTE_MULT if lane == "gpt" else 1.0)
                # refresh projection from observed mean if we have completed legs
                if done:
                    avg = max(spend / max(len(done), 1), 1e-9)
                if spend + avg * remain_slots > CAP_USD:
                    stopped = "projected_over_cap"
                    break
            cluster = json.loads((SLATE / f"{cid}.json").read_text())
            print(f"LEG {i}/40 {cid} {lane} {model} spend={spend:.6f}", flush=True)
            leg = run_leg(key, model, cluster["instruction"], WORLDS / cid, spend)
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
                    leg["scorable"] = isinstance(scored, dict) and "status" in scored and "cause" in scored
                except Exception as exc:
                    leg["score"] = None
                    leg["scorable"] = False
                    leg["harness_exception"] = f"score_exception:{exc}"[:400]
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
                "phase3_pilot": False,
                "channel": "last_assistant_text",
                "trajectory_used_for_p4": False,
            }
            (RUN / f"{cid}_{lane}_tau.txt").write_text(row["tau"])
            (RUN / f"{cid}_{lane}_leg.json").write_text(json.dumps({k: v for k, v in row.items() if k != "tau"}, indent=2, sort_keys=True) + "\n")
            append_leg(row)
            done[sk] = row
            if i % 5 == 0:
                print(f"SPEND_CHECKPOINT legs={len(done)} usd={spend:.6f}", flush=True)
            # Frozen §13: stop remaining spend if E1/E2 fail on the scored prefix.
            if row.get("scorable") and row.get("score"):
                if not gold_in_clean(row["tau"], cluster["gold"]) and row["score"].get("status") == "HIT":
                    stopped = f"E1_false_hit_prefix:{cid}:{lane}"
                    break
                tables = load_tables(cid)
                vals = same_kind_values(cluster["kind"], cluster["gold"], tables)
                if vals and len(vals) >= 2 and row["tau"].strip():
                    inv = e2_on_tau(
                        row["tau"],
                        cluster["kind"],
                        cluster["gold"],
                        cluster["anchors"],
                        distractor_line(vals[0], cluster["anchors"]),
                        distractor_line(vals[1], cluster["anchors"]),
                    )
                    if not inv["pass"]:
                        stopped = f"E2_fail_prefix:{cid}:{lane}"
                        break
            time.sleep(0.2)
    else:
        stopped = None
        key_name = "score-only"

    legs = [done[f"{cid}:{lane}"] for cid, lane, _ in slots() if f"{cid}:{lane}" in done]
    if not legs:
        print("no legs recorded", file=sys.stderr)
        return 1
    # Estimands only after the confirmatory set is complete, unless a kill stopped spend.
    if len(legs) < 40 and not stopped:
        stopped = "incomplete"
    analysis = analyze(legs)
    write_report(info, legs, analysis, spend if not score_only else max((float(x.get("spend_usd_end") or 0) for x in legs), default=0.0), stopped)
    if stopped and stopped.startswith("E1"):
        return 1
    if stopped and stopped.startswith("E2"):
        return 1
    if len(legs) != 40:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
