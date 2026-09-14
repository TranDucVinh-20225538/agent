# P3-CORE human check — 13 M1a rows, same codebook as U2

**Status:** LOCKED 2026-09-13, before full Path-UV 106-R rates.
**Annotators:** 3. Majority vote. Primary IRR: Fleiss' κ.
**Codebook:** `experiment_path_uv/CODEBOOK.md` (DECISIVE / EQUIVALENT /
IRRECOVERABLE unchanged).
**Sheets:** `evidence-loss-audit` (`build_stage1` / `build_stage2`).
**Join protocol** `PROTOCOL.md` in this folder stays frozen. This file
is an **additional** human layer. It does not reopen the S=100 join and
does not license “screenshots contained gold” from `tab:m1a-s100`.

PNG bundle is on disk (`hpc_import/`, 11/11 dirs, 388 PNG, 0 missing
refs). STOP-NO-PNG lifted. Draw: `out_p3h/` (seed `20260913`).

This agent is not an official annotator. An **A0 draft** walkthrough
exists in `RESULT_P3H.md` / `out_p3h/p3h_*_A0.csv` because the operator
authorized starting. It does **not** replace the locked 3 humans.

## Why

`tab:m1a-s100` is an automatic S-join. Thirteen rows is small and cheap.
Three humans applying the same two-stage codebook puts a person on the
CORE claim (gold entered `found`, then fail-closed aggregation dropped
it), instead of only the locked rubric score.

## Population (closed)

Exactly the 13 rows in `join.json` / `tab:m1a-join`. No 57-leg or
171-leg expansion.

| lane | task | leg | component |
|---|---|---|---|
| flash | counterfactual-f010 | G0 | liquid_cash |
| flash | counterfactual-f013 | G0 | batbucks_dividends |
| flash | counterfactual-f013 | G0 | gringotts_savings |
| flash | counterfactual-f013 | G1 | gringotts_savings |
| flash | retrieval-f009 | G1 | nyc_flight_confirmation |
| flash | retrieval-f010 | G1 | host_name |
| gpt | aggregation-f020 | G0 | batbucks_cash |
| gpt | retrieval-f009 | G0 | nyc_hotel_confirmation |
| gpt | retrieval-f009 | G1 | nyc_flight_confirmation |
| flash | counterfactual-f005 | G1 | gme_shares |
| claude | counterfactual-f005 | G0 | gme_avg_cost |
| claude | counterfactual-f005 | G0 | gme_shares |
| flash | aggregation-f020 | G1 | batbucks_cash |

## Mapping onto the four links

P3 already has typed gold and a known discard (definitional M1a). The
visual check asks whether that discard is **irrecoverable on the
screen**, not whether the extractor log is true.

| Link | P3 analogue |
|---|---|
| Opportunity | Episode has more than the last scored observation. |
| Discard | Gold entered `found` and is absent from the fail-closed survivor (definitional TRUE on these 13). |
| Isolation-DECISIVE | Human, shown task + **one** screenshot, says the **gold component** is determining on that frame. |
| IRRECOVERABLE | Isolation-DECISIVE on a non-last frame **and** Stage 2 says the last/kept observation is NOT_EQUIVALENT. |

Keep-set analogue (lab only): the **last screenshot** of that leg (the
visual stand-in for the last observation the extractor scored). Gallery
foils: other frames of the same unique traj directory, unlabeled.

Annotators do **not** see `found`, match bits, `S`, `Y`, `uv_*`, or
keep/discard tags. They **may** see the task text. They do **not** see
the gold numeral on the Stage-1 card (that would turn the task into
OCR-the-number). The codebook question stays: is this frame determining
for whether the agent completed the stated task, if it were the only
frame?

If a rater cannot tell which component is at issue, they mark UNCLEAR.
Do not print the gold string on the sheet.

## Frame draw (cheap; locked)

Per **unique traj directory** (11 dirs, 13 rows share two dirs):

- Always include the last screenshot.
- Include up to 2 earlier screenshots: prefer frames whose adjacent
  `traj.jsonl` line contains the gold string when that join is already
  recorded; else take the two frames immediately before last.
- Seed `20260913`. Sort paths before RNG if a further subsample is
  required. Cap **3 frames per unique directory**.

13 rows × ≤3 frames is the Stage-1 universe. Shared-traj rows (f013-G0
two components; f005-G0 two components) reuse the same images and get
**separate** Stage-1 items (same PNG, different task/component context
in the lab key only — the annotator sheet still shows only task text +
one image).

Stage 2: every Stage-1 DECISIVE frame that is **not** the last frame,
plus last-frame DECISIVE foils. Gallery = last frame + other drawn
frames of that directory, target excluded, order shuffled.

## Numbers (after labels; not now)

| ID | Estimand | Role |
|---|---|---|
| P3H-iso | P(isolation DECISIVE \| drawn non-last frames) | Secondary |
| P3H-red | P(REDUNDANT \| those DECISIVE) | Secondary |
| **P3H-irr** | **P(IRRECOVERABLE \| drawn non-last frames)** | **Primary** |

UNCLEAR held out. Do not treat S=100 as DECISIVE. Do not change this
rule after Path-UV R rates appear. Do not enlarge to 171.

## Do not

- Start before `hpc_import/` has PNGs for a row (STOP-NO-PNG on that row).
- OCR screenshots as a substitute for the three humans.
- Use this agent as an annotator.
- Move `experiment_path_uv/run_r.py` to “share” helpers with this packet.
- Claim transport of M1a. This is a human check **on CORE**, not a new
  instrument.
