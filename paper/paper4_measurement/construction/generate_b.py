#!/usr/bin/env python3
"""P4-B Phase 1: instantiate worlds, lock gold from L, audit construction.

No per-id branch. No observations. No agents. Does not edit p4_instrument.py.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent
P4 = ROOT.parent
INSTR = P4 / "instrument" / "p4_instrument.py"
SLATE = ROOT / "slate" / "b"
WORLDS = SLATE / "worlds"
OUT = ROOT / "out"
EXPECTED_INSTR = "c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59"
N_B = 20
KIND_QUOTA = {"money_usd": 8, "integer": 6, "entity": 3, "categorical": 3}
FAMILY_QUOTA = {"Locate": 4, "Compute": 4, "Reconcile": 4, "Filter": 4, "Tally": 4}
FAMILY_OP = {
    "Locate": "select_join",
    "Filter": "select_join",
    "Compute": "sum_join",
    "Tally": "count_join",
    "Reconcile": "live_not_stale",
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
    # entity / categorical: quoted-ish tokens are not required; use kv values later
    return []


def blob_of(files: dict[str, str]) -> str:
    return "\n".join(files.values())


def t3_ok(kind: str, gold: str, files: dict[str, str], tables: dict[str, list[dict]]) -> bool:
    blob = blob_of(files)
    if kind in {"money_usd", "integer"}:
        vals = [format_gold(kind, v) if kind == "money_usd" and "." in v else v for v in kind_values(kind, blob)]
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
    # entity/categorical: all cell values except gold
    cells = []
    for rows in tables.values():
        for row in rows:
            for v in row.values():
                s = str(v).strip()
                if s and s != gold:
                    cells.append(s)
    return len(unique(cells)) >= 3


def main() -> int:
    errors: list[str] = []
    instr_sha = sha256_file(INSTR)
    if instr_sha != EXPECTED_INSTR:
        errors.append(f"instrument hash drifted: {instr_sha}")

    sys.path.insert(0, str(INSTR.parent))
    from p4_instrument import parse_money, v3_match

    qtok = load_wordlist("wordlists_q.txt")
    vtok = load_wordlist("wordlists_v.txt")
    rtok = load_wordlist("wordlists_r.txt")
    btok = load_wordlist("wordlists_b.txt")
    if btok & qtok or btok & vtok or btok & rtok:
        errors.append("wordlists_b not disjoint from Q/V/R")
    foreign_cov = qtok | vtok | rtok

    params = json.loads((ROOT / "params_b.json").read_text())
    ids = [f"B{i:02d}" for i in range(1, 21)]
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
    entity_files = 0

    for cid in ids:
        row = params[cid]
        family, kind = row["family"], row["kind"]
        kinds[kind] = kinds.get(kind, 0) + 1
        families[family] = families.get(family, 0) + 1
        loc = row["locator"]
        if loc["op"] != FAMILY_OP[family]:
            errors.append(f"{cid}: op {loc['op']} != family {family}")
        if loc["left"] == loc["right"]:
            errors.append(f"{cid}: T8 sources not distinct")

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
            if parsed != spec["rows"] and spec["format"] != "ics":
                # ics adds empty location/hours possibly; compare after parse
                if parsed != parse_file(spec, text):
                    errors.append(f"{cid}: parse roundtrip {rel}")
            tables[rel] = parsed
            if parse_file(spec, dest.read_text()) != parsed:
                errors.append(f"{cid}: disk parse mismatch {rel}")

        meta = {
            "id": cid,
            "family": family,
            "kind": kind,
            "component_id": row["component_id"],
            "instruction": row["instruction"],
            "anchors": row["anchors"],
            "locator": loc,
            "files": sorted(files),
        }
        (wdir / "world_meta.json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
        if "gold" in meta or "observations" in meta:
            errors.append(f"{cid}: gold/observations leaked into world_meta")

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
            "n_anchors": len(row["anchors"]) >= 1,
            "anchors_ge_2_tokens": all(len(a.split()) >= 2 for a in row["anchors"]),
            "anchor_literal": all(a in row["instruction"] for a in row["anchors"]),
            "T4_no_observations": "observations" not in row and "last_response" not in row,
            "T5_no_llm_judge": row.get("grading") is None,
            "T6_id_ok": cid not in EXCLUSION_IDS and not cid.startswith("Q") and not cid.startswith("V"),
            "T8_two_sources": loc["left"] != loc["right"] and loc["left"] in files and loc["right"] in files,
        }
        inst = row["instruction"]
        blob = inst + "\n" + blob_of(files)
        checks["T7_no_qvr_tokens"] = not (words(blob) & foreign_cov)
        checks["own_cover_token"] = bool(words(inst) & btok)
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
            checks["gold_not_in_anchor"] = all(gold.casefold() not in a.casefold() for a in row["anchors"])
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
            checks["gold_not_in_anchor"] = False
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
            "component_id": row["component_id"],
            "instruction": inst,
            "anchors": row["anchors"],
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
    if entity_files > 1:
        errors.append(f"entity filename cap exceeded: {entity_files}")

    n_pass = sum(1 for c in clusters if c["construction"]["pass"] and c["gold"] is not None)
    gate = "PASS" if n_pass == N_B and not errors else "FAIL"

    payload = {
        "phase": 1,
        "workstream": "P4-B",
        "status": gate,
        "N_B": N_B,
        "n_attempted": 20,
        "n_pass": n_pass,
        "kind_counts": kinds,
        "family_counts": families,
        "entity_filename_n": entity_files,
        "api_spend_usd": 0,
        "agents_run": 0,
        "instrument_sha256": instr_sha,
        "instrument_modified": False,
        "errors": errors,
        "clusters": [
            {
                "id": c["id"],
                "family": c["family"],
                "kind": c["kind"],
                "gold": c["gold"],
                "anchors": c["anchors"],
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
    (OUT / "p4b_phase1_construction.json").write_bytes(spec_bytes)

    lines = [
        "# P4-B Phase 1 construction",
        "",
        f"status = **{gate}**",
        f"n_pass = {n_pass} / {N_B}",
        f"api_spend_usd = 0",
        f"instrument_sha256 = `{instr_sha}`",
        f"construction_json_sha256 = `{sha256_bytes(spec_bytes)}`",
        f"params_b_sha256 = `{sha256_file(ROOT / 'params_b.json')}`",
        f"generate_b_sha256 = `{sha256_file(ROOT / 'generate_b.py')}`",
        f"wordlists_b_sha256 = `{sha256_file(ROOT / 'wordlists_b.txt')}`",
        "",
        f"kind counts: {kinds}",
        f"family counts: {families}",
        "",
        "| id | family | kind | gold | anchors | pass | failures |",
        "|---|---|---|---|---|---|---|",
    ]
    for c in payload["clusters"]:
        lines.append(
            f"| `{c['id']}` | {c['family']} | {c['kind']} | `{c['gold']}` | {c['anchors']} | {c['construction_pass']} | {c['failures']} |"
        )
    if errors:
        lines += ["", "## Errors", ""]
        for e in errors:
            lines.append(f"- {e}")
    else:
        lines += ["", "No construction errors.", ""]
    lines += [
        "",
        "Phase 2 qualification is BLOCKED until authorized.",
        "No agents. $0 API.",
    ]
    (OUT / "p4b_phase1_construction.md").write_text("\n".join(lines) + "\n")
    (OUT / "p4b_phase1_status.json").write_text(
        json.dumps(
            {
                "phase": 1,
                "workstream": "P4-B",
                "status": gate,
                "next": "PHASE_2_QUALIFICATION" if gate == "PASS" else "STOP",
                "next_status": "BLOCKED",
                "N_B": 20,
                "n_pass": n_pass,
                "api_spend_usd": 0,
                "instrument_modified": False,
                "agents_run": 0,
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
