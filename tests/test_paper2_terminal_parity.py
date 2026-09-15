#!/usr/bin/env python3
"""Gate −1.5 Closure B: runtime vs offline terminal classifier parity.

Zero-API, no QEMU, no network, no experiment results required.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from paper2_traj_terminal import (  # noqa: E402
    EV_MALFORMED_ACTION,
    EV_MISSING_ACTION_FIELD,
    EV_MISSING_LAST_ACTION,
    EV_NO_TRAJ,
    offline_classify_dir,
    runtime_classify_dir,
)

FIX = ROOT / "tests" / "fixtures" / "paper2_terminal"

CASES = [
    ("01_done", "DONE", True, "DONE"),
    ("02_fail", "FAIL", False, "TERMINAL_FAIL"),
    ("03_predict_crash", "PREDICT_CRASH", False, "TERMINAL_FAIL"),
    ("04_empty_xml", "EMPTY_XML", False, "TERMINAL_FAIL"),
    ("05_malformed_action", None, False, "TERMINAL_FAIL"),
    ("06_missing_action", None, False, "TERMINAL_FAIL"),
    ("07_missing_rubric_and_traj", None, False, "BOOT_NO_RESULT"),
    ("08_boot_no_result", None, False, "BOOT_NO_RESULT"),
    ("09_unreadable_placeholder", None, False, "BOOT_NO_RESULT"),
    # Closure follow-up: prior DONE must NOT back-scan into VALID_DONE
    # when the final row is malformed.
    (
        "10_fallback_trap_done_then_malformed",
        None,
        False,
        "TERMINAL_FAIL",
    ),
]


class TestPaper2TerminalParity(unittest.TestCase):
    def test_fixtures_exist(self):
        for name, *_ in CASES:
            self.assertTrue((FIX / name / "leg").is_dir(), name)

    def test_runtime_offline_parity(self):
        rows = []
        for name, expect_action, expect_valid, expect_status in CASES:
            d = FIX / name / "leg"
            rt = runtime_classify_dir(d)
            off = offline_classify_dir(d)
            rows.append((name, rt, off))
            self.assertEqual(
                rt["valid_done"],
                off["valid_done"],
                f"{name}: valid_done mismatch rt={rt} off={off}",
            )
            self.assertEqual(
                rt["status"],
                off["status"],
                f"{name}: status mismatch rt={rt} off={off}",
            )
            self.assertEqual(rt["valid_done"], expect_valid, name)
            self.assertEqual(rt["status"], expect_status, name)
            self.assertEqual(rt["canonical_last_action"], expect_action, name)
            # Safety: never DONE unless valid_done
            if rt["status"] == "DONE":
                self.assertTrue(rt["valid_done"], name)
            if not rt["valid_done"]:
                self.assertNotEqual(rt["status"], "DONE", name)

        # Explicit evidence tags for hard cases
        self.assertEqual(
            runtime_classify_dir(FIX / "05_malformed_action" / "leg")["evidence_kind"],
            EV_MALFORMED_ACTION,
        )
        self.assertEqual(
            runtime_classify_dir(FIX / "06_missing_action" / "leg")["evidence_kind"],
            EV_MISSING_ACTION_FIELD,
        )
        self.assertEqual(
            runtime_classify_dir(FIX / "07_missing_rubric_and_traj" / "leg")["evidence_kind"],
            EV_NO_TRAJ,
        )
        self.assertFalse(
            runtime_classify_dir(FIX / "07_missing_rubric_and_traj" / "leg")[
                "rubric_bundle_present"
            ]
        )
        # Corrupt-only traj → no usable last action
        self.assertEqual(
            runtime_classify_dir(FIX / "09_unreadable_placeholder" / "leg")["evidence_kind"],
            EV_MISSING_LAST_ACTION,
        )

    def test_done_without_rubric_still_done_and_missing_rubric_alone_not_done(self):
        """rubric_bundle is orthogonal; absence never promotes DONE."""
        with tempfile.TemporaryDirectory() as td:
            leg = Path(td) / "leg"
            leg.mkdir()
            (leg / "traj.jsonl").write_text(
                '{"step_num":1,"action":"DONE","done":true}\n', encoding="utf-8"
            )
            # no rubric_bundle.json
            rt = runtime_classify_dir(leg)
            off = offline_classify_dir(leg)
            self.assertEqual(rt["valid_done"], off["valid_done"])
            self.assertTrue(rt["valid_done"])
            self.assertEqual(rt["status"], "DONE")
            self.assertFalse(rt["rubric_bundle_present"])

        with tempfile.TemporaryDirectory() as td:
            leg = Path(td) / "leg"
            leg.mkdir()
            # rubric present but no traj → still not DONE
            (leg / "rubric_bundle.json").write_text("{}", encoding="utf-8")
            rt = runtime_classify_dir(leg)
            off = offline_classify_dir(leg)
            self.assertEqual(rt["valid_done"], off["valid_done"])
            self.assertFalse(rt["valid_done"])
            self.assertEqual(rt["status"], "BOOT_NO_RESULT")
            self.assertTrue(rt["rubric_bundle_present"])

    def test_false_done_trap_done_true_not_sufficient(self):
        d = FIX / "02_fail" / "leg"
        rt = runtime_classify_dir(d)
        self.assertFalse(rt["valid_done"])
        self.assertEqual(rt["status"], "TERMINAL_FAIL")
        # traj literally contains "done": true
        text = (d / "traj.jsonl").read_text()
        self.assertIn('"done": true', text)
        self.assertNotEqual(rt["canonical_last_action"], "DONE")

    def test_fallback_trap_no_backscan_to_prior_DONE(self):
        """Step N−1 DONE + step N malformed ⇒ not VALID_DONE."""
        from paper2_traj_terminal import inspect_last_action

        d = FIX / "10_fallback_trap_done_then_malformed" / "leg"
        info = inspect_last_action(d / "traj.jsonl")
        self.assertIsNone(info["canonical_last_action"])
        self.assertFalse(info["valid_done"])
        self.assertEqual(info["evidence_kind"], EV_MALFORMED_ACTION)
        # Prior row literally has action DONE — must not be selected
        text = (d / "traj.jsonl").read_text()
        self.assertIn('"action": "DONE"', text)
        rt = runtime_classify_dir(d)
        off = offline_classify_dir(d)
        self.assertEqual(rt["valid_done"], off["valid_done"])
        self.assertFalse(rt["valid_done"])
        self.assertEqual(rt["status"], "TERMINAL_FAIL")


def write_report(path: Path) -> None:
    lines = [
        "# Gate −1.5 Closure B — runtime/offline parity",
        "",
        "| Fixture | Runtime | Offline | valid_done R/O | Match |",
        "| --- | --- | --- | --- | --- |",
    ]
    all_ok = True
    for name, *_ in CASES:
        d = FIX / name / "leg"
        rt = runtime_classify_dir(d)
        off = offline_classify_dir(d)
        match = (
            rt["status"] == off["status"] and rt["valid_done"] == off["valid_done"]
        )
        all_ok = all_ok and match
        lines.append(
            f"| {name} | {rt['status']} | {off['status']} | "
            f"{rt['valid_done']}/{off['valid_done']} | {'YES' if match else 'NO'} |"
        )
    lines.append("")
    lines.append(f"**Overall:** `{'PASS' if all_ok else 'FAIL'}`")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    # machine-readable
    summary = []
    for name, expect_action, expect_valid, expect_status in CASES:
        d = FIX / name / "leg"
        rt = runtime_classify_dir(d)
        off = offline_classify_dir(d)
        summary.append(
            {
                "fixture": name,
                "runtime": rt,
                "offline": off,
                "match": rt["status"] == off["status"]
                and rt["valid_done"] == off["valid_done"],
                "expect_status": expect_status,
                "expect_valid_done": expect_valid,
                "expect_action": expect_action,
            }
        )
    (path.parent / "gate15_closure_B_parity.json").write_text(
        json.dumps({"pass": all_ok, "cases": summary}, indent=2, default=str) + "\n"
    )


if __name__ == "__main__":
    write_report(ROOT / "out" / "gate15_closure_B_parity.md")
    # Also dump Closure A matrix while we're here
    from paper2_traj_terminal import inspect_last_action, find_traj

    matrix = []
    for name, expect_action, expect_valid, expect_status in CASES:
        d = FIX / name / "leg"
        traj = find_traj(d)
        info = inspect_last_action(traj) if traj else {
            "evidence_kind": EV_NO_TRAJ,
            "canonical_last_action": None,
            "valid_done": False,
            "raw_action": None,
        }
        rt = runtime_classify_dir(d)
        off = offline_classify_dir(d)
        matrix.append(
            {
                "case": name,
                "input": name,
                "canonical_last_action": info.get("canonical_last_action"),
                "evidence_kind": info.get("evidence_kind"),
                "valid_done": info.get("valid_done"),
                "runtime_status": rt["status"],
                "offline_status": off["status"],
                "rubric_bundle_present": rt["rubric_bundle_present"],
                "expect_action": expect_action,
                "expect_valid": expect_valid,
                "expect_status": expect_status,
            }
        )
    (ROOT / "out" / "gate15_closure_A_matrix.json").write_text(
        json.dumps(matrix, indent=2, default=str) + "\n"
    )
    md = [
        "# Gate −1.5 Closure A — final-action fail-closed matrix",
        "",
        "| Case | canonical_last_action | evidence_kind | valid_done | runtime | offline |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for m in matrix:
        md.append(
            f"| {m['case']} | `{m['canonical_last_action']}` | {m['evidence_kind']} | "
            f"{m['valid_done']} | {m['runtime_status']} | {m['offline_status']} |"
        )
    md += [
        "",
        "## Safety property",
        "",
        "Missing, malformed, unreadable, or absent final-action evidence "
        "⇒ `valid_done=false` and status ≠ `DONE`.",
        "",
        "`rubric_bundle.json` is **not** consulted for DONE; absence never promotes DONE.",
        "",
    ]
    (ROOT / "out" / "gate15_closure_A_matrix.md").write_text("\n".join(md) + "\n")
    print((ROOT / "out" / "gate15_closure_B_parity.md").read_text())
    raise SystemExit(0 if unittest.main(verbosity=2, exit=False).result.wasSuccessful() else 1)
