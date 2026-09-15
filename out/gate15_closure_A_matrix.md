# Gate −1.5 Closure A — final-action fail-closed matrix

| Case | canonical_last_action | evidence_kind | valid_done | runtime | offline |
| --- | --- | --- | --- | --- | --- |
| 01_done | `DONE` | CANONICAL_STRING_ACTION | True | DONE | DONE |
| 02_fail | `FAIL` | CANONICAL_STRING_ACTION | False | TERMINAL_FAIL | TERMINAL_FAIL |
| 03_predict_crash | `PREDICT_CRASH` | CANONICAL_STRING_ACTION | False | TERMINAL_FAIL | TERMINAL_FAIL |
| 04_empty_xml | `EMPTY_XML` | CANONICAL_STRING_ACTION | False | TERMINAL_FAIL | TERMINAL_FAIL |
| 05_malformed_action | `None` | MALFORMED_ACTION | False | TERMINAL_FAIL | TERMINAL_FAIL |
| 06_missing_action | `None` | MISSING_ACTION_FIELD | False | TERMINAL_FAIL | TERMINAL_FAIL |
| 07_missing_rubric_and_traj | `None` | NO_TRAJ | False | BOOT_NO_RESULT | BOOT_NO_RESULT |
| 08_boot_no_result | `None` | NO_TRAJ | False | BOOT_NO_RESULT | BOOT_NO_RESULT |
| 09_unreadable_placeholder | `None` | MISSING_LAST_ACTION | False | BOOT_NO_RESULT | BOOT_NO_RESULT |
| 10_fallback_trap_done_then_malformed | `None` | MALFORMED_ACTION | False | TERMINAL_FAIL | TERMINAL_FAIL |

## Safety property

Missing, malformed, unreadable, or absent final-action evidence ⇒ `valid_done=false` and status ≠ `DONE`.

`rubric_bundle.json` is **not** consulted for DONE; absence never promotes DONE.

