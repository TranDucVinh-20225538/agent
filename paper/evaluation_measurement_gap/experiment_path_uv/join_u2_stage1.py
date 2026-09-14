#!/usr/bin/env python3
"""Join 3 human Stage-1 CSVs. Lab only. Does not label. Does not write main.tex."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
PACK = ROOT / "annotators"

RATERS = {
    "vinh": PACK / "labels_VINH-1_all.csv",
    "toan": PACK / "labels_TOAN-1_all.csv",
    "hung": PACK / "labels_HUNG-1_all.csv",
}
CATS = ("DECISIVE", "NOT_DECISIVE", "UNCLEAR")


def load_labels(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for r in csv.DictReader(path.open()):
        lab = (r.get("isolation") or "").strip()
        if r.get("item_id") and lab in CATS:
            out[r["item_id"]] = lab
    return out


def majority_label(labels: list[str], hold: str = "UNCLEAR") -> str:
    votes = [x for x in labels if x and x != hold]
    if len(votes) < 2:
        return ""
    counts = Counter(votes)
    top = max(counts.values())
    winners = [k for k, c in counts.items() if c == top]
    if len(winners) != 1 or top < 2:
        return ""
    return winners[0]


def cohen(pairs: list[tuple[str, str]], labels: tuple[str, ...]) -> tuple[float, float, float]:
    n = len(pairs)
    po = sum(1 for a, b in pairs if a == b) / n
    ca = Counter(a for a, _ in pairs)
    cb = Counter(b for _, b in pairs)
    pe = sum((ca[k] / n) * (cb[k] / n) for k in labels)
    k = (po - pe) / (1 - pe) if pe < 1 else 1.0
    return po, pe, k


def fleiss(rows: list[list[str]], cats: tuple[str, ...]) -> float:
    n = len(rows)
    k = len(rows[0])
    N = n * k
    mat = []
    for row in rows:
        c = Counter(row)
        mat.append([c[cat] for cat in cats])
    p = [sum(col[j] for col in mat) / N for j in range(len(cats))]
    pbar = 0.0
    for col in mat:
        pbar += (sum(x * x for x in col) - k) / (k * (k - 1))
    pbar /= n
    pe = sum(x * x for x in p)
    return (pbar - pe) / (1 - pe) if pe < 1 else 1.0


def bin_d(x: str) -> str:
    return "D" if x == "DECISIVE" else "nD"


def main() -> None:
    need = [r["item_id"] for r in csv.DictReader((PACK / "stage1_all.csv").open())]
    sheet = {r["item_id"]: r for r in csv.DictReader((OUT / "u2_stage1_sheet.csv").open())}
    key = {
        (r["task_id"], r["frame_index"]): r
        for r in csv.DictReader((OUT / "u2_stage1_key.csv").open())
    }
    labs = {name: load_labels(p) for name, p in RATERS.items()}
    for name, d in labs.items():
        miss = [i for i in need if i not in d]
        if miss:
            raise SystemExit(f"{name} missing {len(miss)} e.g. {miss[:5]}")

    join_rows = []
    ratings3 = []
    ratings_bin = []
    for iid in need:
        s = sheet[iid]
        krow = key[(s["task_id"], s["frame_index"])]
        v, t, h = labs["vinh"][iid], labs["toan"][iid], labs["hung"][iid]
        maj = majority_label([v, t, h])
        join_rows.append(
            {
                "item_id": iid,
                "task_id": s["task_id"],
                "frame_index": s["frame_index"],
                "in_discard": krow["in_discard"],
                "role": krow["role"],
                "pilot6": krow["pilot6"],
                "vinh": v,
                "toan": t,
                "hung": h,
                "majority": maj,
                "n_decisive": str(sum(x == "DECISIVE" for x in (v, t, h))),
            }
        )
        ratings3.append([v, t, h])
        ratings_bin.append([bin_d(v), bin_d(t), bin_d(h)])

    k3 = fleiss(ratings3, CATS)
    kbin = fleiss(ratings_bin, ("D", "nD"))
    no_u = [
        [bin_d(a), bin_d(b), bin_d(c)]
        for a, b, c in ratings3
        if "UNCLEAR" not in (a, b, c)
    ]
    kbin_nou = fleiss(no_u, ("D", "nD")) if no_u else float("nan")

    pairs = {
        "vinh-toan": [(labs["vinh"][i], labs["toan"][i]) for i in need],
        "vinh-hung": [(labs["vinh"][i], labs["hung"][i]) for i in need],
        "toan-hung": [(labs["toan"][i], labs["hung"][i]) for i in need],
    }
    pairwise = {}
    for name, ps in pairs.items():
        pairwise[name] = {
            "3cat": cohen(ps, CATS)[2],
            "bin": cohen([(bin_d(a), bin_d(b)) for a, b in ps], ("D", "nD"))[2],
        }

    disc = [r for r in join_rows if r["in_discard"] == "1" and r["role"] == "event"]
    hold = [r for r in disc if not r["majority"]]
    den = [r for r in disc if r["majority"]]
    iso_n = sum(1 for r in den if r["majority"] == "DECISIVE")
    u2_iso = iso_n / len(den) if den else float("nan")

    fields = list(join_rows[0].keys())
    with (OUT / "u2_stage1_join.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(join_rows)

    by = defaultdict(lambda: Counter())
    for r in disc:
        by[r["task_id"]][r["majority"] or "HOLD"] += 1
        if r["majority"] == "DECISIVE":
            by[r["task_id"]]["discD"] += 1

    keep_d = defaultdict(int)
    for r in join_rows:
        if r["in_discard"] == "0" and r["majority"] == "DECISIVE":
            keep_d[r["task_id"]] += 1

    s2_disc = sum(
        1
        for r in join_rows
        if r["role"] == "event"
        and r["in_discard"] == "1"
        and r["majority"] == "DECISIVE"
    )
    s2_keep = sum(
        1
        for r in join_rows
        if r["role"] == "event"
        and r["in_discard"] == "0"
        and r["majority"] == "DECISIVE"
    )

    lines = [
        "# U2 Stage 1 — 3 human join",
        "",
        f"**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "**Status:** S1 JOINED. Not U2-irr. Not for `main.tex` until S2.",
        "Raters: VINH-1, TOAN-1, HUNG-1. Majority after holding UNCLEAR per codebook.",
        "",
        "## IRR",
        "",
        f"| | κ |",
        f"|---|---:|",
        f"| Fleiss 3-cat | {k3:.3f} |",
        f"| **Fleiss D vs not (primary)** | **{kbin:.3f}** |",
        f"| Fleiss D vs not, drop any-U items (n={len(no_u)}) | {kbin_nou:.3f} |",
        f"| Cohen Vinh–Toan / Vinh–Hung / Toan–Hung (D vs not) | {pairwise['vinh-toan']['bin']:.3f} / {pairwise['vinh-hung']['bin']:.3f} / {pairwise['toan-hung']['bin']:.3f} |",
        "",
        "## U2-iso (majority, discard frames in event episodes)",
        "",
        f"|D| = {len(disc)}. Hold (no majority) = {len(hold)}.",
        f"**U2-iso = {iso_n}/{len(den)} = {u2_iso:.3f}**.",
        "Secondary. Not M1a-shape. Not U2-irr.",
        "",
        f"S2 candidates: {s2_disc} discard DECISIVE + {s2_keep} keep foils = {s2_disc + s2_keep}.",
        "",
        "## Per-rater D count (all 1232)",
        "",
        "| Rater | D | ND | U |",
        "|---|---:|---:|---:|",
        f"| Vinh | {sum(1 for r in join_rows if r['vinh']=='DECISIVE')} | {sum(1 for r in join_rows if r['vinh']=='NOT_DECISIVE')} | {sum(1 for r in join_rows if r['vinh']=='UNCLEAR')} |",
        f"| Toan | {sum(1 for r in join_rows if r['toan']=='DECISIVE')} | {sum(1 for r in join_rows if r['toan']=='NOT_DECISIVE')} | {sum(1 for r in join_rows if r['toan']=='UNCLEAR')} |",
        f"| Hung | {sum(1 for r in join_rows if r['hung']=='DECISIVE')} | {sum(1 for r in join_rows if r['hung']=='NOT_DECISIVE')} | {sum(1 for r in join_rows if r['hung']=='UNCLEAR')} |",
        f"| Majority | {sum(1 for r in join_rows if r['majority']=='DECISIVE')} | {sum(1 for r in join_rows if r['majority']=='NOT_DECISIVE')} | hold {sum(1 for r in join_rows if not r['majority'])} |",
        "",
        "## Forbidden",
        "",
        "- Headline U2-iso as U2.",
        "- Fake a 4th rater. Copy one CSV as another rater.",
        "- Put these rates in `main.tex` before Stage 2.",
        "",
        f"Artifact: `out/u2_stage1_join.csv` ({len(join_rows)} rows).",
    ]
    (OUT / "u2_s1_human.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nwrote {OUT / 'u2_stage1_join.csv'} and {OUT / 'u2_s1_human.md'}", flush=True)


if __name__ == "__main__":
    main()
