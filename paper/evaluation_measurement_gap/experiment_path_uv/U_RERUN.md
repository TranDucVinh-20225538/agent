# U2 prerequisite — re-run UV to recover R

Released HF columns do **not** include `step2_relevance_scores` or
`step3_grouped_screenshots`. Screenshots **are** in `trajectories`.

To open U2 (human decisive-frame on the actual discard set):

1. Export PNGs (`export_screenshots.py`) in chronological `screenshots[]` order.
2. **What we actually run (`run_r.py`), not full `MMRubricAgent`:**
   - Rubric: a **short** explicit-criteria prompt (not official step 0a/0b/0c).
     Degrees of freedom remain here. Do not claim “official UV rubric.”
   - Relevance prompt: official `MM_SCREENSHOT_CRITERION_RELEVANCE_PROMPT`.
   - Grouping + filter: official Step 3 (`group_r.py`, `K=5`).
   - DISCARD = union complement (`discard_set`).
   - Steps 4–10 (evidence / outcome) are **not** run.
3. Then `sample_u2.py` once, then humans per `CODEBOOK.md` (two stages).
   This agent does not annotate.

Re-run uses **our** LLM endpoints and is a **new instrument instance**.
Do not claim we recovered the authors’ unpublished R. Do not compare
our `uv_outcome_success` to the released column as a paper finding
unless a pre-specified reproduction check is written first.

Key source (2026-09-13): `/Users/cubo/CMU/agent/.env` `OPENROUTER_API_KEY_LARGE`.
No project `.venv` on this machine.

Pilot (1 OM2W task, 10 frames): discard 4/10; spend ~$0.05.
Instance: `openai/gpt-5.5` (rubric) + `openai/o4-mini` (relevance).
Official grouping (`K=5` + relevance filter). Not authors' R.
Steps 4–10 not run. Do not treat pilot as a paper rate.
