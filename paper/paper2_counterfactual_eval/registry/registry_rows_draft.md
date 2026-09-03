# Paper 2 registry rows — draft (D, kind, role, w_i)

DRAFT, not frozen. Per-row human review required before any row is
used for inject-probe design. Rules this draft follows (frozen
2026-09-03): draft `determining` only from rubric criteria that pin a
specific value/record; never auto-draft `held` or `distractor`;
every non-drafted criterion is recorded under `omitted_rubric_ids`
with a reason; w_i is role-based (1 for determining/held, 0 for
distractor) per DESIGN.md §2, not re-derived here; rows with 0 or
>4 determining candidates are flagged `needs_review` and
excluded from auto-freeze.

- Tasks: **27**
- Clean (0 flags, still needs a human pass for `held`/`distractor`): **19**
- `needs_review`: **8**
- Total drafted `determining` components: **67**

## Rows

| id | category | rubric criteria | determining (draft) | omitted | needs_review |
| --- | --- | ---: | ---: | ---: | --- |
| aggregation-f004 | aggregation | 4 | 4 | 0 |  |
| aggregation-f020 | aggregation | 6 | 3 | 3 |  |
| aggregation-f036 | aggregation | 6 | 5 | 1 | cap_gt4_determining(5) |
| aggregation-f037 | aggregation | 5 | 1 | 4 |  |
| aggregation-f040 | aggregation | 7 | 2 | 5 |  |
| contradiction-f003 | contradiction | 8 | 5 | 3 | cap_gt4_determining(5) |
| contradiction-f004 | contradiction | 5 | 3 | 2 |  |
| contradiction-f006 | contradiction | 5 | 2 | 3 |  |
| contradiction-f011 | contradiction | 4 | 0 | 4 | zero_candidates |
| contradiction-f014 | contradiction | 5 | 1 | 4 |  |
| contradiction-f017 | contradiction | 4 | 2 | 2 |  |
| contradiction-f022 | contradiction | 8 | 1 | 7 |  |
| contradiction-f024 | contradiction | 9 | 1 | 8 |  |
| counterfactual-f001 | counterfactual | 7 | 3 | 4 |  |
| counterfactual-f002 | counterfactual | 6 | 5 | 1 | cap_gt4_determining(5) |
| counterfactual-f003 | counterfactual | 6 | 5 | 1 | cap_gt4_determining(5) |
| counterfactual-f005 | counterfactual | 6 | 5 | 1 | cap_gt4_determining(5) |
| counterfactual-f010 | counterfactual | 6 | 5 | 1 | cap_gt4_determining(5) |
| counterfactual-f013 | counterfactual | 5 | 2 | 3 |  |
| preference_inference-f010 | preference_inference | 6 | 2 | 4 |  |
| preference_inference-f014 | preference_inference | 6 | 3 | 3 |  |
| retrieval-f002 | retrieval | 3 | 1 | 2 |  |
| retrieval-f005 | retrieval | 3 | 2 | 1 |  |
| retrieval-f009 | retrieval | 4 | 1 | 3 |  |
| retrieval-f010 | retrieval | 4 | 1 | 3 |  |
| retrieval-f017 | retrieval | 4 | 2 | 2 |  |
| situated_action-f029 | situated_action | 5 | 0 | 5 | zero_candidates |

## needs_review detail

### aggregation-f036 — cap_gt4_determining(5)

- determining candidate `aggregation-f036.c1` (money_usd): Agent sums every seeded Scranton Improv outbound class debit as it appears in the ledger in the last full calendar year (matching 'Scranton Improv Workshop' or 'SCRANTON IMPROV ACADEMY' case-insensitively, where Scranton Improv is the payee/merchant — debits from both description patterns must be included in the sum) to an annual total computed from the actual seeded ledger charges (not a fabricated estimate); excludes any inbound teaching-income credits such as 'Scranton Improv Academy - 1099-NEC payment' or 'VENMO SCRANTON IMPROV ACADEMY', and excludes transportation/eTaxi debits where Scranton Improv is only the venue address, not the payee
- determining candidate `aggregation-f036.c2` (money_usd): Agent reports the last-full-calendar-year transaction count alongside the annual dollar total
- determining candidate `aggregation-f036.c3` (money_usd): Agent shows the individual Scranton Improv charge amounts as they appear in the ledger (whether they are the same unit amount or vary by session) and uses those values to explain the total
- determining candidate `aggregation-f036.c4` (money_usd): Agent reports the total spend for the last full calendar year on Scranton Improv (no specific per-charge unit-cadence assertion required — flat per-session, biweekly, monthly, or mixed are all acceptable as long as the sum reconciles)
- determining candidate `aggregation-f036.c5` (money_usd): Agent delivers the last-full-calendar-year total and supporting count in a single answer

### contradiction-f003 — cap_gt4_determining(5)

- determining candidate `contradiction-f003.c0` (categorical): Agent reads the Dinoco profile's actual loyalty tier and mileage balance directly from Dinoco Airlines (and notes if it differs from Michael's Gold Voyager claim)
- determining candidate `contradiction-f003.c4` (money_usd): Agent computes miles-earned-from-actual-flights and compares to the profile balance
- determining candidate `contradiction-f003.c5` (money_usd): Agent flags the Dinoco mileage discrepancy between profile balance and booked flights and explains whether the gap is realistic or inflated
- determining candidate `contradiction-f003.c6` (money_usd): Agent cites Dinoco Airlines flight history, Gringotts charges, and HooliMail itineraries as the sources reconciling Michael's booked flights with his profile balance
- determining candidate `contradiction-f003.c7` (money_usd): Agent completes the walk-through of flights Michael has actually booked and reports whether the Dinoco profile's live mileage balance is realistic or inflated relative to the flights Michael has taken

