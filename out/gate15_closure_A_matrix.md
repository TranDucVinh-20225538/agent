# Gate −1.5 Closure A — final-action fail-closed matrix

| Case | input condition | canonical_last_action | evidence_kind | valid_done | runtime | offline | explicit path |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 01_done | fixture `01_done` | `DONE` | CANONICAL_STRING_ACTION | True | DONE | DONE | inspect → CANONICAL_STRING action=DONE → valid_done → runtime/offline DONE |
| 02_fail | fixture `02_fail` | `FAIL` | CANONICAL_STRING_ACTION | False | TERMINAL_FAIL | TERMINAL_FAIL | action=FAIL even if done:true → valid_done=false → TERMINAL_FAIL |
| 03_predict_crash | fixture `03_predict_crash` | `PREDICT_CRASH` | CANONICAL_STRING_ACTION | False | TERMINAL_FAIL | TERMINAL_FAIL | action=PREDICT_CRASH + done:true → TERMINAL_FAIL |
| 04_empty_xml | fixture `04_empty_xml` | `EMPTY_XML` | CANONICAL_STRING_ACTION | False | TERMINAL_FAIL | TERMINAL_FAIL | action=EMPTY_XML → TERMINAL_FAIL (not DONE) |
| 05_malformed_action | fixture `05_malformed_action` | `None` | MALFORMED_ACTION | False | TERMINAL_FAIL | TERMINAL_FAIL | non-string action → MALFORMED_ACTION → TERMINAL_FAIL |
| 06_missing_action | fixture `06_missing_action` | `None` | MISSING_ACTION_FIELD | False | TERMINAL_FAIL | TERMINAL_FAIL | missing action key → MISSING_ACTION_FIELD → TERMINAL_FAIL |
| 07_missing_rubric_and_traj | fixture `07_missing_rubric_and_traj` | `None` | NO_TRAJ | False | BOOT_NO_RESULT | BOOT_NO_RESULT | no traj → NO_TRAJ; rubric absent → BOOT_NO_RESULT (never DONE) |
| 08_boot_no_result | fixture `08_boot_no_result` | `None` | NO_TRAJ | False | BOOT_NO_RESULT | BOOT_NO_RESULT | no usable traj (empty/zero-byte ignored) → BOOT_NO_RESULT |
| 09_unreadable_placeholder | fixture `09_unreadable_placeholder` | `None` | MISSING_LAST_ACTION | False | BOOT_NO_RESULT | BOOT_NO_RESULT | non-JSON traj lines → MISSING_LAST_ACTION → BOOT_NO_RESULT |

## Required safety property

Missing / malformed / unreadable / absent final-action evidence ⇒ `valid_done=false` and **never** checkpoint/`status=DONE`.

Implemented explicitly in `scripts/paper2_traj_terminal.py`::`inspect_last_action` / `runtime_classify_dir` / `classify_leg` (no bare exception → DONE path).

`rubric_bundle.json` is orthogonal: absence does not promote DONE; presence without traj does not promote DONE.

