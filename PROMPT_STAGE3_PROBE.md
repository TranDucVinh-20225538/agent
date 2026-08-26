# Stage 3 — probe ALL eligible tasks, $0 only

You are running on **node30**. Workdir: `/mnt/data2/Vinh/agent`.
Branch: `phase-a-results`. Guest: official MyPCBench QEMU image, TCG is fine.
Persona email: `michael.scott@dundermifflin.com`.

This session is **read-only probes**. It is not an experiment run.

The Stage 1–2 screening is already frozen. Do **NOT** change the eligibility
rule, sample rule, or task selection. Do **NOT** re-run
`python3 scripts/evidence_screen.py`. Use the frozen lists:

- `out/evidence_funnel.md`
- `out/evidence_screening.csv`
- `out/evidence_sample.csv`
- `out/evidence_eligible.json`
- `out/evidence_eligible_ids.txt`

There are **10 eligible** tasks under the frozen A–E criteria.

Run the dummy/schema probe for ALL 10, in this order:

Confirmatory sample (frozen, n=8):

1. `retrieval-f001`
2. `retrieval-f029`
3. `retrieval-f030`
4. `aggregation-f003`
5. `aggregation-f018`
6. `preference_inference-f004`
7. `preference_inference-f018`
8. `counterfactual-f004`

Eligible reserve (not replacements):

9. `retrieval-f003`
10. `retrieval-f016`

Important:

- The 8-task confirmatory sample remains frozen.
- The 2 reserve tasks are **NOT** replacements based on probe outcome.
- Do not reselect, reorder, add, or drop tasks.
- Do not run Claude.
- Do not call any LLM API (`ANTHROPIC_API_KEY` / `OPENAI_API_KEY` unused).
- Do not run the judge (`judge_results.py`).
- Do not `UPDATE` / `INSERT` / `DELETE` / `DROP` in guest SQLite.
- Do not modify instruction, rubric, planner, login, or GUI.
- Do not spend any API credits.

If a probe is non-identifiable, confounded, or technically broken: **record it
and continue to the next id.** Never swap in another task.

---

## What “identifiable” means (this is not “will the result look good”)

A task is identifiable iff, from the live guest data, you can name a
**hypothesized determining set** D such that:

1. D is a concrete set of records/fields (table.column, files on disk if the
   rubric also reads Files).
2. A later counterfactual on D could in principle change the gold the rubric
   scores — you do **not** apply that counterfactual now.
3. Competing gold functions that the pinned rubric also accepts (or that the
   instruction equally licenses) do **not** currently yield the same winner /
   the same scalar. If they do, the contrast is not identifiable on this seed.

This is the f009 rule: count winner = spend winner →
`rejected_not_identifiable`. That is a protocol result, not a failed experiment
and not a reason to pick a prettier task.

A task can be identifiable and still be expected to **support** attribution.
Keep it. Negative and positive probes are both in-sample.

Status vocabulary (use exactly these):

| status | when |
| --- | --- |
| `identifiable` | D exists; competing bases currently disagree or a unique gold scalar exists and could be moved |
| `rejected_not_identifiable` | competing bases currently coincide, n<2 for an aggregation, or no unique D |
| `confounded` | protocol confound (rubric pins a named entity/dollar the live rows currently match; Files and SQLite are dual gold; GUI-only evidence; etc.) |
| `technical_failure` | VM/API/schema dump failed; still keep the row |

`confounded` does **not** demote the task out of the sample. Record it.

---

## Hard constraints on tooling

- Agent: `dummy` / `dummy` only.
- Always `MYPCBENCH_CF_PROBE_ONLY=1`.
- `cf/interventions.json` currently has a probe for `retrieval-f001` among
  these 10. For the other nine you **may** add a **probe-only** entry:
  `SELECT` (and `.schema` notes), `patch: []`, no `dynamic_patch`.
- You may **not** add an `UPDATE`/`INSERT` patch in this session.
- `scripts/cf_inject.py` refuses tasks with no probe spec. Add the SELECT
  after you have seen the live schema, then dump with `--probe-only`.
- Prefer one VM boot per task via
  `scripts/phase_d_eligible_probe.sh`, **or** one long-lived guest and
  Control API `sqlite3` SELECTs. Either is fine. Writes are not.
- Bind Control API to `127.0.0.1` on this host. Do not judge.
- Image: `MYPCBENCH_SKIP_QCOW2_REFRESH=1`. Do not refresh the qcow2.

Pinned rubrics (not `all_tasks_with_grading.json`):

`external/MyPCBench-main/tasks/final/<app>/<app>.rubrics.json`

---

## Per-task hypothesized determining set (verify, do not assume)

These are **starting hypotheses** from the pinned instruction/rubric. The
probe must confirm or revise them from live schema/data. If the live schema
disagrees, trust the guest and record the revision in `determining_set`.

