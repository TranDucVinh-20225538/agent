# P3-0.7 — Identification Audit (pre-registration)

Status: **FROZEN BEFORE EXECUTION.** Written after seeing the 0.6 category counts, and
before computing any window-level quantity.

Amendment to `P3_0_SPEC.md`, following `P3_0_RECALL_AUDIT_SPEC.md`. It modifies nothing:
not Gate 0, not Gate 1, not the extractor at `3242c30`, not `protocol/matching.py`, not
`out/study2_gold_path_lock.json`, not any archive, not any Paper 2 number. It adds one
read-only observation of the frozen extractor's own intermediate state.

---

## 1. Baseline carried forward from 0.6

No separate artifact is created for the 0.6 recomputation. Its numbers are recorded here,
and this section is the citable form.

0.6 ran once on 57 legs and 134 leg×component rows, `ANOMALY = 0`, and the frozen
extractor reproduced every recorded gold and match value. Raw categories: `MATCH` 20,
`RECALL_MISS` 39, `ABSENT` 61, `VACUOUS_GOLD` 14.

Five rows are **structurally unreadable** and are excluded from every share below. All
five are `ABSENT`, so the exclusion mechanically *raises* the recall-miss share; it is not
a neutral cleaning and must not be presented as one.

| # | leg | component | why unreadable |
|---|---|---|---|
| 1 | `A / flash / preference_inference-f014 / G1` | `designated_booking_property` | gold contains `(`; `extract_entity` applies `re.split(r"[(\[]", s)[0]`, so the frozen extractor can never report it whatever the agent writes |
| 2 | `A / gpt / preference_inference-f014 / G1` | same | same |
| 3 | `gate0 / claude / preference_inference-f014 / G1` | same | same |
| 4 | `A / flash / retrieval-f009 / G0` | `nyc_checkin_date` | `cand=0` and `_DATE_RE` is ISO-only, so "no date reported" and "non-ISO date reported" are indistinguishable |
| 5 | `A / flash / retrieval-f009 / G1` | same | same |

Recall-miss share of interpretable non-matches, `RECALL_MISS / (RECALL_MISS + ABSENT)`,
Wilson 95%:

| population | miss | absent | share | 95% CI |
|---|---|---|---|---|
| `A` | 24 | 39 | **0.381** | [0.271, 0.504] |
| outside `A` | 15 | 17 | **0.469** | [0.309, 0.636] |
| all 57 legs | 39 | 56 | **0.411** | [0.317, 0.511] |

The two CIs overlap heavily, so **there is no evidence that `A` differs from outside `A`**
in recall-miss rate. By kind: `integer` **0.722** [0.491, 0.875], `entity` 0.368
[0.191, 0.590], `money_usd` 0.345 [0.234, 0.477], `state` 0/3, and `categorical` has
2 `MATCH` and **zero interpretable non-matches**, so it is non-informative.

The pattern that motivates this gate:

| task group | miss | absent | share | 95% CI |
|---|---|---|---|---|
| `counterfactual-*` + `contradiction-f004` | 23 | 16 | **0.590** | [0.434, 0.729] |
| all other tasks | 16 | 40 | **0.286** | [0.184, 0.415] |

The `INT_RE` lookahead hazard was checked and does **not** bind: the only `cand=0`
integer row is `gpt/contradiction-f004/G1`, whose money component also has `cand=0`, and
since `MONEY_RE` matches bare integers the answer contains essentially no numeric token
at all, so that absence is genuine. Zero rows are excluded on `INT_RE` grounds.

Gate 0 status, restated: Gate 0 did not establish completion-conditioned evidence
dissociation under the frozen extractor, and its negative result is **instrument-limited**.
Its `0/4` was `0/3` testable, because `gpt/preference_inference-f010` is vacuous by
construction. `flash/counterfactual-f005` and `gpt/retrieval-f010` are **leads, not
evidence**: presence is not correctness and not reliability.

## 2. The mechanism, and the prediction

`extract_money`, `extract_int` and `extract_entity` each accumulate one candidate per
label hit into a list `found`, then return `_unique_or_none(found)`. That function returns
`None` whenever any accumulated value disagrees with the first:

```
first = norm[0]
for x in norm[1:]:
    if isinstance(first, Decimal) and isinstance(x, Decimal):
        if first != x:
            return None
    elif str(first).casefold() != str(x).casefold():
        return None
```

