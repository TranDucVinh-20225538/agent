Open PHASE_3_FLASH_PILOT on this HPC checkout.

You have the OpenRouter SMALL key. Run exactly the preregistered Flash
observability pilot. Do not audit P4-B. Do not edit the sealed corpus,
gold, instrument, transforms, or N_B. Do not amend git history.

Pull **branch `p4b-phase3-hpc`** (not a merge of `origin/phase-a-results`):

```bash
git fetch origin
git checkout p4b-phase3-hpc
git pull origin p4b-phase3-hpc
python3 paper/paper4_measurement/instrument/p4b_flash_pilot.py --check
bash scripts/p4b_phase3_flash_pilot.sh
```

Follow `paper/paper4_measurement/P4B_PHASE3_HPC.md`.

Requirements:

* Frozen instrument `c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59` and sealed P4-B worlds/gold.
* Flash only: `qwen/qwen3.8-flash` via OpenRouter SMALL (`OPENROUTER_API_KEY_SMALL`).
* IDs: B01, B02, B03 in order. `max_steps = 40`. Hard cap $30.
* Runner is `p4b_flash_pilot.py` (list_dir/read_file on the sealed snapshot). Do **not** boot QEMU/TCG for this pilot.
* Hide `world_meta.json` (the runner already does). Do not feed gold or L to the model.
* Record natural last-text τ and frozen P4 `{status, cause, committed}`.
* Pilot is **not** confirmatory E1–E4 and **not** N_B.
* Do not open GPT or Claude. Do not proceed to Phase 4.

Gate: PASS iff ≥ 2 of 3 legs yield a last-text the frozen instrument scores without harness exception (HIT/MISS/ABSTAIN all count).

If FAIL or BLOCKED: record USD + three results and **stop**. Do not repair tasks or the instrument.

If PASS: freeze the pilot record, report actual USD, all three `{status, cause}`, `n_scorable`, and that PHASE_4_MAIN is still BLOCKED.

Hard stop after B01–B03. Do not spend beyond $30.
