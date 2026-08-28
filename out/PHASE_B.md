# Phase B — frozen task expansion

**Status: FROZEN. B.1 guest validation 10/10 (2026-08-28). Do not rewrite I.**

Frozen statement:

> Eligibility → intervention → expected determining set → scoring
> interpretation are frozen before any Phase-B trajectory is observed.

Ledger: `cf/phase_b_freeze.json` (sha256 of the spec files + git HEAD).

Pipeline:

```
specified_not_frozen
        ↓
       FREEZE          ← you are here for the specs
        ↓
implementation         ← file_patches + f004_hd_rank_flip (this commit/session)
        ↓
validation of I        ← 10/10 (out/phase_b_validate.md). f030 gold_moved=False is Type B.
        ↓
RUN                    ← B.2 Claude / GPT / Qwen 35B-A3B on the six unrun tasks; reuse Stage 4 for the four already-run IDs
        ↓
NO CHANGES TO I
```

If a task fails because of QEMU or tooling, that cell is a failed
execution. Do not edit the intervention and re-run to rescue the task.

Stage 4 stays closed as a historical census. Phase B does **not** change
VM, instruction, UI, rubric, harness, or validity (`DONE` from last
`traj.jsonl` action). Failure rate is a result. Do not require 30/30 DONE.

## Universe

All 10 A–E eligible tasks (`out/evidence_eligible.json`, seed 20260826).
Not a Type A cherry-pick. Not 15.

> Tasks were selected from the complete A–E eligible universe, and
> interventions were specified before observing agent outcomes.

## Models

- **B.1** freeze + implement inject + validate 10 interventions in guest
- **B.2** Claude / GPT / Qwen3.5-35B-A3B on the same 10 (30 paired episodes)
- **B.3** 9B / Flash ablation only after B.2 validity is in hand

## Type B (pre-specified)

1. `preference_inference-f018` — joint $D$; Stage 4 lock; not a 2×2
2. `retrieval-f030` — $I$ moves sqlite-only charitable; 1099+file held
3. `aggregation-f018` — $I$ moves sqlite-only charitable + home-office; W-2/1099+files held

## Contrast (score-sensitive if tracking)

- `preference_inference-f004` — rubric pins Cooper's as HD top; $D=1,\Delta S\neq 0$ expected
- `counterfactual-f004` — CF removes the contradiction the rubric rewards flagging

Type A cells sit next to those: $D=1,\Delta S=0$ is then a finding, not a default.

## Inject implementation (B.1)

- `scripts/cf_inject.py` loads `cf/phase_b_interventions.json` first, then
  `cf/interventions.json`, then `cf/stage4_locked.json`
- Dual-channel: `file_patches` are written into the guest (not sqlite-only)
- `preference_inference-f004`: `scripts/f004_dynamic.py` computes $k$ from
  live HangryDash counts. Aborts if the live HD winner is not Cooper's.
  Does not touch TableFind. Does not accept a hand-written ranking.

Guest validation of every $I$ is still required before B.2. Offline unit
checks (`python3 scripts/f004_dynamic.py`, `python3 scripts/cf_file_patch.py`,
`python3 scripts/test_phase_b_inject.py`) are not a substitute.

## Files

- `cf/phase_b_registry.json` — canonical, frozen
- `cf/phase_b_registry.csv`
- `cf/phase_b_interventions.json` — the six new $I$
- `cf/phase_b_freeze.json` — hashes
- `cf/stage4_locked.json` — the four observed $I$ (do not edit)
