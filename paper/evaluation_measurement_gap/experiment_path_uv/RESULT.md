# Path UV RESULT

**Date:** 2026-09-14  
**Status:** U1 **DONE and frozen**. R **DONE**. U2 Stage 1 **JOINED** (3 humans). U2-irr blocked on Stage 2.

Not Path A. Not Path B. Not M1a transport. `uv_*` is never gold.

## Licensed U1 finding

On released CUAVerifierBench `trajectories` (260 rows), `n_screenshots > K`
is the **necessary** condition for per-criterion top-K to be able to drop
a frame. It is **not** the discard set. Union-across-criteria discard
needs `step2_relevance_scores` (not in HF columns).

| | OM2W Browserbase (primary) | internal (secondary) |
|---|---:|---:|
| Episodes | 106 | 154 |
| **K=5 n > K** | **93/106** | 52/154 |
| n min / median / max | 4 / 19 / 101 | 0 / 0 / 101 |
| K=3 n > K | 106/106 | 53/154 |
| K=7 n > K | 84/106 | 52/154 |

Internal median 0: many `internal` rows have no screenshots in the
release (one parquet shard is 732 KB). Do not pool with OM2W.

On the public OM2W split, top-5 **can** truncate almost every trajectory
(median 19 frames). That is a better *opportunity* rate than WebJudge
B1 (10/1790 cap-hits).

Chain (do not skip a link):
**opportunity** (`n>K`) ≠ **discard** (union complement of keep lists) ≠
**isolation DECISIVE** ≠ **IRRECOVERABLE** (decisive and not equivalent
in the kept set). Only the last is the M1a-shape analogue. See
`CODEBOOK.md` / `SAMPLE_LOCK.md`.

## Forbidden

- 93/106 as “UV discarded evidence”
- M1a transported
- Using `uv_outcome_success` or human outcome as frame gold
- Putting U1 or U2-iso in `main.tex` as E2 / M1a transport

## U2 Stage 1 (lab; not U2-irr)

3 raters `VINH-1` / `TOAN-1` / `HUNG-1`. Fleiss D vs not **0.689**.
Majority U2-iso **234/893 = 0.262** (hold 10). See `out/u2_s1_human.md`.
Stage 2 sheet: 361 items (`join_u2_stage2.py`). Not in `main.tex`.

## Frozen artifacts

| File | sha256 |
|---|---|
| `out/u1_cells.csv` | `db4e45d080b88ea4fe900ec0068a282020f30ea38f442c380db43aba72841a14` |
| `out/u1_meta.jsonl` | `237d86086d5468430713f71e4a6dc33ea158a25ea81c902625548616f92f3673` |
| `src/mm_rubric_agent.py` | `865d93e6a120f1b8a9a4ce1a834ece4680d466e893f602322ff94b29a46792d6` |

Do not retune K. Next: `U_RERUN.md` (API) then U2 humans. This agent does not annotate.
