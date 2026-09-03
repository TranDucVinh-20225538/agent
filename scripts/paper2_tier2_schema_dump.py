#!/usr/bin/env python3
"""Dump guest schema/sample rows needed to fill Paper 2 Tier 2 SQL.

No agent. No patches. Snapshot-free read-only probes against a clean boot.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("AGENT_ROOT", Path(__file__).resolve().parents[1]))
HARNESS = ROOT / "external/MyPCBench-main/agent-harness"
OUT = ROOT / "out" / "paper2_tier2_schema_dump.json"
EMAIL = "michael.scott@dundermifflin.com"

QUERIES = {
    "sqlite_files": "ls -1 /data/*.sqlite",
    "lockedin_tables": "sqlite3 /data/lockedin.sqlite \".tables\"",
    "lockedin_schema": "sqlite3 /data/lockedin.sqlite \".schema\"",
    "lockedin_sample": (
        "sqlite3 -json /data/lockedin.sqlite "
        "\"SELECT * FROM sqlite_master WHERE type='table'\""
    ),
    "speedtax_w2": (
        f"sqlite3 -json /data/speedtax.sqlite "
        f"\"SELECT d.field_name, d.field_value FROM tax_data d "
        f"JOIN tax_returns tr ON tr.id = d.return_id "
        f"WHERE tr.user_email = '{EMAIL}' AND tr.tax_year = 2025 "
        f"AND (lower(d.field_name) LIKE '%w2%' OR lower(d.field_name) LIKE '%wage%' "
        f"OR lower(d.field_name) LIKE '%salary%' OR lower(d.field_name) LIKE '%employer%') "
        f"ORDER BY d.field_name\""
    ),
    "cheskepdia_schema": "sqlite3 /data/cheskepdia.sqlite \".schema\"",
    "cheskepdia_bookings": (
        f"sqlite3 -json /data/cheskepdia.sqlite "
        f"\"SELECT id, property_name, location, address, check_in, check_out, "
        f"total_price, confirmation_code, host_name, status "
        f"FROM bookings WHERE user_email = '{EMAIL}' ORDER BY check_in\""
    ),
    "dinoco_schema": "sqlite3 /data/dinoco-airlines.sqlite \".schema\"",
    "dinoco_jamaica": (
        f"sqlite3 -json /data/dinoco-airlines.sqlite "
        f"\"SELECT * FROM bookings WHERE user_email = '{EMAIL}' "
        f"AND (lower(ifnull(destination,'')) LIKE '%jamaica%' "
        f"OR lower(ifnull(origin,'')) LIKE '%jamaica%' "
        f"OR lower(ifnull(route,'')) LIKE '%jamaica%' "
        f"OR lower(ifnull(confirmation_code,'')) LIKE '%mbj%' "
        f"OR lower(cast(id as text)) LIKE '%jama%') LIMIT 20\""
    ),
    "dinoco_all_cols_probe": (
        "sqlite3 /data/dinoco-airlines.sqlite "
        "\"PRAGMA table_info(bookings);\""
    ),
    "dinoco_sample": (
        f"sqlite3 -json /data/dinoco-airlines.sqlite "
        f"\"SELECT * FROM bookings WHERE user_email = '{EMAIL}' LIMIT 15\""
    ),
    "hoolichat_ls": "ls -la /data/*chat* /data/*hooli* /data/*message* 2>/dev/null; ls /data/*.sqlite",
    "mail_tables": "sqlite3 /data/mail.sqlite \".tables\"",
}


def main() -> int:
    sys.path.insert(0, str(HARNESS))
    from env import MyPCBenchEnv

    qcow2 = os.environ.get("MYPCBENCH_QCOW2")
    if not qcow2:
        raise SystemExit("MYPCBENCH_QCOW2 unset")
    env = MyPCBenchEnv(
        backend="qemu",
        qcow2_path=qcow2,
        headless=True,
        persona="michael_scott",
        container_name=f"mypcbench-paper2-schema-{os.getpid()}",
    )
    print("reset()...", flush=True)
    env.reset()
    print(f"ready {env.base_url}", flush=True)
    results = {"written_at": datetime.now(timezone.utc).isoformat(), "email": EMAIL}
    try:
        for name, cmd in QUERIES.items():
            print(f"--- {name} ---", flush=True)
            r = env._execute_shell(cmd)
            out = ((r.get("output") or "") + (r.get("error") or "")).strip()
            results[name] = out[:20000]
            print(out[:1500], flush=True)
        # follow-ups depending on lockedin tables
        tables = results.get("lockedin_tables", "")
        for t in tables.split():
            cmd = f"sqlite3 -json /data/lockedin.sqlite \"SELECT * FROM {t} LIMIT 8\""
            r = env._execute_shell(cmd)
            out = ((r.get("output") or "") + (r.get("error") or "")).strip()
            results[f"lockedin_{t}_sample"] = out[:8000]
            print(f"lockedin.{t}: {out[:400]}", flush=True)
        # dinoco other tables if bookings empty of jamaica
        r = env._execute_shell("sqlite3 /data/dinoco-airlines.sqlite \".tables\"")
        tables = ((r.get("output") or "") + (r.get("error") or "")).strip()
        results["dinoco_tables"] = tables
        for t in tables.split():
            r = env._execute_shell(
                f"sqlite3 /data/dinoco-airlines.sqlite \"PRAGMA table_info({t});\""
            )
            results[f"dinoco_{t}_cols"] = ((r.get("output") or "") + (r.get("error") or "")).strip()
            r = env._execute_shell(
                f"sqlite3 -json /data/dinoco-airlines.sqlite "
                f"\"SELECT * FROM {t} WHERE "
                f"lower(ifnull(cast(user_email as text),'')) = '{EMAIL}' "
                f"OR lower(ifnull(cast(email as text),'')) = '{EMAIL}' "
                f"LIMIT 5\""
            )
            results[f"dinoco_{t}_sample"] = (
                ((r.get("output") or "") + (r.get("error") or "")).strip()[:8000]
            )
    finally:
        try:
            env.close()
        except Exception:
            pass
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(results, indent=2) + "\n")
        print(f"wrote {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
