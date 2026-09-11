#!/usr/bin/env python3
"""Paper-2 trajectory terminal classification (measurement layer).

Canonical rule (Gate −1.5):
  VALID_DONE ⇔ canonical_last_action == \"DONE\"

Fail-closed (Gate −1.5 Closure A):
  Missing, malformed, unreadable, or absent final-action evidence
  never yields VALID_DONE / checkpoint status DONE.

Does NOT treat traj field \"done\": true as success (FAIL / PREDICT_CRASH
also set done=true in run_mypcbench.py).

Does NOT consult rubric_bundle.json for DONE (judge channel is orthogonal).

CLI:
  paper2_traj_terminal.py last-action <traj.jsonl>
  paper2_traj_terminal.py has-done <traj.jsonl>     # exit 0 iff VALID_DONE
  paper2_traj_terminal.py has-done-dir <result_dir> # finds traj.jsonl under dir
  paper2_traj_terminal.py inspect <traj.jsonl|result_dir>
  paper2_traj_terminal.py classify-dir <result_dir>  # runtime-parity status
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Explicit evidence tags (never implicit via bare exceptions for measurement).
EV_CANONICAL_STRING = "CANONICAL_STRING_ACTION"
EV_EMPTY_TRAJ = "EMPTY_TRAJ"
EV_NO_TRAJ = "NO_TRAJ"
EV_UNREADABLE_TRAJ = "UNREADABLE_TRAJ"
EV_MALFORMED_ACTION = "MALFORMED_ACTION"
EV_MISSING_ACTION_FIELD = "MISSING_ACTION_FIELD"
EV_MISSING_LAST_ACTION = "MISSING_LAST_ACTION"  # umbrella for no usable final action


def _read_text_fail_closed(path: Path) -> Tuple[Optional[str], Optional[str]]:
    """Return (text, error_kind). error_kind set ⇒ fail closed."""
    try:
        return path.read_text(errors="replace"), None
    except OSError:
        return None, EV_UNREADABLE_TRAJ


def load_traj_rows(traj_path: Path) -> List[Dict[str, Any]]:
    """Load well-formed JSON object rows; skip malformed lines (fail closed later)."""
    text, err = _read_text_fail_closed(traj_path)
    if err is not None or text is None:
        return []
    rows: List[Dict[str, Any]] = []
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


def load_traj_rows_with_meta(traj_path: Path) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """Like load_traj_rows but surfaces UNREADABLE vs empty-parse."""
    text, err = _read_text_fail_closed(traj_path)
    if err is not None:
        return [], err
    assert text is not None
    rows: List[Dict[str, Any]] = []
    any_line = False
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        any_line = True
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    if not rows:
        return [], EV_EMPTY_TRAJ if not any_line else EV_MISSING_LAST_ACTION
    return rows, None


def inspect_last_action(traj_path: Path) -> Dict[str, Any]:
    """Explicit final-action evidence inspection (fail closed).

    valid_done is True only when the last successfully parsed row has
    action that is exactly the string \"DONE\".
    """
    rows, load_err = load_traj_rows_with_meta(traj_path)
    if load_err is not None:
        return {
            "evidence_kind": load_err,
            "canonical_last_action": None,
            "raw_action": None,
            "valid_done": False,
            "has_steps": False,
            "row_count": 0,
            "traj_path": str(traj_path),
        }

    last = rows[-1]
    has_steps = any("step_num" in r for r in rows)
    if "action" not in last:
        return {
            "evidence_kind": EV_MISSING_ACTION_FIELD,
            "canonical_last_action": None,
            "raw_action": None,
            "valid_done": False,
            "has_steps": has_steps,
            "row_count": len(rows),
            "traj_path": str(traj_path),
        }

    raw = last.get("action")
    if not isinstance(raw, str):
        # Nested / non-string action objects are not canonical terminals.
        return {
            "evidence_kind": EV_MALFORMED_ACTION,
            "canonical_last_action": None,
            "raw_action": raw,
            "valid_done": False,
            "has_steps": has_steps,
            "row_count": len(rows),
            "traj_path": str(traj_path),
        }

    return {
        "evidence_kind": EV_CANONICAL_STRING,
        "canonical_last_action": raw,
        "raw_action": raw,
        "valid_done": raw == "DONE",
        "has_steps": has_steps,
        "row_count": len(rows),
        "traj_path": str(traj_path),
    }


def canonical_last_action(traj_path: Path) -> Optional[str]:
    """Last well-formed string ``action``, or None (fail closed)."""
    info = inspect_last_action(traj_path)
    return info["canonical_last_action"]


def find_traj(dir_path: Path) -> Optional[Path]:
    if not dir_path.exists():
        return None
    try:
        for p in sorted(dir_path.rglob("traj.jsonl")):
            try:
                if p.is_file() and p.stat().st_size > 0:
                    return p
            except OSError:
                continue
    except OSError:
        return None
    return None


def has_done_action(traj_path: Path) -> bool:
    """VALID_DONE predicate used by runtime cell_has_done / write_leg_checkpoint."""
    return bool(inspect_last_action(traj_path)["valid_done"])


def rubric_bundle_present(dir_path: Path) -> bool:
    """Judge packaging only — never promotes VALID_DONE."""
    try:
        return (dir_path / "rubric_bundle.json").is_file()
    except OSError:
        return False


def runtime_classify_dir(result_dir: Path) -> Dict[str, Any]:
    """Mirror paper2_exec_run.sh post-leg branch (no bash, no API).

    if cell_has_done → DONE
    elif cell_has_step → TERMINAL_FAIL
    else → BOOT_NO_RESULT
    """
    traj = find_traj(result_dir)
    rubric = rubric_bundle_present(result_dir)
    if traj is None:
        return {
            "path": "runtime",
            "status": "BOOT_NO_RESULT",
            "valid_done": False,
            "canonical_last_action": None,
            "evidence_kind": EV_NO_TRAJ,
            "has_steps": False,
            "rubric_bundle_present": rubric,
            "traj_path": None,
        }
    info = inspect_last_action(traj)
    # Mirror paper2_exec_run.sh: DONE only via has-done; else steps→FAIL; else boot.
    if info["valid_done"]:
        status = "DONE"
    elif info["has_steps"]:
        status = "TERMINAL_FAIL"
    elif info["row_count"] > 0 and info["evidence_kind"] in (
        EV_CANONICAL_STRING, EV_MALFORMED_ACTION, EV_MISSING_ACTION_FIELD
    ):
        # Parsed traj content without step_num still terminal-fail (not boot).
        status = "TERMINAL_FAIL"
    else:
        status = "BOOT_NO_RESULT"
    return {
        "path": "runtime",
        "status": status,
        "valid_done": bool(info["valid_done"]),
        "canonical_last_action": info["canonical_last_action"],
        "evidence_kind": info["evidence_kind"] if traj else EV_NO_TRAJ,
        "has_steps": bool(info["has_steps"]),
        "rubric_bundle_present": rubric,
        "traj_path": str(traj),
    }


def classify_leg(
    *,
    old_status: Optional[str],
    traj_path: Optional[Path],
    has_steps: bool,
    result_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Offline reclassification record (canonical_audit_paper2.py)."""
    rubric = rubric_bundle_present(result_dir) if result_dir else False

    if traj_path is None:
        last = None
        evidence = EV_NO_TRAJ
        new_status = "BOOT_NO_RESULT" if not has_steps else "TERMINAL_FAIL"
        reason = "no_traj"
        valid = False
    else:
        info = inspect_last_action(traj_path)
        last = info["canonical_last_action"]
        evidence = info["evidence_kind"]
        valid = bool(info["valid_done"])
        # Prefer inspector has_steps when traj present.
        steps_flag = bool(info["has_steps"]) or has_steps
        if valid:
            new_status = "DONE"
            reason = "canonical_last_action_DONE"
        elif steps_flag or evidence in (
            EV_CANONICAL_STRING, EV_MALFORMED_ACTION, EV_MISSING_ACTION_FIELD
        ):
            new_status = "TERMINAL_FAIL"
            reason = f"evidence={evidence}; canonical_last_action={last!r}"
        else:
            # EMPTY_TRAJ / UNREADABLE / MISSING_LAST_ACTION without steps
            new_status = "BOOT_NO_RESULT"
            reason = evidence

    # Safety property: never DONE unless valid.
    if new_status == "DONE" and not valid:
        new_status = "TERMINAL_FAIL"
        reason = "fail_closed_invalid_done_guard"

    old = old_status
    mismatch = (old is not None) and (old != new_status)
    mismatch_reason = None
    if mismatch:
        if old == "DONE" and new_status != "DONE":
            mismatch_reason = (
                "false_DONE: checkpoint used done:true heuristic; "
                f"canonical_last_action={last!r}; evidence={evidence}"
            )
        else:
            mismatch_reason = f"status_changed {old} → {new_status}"

    return {
        "old_checkpoint_status": old,
        "canonical_final_action": last,
        "new_classification": new_status,
        "has_done_action_canonical": valid,
        "valid_done": valid,
        "evidence_kind": evidence,
        "rubric_bundle_present": rubric,
        "mismatch": mismatch,
        "mismatch_reason": mismatch_reason,
        "traj_path": str(traj_path) if traj_path else None,
        "reason": reason,
    }