So the frozen extractor is **fail-closed on ambiguity**. In a counterfactual or
contradiction probe the agent naturally states both the pre-injection and the
post-injection value of the same quantity, two label windows then disagree, and the
extractor returns `None` on exactly the task family it was built to measure.

**Primary prediction.** For a `RECALL_MISS` row, at least one `_unique_or_none` call
during that component's extraction received a `found` list containing two or more
mutually disagreeing values.

**Secondary prediction.** The share of `RECALL_MISS` explained this way is higher in
`counterfactual-*` + `contradiction-f004` than in the other tasks. This is the
non-tautological half: the primary prediction could hold by any route, whereas the
mechanism as stated claims a *specific cause*, namely the injected world producing two
values for one quantity, and that cause implies task-level concentration.

Both predictions are answerable from the existing archive. No model run, no human judge,
no new construct, no change to the extractor.

### 2.1 A competing cause, identified a priori: a broken label

While validating the classifier against synthetic answers — before running on any
archive row — one frozen label was found to be malformed:

```
("contradiction-f004",  "gme_avg_cost"): [r"avg(erage)? cost", r"average cost"],
("counterfactual-f005", "gme_avg_cost"): [r"avg(erage)? cost"],
```

`avg(erage)? cost` matches `avg cost` and `avgerage cost`. It does **not** match
`average cost`, which is the natural spelling. Verified:

```
r'avg(erage)? cost' vs 'avg cost'      -> True
r'avg(erage)? cost' vs 'average cost'  -> False
r'avg(erage)? cost' vs 'avgerage cost' -> True
```

A scan of every frozen label containing an optional group found this construction only
here; `top (inbox )?sender` and `upcoming (dinoco )?flights` are both well formed.

This yields a **within-quantity natural control that already exists in the frozen code**.
The two components share an id, a kind, and the gold value $42.12$, and differ only in
that `contradiction-f004` carries a covering second label while `counterfactual-f005`
does not. On the synthetic answer `"Average cost: $42.12 per share."` the frozen
extractor gives `HIT` for `contradiction-f004` and `None` for `counterfactual-f005`.

**Sub-prediction, fixed here.** If label coverage is the operative cause for this
quantity, then `RECALL_MISS` rows on `counterfactual-f005/gme_avg_cost` are `M2`, and
`RECALL_MISS` rows on `contradiction-f004/gme_avg_cost` are not `M2` on label-coverage
grounds. This is checkable on five existing rows and is independent of the primary
prediction: `M2` and `M1` are mutually exclusive causes, so this control can fail while
the primary prediction still holds, or vice versa.

Recording this competing cause in advance matters because `counterfactual-f005` is the
largest single contributor to `RECALL_MISS` in the 0.6 baseline. Had it been discovered
after the run, attributing its misses to a label typo rather than to `_unique_or_none`
would have been indistinguishable from rescuing the mechanism.

## 3. Population

All 134 leg×component rows of `out/p3_0_recall_audit.jsonl`, over the same 57 legs. No
subsetting, no cells or lanes added. Paths are rejoined from
`out/study2_hatd_legs.jsonl` and `out/p3_0_extracted.jsonl` on `(lane, task, leg)`.

The runner **must abort** if the row count is not 134, the leg count not 57, or the
category counts not exactly `MATCH` 20, `RECALL_MISS` 39, `ABSENT` 61, `VACUOUS_GOLD` 14,
`ANOMALY` 0.

## 4. Instrumentation, not reimplementation

The window logic is **not** reimplemented. `study2_hatd_extract._unique_or_none` is
wrapped by a recorder that returns the original function's value unchanged and appends
`(found, returned)` to a log; the frozen `extract_component` and `gold_for_component` are
then called exactly as `extract_leg` calls them.

Two guards make the faithfulness checkable rather than asserted:

1. every recomputed `reported` and `gold` must equal what 0.6 recorded, or abort — so the
   instrumentation provably did not alter behaviour;
2. whenever the recorder logs `returned is not None`, the filtered `found` list must be
   non-empty, or abort — the consistency condition implied by the frozen function.

Because `_unique_or_none` returns `None` if and only if its filtered input is empty or
contains a disagreement, the two causes are separated directly from the frozen
function's own output, with no predicate of mine substituted for it.

## 5. Cause taxonomy

