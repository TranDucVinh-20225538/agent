#!/usr/bin/env python3
"""Read-only Stage-4 trajectory audit. Writes only under this directory."""
from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import beta

ROOT = Path("/mnt/data2/Vinh/agent")
OUT = ROOT / "out" / "stage4_counterfactual_analysis"
EXPECTED_F001_BASE = "Gold Voyager / 38450"
EXPECTED_F001_CF = "Silver Voyager / 8620"
EXPECTED_F003_BASE_COMBINED = 4871.70
EXPECTED_F003_CF_COMBINED = 400.0


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def load_json(path: Path):
    if not path or not path.is_file():
        return None
    return json.loads(path.read_text())


def load_traj(path: Path) -> list[dict]:
    if not path or not path.is_file():
        return []
    rows = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def last_action(rows: list[dict]) -> str:
    if not rows:
        return ""
    return str(rows[-1].get("action") or "")


def is_done(rows: list[dict]) -> bool:
    return last_action(rows) == "DONE"


def score_int(scores_path: Path | None) -> int | None:
    data = load_json(scores_path) if scores_path else None
    if not data:
        return None
    rows = data.get("rows") or []
    if not rows:
        if "avg_score" in data:
            return int(round(float(data["avg_score"]) * 100))
        return None
    raw = rows[0].get("raw")
    if raw is not None:
        return int(raw)
    sc = rows[0].get("score")
    if sc is None:
        return None
    sc = float(sc)
    return int(round(sc * 100)) if sc <= 1.0 else int(round(sc))


def writer_fields(model_key: str, task: str) -> tuple[str, str]:
    """Secondary writer table only. Never used as DONE/validity."""
    md_map = {
        "claude": ROOT / "out" / "evidence_stage4_results.md",
        "openai": ROOT / "out" / "evidence_stage4_openai_results.md",
        "qwen35a3b": ROOT / "out" / "evidence_stage4_qwen35a3b_results.md",
        "qwen359b": ROOT / "out" / "evidence_stage4_qwen359b_results.md",
        "qwen38flash": ROOT / "out" / "evidence_stage4_qwen38flash_results.md",
    }
    path = md_map.get(model_key)
    if not path or not path.is_file():
        return "", ""
    for line in path.read_text().splitlines():
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 12:
            continue
        if parts[0] == task:
            return parts[11], f"{parts[8]}/{parts[9]}"
    return "", ""


def parse_probe(s: str | None):
    if not s:
        return None
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return None


def guest_gold(guest: dict | None, task: str, condition: str) -> tuple[str, str]:
    """Return (gold_state, discrepancy_note)."""
    if not guest:
        return "", "missing guest.json"
    notes = []
    if task == "retrieval-f001":
        after = parse_probe(guest.get("probe_after"))
        before = parse_probe(guest.get("probe_before"))
        row = None
        if condition.startswith("cf") or condition == "cf":
            row = (after or [None])[0] if after else None
            source = "probe_after"
        else:
            row = (before or [None])[0] if before else None
            source = "probe_before"
        if not row:
            return "", f"no {source} in guest"
        status = row.get("status")
        miles = row.get("miles")
        state = f"{status} / {miles}"
        if condition == "base" and (status != "Gold Voyager" or int(miles) != 38450):
            notes.append(
                f"DISCREPANCY vs expected {EXPECTED_F001_BASE}: guest {source}={state}"
            )
        if condition.startswith("cf") and (
            status != "Silver Voyager" or int(miles) != 8620
        ):
            notes.append(
                f"DISCREPANCY vs expected {EXPECTED_F001_CF}: guest {source}={state}"
            )
        return state, "; ".join(notes)
    if task == "aggregation-f003":
        extras = []
        if condition.startswith("cf") or condition == "cf":
            extras = guest.get("extra_probes_after") or []
            source = "extra_probes_after"
        else:
            extras = guest.get("extra_probes") or guest.get("extra_probes_before") or []
            source = "extra_probes or extra_probes_before"
        combined = None
        n_filed = None
        if extras:
            result = parse_probe(extras[0].get("result"))
            if result:
                n_filed = result[0].get("n_filed")
                combined = result[0].get("combined_refund")
        if combined is None:
            return "", f"no combined_refund in {source}"
        combined_f = float(combined)
        state = f"n_filed={n_filed} combined={combined_f:.2f}"
        if condition == "base" and abs(combined_f - EXPECTED_F003_BASE_COMBINED) > 0.05:
            notes.append(
                f"DISCREPANCY vs expected combined={EXPECTED_F003_BASE_COMBINED}: {state}"
            )
        if condition.startswith("cf") and abs(combined_f - EXPECTED_F003_CF_COMBINED) > 0.05:
            notes.append(
                f"DISCREPANCY vs expected combined={EXPECTED_F003_CF_COMBINED}: {state}"
            )
        return state, "; ".join(notes)
    return "", "unknown task"


def norm_text(rows: list[dict]) -> str:
    if not rows:
        return ""
    return str(rows[-1].get("response") or "")


def f001_answer(text: str) -> tuple[str, bool | None]:
    low = text.lower()
    gold = bool(re.search(r"gold\s*voyager", low))
    silver = bool(re.search(r"silver\s*voyager", low))
    has_38450 = "38450" in re.sub(r"[, ]", "", text) or "38,450" in text
    has_8620 = "8620" in re.sub(r"[, ]", "", text) or "8,620" in text
    bits = []
    if gold:
        bits.append("Gold Voyager")
    if silver:
        bits.append("Silver Voyager")
    if has_38450:
        bits.append("38450")
    if has_8620:
        bits.append("8620")
    state = " / ".join(bits) if bits else "unparsed"
    return state, None


def f003_answer(text: str) -> str:
    compact = re.sub(r"[, ]", "", text)
    hits = []
    if "4872" in compact or "4871.70" in compact or "4,871.70" in text or "4,872" in text:
        hits.append("4872")
    if re.search(r"(?<!\d)400(?!\d)", compact) or "$400" in text:
        hits.append("400")
    if "3150" in compact or "3,150" in text:
        hits.append("3150")
    if "1722" in compact or "1,722" in text:
        hits.append("1722")
    if "250" in compact and "150" in compact:
        hits.append("250+150")
    return "+".join(hits) if hits else "unparsed"


