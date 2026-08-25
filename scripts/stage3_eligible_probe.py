#!/usr/bin/env python3
"""Stage 3: one-boot dummy guest, SELECT-only identifiability probes.

Frozen 10-task list. No Claude, no judge, no SQLite writes, no task swaps.
"""
from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path("/mnt/data2/Vinh/agent")
HARNESS = ROOT / "external/MyPCBench-main/agent-harness"
RESULTS = ROOT / "results"
OUT = ROOT / "out"
EMAIL = "michael.scott@dundermifflin.com"

TASKS = [
    ("retrieval-f001", "sample", "point_field", "dinoco-airlines.sqlite", "loyalty"),
    ("retrieval-f029", "sample", "point_field", "speedtax.sqlite", "tax_returns tax_documents tax_data"),
    ("retrieval-f030", "sample", "point_field", "speedtax.sqlite", "tax_returns tax_documents tax_data"),
    ("aggregation-f003", "sample", "aggregation", "speedtax.sqlite", "tax_returns"),
    ("aggregation-f018", "sample", "aggregation", "speedtax.sqlite", "tax_returns tax_documents tax_data"),
    ("preference_inference-f004", "sample", "multi_record", "tablefind.sqlite hangrydash.sqlite", "reservations restaurants orders"),
    ("preference_inference-f018", "sample", "multi_record", "batbucks.sqlite oddsmarket.sqlite", "holdings positions"),
    ("counterfactual-f004", "sample", "contradiction_cross_source", "vaultbank.sqlite speedtax.sqlite hoolicalendar.sqlite mail.sqlite", "transactions tax_documents events emails"),
    ("retrieval-f003", "reserve", "point_field", "speedtax.sqlite", "tax_returns tax_documents tax_data"),
    ("retrieval-f016", "reserve", "point_field", "batbucks.sqlite", "holdings portfolio"),
]

SCHEMA_DBS = [
    "dinoco-airlines.sqlite",
    "speedtax.sqlite",
    "tablefind.sqlite",
    "hangrydash.sqlite",
    "batbucks.sqlite",
    "oddsmarket.sqlite",
    "vaultbank.sqlite",
    "hoolicalendar.sqlite",
    "mail.sqlite",
]


def parse_jsonish(value):
    if value is None or value == "":
        return []
    if isinstance(value, (list, dict)):
        return value
    text = str(value).strip()
    if not text or text.startswith("ERROR"):
        return text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def compact(obj, limit=400):
    text = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    if len(text) > limit:
        return text[: limit - 3] + "..."
    return text


def guest_sh(env, command: str) -> dict:
    return env._execute_shell(command)


def guest_text(env, command: str) -> str:
    result = guest_sh(env, command)
    out = (result.get("output") or "") + (result.get("error") or "")
    return out.strip()


def dump_schema(env, db: str) -> str:
    return guest_text(env, f"sqlite3 /data/{db} '.tables' ; echo '---SCHEMA---' ; sqlite3 /data/{db} '.schema'")


def load_guest(task_id: str) -> dict:
    path = RESULTS / f"probe-{task_id}" / f"{task_id}.guest.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def extra_named(record: dict, db: str) -> list:
    found = []
    for ep in record.get("extra_probes") or []:
        if ep.get("db") == db:
            found.append(parse_jsonish(ep.get("result")))
    return found


def numbers_from_text(text: str) -> list[float]:
    if not text:
        return []
    found = []
    for match in re.findall(r"\$?([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?|[0-9]+(?:\.[0-9]+)?)", text):
        try:
            found.append(float(match.replace(",", "")))
        except ValueError:
            continue
    return found


def w2_from_docs(rows) -> dict:
    if not isinstance(rows, list):
        return {}
    for row in rows:
        blob = row.get("data_json") if isinstance(row, dict) else None
        if not blob:
            continue
        data = parse_jsonish(blob) if not isinstance(blob, dict) else blob
        if not isinstance(data, dict):
            continue
        lower = {str(k).lower(): v for k, v in data.items()}
        wages = lower.get("wages") or lower.get("box1") or lower.get("box_1") or lower.get("gross")
        employer = (
            lower.get("employer")
            or lower.get("employer_name")
            or lower.get("employername")
            or lower.get("company")
        )
        fed = (
            lower.get("federal_withholding")
            or lower.get("federal_tax_withheld")
            or lower.get("federal_income_tax_withheld")
            or lower.get("box2")
            or lower.get("box_2")
        )
        if wages is not None or employer is not None:
            return {"wages": wages, "employer": employer, "federal_withholding": fed, "raw": data}
    return {}


