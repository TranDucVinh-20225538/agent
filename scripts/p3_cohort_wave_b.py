#!/usr/bin/env python3
"""Wave B: SELECT-only gold probes for the locked 16.

No agent. No patch. No probe_after. One dummy guest.
Reads paper/paper3_observation_grounded/p3_cohort_slate16_probes.json
as already declared. Do not edit that file after seeing values.

Host-only. Local checkout has no qcow2.
"""
from __future__ import annotations

import json
import os
import sys
import traceback
from pathlib import Path

ROOT = Path(os.environ.get("AGENT_ROOT", Path(__file__).resolve().parents[1]))
SPEC = ROOT / "paper/paper3_observation_grounded/p3_cohort_slate16_probes.json"
OUT = ROOT / "out" / "p3_cohort_probe"
HARNESS = ROOT / "external/MyPCBench-main/agent-harness"
EMAIL = "michael.scott@dundermifflin.com"


def guest_text(env, command: str) -> str:
    result = env._execute_shell(command)
    return ((result.get("output") or "") + (result.get("error") or "")).strip()


def run_sql(env, db: str, sql: str) -> str:
    sql_q = sql.replace(":email", f"'{EMAIL}'").replace('"', '\\"')
    return guest_text(env, f'sqlite3 -json /data/{db} "{sql_q}"')


def dump_schema(env, db: str) -> str:
    return guest_text(
        env,
        f"sqlite3 /data/{db} '.tables' ; echo '---' ; sqlite3 /data/{db} '.schema'",
    )


def parse_jsonish(text: str):
    t = (text or "").strip()
    if not t:
        return None, "empty"
    if t.startswith("ERROR") or "Error:" in t or "no such" in t.lower():
        return None, t[:240]
    try:
        return json.loads(t), "ok"
    except json.JSONDecodeError:
        return None, t[:240]


def unique_ok(rows, path: str):
    if not isinstance(rows, list):
        return False, "not-a-list"
    field = path.split(".")[-1]
    if ".0." in path:
        if len(rows) != 1:
            return False, f"want-1-row got {len(rows)}"
        if field not in rows[0] or rows[0][field] in (None, ""):
            return False, f"null:{field}"
        return True, "ok"
    if not rows:
        return False, "empty"
    if field not in rows[0]:
        return False, f"missing:{field}"
    return True, "ok"


def boot_env():
    sys.path.insert(0, str(HARNESS))
    from env import MyPCBenchEnv

    qcow2 = os.environ.get("MYPCBENCH_QCOW2")
    if not qcow2:
        raise SystemExit("MYPCBENCH_QCOW2 is not set")
    env = MyPCBenchEnv(
        backend="qemu",
        qcow2_path=qcow2,
        headless=True,
        persona="michael_scott",
        container_name=f"mypcbench-p3-waveb-{os.getpid()}",
    )
    print(f"reset() starting; qcow2={qcow2}", flush=True)
    env.reset()
    print(f"guest ready at {env.base_url}", flush=True)
    return env


def write_abort(reason: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    doc = {
        "protocol": "P3_COHORT_PROBE_PROTOCOL.md",
        "wave": "B",
        "status": "TECHNICAL_ABORT",
        "n_scored": 0,
        "n_survive": None,
        "reason": reason,
    }
    (OUT / "wave_b.json").write_text(json.dumps(doc, indent=2) + "\n")
    (OUT / "wave_b.md").write_text(
        "# Wave B TECHNICAL_ABORT — not scored\n\n"
        f"{reason}\n\n"
        "Do not run apply_gate on this file. 0/16 is not a probe result.\n"
    )
    print(f"TECHNICAL_ABORT: {reason}", flush=True)


def write_report(rows: list[dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    n_yes = sum(1 for r in rows if r["survive"])
    doc = {
        "protocol": "P3_COHORT_PROBE_PROTOCOL.md",
        "wave": "B",
        "status": "SCORED",
        "n_scored": len(rows),
        "n_survive": n_yes,
        "n_fail": len(rows) - n_yes,
        "rows": rows,
    }
    (OUT / "wave_b.json").write_text(json.dumps(doc, indent=2) + "\n")
    lines = [
        "# Wave B — slate 16 gold-lock (SELECT-only)",
        "",
        f"Survivors: **{n_yes}/16**.",
        "",
        "| id | survive | unlocked |",
        "|---|---|---|",
    ]
    for r in rows:
        bad = ", ".join(c["id"] for c in r["components"] if not c["locked"]) or "—"
        lines.append(f"| `{r['id']}` | {'YES' if r['survive'] else 'NO'} | {bad} |")
    lines.append("")
    (OUT / "wave_b.md").write_text("\n".join(lines) + "\n")
    print(f"Wave B {n_yes}/16 survive. wrote {OUT / 'wave_b.md'}", flush=True)


def main() -> int:
    os.environ.pop("ANTHROPIC_API_KEY", None)
    os.environ.pop("OPENAI_API_KEY", None)
    os.environ.pop("OPENROUTER_API_KEY", None)
    os.environ.pop("MYPCBENCH_CF_TASK", None)
    os.environ.pop("MYPCBENCH_CF_SCRIPT", None)
    os.environ.pop("MYPCBENCH_CF_PROBE_ONLY", None)

    if not SPEC.is_file():
        raise SystemExit(f"missing {SPEC}")
    spec = json.loads(SPEC.read_text())
    clusters = spec["clusters"]
    if len(clusters) != 16:
        raise SystemExit(f"STOP: slate16 must be 16, got {len(clusters)}")

    OUT.mkdir(parents=True, exist_ok=True)
    env = None
    rows: list[dict] = []
    try:
        env = boot_env()
        for cluster in clusters:
            print(f"----- SELECT {cluster['id']} -----", flush=True)
            comps = []
            ok_all = True
            extras = []
            primary = None
            for i, d in enumerate(cluster["determining"]):
                if d.get("schema_first"):
                    schema = dump_schema(env, d["db"])
                    stem = d["db"].replace(".sqlite", "")
                    (OUT / f"schema_{cluster['id']}_{stem}.txt").write_text(schema + "\n")
                raw = run_sql(env, d["db"], d["sql"])
                parsed, why = parse_jsonish(raw)
                locked = False
                reason = why
                if parsed is not None:
                    locked, reason = unique_ok(parsed, d["path"])
                if not locked:
                    ok_all = False
                rec = {
                    "id": d["id"],
                    "kind": d["kind"],
                    "db": d["db"],
                    "path": d["path"],
                    "locked": locked,
                    "reason": reason,
                    "n_rows": len(parsed) if isinstance(parsed, list) else 0,
                }
                comps.append(rec)
                print(f"  {d['id']} locked={locked} {reason}", flush=True)
                if i == 0:
                    primary = raw
                else:
                    extras.append({"db": d["db"], "sql": d["sql"], "result": raw})
            rows.append(
                {
                    "id": cluster["id"],
                    "wave": "B",
                    "survive": ok_all,
                    "components": comps,
                    "probe_before": primary,
                    "extra_probes_before": extras,
                    "models": ["flash", "gpt"],
                }
            )
    except Exception as exc:
        print(f"TECHNICAL FAILURE during boot/wave B: {exc!r}", flush=True)
        traceback.print_exc()
        write_abort(repr(exc))
        return 2
    finally:
        if env is not None:
            try:
                env.close()
            except Exception:
                pass

    write_report(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
