# Path B RESULT

**Date:** 2026-09-13  
**Status:** B1 **DONE and frozen**. B2 **OPEN but blocked** on screenshots + humans.

Not Path A. Not M1a transport. Not E2. `Score` is never gold.

## Licensed B1 finding

On the released WebJudge o4-mini judge product (1790 episodes, six agent files), after per-screenshot `Score` is collected, **qualified-then-cap discard** (`Score >= 3` enters `R`, then `R[50:]` is dropped) is **rare and agent-specific**.

| | T=2 (sensitivity) | **T=3 (PRIMARY)** | T=4 (sensitivity) |
|---|---:|---:|---:|
| Episodes | 1790 | **1790** | 1790 |
| Cap-hit episodes | 16 | **10** | 0 |
| Qualified frames | 16331 | **12551** | 4143 |
| Discarded after cap | 944 | **536** | 0 |
| Discard / qualified | 0.0578 | **0.0427** | 0 |

At primary T=3, all 10 cap hits are **Operator** (10/300). Agent-E, Browser Use, Claude 3.5, Claude 3.7, and SeeAct: **0/1490**.

The 10 Operator episodes (from `out/b2_episode_sample.csv`, role `cap_hit`):

| task_id | n_qualified | n_discard | n_scored |
|---|---:|---:|---:|
| b3f8bd9198d9d157e0848109563c4b23 | 172 | 122 | 212 |
| fe33894188d20d7469f37a9fd855e7ff | 135 | 85 | 185 |
| 33bd2cdcea4fcc42a09a8a1e4e5841c6 | 134 | 84 | 180 |
| 2e4e21cf1449c6894b17d571c47b77ea | 126 | 76 | 181 |
| 4639a54f3ab549864fd8d60b7398b1e1 | 99 | 49 | 195 |
| 7e1047f4803237f319c004f7a7f6bccb | 92 | 42 | 103 |
| 6b2cfae0ef25c73d1224b6ab74cb8b63 | 91 | 41 | 325 |
| a13e4231a3d6a7000c622c56448d97ba | 76 | 26 | 126 |
| b2f4fde2fce122a93c7b578086cb0585 | 58 | 8 | 481 |
| 753f372c189d3b306623cb0c65b50320 | 53 | 3 | 71 |

## What B1 is allowed to say

- The released instrument **does** implement collect-then-`[:50]` after `Score >= T`.
- On this product, that discard **fires** on 10/1790 episodes at the authors' T=3.
- Those 10 are long Operator traces. Other released agents never hit the cap at T=3.

## What B1 is forbidden to say

- Those discarded frames were determining / decisive (that is B2).
- M1a transported from MyPCBench.
- Public CUA benches are invalid.
- WebJudge scores are wrong.
- 536/12551 is a reliability error rate.
- “Almost never” as a reason to retune `T` or `MAX_IMAGE`.

## Frozen artifacts

| File | sha256 |
|---|---|
| `out/b1_cells.csv` | `87b8a5e1a633de78b736d00e5d44dc17b812441ec631e3993866a77471d25431` |
| `out/b1_result.md` | `4a72b73d3ffc31f405f84499ca2714521687eb03dc743883a79c679f7863286a` |
| `data/agente_results.json` | `23c04410958bb488397b39d8d08a0138c0a87feaf304f9ae63c11e726a49bf26` |
| `data/src/webjudge_online_mind2web.py` | `e3cd499b7c1fc92cbd51d3c4216c95ebab774c2c2cd998c5ad6dad94710780c4` |
| `out/b2_episode_sample.csv` | `291413feaada767aa10f34532f1a43526d755da5d566a08c7164bdf0cba2d4dd` |
| `out/b2_frame_sample.csv` | `3a5f4bcff7c69e99201810991c80acded1dd0f9cff50a86f210f5622852c9dd0` |
| `out/b2_annotation_sheet.csv` | `676dab9857097b54c3651d73484767d8bd28f2190fe717aad3b3c2a20c1d0c25` |

Do not retune `T` or `MAX_IMAGE`. Do not recode cells.

## B2 status

Sample frozen (`sample_b2.py`, seed `20260913`) **before labels**:

- 30 episodes: 10 cap-hit (census) + 10 Operator near-miss + 10 other-agent controls.
- 1065 annotation items; 536 of them are the actual T=3 discard set (all of it), plus matched keep frames from the same episodes (annotators do not see keep/discard).

**Blocker:** released JSON is `{Response, Score}` only. Screenshot bytes are not there. Online-Mind2Web public repo ships one example trajectory, not the 1790. Operator traces were collected by OSU NLP via the Operator web UI (HF discussion #8), not an API dump. Task-level `human_label.json` is **not** frame gold.

B2 starts only when v2 `trajectory/*.png` exist for every sampled `(agent_file, task_id)`, aligned to `image_judge_record` order. This agent does not annotate.

Until then: do not put B1 in the manuscript as E2 or as “M1a on WebJudge.”