def fields_by_year(rows) -> dict:
    out = {}
    if not isinstance(rows, list):
        return out
    for row in rows:
        if not isinstance(row, dict):
            continue
        year = row.get("tax_year")
        name = str(row.get("field_name") or "").lower()
        val = row.get("field_value")
        out.setdefault(year, {})[name] = val
    return out


def classify(task_id: str, evidence_type: str, record: dict) -> dict:
    """Return determining_set, identifiable, pre_gold, probe_result, status, reason."""
    if not record:
        return {
            "determining_set": "NA",
            "identifiable": "unknown",
            "pre_gold": "NA",
            "probe_result": "no guest.json",
            "status": "technical_failure",
            "reason_if_rejected": "VM/API/schema dump failed; no guest.json",
        }

    probe = parse_jsonish(record.get("probe_before"))
    extras = record.get("extra_probes") or []
    files = record.get("files") or {}

    if task_id == "retrieval-f001":
        row = probe[0] if isinstance(probe, list) and probe else {}
        status = row.get("status")
        miles = row.get("miles")
        unique = bool(status) and miles is not None
        d = "dinoco-airlines.sqlite loyalty.{status,miles,miles_ytd}"
        gold = f"status={status} miles={miles} miles_ytd={row.get('miles_ytd')}"
        return {
            "determining_set": d,
            "identifiable": "true" if unique else "false",
            "pre_gold": gold,
            "probe_result": compact(probe),
            "status": "identifiable" if unique else "rejected_not_identifiable",
            "reason_if_rejected": "" if unique else "no unique loyalty tier+miles row",
        }

    if task_id in ("retrieval-f029", "retrieval-f003"):
        docs = probe if isinstance(probe, list) else []
        tax_data_rows = []
        for ep in extras:
            parsed = parse_jsonish(ep.get("result"))
            if isinstance(parsed, list) and parsed and "field_name" in (parsed[0] or {}):
                tax_data_rows = parsed
        w2 = w2_from_docs(docs)
        by_year = fields_by_year(tax_data_rows)
        file_txt = files.get("~/Documents/Tax_2025/w2_summary.txt", "")
        file_nums = numbers_from_text(file_txt)
        # Most-recent: highest tax_year in docs; for f003 only filed (query already filters).
        years = [r.get("tax_year") for r in docs if isinstance(r, dict) and r.get("tax_year") is not None]
        latest = max(years) if years else None
        latest_fields = by_year.get(latest, {})
        wages = w2.get("wages") or latest_fields.get("wages") or latest_fields.get("w2_wages") or latest_fields.get("box1_wages")
        employer = w2.get("employer") or latest_fields.get("employer") or latest_fields.get("employer_name")
        fed = w2.get("federal_withholding") or latest_fields.get("federal_withholding") or latest_fields.get("federal_tax_withheld")
        if wages is None:
            for key, val in latest_fields.items():
                if "wage" in key or key in ("box1", "box_1"):
                    wages = val
                    break
        if employer is None:
            for key, val in latest_fields.items():
                if "employer" in key:
                    employer = val
                    break
        if fed is None:
            for key, val in latest_fields.items():
                if "federal" in key and "withhold" in key:
                    fed = val
                    break
        employer_s = str(employer or "")
        dunder = "dunder mifflin" in employer_s.lower() or "dunder mifflin" in file_txt.lower()
        sqlite_nums = [float(x) for x in (wages, fed) if x is not None]
        try:
            sqlite_nums = [float(str(x).replace(",", "").replace("$", "")) for x in sqlite_nums]
        except ValueError:
            pass
        agree = False
        if sqlite_nums and file_nums:
            agree = any(abs(a - b) < 0.02 for a in sqlite_nums for b in file_nums)
        gold = (
            f"year={latest} wages={wages} employer={employer_s or 'NA'} "
            f"fed_wh={fed} file_agree={agree}"
        )
        if task_id == "retrieval-f003":
            unique = wages is not None
            refunds = [r.get("federal_refund_amount") for r in docs if isinstance(r, dict)]
            same_as_refund = False
            try:
                same_as_refund = wages is not None and any(
                    abs(float(wages) - float(r)) < 0.02 for r in refunds if r is not None
                )
            except (TypeError, ValueError):
                same_as_refund = False
            d = "speedtax.sqlite tax_documents.data_json.wages on max filed tax_year (not refund)"
            if not unique:
                return {
                    "determining_set": d,
                    "identifiable": "false",
                    "pre_gold": gold,
                    "probe_result": compact({"docs": docs[:4], "fields": latest_fields}),
                    "status": "rejected_not_identifiable",
                    "reason_if_rejected": "no unique prior-year filed W-2 wages figure",
                }
            note = "wages currently equal refund" if same_as_refund else ""
            return {
                "determining_set": d,
                "identifiable": "true",
                "pre_gold": gold,
                "probe_result": compact({"wages": wages, "employer": employer_s, "refunds": refunds, "note": note}),
                "status": "identifiable",
                "reason_if_rejected": "",
            }
        d = "speedtax.sqlite tax_documents.data_json.{wages,employer_name,federal_tax_withheld} AND Files Tax_2025/w2_summary.txt"
        reasons = []
        status = "identifiable"
        ident = "true"
        if dunder:
            status = "confounded"
            ident = "true"
            reasons.append("rubric names Dunder Mifflin; live employer/file currently match that pin")
        if agree:
            status = "confounded"
            ident = "true"
            reasons.append("Files and SQLite currently agree (dual-channel gold); sqlite-only CF may be silent if agent reads the file")
        if wages is None:
            status = "rejected_not_identifiable"
            ident = "false"
            reasons = ["no unique live W-2 wages figure"]
        return {
            "determining_set": d,
            "identifiable": ident,
            "pre_gold": gold,
            "probe_result": compact({"w2": w2 or latest_fields, "file_head": file_txt[:240], "agree": agree}),
            "status": status,
            "reason_if_rejected": "; ".join(reasons) if status != "identifiable" else "",
        }

    if task_id == "retrieval-f030":
        docs = probe if isinstance(probe, list) else []
        tax_data_rows = []
        for ep in extras:
            parsed = parse_jsonish(ep.get("result"))
            if isinstance(parsed, list):
                tax_data_rows.extend([r for r in parsed if isinstance(r, dict)])
        file_txt = files.get("~/Documents/Tax_2025/1099s.txt", "")
        years = [r.get("tax_year") for r in docs if isinstance(r, dict) and r.get("tax_year") is not None]
        latest = max(years) if years else None
        amount = payer = charitable = None
        latest_docs = [r for r in docs if isinstance(r, dict) and r.get("tax_year") == latest] or docs
        for row in latest_docs:
            blob = parse_jsonish(row.get("data_json")) if isinstance(row, dict) else None
            if isinstance(blob, dict):
                lower = {str(k).lower(): v for k, v in blob.items()}
                amount = amount or lower.get("nonemployee_compensation") or lower.get("amount") or lower.get("income") or lower.get("compensation")
                payer = payer or lower.get("payer_name") or lower.get("payer") or lower.get("name")
        latest_td = [r for r in tax_data_rows if isinstance(r, dict) and r.get("tax_year") == latest] or tax_data_rows
        for row in latest_td:
            name = str(row.get("field_name") or "").lower()
            val = row.get("field_value")
            if ("1099" in name and any(k in name for k in ("amount", "income", "comp"))) and amount is None:
                amount = val
            if ("payer" in name) and payer is None:
                payer = val
            if "charit" in name and charitable is None:
                charitable = val
        payer_s = str(payer or "")
        pinned = "scranton improv" in payer_s.lower() or "scranton improv" in file_txt.lower()
        file_nums = numbers_from_text(file_txt)
        agree = False
        try:
            if amount is not None and file_nums:
                agree = any(abs(float(str(amount).replace(",", "").replace("$", "")) - b) < 0.02 for b in file_nums)
        except ValueError:
            agree = False
        gold = f"year={latest} 1099_amount={amount} payer={payer_s or 'NA'} charitable={charitable} file_agree={agree}"
        d = "speedtax.sqlite tax_documents.data_json.{nonemployee_compensation,payer_name} + tax_data.charitable_total AND Files Tax_2025/1099s.txt"
        reasons = []
        status = "identifiable"
        ident = "true"
        if pinned:
            status = "confounded"
            reasons.append("rubric names Scranton Improv Academy; live payer/file currently match that pin")
        if agree:
            status = "confounded"
            reasons.append("Files and SQLite currently agree (dual-channel gold)")
        if amount is None and charitable is None:
            status = "rejected_not_identifiable"
            ident = "false"
            reasons = ["no unique live 1099 amount or charitable total"]
        return {
            "determining_set": d,
            "identifiable": ident,
            "pre_gold": gold,
            "probe_result": compact({"docs": docs[:4], "tax_data": tax_data_rows[:12], "file_head": file_txt[:240]}),
            "status": status,
            "reason_if_rejected": "; ".join(reasons) if status != "identifiable" else "",
        }

    if task_id == "aggregation-f003":
        rows = probe if isinstance(probe, list) else []
        extra = parse_jsonish(extras[0]["result"]) if extras else []
        n_filed_extra = extra[0].get("n_filed") if isinstance(extra, list) and extra and isinstance(extra[0], dict) else None
        filed = [r for r in rows if isinstance(r, dict) and str(r.get("status") or "").lower() == "filed"]
        inprog = [r for r in rows if isinstance(r, dict) and str(r.get("status") or "").lower() != "filed"]
        current = None
        if inprog:
            current = min(r.get("tax_year") for r in inprog if r.get("tax_year") is not None)
        elif rows:
            current = max(r.get("tax_year") for r in rows if r.get("tax_year") is not None)
        prior = [r for r in filed if current is None or (r.get("tax_year") is not None and r["tax_year"] < current)]
        n_filed = len(prior)
        combined = 0.0
        for r in prior:
            combined += float(r.get("federal_refund_amount") or 0) + float(r.get("state_refund_amount") or 0)
        gold = (
            f"n_filed={n_filed} current_year={current} combined_refund={combined:.2f} "
            f"filed_years={[r.get('tax_year') for r in prior]}"
        )
        d = "speedtax.sqlite tax_returns[status=filed, tax_year<current].{federal_refund_amount,state_refund_amount}"
        if n_filed < 2:
            return {
                "determining_set": d,
                "identifiable": "false",
                "pre_gold": gold,
                "probe_result": compact({"returns": rows, "n_filed_sql": n_filed_extra}),
                "status": "rejected_not_identifiable",
                "reason_if_rejected": f"n_filed={n_filed}<2; point lookup, not aggregation",
            }
        return {
            "determining_set": d,
            "identifiable": "true",
            "pre_gold": gold,
            "probe_result": compact({"returns": rows, "n_filed_sql": n_filed_extra, "combined": combined}),
            "status": "identifiable",
            "reason_if_rejected": "",
        }

    if task_id == "aggregation-f018":
        rows = probe if isinstance(probe, list) else []
        docs = parse_jsonish(extras[0]["result"]) if extras else []
        w2_txt = files.get("~/Documents/Tax_2025/w2_summary.txt", "")
        n1099_txt = files.get("~/Documents/Tax_2025/1099s.txt", "")
        fields = {str(r.get("field_name") or "").lower(): r.get("field_value") for r in rows if isinstance(r, dict)}
        line = {
            "charitable": fields.get("charitable_total") or fields.get("charitable_contributions"),
            "home_office_days": fields.get("home_office_days"),
            "1099_amount": fields.get("1099_amount_0"),
            "1099_payer": fields.get("1099_payer_0"),
            "w2_gross": fields.get("w2_gross_wages"),
            "w2_fed_wh": fields.get("w2_federal_withheld"),
            "w2_state_wh": fields.get("w2_state_withheld"),
            "w2_employer": fields.get("w2_employer"),
        }
        w2_norm = w2_txt.replace(",", "")
        n1099_norm = n1099_txt.replace(",", "")
        w2_match = bool(line["w2_gross"]) and str(line["w2_gross"]).split(".")[0] in w2_norm and bool(line["w2_fed_wh"]) and str(line["w2_fed_wh"]).split(".")[0] in w2_norm
        n1099_match = bool(line["1099_amount"]) and str(line["1099_amount"]).split(".")[0] in n1099_norm
        payer_in_file = "scranton improv" in n1099_txt.lower()
        char_in_file = bool(line.get("charitable")) and str(line["charitable"]) in (w2_txt + n1099_txt)
        home_in_file = bool(line.get("home_office_days")) and str(line["home_office_days"]) in (w2_txt + n1099_txt)
        match = w2_match and n1099_match
        gold = (
            f"charitable={line['charitable']} home_office_days={line['home_office_days']} "
            f"1099={line['1099_amount']}/{line['1099_payer']} w2={line['w2_gross']}/"
            f"fed_wh={line['w2_fed_wh']}/state_wh={line['w2_state_wh']} "
            f"files_match_w2={w2_match} files_match_1099={n1099_match} "
            f"charitable_in_files={char_in_file} home_office_in_files={home_in_file}"
        )
        d = "speedtax.sqlite TY2025 {charitable,home-office,1099,W-2} AND Files Tax_2025/{w2_summary.txt,1099s.txt}"
        if not fields and not docs:
            return {
                "determining_set": d,
                "identifiable": "false",
                "pre_gold": gold,
                "probe_result": compact({"fields": fields, "docs": docs, "files": {k: v[:120] for k, v in files.items()}}),
                "status": "rejected_not_identifiable",
                "reason_if_rejected": "no TY2025 line items in sqlite",
            }
        if match:
            return {
                "determining_set": d,
                "identifiable": "true",
                "pre_gold": gold,
                "probe_result": compact({"line": line, "w2_match": w2_match, "n1099_match": n1099_match, "payer_in_file": payer_in_file}),
                "status": "confounded",
                "reason_if_rejected": "W-2 and 1099 currently match Tax_2025 files (dual-channel gold); sqlite-only CF on those lines would be silent if the agent reads the files. Charitable and home-office days are sqlite-only.",
            }
        return {
            "determining_set": d,
            "identifiable": "true",
            "pre_gold": gold,
            "probe_result": compact({"line": line, "w2_match": w2_match, "n1099_match": n1099_match, "docs": docs}),
            "status": "identifiable",
            "reason_if_rejected": "",
        }

    if task_id == "preference_inference-f004":
        tf = probe if isinstance(probe, list) else []
        hd = parse_jsonish(extras[0]["result"]) if extras else []
        tf_top = tf[0]["name"] if tf and isinstance(tf[0], dict) else None
        hd_top = hd[0]["name"] if hd and isinstance(hd[0], dict) else None
        tf_n = sum(int(r.get("n") or 0) for r in tf if isinstance(r, dict))
        hd_n = sum(int(r.get("n") or 0) for r in hd if isinstance(r, dict))
        split = "dine-out" if tf_n > hd_n else ("delivery" if hd_n > tf_n else "tie")
        coopers = hd_top is not None and "cooper" in str(hd_top).lower()
        tf_flip = len(tf) >= 2 and int(tf[0].get("n") or 0) != int(tf[1].get("n") or 0)
        hd_flip = isinstance(hd, list) and len(hd) >= 2 and int(hd[0].get("n") or 0) != int(hd[1].get("n") or 0)
        gold = (
            f"tablefind_top={tf_top} n={tf[0].get('n') if tf else None} "
            f"hangrydash_top={hd_top} n={hd[0].get('n') if hd else None} "
            f"split={split} tf_total={tf_n} hd_total={hd_n} coopers_hd_top={coopers}"
        )
        d = "tablefind.sqlite reservations counts (top 5) AND hangrydash.sqlite orders counts (top 5)"
        if not tf or not hd:
            return {
                "determining_set": d,
                "identifiable": "false",
                "pre_gold": gold,
                "probe_result": compact({"tablefind": tf[:5], "hangrydash": hd[:5]}),
                "status": "rejected_not_identifiable",
                "reason_if_rejected": "missing TableFind or HangryDash ranking",
            }
        if not (tf_flip or hd_flip) and tf_n == hd_n:
            return {
                "determining_set": d,
                "identifiable": "false",
                "pre_gold": gold,
                "probe_result": compact({"tablefind": tf[:5], "hangrydash": hd[:5]}),
                "status": "rejected_not_identifiable",
                "reason_if_rejected": "split and both tops cannot be flipped independently on this seed",
            }
        if coopers:
            return {
                "determining_set": d,
                "identifiable": "true",
                "pre_gold": gold,
                "probe_result": compact({"tablefind": tf[:5], "hangrydash": hd[:5], "flip_tf": tf_flip, "flip_hd": hd_flip}),
                "status": "confounded",
                "reason_if_rejected": "rubric names Cooper's Seafood House as HangryDash top; live ranking currently matches that pin",
            }
        return {
            "determining_set": d,
            "identifiable": "true",
            "pre_gold": gold,
            "probe_result": compact({"tablefind": tf[:5], "hangrydash": hd[:5]}),
            "status": "identifiable" if not coopers else "confounded",
            "reason_if_rejected": "" if not coopers else "rubric names Cooper's Seafood House as HangryDash top",
        }

    if task_id == "preference_inference-f018":
        gme = probe if isinstance(probe, list) else []
        om = parse_jsonish(extras[0]["result"]) if extras else []
        gme_ok = isinstance(gme, list) and any(str(r.get("ticker") or "").upper() == "GME" for r in gme if isinstance(r, dict))
        yes = []
        if isinstance(om, list):
            for r in om:
                if not isinstance(r, dict):
                    continue
                side = str(r.get("side") or "").upper()
                title = str(r.get("title") or "")
                if side in ("YES", "Y") and ("100" in title or "above" in title.lower() or "gamestop" in title.lower()):
                    yes.append(r)
                elif side in ("YES", "Y"):
                    yes.append(r)
        gold = f"gme={compact(gme)} odds={compact(om)}"
        d = "batbucks.sqlite holdings GME.{shares,avg_cost} AND oddsmarket.sqlite GameStop-above-$100 YES"
        if not gme_ok or not yes:
            missing = []
            if not gme_ok:
                missing.append("BatBucks GME holding")
            if not yes:
                missing.append("OddsMarket GameStop-above-$100 YES")
            return {
                "determining_set": d,
                "identifiable": "false",
                "pre_gold": gold,
                "probe_result": compact({"gme": gme, "odds": om}),
                "status": "rejected_not_identifiable",
                "reason_if_rejected": "missing " + " and ".join(missing),
            }
        return {
            "determining_set": d,
            "identifiable": "true",
            "pre_gold": gold,
            "probe_result": compact({"gme": gme, "yes": yes}),
            "status": "identifiable",
            "reason_if_rejected": "",
        }

    if task_id == "counterfactual-f004":
        charges = probe if isinstance(probe, list) else []
        docs = tax_data = events = mail = []
        for ep in extras:
            parsed = parse_jsonish(ep.get("result"))
            db = ep.get("db")
            if db == "speedtax.sqlite" and isinstance(parsed, list) and parsed:
                if "field_name" in (parsed[0] or {}):
                    tax_data = parsed
                else:
                    docs = parsed
            elif db == "hoolicalendar.sqlite":
                events = parsed if isinstance(parsed, list) else []
            elif db == "mail.sqlite":
                mail = parsed if isinstance(parsed, list) else []
        pays = False
        for r in charges:
            try:
                amt = float(r.get("amount") or 0)
            except (TypeError, ValueError):
                amt = 0
            if amt < 0 or str(r.get("category") or "").lower() in ("education", "entertainment", "tuition"):
                pays = True
            if amt != 0:
                pays = True
        has_1099 = False
        for row in list(docs) + list(tax_data):
            blob = json.dumps(row).lower()
            if "improv" in blob or "1099" in blob:
                has_1099 = True
        gold = (
            f"gringotts_n={len(charges)} pays={pays} has_1099={has_1099} "
            f"1099_ty2025=1200 calendar_improv_n={len(events)} mail_improv_n={len(mail)}"
        )
        d = "vaultbank.sqlite improv transactions AND speedtax 1099 AND hoolicalendar improv events AND mail improv threads"
        if pays and has_1099:
            return {
                "determining_set": d,
                "identifiable": "true",
                "pre_gold": gold,
                "probe_result": compact({"charges": charges[:8], "docs": docs[:4], "tax_data": tax_data[:8], "events": events[:6], "mail": mail[:6]}),
                "status": "identifiable",
                "reason_if_rejected": "",
            }
        return {
            "determining_set": d,
            "identifiable": "false",
            "pre_gold": gold,
            "probe_result": compact({"charges": charges[:8], "docs": docs[:4], "tax_data": tax_data[:8], "events": events[:6], "mail": mail[:6]}),
            "status": "rejected_not_identifiable",
            "reason_if_rejected": "student-vs-teacher signals currently do not conflict (need pay tuition AND receive 1099)",
        }

    if task_id == "retrieval-f016":
        holdings = probe if isinstance(probe, list) else []
        total = None
        cash = None
        for ep in extras:
            parsed = parse_jsonish(ep.get("result"))
            if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict):
                if "cost_basis_total" in parsed[0]:
                    total = parsed[0]["cost_basis_total"]
                if "cash" in parsed[0]:
                    cash = parsed[0]["cash"]
        if total is None and holdings:
            try:
                total = sum(float(r.get("cost_basis") or 0) for r in holdings if isinstance(r, dict))
            except (TypeError, ValueError):
                total = None
        gold = f"cost_basis_total={total} cash={cash} holdings={compact(holdings)}"
        d = "batbucks.sqlite holdings sum(shares*avg_cost) AND portfolio.cash"
        unique = total is not None and cash is not None
        return {
            "determining_set": d,
            "identifiable": "true" if unique else "false",
            "pre_gold": gold,
            "probe_result": compact({"holdings": holdings, "total": total, "cash": cash}),
            "status": "identifiable" if unique else "rejected_not_identifiable",
            "reason_if_rejected": "" if unique else "missing unique cost-basis total or cash",
        }

    return {
        "determining_set": "NA",
        "identifiable": "unknown",
        "pre_gold": "NA",
        "probe_result": compact(record)[:400],
        "status": "technical_failure",
        "reason_if_rejected": "unhandled task in classifier",
    }


