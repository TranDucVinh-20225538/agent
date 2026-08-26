"""Apply an intervention inside a running guest, through the harness Control API.

`env.py` reaches the guest with `POST {base_url}/execute` and `{"command": ...,
"shell": true}`, and uses the guest's `sqlite3` binary for its own seed backfill.
This does the same thing, so it does not depend on harness internals.

The intervention must land after warm-up and before the agent's first action.
The recommended wiring is a single call inside `_prewarm_lazy_dbs`, immediately
after the authors' own `dinoco-airlines` backfill, which is exactly that point:

    subprocess.run([sys.executable, "<repo>/scripts/cf_inject.py",
                    "--api", self.base_url, "--task", os.environ["MYPCBENCH_CF_TASK"]])

Usage
    python3 scripts/cf_inject.py --api http://127.0.0.1:5000 --task retrieval-f001
    python3 scripts/cf_inject.py --api http://127.0.0.1:5000 --task retrieval-f001 --probe-only
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import shlex

import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "cf" / "interventions.json"
GUEST_DATA = "/data"


def load_spec(task_id: str) -> tuple[dict, str]:
    payload = json.loads(SPEC.read_text())
    for entry in payload["interventions"]:
        if entry["id"] == task_id:
            return entry, payload["_email"]
    raise SystemExit(f"no intervention defined for {task_id}")


def guest_exec(api: str, command: str, timeout: int = 120) -> dict:
    body = json.dumps({"command": command, "shell": True}).encode()
    request = urllib.request.Request(
        f"{api.rstrip('/')}/execute",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read())
    except urllib.error.URLError as exc:
        raise SystemExit(f"Control API unreachable at {api}: {exc}")


def sqlite(api: str, db: str, sql: str, json_out: bool = False) -> str:
    """Run one SQL statement in the guest. The email is inlined because the
    sqlite3 CLI cannot bind named parameters."""
    flag = "-json " if json_out else ""
    escaped = sql.replace("\\", "\\\\").replace('"', '\\"')
    result = guest_exec(api, f'sqlite3 {flag}{GUEST_DATA}/{db} "{escaped}"')
    if result.get("returncode") not in (0, None):
        raise SystemExit(
            f"guest sqlite3 failed ({result.get('returncode')}): "
            f"{result.get('error') or result.get('output')}"
        )
    return (result.get("output") or "").strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", required=True, help="harness Control API base URL")
    parser.add_argument("--task", required=True)
    parser.add_argument("--probe-only", action="store_true")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    if os.environ.get("MYPCBENCH_CF_PROBE_ONLY", "").lower() in ("1", "true", "yes"):
        args.probe_only = True
    if args.out is None:
        env_out = os.environ.get("MYPCBENCH_CF_OUT")
        args.out = Path(env_out) if env_out else ROOT / "out" / "cf_runs"

    spec, email = load_spec(args.task)
    if not spec.get("probe"):
        raise SystemExit(f"{args.task} is a {spec['role']} entry with no probe")

    probe_sql = spec["probe"].replace(":email", f"'{email}'")
    before = sqlite(args.api, spec["db"], probe_sql, json_out=True)
    print(f"probe before: {before}")

    def sqlite_bound(sql: str, json_out: bool = False) -> str:
        return sqlite(args.api, spec["db"], sql.replace(":email", f"'{email}'"), json_out=json_out)

    extra_before = []
    for ep in spec.get("extra_probes") or []:
        ep_sql = ep["sql"].replace(":email", f"'{email}'")
        try:
            ep_result = sqlite(args.api, ep["db"], ep_sql, json_out=True)
        except SystemExit as exc:
            ep_result = f"ERROR: {exc}"
        extra_before.append({"db": ep["db"], "sql": ep["sql"], "result": ep_result})

    file_blobs = {}
    for rel in spec.get("files") or []:
        guest_path = rel.replace("~", "/home/user")
        listed = guest_exec(
            args.api,
            f"if [ -f {shlex.quote(guest_path)} ]; then cat {shlex.quote(guest_path)}; "
            f"else echo FILE_MISSING:{shlex.quote(guest_path)}; "
            f"find /home -name $(basename {shlex.quote(guest_path)}) 2>/dev/null; fi",
        )
        file_blobs[rel] = ((listed.get("output") or "") + (listed.get("error") or "")).strip()

    if args.probe_only:
        args.out.mkdir(parents=True, exist_ok=True)
        record = {
            "id": args.task,
            "role": spec["role"],
            "db": spec.get("db"),
            "where": "guest",
            "mode": "probe-only",
            "probe": spec.get("probe"),
            "probe_before": before,
            "extra_probes": extra_before,
            "files": file_blobs,
        }
        path = args.out / f"{args.task}.guest.json"
        path.write_text(json.dumps(record, indent=2) + "\n")
        print(f"wrote {path}")
        return 0

    statements = list(spec.get("patch") or [])
    builder = spec.get("dynamic_patch")
    if builder:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import f009_dynamic
        kind = builder.split("_")[-1].upper()
        statements = f009_dynamic.build(kind, sqlite_bound, email)

    for statement in statements:
        sqlite_bound(statement)

    extra_patch_sql = []
    for ep in spec.get("extra_patches") or []:
        extra_patch_sql.append({"db": ep["db"], "sql": ep["sql"]})
        sqlite(args.api, ep["db"], ep["sql"].replace(":email", f"'{email}'"))

    after = sqlite(args.api, spec["db"], probe_sql, json_out=True)
    print(f"probe after:  {after}")

    extra_after = []
    for ep in spec.get("extra_probes") or []:
        ep_sql = ep["sql"].replace(":email", f"'{email}'")
        try:
            ep_result = sqlite(args.api, ep["db"], ep_sql, json_out=True)
        except SystemExit as exc:
            ep_result = f"ERROR: {exc}"
        extra_after.append({"db": ep["db"], "sql": ep["sql"], "result": ep_result})
        print(f"extra probe after [{ep['db']}]: {ep_result[:500]}")

    moved = before != after
    if spec["expect"].get("probe_changes") and not moved:
        print("FAILED: the gold did not move inside the guest")

    forbidden = spec["expect"].get("after_must_not_contain")
    if forbidden and forbidden.lower() in after.lower():
        print(f"FAILED: after probe still contains {forbidden!r}")
        moved = False

    print(f"description dump (after): {after}")

    args.out.mkdir(parents=True, exist_ok=True)
    record = {
        "id": args.task,
        "role": spec["role"],
        "db": spec["db"],
        "where": "guest",
        "applied_at": datetime.now(timezone.utc).isoformat(),
        "patch": statements,
        "extra_patches": extra_patch_sql,
        "probe": spec["probe"],
        "probe_before": before,
        "probe_after": after,
        "extra_probes_before": extra_before,
        "extra_probes_after": extra_after,
        "gold_moved": moved,
    }
    path = args.out / f"{args.task}.guest.json"
    path.write_text(json.dumps(record, indent=2) + "\n")
    patch_path = args.out / "sql-patch.json"
    patch_path.write_text(json.dumps({
        "condition": args.task,
        "id": args.task,
        "patch": statements,
    }, indent=2) + "\n")
    print(f"wrote {path}")
    print(f"wrote {patch_path}")
    return 0 if moved else 1


if __name__ == "__main__":
    sys.exit(main())
