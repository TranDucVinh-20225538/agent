# P4-B Phase 3 — HPC Flash pilot

Do **not** audit P4-B again. Do **not** edit the sealed corpus, gold,
instrument, transforms, or `N_B`. Do **not** amend git history to fake a
Phase-0 chronology.

Laptop/local Cursor **cannot** spend. This file is the licensed Phase-3
run on HPC (SMALL OpenRouter key).

Standing documentation (do not “fix” these by rewriting commits):

> Task construction was outcome-blind but not investigator-blind: the
> authors knew the frozen measurement instrument and the failure of the
> preceding MyPCBench validation attempt, but no agent outcomes from
> P4-B were available during corpus construction.

> The repository does not provide cryptographic evidence that the corpus
> size was committed before the first task artifact was created.

Audit freeze: commit `df2a067a0a874a5868935b96e2872288cb84cf1a`
(`GO WITH DOCUMENTATION`).

## What this is

Observability only. **Not** confirmatory `N_B`. **Not** E1–E4.

- IDs: `B01`, `B02`, `B03` in that order
- Model: `qwen/qwen3.8-flash` (SMALL OpenRouter lane)
- `max_steps = 40`
- Hard cap: **$30**
- Gate: ≥ 2 of 3 legs produce a last-text `τ` that the frozen instrument
  scores without harness exception (HIT/MISS/ABSTAIN all count)
- Do **not** open GPT, Claude, or Phase 4
- Do **not** edit `p4_instrument.py`, gold, anchors, worlds, or `N_B`
- If the gate FAIL: **stop**. Do not retune tasks to “save” the pilot.

This licensed runner is `p4b_flash_pilot.py`: OpenRouter tool-use
(`list_dir` / `read_file`) over the sealed world snapshot. It hides
`world_meta.json`. It does **not** boot QEMU/TCG. Do not substitute an
OSWorld/QEMU harness for this pilot.

## Pull (use this branch — not a merge of `phase-a-results`)

`phase-a-results` on origin has Paper-2 commits this worktree does not
share. HPC must **not** rebase or merge those 16 commits as part of this
run.

```bash
git fetch origin
git checkout p4b-phase3-hpc
git pull origin p4b-phase3-hpc
git log -1 --oneline
test -f paper/paper4_measurement/construction/sealed/P4B_PHASE2_SEAL.json
test -f paper/paper4_measurement/P4_B_ANTI_CIRCULARITY_AUDIT.md
python3 paper/paper4_measurement/instrument/p4b_flash_pilot.py --check
```

`--check` must print `"preflight": "OK"` and instrument hash
`c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59`.

Confirm `P4B_PHASE2_SEAL.json` still has `gate=PASS`, `agent_run=false`.

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

Overwrite any laptop `BLOCKED` stub with the HPC result.

## After the run

Report: gate PASS/FAIL/BLOCKED, actual USD, three `{status, cause}`,
`n_scorable`. **Stop.** Do not start Phase 4.

| Gate | Meaning | Next |
|---|---|---|
| PASS (`n_scorable ≥ 2`) | Natural last-text is obtainable | Phase 4 remains BLOCKED until separately licensed (20 Flash + 20 GPT) |
| FAIL (`n_scorable < 2`) | Observability fail | Stop. Do not edit tasks/instrument |
| BLOCKED (no key / spend cap before 2 scorable) | Could not run | Stop. $0 or ≤ $30. Not a lowered `N_B` |

Hard stop after B01–B03. Do not spend beyond $30.
