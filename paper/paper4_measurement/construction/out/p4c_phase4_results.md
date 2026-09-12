# P4-C Phase 4 confirmatory validation

N_C = 30 clusters; confirmatory episodes = 60 / 60
models = Flash `qwen/qwen3.8-flash` (primary) + GPT `openai/gpt-5.5` (paired)
api_spend_usd_phase4 = 0.395962
api_spend_usd_cumulative = 0.397092 / 400.0
stopped = None
Phase-3 pilot τ not pooled. Claude not run. P4-B not pooled.
Measurement channel = last assistant text only. Execution status is not HIT/MISS.
ABSTAIN is missing correspondence measurement, not task failure.

## Primary public report (Flash confirmatory, N_C = 30)

- Cov = **0.1667**  (3+2)/30
- CC = **0.6000**
- Abs = 0.8333  (25/30)
- DH (Cov, CC) = DH=0.1000 (Cov=0.1667, CC=0.6000)

## Flash episode counts (not N)

- HIT = 3
- MISS = 2
- ABSTAIN = 25
- unscored = 0

## GPT paired (descriptive, not gated)

- HIT/MISS/ABSTAIN/unscored = 5/1/24/0
- Cov = 0.2000
- CC = 0.8333333333333334

## Gates (Flash confirmatory unless noted)

- G1 false HIT = **PASS** (n_false_hit=0; designed C3/C4 HIT=[])
- G2 C1 sensitivity = **NOT_EVALUABLE** (eligible=3, floor=10, hit_rate=1.0)
- G3 C2 discrimination = **NOT_EVALUABLE** (eligible=0, floor=10, miss_rate=None)
- G4 invariance = **PASS** (n_changed=0)
- G5 coverage = **FAIL** (Cov=0.1667, gate≥0.5)
- G6 scalar honesty = **PASS**
- P4-C-Metric v1 = **FAIL**

## Per cluster (Flash primary / GPT pair)

| id | family | slot | flash_exec | flash_Y | flash_cause | flash_GT | gpt_Y | gpt_cause |
|---|---|---|---|---|---|---|---|---|
| `C01` | Locate | C1-intended | DONE | HIT | match | SUCCESS | HIT | match |
| `C02` | Locate | C2-intended | DONE | HIT | match | SUCCESS | ABSTAIN | no_anchor |
| `C03` | Locate | C1-intended | DONE | MISS | mismatch | SUCCESS | ABSTAIN | no_anchor |
| `C04` | Locate | C2-intended | DONE | MISS | mismatch | SUCCESS | MISS | mismatch |
| `C05` | Locate | ordinary | DONE | ABSTAIN | no_anchor | SUCCESS | HIT | match |
| `C06` | Compute | C1-intended | DONE | ABSTAIN | no_anchor | SUCCESS | ABSTAIN | no_anchor |
| `C07` | Compute | C2-intended | DONE | ABSTAIN | no_anchor | SUCCESS | ABSTAIN | no_anchor |
| `C08` | Compute | C1-intended | DONE | ABSTAIN | no_anchor | SUCCESS | ABSTAIN | no_anchor |
| `C09` | Compute | ordinary | DONE | ABSTAIN | no_anchor | SUCCESS | ABSTAIN | no_anchor |
| `C10` | Compute | C2-intended | DONE | HIT | match | SUCCESS | ABSTAIN | no_anchor |
| `C11` | Reconcile | C1-intended | DONE | ABSTAIN | no_anchor | SUCCESS | ABSTAIN | no_anchor |
| `C12` | Reconcile | C2-intended | DONE | ABSTAIN | no_anchor | SUCCESS | ABSTAIN | no_anchor |
| `C13` | Reconcile | C2-intended | DONE | ABSTAIN | no_anchor | SUCCESS | ABSTAIN | no_anchor |
| `C14` | Reconcile | C1-intended | DONE | ABSTAIN | no_anchor | SUCCESS | ABSTAIN | no_anchor |
| `C15` | Reconcile | ordinary | DONE | ABSTAIN | no_anchor | SUCCESS | HIT | match |
| `C16` | Filter | C1-intended | DONE | ABSTAIN | no_anchor | SUCCESS | ABSTAIN | no_anchor |
| `C17` | Filter | C2-intended | DONE | ABSTAIN | no_anchor | SUCCESS | ABSTAIN | no_anchor |
| `C18` | Filter | ordinary | DONE | ABSTAIN | no_anchor | SUCCESS | ABSTAIN | no_anchor |
| `C19` | Filter | ordinary | DONE | ABSTAIN | no_anchor | SUCCESS | ABSTAIN | no_anchor |
| `C20` | Filter | C1-intended | DONE | ABSTAIN | no_anchor | SUCCESS | HIT | match |
| `C21` | Tally | C1-intended | DONE | ABSTAIN | no_anchor | SUCCESS | ABSTAIN | no_anchor |
| `C22` | Tally | C2-intended | DONE | ABSTAIN | no_anchor | SUCCESS | ABSTAIN | no_anchor |
| `C23` | Tally | ordinary | DONE | ABSTAIN | no_anchor | SUCCESS | ABSTAIN | no_anchor |
| `C24` | Tally | ordinary | DONE | ABSTAIN | no_anchor | SUCCESS | ABSTAIN | no_anchor |
| `C25` | Tally | C2-intended | DONE | ABSTAIN | no_anchor | SUCCESS | ABSTAIN | no_anchor |
| `C26` | Multi-step | C1-intended | DONE | ABSTAIN | no_anchor | SUCCESS | ABSTAIN | no_anchor |
| `C27` | Multi-step | C2-intended | DONE | ABSTAIN | no_anchor | SUCCESS | ABSTAIN | no_anchor |
| `C28` | Multi-step | ordinary | DONE | ABSTAIN | no_anchor | SUCCESS | ABSTAIN | no_anchor |
| `C29` | Multi-step | ordinary | DONE | ABSTAIN | ambiguous | SUCCESS | HIT | match |
| `C30` | Multi-step | ordinary | DONE | ABSTAIN | no_anchor | SUCCESS | ABSTAIN | no_anchor |

G2/G3 floors are on distinct Flash-eligible clusters, not 60 episodes.
NOT EVALUABLE on a required floor fails P4-C. Corpus/gold/instrument were not modified.
