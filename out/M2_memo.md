# M2 — the seed data, opened

Everything below is read out of `michael_scott.qcow2` as served by HuggingFace
on 2026-08-25, without booting the guest.

## The counterfactual works on real seed data

`retrieval-f001` asks "What's my current FlyMiles loyalty tier on Dinoco and how
many miles do I have in the bank?" Its three criteria all require reading the
live Dinoco profile, and its rubric text is identical across all four release
channels.

The determining record is one row:

```
table  loyalty  (dinoco-airlines.sqlite)
cols   id, user_email, status, miles, miles_ytd,
       medallion_qualifying_miles, member_since, skymiles_number
```

Applying `cf/interventions.json` through `scripts/cf_patch.py`:

```
probe before: [('Gold Voyager', 38450, 14280)]
probe after:  [('Silver Voyager', 8620, 8620)]
```

The gold moves, the instruction still makes sense, and no rubric wording needs
editing. What is left for an end-to-end run is booting the guest, which needs an
x86 host with KVM.

## The branching counterfactual, now on real data

An earlier run of `hard_app-f033` used a mock database built before the image
finished downloading, so it demonstrated the mechanism and nothing about this
benchmark. Re-run against the extracted `hoolicalendar.sqlite`:

```
probe before: [(1,)]     overlap exists, correct behaviour is reschedule-and-notify
probe after:  [(0,)]     no overlap, correct behaviour is all-clear
tables touched: ['events']
rows differing in events: 1  (id=705 'Scranton Improv 201' 19:54 -> 21:54)
```

The determining set is precise. On the Thursday after the bake date the improv
block is 19:54-21:54, and the only overlapping meeting carrying both
`andy.bernard@` and `jim.halpert@` is event 755, "Client Dinner - Dunmore High
School" 18:45-20:15, overlapping by 21 minutes. Two other events overlap the
improv block but have no attendees, which criterion 5 explicitly permits leaving
in place. Moving one event by two hours flips the entire correct behaviour of a
ten-criterion task.

Two details that would have silently confounded the run:

- `datetime()` returns space-separated timestamps while every stored value uses
  the ISO `T` form. The patch restores the separator, otherwise one row in the
  table has a format the app has never had to parse.
- The Thursday is computed from the guest clock rather than hardcoded, because
  the image rebases dates at boot.

`cf_patch.py` now hashes every table before and after and records which ones
moved, so each run carries its own evidence that the intervention was minimal.

A side observation while resolving attendees: `event_attendees` holds **2 rows
in total** across 121 calendar events, both on event 755. Criterion 8 of this
task offers an escape hatch — "if the moved meeting has no attendees listed,
notes that no invites were needed" — which almost every event in the calendar
would qualify for.

## Two labelling systems in one file disagree on 39 tasks

Joining the run records to the task file by `id` surfaced that
`hard_app-f033` carries `category: situated_action`. It is not an isolated slip.
Each task has both an id namespace and a `category` field, and they disagree for
**39/184** tasks:

| id namespace | tasks named that way | filed under that category | filed elsewhere |
| --- | --- | --- | --- |
| `hard_app-*` | 22 | 1 | 14 situated_action, 7 long_horizon |
| `cua_only-*` | 20 | 2 | 9 long_horizon, 9 situated_action |

Both names exist as category values, so this is not a renaming that finished
cleanly — the same label means one thing as an id prefix and another as a
category. Any per-category result therefore depends on which field the reporter
grouped by, and the two groupings differ for a fifth of the suite.

The `cua_only` case matters most for this study's argument. The name reads as
computer-use-only, which is the closest thing the artifact has to an explicit
non-personal marker, yet 18 of those 20 tasks are filed under
`situated_action` or `long_horizon`. Whatever the intent was, the suite's own
annotations do not agree with each other about which tasks are personal — before
anyone asks whether success is attributable to personal information.

## Reading the image required decoding it

The image stores 177,156 clusters and nearly all of them are zlib-deflated. The
libqcow reader returns zeros for compressed clusters instead of failing, so the
root filesystem appears empty and a raw scan finds no SQLite headers at all —
which reads exactly like a corrupt download. `scripts/qcow2.py` resolves the
L1/L2 tables and inflates clusters, and the ext4 layer sits on top of it. Anyone
auditing this image will hit the same wall.

## The published checksum does not match the file served

| | |
| --- | --- |
| downloaded file, sha256 | `59c9614ce0a4b79473e4c4ec6876ec5fd1f00ca2b4bac785b77c4b24506aa972` |
| HuggingFace `x-linked-etag` for that object | identical |
| repo `SHA256SUMS` and `VERSION.json` claim | `6e2c6954b3f22daebef832b8b7d5bc0ea76fe540da57192fb8b0923cef5e4770` |

The download was verified byte-for-byte against the server at six offsets
including the resume boundary, and the size matches exactly. The
`all_tasks_with_grading.json` digest published in the same `SHA256SUMS` matches
its file precisely, so the checksum file is not broken in general — only the
image entry disagrees with the artifact being served.

The metadata inside the image disagrees with the metadata beside it:

| | inside image (`/data/_seed_meta.json`) | beside image (`VERSION.json`) |
| --- | --- | --- |
| build | `build-source-v1.2.47`, sha `02f97539a10b` | `v1.2.48-8678e36` |
| bake reference time | 2026-08-21T05:00:12Z | 2026-08-14T00:00:00Z |

## Three copies of every database, and only one is live

50 SQLite files in three trees:

- `/data/*.sqlite` — the paths `env.py` health-checks and patches; 16 Dinoco flights
- `/data/vms/michael_scott/*.sqlite` — 12 Dinoco flights
- `/data/worlds/scranton-office/*.sqlite` — used by `run_parallel_tasks.py`; no `loyalty` table at all

