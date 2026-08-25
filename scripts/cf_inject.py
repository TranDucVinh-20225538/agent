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
import sys
from datetime import datetime, timezone
from pathlib import Path

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
    parser.add_argument("--out", type=Path, default=ROOT / "out" / "cf_runs")
    args = parser.parse_args()

    spec, email = load_spec(args.task)
    if not spec.get("probe"):
        raise SystemExit(f"{args.task} is a {spec['role']} entry with no probe")

    probe_sql = spec["probe"].replace(":email", f"'{email}'")
    before = sqlite(args.api, spec["db"], probe_sql, json_out=True)
    print(f"probe before: {before}")

    if args.probe_only:
        return 0

    for statement in spec["patch"]:
        sqlite(args.api, spec["db"], statement.replace(":email", f"'{email}'"))

    after = sqlite(args.api, spec["db"], probe_sql, json_out=True)
    print(f"probe after:  {after}")

    moved = before != after
    if spec["expect"].get("probe_changes") and not moved:
        print("FAILED: the gold did not move inside the guest")

    args.out.mkdir(parents=True, exist_ok=True)
    record = {
        "id": args.task,
        "role": spec["role"],
        "db": spec["db"],
        "where": "guest",
        "applied_at": datetime.now(timezone.utc).isoformat(),
        "patch": spec["patch"],
        "probe": spec["probe"],
        "probe_before": before,
        "probe_after": after,
        "gold_moved": moved,
    }
    path = args.out / f"{args.task}.guest.json"
    path.write_text(json.dumps(record, indent=2))
    print(f"wrote {path}")
    return 0 if moved else 1


if __name__ == "__main__":
    sys.exit(main())
