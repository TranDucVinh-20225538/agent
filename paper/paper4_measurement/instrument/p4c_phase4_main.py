#!/usr/bin/env python3
"""P4-C Phase 4 confirmatory validation. 30 clusters × 2 models = 60 legs.

Does not edit p4_instrument.py, gold, anchors, worlds, transforms, N_C, or P4-B.
Does not pool Phase-3 pilot τ into N_C. Does not run Claude.
Primary gates use Flash confirmatory legs. GPT is paired/descriptive.
LARGE OpenRouter lane only.
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
CQDIR = CON / "slate" / "cq"
WORLDS = SLATE / "worlds"
OUT = CON / "out"
SEAL = CON / "sealed" / "P4C_PHASE2_SEAL.json"
TRANS = CON / "transforms_c.py"
ADJ = CON / "adjudicator_c.py"
GOLD_SPEC = OUT / "p4c_gold_spec.json"
PHASE3 = OUT / "p4c_phase3_status.json"
RUN = OUT / "p4c_phase4"
EXPECTED_INSTR = "c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59"
EXPECTED_SEAL_GATE = "PASS"
EXPECTED_CLUSTERS = "bd30104becac546169ce62f921e6079a3df758a9a0fccf95106f9aa59060352f"
EXPECTED_WORLDS = "b39c1e082a21c18f4a2b105e94586b3d0584b57af6c3a6904e50fa903ef75c4b"
EXPECTED_GOLD = "dfe9e6a308bc5b21e59c8ca27f2182b7e7773441ba185012371dc2fc1fd8c2d8"
EXPECTED_TRANS = "e6a000c62413be724d6452c27dbf755defac8baa173ed146ea7d092778d2bcd3"
EXPECTED_ADJ = "595b02f50a2ad968b56051bb4d0b8d8686697a29a94ac39afaf2e1d53b97a8b2"
IDS = [f"C{i:02d}" for i in range(1, 31)]
CQ_IDS = [f"CQ{i:02d}" for i in range(1, 7)]
FLASH = "qwen/qwen3.8-flash"
GPT = "openai/gpt-5.5"
MODELS = (("flash", FLASH), ("gpt", GPT))
MAX_STEPS = 40
N_C = 30
N_SLOTS = 60
CAP_USD = 400.0
PHASE3_SPEND = 0.00113
FLASH_BURN_PER_LEG = PHASE3_SPEND / 3.0
GPT_QUOTE_MULT = 5.0
READ_CAP = 32_000
FALLBACK_IN_PER_M = 0.10
FALLBACK_OUT_PER_M = 0.40
C1_FLOOR = 10
C2_FLOOR = 10
COV_GATE = 0.50

sys.path.insert(0, str(INSTR.parent))
sys.path.insert(0, str(CON))
from p4_instrument import (  # noqa: E402
    extract_candidates,
    locate_lines,
    score,
    v1_clean,
    v3_match,
)
import generate_c as g  # noqa: E402
import transforms_c as T  # noqa: E402
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
            "HTTP-Referer": "https://local.p4c-phase4",
            "X-Title": "P4-C Phase 4 confirmatory",
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
                    tool_trace.append({"tool": name, "path": str(args.get("path") or "."), "result": result})
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
                        probe = int(canon) if kind == "integer" else g.format_gold(kind, s)
                        if not v3_match(kind, probe, gold) and canon not in found:
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
    cleaned, _cause = v1_clean(tau)
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


def g4_on_tau(tau: str, kind: str, gold: str, anchors: list[str], d1: str, d2: str) -> dict:
    base = score(tau, kind=kind, gold=gold, anchors=anchors)
    c5 = score(T.c5_irr(tau, d1), kind=kind, gold=gold, anchors=anchors)
    t6a, t6b = T.c6_pair(tau, d1, d2)
    c6a = score(t6a, kind=kind, gold=gold, anchors=anchors)
    c6b = score(t6b, kind=kind, gold=gold, anchors=anchors)
    changed = []
    for name, sc in (("c5", c5), ("c6a", c6a), ("c6b", c6b)):
        if sc.get("status") != base.get("status") or sc.get("committed") != base.get("committed"):
            changed.append(name)
    return {"base": base, "changed": changed, "pass": not changed}


def slots() -> list[tuple[str, str, str]]:
    out = []
    for lane, model in MODELS:
        for cid in IDS:
            out.append((cid, lane, model))
    return out


def designed_c3_c4() -> dict:
    hits = []
    rows = {}
    for cid in CQ_IDS:
        cluster = json.loads((CQDIR / f"{cid}.json").read_text())
        for ctrl in ("C3", "C4"):
            sc = score(
                cluster["observations"][ctrl],
                kind=cluster["kind"],
                gold=cluster["gold"],
                anchors=cluster["anchors"],
            )
            rows[f"{cid}:{ctrl}"] = sc
            if sc.get("status") == "HIT":
                hits.append(f"{cid}:{ctrl}")
    return {"n_hit": len(hits), "hits": hits, "controls": rows}


def preflight() -> dict:
    instr_sha = sha256_file(INSTR)
    if instr_sha != EXPECTED_INSTR:
        raise SystemExit(f"instrument drifted: {instr_sha}")
    seal = json.loads(SEAL.read_text())
    if seal.get("gate") != EXPECTED_SEAL_GATE or seal.get("status") != "SEALED":
        raise SystemExit("Phase 2 seal is not PASS/SEALED")
    p3 = json.loads(PHASE3.read_text())
    if p3.get("status") != "PASS":
        raise SystemExit("Phase 3 is not PASS")
    cluster_paths = [SLATE / f"{cid}.json" for cid in IDS]
    world_paths = sorted(p for p in WORLDS.rglob("*") if p.is_file())
    clusters_sha = combined_hash(cluster_paths)
    worlds_sha = combined_hash(world_paths)
    gold_sha = sha256_file(GOLD_SPEC)
    trans_sha = sha256_file(TRANS)
    adj_sha = sha256_file(ADJ)
    if clusters_sha != EXPECTED_CLUSTERS or clusters_sha != seal["clusters_sha256"]:
        raise SystemExit(f"clusters hash mismatch: {clusters_sha}")
    if worlds_sha != EXPECTED_WORLDS or worlds_sha != seal["worlds_sha256"]:
        raise SystemExit(f"worlds hash mismatch: {worlds_sha}")
    if gold_sha != EXPECTED_GOLD or gold_sha != seal["gold_spec_sha256"]:
        raise SystemExit(f"gold spec hash mismatch: {gold_sha}")
    if trans_sha != EXPECTED_TRANS or trans_sha != seal["transforms_c_sha256"]:
        raise SystemExit(f"transforms hash mismatch: {trans_sha}")
    if adj_sha != EXPECTED_ADJ or adj_sha != seal["adjudicator_c_sha256"]:
        raise SystemExit(f"adjudicator hash mismatch: {adj_sha}")
    for cid in IDS:
        cluster = json.loads((SLATE / f"{cid}.json").read_text())
        if cluster.get("id") != cid:
            raise SystemExit(f"{cid} id mismatch")
        if "observations" in cluster:
            raise SystemExit(f"{cid} has observations")
        if not (WORLDS / cid).is_dir():
            raise SystemExit(f"missing world {cid}")
    remaining = CAP_USD - PHASE3_SPEND
    projected = 30 * FLASH_BURN_PER_LEG + 30 * FLASH_BURN_PER_LEG * GPT_QUOTE_MULT
    if projected > remaining:
        raise SystemExit(f"preflight projection {projected:.6f} exceeds remaining {remaining:.6f}")
    return {
        "instrument_sha256": instr_sha,
        "clusters_sha256": clusters_sha,
        "worlds_sha256": worlds_sha,
        "gold_spec_sha256": gold_sha,
        "transforms_c_sha256": trans_sha,
        "adjudicator_c_sha256": adj_sha,
        "seal_gate": seal.get("gate"),
        "phase3_spend_usd": PHASE3_SPEND,
        "projected_phase4_usd": round(projected, 6),
        "remaining_cap_usd": round(remaining, 6),
        "flash_model": FLASH,
        "gpt_model": GPT,
        "n_slots": N_SLOTS,
        "N_C": N_C,
        "pilot_pooled": False,
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
    cov = (n_hit + n_miss) / N_C
    cc = (n_hit / (n_hit + n_miss)) if (n_hit + n_miss) else None
    abs_ = n_abstain / N_C
    dh = n_hit / N_C
    return {
        "HIT": n_hit,
        "MISS": n_miss,
        "ABSTAIN": n_abstain,
        "unscored": n_unscored,
        "n_scorable": n,
        "Cov": cov,
        "CC": cc,
        "Abs": abs_,
        "DH": dh,
    }


def analyze(legs: list[dict]) -> dict:
    by_cluster: dict[str, dict] = {cid: {} for cid in IDS}
    g1_false = []
    g4_fail = []
    c1_elig = []
    c2_elig = []
    designed = designed_c3_c4()

    for row in legs:
        cid = row["id"]
        lane = row["lane"]
        cluster = json.loads((SLATE / f"{cid}.json").read_text())
        kind, gold, anchors = cluster["kind"], cluster["gold"], cluster["anchors"]
        slot = cluster["slot"]
        tables = load_tables(cid)
        vals = same_kind_values(kind, gold, tables)
        d1 = distractor_line(vals[0] if vals else "0", anchors)
        d2 = distractor_line(vals[1] if len(vals) > 1 else "1", anchors)
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
                g1_false.append({"id": cid, "lane": lane})
            inv = g4_on_tau(tau, kind, gold, anchors, d1, d2)
            row["g4"] = {"pass": inv["pass"], "changed": inv["changed"]}
            if lane == "flash" and not inv["pass"]:
                g4_fail.append({"id": cid, "changed": inv["changed"]})
            geom1 = natural_c1(tau, kind, gold, anchors)
            geom2 = natural_c2(tau, kind, gold, anchors)
            gt_lab = gt.get("gt")
            if lane == "flash":
                if (slot == "C1-intended" or gt_lab == "SUCCESS") and gt_lab != "FAIL" and geom1:
                    c1_elig.append({"id": cid, "status": sc.get("status"), "gt": gt_lab, "slot": slot})
                if (slot == "C2-intended" or gt_lab == "FAIL") and geom2:
                    c2_elig.append({"id": cid, "status": sc.get("status"), "gt": gt_lab, "slot": slot})
        by_cluster[cid][lane] = row

    flash_m = lane_counts(legs, "flash")
    gpt_m = lane_counts(legs, "gpt")

    n_c1 = len(c1_elig)
    n_c2 = len(c2_elig)
    c1_hits = sum(1 for r in c1_elig if r["status"] == "HIT")
    c2_miss = sum(1 for r in c2_elig if r["status"] == "MISS")
    c1_rate = (c1_hits / n_c1) if n_c1 else None
    c2_rate = (c2_miss / n_c2) if n_c2 else None

    g1_designed_ok = designed["n_hit"] == 0
    g1_gate = "PASS" if (not g1_false and g1_designed_ok) else "FAIL"
    if n_c1 < C1_FLOOR:
        g2_gate = "NOT_EVALUABLE"
    else:
        g2_gate = "PASS" if (c1_rate is not None and c1_rate >= 0.90) else "FAIL"
    if n_c2 < C2_FLOOR:
        g3_gate = "NOT_EVALUABLE"
    else:
        g3_gate = "PASS" if (c2_rate is not None and c2_rate >= 0.90) else "FAIL"
    g4_gate = "PASS" if not g4_fail else "FAIL"
    g5_gate = "PASS" if flash_m["Cov"] >= COV_GATE else "FAIL"
    g6_gate = "PASS"
    if flash_m["CC"] is None and flash_m["HIT"] + flash_m["MISS"] > 0:
        g6_gate = "FAIL"

    metric = "FAIL"
    gates = {
        "G1": g1_gate,
        "G2": g2_gate,
        "G3": g3_gate,
        "G4": g4_gate,
        "G5": g5_gate,
        "G6": g6_gate,
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
            "Cov": flash_m["Cov"],
            "CC": flash_m["CC"],
            "display": f"DH={flash_m['DH']:.4f} (Cov={flash_m['Cov']:.4f}, CC={flash_m['CC']:.4f})",
        }

    return {
        "n_legs": len(legs),
        "N_C": N_C,
        "note_unit": "N_C=30 clusters. 60 episodes are paired observations, not 60 clusters. Phase-3 pilot τ not pooled.",
        "flash": flash_m,
        "gpt": gpt_m,
        "primary_public": {"Cov": flash_m["Cov"], "CC": flash_m["CC"]},
        "DH_with_coverage": dh_flash,
        "cluster_table": cluster_rows,
        "G1": {
            "gate": g1_gate,
            "false_hit": g1_false,
            "n_false_hit": len(g1_false),
            "designed_c3_c4_hit": designed["hits"],
        },
        "G2": {
            "gate": g2_gate,
            "n_eligible": n_c1,
            "floor": C1_FLOOR,
            "n_hit": c1_hits,
            "hit_rate": c1_rate,
            "eligible": c1_elig,
        },
        "G3": {
            "gate": g3_gate,
            "n_eligible": n_c2,
            "floor": C2_FLOOR,
            "n_miss": c2_miss,
            "miss_rate": c2_rate,
            "eligible": c2_elig,
        },
        "G4": {"gate": g4_gate, "n_changed": len(g4_fail), "failures": g4_fail},
        "G5": {"gate": g5_gate, "Cov": flash_m["Cov"], "threshold": COV_GATE},
        "G6": {
            "gate": g6_gate,
            "published": "(Cov, CC) and optional DH (Cov, CC)",
            "ABSTAIN_hidden": False,
        },
        "P4C_metric": metric,
        "gates": gates,
    }


def write_report(info: dict, legs: list[dict], analysis: dict, spend: float, stopped: str | None) -> None:
    payload = {
        "phase": 4,
        "workstream": "P4-C",
        "models": {"flash": FLASH, "gpt": GPT},
        "N_C": N_C,
        "n_slots": N_SLOTS,
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
        "p4b_modified": False,
        "pilot_pooled": False,
        "claude_run": False,
        **analysis,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "p4c_phase4_results.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    flash = analysis["flash"]
    cc_s = "undefined" if flash["CC"] is None else f"{flash['CC']:.4f}"
    dh = analysis["DH_with_coverage"]
    dh_s = dh["display"] if dh else "undefined (CC undefined)"
    lines = [
        "# P4-C Phase 4 confirmatory validation",
        "",
        f"N_C = 30 clusters; confirmatory episodes = {len(legs)} / 60",
        f"models = Flash `{FLASH}` (primary) + GPT `{GPT}` (paired)",
        f"api_spend_usd_phase4 = {payload['api_spend_usd_phase4']}",
        f"api_spend_usd_cumulative = {payload['api_spend_usd_cumulative']} / {CAP_USD}",
        f"stopped = {stopped}",
        "Phase-3 pilot τ not pooled. Claude not run. P4-B not pooled.",
        "Measurement channel = last assistant text only. Execution status is not HIT/MISS.",
        "ABSTAIN is missing correspondence measurement, not task failure.",
        "",
        "## Primary public report (Flash confirmatory, N_C = 30)",
        "",
        f"- Cov = **{flash['Cov']:.4f}**  ({flash['HIT']}+{flash['MISS']})/{N_C}",
        f"- CC = **{cc_s}**",
        f"- Abs = {flash['Abs']:.4f}  ({flash['ABSTAIN']}/{N_C})",
        f"- DH (Cov, CC) = {dh_s}",
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
        f"- Cov = {analysis['gpt']['Cov']:.4f}",
        f"- CC = {analysis['gpt']['CC']}",
        "",
        "## Gates (Flash confirmatory unless noted)",
        "",
        f"- G1 false HIT = **{analysis['G1']['gate']}** (n_false_hit={analysis['G1']['n_false_hit']}; designed C3/C4 HIT={analysis['G1']['designed_c3_c4_hit']})",
        f"- G2 C1 sensitivity = **{analysis['G2']['gate']}** (eligible={analysis['G2']['n_eligible']}, floor={C1_FLOOR}, hit_rate={analysis['G2']['hit_rate']})",
        f"- G3 C2 discrimination = **{analysis['G3']['gate']}** (eligible={analysis['G3']['n_eligible']}, floor={C2_FLOOR}, miss_rate={analysis['G3']['miss_rate']})",
        f"- G4 invariance = **{analysis['G4']['gate']}** (n_changed={analysis['G4']['n_changed']})",
        f"- G5 coverage = **{analysis['G5']['gate']}** (Cov={analysis['G5']['Cov']:.4f}, gate≥{COV_GATE})",
        f"- G6 scalar honesty = **{analysis['G6']['gate']}**",
        f"- P4-C-Metric v1 = **{analysis['P4C_metric']}**",
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
        "G2/G3 floors are on distinct Flash-eligible clusters, not 60 episodes.",
        "NOT EVALUABLE on a required floor fails P4-C. Corpus/gold/instrument were not modified.",
    ]
    (OUT / "p4c_phase4_results.md").write_text("\n".join(lines) + "\n")
    complete = len(legs) == N_SLOTS and not (stopped and str(stopped).startswith("G1"))
    status = analysis["P4C_metric"] if len(legs) == N_SLOTS else "INCOMPLETE"
    (OUT / "p4c_phase4_status.json").write_text(
        json.dumps(
            {
                "phase": 4,
                "workstream": "P4-C",
                "status": status,
                "n_completed": len(legs),
                "api_spend_usd": payload["api_spend_usd_phase4"],
                "G1": analysis["G1"]["gate"],
                "G2": analysis["G2"]["gate"],
                "G3": analysis["G3"]["gate"],
                "G4": analysis["G4"]["gate"],
                "G5": analysis["G5"]["gate"],
                "G6": analysis["G6"]["gate"],
                "Cov": flash["Cov"],
                "CC": flash["CC"],
                "next": "PHASE_5_CLAUDE" if analysis["P4C_metric"] == "PASS" else "STOP",
                "next_status": "BLOCKED",
                "instrument_modified": False,
                "corpus_modified": False,
                "p4b_modified": False,
                "pilot_pooled": False,
                "complete": complete,
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
                "channel": "last_assistant_text",
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
                if len(vals) >= 2:
                    inv = g4_on_tau(
                        row["tau"],
                        cluster["kind"],
                        cluster["gold"],
                        cluster["anchors"],
                        distractor_line(vals[0], cluster["anchors"]),
                        distractor_line(vals[1], cluster["anchors"]),
                    )
                    if not inv["pass"]:
                        stopped = f"G4_fail_prefix:{cid}:{lane}"
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
    return 0 if analysis["P4C_metric"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
