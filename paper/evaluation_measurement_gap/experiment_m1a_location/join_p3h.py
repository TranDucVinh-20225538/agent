#!/usr/bin/env python3
"""Join A0 Stage-1 labels to Stage-2 and locked rates. Not 3-rater official."""

from __future__ import annotations

import csv
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "evidence-loss-audit" / "src"),
)
from evidence_loss_audit.chain import classify_links

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out_p3h"
SEED = 20260913


def main() -> None:
    key = list(csv.DictReader((OUT / "p3h_stage1_key.csv").open()))
    lab1 = {r["item_id"]: r for r in csv.DictReader((OUT / "p3h_stage1_labels_A0.csv").open())}

    by_dir_frames: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    last_of: dict[tuple[str, str, str], int] = {}
    for r in key:
        d = (r["lane"], r["task"], r["leg"])
        fi = int(r["frame_index"])
        if fi not in by_dir_frames[d]:
            by_dir_frames[d].append(fi)
        if int(r["is_last"]):
            last_of[d] = fi

    # Stage-2 targets: all DECISIVE
    targets = []
    for r in key:
        iso = lab1[r["item_id"]]["isolation"]
        if iso != "DECISIVE":
            continue
        d = (r["lane"], r["task"], r["leg"])
        last = last_of[d]
        gallery = [i for i in by_dir_frames[d] if i != int(r["frame_index"])]
        targets.append(
            {
                **r,
                "isolation": iso,
                "gallery_frames": gallery,
                "last_frame": last,
                "foil": int(int(r["is_last"]) == 1),
            }
        )

    rng = random.Random(SEED)
    for t in targets:
        g = list(t["gallery_frames"])
        rng.shuffle(g)
        t["gallery_frames"] = g

    # A0 Stage-2: last-frame visual vs target evidence (viewed)
    # Keys: (lane, task, leg, component, target_frame) → EQUIVALENT / NOT
    s2_a0 = {
        # liquid 66493 still on last
        ("flash", "counterfactual-f010", "G0", "liquid_cash", 15): "EQUIVALENT",
        ("flash", "counterfactual-f010", "G0", "liquid_cash", 16): "EQUIVALENT",
        ("flash", "counterfactual-f010", "G0", "liquid_cash", 17): "EQUIVALENT",
        # BatBucks 420 still on last
        ("flash", "aggregation-f020", "G1", "batbucks_cash", 30): "EQUIVALENT",
        ("flash", "aggregation-f020", "G1", "batbucks_cash", 31): "EQUIVALENT",
        ("gpt", "aggregation-f020", "G0", "batbucks_cash", 53): "EQUIVALENT",
        ("gpt", "aggregation-f020", "G0", "batbucks_cash", 54): "EQUIVALENT",
        # 64.88 not on last accounts dump
        ("flash", "counterfactual-f013", "G0", "batbucks_dividends", 48): "NOT_EQUIVALENT",
        ("flash", "counterfactual-f013", "G0", "batbucks_dividends", 49): "NOT_EQUIVALENT",
        # 16413 is the last frame itself
        ("flash", "counterfactual-f013", "G0", "gringotts_savings", 56): "NOT_EQUIVALENT",
        # 3282 only on last
        ("flash", "counterfactual-f013", "G1", "gringotts_savings", 67): "NOT_EQUIVALENT",
        # DN-87856 still on last
        ("flash", "retrieval-f009", "G1", "nyc_flight_confirmation", 31): "EQUIVALENT",
        ("flash", "retrieval-f009", "G1", "nyc_flight_confirmation", 32): "EQUIVALENT",
        ("flash", "retrieval-f009", "G1", "nyc_flight_confirmation", 40): "EQUIVALENT",
        # host name not on last price page
        ("flash", "retrieval-f010", "G1", "host_name", 12): "NOT_EQUIVALENT",
    }

    st2_key = []
    st2_ann = []
    rng2 = random.Random(SEED)
    pack = targets[:]
    rng2.shuffle(pack)
    for n, t in enumerate(pack, start=1):
        item = f"P3H-S2-{n:04d}"
        k = (t["lane"], t["task"], t["leg"], t["component"], int(t["frame_index"]))
        eq = s2_a0[k]
        t["item_id_s2"] = item
        t["equivalence"] = eq
        st2_key.append(
            {
                "item_id": item,
                "s1_item_id": t["item_id"],
                "lane": t["lane"],
                "task": t["task"],
                "leg": t["leg"],
                "component": t["component"],
                "target_frame": t["frame_index"],
                "is_last": t["is_last"],
                "foil": t["foil"],
                "gallery_frames": ",".join(str(i) for i in t["gallery_frames"]),
                "equivalence": eq,
            }
        )
        st2_ann.append(
            {
                "item_id": item,
                "task": t["task"],
                "leg": t["leg"],
                "target_png": t["png_path"],
                "gallery_note": "other drawn frames of this dir; last is keep analogue",
            }
        )

    with (OUT / "p3h_stage2_key.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(st2_key[0]))
        w.writeheader()
        w.writerows(st2_key)
    with (OUT / "p3h_stage2_sheet.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(st2_ann[0]))
        w.writeheader()
        w.writerows(st2_ann)

    # Rates on drawn non-last frames (13 rows × 2 = 26)
    nonlast = [r for r in key if int(r["is_last"]) == 0]
    n_nl = len(nonlast)
    n_iso = 0
    n_irr = 0
    n_red = 0
    n_hold = 0
    rows_out = []
    for r in nonlast:
        iso = lab1[r["item_id"]]["isolation"]
        eq = None
        if iso == "DECISIVE":
            k = (r["lane"], r["task"], r["leg"], r["component"], int(r["frame_index"]))
            eq = s2_a0[k]
        link = classify_links(
            n_items=3,
            keep_cap=1,
            in_discard=True,
            isolation=iso,
            equivalence=eq,
        )
        if iso == "UNCLEAR":
            n_hold += 1
        if link.isolation_decisive:
            n_iso += 1
        if link.irrecoverable:
            n_irr += 1
        if link.redundant:
            n_red += 1
        rows_out.append(
            {
                "item_id": r["item_id"],
                "row_id": r["row_id"],
                "frame_index": r["frame_index"],
                "is_last": r["is_last"],
                "isolation": iso,
                "equivalence": eq or "",
                "class": link.note,
            }
        )

    with (OUT / "p3h_join_A0.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0]))
        w.writeheader()
        w.writerows(rows_out)

    den = n_nl - n_hold
    summary = {
        "rater": "A0-agent-draft",
        "official_3human": False,
        "n_stage1_items": len(key),
        "n_nonlast": n_nl,
        "n_hold_unclear": n_hold,
        "P3H-iso": {"num": n_iso, "den": den},
        "P3H-red": {"num": n_red, "den": n_iso},
        "P3H-irr": {"num": n_irr, "den": den},
        "irrecoverable_rows": [
            r["row_id"] + f"#f{r['frame_index']}"
            for r in rows_out
            if r["class"] == "irrecoverable"
        ],
    }
    (OUT / "p3h_summary_A0.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
