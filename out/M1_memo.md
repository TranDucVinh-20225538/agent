# Milestone 1 — where the seed lives, and can it be changed

Source: `external/MyPCBench-main` (GitHub release, tarball of `main`).

## The seed is not in the repo

- `personas/michael_scott.json` (83 KB) is read at runtime by
  `agent-harness/utils/persona_registry.py` for exactly three things: the
  auto-login email, and the `{PERSONA_NAME}` / `{PERSONA_CITY}` prompt
  variables. It does not seed any application.
- `tasks/final/variables.json` is read by **no code in the repo**. It is a
  reference sheet for task authors, not generator input. Editing it changes
  nothing.
- No generator ships with the release. The data is baked into the VM image
  (`ljang/mypcbench-qemu`, ~5 GB compressed / ~10 GB expanded qcow2, obtainable
  via `scripts/get-eval-image.sh` through skopeo or the HuggingFace mirror).
  The image is rebuilt daily and an in-VM `mypcbench-date-rebase` service
  shifts seeded dates so the history always reads as current.

So "edit variables.json and regenerate" is not a path. The counterfactual has
to be applied to live state inside the VM.

## The seed is per-app SQLite, and the harness already documents it

`agent-harness/env.py` (~line 865) enumerates all 17 applications as
`(db_name, app, port, init_path)` and then asserts a row exists in each:

| app | db | table asserted | key |
| --- | --- | --- | --- |
| hangrydash | `hangrydash.sqlite` | `orders` | `user_email` |
| kwik-e-mart | `kwik-e-mart.sqlite` | `orders` | `user_email` |
| dinoco-airlines | `dinoco-airlines.sqlite` | `flights` | `user_email` |
| hoolicalendar | `hoolicalendar.sqlite` | `events` | `user_email` |
| tablefind | `tablefind.sqlite` | `reservations` | `user_email` |
| vaultbank | `vaultbank.sqlite` | `accounts` | `user_email` |
| batbucks | `batbucks.sqlite` | `holdings` | `user_email` |
| etaxi | `etaxi.sqlite` | `rides` | `user_email` |
| cheskepdia | `cheskepdia.sqlite` | `bookings` | `user_email` |
| speedtax | `speedtax.sqlite` | `tax_returns` | `user_email` |
| mail | `mail.sqlite` | `emails` | — |
| hoolishop, oddsmarket, buzzchat, workbuzz, sprintboard, lockedin | ... | `orders`, `positions`, `contacts`, `channels`, `projects`, `posts` | mixed |

Databases live at `/data/<db>.sqlite` in the guest. Each app is warmed by a
`GET` on its `init_path` **before the agent starts**, from the harness `reset`
path. That warmup is the natural injection point: apply the counterfactual SQL
after warmup and before the agent's first observation.

This means an intervention is a targeted `UPDATE` on one table, not a rewrite
of the persona. It matches the design constraint we already had: change only
the records that generate the gold for that item, leave authentication, the
GUI and every unrelated app untouched.

## Which file grades, and where the argmax wording came from

Four task files carry grading. Comparing rubric lists across all 184 ids:

| pair | identical rubrics | criteria totals |
| --- | --- | --- |
| HuggingFace split vs `mypcbench_legacy.json` | 146/184 | 1,191 vs 1,192 |
| HuggingFace split vs `all_tasks_with_grading.json` | 42/184 | 1,191 vs 1,129 |
| `mypcbench_clean.json` vs `all_tasks_with_grading.json` | 184/184 | 1,129 vs 1,129 |
| `mypcbench_legacy.json` vs `all_tasks_with_grading.json` | 54/184 | 1,192 vs 1,129 |

A fourth channel exists: the image repo ships its own `all_tasks_with_grading.json`
next to the qcow2, carrying **1,132** criteria and matching the GitHub canonical
on 130/184 rubric lists. Instructions are byte-identical across all four
channels; only the grading criteria move.

| channel | criteria | mean per task |
| --- | --- | --- |
| HuggingFace `tasks.jsonl` split | 1,191 | 6.47 |
| `mypcbench_legacy.json` | 1,192 | 6.48 |
| GitHub `all_tasks_with_grading.json` = `mypcbench_clean.json` | 1,129 | 6.14 |
| shipped beside the image (v1.2.48) | 1,132 | 6.15 |

