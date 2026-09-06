#!/usr/bin/env python3
"""Paper-2 trajectory terminal classification (measurement layer).

Canonical rule (Gate −1.5):
  VALID_DONE ⇔ canonical_last_action == \"DONE\"

Does NOT treat traj field \"done\": true as success (FAIL / PREDICT_CRASH
also set done=true in run_mypcbench.py).

CLI:
  paper2_traj_terminal.py last-action <traj.jsonl>
  paper2_traj_terminal.py has-done <traj.jsonl>     # exit 0 iff VALID_DONE
  paper2_traj_terminal.py has-done-dir <result_dir> # finds traj.jsonl under dir
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _normalize_action(raw: Any) -> Optional[str]:
    if raw is None:
        return None
    if isinstance(raw, str):
        return raw
    return str(raw)


def load_traj_rows(traj_path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    text = traj_path.read_text(errors="replace")
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def canonical_last_action(traj_path: Path) -> Optional[str]:
    """Last successfully parsed traj row's ``action`` field, or None if empty."""
    rows = load_traj_rows(traj_path)
    if not rows:
        return None
    return _normalize_action(rows[-1].get("action"))


def find_traj(dir_path: Path) -> Optional[Path]:
    if not dir_path.exists():
        return None
    for p in sorted(dir_path.rglob("traj.jsonl")):
        if p.is_file() and p.stat().st_size > 0:
            return p
    return None


def has_done_action(traj_path: Path) -> bool:
    return canonical_last_action(traj_path) == "DONE"


def classify_leg(
    *,
    old_status: Optional[str],
    traj_path: Optional[Path],
    has_steps: bool,
) -> Dict[str, Any]:
    """Offline reclassification record."""
    if traj_path is None:
        last = None
        new_status = "BOOT_NO_RESULT" if not has_steps else "TERMINAL_FAIL"
        reason = "no_traj"
    else:
        last = canonical_last_action(traj_path)
        if last == "DONE":
            new_status = "DONE"
            reason = "canonical_last_action_DONE"
        elif last is None and not has_steps:
            new_status = "BOOT_NO_RESULT"
            reason = "empty_traj"
        else:
            new_status = "TERMINAL_FAIL"
            reason = f"canonical_last_action={last!r}"

    old = old_status
    mismatch = (old is not None) and (old != new_status)
    mismatch_reason = None
    if mismatch:
        if old == "DONE" and new_status != "DONE":
            mismatch_reason = (
                "false_DONE: checkpoint used done:true heuristic; "
                f"canonical_last_action={last!r}"
            )
        else:
            mismatch_reason = f"status_changed {old} → {new_status}"

    return {
        "old_checkpoint_status": old,
        "canonical_final_action": last,
        "new_classification": new_status,
        "has_done_action_canonical": last == "DONE",
        "mismatch": mismatch,
        "mismatch_reason": mismatch_reason,
        "traj_path": str(traj_path) if traj_path else None,
    }


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    cmd = argv[1]
    if cmd == "last-action":
        if len(argv) != 3:
            print("usage: last-action <traj.jsonl>", file=sys.stderr)
            return 2
        act = canonical_last_action(Path(argv[2]))
        print(act if act is not None else "")
        return 0
    if cmd == "has-done":
        if len(argv) != 3:
            print("usage: has-done <traj.jsonl>", file=sys.stderr)
            return 2
        return 0 if has_done_action(Path(argv[2])) else 1
    if cmd == "has-done-dir":
        if len(argv) != 3:
            print("usage: has-done-dir <result_dir>", file=sys.stderr)
            return 2
        traj = find_traj(Path(argv[2]))
        if traj is None:
            return 1
        return 0 if has_done_action(traj) else 1
    print(f"unknown command: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