def write_results(rows: list[dict]) -> None:
    cols = [
        "task_id",
        "role",
        "evidence_type",
        "determining_set",
        "identifiable",
        "pre_gold",
        "probe_result",
        "status",
        "reason_if_rejected",
    ]
    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / "evidence_probe_results.csv"
    with csv_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore", quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in cols})

    counts = {"identifiable": 0, "rejected_not_identifiable": 0, "confounded": 0, "technical_failure": 0}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1

    md = []
    md.append("# Stage 3 identifiability probes")
    md.append("")
    md.append(
        "Stage 1–2 screening is frozen; this table is Stage 3 probes only; $0 Claude."
    )
    md.append("")
    md.append("| " + " | ".join(cols) + " |")
    md.append("| " + " | ".join("---" for _ in cols) + " |")
    for row in rows:
        cells = []
        for k in cols:
            val = str(row.get(k, "")).replace("|", "\\|").replace("\n", " ")
            cells.append(val)
        md.append("| " + " | ".join(cells) + " |")
    md.append("")
    md.append(
        f"Counts: n identifiable = {counts['identifiable']}; "
        f"n rejected_not_identifiable = {counts['rejected_not_identifiable']}; "
        f"n confounded = {counts['confounded']}; "
        f"n technical_failure = {counts['technical_failure']}."
    )
    md.append("")
    md.append(
        "The confirmatory sample is still these 8 ids "
        "(retrieval-f001, retrieval-f029, retrieval-f030, aggregation-f003, "
        "aggregation-f018, preference_inference-f004, preference_inference-f018, "
        "counterfactual-f004), including any that were rejected or confounded. "
        "Reserves retrieval-f003 and retrieval-f016 were not promoted."
    )
    md.append("")
    (OUT / "evidence_probe_results.md").write_text("\n".join(md) + "\n")
    print(f"wrote {csv_path}")
    print(f"wrote {OUT / 'evidence_probe_results.md'}")
    print(
        f"counts identifiable={counts['identifiable']} "
        f"rejected={counts['rejected_not_identifiable']} "
        f"confounded={counts['confounded']} "
        f"technical_failure={counts['technical_failure']}"
    )


