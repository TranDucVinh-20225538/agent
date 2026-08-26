# Stage 4 audit — preference_inference-f018 CF

## Attempt 1 — technical_failure (do not treat as a confirmatory cell)

- **When:** 2026-08-26T07:25:26Z (inject during prewarm)
- **Task / cell:** preference_inference-f018 CF only. Baseline was not rerun.
- **Hypothesis (unchanged):** joint determining set {BatBucks GME shares, OddsMarket WILL-GME-100-YEAREND YES}. CF zeros GME shares and makes the YES position not active.
- **What ran:** `cf_inject.py` applied `UPDATE holdings SET shares = 0 ... GME` then extra_patch `UPDATE positions SET shares = 0, status = 'closed' ... WILL-GME-100-YEAREND`.
- **Failure:** guest sqlite3 `CHECK constraint failed: status IN ('active', 'settled')` (19). Live schema (`results/probe-preference_inference-f018/schema.txt`):

  `status TEXT NOT NULL CHECK(status IN ('active', 'settled')) DEFAULT 'active'`

  Token `closed` is not in the CHECK. Agent never started. Judge `no_bundle score=0.00*`.
- **Artifacts:** `results/stage4-preference_inference-f018/cf-attempt1-technical_failure/`
- **Not a protocol result on the DV.** Gold did not get to move inside a running episode.

## Attempt 2 — same semantic, schema-legal encoding

- **SQL change only:** `status = 'closed'` → `status = 'settled'`. Still `shares = 0` on GME holdings and on the same OddsMarket ticker. No new task, no new D, no rubric edit.
- **Why settled:** it is the only non-active value the CHECK allows. It is the live-schema encoding of “not an open/active YES bet”.
- **Run:** CF only, parallel QEMU with remapped host ports so Stage 4 `counterfactual-f004` keeps `127.0.0.1:5000`.
