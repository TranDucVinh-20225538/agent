# Executor invariant check (representatives)
Marks: PASS / FAIL / NOT_APPLICABLE / NOT_VERIFIABLE

## contradiction-f022__G0__NO_ACTION_AFTER_VALID_ACTION
- **full history retained?** → `NOT_VERIFIABLE` — archived messages.json often assistant-only / images stripped; cannot prove full wire history
- **screenshot cadence retained?** → `PASS` — traj screenshot_file fields present on many steps; PNGs exist in archive dirs
- **system prompt unchanged?** → `NOT_VERIFIABLE` — runtime injects current date; archived dump may omit system turn
- **parser called?** → `PASS` — non-empty action or EMPTY_XML/TOOL_CALL implies predict→parse path ran (except PREDICT_CRASH)
- **parser result correct under frozen grammar?** → `NOT_VERIFIABLE` — for malformed examples, rejecting non-computer_use/bash matches frozen grammar; other classes need manual review
- **QEMU action actually executed?** → `PASS` — GUI actions appear in traj; EMPTY/CRASH steps have no GUI dispatch
- **action result inserted into next turn?** → `NOT_VERIFIABLE` — bash injection path exists in code; not fully reconstructed from sanitized archive
- **accidental history truncation?** → `NOT_VERIFIABLE` — no direct counterfactual dump of pre-send messages per step
- **mutation of messages by transport?** → `PASS` — transport deep-copies messages; rejects tool schema keys — unit-tested path
- **step counter correct?** → `PASS` — traj step_num sequence length=3 vs metadata steps=3
- **terminal classifier correct?** → `PASS` — inspect={'evidence_kind': 'CANONICAL_STRING_ACTION', 'canonical_last_action': 'TOOL_CALL', 'raw_action': 'TOOL_CALL', 'valid_done': False, 'has_steps': True, 'row_count': 3, 'traj_path': '/mnt/data2/Vinh/agent/results/paper2_exec/study2-flash/contradiction-f022/G0/contradiction-f022/traj.jsonl'} checkpoint=TERMINAL_FAIL

## contradiction-f022__G1__MALFORMED_ACTION_SYNTAX
- **full history retained?** → `NOT_VERIFIABLE` — archived messages.json often assistant-only / images stripped; cannot prove full wire history
- **screenshot cadence retained?** → `PASS` — traj screenshot_file fields present on many steps; PNGs exist in archive dirs
- **system prompt unchanged?** → `NOT_VERIFIABLE` — runtime injects current date; archived dump may omit system turn
- **parser called?** → `PASS` — non-empty action or EMPTY_XML/TOOL_CALL implies predict→parse path ran (except PREDICT_CRASH)
- **parser result correct under frozen grammar?** → `PASS` — for malformed examples, rejecting non-computer_use/bash matches frozen grammar; other classes need manual review
- **QEMU action actually executed?** → `NOT_APPLICABLE` — GUI actions appear in traj; EMPTY/CRASH steps have no GUI dispatch
- **action result inserted into next turn?** → `NOT_VERIFIABLE` — bash injection path exists in code; not fully reconstructed from sanitized archive
- **accidental history truncation?** → `NOT_VERIFIABLE` — no direct counterfactual dump of pre-send messages per step
- **mutation of messages by transport?** → `PASS` — transport deep-copies messages; rejects tool schema keys — unit-tested path
- **step counter correct?** → `PASS` — traj step_num sequence length=2 vs metadata steps=2
- **terminal classifier correct?** → `PASS` — inspect={'evidence_kind': 'CANONICAL_STRING_ACTION', 'canonical_last_action': 'EMPTY_XML', 'raw_action': 'EMPTY_XML', 'valid_done': False, 'has_steps': True, 'row_count': 2, 'traj_path': '/mnt/data2/Vinh/agent/results/paper2_exec/study2-flash/contradiction-f022/G1/contradiction-f022/traj.jsonl'} checkpoint=TERMINAL_FAIL

