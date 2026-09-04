#!/usr/bin/env python3
"""Dump guest schema for Paper 2 Tier 3 fill (mail / chili file / speedtax)."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("AGENT_ROOT", Path(__file__).resolve().parents[1]))
HARNESS = ROOT / "external/MyPCBench-main/agent-harness"
OUT = ROOT / "out" / "paper2_tier3_schema_dump.json"
EMAIL = "michael.scott@dundermifflin.com"

QUERIES = {
    "mail_tables": "sqlite3 /data/mail.sqlite \".tables\"",
    "mail_schema_emails": "sqlite3 /data/mail.sqlite \".schema emails\"",
    "mail_schema_sent": "sqlite3 /data/mail.sqlite \".schema sent\"",
    "mail_sample_emails": "sqlite3 -json /data/mail.sqlite \"SELECT * FROM emails LIMIT 2\"",
    "mail_sample_sent": "sqlite3 -json /data/mail.sqlite \"SELECT * FROM sent LIMIT 2\"",
    "chili_ls": (
        "ls -la /home/user/Downloads/ 2>/dev/null | head -50; "
        "ls -la /home/user/Downloads/*[Cc]hili* /home/user/Downloads/*[Rr]eceipt* 2>/dev/null"
    ),
    "chili_cat": (
        "for f in /home/user/Downloads/*[Cc]hili* /home/user/Downloads/Chilis* "
        "/home/user/Downloads/*Receipt*; do "
        "  [ -f \"$f\" ] || continue; echo ===== \"$f\" =====; head -50 \"$f\"; "
        "done"
    ),
    "vault_chili": (
        f"sqlite3 -json /data/vaultbank.sqlite "
        f"\"SELECT t.id, t.date, t.description, t.amount, t.category FROM transactions t "
        f"JOIN accounts a ON a.id = t.account_id WHERE a.user_email = '{EMAIL}' "
        f"AND lower(t.description) LIKE '%chili%' ORDER BY t.date\""
    ),
    "speedtax_fields": (
        f"sqlite3 -json /data/speedtax.sqlite "
        f"\"SELECT d.field_name, d.field_value FROM tax_data d "
        f"JOIN tax_returns tr ON tr.id = d.return_id "
        f"WHERE tr.user_email = '{EMAIL}' AND tr.tax_year = 2025 ORDER BY d.field_name\""
    ),
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
        container_name=f"mypcbench-paper2-t3schema-{os.getpid()}",
    )
    print("reset()...", flush=True)
    env.reset()
    print(f"ready {env.base_url}", flush=True)
    results: dict = {"written_at": datetime.now(timezone.utc).isoformat(), "email": EMAIL}
    try:
        for name, cmd in QUERIES.items():
            print(f"--- {name} ---", flush=True)
            r = env._execute_shell(cmd)
            out = ((r.get("output") or "") + (r.get("error") or "")).strip()
            results[name] = out[:40000]
            print(out[:2500], flush=True)

        # Discover sender column + top-N
        sample = results.get("mail_sample_emails", "")
        results["mail_sample_emails_raw"] = sample
        for col in (
            "from_address",
            "from_email",
            "sender",
            "from_addr",
            "author_email",
            "\"from\"",
        ):
            sql = (
                f"SELECT {col} AS sender, count(*) AS n FROM emails "
                f"GROUP BY {col} ORDER BY n DESC LIMIT 15"
            )
            r = env._execute_shell(f"sqlite3 -json /data/mail.sqlite \"{sql}\"")
            out = ((r.get("output") or "") + (r.get("error") or "")).strip()
            key = f"top_by_{col.replace(chr(34), '')}"
            results[key] = out[:12000]
            print(f"{key}: {out[:600]}", flush=True)
            if out and not out.lower().startswith("error"):
                break

        # Timestamp columns for latency probes
        for sql in (
            "PRAGMA table_info(emails);",
            "PRAGMA table_info(sent);",
            "PRAGMA table_info(message_metadata);",
        ):
            r = env._execute_shell(f"sqlite3 /data/mail.sqlite \"{sql}\"")
            out = ((r.get("output") or "") + (r.get("error") or "")).strip()
            results[f"pragma_{sql}"] = out
            print(out[:800], flush=True)
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
    raise SystemExit(main())
