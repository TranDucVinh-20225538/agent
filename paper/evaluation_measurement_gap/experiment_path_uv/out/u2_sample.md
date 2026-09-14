# U2 sample (drawn after R, rule locked before R)

**Status:** DRAWN. Seed `20260913`. Do not redraw.

Seed `20260913`. Event episodes: 40. Controls: 1.
Pilot-6 (first event task_id): Airbnb--a13e4231, Akc--eb2db4b7, Allrecipes--75a1b5dc, Amtrak--323bd85e, Apartments--c0fa2c0e, Arxiv--71f8de18.
Stage-1 items: 1232. Discard items: 903 (`|D|` = U2 denominator).
Stage-2 sheet is built after stage-1 DECISIVE labels (`join_u2_stage2.py`).

## Check after full 106-R (not a new draw)

| Symbol | Value | Rule |
|---|---|---|
| Universe | 106 OM2W | lock |
| \|E\| | **97** | `n_discard >= 1` → sample 40 (not census) |
| Zero-discard | 9 | — |
| \|C\| | **1** | `n_discard == 0` and `n_frames > 5` |
| Controls drawn | **1** | `min(20, \|C\|)`. Do not pad. |
| \|D\| | **903** | sampled discard frames in event episodes |

The 8 zero-discard episodes with `n_frames ≤ 5` are **not** in `C`.
They never had opportunity for top-K to drop a frame. They are not
“kept everything.” Only `Recreation--c09721cc` (n=6, n_discard=0) is
a true control.

Annotators see `u2_stage1_sheet.csv` only (`item_id`, `task_id`,
`frame_index`). Keep `u2_stage1_key.csv` in the lab.
