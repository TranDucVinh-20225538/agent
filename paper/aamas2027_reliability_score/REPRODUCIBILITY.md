# Reproducibility (anonymous)

Pinned tree that reproduces Table 2 (layer repairs) and the R-AGG census
`+8` correct / `+18` wrong:

- repo commit: `7b1f5073a06948d3b2fb3556f664668c7f011160` (`7b1f507`)
- frozen extractor: `3242c30`

`origin/phase-a-results` at `a330e15e8659bfe5e4ff6a9e16f56efbbc0e4014` is **not**
this pin. Do not substitute it.

Gates, in order, on a host where `/data2/hpcshared` resolves:

```bash
python3 scripts/p3_1_repair.py parity
python3 scripts/p3_1_repair.py synthetic
```

Signed-movement robustness (leave-one-task-out, 13 contributing tasks):

```bash
python3 scripts/p3_1_task_jackknife.py
```

Inputs (unchanged): `out/p3_0_recall_audit.jsonl`, `out/study2_hatd_legs.jsonl`,
`out/p3_0_extracted.jsonl`. Record: `out/p3_1_task_jackknife.json`.

Do not treat a branch name as a pin. Do not put a username URL in the
anonymous PDF.