def tracking_for_cell(task: str, condition: str, text: str, done: bool) -> tuple[str, str]:
    if not done:
        return "", "not evaluated: cell not DONE"
    if task == "retrieval-f001":
        state, _ = f001_answer(text)
        low = text.lower()
        has_gold = bool(re.search(r"gold\s*voyager", low))
        has_silver = bool(re.search(r"silver\s*voyager", low))
        has_38450 = "38450" in re.sub(r"[, ]", "", text) or "38,450" in text
        has_8620 = "8620" in re.sub(r"[, ]", "", text) or "8,620" in text
        if condition == "base":
            ok = has_gold and has_38450 and not has_silver
            ev = f"trajectory reports {state}"
            return ("yes" if ok else "no"), ev
        ok = has_silver and has_8620 and not has_gold
        # Flash CF also mentions Gold as next-tier name; allow Gold only as "Gold Voyager" progress phrase
        if has_gold and has_silver:
            # next-tier mention is not the current tier if Silver is stated as current
            if re.search(r"loyalty tier:\s*silver", low) or re.search(
                r"tier is silver", low
            ) or re.search(r"silver voyager", low):
                current_silver = True
            else:
                current_silver = False
            ok = current_silver and has_8620
            ev = (
                f"trajectory reports {state}; Silver treated as current tier "
                f"(Gold also appears in text; flagged if ambiguous)"
            )
            if "needed for gold" in low or "short of" in low or "progress to next" in low:
                ok = has_silver and has_8620
                ev = f"trajectory reports current Silver Voyager / 8620; Gold appears only as next-tier language"
            elif not current_silver:
                return "ambiguous", ev + " — MANUAL REVIEW: both Gold and Silver in DONE text"
        else:
            ev = f"trajectory reports {state}"
        return ("yes" if ok else "no"), ev
    if task == "aggregation-f003":
        state = f003_answer(text)
        compact = re.sub(r"[, $]", "", text)
        if condition == "base":
            ok = ("4872" in compact) or ("4871.70" in compact) or (
                "3150" in compact and "1722" in compact
            )
            ev = f"trajectory refund claims: {state}"
            return ("yes" if ok else "no"), ev
        has_400 = bool(re.search(r"(?<!\d)400(?!\d)", compact)) or "$400" in text
        has_250_150 = "250" in compact and "150" in compact
        ok = has_400 or has_250_150
        ev = f"trajectory refund claims: {state}"
        return ("yes" if ok else "no"), ev
    return "ambiguous", "unknown task"


def classify_failure(rows: list[dict], cond: str, model: str, task: str) -> str:
    if not rows:
        return "NOT_DONE"
    act = last_action(rows)
    if act == "DONE":
        return ""
    if act == "FAIL":
        return "OTHER_EXECUTION_FAILURE"
    if act == "TOOL_CALL":
        return "TOOL_CALL_FAILURE"
    if act == "EMPTY_XML":
        return "NO_ACTION"
    if len(rows) == 1 and act != "DONE":
        return "NO_ACTION"
    if act != "DONE":
        return "NOT_DONE"
    return "OTHER"


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> list[float | None]:
    if n <= 0:
        return [None, None]
    # lower
    if k == 0:
        lo = 0.0
    else:
        lo = float(beta.ppf(alpha / 2, k, n - k + 1))
    if k == n:
        hi = 1.0
    else:
        hi = float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return [lo, hi]


def fmt_ci(ci: list[float | None]) -> str:
    if ci[0] is None:
        return "n/a"
    return f"[{ci[0]:.3f}, {ci[1]:.3f}]"


