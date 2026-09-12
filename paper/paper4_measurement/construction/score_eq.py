#!/usr/bin/env python3
"""Score EQ01–EQ06 against frozen score_v2. $0. No agents.

Does not edit p4_instrument.py or D01–D30. Property tests for DFC only.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
P4 = ROOT.parent
EQDIR = ROOT / "slate" / "eq"
OUT = ROOT / "out"
INSTR_V1 = P4 / "instrument" / "p4_instrument.py"
INSTR_V2 = P4 / "instrument" / "p4_instrument_v2.py"
EXPECTED_INSTR_V1 = "c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59"
EXPECTED_INSTR_V2 = "a87ac636a729d99852eb837583b24bce372ff49c196f2be7e39e4f750622fcf3"

sys.path.insert(0, str(INSTR_V2.parent))
sys.path.insert(0, str(ROOT))
from p4_instrument_v2 import score_v2  # noqa: E402
import transforms_d as T  # noqa: E402

EQ_IDS = [f"EQ{i:02d}" for i in range(1, 7)]
COMMON = [
    "HIT_CLAIM",
    "MISS_CLAIM",
    "NO_CLAIM",
    "AMBIGUOUS_TWO",
    "C3_NO_CLAIM",
    "C4_MARKUP",
    "C5_WORKING",
    "C6_WORKING",
    "C6_CLAIM",
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_eq(cid: str) -> dict:
    path = EQDIR / f"{cid}.json"
    if path.parent.resolve() != EQDIR.resolve():
        raise SystemExit(f"refusing non-DQ path {path}")
    obj = json.loads(path.read_text())
    if obj.get("id") != cid or obj.get("role") != "qualification":
        raise SystemExit(f"{cid}: not a DQ qualification cluster")
    if "anchors" in obj:
        raise SystemExit(f"{cid}: anchors not allowed")
    return obj


def score_obs(cluster: dict, key: str) -> dict:
    return score_v2(cluster["observations"][key], kind=cluster["kind"], gold=cluster["gold"])


def property_failures(cid: str, cluster: dict, rows: dict) -> list[str]:
    fails = []
    hit = rows["HIT_CLAIM"]
    if hit["status"] != "HIT":
        fails.append(f"{cid} HIT_CLAIM: {hit}")
    if rows["MISS_CLAIM"]["status"] != "MISS":
        fails.append(f"{cid} MISS_CLAIM: {rows['MISS_CLAIM']}")
    if rows["NO_CLAIM"]["status"] != "ABSTAIN" or rows["NO_CLAIM"].get("cause") != "no_claim":
        fails.append(f"{cid} NO_CLAIM: {rows['NO_CLAIM']}")
    amb = rows["AMBIGUOUS_TWO"]
    if amb["status"] != "ABSTAIN" or amb.get("cause") != "ambiguous_claim":
        fails.append(f"{cid} AMBIGUOUS_TWO: {amb}")
    if "AMBIGUOUS_LINE" in rows:
        al = rows["AMBIGUOUS_LINE"]
        if al["status"] != "ABSTAIN" or al.get("cause") != "ambiguous_claim":
            fails.append(f"{cid} AMBIGUOUS_LINE: {al}")
    if rows["C3_NO_CLAIM"]["status"] == "HIT":
        fails.append(f"{cid} C3_NO_CLAIM is HIT")
    if rows["C4_MARKUP"]["status"] == "HIT":
        fails.append(f"{cid} C4_MARKUP is HIT")
    for key in ("C5_WORKING", "C6_WORKING"):
        tr = rows[key]
        if tr["status"] != hit["status"] or tr.get("committed") != hit.get("committed"):
            fails.append(f"{cid} {key}: not identical to HIT_CLAIM")
        if tr.get("cause") != hit.get("cause"):
            fails.append(f"{cid} {key}: cause {tr.get('cause')} != HIT {hit.get('cause')}")
    if rows["C6_CLAIM"]["status"] != "MISS":
        fails.append(f"{cid} C6_CLAIM: {rows['C6_CLAIM']}")

    tau = cluster["observations"]["HIT_CLAIM"]
    irr_a, irr_b = T.c6_working_pair(tau, "Spare citole note lists unused context.", "Spare shawm note lists unused context.")
    sa = score_v2(irr_a, kind=cluster["kind"], gold=cluster["gold"])
    sb = score_v2(irr_b, kind=cluster["kind"], gold=cluster["gold"])
    if sa != hit or sb != hit:
        fails.append(f"{cid} transform working_irr changed Y: {sa} {sb}")
    dropped = score_v2(T.c3_drop_claim(tau), kind=cluster["kind"], gold=cluster["gold"])
    if dropped["status"] == "HIT":
        fails.append(f"{cid} transform c3_drop_claim is HIT")
    marked = score_v2(T.c4_markup(tau, cluster["gold"]), kind=cluster["kind"], gold=cluster["gold"])
    if marked["status"] == "HIT":
        fails.append(f"{cid} transform c4_markup is HIT")
    replaced = score_v2(T.replace_claim(tau, cluster["wrong"]), kind=cluster["kind"], gold=cluster["gold"])
    if replaced["status"] != "MISS":
        fails.append(f"{cid} transform replace_claim: {replaced}")
    chan = score_v2(T.chan_unterminated(tau), kind=cluster["kind"], gold=cluster["gold"])
    if chan["status"] != "ABSTAIN" or chan.get("cause") != "channel_indeterminate":
        fails.append(f"{cid} transform chan_unterminated: {chan}")
    return fails


def main() -> int:
    errors: list[str] = []
    v1 = sha256_file(INSTR_V1)
    v2 = sha256_file(INSTR_V2)
    if v1 != EXPECTED_INSTR_V1:
        errors.append(f"v1 instrument hash drifted: {v1}")
    if v2 != EXPECTED_INSTR_V2:
        errors.append(f"v2 instrument hash drifted: {v2}")

    kinds_seen: dict[str, int] = {}
    texts_per_kind: dict[str, int] = {}
    cluster_rows = []
    n_pass = 0
    for cid in EQ_IDS:
        cluster = load_eq(cid)
        kind = cluster["kind"]
        kinds_seen[kind] = kinds_seen.get(kind, 0) + 1
        missing = [k for k in COMMON if k not in cluster["observations"]]
        if missing:
            errors.append(f"{cid}: missing observations {missing}")
            continue
        if kind in {"money_usd", "integer"} and "AMBIGUOUS_LINE" not in cluster["observations"]:
            errors.append(f"{cid}: money/integer missing AMBIGUOUS_LINE")
        rows = {k: score_obs(cluster, k) for k in cluster["observations"]}
        texts_per_kind[kind] = texts_per_kind.get(kind, 0) + len(rows)
        fails = property_failures(cid, cluster, rows)
        ok = not fails
        if ok:
            n_pass += 1
        else:
            errors.extend(fails)
        cluster_rows.append(
            {
                "id": cid,
                "kind": kind,
                "n_texts": len(rows),
                "pass": ok,
                "rows": rows,
                "failures": fails,
            }
        )

    for kind, n in texts_per_kind.items():
        if n < 6:
            errors.append(f"{kind}: only {n} authored last-texts (<6)")
    for kind in ("money_usd", "integer", "entity", "categorical"):
        if kind not in texts_per_kind:
            errors.append(f"missing kind {kind}")

    gate = "PASS" if n_pass == 6 and not errors else "FAIL"
    payload = {
        "phase": 2,
        "workstream": "P4-D",
        "object": "Q3",
        "qualification": gate,
        "property_pass_clusters": n_pass,
        "n_clusters": 6,
        "texts_per_kind": texts_per_kind,
        "instrument_v1_sha256": v1,
        "instrument_v2_sha256": v2,
        "agents_run": 0,
        "api_spend_usd": 0,
        "errors": errors,
        "clusters": cluster_rows,
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "eq_qualification.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# P4-D Q3 synthetic qualification",
        "",
        f"status = **{gate}**",
        f"property_pass_clusters = {n_pass} / 6",
        f"texts_per_kind = {texts_per_kind}",
        f"instrument_v2_sha256 = `{v2}`",
        f"api_spend_usd = 0",
        "",
    ]
    if errors:
        lines += ["## Errors", ""]
        for e in errors:
            lines.append(f"- {e}")
    else:
        lines += ["No Q3 errors.", ""]
    (OUT / "eq_qualification.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if gate == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
