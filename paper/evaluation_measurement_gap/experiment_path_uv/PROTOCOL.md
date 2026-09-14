# Path UV protocol

**Status:** OPEN 2026-09-13. `UV_LOCK.md` is the constant lock.

1. `python3 experiment_path_uv/fetch_uv.py` — source + parquet metadata.
2. `python3 experiment_path_uv/classify_u1.py` — freeze `out/u1_cells.csv`.
3. Do not retune K.
4. Do not re-run UV until U1 is written and the user orders `U_RERUN.md`.
5. Do not put U1 in `main.tex` as E2 / M1a transport.
6. U2 sample rule is `SAMPLE_LOCK.md` (locked before full R). Do not retune.
   Annotators: **3** (Fleiss' κ + majority). Locked before full 106-R.
7. `sample_u2.py` once after `r_results.jsonl` is complete. Two-stage
   labels only. Primary number is IRRECOVERABLE, not isolation DECISIVE.
   Do not move or refactor `run_r.py` / `group_r.py` while R is running.
   Generic copy of the audit helpers: `../evidence-loss-audit/` (do not
   import that package from the live recovery job).