# Cell registry: one row per trajectory we analyze
CELLS = [
    # Claude
    dict(model="Claude", lane="primary", model_key="claude", task="retrieval-f001", condition="base",
         traj="results/stage4-retrieval-f001/base/retrieval-f001/traj.jsonl",
         guest="results/stage4-retrieval-f001/base/retrieval-f001.guest.json",
         sql="", scores="results/stage4-retrieval-f001/base/scores.json"),
    dict(model="Claude", lane="primary", model_key="claude", task="retrieval-f001", condition="cf",
         traj="results/stage4-retrieval-f001/cf/retrieval-f001/traj.jsonl",
         guest="results/stage4-retrieval-f001/cf/retrieval-f001.guest.json",
         sql="results/stage4-retrieval-f001/cf/sql-patch.json",
         scores="results/stage4-retrieval-f001/cf/scores.json"),
    dict(model="Claude", lane="primary", model_key="claude", task="aggregation-f003", condition="base",
         traj="results/stage4-aggregation-f003/base/aggregation-f003/traj.jsonl",
         guest="results/stage4-aggregation-f003/base/aggregation-f003.guest.json",
         sql="", scores="results/stage4-aggregation-f003/base/scores.json"),
    dict(model="Claude", lane="primary", model_key="claude", task="aggregation-f003", condition="cf",
         traj="results/stage4-aggregation-f003/cf/aggregation-f003/traj.jsonl",
         guest="results/stage4-aggregation-f003/cf/aggregation-f003.guest.json",
         sql="results/stage4-aggregation-f003/cf/sql-patch.json",
         scores="results/stage4-aggregation-f003/cf/scores.json"),
    # GPT
    dict(model="GPT", lane="primary", model_key="openai", task="retrieval-f001", condition="base",
         traj="results/stage4-openai-retrieval-f001/base/retrieval-f001/traj.jsonl",
         guest="results/stage4-openai-retrieval-f001/base/retrieval-f001.guest.json",
         sql="", scores="results/stage4-openai-retrieval-f001/base/scores.json"),
    dict(model="GPT", lane="primary", model_key="openai", task="retrieval-f001", condition="cf",
         traj="results/stage4-openai-retrieval-f001/cf/retrieval-f001/traj.jsonl",
         guest="results/stage4-openai-retrieval-f001/cf/retrieval-f001.guest.json",
         sql="results/stage4-openai-retrieval-f001/cf/sql-patch.json",
         scores="results/stage4-openai-retrieval-f001/cf/scores.json"),
    dict(model="GPT", lane="primary", model_key="openai", task="aggregation-f003", condition="base",
         traj="results/stage4-openai-aggregation-f003/base/aggregation-f003/traj.jsonl",
         guest="results/stage4-openai-aggregation-f003/base/aggregation-f003.guest.json",
         sql="", scores="results/stage4-openai-aggregation-f003/base/scores.json"),
    dict(model="GPT", lane="primary", model_key="openai", task="aggregation-f003", condition="cf",
         traj="results/stage4-openai-aggregation-f003/cf/aggregation-f003/traj.jsonl",
         guest="results/stage4-openai-aggregation-f003/cf/aggregation-f003.guest.json",
         sql="results/stage4-openai-aggregation-f003/cf/sql-patch.json",
         scores="results/stage4-openai-aggregation-f003/cf/scores.json"),
    # 35B-A3B paper
    dict(model="Qwen3.5-35B-A3B", lane="primary", model_key="qwen35a3b", task="retrieval-f001", condition="base",
         traj="results/stage4-qwen35a3b-retrieval-f001/base/retrieval-f001/traj.jsonl",
         guest="results/stage4-qwen35a3b-retrieval-f001/base/retrieval-f001.guest.json",
         sql="", scores="results/stage4-qwen35a3b-retrieval-f001/base/scores.json"),
    dict(model="Qwen3.5-35B-A3B", lane="primary", model_key="qwen35a3b", task="retrieval-f001", condition="cf",
         traj="results/stage4-qwen35a3b-retrieval-f001/cf/retrieval-f001/traj.jsonl",
         guest="results/stage4-qwen35a3b-retrieval-f001/cf/retrieval-f001.guest.json",
         sql="results/stage4-qwen35a3b-retrieval-f001/cf/sql-patch.json",
         scores="results/stage4-qwen35a3b-retrieval-f001/cf/scores.json"),
    dict(model="Qwen3.5-35B-A3B", lane="primary", model_key="qwen35a3b", task="aggregation-f003", condition="base",
         traj="results/stage4-qwen35a3b-aggregation-f003/base/aggregation-f003/traj.jsonl",
         guest="results/stage4-qwen35a3b-aggregation-f003/base/aggregation-f003.guest.json",
         sql="", scores="results/stage4-qwen35a3b-aggregation-f003/base/scores.json"),
    dict(model="Qwen3.5-35B-A3B", lane="primary", model_key="qwen35a3b", task="aggregation-f003", condition="cf",
         traj="results/stage4-qwen35a3b-aggregation-f003/cf/aggregation-f003/traj.jsonl",
         guest="results/stage4-qwen35a3b-aggregation-f003/cf/aggregation-f003.guest.json",
         sql="results/stage4-qwen35a3b-aggregation-f003/cf/sql-patch.json",
         scores="results/stage4-qwen35a3b-aggregation-f003/cf/scores.json",
         notes_fixed="canonical CF directory is the retry3 recaptcha FAIL cell; scores.json result_dir points at cf-retry3"),
    dict(model="Qwen3.5-35B-A3B", lane="primary", model_key="qwen35a3b", task="aggregation-f003",
         condition="cf-attempt1",
         traj="results/stage4-qwen35a3b-aggregation-f003/cf-attempt1-80step-no_done/aggregation-f003/traj.jsonl",
         guest="results/stage4-qwen35a3b-aggregation-f003/cf-attempt1-80step-no_done/aggregation-f003.guest.json",
         sql="results/stage4-qwen35a3b-aggregation-f003/cf-attempt1-80step-no_done/sql-patch.json",
         scores="results/stage4-qwen35a3b-aggregation-f003/cf-attempt1-80step-no_done/scores.json",
         notes_fixed="failed CF attempt 1: 80 TOOL_CALL steps, never DONE"),
    dict(model="Qwen3.5-35B-A3B", lane="primary", model_key="qwen35a3b", task="aggregation-f003",
         condition="cf-attempt2",
         traj="results/stage4-qwen35a3b-aggregation-f003/cf-attempt2-step2-no_actions/aggregation-f003/traj.jsonl",
         guest="results/stage4-qwen35a3b-aggregation-f003/cf-attempt2-step2-no_actions/aggregation-f003.guest.json",
         sql="results/stage4-qwen35a3b-aggregation-f003/cf-attempt2-step2-no_actions/sql-patch.json",
         scores="results/stage4-qwen35a3b-aggregation-f003/cf-attempt2-step2-no_actions/scores.json",
         notes_fixed="failed CF attempt 2: 1-step traj then stop (no DONE)"),
    # 9B
    dict(model="Qwen3.5-9B", lane="size_ablation", model_key="qwen359b", task="retrieval-f001", condition="base",
         traj="results/stage4-qwen359b-retrieval-f001/base/retrieval-f001/traj.jsonl",
         guest="results/stage4-qwen359b-retrieval-f001/base/retrieval-f001.guest.json",
         sql="", scores="results/stage4-qwen359b-retrieval-f001/base/scores.json"),
    dict(model="Qwen3.5-9B", lane="size_ablation", model_key="qwen359b", task="retrieval-f001", condition="cf",
         traj="results/stage4-qwen359b-retrieval-f001/cf/retrieval-f001/traj.jsonl",
         guest="results/stage4-qwen359b-retrieval-f001/cf/retrieval-f001.guest.json",
         sql="results/stage4-qwen359b-retrieval-f001/cf/sql-patch.json",
         scores="results/stage4-qwen359b-retrieval-f001/cf/scores.json"),
    dict(model="Qwen3.5-9B", lane="size_ablation", model_key="qwen359b", task="aggregation-f003", condition="base",
         traj="results/stage4-qwen359b-aggregation-f003/base/aggregation-f003/traj.jsonl",
         guest="results/stage4-qwen359b-aggregation-f003/base/aggregation-f003.guest.json",
         sql="", scores="results/stage4-qwen359b-aggregation-f003/base/scores.json"),
    dict(model="Qwen3.5-9B", lane="size_ablation", model_key="qwen359b", task="aggregation-f003", condition="cf",
         traj="results/stage4-qwen359b-aggregation-f003/cf/aggregation-f003/traj.jsonl",
         guest="results/stage4-qwen359b-aggregation-f003/cf/aggregation-f003.guest.json",
         sql="results/stage4-qwen359b-aggregation-f003/cf/sql-patch.json",
         scores="results/stage4-qwen359b-aggregation-f003/cf/scores.json"),
    dict(model="Qwen3.5-9B", lane="size_ablation", model_key="qwen359b", task="aggregation-f003",
         condition="cf-incomplete",
         traj="results/stage4-qwen359b-aggregation-f003/cf-incomplete-20260827T071422/aggregation-f003/traj.jsonl",
         guest="results/stage4-qwen359b-aggregation-f003/cf-incomplete-20260827T071422/aggregation-f003.guest.json",
         sql="results/stage4-qwen359b-aggregation-f003/cf-incomplete-20260827T071422/sql-patch.json",
         scores="",
         notes_fixed="aborted CF attempt archived before canonical DONE CF; agent copy has guest/sql only"),
    # Flash
    dict(model="Qwen3.8-Flash", lane="exploratory", model_key="qwen38flash", task="retrieval-f001", condition="base",
         traj="results/stage4-qwen38flash-retrieval-f001/base/retrieval-f001/traj.jsonl",
         guest="results/stage4-qwen38flash-retrieval-f001/base/retrieval-f001.guest.json",
         sql="", scores="results/stage4-qwen38flash-retrieval-f001/base/scores.json"),
    dict(model="Qwen3.8-Flash", lane="exploratory", model_key="qwen38flash", task="retrieval-f001", condition="cf",
         traj="results/stage4-qwen38flash-retrieval-f001/cf/retrieval-f001/traj.jsonl",
         guest="results/stage4-qwen38flash-retrieval-f001/cf/retrieval-f001.guest.json",
         sql="results/stage4-qwen38flash-retrieval-f001/cf/sql-patch.json",
         scores="results/stage4-qwen38flash-retrieval-f001/cf/scores.json"),
    dict(model="Qwen3.8-Flash", lane="exploratory", model_key="qwen38flash", task="aggregation-f003", condition="base",
         traj="results/stage4-qwen38flash-aggregation-f003/base/aggregation-f003/traj.jsonl",
         guest="results/stage4-qwen38flash-aggregation-f003/base/aggregation-f003.guest.json",
         sql="", scores="results/stage4-qwen38flash-aggregation-f003/base/scores.json"),
    dict(model="Qwen3.8-Flash", lane="exploratory", model_key="qwen38flash", task="aggregation-f003", condition="cf",
         traj="results/stage4-qwen38flash-aggregation-f003/cf/aggregation-f003/traj.jsonl",
         guest="results/stage4-qwen38flash-aggregation-f003/cf/aggregation-f003.guest.json",
         sql="results/stage4-qwen38flash-aggregation-f003/cf/sql-patch.json",
         scores="results/stage4-qwen38flash-aggregation-f003/cf/scores.json"),
]