| task_id | evidence_type | hypothesized D | identifiability check |
| --- | --- | --- | --- |
| `retrieval-f001` | point_field | `dinoco-airlines.sqlite` `loyalty.{status,miles}` | unique live tier+miles; already probed in pilot — still dump again and record |
| `retrieval-f029` | point_field | SpeedTax most-recent W-2 `{wages, employer, federal_withholding}` **and** `~/Documents/Tax_2025/w2_summary.txt` | if file and sqlite currently agree, note dual-channel gold; rubric also names “Dunder Mifflin” — flag if that pins gold independently of the row |
| `retrieval-f030` | point_field | SpeedTax most-recent `{1099 amount, 1099 payer, charitable total}` **and** `~/Documents/Tax_2025/1099s.txt` | same dual-channel check; rubric names “Scranton Improv Academy” — flag if pinned |
| `aggregation-f003` | aggregation | SpeedTax filed prior-year returns: `sum(federal_refund_amount + state_refund_amount)`, n_filed ≥ 2 | if n_filed < 2 → `rejected_not_identifiable` (point lookup, not aggregation) |
| `aggregation-f018` | aggregation | in-progress TY2025 SpeedTax line items `{charitable, home-office days, 1099, W-2 gross/withholdings}` vs Files `Tax_2025/*` | identifiable as a reconcile task only if sqlite and files can disagree; if they currently match, record whether an sqlite-only intervention would be silent |
| `preference_inference-f004` | multi_record | TableFind reservation counts (top 5) vs HangryDash order counts (top 5); dine-out vs delivery split | dump both rankings; if the split (or both tops) cannot be flipped independently, reject; **rubric names “Cooper's Seafood House” as HangryDash top** — if live data currently is Cooper's, that is a rubric pin, status `confounded` or note under `reason_if_rejected` while still filling `pre_gold` |
| `preference_inference-f018` | multi_record | BatBucks GME `{shares, avg_cost}` **and** OddsMarket GameStop-above-$100 YES position | if either side is missing, reject; if both exist, identifiable as a joint set |
| `counterfactual-f004` | contradiction_cross_source | Gringotts improv charges vs SpeedTax 1099 from same payer vs calendar blocks vs HooliMail threads | identifiable only if student-vs-teacher signals currently **conflict** (pay tuition **and** receive 1099). If they currently agree, the contradiction is not identifiable on this seed |
| `retrieval-f003` | point_field | W-2 wages on most recent **filed prior-year** SpeedTax return | unique wages figure, not the refund |
| `retrieval-f016` | point_field | BatBucks `sum(shares * avg_cost)` across holdings, plus cash | unique cost-basis total + cash; not market value |

Reserve tasks 9–10 stay reserve even if they look cleaner than a sample member.

---

## Procedure, for each of the 10

1. Boot the official MyPCBench VM using the existing TCG setup (dummy agent).
2. Inspect the relevant SQLite schema/data (and Files paths if the rubric
   names `~/Documents/...`). `sqlite3 /data/<db> ".tables"` / `.schema`.
3. Write the hypothesized determining set, revised if the schema differs.
4. Run the **minimum read-only** probe needed to test identifiability
   (`SELECT` only). Save raw JSON under `results/probe-<task_id>/`.
5. Record the pre-intervention gold state (`pre_gold`).
6. Do **NOT** perform the actual intervention.
7. If not identifiable, `status = rejected_not_identifiable`.
8. If there is a protocol confound or technical failure, record it
   explicitly. Do not replace the task.

You may reuse a prior dummy dump for `retrieval-f001` only if the guest JSON
is on this machine **and** you copy it into `results/probe-retrieval-f001/`
and still fill the row. Prefer a fresh probe-only dump if cheap.

---

## Write these two files when all 10 rows exist

`out/evidence_probe_results.csv`

Columns, in this order:

```
task_id
role
evidence_type
determining_set
identifiable
pre_gold
probe_result
status
reason_if_rejected
```

- `role` = `sample` or `reserve`
- `identifiable` = `true` / `false` / `unknown`
- `pre_gold` = compact live gold (numbers, names, n_filed, rankings). Quote CSV.
- `probe_result` = one-line summary of what the SELECT showed
- `reason_if_rejected` = empty if `status=identifiable`; otherwise the reason

`out/evidence_probe_results.md`

Must include:

1. One sentence: Stage 1–2 frozen; this table is Stage 3 probes only; $0 Claude.
2. The complete 10-row table (same columns).
3. Counts: n identifiable / n rejected_not_identifiable / n confounded /
   n technical_failure.
4. Explicit statement: the confirmatory sample is still these 8 ids, including
   any that were rejected or confounded. Reserves were not promoted.

Also keep raw dumps:

```
results/probe-<task_id>/<task_id>.guest.json
results/probe-<task_id>/schema.txt   # optional but useful
```

Do not invent rows. If a dump failed, `status=technical_failure` and leave
`pre_gold` empty or `NA`.

---

## After all 10 probes finish

1. `git status` / `git diff` / `git log -5`
2. Stage only probe artifacts and this session’s notes. Do **not** commit
   `.env`, API keys, qcow2, or `__pycache__`.
3. Commit on `phase-a-results` with a message like:

   ```
   Record $0 identifiability probes for all 10 eligible tasks.

   Confirmatory sample remains frozen; reserves are not replacements.
   ```

4. `git push -u origin HEAD` (this host; permissions as usual).
5. Print:
   - commit hash (`git rev-parse HEAD`)
   - the complete 10-task result table

---

## STOP

Do **NOT** automatically launch Claude after the probes.
Do **NOT** spend any API credits.
Do **NOT** start Stage 4.

End the session once the commit is pushed and the table is printed.
