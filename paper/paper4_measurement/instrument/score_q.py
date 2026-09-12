#!/usr/bin/env python3
"""Score Q01–Q06 only. Refuses sealed V*. $0. No agents."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QDIR = ROOT / "construction" / "slate" / "q"
OUT = ROOT / "construction" / "out"
INSTR = Path(__file__).resolve().parent / "p4_instrument.py"
TRACES = ROOT / "construction" / "out" / "q_spec_traces.json"
SEAL = ROOT / "construction" / "sealed" / "V_SEAL.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from p4_instrument import refuse_v_path, score  # noqa: E402

Q_IDS = [f"Q{i:02d}" for i in range(1, 7)]
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
    refuse_v_path(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_q(cid: str) -> dict:
    path = QDIR / f"{cid}.json"
    refuse_v_path(path)
    if path.parent.resolve() != QDIR.resolve():
        raise SystemExit(f"refusing non-Q path {path}")
    obj = json.loads(path.read_text())
    if obj.get("id") != cid or obj.get("role") != "qualification":
        raise SystemExit(f"{cid}: not a qualification cluster")
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


def vs_traces(rows: dict, traces: dict) -> list[str]:
    fails = []
    for ctrl in CONTROLS:
        got, exp = rows[ctrl], traces[ctrl]
        for k in ("status", "cause", "committed"):
            if got.get(k) != exp.get(k):
                fails.append(f"{ctrl}.{k}: got {got.get(k)!r} expected {exp.get(k)!r}")
    return fails


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def main() -> int:
    refuse_v_path(QDIR)
    refuse_v_path(TRACES)
    refuse_v_path(SEAL)
    traces = json.loads(TRACES.read_text())
    seal_meta = json.loads(SEAL.read_text())
    instrument_sha = sha256_file(INSTR)
    pass_n = 0
    clusters = {}
    prop_fails: list[str] = []
    trace_fails: list[str] = []
    for cid in Q_IDS:
        cluster = load_q(cid)
        rows = score_cluster(cluster)
        clusters[cid] = {
            "kind": cluster["kind"],
            "component_id": cluster["component_id"],
            "controls": rows,
        }
        pf = property_failures(cid, rows)
        tf = vs_traces(rows, traces[cid])
        prop_fails.extend(pf)
        if tf:
            trace_fails.append(f"{cid}: " + "; ".join(tf))
        if not pf:
            pass_n += 1

    payload = {
        "scored_at": datetime.now(timezone.utc).isoformat(),
        "instrument_sha256": instrument_sha,
        "q_spec_traces_sha256": sha256_file(TRACES),
        "v_seal_combined_sha256_unopened": seal_meta["combined_sha256"],
        "n_clusters": 6,
        "property_pass_clusters": pass_n,
        "property_failures": prop_fails,
        "spec_trace_mismatches": trace_fails,
        "clusters": clusters,
        "v_star_scored": False,
        "api_spend_usd": 0,
    }
    OUT.mkdir(exist_ok=True)
    initial_path = OUT / "q_score_initial.json"
    write_json(initial_path, payload)

    bugfix = False
    final = payload
    if trace_fails:
        # Protocol: mismatch to spec-trace is an implementation bug.
        # This driver does not retune §2 against properties. A bugfix would
        # edit p4_instrument.py to match §2, then re-score once.
        # If we are here, the implementation disagrees with the construction
        # traces; the caller must inspect the mismatches, not V*.
        pass

    q_pass = (not prop_fails) and (not trace_fails) and pass_n == 6
    final_path = OUT / "q_score_final.json"
    write_json(final_path, {**final, "bugfix_to_spec": bugfix, "qualification": "PASS" if q_pass else "FAIL"})

    lines = [
        "# P4 Q qualification",
        "",
        f"instrument_sha256 = `{instrument_sha}`",
        f"V seal (unopened) = `{seal_meta['combined_sha256']}`",
        f"bugfix-to-spec = {bugfix}",
        f"qualification = {'PASS' if q_pass else 'FAIL'}",
        f"V* scored = no",
        f"API spend = $0",
        "",
        "| Cluster | kind | C1 | C2 | C3 | C4 | C5 | C6 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for cid in Q_IDS:
        row = clusters[cid]["controls"]
        cells = " | ".join(
            f"{row[c]['status']}" + (f"/{row[c]['cause']}" if row[c].get("cause") else "")
            for c in CONTROLS
        )
        lines.append(f"| {cid} | {clusters[cid]['kind']} | {cells} |")
    lines += ["", "Spec-trace mismatches:"]
    if trace_fails:
        lines.extend(f"- {x}" for x in trace_fails)
    else:
        lines.append("- none")
    lines += ["", "Property failures:"]
    if prop_fails:
        lines.extend(f"- {x}" for x in prop_fails)
    else:
        lines.append("- none")
    licensed = q_pass
    lines += [
        "",
        f"Licensed to score V* = {'yes (after freeze commit)' if licensed else 'no'}",
        "Stop after Q. V* not opened.",
    ]
    (OUT / "q_qualification.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if q_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