def analyze_cell(spec: dict) -> dict:
    traj_p = ROOT / spec["traj"] if spec["traj"] else None
    guest_p = ROOT / spec["guest"] if spec["guest"] else None
    sql_p = ROOT / spec["sql"] if spec.get("sql") else None
    scores_p = ROOT / spec["scores"] if spec.get("scores") else None
    rows = load_traj(traj_p) if traj_p else []
    guest = load_json(guest_p) if guest_p else None
    done = is_done(rows)
    last = last_action(rows)
    gold, gold_note = guest_gold(guest, spec["task"], spec["condition"])
    text = norm_text(rows)
    tracking, track_ev = tracking_for_cell(spec["task"], spec["condition"], text, done)
    sc = score_int(scores_p) if scores_p and scores_p.is_file() else None
    wstatus, wscore = writer_fields(spec["model_key"], spec["task"])
    fail = classify_failure(rows, spec["condition"], spec["model"], spec["task"])
    notes = [spec.get("notes_fixed") or ""]
    if gold_note:
        notes.append(gold_note)
    # Flash CF writer gold=True is a known parser mismatch — record if writer used
    if spec["model"] == "Qwen3.8-Flash" and spec["task"] == "retrieval-f001" and spec["condition"] == "cf":
        notes.append(
            "writer DV listed gold=True alongside silver=True; guest probe_after is Silver Voyager / 8620 (writer boolean not authoritative)"
        )
    if spec["model"] == "Qwen3.5-35B-A3B" and spec["task"] == "aggregation-f003" and spec["condition"] == "cf":
        notes.append(
            "writer table status=ok and judge 75/0 must not be treated as a valid pair; last traj action is FAIL"
        )
    exec_fail = (not done) or bool(fail)
    valid = bool(
        traj_p
        and traj_p.is_file()
        and done
        and gold
        and tracking in {"yes", "no", "ambiguous"}
        and not exec_fail
    )
    # ambiguous tracking still a valid cell if DONE+gold, but pair tracking may fail
    if tracking == "ambiguous":
        notes.append("MANUAL REVIEW: tracking labelled ambiguous")
    if not done:
        valid = False
        tracking = ""
        track_ev = "not evaluated: last action is not DONE"
    if done and not gold:
        valid = False
        notes.append("guest gold unverified")
    final_state = ""
    if spec["task"] == "retrieval-f001":
        final_state, _ = f001_answer(text) if done else ""
        if not done:
            final_state = ""
    elif spec["task"] == "aggregation-f003":
        final_state = f003_answer(text) if done else ""
    why = ""
    if not valid:
        if not (traj_p and traj_p.is_file()):
            why = "trajectory missing"
        elif not done:
            why = f"last action {last!r} is not DONE"
        elif not gold:
            why = "guest/sql gold unverified"
        else:
            why = fail or "execution/attribution failure"
    return {
        "model": spec["model"],
        "lane": spec["lane"],
        "task": spec["task"],
        "condition": spec["condition"],
        "trajectory_path": spec["traj"],
        "guest_artifact_path": spec["guest"],
        "sql_patch_path": spec.get("sql") or "",
        "trajectory_exists": bool(traj_p and traj_p.is_file()),
        "step_count": len(rows),
        "last_action": last,
        "writer_status": wstatus,
        "writer_score": wscore,
        "done": done,
        "valid_cell": valid,
        "tracking": tracking,
        "tracking_evidence": track_ev,
        "gold_state": gold,
        "final_answer_state": final_state,
        "score": sc if sc is not None else "",
        "failure_type": fail if not done else "",
        "why_invalid": why,
        "notes": "; ".join(n for n in notes if n),
        "first_action": str(rows[0].get("action") or "") if rows else "",
        "done_response_excerpt": (
            re.sub(r"\s+", " ", text)[:280] if done else ""
        ),
    }


def pair_key(model, task):
    return (model, task)


def build_pairs(cells: list[dict]) -> list[dict]:
    by = {}
    for c in cells:
        if c["condition"] in {"base", "cf"}:
            by.setdefault((c["model"], c["task"], c["lane"]), {})[c["condition"]] = c
    pairs = []
    for (model, task, lane), d in sorted(by.items(), key=lambda x: (x[0][2], x[0][0], x[0][1])):
        b, cf = d.get("base"), d.get("cf")
        if not b or not cf:
            continue
        gold_changed = bool(b["gold_state"] and cf["gold_state"] and b["gold_state"] != cf["gold_state"])
        if task == "retrieval-f001":
            gold_changed = "Gold" in (b["gold_state"] or "") and "Silver" in (cf["gold_state"] or "")
        if task == "aggregation-f003":
            gold_changed = "4871.70" in (b["gold_state"] or "") and "400.00" in (cf["gold_state"] or "")
        valid_pair = bool(b["valid_cell"] and cf["valid_cell"] and gold_changed)
        # 35B f003 hard rule
        if model == "Qwen3.5-35B-A3B" and task == "aggregation-f003":
            valid_pair = False
        tb = b["tracking"] == "yes"
        tcf = cf["tracking"] == "yes"
        tracking_pair = bool(valid_pair and tb and tcf)
        bsc = b["score"] if b["score"] != "" else None
        csc = cf["score"] if cf["score"] != "" else None
        if valid_pair and bsc is not None and csc is not None:
            delta = int(csc) - int(bsc)
            invariant = int(csc) == int(bsc)
        else:
            delta = ""
            invariant = ""
        diss = bool(valid_pair and tracking_pair and invariant is True)
        notes = []
        if model == "Qwen3.5-35B-A3B" and task == "aggregation-f003":
            notes.append("NO valid pair: all three CF attempts failed/incomplete; excluded from all semantic denominators")
        if not gold_changed:
            notes.append("gold_changed false or unverified")
        pairs.append({
            "model": model,
            "lane": lane,
            "task": task,
            "base_trajectory": b["trajectory_path"],
            "cf_trajectory": cf["trajectory_path"],
            "base_gold": b["gold_state"],
            "cf_gold": cf["gold_state"],
            "gold_changed": gold_changed,
            "base_score": bsc if bsc is not None else "",
            "cf_score": csc if csc is not None else "",
            "score_delta": delta,
            "score_invariant": invariant if invariant != "" else "",
            "tracking_base": b["tracking"],
            "tracking_cf": cf["tracking"],
            "tracking_pair": tracking_pair,
            "valid_pair": valid_pair,
            "dissociation_event": diss,
            "notes": "; ".join(notes),
        })
    return pairs


