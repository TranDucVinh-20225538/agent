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
import base64
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import shlex

import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cf_file_patch  # noqa: E402

GUEST_DATA = "/data"
DEFAULT_EMAIL = "michael.scott@dundermifflin.com"
# Phase B specs first so the six frozen IDs are not shadowed by Stage 3
# probe-only stubs in interventions.json.
SPEC_PATHS = (
    ROOT / "cf" / "phase_b_interventions.json",
    ROOT / "cf" / "interventions.json",
    ROOT / "cf" / "stage4_locked.json",
)


def load_spec(task_id: str) -> tuple[dict, str]:
    last_email = DEFAULT_EMAIL
    for path in SPEC_PATHS:
        if not path.is_file():
            continue
        payload = json.loads(path.read_text())
        last_email = payload.get("_email") or last_email
        for entry in payload.get("interventions") or []:
            if entry.get("id") == task_id:
                return entry, last_email
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


def file_rels(spec: dict) -> list[str]:
    rels = list(spec.get("files") or [])
    for patch in spec.get("file_patches") or []:
        path = patch["path"]
        if path not in rels:
            rels.append(path)
    return rels


def guest_read_file(api: str, rel: str) -> str:
    guest_path = rel.replace("~", "/home/user")
    listed = guest_exec(
        api,
        f"if [ -f {shlex.quote(guest_path)} ]; then cat {shlex.quote(guest_path)}; "
        f"else echo FILE_MISSING:{shlex.quote(guest_path)}; "
        f"find /home -name $(basename {shlex.quote(guest_path)}) 2>/dev/null; fi",
    )
    return ((listed.get("output") or "") + (listed.get("error") or "")).strip()


def guest_write_text(api: str, rel: str, text: str) -> None:
    guest_path = rel.replace("~", "/home/user")
    payload = base64.b64encode(text.encode("utf-8")).decode("ascii")
    cmd = (
        "python3 -c "
        "'import base64,pathlib,sys; "
        "pathlib.Path(sys.argv[1]).write_bytes(base64.b64decode(sys.argv[2]))' "
        f"{shlex.quote(guest_path)} {shlex.quote(payload)}"
    )
    result = guest_exec(api, cmd)
    if result.get("returncode") not in (0, None):
        fallback = (
            f"printf '%s' {shlex.quote(payload)} | base64 -d > {shlex.quote(guest_path)}"
        )
        result = guest_exec(api, fallback)
        if result.get("returncode") not in (0, None):
            raise SystemExit(
                f"guest file write failed ({result.get('returncode')}): "
                f"{result.get('error') or result.get('output')}"
            )


def build_statements(spec: dict, sqlite_bound, email: str) -> list[str]:
    builder = spec.get("dynamic_patch")
    if not builder:
        return list(spec.get("patch") or [])
    if builder.startswith("f009_"):
        import f009_dynamic
        kind = builder.split("_")[-1].upper()
        return f009_dynamic.build(kind, sqlite_bound, email)
    if builder == "f004_hd_rank_flip":
        import f004_dynamic
        return f004_dynamic.build(sqlite_bound, email)
    raise SystemExit(f"unknown dynamic_patch {builder!r}")


def evaluate_expect(
    spec: dict,
    moved: bool,
    after: str,
    files_before: dict,
    files_after: dict,
    extra_before: list,
    extra_after: list,
) -> list[str]:
    expect = spec.get("expect") or {}
    fails = []
    if expect.get("probe_changes") is True and not moved:
        fails.append("the gold did not move inside the guest")
    if expect.get("probe_changes") is False and moved:
        fails.append("primary probe moved but expect.probe_changes is false")
    if "probe_changes" not in expect and (spec.get("patch") or spec.get("dynamic_patch")):
        if not moved:
            fails.append("the gold did not move inside the guest")
    forbidden = expect.get("after_must_not_contain")
    if forbidden and forbidden.lower() in after.lower():
        fails.append(f"after probe still contains {forbidden!r}")
    if expect.get("file_must_also_change"):
        if files_before == files_after:
            fails.append("files did not change")
    if expect.get("extra_probe_charitable_changes"):
        if extra_before == extra_after:
            fails.append("extra probe (charitable) did not change")
    if expect.get("extra_probes_must_not_change"):
        if extra_before != extra_after:
            fails.append("extra probes moved but must not")
    return fails


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
        raise SystemExit(f"{args.task} has no probe")

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
    for rel in file_rels(spec):
        file_blobs[rel] = guest_read_file(args.api, rel)

    if args.probe_only:
        args.out.mkdir(parents=True, exist_ok=True)
        record = {
            "id": args.task,
            "role": spec.get("role"),
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

    planned_files = spec.get("file_patches") or []
    planned_texts = {}
    for patch in planned_files:
        rel = patch["path"]
        src = file_blobs.get(rel, "")
        if src.startswith("FILE_MISSING:"):
            raise SystemExit(f"file patch: {rel} is missing in the guest")
        nxt = cf_file_patch.apply_replacements(src, patch.get("replace") or [])
        cf_file_patch.check_hold_constant(nxt, patch.get("hold_constant"))
        planned_texts[rel] = nxt

    statements = build_statements(spec, sqlite_bound, email)
    if spec.get("dynamic_patch") and not statements:
        raise SystemExit(f"{args.task}: dynamic_patch produced no SQL")

    for statement in statements:
        sqlite_bound(statement)

    extra_patch_sql = []
    for ep in spec.get("extra_patches") or []:
        extra_patch_sql.append({"db": ep["db"], "sql": ep["sql"]})
        sqlite(args.api, ep["db"], ep["sql"].replace(":email", f"'{email}'"))

    files_after = dict(file_blobs)
    for rel, text in planned_texts.items():
        guest_write_text(args.api, rel, text)
        files_after[rel] = guest_read_file(args.api, rel)
        if files_after[rel].rstrip("\n") != text.rstrip("\n"):
            raise SystemExit(f"file patch: {rel} did not round-trip after write")

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
    fails = evaluate_expect(
        spec, moved, after, file_blobs, files_after, extra_before, extra_after,
    )
    for reason in fails:
        print(f"FAILED: {reason}")

    print(f"description dump (after): {after}")

    args.out.mkdir(parents=True, exist_ok=True)
    record = {
        "id": args.task,
        "role": spec.get("role"),
        "db": spec.get("db"),
        "where": "guest",
        "applied_at": datetime.now(timezone.utc).isoformat(),
        "patch": statements,
        "extra_patches": extra_patch_sql,
        "file_patches": planned_files,
        "probe": spec["probe"],
        "probe_before": before,
        "probe_after": after,
        "extra_probes_before": extra_before,
        "extra_probes_after": extra_after,
        "files_before": file_blobs,
        "files_after": files_after,
        "gold_moved": moved,
        "ok": not fails,
        "fails": fails,
    }
    path = args.out / f"{args.task}.guest.json"
    path.write_text(json.dumps(record, indent=2) + "\n")
    patch_path = args.out / "sql-patch.json"
    patch_path.write_text(json.dumps({
        "condition": args.task,
        "id": args.task,
        "patch": statements,
        "file_patches": planned_files,
    }, indent=2) + "\n")
    print(f"wrote {path}")
    print(f"wrote {patch_path}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
