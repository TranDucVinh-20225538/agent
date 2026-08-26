"""Stage 1–2: screen all 184 tasks, then select a confirmatory sample.

Selection is a function of pre-registered eligibility only. It does not look at
agent outcomes, hypothesized support, or whether a probe SQL has already been
hand-written. Identifiability that needs a guest dump is recorded as
pending_probe, not as a reason to prefer a task.

No Claude is invoked.
"""

from __future__ import annotations

import csv
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
RESULTS = ROOT / "results"

# Pre-registered. Changing this after seeing agent results is a protocol deviation.
SEED = 20260826
K_PER_TYPE = 3

EVIDENCE_TYPES = [
    "point_field",
    "joint_branching",
    "aggregation",
    "multi_record",
    "latent_action",
    "revealed_vs_stated",
    "contradiction_cross_source",
    "control_no_personal_records",
    "other",
]

APP_DB = {
    "SpeedTax": "speedtax.sqlite",
    "Gringotts": "vaultbank.sqlite",
    "HangryDash": "hangrydash.sqlite",
    "Kwik-E-Mart": "kwik-e-mart.sqlite",
    "Dinoco Airlines": "dinoco-airlines.sqlite",
    "HooliCalendar": "hoolicalendar.sqlite",
    "Cheskepdia": "cheskepdia.sqlite",
    "eTaxi": "etaxi.sqlite",
    "BatBucks": "batbucks.sqlite",
    "HooliMail": "mail.sqlite",
    "LockedIn": "lockedin.sqlite",
    "TableFind": "tablefind.sqlite",
    "HooliShop": "hoolishop.sqlite",
    "OddsMarket": "oddsmarket.sqlite",
    "HooliWork": None,  # no persona sqlite in env.py warmup list
    "HooliChat": None,
    "Files": None,
    "LibreOffice": None,
    "LibreOffice Calc": None,
    "LibreOffice Writer": None,
}

GUI_RE = re.compile(
    r"libreoffice|spreadsheet|\.ods|\.xlsx|\bcalc\b|\bwriter\b|\bchart\b",
    re.I,
)
MONEY_RE = re.compile(r"\$\s?\d[\d,]*(?:\.\d+)?")


def load_invariant() -> set[str]:
    return set(json.loads((OUT / "channel_invariant_tasks.json").read_text()))


def load_pinned() -> dict[str, dict]:
    pinned: dict[str, dict] = {}
    root = ROOT / "external" / "MyPCBench-main" / "tasks" / "final"
    if not root.exists():
        return pinned
    for path in root.glob("*/*.rubrics.json"):
        data = json.loads(path.read_text())
        tasks = data if isinstance(data, list) else data.get("tasks", [])
        for task in tasks:
            if isinstance(task, dict) and "id" in task:
                pinned[task["id"]] = task
    return pinned


def evidence_type(task: dict) -> str:
    """Deterministic map from public fields. Not tuned on agent runs."""
    inst = (task.get("instruction") or "").lower()
    cat = task.get("category") or ""
    weight = float(task.get("attributable_weight") or 0)
    if weight == 0 and cat in {"situated_action", "cua_only"}:
        return "control_no_personal_records"
    if cat == "aggregation":
        return "aggregation"
    if cat == "contradiction":
        return "contradiction_cross_source"
    if cat == "retrieval":
        return "point_field"
    if "usual" in inst and any(w in inst for w in ("order", "from ")):
        return "latent_action"
    if cat == "preference_inference" and any(
        w in inst for w in ("sticking", "tell people", "really")
    ):
        return "revealed_vs_stated"
    if cat == "preference_inference":
        return "multi_record"
    if cat == "hard_app" and ("if there" in inst or "if no " in inst):
        return "joint_branching"
    if cat in {"contradiction", "counterfactual"} or "do they all agree" in inst:
        return "contradiction_cross_source"
    if cat == "counterfactual":
        return "contradiction_cross_source"
    return "other"


def mapped_dbs(apps: list[str]) -> list[str]:
    dbs = []
    for app in apps:
        db = APP_DB.get(app, "UNMAPPED")
        if db and db != "UNMAPPED":
            dbs.append(db)
    return dbs


