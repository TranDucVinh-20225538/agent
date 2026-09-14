"""List family-ADMIT unique keys. No trajectory JSON, no V, no rates."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ANN = ROOT / "schema" / "annotations.csv"
WA = ROOT / "schema" / "webarena.csv"
VWA = ROOT / "schema" / "visualwebarena.csv"


def _eval_types_map(path: Path) -> dict[str, str]:
    out = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            out[row["task_name"]] = row["eval_types"].strip()
    return out


def _parts(et: str) -> set[str]:
    return set(et.replace(",", " ").split())


def family_of(benchmark: str, task_id: str, wa: dict[str, str], vwa: dict[str, str]) -> tuple[str, str]:
    """Return (status, family_code). family_code in string|url|string_url|assistant|stop."""
    if benchmark == "workarena":
        return "STOP-INCOMPATIBLE", "stop"
    if benchmark == "assistantbench":
        return "ADMIT", "assistant"
    if benchmark == "webarena":
        et = wa.get(task_id, "")
        parts = _parts(et)
        if not et or parts & {"program_html", "page_image_query"}:
            return "STOP-INCOMPATIBLE", "stop"
        if parts == {"string_match"}:
            return "ADMIT", "string"
        if parts == {"url_match"}:
            return "ADMIT", "url"
        if parts == {"string_match", "url_match"}:
            return "ADMIT", "string_url"
        return "STOP-INCOMPATIBLE", "stop"
    if benchmark == "visualwebarena":
        canon = task_id.replace(".resized", "")
        et = vwa.get(canon, "")
        parts = _parts(et)
        if not et or parts & {"program_html", "page_image_query"}:
            return "STOP-INCOMPATIBLE", "stop"
        if parts == {"string_match"}:
            return "ADMIT", "string"
        if parts == {"url_match"}:
            return "ADMIT", "url"
        if parts == {"string_match", "url_match"}:
            return "ADMIT", "string_url"
        return "STOP-INCOMPATIBLE", "stop"
    return "STOP-INCOMPATIBLE", "stop"


def unique_keys(ann_path: Path):
    seen = set()
    with ann_path.open(newline="") as f:
        for row in csv.DictReader(f):
            key = (row["benchmark"], row["task_id"], row["model_name"], row["exp_name"])
            if key not in seen:
                seen.add(key)
                yield key


def main() -> None:
    wa = _eval_types_map(WA)
    vwa = _eval_types_map(VWA)
    status_c = Counter()
    fam_c = Counter()
    rows = []
    for bench, tid, model, exp in unique_keys(ANN):
        status, fam = family_of(bench, tid, wa, vwa)
        status_c[status] += 1
        if status == "ADMIT":
            fam_c[f"{bench}:{fam}"] += 1
            rel = f"cleaned/{bench}/{model}/{exp}/{tid}.json"
            rows.append((bench, tid, model, exp, fam, rel))
    out = ROOT / "schema" / "admitted_keys.csv"
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["benchmark", "task_id", "model_name", "exp_name", "family", "rel_path"])
        w.writerows(rows)
    print("unique", sum(status_c.values()), dict(status_c))
    print("admitted_by_family", dict(fam_c))
    print("wrote", out, "n", len(rows))


if __name__ == "__main__":
    main()
