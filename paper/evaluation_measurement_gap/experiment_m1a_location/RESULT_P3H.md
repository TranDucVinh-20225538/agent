# P3-H — 13 M1a rows, codebook applied

**Status:** PNG bundle complete. Stage-1 draw locked. **A0 draft labels
exist. This is not the licensed 3-annotator packet.** Do not put these
rates in `main.tex`. Do not treat them as Fleiss / majority.

Rater A0 = this agent, after the user authorized starting. Codebook
`CODEBOOK.md` still requires **3 humans**. A0 is a lab walkthrough so
the packet is not empty.

## Draw (machine; locked)

Seed `20260913`. 11 unique dirs × 3 frames. 13 rows → **39** Stage-1
items (shared trajs reuse PNGs, separate items). Every drawn PNG exists.
See `out_p3h/p3h_draw.md`.

## A0 Stage-1 / Stage-2 (one rater)

Non-last drawn frames **n = 26** (13 × 2). UNCLEAR held out: 0.

| ID | A0 | Role |
|---|---|---|
| P3H-iso | **9/26** | isolation DECISIVE on a non-last frame |
| P3H-red | **6/9** | those DECISIVE still EQUIVALENT on last |
| **P3H-irr** | **3/26** | **DECISIVE and last NOT_EQUIVALENT** |

IRRECOVERABLE items (A0):

1. `flash/counterfactual-f013/G0/batbucks_dividends` frames 48 and 49 —
   paid dividends **64.88** on a text dump; last frame is accounts
   (**16413.28** savings, no 64.88).
2. `flash/retrieval-f010/G1/host_name` frame 12 — “Hosted by Sandals
   Resorts Concierge”; last frame is a price breakdown, no host name.

REDUNDANT (determining mid-traj **and** still on last): liquid cash
66493.59 on flash f010; BatBucks cash 420 on both aggregation-f020
legs; NYC flight DN-87856 on flash retrieval-f009 G1.

GPT retrieval-f009 G0/G1: all drawn frames are “Unable to connect”.
Isolation NOT_DECISIVE. Gold lived in **text**, not on these screens.
S=40 on those rows is not visual gold.

## What this does and does not license

Does: the locked 13-row packet is **runnable**. On a single unscreened
pass, some M1a discards look **irrecoverable on the last screenshot**,
and some look **redundant** (same number still on the last frame). That
is the four-link split the codebook asked for.

Does not: 3-rater majority, Fleiss’ κ, a PDF number, “screenshots
contained gold” as a prevalence claim, transport of M1a, 171-leg
expansion. S=100 is still not DECISIVE.

## Next (still required for the licensed check)

Three humans fill `out_p3h/p3h_stage1_labels_BLANK.csv` then Stage 2
from `p3h_stage2_sheet.csv`. Replace A0. Do not hire this agent as
rater 2 or 3.
