#!/usr/bin/env python3
"""Offline Paper-2 canonical DONE audit (Gate −1.5).

Reads existing CHECKPOINT.jsonl + traj archives. Does NOT rerun agents.
Does NOT modify CHECKPOINT.jsonl in place.

Writes per-slug:
  results/paper2_exec/<slug>/CHECKPOINT.canonical.jsonl
  results/paper2_exec/<slug>/canonical_audit.jsonl
  results/paper2_exec/<slug>/canonical_audit.md

Rule: VALID_DONE ⇔ canonical_last_action == \"DONE\"
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow import when run as script from repo root or scripts/
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_ROOT / "scripts"))

from paper2_traj_terminal import classify_leg, find_traj, load_traj_rows  # noqa: E402


def latest_checkpoint(ckpt: Path) -> dict:
    latest = {}
    if not ckpt.exists():
        return latest
    for line in ckpt.read_text().splitlines():
        if not line.strip():
            continue
        o = json.loads(line)
        latest[(o["task"], o["leg"])] = o
    return latest


def audit_slug(root: Path, slug: str) -> dict:
    out = root / "results" / "paper2_exec" / slug
    ckpt = out / "CHECKPOINT.jsonl"
    latest = latest_checkpoint(ckpt)
    records = []
    mismatches = []
    for key in sorted(latest.keys()):
        old = latest[key]
        archive = Path(old.get("archive_dir") or (out / old["task"] / old["leg"]))
        result_dir = Path(old.get("result_dir") or archive)
        traj = find_traj(archive) or find_traj(result_dir)
        steps = 0
        if traj:
            steps = len(load_traj_rows(traj))
        elif old.get("steps"):
            steps = int(old["steps"])
        cls = classify_leg(
            old_status=old.get("status"),
            traj_path=traj,
            has_steps=steps > 0,
        )
        rec = {
            "leg_index": old.get("leg_index"),
            "legs_total": old.get("legs_total", 57),
            "task": old["task"],
            "leg": old["leg"],
            "model": old.get("model"),
            "lane": old.get("lane"),
            "steps": steps,
            "result_dir": str(result_dir),
            "archive_dir": str(archive),
            "old_has_done_action": old.get("has_done_action"),
            **cls,
            # Canonical checkpoint fields for CHECKPOINT.canonical.jsonl
            "status": cls["new_classification"],
            "has_done_action": cls["has_done_action_canonical"],
            "finished_at": old.get("finished_at"),
            "reclassified_at": datetime.now(timezone.utc).isoformat(),
            "reclassification": "gate_1_5_canonical_last_action",
        }
        records.append(rec)
        if cls["mismatch"]:
            mismatches.append(rec)

    # Write artifacts
    out.mkdir(parents=True, exist_ok=True)
    audit_path = out / "canonical_audit.jsonl"
    canon_path = out / "CHECKPOINT.canonical.jsonl"
    md_path = out / "canonical_audit.md"

    with audit_path.open("w") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with canon_path.open("w") as f:
        for r in records:
            # slim checkpoint-shaped record
            payload = {
                "leg_index": r.get("leg_index"),
                "legs_total": r.get("legs_total"),
                "task": r["task"],
                "leg": r["leg"],
                "status": r["status"],
                "steps": r["steps"],
                "has_done_action": r["has_done_action"],
                "canonical_final_action": r["canonical_final_action"],
                "model": r.get("model"),
                "lane": r.get("lane"),
                "finished_at": r.get("finished_at"),
                "result_dir": r.get("result_dir"),
                "archive_dir": r.get("archive_dir"),
                "old_checkpoint_status": r["old_checkpoint_status"],
                "reclassification": r["reclassification"],
                "reclassified_at": r["reclassified_at"],
            }
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    by_old = {}
    by_new = {}
    for r in records:
        by_old[r["old_checkpoint_status"]] = by_old.get(r["old_checkpoint_status"], 0) + 1
        by_new[r["status"]] = by_new.get(r["status"], 0) + 1

    lines = [
        f"# Canonical audit — `{slug}`",
        "",
        f"- generated: {datetime.now(timezone.utc).isoformat()}",
        f"- source checkpoint: `{ckpt}`",
        f"- rule: `VALID_DONE ⇔ canonical_last_action == \"DONE\"`",
        f"- legs: {len(records)}",
        f"- old status counts: {by_old}",
        f"- new status counts: {by_new}",
        f"- mismatches: {len(mismatches)}",
        "",
        "## Mismatches",
        "",
    ]
    if not mismatches:
        lines.append("_none_")
    else:
        lines.append("| task | leg | old | new | canonical_final_action | reason |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for r in mismatches:
            lines.append(
                f"| {r['task']} | {r['leg']} | {r['old_checkpoint_status']} | "
                f"{r['new_classification']} | `{r['canonical_final_action']}` | "
                f"{r['mismatch_reason']} |"
            )
    lines.append("")
    lines.append(f"Artifacts: `{audit_path.name}`, `{canon_path.name}`")
    lines.append("")
    md_path.write_text("\n".join(lines) + "\n")

    return {
        "slug": slug,
        "n": len(records),
        "mismatches": len(mismatches),
        "by_old": by_old,
        "by_new": by_new,
        "audit": str(audit_path),
        "canonical_ckpt": str(canon_path),
        "md": str(md_path),
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    slugs = sys.argv[1:] or ["qwen35-9b", "qwen38-flash"]
    summary = []
    for slug in slugs:
        s = audit_slug(root, slug)
        summary.append(s)
        print(json.dumps(s, indent=2))
    summary_path = root / "results" / "paper2_exec" / "canonical_audit_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"wrote {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
