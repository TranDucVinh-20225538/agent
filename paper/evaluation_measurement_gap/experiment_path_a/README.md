# Path A — public observation + ABSTAIN

**STOPPED.** Licensed sentence is 126 vs 173 only. Not M1a transport. Do not retune. Do not count another rate.

| File | Role |
|---|---|
| `PROTOCOL.md` | Question, tables, objects |
| `I_LOCK.md` | Family admission (498 / 804). No rates |
| `EPISODE_ELIGIBILITY.md` | EXEC_FAIL vs ELIGIBLE |
| `EXTRACTOR.md` / `extract_i.py` / `test_extract_i.py` | Outcome-blind \(I\) |
| `schema/admitted_keys.csv` | 498 download paths |
| `RESULT.md` | Licensed finding: 126 vs 173 heterogeneous FAIL; Table 2 secondary |
| `out/qc_success_abstain.md` | QC of eight SUCCESS∩ABSTAIN; not a finding |

Do not commit `data/`. Extractor and `path_a_cells.csv` stay frozen. QC overlay does not retune \(I\).

`python3 test_extract_i.py`  
`python3 list_admitted.py`  
`python3 fetch_admitted.py`  # optional first-arg limit