Only **42/184 tasks have rubric text identical across all four channels**, so
which release a study downloads changes the instrument for the other 142. That
makes channel invariance a selection criterion, not a footnote: `retrieval-f001`
and the control `situated_action-f028` are invariant, while `hard_app-f033`
keeps its ten criteria but rewords them per channel.

The image's `VERSION.json` (v1.2.48, built 2026-08-14) also states in its own
words that "the daily job had been re-tagging one digest" since 2026-07-19, and
that "all 184 instructions restored to their pre-audit originals, rubrics and
required_subtasks realigned to them; 184 tasks / 1132 rubric items". So the
"rebuilt daily" property documented in `NO_DOCKER.md` did not hold for about a
month, and the grading has been revised at least twice since release.

The HuggingFace split tracks the legacy grading, not the file the harness
grades with. The paper reports 1,191 criteria at mean 6.5 per task, which
matches the legacy/HuggingFace side; the canonical file the runner uses has
1,129 at mean 6.14. So the split most people will load via `load_dataset`
reproduces the pre-revision instrument.

That resolves the disagreement about `preference_inference-f009`. The
single-valued wording ("plurality of orders", `/api/orders`) exists in the
HuggingFace split and in `mypcbench_legacy.json`; the string "Wegmans" appears
inside a rubric only in the legacy file. The canonical graded rubric has no
"plurality", no `/api/orders`, and accepts either order count or total spend.
So the task is not a clean existence proof and must not be the first
counterfactual.

It is, however, a free result. In the canonical file the same task still
carries a design note:

> `required_subtasks`: "Identify the top store by Michael's Kwik-E-Mart order
> count (plurality, not necessarily majority) from /api/orders"

The design intent is single-valued while the criterion that actually grades
admits two bases that can name different stores. The stated intent and the
graded criterion disagree inside one released task, which is the
annotation-is-not-attribution point visible without running anything.

## Two release channels disagree

The HuggingFace split (`data/tasks.jsonl`) and the GitHub canonical file
(`tasks/final/all_tasks_with_grading.json`) have the same 184 ids and byte
identical instructions for all 184 tasks, but:

- rubric lists differ on **142 of 184 tasks**
- **61 tasks** have a different number of criteria
- totals: 1,191 criteria (mean 6.5/task) on HuggingFace versus 1,129 (mean 6.1)
  in the repo

The paper reports "1,191 in total, mean 6.5 per task", which matches the
HuggingFace split, not the file the harness grades with. The grading instrument
was revised after the reported run without the headline numbers changing.

