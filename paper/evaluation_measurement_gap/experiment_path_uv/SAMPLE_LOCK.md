# U2 sample lock — frozen 2026-09-13 before full 106-R rates

**Status:** LOCKED. Seed `20260913`. Primary split OM2W only.
**Annotators:** 3 (Fleiss' κ + majority). Locked before full 106-R.
Do not rewrite after `r_results.jsonl` is complete.
U1 `n > 5` (93/106) may be used; **discard counts from R may not**
change this rule.

Pilot R on `Babycenter--7680a920` (4/10 discard) is **not** a sampling
stratum and is not a reason to prefer that task.

## Universe

`fara7b_om2w_browserbase` (n=106). Do not pool `internal`.

## Reproducibility (seed is not enough by itself)

Sort `r_results.jsonl` rows by `task_id` **before** building `E`/`C` or
consuming `Random(20260913)`. JSONL write order must not change the
sample. After each episode draw, sort the drawn lists by `task_id`
again so later frame shuffles see a fixed sequence. Discard frame
indices are emitted in sorted order before the sheet shuffle.

## After R exists — episode draw

Let `E` = episodes with `n_discard >= 1`.
Let `C` = episodes with `n_discard == 0` and `n_screenshots > 5`
(`n_frames` on the R row is that count).

| If | Draw |
|---|---|
| \|E\| ≤ 40 | Census all of `E`. Controls: `min(20, \|C\|)` from `C`, nearest `n_screenshots` to median(`E`); ties broken by stable `task_id` order (no extra RNG). |
| \|E\| > 40 | `Random(20260913).sample(E, 40)`. Controls: 20 from `C` by the same nearest-median + `task_id` tie-break. |

Do not add episodes to chase a rate. Do not drop `Babycenter--7680a920`
if the RNG includes it; do not force it in if the RNG excludes it
(except it may appear in `E` naturally).

## Frame draw (stage 1)

**Event episode:** all discard frames + `min(n_discard, n_keep)` keep
frames, keep sample `Random(20260913)` without replacement.

**Control episode:** `min(10, n_frames)` frames, `Random(20260913)`.

Annotation sheet shuffles items; hides `in_discard`.

## Pilot: 6 event episodes

After the locked episode draw, sort `event` by `task_id`. The pilot is
the **first 6** of that list (or all of `event` if fewer than 6).

These 6 are a **subset of the locked sample**, not a separate draw.
They count in `U2-irr` / `U2-iso` / `U2-red`. Do not drop them after
the pilot. Use them only to check codebook ambiguity (IRR) before
the remaining event+control sheets.

## Stage 2 draw

Every stage-1 **DECISIVE** frame in an **event** episode (discard and
keep targets). Gallery built per `CODEBOOK.md`. Control-episode frames
do not enter stage 2 (no discard set to test recoverability).

## Primary / secondary numbers (denominators locked)

Let `D` = sampled **discard** frames in event episodes (stage 1).

| ID | Estimand | Role |
|---|---|---|
| U2-iso | P(isolation DECISIVE \| D) | Secondary. Not M1a-shape. |
| U2-red | P(REDUNDANT \| D) | Secondary. Evidence still in keep-set. |
| **U2-irr** | **P(IRRECOVERABLE \| D)** | **Primary.** Only this is the M1a-shape analogue. |

UNCLEAR held out of each rate; report n held out. Do not use
`n_screenshots > 5` as the U2 denominator.

## N after R (do not retune the draw)

Census / 40+20 stays. When `r_results.jsonl` is complete, record `|E|`
and `|D|` in the sample md. That is a **check**, not a new draw.
If `|D|` is tiny, report it; do not enlarge the sample after seeing rates.

**Recorded 2026-09-14 (draw already written):** `|E|=97`, `|C|=1`,
`|D|=903`. Controls = 1 (`Recreation--c09721cc`). Do not add
zero-discard `n≤5` episodes to chase 20 controls.

## Script

`sample_u2.py` runs **once** after R is complete, using this file only.
If the script disagrees with this file, this file wins.
