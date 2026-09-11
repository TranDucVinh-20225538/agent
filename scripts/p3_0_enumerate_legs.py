#!/usr/bin/env python3
"""P3-0 step 0.1: classify every Study 2 leg, so Gate 0's reach is known before it runs.

Read-only. Touches nothing under the archive; opens rubric_result.json for the score and
delegates every terminal decision to scripts/paper2_traj_terminal.py, which is canonical
and fail-closed. DONE detection is deliberately not reimplemented here: every count this
script prints inherits the fail-closed lower-bound property from that module.

The output is the cross-tab that decides whether Gate 0 has any power:

    measurability   keyed task (both locks define parsers and gold paths)
                    unkeyed task (extractor returns no components -> vacuous, never a miss)
    exclusion cause G2 (excluded by the pairing design)
                    G0/G1 orphan (this leg reached DONE, its partner did not)

Usage:
    p3_0_enumerate_legs.py ROOT [--terminal PATH_TO_paper2_traj_terminal.py]
                                [--lock out/study2_gold_path_lock.json]
                                [--jsonl out/p3_0_legs.jsonl]

ROOT is the directory holding the per-lane trees, e.g.
    /data2/hpcshared/Vinh-/agent/results/paper2_exec
with lanes study2-gpt / study2-flash / study2-claude beneath it.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import subprocess
import sys

LEGS = ("G0", "G1", "G2")


def keyed_tasks(lock_path):
    with open(lock_path) as fh:
        lock = json.load(fh)
    return set((lock.get("components") or {}).keys())


def terminal_status(terminal_py, leg_dir):
    """Canonical, fail-closed. Returns (status, canonical_last_action, valid_done).

    `classify-dir` reports runtime-parity `status` in {DONE, TERMINAL_FAIL,
    BOOT_NO_RESULT} and a separate authoritative boolean `valid_done`. Completion is
    read from the boolean, never from the status string, and anything that is not
    literally True counts as not done.
    """
    try:
        r = subprocess.run(
            [sys.executable, terminal_py, "classify-dir", leg_dir],
            capture_output=True, text=True, timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return f"CLASSIFY_ERROR:{type(e).__name__}", None, False
    if r.returncode != 0:
        first = (r.stderr or "").strip().splitlines()
        return f"CLASSIFY_RC{r.returncode}:{first[0][:60] if first else ''}", None, False
    try:
        d = json.loads(r.stdout)
    except json.JSONDecodeError:
        return "CLASSIFY_UNPARSEABLE", None, False
    return str(d.get("status", "UNKNOWN")), d.get("canonical_last_action"), d.get("valid_done") is True


def cell_score(leg_dir):
    for base, _dirs, files in os.walk(leg_dir):
        if "rubric_result.json" in files:
            try:
                with open(os.path.join(base, "rubric_result.json")) as fh:
                    return json.load(fh).get("score")
            except (OSError, json.JSONDecodeError):
                return None
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--terminal", default="scripts/paper2_traj_terminal.py")
    ap.add_argument("--lock", default="out/study2_gold_path_lock.json")
    ap.add_argument("--jsonl", default="out/p3_0_legs.jsonl")
    a = ap.parse_args()

    if not os.path.exists(a.terminal):
        print(f"canonical terminal script not found: {a.terminal}\n"
              "P3-0 must not reimplement DONE detection; point --terminal at it.",
              file=sys.stderr)
        return 2

    keyed = keyed_tasks(a.lock)
    print(f"keyed tasks in gold lock: {len(keyed)}")

    rows = []
    for lane_dir in sorted(os.listdir(a.root)):
        lane_path = os.path.join(a.root, lane_dir)
        if not os.path.isdir(lane_path):
            continue
        lane = lane_dir.replace("study2-", "")
        for task in sorted(os.listdir(lane_path)):
            task_path = os.path.join(lane_path, task)
            if not os.path.isdir(task_path):
                continue
            present = [l for l in LEGS if os.path.isdir(os.path.join(task_path, l))]
            status = {}
            for leg in present:
                status[leg] = terminal_status(a.terminal, os.path.join(task_path, leg))
            in_A = (status.get("G0", (None, None, False))[2]
                    and status.get("G1", (None, None, False))[2])
            for leg in present:
                st, last_action, vd = status[leg]
                if leg == "G2":
                    cause = "G2_by_design"
                elif in_A:
                    cause = "in_A"
                else:
                    cause = "orphan" if vd else "not_done"
                rows.append({
                    "lane": lane,
                    "task": task,
                    "leg": leg,
                    "terminal_status": st,
                    "canonical_last_action": last_action,
                    "valid_done": vd,
                    "cell_in_A": in_A,
                    "task_keyed": task in keyed,
                    "exclusion_cause": cause,
                    "score": cell_score(os.path.join(task_path, leg)),
                    # The only stratum Gate 0 can measure with zero lock change.
                    "gate0_measurable": (vd and not in_A and task in keyed),
                    "dir": os.path.join(task_path, leg),
                })

    with open(a.jsonl, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")

    print(f"legs enumerated: {len(rows)}  -> {a.jsonl}\n")

    by_lane = collections.Counter(r["lane"] for r in rows)
    done = collections.Counter(r["lane"] for r in rows if r["valid_done"])
    inA = collections.Counter(r["lane"] for r in rows if r["cell_in_A"] and r["leg"] in ("G0", "G1"))
    print(f"{'lane':8s} {'legs':>5s} {'VALID_DONE':>11s} {'legs in A':>10s}")
    for lane in sorted(by_lane):
        print(f"{lane:8s} {by_lane[lane]:>5d} {done[lane]:>11d} {inA[lane]:>10d}")

    # The decisive table: excluded-but-DONE legs, split by measurability and cause.
    exc = [r for r in rows if r["valid_done"] and not (r["cell_in_A"] and r["leg"] in ("G0", "G1"))]
    print(f"\nexcluded-but-VALID_DONE legs: {len(exc)}")
    hdr = f"{'lane':8s} {'cause':14s} {'keyed':>6s} {'n':>4s} {'n S>=90':>8s}"
    print(hdr)
    print("-" * len(hdr))
    grp = collections.defaultdict(list)
    for r in exc:
        grp[(r["lane"], r["exclusion_cause"], r["task_keyed"])].append(r)
    for (lane, cause, k), rs in sorted(grp.items()):
        hi = sum(1 for r in rs if isinstance(r["score"], (int, float)) and r["score"] >= 90)
        print(f"{lane:8s} {cause:14s} {str(k):>6s} {len(rs):>4d} {hi:>8d}")

    meas = [r for r in exc if r["gate0_measurable"]]
    print(f"\nGate 0 measurable stratum (VALID_DONE, outside A, keyed task): {len(meas)}")
    print(f"  by lane: {dict(collections.Counter(r['lane'] for r in meas))}")
    print(f"  by cause: {dict(collections.Counter(r['exclusion_cause'] for r in meas))}")
    vac = [r for r in exc if not r["task_keyed"]]
    print(f"Vacuous (unkeyed task; report as not measurable, NEVER as a mismatch): {len(vac)}")

    # Cells where both legs terminated but the cell still sits outside A should not exist;
    # print any, since that would mean the pairing rule and the terminal channel disagree.
    bad = collections.defaultdict(set)
    for r in rows:
        if r["leg"] in ("G0", "G1") and r["valid_done"]:
            bad[(r["lane"], r["task"])].add(r["leg"])
    anom = [k for k, v in bad.items() if v == {"G0", "G1"}
            and not any(r["cell_in_A"] for r in rows if (r["lane"], r["task"]) == k)]
    if anom:
        print(f"\n!! inconsistency: {len(anom)} cells have both legs VALID_DONE but are not in A")
        for k in anom:
            print(f"   {k}")

    print(f"\nHigh-score non-DONE cells for Gate 1 (score >= 90, not VALID_DONE):")
    g1 = [r for r in rows if not r["valid_done"]
          and isinstance(r["score"], (int, float)) and r["score"] >= 90]
    print(f"  n = {len(g1)}  by lane: {dict(collections.Counter(r['lane'] for r in g1))}")
    for r in sorted(g1, key=lambda x: (x["lane"], x["task"], x["leg"])):
        print(f"   {r['lane']:8s} {r['task']:28s} {r['leg']} "
              f"S={r['score']:<5} {r['terminal_status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
