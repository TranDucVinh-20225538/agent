#!/usr/bin/env python3
"""Single sealed V* pass against the frozen §2 instrument. $0. No agents.

Does not modify p4_instrument.py, V*, params_v, or the seal.
Aborts if the instrument sha256 is not the freeze hash.
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VDIR = ROOT / "construction" / "sealed" / "v"
OUT = ROOT / "construction" / "out"
INSTR = Path(__file__).resolve().parent / "p4_instrument.py"
SEAL = ROOT / "construction" / "sealed" / "V_SEAL.json"
EXPECTED_INSTR = "c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59"
EXPECTED_SEAL = "26df37a1fe10b05ebb674fea28cf2ac03dcc7772227df9de902f4aed08cb4189"
EXPECTED_COMMIT = "c35e828db89a9c7eb9d479601215a29221f5d744"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from p4_instrument import score  # noqa: E402

V_IDS = [f"V{i:02d}" for i in range(1, 21)]
CONTROLS = ["C1", "C2", "C3", "C4", "C5", "C6"]
PROPERTIES = CONTROLS[:]

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


def combined_v_hash() -> str:
    h = hashlib.sha256()
    for cid in V_IDS:
        digest = sha256_file(VDIR / f"{cid}.json")
        h.update(digest.encode())
        h.update(b"\n")
    return h.hexdigest()


def property_holds(ctrl: str, rows: dict) -> bool:
    spec = REQUIRED[ctrl]
    tr = rows[ctrl]
    if spec.get("status") and tr["status"] != spec["status"]:
        return False
    if spec.get("status_in") and tr["status"] not in spec["status_in"]:
        return False
    if spec.get("cause_in") and tr.get("cause") not in spec["cause_in"]:
        return False
    if spec.get("same_as"):
        other = rows[spec["same_as"]]
        if tr["status"] != other["status"] or tr["committed"] != other["committed"]:
            return False
        if ctrl == "C5" and tr.get("cause") != other.get("cause"):
            return False
    return True


def main() -> int:
    instr_sha = sha256_file(INSTR)
    if instr_sha != EXPECTED_INSTR:
        raise SystemExit(f"instrument hash {instr_sha} != freeze {EXPECTED_INSTR}")
    seal = json.loads(SEAL.read_text())
    if seal["combined_sha256"] != EXPECTED_SEAL:
        raise SystemExit("V_SEAL.json combined hash drifted before scoring")
    before = combined_v_hash()
    if before != EXPECTED_SEAL:
        raise SystemExit("V* file hashes drifted before scoring")

    clusters = {}
    holds = {p: 0 for p in PROPERTIES}
    fails: list[str] = []
    abstain_causes: Counter[str] = Counter()
    n_all_six = 0

    for cid in V_IDS:
        path = VDIR / f"{cid}.json"
        obj = json.loads(path.read_text())
        if obj.get("id") != cid or obj.get("role") != "held-out":
            raise SystemExit(f"{cid}: not a sealed held-out cluster")
        rows = {}
        for ctrl in CONTROLS:
            rows[ctrl] = score(
                obj["observations"][ctrl],
                kind=obj["kind"],
                gold=obj["gold"],
                anchors=obj["anchors"],
            )
            if rows[ctrl]["status"] == "ABSTAIN":
                abstain_causes[rows[ctrl]["cause"]] += 1
        H = {p: int(property_holds(p, rows)) for p in PROPERTIES}
        for p, h in H.items():
            holds[p] += h
            if not h:
                fails.append(
                    f"{cid} {p}: {rows[p]['status']}/{rows[p].get('cause')} "
                    f"committed={rows[p].get('committed')!r}"
                )
        all_six = all(H.values())
        if all_six:
            n_all_six += 1
        clusters[cid] = {
            "kind": obj["kind"],
            "component_id": obj["component_id"],
            "v_markup_dialect": obj.get("v_markup_dialect"),
            "controls": rows,
            "H": H,
            "all_six": all_six,
        }

    after = combined_v_hash()
    if after != before or sha256_file(INSTR) != EXPECTED_INSTR:
        raise SystemExit("instrument or V* changed during scoring")

    n = 20
    hold_rate = {p: holds[p] / n for p in PROPERTIES}
    v_pass = all(hold_rate[p] == 1.0 for p in PROPERTIES)
    payload = {
        "scored_at": datetime.now(timezone.utc).isoformat(),
        "freeze_commit": EXPECTED_COMMIT,
        "instrument_sha256": instr_sha,
        "v_seal_combined_sha256": EXPECTED_SEAL,
        "v_star_scored": True,
        "n_clusters": n,
        "n_clusters_all_six": n_all_six,
        "hold_counts": holds,
        "hold_rate": hold_rate,
        "qualification": "PASS" if v_pass else "FAIL",
        "conjunction": "one H(p,c)=0 fails V*",
        "failures": fails,
        "abstain_causes": dict(abstain_causes),
        "api_spend_usd": 0,
        "instrument_modified": False,
        "v_star_modified": False,
        "clusters": clusters,
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "v_score.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    lines = [
        "# P4 V* single sealed pass",
        "",
        f"freeze_commit = `{EXPECTED_COMMIT}`",
        f"instrument_sha256 = `{instr_sha}`",
        f"V seal = `{EXPECTED_SEAL}`",
        f"qualification = {'PASS' if v_pass else 'FAIL'}",
        f"clusters with all six properties = {n_all_six} / 20",
        f"API spend = $0",
        f"instrument modified = no",
        f"V* modified = no",
        "",
        "| Cluster | kind | dialect | C1 | C2 | C3 | C4 | C5 | C6 | all_six |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for cid in V_IDS:
        row = clusters[cid]["controls"]
        cells = " | ".join(
            f"{row[c]['status']}/{row[c]['cause']}" for c in CONTROLS
        )
        lines.append(
            f"| {cid} | {clusters[cid]['kind']} | {clusters[cid].get('v_markup_dialect')} | {cells} | {clusters[cid]['all_six']} |"
        )
    lines += ["", "Hold-rate r_p = (1/20) sum H(p,c)", ""]
    lines.append("| property | holds | r_p |")
    lines.append("|---|---|---|")
    for p in PROPERTIES:
        lines.append(f"| {p} | {holds[p]} / 20 | {hold_rate[p]:.2f} |")
    lines += ["", "ABSTAIN causes:"]
    if abstain_causes:
        for cause, k in sorted(abstain_causes.items()):
            lines.append(f"- `{cause}`: {k}")
    else:
        lines.append("- none")
    lines += ["", "Failures:"]
    if fails:
        lines.extend(f"- {x}" for x in fails)
    else:
        lines.append("- none")
    lines += [
        "",
        "Agent validation not opened. Stop after this pass.",
    ]
    (OUT / "v_qualification.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if v_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
