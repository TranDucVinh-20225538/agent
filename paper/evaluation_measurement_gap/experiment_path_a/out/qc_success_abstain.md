# QC — eight ELIGIBLE SUCCESS ∩ ABSTAIN rows

**Date:** 2026-09-13  
**Cells file unchanged:** `path_a_cells.csv` sha256 `614416284d3854183afeea330d4611c2f514612aafb263034721f0d3362fd516`  
**Extractor unchanged.** This file is interpretation of eight rows, not a retune.

Do **not** copy “eight released SUCCESS have empty \(I\)” into `CLAIM_LEDGER.md` or `draft/main.tex`.

## Ordered hypotheses (protocol)

1. Earlier `send_msg_to_user` than last step → last-step locked \(I\) ≠ BrowserGym \(I\) (EXTRACTOR_LAG).
2. `url_match` SUCCESS with a URL the extractor missed.
3. `cum_reward` rose on a mid-trajectory step, not last-step official.
4. Truly empty \(I\) all trajectory and \(V=1\) (existence; harness / oracle leak).

## Outcome

All eight are family `string` (not `url`). **Zero** `send_msg_to_user` anywhere in action or assistant chat. Hypothesis 1 (earlier send) is **false**. Hypothesis 2 does not apply.

| n | What |
|---|---|
| 7 | Last non-null action is `report_infeasible(...)`. Locked \(I_{\mathrm{ans}}\) is send_msg-only, so \(E=\)ABSTAIN. BrowserGym maps infeasible chat to a STOP with answer `N/A`. Six of seven are WebArena `string_match` with `fuzzy_match` gold `N/A`. Recode **EXTRACTOR_LAG**: last-step locked \(I\) ≠ oracle \(I\). Not “score without \(I\).” |
| 1 | `webarena.723` / gpt-4o: no `send_msg`, no `report_infeasible`, no infeasible chat role, gold `N/A`, `cum_reward=1`. **QC_OPEN** — unexplained; closed. Not a finding. Do not reopen the extractor. |

`cum_raw_reward=0` on all eight while `cum_reward=1.0`. Not used to recode ABSTAIN→FAIL.

**STOP.** Path A is closed. Do not retune. Do not count another rate.

## Overlay

`qc_success_abstain.csv`. Maximum recode is EXTRACTOR_LAG / QC_OPEN on these eight keys. Do not retune `extract_i.py`. Do not recode ABSTAIN as FAIL.
