# Canonical audit — `qwen38-flash`

- generated: 2026-09-06T11:21:25.684949+00:00
- source checkpoint: `/mnt/data2/Vinh/agent/results/paper2_exec/qwen38-flash/CHECKPOINT.jsonl`
- rule: `VALID_DONE ⇔ canonical_last_action == "DONE"`
- legs: 57
- old status counts: {'DONE': 27, 'TERMINAL_FAIL': 30}
- new status counts: {'DONE': 23, 'TERMINAL_FAIL': 34}
- mismatches: 4

## Mismatches

| task | leg | old | new | canonical_final_action | reason |
| --- | --- | --- | --- | --- | --- |
| aggregation-f036 | G0 | DONE | TERMINAL_FAIL | `PREDICT_CRASH` | false_DONE: checkpoint used done:true heuristic; canonical_last_action='PREDICT_CRASH' |
| aggregation-f040 | G2 | DONE | TERMINAL_FAIL | `FAIL` | false_DONE: checkpoint used done:true heuristic; canonical_last_action='FAIL' |
| contradiction-f006 | G1 | DONE | TERMINAL_FAIL | `PREDICT_CRASH` | false_DONE: checkpoint used done:true heuristic; canonical_last_action='PREDICT_CRASH' |
| preference_inference-f014 | G0 | DONE | TERMINAL_FAIL | `PREDICT_CRASH` | false_DONE: checkpoint used done:true heuristic; canonical_last_action='PREDICT_CRASH' |

Artifacts: `canonical_audit.jsonl`, `CHECKPOINT.canonical.jsonl`