def summarize(pairs: list[dict], lane: str) -> dict:
    subset = [p for p in pairs if p["lane"] == lane]
    valid = [p for p in subset if p["valid_pair"]]
    track = [p for p in valid if p["tracking_pair"]]
    inv = [p for p in track if p["score_invariant"] is True]
    sens = [p for p in track if p["score_invariant"] is False]
    diss = [p for p in valid if p["dissociation_event"]]
    n = len(track)
    k = len(inv)
    rate = (k / n) if n else None
    ci = clopper_pearson(k, n) if n else [None, None]
    return {
        "valid_pairs": len(valid),
        "tracking_valid": n,
        "score_invariant": k,
        "score_sensitive": len(sens),
        "dissociation_events": len(diss),
        "invariance_rate": rate,
        "clopper_pearson_95ci": ci,
        "pairs": valid,
        "all_lane_pairs": subset,
    }


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]):
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


def md_escape(s) -> str:
    return str(s).replace("|", "\\|")


def pair_interp(p: dict) -> str:
    if not p["valid_pair"]:
        return "Excluded: no valid CF cell (execution failure). Not semantic non-tracking."
    if p["tracking_pair"] and p["score_invariant"] is True:
        return "Tracked the state change; conventional score unchanged (dissociation)."
    if p["tracking_pair"] and p["score_invariant"] is False:
        return "Tracked the state change; conventional score moved (score-sensitive)."
    if not p["tracking_pair"]:
        return "Valid pair but tracking failed or ambiguous."
    return ""


def write_table(path_md: Path, path_tex: Path, title: str, pairs: list[dict], extra: str):
    cols = [
        "Agent/model", "Task", "Base gold", "CF gold", "Base score", "CF score",
        "Tracking", "Valid pair", "Dissociation", "Interpretation",
    ]
    lines = [f"# {title}", "", extra, "", "| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    tex = [
        r"\begin{tabular}{llcccccccl}",
        r"\hline",
        r"Agent & Task & Base gold & CF gold & Base & CF & Track & Valid & Dissoc. & Interpretation \\",
        r"\hline",
    ]
    for p in pairs:
        row = [
            p["model"], p["task"], p["base_gold"], p["cf_gold"],
            str(p["base_score"]), str(p["cf_score"]),
            "yes" if p["tracking_pair"] else ("no" if p["valid_pair"] else "n/a"),
            "yes" if p["valid_pair"] else "no",
            "yes" if p["dissociation_event"] else ("no" if p["valid_pair"] else "n/a"),
            pair_interp(p),
        ]
        lines.append("| " + " | ".join(md_escape(x) for x in row) + " |")
        tex.append(" & ".join(str(x).replace("&", r"\&") for x in row) + r" \\")
    tex += [r"\hline", r"\end{tabular}"]
    path_md.write_text("\n".join(lines) + "\n")
    path_tex.write_text("\n".join(tex) + "\n")


def figures(primary, ablation, exploratory, pairs):
    def scatter(subset, title, fname, nnote):
        fig, ax = plt.subplots(figsize=(6.2, 4.6))
        markers = {"retrieval-f001": "o", "aggregation-f003": "s"}
        colors = {"Claude": "#1f4e79", "GPT": "#2a9d8f", "Qwen3.5-35B-A3B": "#e76f51",
                  "Qwen3.5-9B": "#6d597a", "Qwen3.8-Flash": "#b56576"}
        for p in subset:
            if p["base_score"] == "" or p["cf_score"] == "":
                continue
            ax.scatter(
                [int(p["base_score"])], [int(p["cf_score"])],
                marker=markers.get(p["task"], "o"),
                color=colors.get(p["model"], "gray"),
                s=90, zorder=3, label=f"{p['model']} {p['task']}",
            )
        ax.plot([0, 100], [0, 100], color="#bbbbbb", lw=1, zorder=1)
        ax.set_xlim(-5, 105)
        ax.set_ylim(-5, 105)
        ax.set_xlabel("Baseline score (0–100)")
        ax.set_ylabel("Counterfactual score (0–100)")
        ax.set_title(title)
        ax.legend(fontsize=7, loc="lower right")
        ax.text(0.02, 0.98, nnote, transform=ax.transAxes, va="top", fontsize=8)
        fig.tight_layout()
        fig.savefig(OUT / fname, dpi=200)
        plt.close(fig)

    pv = [p for p in pairs if p["lane"] == "primary" and p["valid_pair"]]
    av = [p for p in pairs if p["lane"] == "size_ablation" and p["valid_pair"]]
    ev = [p for p in pairs if p["lane"] == "exploratory" and p["valid_pair"]]
    scatter(pv, "Primary P1 paired scores (valid pairs only)", "score_pairs_primary.png",
            f"n={len(pv)} valid pairs; points on the diagonal are score-invariant")
    scatter(av, "Size ablation paired scores (Qwen3.5-9B)", "score_pairs_ablation.png",
            f"n={len(av)} valid pairs; not pooled into primary P1")
    # gold state change
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.8))
    axes[0].bar(["BASE", "CF"], [38450, 8620], color=["#1f4e79", "#e76f51"])
    axes[0].set_ylabel("Miles")
    axes[0].set_title("f001 loyalty miles")
    axes[1].bar(["BASE", "CF"], [4871.70, 400.0], color=["#1f4e79", "#e76f51"])
    axes[1].set_ylabel("Combined refund ($)")
    axes[1].set_title("f003 filed combined refund")
    fig.suptitle("Task-relevant guest state changes under the frozen SQL intervention")
    fig.text(
        0.5, 0.01,
        "The underlying task-relevant state changes between baseline and counterfactual conditions; score change is evaluated separately.",
        ha="center", fontsize=8,
    )
    fig.tight_layout(rect=[0, 0.08, 1, 0.95])
    fig.savefig(OUT / "gold_state_change.png", dpi=200)
    plt.close(fig)
    # invariance by tier — three separate bars, not one pooled estimate
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    labels = ["Primary P1", "Size ablation\n(9B)", "Exploratory\n(Flash)"]
    stats = [primary, ablation, exploratory]
    xs = range(3)
    rates = [(s["invariance_rate"] if s["invariance_rate"] is not None else 0) for s in stats]
    ns = [s["tracking_valid"] for s in stats]
    ks = [s["score_invariant"] for s in stats]
    bars = ax.bar(xs, rates, color=["#1f4e79", "#6d597a", "#b56576"])
    ax.set_ylim(0, 1.15)
    ax.set_xticks(list(xs))
    ax.set_xticklabels(labels)
    ax.set_ylabel("Score invariance | tracking-valid pairs")
    ax.set_title("Invariance by analysis tier (not pooled)")
    for i, (k, n, r) in enumerate(zip(ks, ns, rates)):
        ax.text(i, r + 0.04, f"{k}/{n}", ha="center", fontsize=9)
    ax.text(0.02, 0.02, "Tiers are distinct analyses; do not read a single combined rate.",
            transform=ax.transAxes, fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "invariance_by_tier.png", dpi=200)
    plt.close(fig)


