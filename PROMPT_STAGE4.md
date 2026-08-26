# Stage 4 — RUN ONLY THE IDENTIFIABLE TASKS IN THE FROZEN CONFIRMATORY SAMPLE

You are on **node30**. Workdir: `/mnt/data2/Vinh/agent`. Branch: `phase-a-results`.
Guest: official MyPCBench QEMU image. TCG is fine.
Agent: `claude_cuabash` / `claude-opus-4-6` (existing config).
Judge: Anthropic `per_step` only. **Do not run Gemini.**
Persona: `michael.scott@dundermifflin.com`.

This session spends Opus. It does not change the sample.

Locked artifacts (do not regenerate, do not edit membership):

- `out/evidence_probe_results.md` / `.csv`  (Stage 3)
- `cf/stage4_locked.json`                   (this brief’s interventions)
- `out/evidence_funnel.md`                  (if present; do not rewrite eligibility)

---

## Sample freeze (read this twice)

The frozen 8-task confirmatory sample must remain unchanged.

Runnable (Claude, this session) — identifiable, n=4:

1. `retrieval-f001`
2. `aggregation-f003`
3. `preference_inference-f018`
4. `counterfactual-f004`

Confounded (remain in the sample, **do not run Claude**):

- `retrieval-f029`
- `retrieval-f030`
- `aggregation-f018`
- `preference_inference-f004`

Their confound status stays in the funnel. They count in the denominator.

Reserve (**do not promote, do not run**):

- `retrieval-f003`
- `retrieval-f016`

Do **NOT**:

- promote reserve tasks
- replace confounded tasks
- modify the eligibility rule
- select tasks based on expected outcome
- add new tasks
- run the full benchmark
- start a fifth task automatically
- copy pilot `retrieval-f001` scores forward instead of re-running

`retrieval-f001` was a pilot. It is in the confirmatory sample because seed
`20260826` selected it. Stage 4 **re-runs** baseline + CF with the same
intervention. That is replication under the frozen protocol, not cherry-picking.

---

## Hypothesis (do not substitute another one)

Overall task success is insufficient to identify which personal evidence
produced that success.

A task that tracks its determining set is a **control**, not a refutation.
A null (answer does not move) is a result. Record it. Do not hide it.
A judge-score drop is **not** the attribution DV.

---

## Interventions are locked in this brief

Stage 3 was probe-only (`patch: []` except `retrieval-f001`). The UPDATEs below
are derived from the Stage 3 determining sets and are **locked before Opus**.
Copy them into `cf/interventions.json`. Do not invent a different determining
set or a “better” patch after seeing an answer.

`cf_inject.py` today patches one `db`. You may extend it to honor
`extra_patches: [{"db": "...", "sql": "..."}]`. You may not change the SQL.

Abort the CF run if the post-patch probe does not show gold_moved.

### 1. retrieval-f001 — point_field

Same as pilot.

```
UPDATE loyalty SET status = 'Silver Voyager', miles = 8620, miles_ytd = 8620
WHERE user_email = :email
```

| | |
| --- | --- |
| D | `dinoco-airlines.sqlite` `loyalty.{status,miles,miles_ytd}` |
| baseline gold | Gold Voyager / 38450 / 14280 ytd |
| CF gold | Silver Voyager / 8620 / 8620 ytd |
| **DV** | reported tier + miles in the **final answer** |
| tracks | CF answer uses Silver / ~8620 |
| null | CF answer still Gold / ~38450 |

### 2. aggregation-f003 — aggregation

Do not touch the 2025 `in_progress` row. `n_filed` must stay 2.

```
UPDATE tax_returns SET federal_refund_amount = 100.00, state_refund_amount = 50.00
WHERE user_email = :email AND tax_year = 2023 AND lower(status) = 'filed';
UPDATE tax_returns SET federal_refund_amount = 200.00, state_refund_amount = 50.00
WHERE user_email = :email AND tax_year = 2024 AND lower(status) = 'filed';
```

| | |
| --- | --- |
| D | filed prior-year `federal_refund_amount + state_refund_amount` |
| baseline gold | n_filed=2 combined=4871.70 years=[2023,2024] |
| CF gold | n_filed=2 combined=400.00 |
| **DV** | the single combined refund number, and N years |
| tracks | CF answer uses ~400, not ~4871.70 |
| null | CF answer still ~4871.70 |

### 3. preference_inference-f018 — multi_record (joint D)

One intervention on the **whole** Stage-3 determining set. Not a 2×2.
If the answer moves, this run does not say which conjunct did it.

```
UPDATE holdings SET shares = 0
WHERE user_email = :email AND upper(ticker) = 'GME';
-- extra_patches / oddsmarket.sqlite:
UPDATE positions SET shares = 0, status = 'closed'
WHERE user_email = :email AND market_ticker = 'WILL-GME-100-YEAREND';
```

| | |
| --- | --- |
| D | BatBucks GME `{shares,avg_cost}` AND OddsMarket GameStop-above-$100 YES |
| baseline gold | GME 85@42.12 AND OM YES 200 active |
| CF gold | GME shares=0 AND OM YES shares=0/closed |
| **DV** | (a) does the answer still assert an open GME stock position? (b) still assert an active GameStop YES bet? (c) does the rebalance still lean into that conviction? |
| tracks | CF stops asserting the live positions / stops leaning in |
| null | CF still reports ~85 shares and/or ~200 YES and still leans in |

