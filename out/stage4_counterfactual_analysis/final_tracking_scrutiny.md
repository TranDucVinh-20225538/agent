# Final tracking scrutiny (reviewer-facing)

Snapshot `520cf8c`. Gold = guest/SQL. DONE = last `traj.jsonl` action. Tracking is **not** inferred from score.

Do **not** headline `10/15 = 66.7%`. Report per model. Qwen `1/1` is not an invariance finding.

## Coverage table (semantic)

| Model | Valid pairs | Tracking-valid | Type A | Score-sensitive | Type B | Invariance (Type A / tracking-valid) | 95% CI |
|---|---:|---:|---:|---:|---:|---|---|
| Claude | 9 | 7 | 6 | 1 | 2 | 6/7 = 0.857 | [0.42, 1.00] |
| GPT | 8 | 7 | 3 | 4 | 1 | 3/7 = 0.429 | [0.10, 0.82] |
| Qwen3.5-35B-A3B | 1 | 1 | 1 | 0 | 0 | 1/1 = 1.000 | [0.025, 1.00] |
| Union (descriptive only) | 18 | 15 | 10 | 5 | 3 | 10/15 = 0.667 | [0.38, 0.88] |

Qwen execution: 5/20 DONE trajectories. EMPTY_XML/FAIL stay out of the semantic denominator.

---

## Chain used for every pair below

`G0` (guest probe_before / unpatched world) → `I` → `G1` (guest probe_after / extra_probes) → final DONE answer reflects `G1`? → rubric `per_rubric_max` / scalar `S` → `ΔS`.

---

## Type B (sensitive claims) — hold after re-read

### 1. Claude `retrieval-f030` — 100 → 100 — KEEP Type B

**G1 (CF guest):** `gold_moved=false` on the 1099 probe (1099-NEC still `$1200`, Scranton Improv Academy). Extra sqlite: `charitable_contributions` / `charitable_total` = `100` (was `950`). Designed sqlite-only charitable move.

**Base DONE** (`results/phaseb-claude-retrieval-f030/base/retrieval-f030/traj.jsonl`): answers **Tax Year 2024 filed** 1099-NEC **`$1,080`**, charitable **`$950`**. Cross-check table lists 2025 file `$1,200` as a *different year*, not as the return amount. Determining 1099 for this task is TY2025 most-recent return `$1200`. **Base does not report that amount as the answer.**

**CF DONE:** TY2025 in-progress, 1099 **`$1,200`**, charitable claimed **`$100`**, and flags file `$950` vs return `$100`. CF **does** track the moved conjunct.

**Pair tracking:** incomplete because base missed `D` (TY2025 1099 `$1200`). Judge `per_rubric_max` base `[1,1,1,1]` score **100**. High score on a wrong-year 1099.

**Nuance to write honestly:** this Type B is *mis-selected return year on base*, not “CF missed charitable.” CF tracked charitable `$100`. Do not describe it as failing the designed sqlite-only miss; describe it as completion score remaining 100 while the pair does not jointly report the intended 1099 state.

### 2. Claude `preference_inference-f018` — 100 → 100 — KEEP Type B

**G1:** GME `shares=0`. OddsMarket `WILL-GME-100-YEAREND` YES `shares=0` `status=settled` (`cf-retry-inject` guest).

**CF DONE:** BatBucks table **GME 0 shares / $0 basis** (tracks GME conjunct). OddsMarket table still lists **GameStop above $100 by year-end | YES | 200 | $16.00** as an **active** position. Guest says settled/0. **OM conjunct not tracked.** Rebalance still “lean INTO GameStop” off a `$16` YES.

**Judge:** CF `per_rubric_max` all 1s, score **100**. Rubric can credit a plausible lean-in if one conjunct is missed (registry). That is the Type B mechanism.

### 3. GPT `counterfactual-f004` — 87 → 87 — KEEP Type B

**G1:** guest extra `1099_amount_0` = `"0"`; improv income patched. Calendar/tuition held.