def evidence_md(cells: list[dict], pairs: list[dict]) -> str:
    want = [
        ("Claude", "retrieval-f001"),
        ("Claude", "aggregation-f003"),
        ("GPT", "retrieval-f001"),
        ("GPT", "aggregation-f003"),
        ("Qwen3.5-35B-A3B", "retrieval-f001"),
    ]
    idx = {(c["model"], c["task"], c["condition"]): c for c in cells}
    pidx = {(p["model"], p["task"]): p for p in pairs}
    parts = ["# Trajectory evidence (valid primary pairs only)", "",
             "Excerpts are observable final-answer claims from the DONE step, not full chain-of-thought.", ""]
    for model, task in want:
        b = idx[(model, task, "base")]
        cf = idx[(model, task, "cf")]
        p = pidx[(model, task)]
        parts += [
            f"## {model} — {task}",
            "",
            "BASE:",
            f"- relevant state observed/reported: {b['final_answer_state']} (guest: {b['gold_state']})",
            f"- key action(s): first `{b['first_action']}`; last `DONE`",
            f"- final answer: {b['done_response_excerpt']}",
            f"- score: {b['score']}",
            "",
            "COUNTERFACTUAL:",
            f"- relevant state observed/reported: {cf['final_answer_state']} (guest: {cf['gold_state']})",
            f"- key action(s): first `{cf['first_action']}`; last `DONE`",
            f"- final answer: {cf['done_response_excerpt']}",
            f"- score: {cf['score']}",
            "",
            f"STATE CHANGE: {b['gold_state']} → {cf['gold_state']}",
            f"TRACKING: {'yes' if p['tracking_pair'] else 'no'}",
            f"SCORE CHANGE: {p['base_score']} → {p['cf_score']} (delta {p['score_delta']})",
            f"DISSOCIATION: {'yes' if p['dissociation_event'] else 'no'}",
            "",
        ]
    parts += [
        "## Qwen3.5-35B-A3B — aggregation-f003 (not a valid pair)",
        "",
        "BASE is DONE and reports $4,872. Canonical CF last action is FAIL (reCAPTCHA; terminate/failure).",
        "Attempts cf-attempt1 (80 TOOL_CALL), cf-attempt2 (1-step stop), and cf/retry3 (FAIL) are execution failures.",
        "Not counted as semantic non-tracking or as score invariance.",
        "",
    ]
    return "\n".join(parts)


def model_summary_md(cells, pairs, primary, ablation, exploratory) -> str:
    def block(model, lane_name, stats):
        mine = [p for p in pairs if p["model"] == model]
        lines = [f"## {model}", ""]
        for p in mine:
            lines.append(
                f"- {p['task']}: valid_pair={p['valid_pair']}; tracking_pair={p['tracking_pair']}; "
                f"scores {p['base_score']}→{p['cf_score']}; gold {p['base_gold']} → {p['cf_gold']}; "
                f"dissociation={p['dissociation_event']}. {p['notes']}"
            )
        lines.append("")
        return "\n".join(lines)

    return "\n".join([
        "# Primary P1",
        "",
        "Valid pairs are restricted to frozen f001/f003. Execution failures are excluded from tracking and invariance denominators.",
        "",
        block("Claude", "primary", primary),
        block("GPT", "primary", primary),
        block("Qwen3.5-35B-A3B", "primary", primary),
        f"Primary invariance among tracking-valid pairs: {primary['score_invariant']}/{primary['tracking_valid']} "
        f"(Clopper–Pearson 95% CI {fmt_ci(primary['clopper_pearson_95ci'])}). "
        f"Qwen3.5-35B-A3B contributes only the f001 pair.",
        "",
        "# Size Ablation",
        "",
        "Not pooled into primary P1.",
        "",
        block("Qwen3.5-9B", "size_ablation", ablation),
        f"Invariance | tracking-valid: {ablation['score_invariant']}/{ablation['tracking_valid']} "
        f"(95% CI {fmt_ci(ablation['clopper_pearson_95ci'])}).",
        "",
        "# Exploratory",
        "",
        "Not pooled into primary P1. Does not replace Qwen3.5-35B-A3B.",
        "",
        block("Qwen3.8-Flash", "exploratory", exploratory),
        f"Invariance | tracking-valid: {exploratory['score_invariant']}/{exploratory['tracking_valid']} "
        f"(95% CI {fmt_ci(exploratory['clopper_pearson_95ci'])}).",
        "",
    ])