## counterfactual-f002__G2__PROVIDER_RATE_LIMIT
- **full history retained?** → `NOT_VERIFIABLE` — archived messages.json often assistant-only / images stripped; cannot prove full wire history
- **screenshot cadence retained?** → `PASS` — traj screenshot_file fields present on many steps; PNGs exist in archive dirs
- **system prompt unchanged?** → `NOT_VERIFIABLE` — runtime injects current date; archived dump may omit system turn
- **parser called?** → `PASS` — non-empty action or EMPTY_XML/TOOL_CALL implies predict→parse path ran (except PREDICT_CRASH)
- **parser result correct under frozen grammar?** → `NOT_VERIFIABLE` — for malformed examples, rejecting non-computer_use/bash matches frozen grammar; other classes need manual review
- **QEMU action actually executed?** → `NOT_APPLICABLE` — GUI actions appear in traj; EMPTY/CRASH steps have no GUI dispatch
- **action result inserted into next turn?** → `NOT_VERIFIABLE` — bash injection path exists in code; not fully reconstructed from sanitized archive
- **accidental history truncation?** → `NOT_VERIFIABLE` — no direct counterfactual dump of pre-send messages per step
- **mutation of messages by transport?** → `PASS` — transport deep-copies messages; rejects tool schema keys — unit-tested path
- **step counter correct?** → `PASS` — traj step_num sequence length=1 vs metadata steps=1
- **terminal classifier correct?** → `PASS` — inspect={'evidence_kind': 'CANONICAL_STRING_ACTION', 'canonical_last_action': 'PREDICT_CRASH', 'raw_action': 'PREDICT_CRASH', 'valid_done': False, 'has_steps': True, 'row_count': 1, 'traj_path': '/mnt/data2/Vinh/agent/results/paper2_exec/study2-flash/counterfactual-f002/G2/counterfactual-f002/traj.jsonl'} checkpoint=TERMINAL_FAIL

## preference_inference-f010__G1__EMPTY_ACTION
- **full history retained?** → `NOT_VERIFIABLE` — archived messages.json often assistant-only / images stripped; cannot prove full wire history
- **screenshot cadence retained?** → `PASS` — traj screenshot_file fields present on many steps; PNGs exist in archive dirs
- **system prompt unchanged?** → `NOT_VERIFIABLE` — runtime injects current date; archived dump may omit system turn
- **parser called?** → `PASS` — non-empty action or EMPTY_XML/TOOL_CALL implies predict→parse path ran (except PREDICT_CRASH)
- **parser result correct under frozen grammar?** → `PASS` — for malformed examples, rejecting non-computer_use/bash matches frozen grammar; other classes need manual review
- **QEMU action actually executed?** → `NOT_APPLICABLE` — GUI actions appear in traj; EMPTY/CRASH steps have no GUI dispatch
- **action result inserted into next turn?** → `NOT_VERIFIABLE` — bash injection path exists in code; not fully reconstructed from sanitized archive
- **accidental history truncation?** → `NOT_VERIFIABLE` — no direct counterfactual dump of pre-send messages per step
- **mutation of messages by transport?** → `PASS` — transport deep-copies messages; rejects tool schema keys — unit-tested path
- **step counter correct?** → `PASS` — traj step_num sequence length=4 vs metadata steps=4
- **terminal classifier correct?** → `PASS` — inspect={'evidence_kind': 'CANONICAL_STRING_ACTION', 'canonical_last_action': 'TOOL_CALL', 'raw_action': 'TOOL_CALL', 'valid_done': False, 'has_steps': True, 'row_count': 4, 'traj_path': '/mnt/data2/Vinh/agent/results/paper2_exec/study2-flash/preference_inference-f010/G1/preference_inference-f010/traj.jsonl'} checkpoint=TERMINAL_FAIL

## retrieval-f005__G0__STEP_LIMIT_NO_DONE
- **full history retained?** → `NOT_VERIFIABLE` — archived messages.json often assistant-only / images stripped; cannot prove full wire history
- **screenshot cadence retained?** → `PASS` — traj screenshot_file fields present on many steps; PNGs exist in archive dirs
- **system prompt unchanged?** → `NOT_VERIFIABLE` — runtime injects current date; archived dump may omit system turn
- **parser called?** → `PASS` — non-empty action or EMPTY_XML/TOOL_CALL implies predict→parse path ran (except PREDICT_CRASH)
- **parser result correct under frozen grammar?** → `NOT_VERIFIABLE` — for malformed examples, rejecting non-computer_use/bash matches frozen grammar; other classes need manual review
- **QEMU action actually executed?** → `PASS` — GUI actions appear in traj; EMPTY/CRASH steps have no GUI dispatch
- **action result inserted into next turn?** → `NOT_VERIFIABLE` — bash injection path exists in code; not fully reconstructed from sanitized archive
- **accidental history truncation?** → `NOT_VERIFIABLE` — no direct counterfactual dump of pre-send messages per step
- **mutation of messages by transport?** → `PASS` — transport deep-copies messages; rejects tool schema keys — unit-tested path
- **step counter correct?** → `PASS` — traj step_num sequence length=82 vs metadata steps=82
- **terminal classifier correct?** → `PASS` — inspect={'evidence_kind': 'CANONICAL_STRING_ACTION', 'canonical_last_action': 'pyautogui.click(804, 52)', 'raw_action': 'pyautogui.click(804, 52)', 'valid_done': False, 'has_steps': True, 'row_count': 82, 'traj_path': '/mnt/data2/Vinh/agent/results/paper2_exec/study2-flash/retrieval-f005/G0/retrieval-f005/traj.jsonl'} checkpoint=TERMINAL_FAIL