**CF DONE:** still “The 1099 was a **$1,200** 1099-NEC guest instructor stipend” and “**1099 stipend you may be giving up: $1,200/year**” / net savings `$1,068`. Hedge (“if one-time/past-only”) does **not** replace reporting current gold `$0`. **Does not track zeroed 1099.**

**Judge:** CF score **87**, `per_rubric_max` last item 0. Score stays high/unchanged vs base 87 while the contradiction-removing `$0` 1099 is not the reported teaching income.

---

## Type A (tracking-valid, ΔS=0) — hold after re-read

Quotes are from last DONE `response`. Rubrics for f001/f003/f016/agg-f003 do not pin seed numbers (registry).

| Pair | G1 | Final answer | S | Rubric vs D |
|---|---|---|---|---|
| Claude f001 | Silver / 8620 | “**Silver Voyager** … **8,620 miles**” | 100→100 | No Gold/38450 pin |
| GPT f001 | same | “**Silver Voyager** … **8,620 miles**” | 100→100 | same |
| Qwen f001 | same | terminate text: Gold 38450 / Silver 8620 | 100→100 | same; only Qwen semantic pair |
| Claude f003 | 80000 | “**W-2 Gross Wages: $80,000**” (base `$136,320`) | 65→65 | Does not name 136320; 65 is formatting/year criterion, invariant |
| GPT f003 | 80000 | `136,320` / `80,000` only | 100→100 | same |
| Claude f016 | 7114.20 + cash 50 | “**$7,114.20**” / “**$50.00**” (base `$8,213.25` / `$420`) | 100→100 | Does not name 8213.25 |
| Claude f029 | 90000 / 18000 / Dunder | Box 1 **$90,000**, Box 2 **$18,000**, Dunder Mifflin (base 142000/28400) | 100→100 | Employer pin; leftover Box 3 $142k is **not** in `I` |
| Claude agg-f003 | combined 400 | “**$400**” (base **$4,872** ≈ 4871.70 rounded) | 80→80 | Does not name 4871.70 |
| GPT agg-f003 | 400 | “**$400** total” (base `$4,871.70`) | 50→50 | same; 50 is not “success,” but ΔS=0 with tracking |
| Claude agg-f018 | sqlite char/HO = 0; W-2/1099 held | Base SpeedTax **$950 / 104** match file; CF SpeedTax **$0.00 / 0** vs file **$950 / 104** | 100→100 | Designed Type B cell; Claude **tracked** sqlite-only move → Type A |

GPT f001 is Type A and belongs in the Type A list (included above).

---

## Score-sensitive (tracking-valid, ΔS≠0) — supports separability

Same experiment, same agents can produce ΔS=0 and ΔS≠0 **after tracking**:

- Claude pref-f004: HD Cooper 88 → Backyard 59; **100→79** (rubric pins Cooper’s as HD top).
- GPT f016: 8213.25/420 → 7114.20/50; **100→85**.
- GPT f029: 142000/28400 → 90000/18000; **33→100**.
- GPT f030: 1099 $1200 both legs; charitable **$950→$100**; **53→100** (designed Type B cell became score-sensitive).
- GPT pref-f004: HD Backyard 59; **100→58**.

This blocks “the benchmark always yields invariant scores.”

---

## Designed Type B ≠ observed Type B

Pre-specified Type B IDs: f030, agg-f018, pref-f018.

Observed: Claude f030 Type B (wrong-year 1099, not the sqlite miss); Claude agg-f018 Type A; GPT f030 score-sensitive; Claude pref-f018 Type B (joint D). Outcomes are not manufactured by the design list.

---

## Verdict

The 15 tracking-valid and 3 Type B labels **stand** on trajectory + guest evidence. Paper-1 can be written from this census **without more tasks**, provided:

1. Per-model rates, not 10/15 as abstract headline.
2. Qwen described as execution coverage, not 100% invariance.
3. Type B write-ups use the exact misses above (year / OM YES / $1200 stipend), not writer fields.
4. Claim: completion, counterfactual tracking, and score sensitivity are distinct.