def screen_one(task: dict, pinned: dict, invariant: set[str]) -> dict:
    tid = task["id"]
    pin = pinned.get(tid) or {}
    apps = task.get("apps") or []
    inst = task.get("instruction") or ""
    rubric_text = " ".join(
        r.get("criterion", "") for r in (pin.get("grading") or {}).get("rubrics", [])
    )
    et = evidence_type(task)
    channel_invariant = tid in invariant
    sqlite_ok = bool(mapped_dbs(apps))
    cua = bool(pin.get("cua_required"))
    gui = bool(GUI_RE.search(inst + " " + rubric_text + " " + " ".join(apps)))
    pins_gold = bool(MONEY_RE.search(inst))
    dv_from_answer = (not cua) and (not gui)
    # Eligibility A–E, pre-registered. Identifiability is NOT in this list.
    reasons = []
    if not channel_invariant:
        reasons.append("not_channel_invariant")
    if not sqlite_ok:
        reasons.append("no_mapped_sqlite")
    if cua:
        reasons.append("cua_required")
    if gui:
        reasons.append("gui_artifact")
    if pins_gold:
        reasons.append("instruction_pins_gold")
    if et == "other":
        reasons.append("evidence_type_other")
    eligible = not reasons
    return {
        "id": tid,
        "category": task.get("category"),
        "evidence_type": et,
        "apps": "|".join(apps),
        "channel_invariant": channel_invariant,
        "sqlite_mapped": sqlite_ok,
        "mapped_dbs": "|".join(mapped_dbs(apps)),
        "cua_required": cua,
        "gui_artifact": gui,
        "instruction_pins_gold": pins_gold,
        "dv_from_answer": dv_from_answer,
        "identifiable": "pending_dummy_probe" if eligible else "not_applicable",
        "eligible": eligible,
        "exclude_reason": "|".join(reasons) if reasons else "",
        "instruction": inst.replace("\n", " "),
    }


def select_sample(rows: list[dict]) -> list[dict]:
    """If n<=K take all (sorted by id). If n>K, Random(SEED).sample on sorted ids."""
    by_type: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if row["eligible"]:
            by_type[row["evidence_type"]].append(row)
    sample = []
    for et in EVIDENCE_TYPES:
        pool = sorted(by_type.get(et, []), key=lambda r: r["id"])
        if not pool:
            continue
        if len(pool) <= K_PER_TYPE:
            chosen = pool
            rule = f"all_{len(pool)}"
        else:
            rng = random.Random(SEED)
            ids = [r["id"] for r in pool]
            pick = set(rng.sample(ids, K_PER_TYPE))
            chosen = [r for r in pool if r["id"] in pick]
            rule = f"rng({SEED}).sample({len(pool)}, {K_PER_TYPE})"
        for row in chosen:
            rec = dict(row)
            rec["selection_rule"] = rule
            sample.append(rec)
    return sample


