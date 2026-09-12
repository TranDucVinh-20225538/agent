#!/usr/bin/env python3
"""Score CQ01–CQ06 against frozen p4_instrument.score. $0. No agents.

Does not edit score_q.py, p4_instrument.py, or Q/V/R. Property C1–C6 only.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
P4 = ROOT.parent
CQDIR = ROOT / "slate" / "cq"
OUT = ROOT / "out"
INSTR = P4 / "instrument" / "p4_instrument.py"
EXPECTED_INSTR = "c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59"

sys.path.insert(0, str(INSTR.parent))
from p4_instrument import score  # noqa: E402

CQ_IDS = [f"CQ{i:02d}" for i in range(1, 7)]
CONTROLS = ["C1", "C2", "C3", "C4", "C5", "C6"]
REQUIRED = {
    "C1": {"status": "HIT"},
    "C2": {"status": "MISS"},
    "C3": {"status": "ABSTAIN", "cause_in": {"absent", "no_anchor"}},
    "C4": {"status_in": {"MISS", "ABSTAIN"}},
    "C5": {"status": "HIT", "same_as": "C1"},
    "C6": {"same_as": "C5"},
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_cq(cid: str) -> dict:
    path = CQDIR / f"{cid}.json"
    if path.parent.resolve() != CQDIR.resolve():
        raise SystemExit(f"refusing non-CQ path {path}")
    obj = json.loads(path.read_text())
    if obj.get("id") != cid or obj.get("role") != "qualification":
        raise SystemExit(f"{cid}: not a CQ qualification cluster")
    return obj


def score_cluster(cluster: dict) -> dict:
    rows = {}
    for ctrl in CONTROLS:
        rows[ctrl] = score(
            cluster["observations"][ctrl],
            kind=cluster["kind"],
            gold=cluster["gold"],
            anchors=cluster["anchors"],
        )
    return rows


def property_failures(cid: str, rows: dict) -> list[str]:
    fails = []
    for ctrl in CONTROLS:
        spec = REQUIRED[ctrl]
        tr = rows[ctrl]
        if spec.get("status") and tr["status"] != spec["status"]:
            fails.append(f"{cid} {ctrl}: {tr['status']} != {spec['status']}")
        if spec.get("status_in") and tr["status"] not in spec["status_in"]:
            fails.append(f"{cid} {ctrl}: {tr['status']} not in {spec['status_in']}")
        if spec.get("cause_in") and tr.get("cause") not in spec["cause_in"]:
            fails.append(f"{cid} {ctrl}: cause {tr.get('cause')} not in {spec['cause_in']}")
        if spec.get("same_as"):
            other = rows[spec["same_as"]]
            if tr["status"] != other["status"] or tr["committed"] != other["committed"]:
                fails.append(f"{cid} {ctrl}: not identical to {spec['same_as']}")
            if ctrl == "C5" and tr.get("cause") != other.get("cause"):
                fails.append(f"{cid} C5: cause {tr.get('cause')} != C1 {other.get('cause')}")
    return fails


def main() -> int:
    instrument_sha = sha256_file(INSTR)
    if instrument_sha != EXPECTED_INSTR:
        raise SystemExit(f"instrument hash drifted: {instrument_sha}")
    pass_n = 0
    clusters = {}
    prop_fails: list[str] = []
    for cid in CQ_IDS:
        cluster = load_cq(cid)
        rows = score_cluster(cluster)
        clusters[cid] = {
            "kind": cluster["kind"],
            "component_id": cluster["component_id"],
            "controls": rows,
        }
        pf = property_failures(cid, rows)
        prop_fails.extend(pf)
        if not pf:
            pass_n += 1

    cq_pass = (not prop_fails) and pass_n == 6
    payload = {
        "scored_at": datetime.now(timezone.utc).isoformat(),
        "instrument_sha256": instrument_sha,
        "n_clusters": 6,
        "property_pass_clusters": pass_n,
        "property_failures": prop_fails,
        "clusters": clusters,
        "qualification": "PASS" if cq_pass else "FAIL",
        "v_star_scored": False,
        "q_scored": False,
        "p4b_modified": False,
        "instrument_modified": False,
        "api_spend_usd": 0,
        "agents_run": 0,
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "cq_qualification.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    lines = [
        "# P4-C CQ qualification",
        "",
        f"instrument_sha256 = `{instrument_sha}`",
        f"qualification = {'PASS' if cq_pass else 'FAIL'}",
        f"V* scored = no",
        f"Q* re-scored = no",
        f"API spend = $0",
        "",
        "| Cluster | kind | C1 | C2 | C3 | C4 | C5 | C6 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for cid in CQ_IDS:
        row = clusters[cid]["controls"]
        cells = " | ".join(
            f"{row[c]['status']}" + (f"/{row[c]['cause']}" if row[c].get("cause") else "")
            for c in CONTROLS
        )
        lines.append(f"| {cid} | {clusters[cid]['kind']} | {cells} |")
    lines += ["", "Property failures:"]
    if prop_fails:
        lines.extend(f"- {x}" for x in prop_fails)
    else:
        lines.append("- none")
    lines += [
        "",
        "C1–C6 vs frozen instrument. Phase 2 seal is BLOCKED until authorized.",
        "P4-B and Q/V were not modified.",
    ]
    (OUT / "cq_qualification.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if cq_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