For each `RECALL_MISS` row, exactly one cause. The three buckets the analysis is
organised around are `M1`, `M2+M3+M4`, and `ABSENT`; the split of the second bucket is
reported because it determines what a fix would have to address if the mechanism fails.

| cause | condition | reading |
|---|---|---|
| **M1** disagreement | some call received a filtered `found` with ≥2 disagreeing values | **mechanism-consistent**; `_unique_or_none` fail-closed |
| **M2** no label hit | `reported is None`, every filtered `found` empty, and no label regex matched anywhere in the answer | label coverage failure |
| **M3** window miss | `reported is None`, every filtered `found` empty, but some label regex did match | window scope failure: gold is in the text but outside every ±window |
| **M4** wrong pick | `reported is not None` but does not match gold | the first-candidate heuristic chose a different value |

`M1` is split further, because the two forms differ in how damning they are:

* **M1a** — gold is among the disagreeing values under the frozen matcher for that kind.
  The extractor **saw the correct value and discarded it**.
* **M1b** — gold is not among them. The disagreement is between two values that are both
  wrong, and recovering it needs more than removing the fail-closed rule.

For each `M1` row the actual disagreeing values are reported verbatim, because they are
the content of the mechanism and not merely its signature: the claim is that they are the
pre- and post-injection values of one quantity, and that is checkable by inspection of the
reported list without any judgement call.

Labels are taken from the frozen `LABELS` table, with the default
`re.escape(component_id.replace("_", " "))` where absent, and the frozen
`[oddsmarket, yes, position, \bshares\b]` list for the special-cased
`contradiction-f004 / oddsmarket_gme_yes`.

`MATCH`, `ABSENT` and `VACUOUS_GOLD` rows are classified too and reported, so the
`M1` rate among misses can be read against its rate elsewhere rather than in isolation.

## 6. Reporting, fixed in advance

1. Every `RECALL_MISS` row with its cause, and for `M1` rows the verbatim `found` list.
2. Cause counts overall, by stratum, by kind, and by task.
3. The primary quantity: `M1 / RECALL_MISS`, Wilson 95%.
4. The secondary quantity: `M1 / RECALL_MISS` for `counterfactual-*` +
   `contradiction-f004` versus all other tasks, both with Wilson 95%.
5. `M1a` versus `M1b` counts.
6. Cause counts for `MATCH` and `ABSENT` rows, as the contrast class.
7. The §2.1 control: the cause of every `gme_avg_cost` row in both tasks, side by side.

No threshold is declared, here or afterwards. Consistent with the standing rule of this
project, no fraction is nominated in advance as "large enough" and none may be invented
after the fact.

## 7. Pre-registered reading, both directions

* **`M1` is the plurality cause of `RECALL_MISS`, with the task-level concentration.**
  The mechanism holds. P3 then has a mechanistic account rather than an observation that
  recall is low: the frozen measurement layer discards recoverable evidence precisely
  where the counterfactual manipulation creates two values for one quantity. The
  identification failure is a property of the fail-closed aggregation rule, and it is
  repairable in principle.
* **`M1` is the plurality cause but without the task-level concentration.** The
  fail-closed rule is implicated but the injected-world explanation is not. Report the
  primary result and record the secondary prediction as **failed**; do not retrofit a
  different cause story onto the same numbers.
* **`M1` is not the plurality cause.** The mechanism is **abandoned**, stated plainly and
  without salvage, and the `M2`/`M3`/`M4` split becomes the diagnosis instead. This is
  the pre-committed outcome: the mechanism was worth stating because it can die, and if
  it dies it is dropped in one sentence rather than weakened into a contributing factor.

In none of these branches does the result revive the completion-dissociation hypothesis
of Gate 0, and in none of them does `text_present` become a measure of correctness or of
reliability. The §1 terminology lock of `P3_0_SPEC.md` and §2 of
`P3_0_RECALL_AUDIT_SPEC.md` continue to apply in full.

## 8. Order of work and hard stops

1. Freeze this document. Commit before running.
2. Run `scripts/p3_0_identification_audit.py` **once**.
3. Stop.

Do **not** run Gate 1 / `p3_0_item_timing.py` (0.4). Do not modify the frozen extractor,
`matching.py`, the gold lock, the archive, or any Study 2 trajectory. Do not commit on the
host. Do not add cells, lanes, tasks, or external labels. No LLM judge, no semantic
similarity, no screenshots, no manual reading. No model runs. No optional stopping: run
once on all 134 rows and report the output whole.
