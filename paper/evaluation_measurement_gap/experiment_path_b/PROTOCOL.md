# Path B protocol

**Status:** B1 frozen 2026-09-13. B2 sample frozen; labels blocked on screenshots.

`B_LOCK.md` is the constant lock. This file is the run protocol.

## B1 (done)

1. `python3 experiment_path_b/fetch_webjudge.py`
2. `python3 experiment_path_b/classify_b1.py`
3. Do not retune `T` or `MAX_IMAGE` after `out/b1_result.md`.

## B2 (open, blocked)

1. Obtain v2 `trajectory/*.png` for every row in `out/b2_episode_sample.csv`.
2. Align `frame_index` to `image_judge_record` order (same order WebJudge scored).
3. Pilot: 6 episodes (2 cap_hit + 2 operator_nearmiss + 2 other_control), two annotators, codebook as written. Fix only ambiguity, not the DECISIVE definition to chase a rate.
4. Main: remaining 24 episodes. Two annotators on the full `b2_annotation_sheet.csv` (1065 items). They never see `in_discard`, `Score`, `final_eval`, or keep/discard.
5. Primary B2 number: among the 536 discarded frames, P(DECISIVE) with IRR. Secondary: same rate on matched keep frames from the same episodes.
6. This agent is not an annotator.

## Sample note (after B1, before B2 labels)

The codebook’s 80–150 episode target assumed the cap would fire often.
B1 showed 10/1790 cap-hits. The frozen sample is therefore a **census
of all cap-hits** plus 20 matched controls (30 episodes), not an
inflated draw of non-events. Seed `20260913`. `sample_b2.py`.