Two apps are symlinks onto other apps' databases:
`hoolichat.sqlite -> /data/buzzchat.sqlite` and
`hooliwork.sqlite -> /data/workbuzz.sqlite`. HooliChat and BuzzChat, HooliWork
and WorkBuzz are the same store, so a task naming them as two apps is touching
one database.

## The seed state is in the WAL, not in the database file

Every app database ships with a populated `-wal` (Dinoco's is 4.1 MB). Reading
the `.sqlite` file alone gives a different persona:

| | main file only | with WAL applied |
| --- | --- | --- |
| loyalty status | Silver Voyager | Gold Voyager |
| miles | 8,620 | 38,450 |
| Dinoco flights | 7 | 16 |
| Jamaica outbound 2026-09-05 | absent | present as DN1562 |

The WAL state is the correct one: `_seed_meta.json` anchors
`jamaica_outbound: 2026-09-05`, and roughly eight tasks refer to "my upcoming
Jamaica flight", which exists only once the WAL is applied. So any audit that
copies the `.sqlite` files out of the image and diffs them is comparing against
a persona the agent never sees. This is a real trap and it is not documented
anywhere.

## The harness backfill updates nothing

`env.py` writes three fares at warm-up "referenced by task grading":

```
UPDATE flights SET fare_paid=512 WHERE flight_number='AA1482' AND fare_paid=0;
UPDATE flights SET fare_paid=387 WHERE flight_number='DL1358' AND fare_paid=0;
UPDATE flights SET fare_paid=289 WHERE flight_number='AS324'  AND fare_paid=0;
```

No flight in any of the three database trees carries those numbers; every flight
is `DN####`. The statements match zero rows. The values themselves do appear in
the data (DN1562 = 512, DN6769 = 387, DN0324 = 289), so the backfill was written
against an earlier seed that used airline-style codes and was never updated. The
harness and the image have drifted apart.

This does not weaken the method — it strengthens the precedent. The authors
inject SQL into the seed at warm-up as normal practice; this study does the same
thing, correctly targeted.

## The generator ships inside the image, with 27 personas

`/opt/generator/` holds the full data-generation pipeline that the GitHub repo
does not ship: `seed_webapps.py` (1.2 MB), `seed_email.py` (298 KB),
`seed_browser.py` (137 KB), `seed_calendar.py` (71 KB), `enrich_personas.py`,
`city_stores.py`, `restaurant_data.json`, and `generate.py` as the entry point.

`/opt/personas/` holds 27 persona specifications — Michael Scott, Dwight
Schrute, Pam Beesly, Jim Halpert, Angela Martin, Creed Bratton and the rest —
plus `registry.json`, `app-seed-map.json` and a JSON schema directory. The
image's `michael_scott.json` is 87 KB against the repo's copy and adds one key,
`record_counts`.

`/opt/mypcbench-firstboot.sh` explains why: the generator runs **in the guest**
at first boot.

```
PERSONA="${PERSONA:-${MYPCBENCH_PERSONA:-michael_scott}}"
...
elif [ "$(cat /data/.seeded_fingerprint)" != "${PERSONA}:${WORLD}:${VM_ID}:::" ]; then
  need_seed=true
...
  rm -f /data/*.sqlite /data/*.sqlite-wal ...
  python3 /opt/generator/generate.py --persona "$PERSONA" --world "$WORLD" --vm-id "$VM_ID"
```

Its own comment: "This lets the SAME baseline qcow2 become any of the 16
personas with just `docker run -e PERSONA=dwight_schrute ...`". Seeding takes
two to five minutes.

Three consequences. First, "regenerate from the spec" is possible after all —
not from the public repo, but from the image, which has both the specs and the
generator. Second, the single-persona property of the published results is a
choice about what was run, not a limit of the artifact: varying the persona
facet is an environment variable. Third, any intervention must land after
firstboot seeding, and must not disturb `/data/.seeded_fingerprint`, or the next
boot wipes `/data/*.sqlite*` and regenerates everything.

`app-seed-map.json` is close to a determining-records map written by the
authors: per app, the generator function plus the persona sections it requires,
e.g. `vaultbank <- generator/seed_webapps.py::seed_vaultbank` requiring
`identity`, `financial`, `contacts`. What it does not contain is any per-store
grocery breakdown, so the favourite-store gold in `preference_inference-f009` is
a product of the generator's own sampling rather than of anything stated in the
persona.

## The image reports different record counts than the paper

`record_counts` in the image's persona spec is not a bake snapshot; its own note
says it is "Refreshed in-image by emit_persona_stats.py at runtime from the live
SQLite DBs". Computed 2026-08-21:

| | paper as reported to us | live in image |
| --- | --- | --- |
| bank transactions | 1,812 | 1,634 |
| emails | 2,398 | 2,326 |
| calendar events | 679 | **121** |
| messages | 2,526 | **1,520** |
| web visits | 10,746 | 10,600 |

Three of five are within about ten percent; calendar events and messages are
not. The paper-side figures here come from a reading of the paper rather than
from our own extraction, so this needs confirming against the PDF before it is
used, but the in-image side is the authors' own runtime measurement.

## Where this leaves the intervention

Verified and ready: `retrieval-f001`, patching `loyalty` in
`/data/dinoco-airlines.sqlite`, with `situated_action-f028` as the control.

Still to pin down: whether the app process reads `/data/` or
`/data/vms/<vm_id>/`, since the two disagree on flight counts even after the WAL
is applied. `env.py` health-checks and patches `/data/`, and `/data/` holds the
state consistent with the text fixtures, so `/data/` is the working assumption
until the guest is booted.
