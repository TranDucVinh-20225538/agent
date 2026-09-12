Open PHASE_3_FLASH_PILOT on this HPC checkout.

Run exactly the preregistered Flash observability pilot.

Pull `phase-a-results`, then:

```bash
python3 paper/paper4_measurement/instrument/p4b_flash_pilot.py --check
bash scripts/p4b_phase3_flash_pilot.sh
```

Follow `paper/paper4_measurement/P4B_PHASE3_HPC.md`.

Requirements:

* Use the frozen P4 instrument (`c43a920a…7d59`) and sealed P4-B corpus/gold/worlds as committed.
* Do not modify the instrument, corpus, gold, anchors, transforms, or N.
* Run Flash only: `qwen/qwen3.8-flash` via OpenRouter SMALL (`OPENROUTER_API_KEY_SMALL`).
* IDs: B01, B02, B03 in order. `max_steps = 40`. Hard cap $30.
* Do not inspect or use P1–P3 outcomes for tuning.
* Do not add/remove/reorder pilot clusters.
* Record natural last-text τ and the frozen P4 `{status, cause, committed}`.
* Do not treat the pilot as confirmatory E1–E4 or as N_B.
* Do not open GPT or Claude.
* Do not proceed to Phase 4.

Gate: PASS iff ≥ 2 of 3 legs yield a last-text the frozen instrument scores without harness exception.

If FAIL or BLOCKED: record it and stop. Do not repair instrument/corpus from pilot outcomes.

If PASS: freeze the pilot record, report actual USD, all three results, and that the next licensed step is PHASE_4_MAIN (still BLOCKED).

Hard stop after B01–B03. Do not spend beyond $30.