def boot_env():
    sys.path.insert(0, str(HARNESS))
    from env import MyPCBenchEnv

    qcow2 = os.environ.get("MYPCBENCH_QCOW2")
    if not qcow2:
        raise SystemExit("MYPCBENCH_QCOW2 is not set")
    env = MyPCBenchEnv(
        backend="qemu",
        qcow2_path=qcow2,
        headless=True,
        persona="michael_scott",
        container_name=f"mypcbench-stage3-{os.getpid()}",
    )
    print(f"reset() starting; Control API will bind 127.0.0.1; qcow2={qcow2}", flush=True)
    env.reset()
    print(f"guest ready at {env.base_url}", flush=True)
    return env


def probe_all(env) -> list[dict]:
    python = sys.executable
    inject = ROOT / "scripts/cf_inject.py"
    schema_cache = {}
    for db in SCHEMA_DBS:
        print(f"schema {db}", flush=True)
        schema_cache[db] = dump_schema(env, db)

    home_ls = guest_text(env, "ls -la /home; echo '---'; find /home -name 'w2_summary.txt' -o -name '1099s.txt' 2>/dev/null")
    print(home_ls[:1500], flush=True)

    rows = []
    for task_id, role, evidence_type, dbs, _tables in TASKS:
        dest = RESULTS / f"probe-{task_id}"
        dest.mkdir(parents=True, exist_ok=True)
        schema_txt = []
        for db in dbs.split():
            schema_txt.append(f"===== {db} =====\n{schema_cache.get(db, 'MISSING')}\n")
        if "speedtax" in dbs or task_id.startswith("retrieval-f02") or task_id in ("aggregation-f018",):
            schema_txt.append(f"===== Tax_2025 files =====\n{home_ls}\n")
        (dest / "schema.txt").write_text("\n".join(schema_txt))
        print(f"cf_inject --probe-only {task_id}", flush=True)
        proc = subprocess.run(
            [
                python,
                str(inject),
                "--api",
                env.base_url,
                "--task",
                task_id,
                "--probe-only",
                "--out",
                str(dest),
            ],
            capture_output=True,
            text=True,
        )
        print(proc.stdout[-2000:] if proc.stdout else "", flush=True)
        if proc.returncode != 0:
            print(proc.stderr[-2000:] if proc.stderr else "", flush=True)
            fail_path = dest / f"{task_id}.guest.json"
            if not fail_path.exists():
                fail_path.write_text(
                    json.dumps(
                        {
                            "id": task_id,
                            "mode": "probe-only",
                            "error": proc.stderr or proc.stdout,
                            "returncode": proc.returncode,
                        },
                        indent=2,
                    )
                    + "\n"
                )
        record = load_guest(task_id)
        classified = classify(task_id, evidence_type, record)
        row = {
            "task_id": task_id,
            "role": role,
            "evidence_type": evidence_type,
            **classified,
        }
        rows.append(row)
        print(f"  status={row['status']} identifiable={row['identifiable']} pre_gold={row['pre_gold'][:180]}", flush=True)
    return rows


