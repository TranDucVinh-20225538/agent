# Auditing what MyPCBench success is attributable to

MyPCBench reports a single perfect-task rate over a seeded digital life and reads
it as evidence that an agent is a capable personal assistant. A task labelled
memory or preference tells us what the authors intended the task to exercise; it
does not tell us that success came from the personal information named. This
repository intervenes directly on the records that generate a task's correct
answer, leaving authentication, the desktop and every unrelated app untouched,
and asks whether the agent's answer moves with them.

## State

Two interventions are written and verified against the seed data extracted from
the shipped image. In each case the gold moves, exactly one row changes, and no
other table is touched.

| task | database | intervention | gold before | gold after |
| --- | --- | --- | --- | --- |
| `retrieval-f001` | `dinoco-airlines.sqlite` | one row of `loyalty` | Gold Voyager, 38,450 miles | Silver Voyager, 8,620 miles |
| `hard_app-f033` | `hoolicalendar.sqlite` | move the Thursday improv block two hours | overlap exists, so reschedule and notify | no overlap, so report all-clear |

What remains is running an agent and the judge under both conditions, which needs
an x86 Linux host with `/dev/kvm`. See [REPRO.md](REPRO.md).

## Layout

```
cf/interventions.json     one entry per task: the probe that returns the gold,
                          the patch, and what must move
scripts/cf_patch.py       apply an intervention to an extracted database
scripts/cf_inject.py      apply one inside a running guest, via the Control API
scripts/qcow2.py          read-only qcow2 decoder that handles compressed clusters
scripts/extract_dbs.py    pull /data/*.sqlite out of the image and dump schema
scripts/image_ls.py       list and read files inside the image
scripts/m0_scan.py        classify all 1,000+ rubric criteria by evidence type
out/M0_memo.md            what the rubrics actually grade
out/M1_memo.md            where the seed lives, and the four grading channels
out/M2_memo.md            the seed data opened, and the first counterfactuals
```

`scripts/setup.sh` rebuilds the parts that are deliberately not committed: the
upstream harness, the task files, and the readers. The disk image and the
databases extracted from it are not redistributed here.

## Findings that came out of reading the artifact

These are byproducts of getting the intervention to work, not the argument, but
each is checkable and none is documented upstream.

- The seed state lives in the SQLite **WAL**, not the database file. Reading
  `/data/*.sqlite` alone reports Silver Voyager and 7 flights where the live
  environment has Gold Voyager and 16.
- Four different grading files circulate — 1,191 criteria on HuggingFace, 1,192
  in `mypcbench_legacy.json`, 1,129 in the repo canonical, 1,132 shipped beside
  the image. Instructions are identical across all four; only **42/184** tasks
  have rubric text that agrees everywhere.
- The published `SHA256SUMS` and `VERSION.json` digest for the image does not
  match the file served, while the grading file's digest in the same checksum
  file matches exactly.
- The harness's own seed backfill targets flight numbers absent from every
  database in the image, so it updates zero rows.
- Each task carries two labels that disagree for **39/184** tasks: 22 tasks are
  named `hard_app-*` but only one has that category, and 20 are named
  `cua_only-*` but only two do.
- The generator and 27 persona specifications ship inside the image, and
  firstboot can instantiate any of them from one environment variable, so the
  single-persona result is a choice about what was run rather than a limit of the
  artifact.