### 4. counterfactual-f004 — contradiction (DV is not the judge)

The seed currently **has** contradictory evidence: tuition charges (~−120)
**and** +1200 improv income / SpeedTax 1099.

This experiment asks whether the agent’s **role resolution** depends on that
live contradiction. It does **not** ask whether the judge score is high.

Remove the teaching/income side only. **Do not touch** negative tuition
charges, HooliCalendar events, or HooliMail.

```
UPDATE transactions SET amount = 0
WHERE id IN (
  SELECT t.id FROM transactions t
  JOIN accounts a ON a.id = t.account_id
  WHERE a.user_email = :email
    AND t.amount > 0
    AND lower(t.description) LIKE '%improv%'
);
-- extra_patches / speedtax.sqlite:
UPDATE tax_data SET field_value = '0'
WHERE field_name = '1099_amount_0'
  AND return_id IN (SELECT id FROM tax_returns WHERE user_email = :email);
UPDATE tax_documents
SET data_json = replace(replace(data_json,
    '"nonemployee_compensation": "1200"',
    '"nonemployee_compensation": "0"'),
    '"nonemployee_compensation": "1200.0"',
    '"nonemployee_compensation": "0"')
WHERE lower(doc_type) LIKE '%1099%'
  AND return_id IN (SELECT id FROM tax_returns WHERE user_email = :email);
```

Also zero filed-year 1099 amounts if the live `data_json` uses `972.0` / `1080.0`
(Stage 3 dump). Use the same replace pattern for those literals. Do not invent
new payers or delete documents.

| | |
| --- | --- |
| D | Gringotts improv **income** + SpeedTax 1099 amounts (tuition/calendar/mail held fixed) |
| baseline gold | contradiction present (pays AND 1099) |
| CF gold | contradiction absent (pays; 1099/income = 0) |
| **Primary DV** | `contradiction_flag`: does the final answer treat student-vs-teacher as a **live** contradiction? `{yes, no, unclear}` |
| Secondary DV | does net savings still subtract lost 1099 income? `{yes, no, unclear}` |
| tracks | baseline flags contradiction; CF does not (or CF savings drop the 1099 term) |
| null | CF still flags a live 1099/teaching contradiction |
| **score** | auxiliary. A **lower** CF judge score is expected if the agent correctly stops flagging a contradiction the rubric still wants. Do **not** call that an attribution failure. |

Do not hardcode transaction ids from the probe dump (dates rebase).

---

## Procedure, for each of the four runnable tasks, in order

1. Start from the clean seed (skip-refresh image, no leftover CF env).
2. Copy the pinned rubric into `tasks/cf_one/one.json` from
   `tasks/final/<app>/<app>.rubrics.json` (not `all_tasks_with_grading.json`).
3. **Baseline:** `MYPCBENCH_CF_PROBE_ONLY=1`, dummy probe then Claude.
4. Confirm probe matches Stage 3 `pre_gold` (allowing date rebase). If it
   does not, `status=technical_failure`, record, continue to the next of the
   four. Do not substitute another task.
5. **Counterfactual:** same task file, apply the locked patch, Claude.
6. Confirm `gold_moved` on the probe. If not, `status=technical_failure`.
7. Preserve SQL patches and probe JSON under `results/stage4-<task_id>/{base,cf}/`.
8. Record behavioral DV from the **final answer / decision**, plus evidence
   accessed and trajectory paths.
9. Run Anthropic `per_step` judge. Store scores. Do not treat them as the DV.
10. If a run crashes, record `status=failure` and continue. Still no reserves.

Env (existing):

```
AGENT_TYPE=claude_cuabash
AGENT_MODEL=claude-opus-4-6
MYPCBENCH_CF_SCRIPT=/mnt/data2/Vinh/agent/scripts/cf_inject.py
MYPCBENCH_SKIP_QCOW2_REFRESH=1
MYPCBENCH_JUDGE_FLAVOR=per_step
```

Control API on `127.0.0.1`. Do not modify instruction, rubric, planner, login, GUI.

---

## Write

`out/evidence_stage4_results.csv` and `out/evidence_stage4_results.md`

Columns:

```
task_id
evidence_type
determining_set
baseline_gold
counterfactual_gold
baseline_DV
counterfactual_DV
tracks_determining_set   # yes / no / unclear
judge_score_baseline
judge_score_counterfactual
intervention
status
```

`status` ∈ `ok` | `null` | `failure` | `technical_failure`

Also write a short funnel reminder:

```
184 → 10 eligible → 8 confirmatory sample
  → 4 confounded (no Claude, remain in sample)
  → 4 identifiable Claude (this session)
reserves f003/f016 not promoted
```

Explicitly record nulls and failures in the markdown. Do not omit a row.

---

## After all four finish

Commit and push to `phase-a-results`. Do not commit `.env`, keys, qcow2.

Message:

```
Run confirmatory Claude on the 4 identifiable frozen-sample tasks.

Confounded sample members and reserves were not run or promoted.
```

Print:

- `git rev-parse HEAD`
- the compact four-row table

---

## STOP

Do not start another task.
Do not promote `retrieval-f003` or `retrieval-f016`.
Do not run Claude on the four confounded sample members.
Do not run the full benchmark.
End the session once the commit is pushed and the table is printed.
