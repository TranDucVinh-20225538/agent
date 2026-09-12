# P4-M external validation — pre-outcome / non-leakage audit

**Status:** PASS for the protocol that was actually run (eligibility-only).
**Y inspection:** NOT PERFORMED. Phase 5 was not opened.

This audit records that the overnight pass **stopped before** constructing \(Y\). It is not a claim that a transport table is leak-free, because no transport table exists.

## Checks

| Check | Result |
|---|---|
| Sample manifest complete | N/A — no sample. Manifest records NOT CREATED. |
| Each sampled episode has provenance | N/A — none sampled |
| \(I\) mapping works or classified C | Not applied to episodes. Design \(I\) remains final assistant NL only. |
| \(k\) from task specification, never from \(s\) | No \(k\) assigned. No \(s\) recovered. WAV/WA spec JSON was counted for **field names** only. |
| \(P\) unchanged | `p4_instrument_v2.py` hash unchanged; file not edited |
| \(E\) unchanged conceptually | Not executed |
| \(L\) source independent | No episode-level \(L\) bound. Spec gold fields were not used as \(Y\). |
| No evaluator output reaches \(I/P/E\) | No \(I/P/E\) execution on external \(\tau\). WAV `eval_result.json` not fetched. `merge_log.txt` / `SCORES.json` not fetched. |
| No outcome field influences selection | No selection. |
| No post-hoc parser modifications | None. |
| HIT/MISS/success labels not used to build the frame | Confirmed: no frame. |

## What was read from task JSON (not \(Y\))

- Presence/absence of keys: `eval`, `eval_types`, `reference_answers`, `expected.retrieved_data`, evaluator class names.
- Counts of tasks and of eval-type tags.
- One WAV demo `agent_response.json` **schema** (structured fields `task_type` / `status` / `retrieved_data`). That file is an evaluator input shape, not an episode in a sample, and was not scored with `score_v2`.

## Leakage conclusion

No leakage of evaluator success into a sample or into \(P\), because neither a sample nor a parser run was produced.

If a later authorized study opens a corpus, this file does **not** substitute for a new pre-outcome audit on that sample.
