# P4-B Phase 4 post-hoc slice (not a new estimand)

**Status:** analysis only. No additional agent runs. Spend **$0**.  
**Object:** the already-scored confirmatory 40 episodes (`N_B = 20` clusters × Flash + GPT).  
**Not:** a re-estimate of E1–E4, a licence to lower the E3/E4 floor, or a claim that P4 “accurately measures agent reliability.”

Primary Phase-4 record remains `construction/out/p4b_phase4_results.md` (commit `4c3d14bc`).

---

## Locked reading (do not inflate)

P4-B is **positive-but-incomplete**:

> P4 demonstrated zero false-positive HITs and invariance under controlled
> irrelevant-span perturbations, while revealing substantial
> observation-channel abstention under natural agent behavior. However,
> natural success/failure correspondence could not be fully evaluated
> because the prespecified eligibility floors were not met.

| Gate | Result | Meaning here |
|---|---|---|
| E1 | **PASS** (0 false HIT) | Instrument did not invent correspondence on gold-absent last-text |
| E2 | **PASS** | Status/committed value invariant under C5/C6 |
| E3 | **NOT_EVALUABLE** (4 eligible clusters < floor 5) | Natural C1 (success + valid evidence → HIT) not gated |
| E4 | **NOT_EVALUABLE** (0 eligible) | Natural C2 (wrong committed value → MISS) not gated |
| Constructive transfer | **NULL_E3_NOT_EVALUABLE** | Incomplete validation, not an E1/E2 fail |

Do not write “P4 accurately measures agent reliability.”  
Do not run more agents to hunt E3/E4 eligibility after seeing this table.

---

## Hero table: execution ≠ measurement

All 40 confirmatory legs terminated `DONE`. P4 scores **only** last assistant text.

| Execution | P4 measurement | Count |
|---|---|---|
| DONE | HIT | 5 |
| DONE | MISS | 5 |
| DONE | ABSTAIN | 30 |

**30/40 last-texts were insufficient to establish the determining state, even though every computer-use loop finished.** Terminal completion is not observation-grounded measurement success.

---

## 1. The 30 ABSTAIN

| Cause | n | Share of ABSTAIN | Share of 40 |
|---|---|---|---|
| `no_anchor` | 30 | 30/30 | 30/40 |
| `absent` | 0 | 0 | 0 |
| `ambiguous` | 0 | 0 | 0 |
| `channel_indeterminate` | 0 | 0 | 0 |

Every abstention is the same mechanism: the frozen V2 locator found **no instruction-anchor substring** on a newline-terminated line of the last assistant text. The instrument did not then mine screenshots, tools, or intermediate turns.

### By model (descriptive; not a ranking)

| Lane | HIT | MISS | ABSTAIN | ABSTAIN cause |
|---|---|---|---|---|
| Flash (`qwen/qwen3.8-flash`) | 2 | 4 | 14 | 14 `no_anchor` |
| GPT (`openai/gpt-5.5`) | 3 | 1 | 16 | 16 `no_anchor` |

ABSTAIN is **not** a single-model artifact (14 vs 16 on 20 legs each).

### By family (8 episodes each = 4 clusters × 2 models)

| Family | HIT | MISS | ABSTAIN | ABSTAIN / 8 |
|---|---|---|---|---|
| Locate | 3 | 3 | 2 | 0.25 |
| Reconcile | 2 | 1 | 5 | 0.62 |
| Filter | 0 | 1 | 7 | 0.88 |
| Compute | 0 | 0 | 8 | 1.00 |
| Tally | 0 | 0 | 8 | 1.00 |

ABSTAIN **concentrates** on Compute and Tally (16/16) and nearly all Filter (7/8). Locate is the only family with more committed scores than abstentions.

### By kind

| Kind | n episodes | HIT | MISS | ABSTAIN |
|---|---|---|---|---|
| `money_usd` | 16 | 5 | 0 | 11 |
| `integer` | 12 | 0 | 0 | 12 |
| `entity` | 6 | 0 | 2 | 4 |
| `categorical` | 6 | 0 | 3 | 3 |

All five HIT are `money_usd`. All twelve integer episodes (Compute/Tally) abstain. That is a **slice of this 40-run last-text**, not a licence to drop integer clusters.

12 of 20 clusters are ABSTAIN on **both** models.

---

## 2. HIT / MISS (committed last-text only)

**HIT (5):** B01 Flash, B01 GPT, B02 Flash, B09 GPT, B10 GPT — Locate/Reconcile money. Eligible E3 τ are exactly these five; they are all HIT, but they span only **4 clusters**, so E3 stays NOT_EVALUABLE.

**MISS (5):** B03 Flash, B04 Flash, B04 GPT, B12 Flash, B15 Flash. All `mismatch`. Post-hoc geometry (not a new gate): each last-text names a value near gold, but V2 `entity`/`categorical` commit is the **remainder after the first anchor cut**, so the committed span is a longer clause (`listed on the marsh hopper card is **Wren Cobb**.`) rather than the gold token. That is fail-closed unique-or-abstain / V3 mismatch on the observation channel. It is **not** evidence that the desktop loop “failed the task,” and it is not converted into E4 (E4 requires gold *absent* from the cleaned channel plus a unique non-gold candidate).

---

## 3. What this does and does not support

**Supports (already gated):** specificity (E1 = 0 false HIT); invariance (E2); the construct split *task-complete ≠ evidence-sufficient*.

**Does not support:** a reliability leaderboard; a claim that 30/40 abstain means the metric is “too strict to ship” *or* that it is “working as a score.” Abstention is a **feature of fail-closed correspondence** on this channel, and a **usability cost** if someone wanted a dense ranking. P4 is testing the former.

**Incomplete by design of the floor:** natural C1/C2 correspondence remains unevaluable on this confirmatory set. That is a validation-design result, not a reason to add runs or rewrite anchors after seeing τ.

---

## 4. Files

Machine tables: `construction/out/p4b_phase4_posthoc.json`  
Source legs: `construction/out/p4b_phase4/legs.jsonl`  
No API calls. Instrument/corpus hashes unchanged.
