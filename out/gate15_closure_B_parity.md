# Gate −1.5 Closure B — runtime/offline parity

| Fixture | Runtime | Offline | valid_done R/O | Match |
| --- | --- | --- | --- | --- |
| 01_done | DONE | DONE | True/True | YES |
| 02_fail | TERMINAL_FAIL | TERMINAL_FAIL | False/False | YES |
| 03_predict_crash | TERMINAL_FAIL | TERMINAL_FAIL | False/False | YES |
| 04_empty_xml | TERMINAL_FAIL | TERMINAL_FAIL | False/False | YES |
| 05_malformed_action | TERMINAL_FAIL | TERMINAL_FAIL | False/False | YES |
| 06_missing_action | TERMINAL_FAIL | TERMINAL_FAIL | False/False | YES |
| 07_missing_rubric_and_traj | BOOT_NO_RESULT | BOOT_NO_RESULT | False/False | YES |
| 08_boot_no_result | BOOT_NO_RESULT | BOOT_NO_RESULT | False/False | YES |
| 09_unreadable_placeholder | BOOT_NO_RESULT | BOOT_NO_RESULT | False/False | YES |
| 10_fallback_trap_done_then_malformed | TERMINAL_FAIL | TERMINAL_FAIL | False/False | YES |

**Overall:** `PASS`

