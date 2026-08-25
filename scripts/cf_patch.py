"""Apply a counterfactual to one app database and record what moved.

The intervention is a targeted UPDATE on the records that generate the gold for
a single task. Authentication, the desktop and every unrelated application stay
untouched: `env.py` shows each app owns its own /data/<db>.sqlite, so a patch
scoped to one file cannot disturb the rest of the environment.

Usage
    python3 scripts/cf_patch.py --db path/to/dinoco-airlines.sqlite \\
        --task retrieval-f001 [--apply] [--out out/cf_runs]

Without --apply the probe runs and nothing is written, which is how a task is
checked for eligibility before touching the image.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "cf" / "interventions.json"


def load_spec(task_id: str) -> tuple[dict, str]:
    payload = json.loads(SPEC.read_text())
    for entry in payload["interventions"]:
        if entry["id"] == task_id:
            return entry, payload["_email"]
    raise SystemExit(f"no intervention defined for {task_id}")


def run_probe(conn: sqlite3.Connection, sql: str, email: str) -> list[tuple]:
    return conn.execute(sql, {"email": email}).fetchall()


def snapshot(conn: sqlite3.Connection) -> dict:
    """Row count and content hash per table, to bound what the patch touched."""
    import hashlib

    out = {}
    tables = [
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
    ]
    for table in tables:
        rows = conn.execute(f'SELECT * FROM "{table}"').fetchall()
        digest = hashlib.sha256(
            repr(sorted(repr(r) for r in rows)).encode()
        ).hexdigest()[:16]
        out[table] = {"rows": len(rows), "hash": digest}
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--task", required=True)
    parser.add_argument("--apply", action="store_true", help="write the patch")
    parser.add_argument("--out", type=Path, default=ROOT / "out" / "cf_runs")
    args = parser.parse_args()

    spec, email = load_spec(args.task)
    if not spec.get("probe"):
        raise SystemExit(f"{args.task} has no probe; it is a {spec['role']} entry")
    if not args.db.exists():
        raise SystemExit(f"database not found: {args.db}")

    conn = sqlite3.connect(args.db)
    before = run_probe(conn, spec["probe"], email)
    tables_before = snapshot(conn)
    print(f"probe before: {before}")

    if not args.apply:
        print("dry run; pass --apply to write the patch")
        return 0

    backup = args.db.with_suffix(args.db.suffix + ".pre_cf")
    if not backup.exists():
        shutil.copy2(args.db, backup)
        print(f"backup written: {backup}")

    with conn:
        for statement in spec["patch"]:
            conn.execute(statement, {"email": email})

    after = run_probe(conn, spec["probe"], email)
    tables_after = snapshot(conn)
    print(f"probe after:  {after}")

    touched = sorted(
        t for t in tables_before
        if tables_before[t] != tables_after.get(t)
    )
    print(f"tables touched: {touched or 'none'}")

    changed = before != after
    if spec["expect"].get("probe_changes") and not changed:
        print("FAILED: the patch did not move the gold; the probe or the "
              "determining records are wrong")

    args.out.mkdir(parents=True, exist_ok=True)
    record = {
        "id": args.task,
        "role": spec["role"],
        "db": args.db.name,
        "applied_at": datetime.now(timezone.utc).isoformat(),
        "patch": spec["patch"],
        "probe": spec["probe"],
        "probe_before": before,
        "probe_after": after,
        "gold_moved": changed,
        "rubric_text_edit_needed": spec["rubric_text_edit_needed"],
        "tables_touched": touched,
        "tables_unchanged": sorted(set(tables_before) - set(touched)),
    }
    path = args.out / f"{args.task}.json"
    path.write_text(json.dumps(record, indent=2, default=str))
    print(f"wrote {path}")
    return 0 if changed else 1


if __name__ == "__main__":
    sys.exit(main())