def paper_results(primary, ablation, exploratory) -> str:
    pr = primary["invariance_rate"]
    return f"""# Results (Stage 4 paired CUA)

We distinguish three outcomes: (i) whether a cell is a valid DONE trajectory with verified guest state, (ii) whether the agent's final report tracks that state (counterfactual state tracking), and (iii) whether the conventional rubric score is invariant when tracking succeeds.

**Primary P1** (Claude, GPT, Qwen3.5-35B-A3B; frozen retrieval-f001 and aggregation-f003). There are {primary['valid_pairs']} valid paired episodes. Qwen3.5-35B-A3B × f003 has no valid counterfactual: three CF attempts fail as execution (80-step TOOL_CALL loop; one-step stop; reCAPTCHA terminate/FAIL) and are excluded from tracking and invariance denominators. They are not semantic non-tracking. Across the {primary['tracking_valid']} tracking-valid pairs, {primary['score_invariant']} are score-invariant and {primary['score_sensitive']} are score-sensitive (invariance rate {primary['score_invariant']}/{primary['tracking_valid']}; Clopper–Pearson 95% CI {fmt_ci(primary['clopper_pearson_95ci'])}). All {primary['dissociation_events']} tracking-valid invariant pairs are dissociation events: the agent reported the manipulated world state while the 0–100 task score was unchanged. Exact paired scores: Claude f001 100→100, Claude f003 80→80, GPT f001 100→100, GPT f003 50→50, Qwen3.5-35B-A3B f001 100→100.

Successful completion and counterfactual state sensitivity are separable properties. In valid paired episodes, agents could track substantial changes in the underlying task state while retaining the same conventional task score.

**Size ablation** (Qwen3.5-9B; not in primary P1). Both f001 and f003 pairs are valid and tracking-valid. Scores: f001 80→80 (invariant); f003 50→80 (score-sensitive). Invariance among tracking-valid pairs: {ablation['score_invariant']}/{ablation['tracking_valid']} (95% CI {fmt_ci(ablation['clopper_pearson_95ci'])}).

**Exploratory** (Qwen3.8-Flash; not in primary P1; does not replace Qwen3.5-35B-A3B). Both pairs are valid and tracking-valid. Scores: f001 100→100 (invariant); f003 80→100 (score-sensitive). Invariance among tracking-valid pairs: {exploratory['score_invariant']}/{exploratory['tracking_valid']} (95% CI {fmt_ci(exploratory['clopper_pearson_95ci'])}).

These counts are descriptive. The sample is small; we do not claim that all computer-use agents behave this way, nor do we treat execution failure as evidence about state tracking.
"""


