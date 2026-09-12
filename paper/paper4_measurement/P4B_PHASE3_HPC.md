# P4-B Phase 3 — HPC Flash pilot

Laptop/local Cursor **cannot** spend: no OpenRouter SMALL key in that
process. Phase 2 remains **PASS**. This file is the licensed Phase-3 run
on HPC.

## What this is

Observability only. Not confirmatory `N_B`. Not E1–E4.

- IDs: `B01`, `B02`, `B03` in that order
- Model: `qwen/qwen3.8-flash` (SMALL OpenRouter lane)
- `max_steps = 40`
- Hard cap: **$30**
- Gate: ≥ 2 of 3 legs produce a last-text `τ` that the frozen instrument
  scores without harness exception (HIT/MISS/ABSTAIN all count)
- Do **not** open GPT, Claude, or Phase 4
- Do **not** edit `p4_instrument.py`, gold, anchors, worlds, or `N_B`

## Pull

```bash
git fetch origin
git checkout phase-a-results
git pull origin phase-a-results
```

Expected HEAD after this push is recorded in the commit that adds this
file. Confirm:

```bash
git log -1 --oneline
test -f paper/paper4_measurement/construction/sealed/P4B_PHASE2_SEAL.json
python3 paper/paper4_measurement/instrument/p4b_flash_pilot.py --check
```

`--check` must print `"preflight": "OK"` and instrument hash
`c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59`.

## Key (do not print it)

SMALL lane only:

```bash
export OPENROUTER_API_KEY="$OPENROUTER_API_KEY_SMALL"
unset ANTHROPIC_API_KEY OPENAI_API_KEY OPENROUTER_API_KEY_LARGE
```

Reject `sk-proj-*` (GPT). No silent failover to LARGE.

## Run

From repo root:

```bash
bash scripts/p4b_phase3_flash_pilot.sh
```

Writes (do not hand-edit gold/worlds):

- `paper/paper4_measurement/construction/out/p4b_phase3_pilot.md`
- `paper/paper4_measurement/construction/out/p4b_phase3_pilot.json`
- `paper/paper4_measurement/construction/out/p4b_phase3_status.json`
- `paper/paper4_measurement/construction/out/p4b_phase3_pilot/B0{1,2,3}_tau.txt`

## After the run

Report: gate PASS/FAIL/BLOCKED, actual USD, three `{status, cause}`,
`n_scorable`. Stop. Do not start Phase 4.

If `< 2` scorable last-texts: **FAIL**, stop at whatever was spent ≤ $30.
If the key is missing: **BLOCKED**, $0.
