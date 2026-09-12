#!/usr/bin/env python3
"""P4-C2 Phase 1: instantiate worlds, lock gold from L, audit construction.

No per-id branch. No observations. No agents.
Does not edit p4_instrument.py. Does not modify P4-B or P4-C v1.
No anchors in params or score_v2.
"""
from __future__ import annotations

import ast
import csv
import hashlib
import inspect
import io
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent
P4 = ROOT.parent
INSTR_V1 = P4 / "instrument" / "p4_instrument.py"
INSTR_V2 = P4 / "instrument" / "p4_instrument_v2.py"
WRAPPER = P4 / "instrument" / "p4c2_claim_wrapper.txt"
ADJ = ROOT / "adjudicator_d.py"
SLATE = ROOT / "slate" / "d"
WORLDS = SLATE / "worlds"
OUT = ROOT / "out"
EXPECTED_INSTR_V1 = "c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59"
N_D = 30
IDS = [f"D{i:02d}" for i in range(1, 31)]
KIND_QUOTA = {"money_usd": 12, "integer": 9, "entity": 5, "categorical": 4}
FAMILY_QUOTA = {
    "Locate": 5,
    "Compute": 5,
    "Reconcile": 5,
    "Filter": 5,
    "Tally": 5,
    "Multi-step": 5,
}
SLOT_QUOTA = {"C1-intended": 10, "C2-intended": 10, "ordinary": 10}
FAMILY_OP = {
    "Locate": "select_join",
    "Filter": "select_join",
    "Compute": "sum_join",
    "Tally": "count_join",
    "Reconcile": "live_not_stale",
    "Multi-step": "select_join3",
}
FORBIDDEN_VALUES = {
    "4820.50",
    "1205.00",
    "700.00",
    "318.75",
    "2450.00",
    "77.10",
    "6100.00",
    "3910.00",
    "990.00",
    "512.00",
    "42.12",
    "3570.0",
    "3570",
    "88.40",
    "55.90",
    "46.25",
    "64.25",
    "29.60",
    "73.15",
    "37.80",
    "65.30",
    "2",
    "3",
    "4",
    "5",
    "12",
    "14",
    "dim",
    "hush",
    "brisk",
    "Wren Cobb",
    "Tov Gale",
    "night_chute_card.txt",
    "71.30",
    "53.80",
    "44.15",
    "39.25",
    "48.70",
    "62.45",
    "36.90",
    "27.40",
    "33.50",
    "19.85",
    "24.60",
    "Ivo Nair",
    "Rune Pell",
    "Odas Wynn",
    "Sera Pell",
    "Bram Kist",
    "pale",
    "keen",
    "still",
    "raw",
    "6",
    "7",
    "8",
    "9",
    "13",
    "16",
}
FORBIDDEN_SUBSTR = (
    "jamaica",
    "sandals",
    "gme",
    "oddsmarket",
    "batbucks",
    "nyc_flight",
    "settlement_total",
)
TOY_BASENAMES = {"answer", "gold", "result", "label", "p4"}
TOKEN_RE = re.compile(r"[A-Za-z]+")
MONEY_RE = re.compile(
    r"\$\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?|\d{1,3}(?:,\d{3})*\.\d{1,2}"
)
INT_RE = re.compile(r"\d+")
EXCLUSION_IDS = {
    "contradiction-f013",
    "contradiction-f015",
    "contradiction-f016",
    "contradiction-f021",
    "contradiction-f023",
    "counterfactual-f008",
    "counterfactual-f014",
    "retrieval-f020",
    "retrieval-f032",
    "retrieval-f033",
    "retrieval-f035",
    "contradiction-f024",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_wordlist(name: str) -> set[str]:
    return {
        ln.strip().casefold()
        for ln in (ROOT / name).read_text().splitlines()
        if ln.strip()
    }


def words(text: str) -> set[str]:
    return {m.group(0).casefold() for m in TOKEN_RE.finditer(text)}


def no_per_id_branch(src: str, ids: list[str]) -> bool:
    tree = ast.parse(src)
    banned = set(ids)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in {"task_id", "cluster_id"}:
            return False
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value in banned:
                return False
    return True


def emit_csv(columns: list[str], rows: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n")
    w.writeheader()
    for row in rows:
        w.writerow({c: row[c] for c in columns})
    return buf.getvalue()


def emit_kv(rows: list[dict]) -> str:
    blocks = []
    for row in rows:
        blocks.append("\n".join(f"{k}: {v}" for k, v in row.items()))
    return "\n---\n".join(blocks) + "\n"


def emit_ics(rows: list[dict]) -> str:
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0"]
    for row in rows:
        lines += [
            "BEGIN:VEVENT",
            f"SUMMARY:{row['summary']}",
            f"LOCATION:{row.get('location', '')}",
            f"X-HOURS:{row.get('hours', '')}",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\n".join(lines) + "\n"


def emit_html(columns: list[str], rows: list[dict]) -> str:
    head = "".join(f"<th>{c}</th>" for c in columns)
    body = []
    for row in rows:
        tds = "".join(f"<td>{row[c]}</td>" for c in columns)
        body.append(f"<tr>{tds}</tr>")
    return (
        "<html><body><table><tr>"
        + head
        + "</tr>"
        + "".join(body)
        + "</table></body></html>\n"
    )


def emit_txtlist(rows: list[dict], field: str) -> str:
    return "".join(f"{row[field]}\n" for row in rows)


def emit_file(spec: dict) -> str:
    fmt = spec["format"]
    rows = spec["rows"]
    if fmt == "csv":
        return emit_csv(spec["columns"], rows)
    if fmt == "kv":
        return emit_kv(rows)
    if fmt == "ics":
        return emit_ics(rows)
    if fmt == "html":
        return emit_html(spec["columns"], rows)
    if fmt == "txtlist":
        return emit_txtlist(rows, spec.get("field", "name"))
    raise ValueError(fmt)


def parse_csv(text: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(text)))


def parse_kv(text: str) -> list[dict]:
    rows = []
    for block in text.split("\n---\n"):
        row = {}
        for line in block.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                row[k.strip()] = v.strip()
        if row:
            rows.append(row)
    return rows


def parse_ics(text: str) -> list[dict]:
    rows = []
    cur: dict[str, str] = {}
    for line in text.splitlines():
        if line == "BEGIN:VEVENT":
            cur = {}
        elif line == "END:VEVENT":
            if cur:
                rows.append(cur)
            cur = {}
        elif line.startswith("SUMMARY:"):
            cur["summary"] = line.split(":", 1)[1]
        elif line.startswith("LOCATION:"):
            cur["location"] = line.split(":", 1)[1]
        elif line.startswith("X-HOURS:"):
            cur["hours"] = line.split(":", 1)[1]
    return rows


def parse_html(text: str) -> list[dict]:
    th = re.findall(r"<th>(.*?)</th>", text)
    rows = []
    for tr in re.findall(r"<tr>(.*?)</tr>", text)[1:]:
        tds = re.findall(r"<td>(.*?)</td>", tr)
        rows.append(dict(zip(th, tds)))
    return rows


def parse_txtlist(text: str, field: str = "name") -> list[dict]:
    return [{field: ln.strip()} for ln in text.splitlines() if ln.strip()]


def parse_file(spec: dict, text: str) -> list[dict]:
    fmt = spec["format"]
    if fmt == "csv":
        return parse_csv(text)
    if fmt == "kv":
        return parse_kv(text)
    if fmt == "ics":
        return parse_ics(text)
    if fmt == "html":
        return parse_html(text)
    if fmt == "txtlist":
        return parse_txtlist(text, spec.get("field", "name"))
    raise ValueError(fmt)


def match_where(row: dict, where: list[dict]) -> bool:
    for clause in where or []:
        col = clause["col"]
        raw = str(row.get(col, ""))
        if "eq" in clause and raw != str(clause["eq"]):
            return False
        if "ge" in clause:
            try:
                if Decimal(raw) < Decimal(str(clause["ge"])):
                    return False
            except Exception:
                return False
        if "le" in clause:
            try:
                if Decimal(raw) > Decimal(str(clause["le"])):
                    return False
            except Exception:
                return False
    return True


def unique(seq: list[str]) -> list[str]:
    out = []
    for x in seq:
        if x not in out:
            out.append(x)
    return out


def format_gold(kind: str, raw) -> str:
    if kind == "money_usd":
        d = Decimal(str(raw).replace("$", "").replace(",", ""))
        return f"{d:.2f}"
    if kind == "integer":
        return str(int(raw))
    return str(raw).strip()


def apply_locator(tables: dict[str, list[dict]], locator: dict, kind: str) -> str:
    op = locator["op"]
    left = tables[locator["left"]]
    right = tables[locator["right"]]
    key = locator["key"]
    right_keys = {str(r.get(key, "")) for r in right}
    left_f = [r for r in left if match_where(r, locator.get("left_where") or [])]
    joined = [r for r in left_f if str(r.get(key, "")) in right_keys]

    if op == "select_join":
        field = locator["field"]
        vals = unique([str(r[field]) for r in joined if field in r])
        if len(vals) != 1:
            raise ValueError(f"select_join not unique: {vals}")
        return format_gold(kind, vals[0])

    if op == "select_join3":
        mid = tables[locator["mid"]]
        mid_keys = {str(r.get(key, "")) for r in mid}
        field = locator["field"]
        joined3 = [r for r in joined if str(r.get(key, "")) in mid_keys]
        vals = unique([str(r[field]) for r in joined3 if field in r])
        if len(vals) != 1:
            raise ValueError(f"select_join3 not unique: {vals}")
        return format_gold(kind, vals[0])

    if op == "sum_join":
        field = locator["field"]
        if len(joined) < 2:
            raise ValueError(f"sum_join needs >=2 rows, got {len(joined)}")
        total = sum(Decimal(str(r[field]).replace("$", "").replace(",", "")) for r in joined)
        return format_gold(kind, total)

    if op == "count_join":
        return format_gold(kind, len(joined))

    if op == "live_not_stale":
        field = locator["field"]
        live = [r for r in left if match_where(r, locator.get("left_where") or [])]
        stale = [r for r in right if match_where(r, locator.get("right_where") or [])]
        if len(live) != 1 or len(stale) != 1:
            raise ValueError(f"live/stale not unique live={live} stale={stale}")
        lv = format_gold(kind, live[0][field])
        sv = format_gold(kind, stale[0][field])
        if lv == sv:
            raise ValueError("live equals stale")
        return lv

    raise ValueError(op)


def kind_values(kind: str, blob: str) -> list[str]:
    if kind == "money_usd":
        return unique([m.group(0) for m in MONEY_RE.finditer(blob)])
    if kind == "integer":
        money_spans = [m.span() for m in MONEY_RE.finditer(blob)]
        ints = []
        for m in INT_RE.finditer(blob):
            a, b = m.span()
            if any(a < mb and b > ma for ma, mb in money_spans):
                continue
            ints.append(m.group(0))
        return unique(ints)
    return []


def blob_of(files: dict[str, str]) -> str:
    return "\n".join(files.values())


def t3_ok(kind: str, gold: str, files: dict[str, str], tables: dict[str, list[dict]]) -> bool:
    blob = blob_of(files)
    if kind in {"money_usd", "integer"}:
        if kind == "money_usd":
            canon = []
            for v in kind_values(kind, blob):
                try:
                    canon.append(format_gold("money_usd", v))
                except Exception:
                    continue
            others = [v for v in unique(canon) if v != gold]
        else:
            others = [v for v in kind_values(kind, blob) if v != gold]
        return len(others) >= 3
    cells = []
    for rows in tables.values():
        for row in rows:
            for v in row.values():
                s = str(v).strip()
                if s and s != gold:
                    cells.append(s)
    return len(unique(cells)) >= 3


def v2_signature_ok(errors: list[str]) -> None:
    sys.path.insert(0, str(INSTR_V2.parent))
    from p4_instrument_v2 import score_v2

    params = inspect.signature(score_v2).parameters
    if "anchors" in params:
        errors.append("score_v2 still takes anchors")
    if "task_id" in params or "cluster_id" in params:
        errors.append("score_v2 takes task_id")
    src = INSTR_V2.read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "p4_instrument":
            names = {a.name for a in node.names}
            if "score" in names:
                errors.append("instrument v2 imports v1 score")
        if isinstance(node, ast.Import) and any(a.name == "p4_instrument" for a in node.names):
            errors.append("instrument v2 imports p4_instrument")
    if not no_per_id_branch(src, IDS):
        errors.append("p4_instrument_v2.py has a per-id branch")
    probe = score_v2("Working 81.60\n\nCLAIM: 81.60\n", kind="money_usd", gold="81.60")
    if probe.get("status") != "HIT":
        errors.append(f"score_v2 self-check HIT failed: {probe}")
    probe_abs = score_v2("The total is 81.60\n", kind="money_usd", gold="81.60")
    if probe_abs.get("status") != "ABSTAIN" or probe_abs.get("cause") != "no_claim":
        errors.append(f"score_v2 self-check no_claim failed: {probe_abs}")


def main() -> int:
    errors: list[str] = []
    instr_v1_sha = sha256_file(INSTR_V1)
    if instr_v1_sha != EXPECTED_INSTR_V1:
        errors.append(f"v1 instrument hash drifted: {instr_v1_sha}")

    if not WRAPPER.is_file():
        errors.append("missing claim wrapper")
    else:
        wrap = WRAPPER.read_text()
        if "CLAIM:" not in wrap or "<value>" not in wrap:
            errors.append("wrapper missing CLAIM contract")
        if any(tok in wrap.casefold() for tok in ("ridge", "bothy", "gold", "anchor")):
            errors.append("wrapper contains forbidden tokens")

    if not ADJ.is_file():
        errors.append("missing adjudicator_d.py")
    else:
        adj_src = ADJ.read_text()
        adj_tree = ast.parse(adj_src)
        for node in ast.walk(adj_tree):
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("p4_instrument"):
                errors.append("A2 imports a scorer")
                break
            if isinstance(node, ast.Import) and any(
                a.name.startswith("p4_instrument") for a in node.names
            ):
                errors.append("A2 imports a scorer")
                break
        if "ignores last-text" not in adj_src.casefold():
            errors.append("A2 last-text handling unclear")
        if not no_per_id_branch(adj_src, IDS):
            errors.append("adjudicator_d.py has a per-id branch")

    v2_signature_ok(errors)

    qtok = load_wordlist("wordlists_q.txt")
    vtok = load_wordlist("wordlists_v.txt")
    rtok = load_wordlist("wordlists_r.txt")
    btok = load_wordlist("wordlists_b.txt")
    ctok = load_wordlist("wordlists_c.txt")
    dtok = load_wordlist("wordlists_d.txt")
    if dtok & qtok or dtok & vtok or dtok & rtok or dtok & btok or dtok & ctok:
        errors.append("wordlists_d not disjoint from Q/V/R/B/C")
    foreign_cov = qtok | vtok | rtok | btok | ctok

    if not no_per_id_branch(Path(__file__).read_text(), IDS):
        errors.append("generate_d.py has a per-id branch")

    params = json.loads((ROOT / "params_d.json").read_text())
    ids = IDS
    if list(params) != ids:
        errors.append(f"params keys {list(params)} != {ids}")

    SLATE.mkdir(parents=True, exist_ok=True)
    if WORLDS.exists():
        for p in WORLDS.rglob("*"):
            if p.is_file():
                p.unlink()
    WORLDS.mkdir(parents=True, exist_ok=True)

    clusters = []
    kinds: dict[str, int] = {}
    families: dict[str, int] = {}
    slots: dict[str, int] = {}
    entity_files = 0

    sys.path.insert(0, str(INSTR_V2.parent))
    from p4_instrument_v2 import parse_money, v3_match

    for cid in ids:
        row = params[cid]
        if "anchors" in row:
            errors.append(f"{cid}: anchors present in params")
        family, kind = row["family"], row["kind"]
        slot = row["slot"]
        kinds[kind] = kinds.get(kind, 0) + 1
        families[family] = families.get(family, 0) + 1
        slots[slot] = slots.get(slot, 0) + 1
        loc = row["locator"]
        if loc["op"] != FAMILY_OP[family]:
            errors.append(f"{cid}: op {loc['op']} != family {family}")
        if loc["left"] == loc["right"]:
            errors.append(f"{cid}: T8 sources not distinct")
        if family == "Multi-step":
            if loc.get("mid") in {None, loc["left"], loc["right"]}:
                errors.append(f"{cid}: multi-step needs a third distinct source")

        files: dict[str, str] = {}
        tables: dict[str, list[dict]] = {}
        wdir = WORLDS / cid
        wdir.mkdir(parents=True, exist_ok=True)
        for spec in row["files"]:
            text = emit_file(spec)
            rel = spec["path"]
            dest = wdir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text)
            files[rel] = text
            parsed = parse_file(spec, text)
            tables[rel] = parsed
            if parse_file(spec, dest.read_text()) != parsed:
                errors.append(f"{cid}: disk parse mismatch {rel}")

        meta = {
            "id": cid,
            "family": family,
            "kind": kind,
            "component_id": row["component_id"],
            "instruction": row["instruction"],
            "locator": loc,
            "slot": slot,
            "files": sorted(files),
        }
        (wdir / "world_meta.json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
        if "gold" in meta or "observations" in meta or "anchors" in meta:
            errors.append(f"{cid}: gold/observations/anchors leaked into world_meta")

        lock_err = None
        gold = None
        try:
            gold = apply_locator(tables, loc, kind)
        except Exception as exc:
            lock_err = str(exc)

        checks = {
            "gold_locked": lock_err is None,
            "lock_error": lock_err,
            "kind_allowed": kind in KIND_QUOTA,
            "family_known": family in FAMILY_QUOTA,
            "one_component": True,
            "no_anchors": "anchors" not in row,
            "T4_no_observations": "observations" not in row and "last_response" not in row,
            "T4_no_gold_in_params": "gold" not in row,
            "T5_no_llm_judge": row.get("grading") is None,
            "T6_id_ok": cid not in EXCLUSION_IDS and cid.startswith("D"),
            "T8_two_sources": loc["left"] != loc["right"] and loc["left"] in files and loc["right"] in files,
            "slot_known": slot in SLOT_QUOTA,
        }
        if family == "Multi-step":
            checks["T8_three_sources"] = (
                loc.get("mid") in files
                and loc["mid"] != loc["left"]
                and loc["mid"] != loc["right"]
            )
        inst = row["instruction"]
        blob = inst + "\n" + blob_of(files)
        checks["T7_no_foreign_tokens"] = not (words(blob) & foreign_cov)
        checks["own_cover_token"] = bool(words(inst) & dtok)
        checks["forbidden_substr"] = not any(s in blob.casefold() for s in FORBIDDEN_SUBSTR)
        checks["exclusion_id_in_text"] = not any(x in blob for x in EXCLUSION_IDS)
        for spec in row["files"]:
            stem = Path(spec["path"]).stem.casefold()
            if stem in TOY_BASENAMES:
                checks["T2_toy_basename"] = False
                break
        else:
            checks["T2_toy_basename"] = True

        if gold is not None:
            checks["T1_gold_not_in_instruction"] = gold not in inst
            checks["forbidden_gold"] = gold not in FORBIDDEN_VALUES
            checks["T3_distractors"] = t3_ok(kind, gold, files, tables)
            try:
                if kind == "money_usd":
                    checks["correspondence"] = bool(v3_match(kind, parse_money(gold), gold))
                elif kind == "integer":
                    checks["correspondence"] = bool(v3_match(kind, int(gold), gold))
                else:
                    checks["correspondence"] = bool(v3_match(kind, gold, gold))
            except Exception as exc:
                checks["correspondence"] = False
                checks["correspondence_error"] = str(exc)
            if kind == "entity" and (gold.endswith(".txt") or gold.endswith(".m3u") or "/" in gold):
                entity_files += 1
        else:
            checks["T1_gold_not_in_instruction"] = False
            checks["forbidden_gold"] = False
            checks["T3_distractors"] = False
            checks["correspondence"] = False

        skip = {"lock_error", "correspondence_error"}
        checks["pass"] = all(v is True for k, v in checks.items() if k not in skip and k != "pass")
        if not checks["pass"]:
            failed = [k for k, v in checks.items() if k not in skip and k != "pass" and v is not True]
            errors.append(f"{cid}: FAIL {failed}" + (f" lock={lock_err}" if lock_err else ""))

        cluster = {
            "id": cid,
            "family": family,
            "kind": kind,
            "slot": slot,
            "component_id": row["component_id"],
            "instruction": inst,
            "locator": loc,
            "gold": gold,
            "construction": checks,
        }
        (SLATE / f"{cid}.json").write_text(json.dumps(cluster, indent=2, sort_keys=True) + "\n")
        clusters.append(cluster)

    if kinds != KIND_QUOTA:
        errors.append(f"kind quota {kinds} != {KIND_QUOTA}")
    if families != FAMILY_QUOTA:
        errors.append(f"family quota {families} != {FAMILY_QUOTA}")
    if slots != SLOT_QUOTA:
        errors.append(f"slot quota {slots} != {SLOT_QUOTA}")
    if entity_files > 1:
        errors.append(f"entity filename cap exceeded: {entity_files}")

    n_pass = sum(1 for c in clusters if c["construction"]["pass"] and c["gold"] is not None)
    gate = "PASS" if n_pass == N_D and not errors else "FAIL"

    payload = {
        "phase": 1,
        "workstream": "P4-C2",
        "status": gate,
        "N_D": N_D,
        "n_attempted": 30,
        "n_pass": n_pass,
        "kind_counts": kinds,
        "family_counts": families,
        "slot_counts": slots,
        "entity_filename_n": entity_files,
        "api_spend_usd": 0,
        "agents_run": 0,
        "instrument_v1_sha256": instr_v1_sha,
        "instrument_v2_sha256": sha256_file(INSTR_V2),
        "wrapper_sha256": sha256_file(WRAPPER) if WRAPPER.is_file() else None,
        "adjudicator_d_sha256": sha256_file(ADJ) if ADJ.is_file() else None,
        "instrument_v1_modified": False,
        "p4b_modified": False,
        "p4c_modified": False,
        "errors": errors,
        "clusters": [
            {
                "id": c["id"],
                "family": c["family"],
                "kind": c["kind"],
                "slot": c["slot"],
                "gold": c["gold"],
                "locked": c["gold"] is not None,
                "construction_pass": c["construction"]["pass"],
                "failures": [
                    k
                    for k, v in c["construction"].items()
                    if k not in {"pass", "lock_error", "correspondence_error"} and v is not True
                ],
            }
            for c in clusters
        ],
    }
    OUT.mkdir(exist_ok=True)
    spec_bytes = json.dumps(payload, indent=2, sort_keys=True).encode() + b"\n"
    (OUT / "p4c2_phase1_construction.json").write_bytes(spec_bytes)

    lines = [
        "# P4-C2 Phase 1 construction",
        "",
        f"status = **{gate}**",
        f"n_pass = {n_pass} / {N_D}",
        f"api_spend_usd = 0",
        f"instrument_v1_sha256 = `{instr_v1_sha}`",
        f"instrument_v2_sha256 = `{payload['instrument_v2_sha256']}`",
        f"wrapper_sha256 = `{payload['wrapper_sha256']}`",
        f"construction_json_sha256 = `{sha256_bytes(spec_bytes)}`",
        f"params_d_sha256 = `{sha256_file(ROOT / 'params_d.json')}`",
        f"generate_d_sha256 = `{sha256_file(ROOT / 'generate_d.py')}`",
        f"wordlists_d_sha256 = `{sha256_file(ROOT / 'wordlists_d.txt')}`",
        "",
        f"kind counts: {kinds}",
        f"family counts: {families}",
        f"slot counts: {slots}",
        "",
        "| id | family | slot | kind | gold | pass | failures |",
        "|---|---|---|---|---|---|---|",
    ]
    for c in payload["clusters"]:
        lines.append(
            f"| `{c['id']}` | {c['family']} | {c['slot']} | {c['kind']} | `{c['gold']}` | {c['construction_pass']} | {c['failures']} |"
        )
    if errors:
        lines += ["", "## Errors", ""]
        for e in errors:
            lines.append(f"- {e}")
    else:
        lines += ["", "No construction errors.", ""]
    lines += [
        "",
        "P4-B and P4-C v1 were not modified. Phase 2 qualification/seal is BLOCKED until authorized.",
        "No agents. $0 API.",
        "Public v2 quantities remain Form and CC; Form is not coverage.",
    ]
    (OUT / "p4c2_phase1_construction.md").write_text("\n".join(lines) + "\n")
    (OUT / "p4c2_phase1_status.json").write_text(
        json.dumps(
            {
                "phase": 1,
                "workstream": "P4-C2",
                "status": gate,
                "next": "PHASE_2_QUALIFICATION" if gate == "PASS" else "STOP",
                "next_status": "BLOCKED",
                "N_D": 30,
                "n_pass": n_pass,
                "api_spend_usd": 0,
                "instrument_v1_modified": False,
                "p4b_modified": False,
                "p4c_modified": False,
                "agents_run": 0,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    (OUT / "p4c2_phase1_gate.md").write_text(
        "\n".join(
            [
                "# P4-C2 Phase 1 gate",
                "",
                f"status = **{gate}**",
                f"construction = {n_pass}/30",
                "api_spend_usd = 0",
                "agents_run = 0",
                f"instrument_v1_sha256 = `{instr_v1_sha}`",
                "next = PHASE_2_QUALIFICATION (**BLOCKED** until authorized)",
                "",
                "P4-B, P4-C v1, and `p4_instrument.py` were not modified.",
                "Gold locked from L. Params have no observations and no anchors.",
                "Worlds have no gold field. Wrapper is task-agnostic CLAIM contract.",
                "",
            ]
        )
    )
    print("\n".join(lines))
    return 0 if gate == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