## retrieval-f010__G0__SUCCESS_DONE
- **full history retained?** → `NOT_VERIFIABLE` — archived messages.json often assistant-only / images stripped; cannot prove full wire history
- **screenshot cadence retained?** → `PASS` — traj screenshot_file fields present on many steps; PNGs exist in archive dirs
- **system prompt unchanged?** → `NOT_VERIFIABLE` — runtime injects current date; archived dump may omit system turn
- **parser called?** → `PASS` — non-empty action or EMPTY_XML/TOOL_CALL implies predict→parse path ran (except PREDICT_CRASH)
- **parser result correct under frozen grammar?** → `NOT_VERIFIABLE` — for malformed examples, rejecting non-computer_use/bash matches frozen grammar; other classes need manual review
- **QEMU action actually executed?** → `PASS` — GUI actions appear in traj; EMPTY/CRASH steps have no GUI dispatch
- **action result inserted into next turn?** → `NOT_VERIFIABLE` — bash injection path exists in code; not fully reconstructed from sanitized archive
- **accidental history truncation?** → `NOT_VERIFIABLE` — no direct counterfactual dump of pre-send messages per step
- **mutation of messages by transport?** → `PASS` — transport deep-copies messages; rejects tool schema keys — unit-tested path
- **step counter correct?** → `PASS` — traj step_num sequence length=39 vs metadata steps=39
- **terminal classifier correct?** → `PASS` — inspect={'evidence_kind': 'CANONICAL_STRING_ACTION', 'canonical_last_action': 'DONE', 'raw_action': 'DONE', 'valid_done': True, 'has_steps': True, 'row_count': 39, 'traj_path': '/mnt/data2/Vinh/agent/results/paper2_exec/study2-flash/retrieval-f010/G0/retrieval-f010/traj.jsonl'} checkpoint=DONE

## retrieval-f010__G1__SUCCESS_DONE
- **full history retained?** → `NOT_VERIFIABLE` — archived messages.json often assistant-only / images stripped; cannot prove full wire history
- **screenshot cadence retained?** → `PASS` — traj screenshot_file fields present on many steps; PNGs exist in archive dirs
- **system prompt unchanged?** → `NOT_VERIFIABLE` — runtime injects current date; archived dump may omit system turn
- **parser called?** → `PASS` — non-empty action or EMPTY_XML/TOOL_CALL implies predict→parse path ran (except PREDICT_CRASH)
- **parser result correct under frozen grammar?** → `NOT_VERIFIABLE` — for malformed examples, rejecting non-computer_use/bash matches frozen grammar; other classes need manual review
- **QEMU action actually executed?** → `PASS` — GUI actions appear in traj; EMPTY/CRASH steps have no GUI dispatch
- **action result inserted into next turn?** → `NOT_VERIFIABLE` — bash injection path exists in code; not fully reconstructed from sanitized archive
- **accidental history truncation?** → `NOT_VERIFIABLE` — no direct counterfactual dump of pre-send messages per step
- **mutation of messages by transport?** → `PASS` — transport deep-copies messages; rejects tool schema keys — unit-tested path
- **step counter correct?** → `PASS` — traj step_num sequence length=31 vs metadata steps=31
- **terminal classifier correct?** → `PASS` — inspect={'evidence_kind': 'CANONICAL_STRING_ACTION', 'canonical_last_action': 'DONE', 'raw_action': 'DONE', 'valid_done': True, 'has_steps': True, 'row_count': 31, 'traj_path': '/mnt/data2/Vinh/agent/results/paper2_exec/study2-flash/retrieval-f010/G1/retrieval-f010/traj.jsonl'} checkpoint=DONE