def classify_from_dumps() -> list[dict]:
    rows = []
    for task_id, role, evidence_type, _dbs, _tables in TASKS:
        record = load_guest(task_id)
        classified = classify(task_id, evidence_type, record)
        rows.append({"task_id": task_id, "role": role, "evidence_type": evidence_type, **classified})
        print(f"{task_id} status={classified['status']} pre_gold={classified['pre_gold'][:220]}", flush=True)
    return rows


def main() -> int:
    if "--from-dumps" in sys.argv:
        write_results(classify_from_dumps())
        return 0

    os.environ["MYPCBENCH_CF_PROBE_ONLY"] = "1"
    os.environ.pop("MYPCBENCH_CF_TASK", None)
    os.environ.pop("ANTHROPIC_API_KEY", None)
    os.environ.pop("OPENAI_API_KEY", None)
    RESULTS.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    pilot = ROOT / "results/base-retrieval-f001/retrieval-f001.guest.json"
    dest_f001 = RESULTS / "probe-retrieval-f001"
    dest_f001.mkdir(parents=True, exist_ok=True)
    if pilot.exists():
        (dest_f001 / "pilot-retrieval-f001.guest.json").write_text(pilot.read_text())

    env = None
    try:
        env = boot_env()
        rows = probe_all(env)
    except Exception as exc:
        print(f"TECHNICAL FAILURE during boot/dump: {exc!r}", flush=True)
        rows = []
        for task_id, role, evidence_type, _dbs, _tables in TASKS:
            dest = RESULTS / f"probe-{task_id}"
            dest.mkdir(parents=True, exist_ok=True)
            existing = load_guest(task_id)
            if existing:
                classified = classify(task_id, evidence_type, existing)
            else:
                classified = {
                    "determining_set": "NA",
                    "identifiable": "unknown",
                    "pre_gold": "NA",
                    "probe_result": repr(exc),
                    "status": "technical_failure",
                    "reason_if_rejected": f"VM/API/schema dump failed: {exc}",
                }
                (dest / f"{task_id}.guest.json").write_text(
                    json.dumps({"id": task_id, "mode": "probe-only", "error": repr(exc)}, indent=2) + "\n"
                )
            rows.append({"task_id": task_id, "role": role, "evidence_type": evidence_type, **classified})
    finally:
        if env is not None:
            try:
                env.close()
            except Exception as close_exc:
                print(f"env.close() warning: {close_exc!r}", flush=True)

    write_results(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