def offline_classify_dir(result_dir: Path) -> Dict[str, Any]:
    """Offline path used by audit: find traj → classify_leg."""
    traj = find_traj(result_dir)
    has_steps = False
    if traj is not None:
        info = inspect_last_action(traj)
        has_steps = bool(info["has_steps"])
    cls = classify_leg(
        old_status=None,
        traj_path=traj,
        has_steps=has_steps,
        result_dir=result_dir,
    )
    return {
        "path": "offline",
        "status": cls["new_classification"],
        "valid_done": bool(cls["valid_done"]),
        "canonical_last_action": cls["canonical_final_action"],
        "evidence_kind": cls["evidence_kind"],
        "has_steps": has_steps,
        "rubric_bundle_present": cls["rubric_bundle_present"],
        "traj_path": cls["traj_path"],
        "reason": cls["reason"],
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
    if cmd == "inspect":
        if len(argv) != 3:
            print("usage: inspect <traj.jsonl|result_dir>", file=sys.stderr)
            return 2
        p = Path(argv[2])
        if p.is_dir():
            print(json.dumps(runtime_classify_dir(p), indent=2, default=str))
        else:
            print(json.dumps(inspect_last_action(p), indent=2, default=str))
        return 0
    if cmd == "classify-dir":
        if len(argv) != 3:
            print("usage: classify-dir <result_dir>", file=sys.stderr)
            return 2
        print(json.dumps(runtime_classify_dir(Path(argv[2])), indent=2, default=str))
        return 0
    print(f"unknown command: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