def funnel_md(rows: list[dict], sample: list[dict]) -> str:
    n = len(rows)
    c = Counter()
    for row in rows:
        if not row["channel_invariant"]:
            c["not_channel_invariant"] += 1
        if not row["sqlite_mapped"]:
            c["no_mapped_sqlite"] += 1
        if row["cua_required"]:
            c["cua_required"] += 1
        if row["gui_artifact"]:
            c["gui_artifact"] += 1
        if row["instruction_pins_gold"]:
            c["instruction_pins_gold"] += 1
        if row["eligible"]:
            c["eligible"] += 1
    by_reason = Counter(row["exclude_reason"] for row in rows if not row["eligible"])
    lines = [
        "# Dataset selection funnel",
        "",
        "Pre-registered before confirmatory Claude runs. Pilot runs",
        "(retrieval-f001, hard_app-f033, preference_inference-f009, situated_action-f028)",
        "are reported separately and are not used to choose this sample.",
        "",
        "Under A–E, `hard_app-f033` is ineligible (HuggingFace category is",
        "`situated_action`, attributable weight 0 in the screen file, rubric not",
        "channel-invariant, `cua_required`). `preference_inference-f009` is",
        "ineligible (not channel-invariant; LibreOffice Writer in the instruction).",
        "Those remain in the pilot log. They are not re-inserted into the",
        "confirmatory sample to keep a favorite result.",
        "",
        f"- Tasks in release: **{n}**",
        f"- Eligible under A–E: **{c['eligible']}**",
        f"- Confirmatory sample (k≤{K_PER_TYPE} per type, seed={SEED}): **{len(sample)}**",
        "",
        "Exclusions are not mutually exclusive; a task may fail several checks.",
        f"- not channel-invariant: {c['not_channel_invariant']}",
        f"- no mapped sqlite: {c['no_mapped_sqlite']}",
        f"- cua_required: {c['cua_required']}",
        f"- GUI artifact in instruction/rubric/apps: {c['gui_artifact']}",
        f"- instruction pins a dollar gold: {c['instruction_pins_gold']}",
        "",
        "## Primary exclude reason (first-listed conjunction)",
        "",
        "| reason | n |",
        "| --- | ---: |",
    ]
    for reason, k in by_reason.most_common():
        lines.append(f"| `{reason}` | {k} |")
    lines += [
        "",
        "## Eligible by evidence type",
        "",
        "| evidence_type | eligible | in sample |",
        "| --- | ---: | ---: |",
    ]
    elig = Counter(r["evidence_type"] for r in rows if r["eligible"])
    samp = Counter(r["evidence_type"] for r in sample)
    for et in EVIDENCE_TYPES:
        if elig[et] or samp[et]:
            lines.append(f"| {et} | {elig[et]} | {samp[et]} |")
    lines += [
        "",
        "## Selection rule",
        "",
        f"For each evidence type, sort eligible task ids lexicographically. "
        f"If n≤{K_PER_TYPE}, take all. If n>{K_PER_TYPE}, "
        f"`random.Random({SEED}).sample(ids, {K_PER_TYPE})`.",
        "",
        "Do not replace a sampled task that later fails dummy-probe identifiability. "
        "Record it as `rejected_not_identifiable` in the sample outcomes.",
        "",
        "Do not select on hypothesized support for attribution.",
        "",
    ]
    return "\n".join(lines)


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow(row)


def main() -> int:
    tasks = json.loads((OUT / "m0_scan.json").read_text())
    invariant = load_invariant()
    pinned = load_pinned()
    rows = [screen_one(t, pinned, invariant) for t in tasks]
    rows.sort(key=lambda r: (r["evidence_type"], r["id"]))
    sample = select_sample(rows)

    fields = [
        "id", "category", "evidence_type", "apps", "channel_invariant",
        "sqlite_mapped", "mapped_dbs", "cua_required", "gui_artifact",
        "instruction_pins_gold", "dv_from_answer", "identifiable",
        "eligible", "exclude_reason", "instruction",
    ]
    write_csv(OUT / "evidence_screening.csv", rows, fields)
    write_csv(
        OUT / "evidence_sample.csv",
        sample,
        fields + ["selection_rule"],
    )
    (OUT / "evidence_sample.json").write_text(
        json.dumps(
            {
                "seed": SEED,
                "k_per_type": K_PER_TYPE,
                "n_screened": len(rows),
                "n_eligible": sum(1 for r in rows if r["eligible"]),
                "n_sample": len(sample),
                "sample": sample,
            },
            indent=2,
        )
        + "\n"
    )
    (OUT / "evidence_funnel.md").write_text(funnel_md(rows, sample) + "\n")

    elig = sum(1 for r in rows if r["eligible"])
    print(f"screened {len(rows)}  eligible {elig}  sample {len(sample)}  seed {SEED}")
    print(f"wrote {OUT / 'evidence_screening.csv'}")
    print(f"wrote {OUT / 'evidence_sample.csv'}")
    print(f"wrote {OUT / 'evidence_funnel.md'}")
    for row in sample:
        print(f"  SAMPLE {row['evidence_type']:<28} {row['id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