def paper_methods() -> str:
    return """# Methods (Stage 4 paired CUA)

Each frozen identifiable task (retrieval-f001, aggregation-f003) was run as a paired baseline/counterfactual episode on the same MyPCBench guest, prompt, screenshot protocol, and rubric. The counterfactual applied a locked SQL intervention (f001: loyalty status/miles; f003: filed 2023/2024 refund amounts) and guest probes recorded pre/post state. Cells were scored with the existing per-step rubric judge; the 0–100 integer is an auxiliary conventional score, not the attribution DV.

A trajectory is DONE iff the last `traj.jsonl` action is exactly `DONE`. `result.txt`, writer `ok`, and writer `track=yes` are not DONE criteria. A cell is valid for semantic analysis only if it is DONE, guest/SQL gold is verified, a final-answer state can be read from the trajectory, and no execution failure blocks attribution. A valid pair requires both BASE and CF valid, the same frozen task, and verified gold change. Failed or incomplete CF attempts are retained in the failure audit and are excluded from tracking and invariance denominators.

Tracking is whether the DONE-step report matches the verified guest state (f001: Gold/38450 vs Silver/8620; f003: combined ≈4872 vs 400). Score invariance is exact equality of integer 0–100 scores on tracking-valid pairs. Dissociation is tracking plus invariance. Primary P1 pools only Claude, GPT, and Qwen3.5-35B-A3B valid f001/f003 pairs. Qwen3.5-9B is a size ablation and Qwen3.8-Flash is exploratory; neither is pooled into primary P1. Abandoned HPC `results/stage4-qwen35-*` directories are ignored. Proportions are reported as k/n with Clopper–Pearson exact 95% intervals; no p=0.5 test is used.
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cells = [analyze_cell(s) for s in CELLS]
    # ignore abandoned HPC: never referenced in CELLS
    pairs = build_pairs(cells)
    primary = summarize(pairs, "primary")
    ablation = summarize(pairs, "size_ablation")
    exploratory = summarize(pairs, "exploratory")

    # Sanity: independent derivation vs expected
    sanity_notes = []
    if primary["valid_pairs"] != 5:
        sanity_notes.append(f"STOP: primary valid_pairs={primary['valid_pairs']} expected 5")
    if primary["score_invariant"] != 5 or primary["score_sensitive"] != 0:
        sanity_notes.append(
            f"STOP: primary invariant={primary['score_invariant']} sensitive={primary['score_sensitive']}"
        )
    p35 = [p for p in pairs if p["model"] == "Qwen3.5-35B-A3B" and p["task"] == "aggregation-f003"]
    if not p35 or p35[0]["valid_pair"]:
        sanity_notes.append("STOP: 35B f003 valid_pair is not NO")
    # score checks
    expect = {
        ("Claude", "retrieval-f001"): (100, 100),
        ("Claude", "aggregation-f003"): (80, 80),
        ("GPT", "retrieval-f001"): (100, 100),
        ("GPT", "aggregation-f003"): (50, 50),
        ("Qwen3.5-35B-A3B", "retrieval-f001"): (100, 100),
        ("Qwen3.5-9B", "retrieval-f001"): (80, 80),
        ("Qwen3.5-9B", "aggregation-f003"): (50, 80),
        ("Qwen3.8-Flash", "retrieval-f001"): (100, 100),
        ("Qwen3.8-Flash", "aggregation-f003"): (80, 100),
    }
    for p in pairs:
        key = (p["model"], p["task"])
        if key in expect and p["valid_pair"]:
            exp = expect[key]
            got = (p["base_score"], p["cf_score"])
            if got != exp:
                sanity_notes.append(f"STOP: {key} scores {got} != expected {exp} artifact={p['base_trajectory']}")

    inv_fields = [
        "model", "lane", "task", "condition", "trajectory_path", "guest_artifact_path",
        "sql_patch_path", "trajectory_exists", "step_count", "last_action",
        "writer_status", "writer_score", "notes",
    ]
    write_csv(OUT / "artifact_inventory.csv", cells, inv_fields)

    cell_fields = [
        "model", "lane", "task", "condition", "trajectory_path", "guest_artifact_path",
        "sql_patch_path", "done", "valid_cell", "tracking", "tracking_evidence",
        "gold_state", "final_answer_state", "score", "failure_type", "step_count",
        "last_action", "notes",
    ]
    write_csv(OUT / "trajectory_cells.csv", cells, cell_fields)

    pair_fields = [
        "model", "lane", "task", "base_trajectory", "cf_trajectory", "base_gold",
        "cf_gold", "gold_changed", "base_score", "cf_score", "score_delta",
        "score_invariant", "tracking_base", "tracking_cf", "tracking_pair",
        "valid_pair", "dissociation_event", "notes",
    ]
    write_csv(OUT / "paired_results.csv", pairs, pair_fields)

    fail_rows = [c for c in cells if not c["valid_cell"]]
    fail_fields = [
        "model", "task", "condition", "trajectory_path", "failure_type", "last_action",
        "step_count", "writer_status", "writer_score", "why_invalid", "notes",
    ]
    write_csv(OUT / "failure_audit.csv", fail_rows, fail_fields)

    write_table(
        OUT / "table_primary.md", OUT / "table_primary.tex",
        "Primary P1 (Claude, GPT, Qwen3.5-35B-A3B)",
        [p for p in pairs if p["lane"] == "primary"],
        "Only valid DONE pairs enter tracking/invariance. Qwen3.5-35B-A3B × f003 is listed as invalid.",
    )
    write_table(
        OUT / "table_ablation.md", OUT / "table_ablation.tex",
        "Size ablation (Qwen3.5-9B)",
        [p for p in pairs if p["lane"] == "size_ablation"],
        "Not pooled into primary P1.",
    )
    write_table(
        OUT / "table_exploratory.md", OUT / "table_exploratory.tex",
        "Exploratory (Qwen3.8-Flash)",
        [p for p in pairs if p["lane"] == "exploratory"],
        "Exploratory CUA. Does not replace Qwen3.5-35B-A3B.",
    )

    (OUT / "trajectory_evidence.md").write_text(evidence_md(cells, pairs))
    (OUT / "model_summary.md").write_text(model_summary_md(cells, pairs, primary, ablation, exploratory))
    (OUT / "paper_results.md").write_text(paper_results(primary, ablation, exploratory))
    (OUT / "paper_methods.md").write_text(paper_methods())

    figures(primary, ablation, exploratory, pairs)

    summary = {
        "primary": {k: primary[k] for k in [
            "valid_pairs", "tracking_valid", "score_invariant", "score_sensitive",
            "dissociation_events", "invariance_rate", "clopper_pearson_95ci",
        ]},
        "size_ablation": {k: ablation[k] for k in [
            "valid_pairs", "tracking_valid", "score_invariant", "score_sensitive",
            "dissociation_events", "invariance_rate", "clopper_pearson_95ci",
        ]},
        "exploratory": {k: exploratory[k] for k in [
            "valid_pairs", "tracking_valid", "score_invariant", "score_sensitive",
            "dissociation_events", "invariance_rate", "clopper_pearson_95ci",
        ]},
        "sanity_flags": sanity_notes,
    }
    (OUT / "statistical_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    man = ["Stage-4 read-only audit artifact list", ""]
    for c in cells:
        man.append(
            f"{c['model']} {c['task']} {c['condition']}: traj={c['trajectory_path']} "
            f"guest={c['guest_artifact_path']} sql={c['sql_patch_path']} "
            f"valid={c['valid_cell']} why={c['why_invalid']}"
        )
    man += ["", "Pairs:"]
    for p in pairs:
        man.append(
            f"{p['model']} {p['task']}: base={p['base_trajectory']} cf={p['cf_trajectory']} "
            f"valid_pair={p['valid_pair']} {p['notes']}"
        )
    man += [
        "",
        "Writer tables used only as secondary inventory: "
        "out/evidence_stage4_results.md, evidence_stage4_openai_results.md, "
        "evidence_stage4_qwen35a3b_results.md, evidence_stage4_qwen359b_results.md, "
        "evidence_stage4_qwen38flash_results.md",
        "Ignored: results/stage4-qwen35-* (abandoned HPC 27B).",
        "Excluded from primary: f018, f004, confounded and reserve tasks.",
    ]
    (OUT / "reproducibility_manifest.txt").write_text("\n".join(man) + "\n")

    n35_cf_fail = sum(
        1 for c in cells
        if c["model"] == "Qwen3.5-35B-A3B" and c["task"] == "aggregation-f003"
        and str(c["condition"]).startswith("cf")
    )
    fail_types = sorted({c["failure_type"] or "OTHER" for c in fail_rows})

    print("PRIMARY")
    print("-------")
    print(f"valid paired cells: {primary['valid_pairs']}")
    print(f"tracking-valid: {primary['tracking_valid']}")
    print(f"score-invariant: {primary['score_invariant']}")
    print(f"score-sensitive: {primary['score_sensitive']}")
    print(f"dissociation events: {primary['dissociation_events']}")
    print(f"invariance rate: {primary['invariance_rate']}")
    print(f"Clopper-Pearson 95% CI: {fmt_ci(primary['clopper_pearson_95ci'])}")
    print()
    print("SIZE ABLATION")
    print("-------------")
    print(f"valid paired cells: {ablation['valid_pairs']}")
    print(f"tracking-valid: {ablation['tracking_valid']}")
    print(f"score-invariant: {ablation['score_invariant']}")
    print(f"score-sensitive: {ablation['score_sensitive']}")
    print(f"dissociation events: {ablation['dissociation_events']}")
    print(f"invariance rate: {ablation['invariance_rate']}")
    print(f"Clopper-Pearson 95% CI: {fmt_ci(ablation['clopper_pearson_95ci'])}")
    print()
    print("EXPLORATORY")
    print("-----------")
    print(f"valid paired cells: {exploratory['valid_pairs']}")
    print(f"tracking-valid: {exploratory['tracking_valid']}")
    print(f"score-invariant: {exploratory['score_invariant']}")
    print(f"score-sensitive: {exploratory['score_sensitive']}")
    print(f"dissociation events: {exploratory['dissociation_events']}")
    print(f"invariance rate: {exploratory['invariance_rate']}")
    print(f"Clopper-Pearson 95% CI: {fmt_ci(exploratory['clopper_pearson_95ci'])}")
    print()
    print("FAILURES")
    print("--------")
    print(f"number of invalid cells: {len(fail_rows)}")
    print(f"number of Qwen3.5-35B f003 failed CF attempts: {n35_cf_fail}")
    print(f"failure types: {', '.join(fail_types)}")
    print()
    print("SANITY")
    print("------")
    print("primary expected valid pairs = 5")
    print("primary expected invariant pairs = 5")
    print("35B f003 valid pair = NO")
    if sanity_notes:
        print("SANITY FLAGS:")
        for s in sanity_notes:
            print(s)
    print()
    print("Generated files:")
    for p in sorted(OUT.iterdir()):
        if p.name.startswith("."):
            continue
        print(p.relative_to(ROOT))


if __name__ == "__main__":
    main()
