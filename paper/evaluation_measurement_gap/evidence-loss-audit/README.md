# evidence-loss-audit

Audit any evaluator that **collects intermediate evidence and then filters
it** before issuing a verdict.

The tool does **not** conclude that evidence was lost. It only:

1. names the inspectable intermediate state,
2. computes a **discard set** (items that entered collection and are
   absent from the filtered keep-set),
3. emits a locked two-stage annotation packet so **humans** can say
   whether a discarded item was determining in isolation and whether
   equivalent evidence remains in the keep-set.

Until those human labels exist, isolation-DECISIVE is not a loss claim,
and IRRECOVERABLE is undefined.

License: **MIT**.

## When this applies

Use it when an evaluator has, or can reconstruct:

- an intermediate evidence state **R** (frames, spans, candidates, …),
- a later filter / top-K / threshold / uniquify step **A(R)**,
- a final verdict that is **not** the same object as R,
- enough grain that “in R but not in A(R)” is a well-defined set.

It does not apply to final-string matchers, VM state checkers, or
verdict-only dumps that never expose R.

## Four links (do not collapse)

| Link | Meaning | Who |
|---|---|---|
| Opportunity | The filter *could* drop an item (e.g. more items than the keep cap) | machine |
| Discard | The item is in no keep-list after A(R) | machine |
| Isolation-DECISIVE | A human, shown task + this item only, calls it determining | human |
| IRRECOVERABLE | Isolation-DECISIVE **and** no keep-set item is EQUIVALENT | human |

Opportunity ≠ discard ≠ isolation-DECISIVE ≠ IRRECOVERABLE.

**REDUNDANT** = isolation-DECISIVE but an equivalent item remains in the
keep-set. Report it. Do not headline it as loss of determining evidence.

## Install

```bash
pip install -e .
PYTHONPATH=src python3 check_core.py
```

No network calls. No evaluator API. Grouping / scoring stays in a
plug-in adapter.

## Core

```python
from evidence_loss_audit import discard_set, classify_links
from evidence_loss_audit.lock import draw_episodes, render_lock_md
from evidence_loss_audit.sheets import build_stage1, build_stage2

# Union keep-lists → discarded indices
discarded = discard_set(n_items=10, grouped={0: [0, 1, 2], 1: [1, 3]})

row = classify_links(
    n_items=10,
    keep_cap=5,
    in_discard=True,
    isolation="DECISIVE",
    equivalence="NOT_EQUIVALENT",
)
# row.irrecoverable is True only after both human labels exist
```

`discard_set` is union-based: an item is discarded iff it appears in
**none** of the per-criterion (or per-key) keep lists.

## Two-stage sheets

- **Stage 1 (blind):** task text + one evidence item. No keep/discard
  tags, no verdict, no other items.
- **Stage 2 (gallery with foils):** task + target + unlabeled gallery.
  Discard-DECISIVE targets get the keep-set as gallery. Keep-DECISIVE
  targets get other keep items (foils) so stage 2 is not “only
  discarded items get a gallery.”

`lock.render_lock_md` writes a SAMPLE_LOCK-style freeze (seed, census /
40+20, sort-before-RNG). Draw **before** seeing rates. Three annotators,
majority vote, Fleiss' κ — lock that in the codebook, not after rates.

## Adapters

Instrument-specific grouping, prompts, and keep-caps are **not** in
core. Drop a module under `src/evidence_loss_audit/adapters/` that
returns `{key: [kept_indices]}`. Core only sees those lists.

Example adapters ship under `src/evidence_loss_audit/adapters/`.
Copy one; do not hard-code a vendor prompt into `discard_set`.

## What this repository is not

- Not a metric.
- Not an automatic “evidence was lost” classifier.
- Not a substitute for human confirmation.
- Not a rewrite of a live recovery job. If you are reconstructing R
  for one instrument, keep that job’s scripts where they are until the
  run finishes; this package is a **copy** of the reusable logic.
