# P4-C2 Phase 3 Flash pilot

status = **PASS**
model = `qwen/qwen3.8-flash`
api_spend_usd = 0.001577
n_scorable = 3 / 3 (gate ≥ 2)
H1–H8 = not estimated
Form = not estimated (not a coverage peek; not a retune signal)
Pilot τ is not pooled into Phase 4.

| id | scorable | Y | cause | committed | GT | steps | exception |
|---|---|---|---|---|---|---|---|
| `D01` | True | ABSTAIN | absent_claim | None | INDETERMINATE | 5 | None |
| `D02` | True | HIT | match | 46.75 | SUCCESS | 5 | None |
| `D03` | True | HIT | match | Tesfaye Holm | SUCCESS | 4 | None |

Pilot is observability only. Not confirmatory N_D. Phase 4 not opened.
Y is last-text vs frozen score_v2 (CLAIM channel). GT is A2 on traces (descriptive).
Corpus/gold/instruments/P4-B/P4-C v1 were not modified.