### contradiction-f011 — zero_candidates

- (no determining candidates drafted — needs hand design)

### counterfactual-f002 — cap_gt4_determining(5)

- determining candidate `counterfactual-f002.c0` (money_usd): Agent sums liquid rescue cash across Gringotts checking, Gringotts savings, BatBucks portfolio cash, and OddsMarket balance using the live app values
- determining candidate `counterfactual-f002.c1` (money_usd): States the Gringotts credit-card headroom (credit limit minus current balance) and confirms that amount is insufficient by itself to cover the Barbados hotel settle
- determining candidate `counterfactual-f002.c2` (money_usd): Agent computes whether Gringotts checking+savings together cover the Cheskepdia Barbados hotel settle total and reports the resulting residual balance with a qualitative risk note tied to that residual
- determining candidate `counterfactual-f002.c3` (money_usd): Agent proposes BatBucks partial liquidation as a fallback rescue option and cites the agent's at-cost brokerage value
- determining candidate `counterfactual-f002.c5` (money_usd): Agent locates and cites the Cheskepdia policy emails in HooliMail — the CHESK-POL-2 'Alternate card on file: hold policy' ($200 alternate-card hold on decline) and the CHESK-POL-1 updated cancellation grace-period email — and factors them in before ranking the rescue options (these emails exist in the seed; reporting that no such policy email exists does not earn credit)

### counterfactual-f003 — cap_gt4_determining(5)

- determining candidate `counterfactual-f003.c0` (categorical): Agent extracts the funding and commitment figures from a HooliMail conversation whose subject is exactly 'THE DUNDIES ARE BACK BABY' together with ~/Documents/Dundies_2026_Categories.txt, reconciles any difference between the two sources, and correctly uses the document's award-category count as the planned trophy quantity. If more than one live conversation carries that exact subject, the figures are graded against the copy the agent opened; where the copy it opened carries no funding figures, the agent is credited for saying so and proceeding from the document's numbers.
- determining candidate `counterfactual-f003.c1` (money_usd): Agent derives a trophy unit price from last year's HooliShop trophy or award order, as the instruction asks; if no prior-year order carries a usable unit price the agent uses and labels a current-catalog Trophy or Award product, then multiplies by the planned quantity
- determining candidate `counterfactual-f003.c2` (money_usd): Agent establishes the planned venue cost from the sources it consults, or clearly labels the assumption it makes when no venue figure is available, and computes the overrun as that planned cost doubled rather than inventing an unsupported venue price
- determining candidate `counterfactual-f003.c3` (money_usd): Agent proposes concrete dollar cuts to trophies, catering, or both that reconcile to the venue overrun
- determining candidate `counterfactual-f003.c4` (money_usd): Agent computes available Gringotts credit as the visible card limit minus the amount currently owed or used and checks the revised plan against it

### counterfactual-f005 — cap_gt4_determining(5)

- determining candidate `counterfactual-f005.c0` (money_usd): Agent computes the GameStop doubling purchase cost as (current GME shares) * (GME avg_cost) from the live BatBucks holdings table
- determining candidate `counterfactual-f005.c1` (money_usd): Agent reads the live BatBucks cash balance, compares it against the computed doubling cost, and names the resulting shortfall
- determining candidate `counterfactual-f005.c2` (money_usd): Agent reads the Gringotts Sapphire Preferred credit-card available headroom (limit minus current balance) and flags that the card alone cannot fund the GameStop purchase
- determining candidate `counterfactual-f005.c3` (money_usd): Agent evaluates checking + savings + card feasibility for the GameStop purchase using the live Gringotts balances and states the resulting impact on each account balance
- determining candidate `counterfactual-f005.c5` (money_usd): Agent verifies whether Gringotts checking plus savings alone covers the computed GameStop doubling cost without touching the credit card, using the live Gringotts balances, and reports the residual balance

### counterfactual-f010 — cap_gt4_determining(5)

- determining candidate `counterfactual-f010.c0` (money_usd): Agent sums Gringotts checking + savings into a single liquid-cash figure as the first-class upgrade budget (no credit card)
- determining candidate `counterfactual-f010.c1` (money_usd): Agent reads the set of upcoming Dinoco flights as the app displays them and computes total first-class upgrade cost using Michael's stated $600-per-flight assumption (per-leg or per-trip counting are both acceptable, as is the actual Dinoco upgrade fee if shown). Any consistent count of the upcoming flights the app lists is acceptable — if the Upcoming list includes short internal/test itineraries (e.g. DN-CKW confirmation codes), counting them or leaving them out are both correct as long as the agent's arithmetic matches the set it enumerated.
- determining candidate `counterfactual-f010.c2` (money_usd): Agent concludes whether the first-class upgrade is feasible without touching the credit card and reports the residual balance after the upgrade spend
- determining candidate `counterfactual-f010.c3` (entity): Agent lists the upcoming Dinoco trips shown live in the app by confirmation number + duration when evaluating which upgrades are worth it; every upcoming trip the app displays counts, and the agent is not required to exclude short internal/test itineraries.
- determining candidate `counterfactual-f010.c4` (integer): Agent differentiates upgrade priority across the upcoming Dinoco trips shown live in the app with a defensible criterion (e.g., longest-duration as highest-value and shortest as least-value on diminishing returns, OR if the upcoming flights are all comparable long-haul routes, prioritizing by travel companion or time-of-day factors) instead of upgrading every flight blindly; the ranking is judged against whatever set of upcoming trips the agent defensibly enumerated.

### situated_action-f029 — zero_candidates

- (no determining candidates drafted — needs hand design)