The revision direction matters for us. For `preference_inference-f009` the
HuggingFace rubric names the rule ("top-by-order-count store from live order
history (/api/orders), naming whichever store has the plurality of orders")
while the repo rubric deliberately loosens it ("under a basis it states or
makes evident — order count or total spend are both defensible readings of
'favorite'"). The looser wording admits two different gold values.

Consequences: pin the revision in every reported number, and treat a
multi-basis rubric as a task with redundant determining sets — a counterfactual
must move every basis the rubric accepts, or the gold stays ambiguous.

Aggregate classification is stable across the two channels, so the Milestone 0
reading does not depend on the choice: attributable weight 35.5% (HuggingFace)
versus 33.7% (GitHub).

## First counterfactual set

Five tasks, each with the table an intervention would touch.

| task | gold | determining table | intervention | role |
| --- | --- | --- | --- | --- |
| `retrieval-f001` | FlyMiles tier + miles balance | `dinoco-airlines.sqlite` profile/loyalty | change tier and balance | point gold |
| `preference_inference-f009` | favourite grocery store | `kwik-e-mart.sqlite` `orders` | move both order count and total spend to a different store | latent gold, redundant bases |
| `situated_action-f009` | most-ordered Chili's item | `hangrydash.sqlite` `orders` | change the modal item, keep the tiebreak rule satisfiable | latent gold consumed by an action |
| `hard_app-f033` | whether a Thursday conflict exists | `hoolicalendar.sqlite` `events` | toggle the overlap on and off | branching gold, cleanest signal |
| `situated_action-f028` | book a well-rated Scranton weekend | none | apply the same interventions | control: must not move |

Order revised after the file-provenance check: `retrieval-f001` is first (three
criteria, all reading the live Dinoco profile, rubric text survives the patch),
`hard_app-f033` second (every criterion is branch-conditional, so flipping the
overlap flips the whole correct behaviour from reschedule to all-clear),
`situated_action-f028` runs as the control under both, and
`preference_inference-f009` is demoted from existence proof to the documented
non-unique-oracle case.

Open item before any run: confirm the actual column names per table by opening
the qcow2, since `env.py` only asserts table and key existence.

## Tooling state

`cf/interventions.json` holds one entry per task: the probe SQL that returns the
gold the rubric depends on, the patch, and what must move. `scripts/cf_patch.py`
runs the probe, backs up the database, applies the patch, re-probes, and writes a
before/after record to `out/cf_runs/`. Both interventions are exercised end to
end against mock databases built by `scripts/make_mock_dbs.py`:

- `retrieval-f001`: `('Dinoco Bronze', 3604)` becomes `('Dinoco Gold', 48210)`
- `hard_app-f033`: Thursday overlap count 1 becomes 0

Column names are placeholders until the image is opened, so a failure against
the real database localises to schema, not to the tooling.

## The harness already performs the intervention

`agent-harness/env.py` lines 1009-1023 run, after the container boots and
before the agent starts:

```
sqlite3 /data/dinoco-airlines.sqlite
  "UPDATE flights SET fare_paid=512 WHERE flight_number='AA1482' AND fare_paid=0;
   UPDATE flights SET fare_paid=387 WHERE flight_number='DL1358' AND fare_paid=0;
   UPDATE flights SET fare_paid=289 WHERE flight_number='AS324'  AND fare_paid=0;"
```

Its own comment: "Backfill seed-data fields left at their default in the shipped
image but referenced by task grading."

Two things follow. First, the mechanism and the injection point this study needs
are the ones the benchmark authors already use, so "you modified the environment
in a way the benchmark does not support" is not available as an objection.
Second, the shipped image does not by itself determine the gold: three fare
values that grading depends on exist only because the harness writes them in at
warm-up. Gold is a property of image plus harness version, not of the image.

No other write of this kind exists in the harness; `dinoco-airlines.sqlite` is
the only database patched.

## Instructions that hardcode their own gold

`contradiction-f003` opens with "My Dinoco profile says I have **Gold Voyager**
and a decent chunk of miles, but honestly I haven't flown THAT much." The
seeded value is quoted in the instruction, so changing the tier in the database
makes the instruction contradict the environment and the task is no longer
well-formed. Tasks like this are counterfactual-ineligible unless the
instruction is edited too, which changes the item.

Since containers are destroyed and recreated per task (`reset`, soft=False),
this does not contaminate `retrieval-f001`, which asks for the tier without
naming it. But it is a countable eligibility property: once the real seed values
are in hand, matching them against all 184 instructions gives the number of
tasks whose instruction pins its own gold. That number does not currently exist
anywhere.

## Image inventory, real byte sizes

Read from HuggingFace `x-linked-size`, not from the page prose (the "~30 GB" in
the README is the virtual disk size inside the qcow2, not the download):

| file | bytes | note |
| --- | --- | --- |
| `michael_scott.qcow2` | 5,132,255,232 (5.13 GB) | v0.1 current, being downloaded |
| `michael_scott_round78e.qcow2` | 12,409,569,280 (12.41 GB) | archived v0.0, labelled for paper reproduction |
| `mypcbench-michael_scott.qcow2` | 5,433,262,080 | |
| `base.qcow2` | 4,334,026,752 | |
| `mypcbench-desktop.tar.zst` | 3,116,999,767 | |

Schema reading uses the 5.13 GB current image. Any run meant to be compared
against the published numbers has to use `_round78e`; note that the repo ships
only one grading file, the current one, so the archived image does not come with
the grading that produced the paper's numbers.

## Reading the databases without booting

The guest is x86 and this host is arm64, so booting means full emulation. It is
not needed to read schema: `scripts/extract_dbs.py` opens the qcow2, walks the
GPT and the ext4 filesystem through the libyal readers vendored in `vendor/`,
copies `/data/*.sqlite` out and dumps every table and column to
`out/db_schema.json`. Read-only, no root, no daemon.

Running the agent and the judge is still blocked on hardware: that needs an x86
Linux host with KVM. Reading schema locally only unblocks writing the real SQL.
