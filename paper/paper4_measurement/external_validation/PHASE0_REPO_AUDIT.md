# P4-M external validation — Phase 0 repo / research-safety audit

**Date:** 2026-09-13
**Branch:** `phase-a-results`
**HEAD at audit:** `c663cf8` `Record P4-D Phase 4 confirmatory FAIL (G3 W1, I_CC=0).`
**This file is an audit, not a corpus, not a metric, not P4-E.**

## Locks observed

- P4-M theory: CLOSED. Design: FROZEN. Question not reinterpreted.
- Frozen instruments inspected read-only; **not modified**.
- No agents run. No WebArena docker / live sites started. $0 spent.
- No new metric. No P4-E. No parser / `score_v2` / wrapper edits.

## Git status (worktree, not this workstream)

The repository has many unrelated dirty/untracked files (`out/stage4_*`, literature audit, paper drafts, HPC import, etc.). Those files are **out of this workstream** and must not be committed with the external-validation stop artifacts.

P4-M theory markdown under `paper/paper4_measurement/P4_M_*.md` was already untracked before this pass. **Not modified. Not committed here.**

## Frozen artifact hashes (verified unchanged)

| File | sha256 |
|---|---|
| `paper/paper4_measurement/instrument/p4_instrument.py` | `c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59` |
| `paper/paper4_measurement/instrument/p4_instrument_v2.py` | `a87ac636a729d99852eb837583b24bce372ff49c196f2be7e39e4f750622fcf3` |
| `paper/paper4_measurement/instrument/p4c2_claim_wrapper.txt` | `2a028f2b95a7bc1ce815ac4b01dcb1fc7c8814ded7a5f3f38489d4ffe70e8e08` |

`git status --short` on those three files: clean. Hashes match the P4-C2 / P4-D lock records.

`score_v2` is the function `score_v2` inside `p4_instrument_v2.py`. It was **not** executed against an external corpus. It was **not** edited.

## Files required for a *passing* transport study (not used)

If eligibility had passed, the authorized stack would have been:

1. `paper/paper4_measurement/P4_EXTERNAL_VALIDATION_DESIGN.md` (frozen protocol)
2. `paper/paper4_measurement/P4_M_CLAIM_JUSTIFICATION_DESIGN.md` (theory lock; read-only)
3. Frozen `p4_instrument_v2.py` / wrapper (read-only; schema adapter only)
4. An independently sourced trajectory dump meeting the eligibility table
5. New files only under this external-validation workstream

No such dump exists in this repository.

## Local trajectory hunt

- Glob `*webarena*` in the workspace: **empty** (no WebArena / WebArena-Verified checkout or dump).
- Local `trajectory_*.csv` / P1–P3 / P4-B/C/C2/D legs: **ineligible** by frozen design (not independently sourced for this study; P4 slates must not be reused as the external corpus).

## Design file

`P4_EXTERNAL_VALIDATION_DESIGN.md` exists and is complete relative to the frozen question. **Not repaired. Not edited.**

## Phase 0 decision

Proceed to Phase 1 eligibility using **public documentation and small public spec files only**. Do not stand up a benchmark. Do not download large Drive/HF trajectory archives unless a candidate already passes the table on documented fields.

**Outcome of later phases:** eligibility failed; Phases 2–5 were not opened.
