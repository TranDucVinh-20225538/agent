# Extractor lock (10-line rule)

**Status:** LOCKED 2026-09-13. Outcome-blind. Code: `extract_i.py`. Tests: `test_extract_i.py` (synthetic; no \(V\), no human \(L\)).

Run: `python3 test_extract_i.py`

---

1. `episode_status` first (`EPISODE_ELIGIBILITY.md`). EXEC_FAIL never classified as ABSTAIN.
2. Strip `<action>…</action>` if present.
3. `I_ans` = argument of the last `send_msg_to_user(...)` found by walking `steps` **backward**, using `step.action`, else last assistant `content`/`message` if that string is itself `send_msg_to_user(...)`.
4. `click` / `fill` / `goto` are not answers. Last assistant chat is often an action wrapper; do not treat that as \(I_{\mathrm{ans}}\) unless it parses as `send_msg_to_user`.
5. No such action → `I_ans = None` (missing). `send_msg_to_user("")` or whitespace → empty → ABSTAIN on string families.
6. `I_url` = last non-empty `step.url` walking backward (terminal observation step allowed).
7. Family `string` (WA/VWA string_match, AssistantBench emptiness): ABSTAIN iff `I_ans` missing/blank; else DETERMINING.
8. Family `url`: ABSTAIN iff `I_url` missing/blank.
9. Family `string_url`: ABSTAIN if either channel missing/blank. Not an abstract stratum (`n=4` and `n=6`).
10. This module must not import or read `cum_reward` or `trajectory_success`.

Do not retune after seeing ABSTAIN rates.

`report_infeasible` is **not** `send_msg_to_user`. QC of eight SUCCESS∩ABSTAIN (`out/qc_success_abstain.md`): seven EXTRACTOR_LAG; one QC_OPEN (`webarena.723` gpt-4o, unexplained, closed). Overlay only. Do not reopen this module. Path A stopped.
