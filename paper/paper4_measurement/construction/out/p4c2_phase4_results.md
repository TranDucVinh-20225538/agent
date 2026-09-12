# P4-C2 Phase 4 confirmatory validation

N_D = 30 clusters; confirmatory episodes = 60 / 60
models = Flash `qwen/qwen3.8-flash` (primary) + GPT `openai/gpt-5.5` (paired, not gated)
api_spend_usd_phase4 = 0.450873
api_spend_usd_cumulative = 0.45245 / 400.0
stopped = None
Phase-3 pilot τ not pooled. Claude not run. P4-B and P4-C v1 not pooled.
Measurement channel = last assistant text, CLAIM line only. Execution status is not HIT/MISS.
ABSTAIN is missing correspondence measurement, not task failure.
Form is interface compliance (parseable unique CLAIM). Never named coverage.

## Primary public report (Flash confirmatory, N_D = 30)

- Form = **0.9333**  (26+2)/30
- CC = **0.9286**
- Abs = 0.0333  (1/30)
- DH (Form, CC) = DH=0.8667 (Form=0.9333, CC=0.9286)

## Flash episode counts (not N)

- HIT = 26
- MISS = 2
- ABSTAIN = 1
- unscored = 1

## GPT paired (descriptive, not gated)

- HIT/MISS/ABSTAIN/unscored = 30/0/0/0
- Form = 1.0000
- CC = 1.0

## Gates (Flash confirmatory unless noted)

- H1 false HIT = **PASS** (n_false_hit=0; designed C3/C4 HIT=[]; transform HIT=[])
- H2 C1 sensitivity = **PASS** (eligible=10, floor=10, hit_rate=1.0)
- H3 C2 discrimination = **NOT_EVALUABLE** (eligible=8, floor=10, miss_rate=0.0)
- H4 invariance = **PASS** (n_changed=0; CLAIM-span named, not gated)
- H5 interface compliance = **PASS** (Form=0.9333, gate≥0.8; not coverage)
- H6 scalar honesty = **PASS**
- H7 anti-recovery = **PASS**
- H8 anti-circularity = **PASS**
- P4-C2-Metric v2 = **FAIL**

## Per cluster (Flash primary / GPT pair)

| id | family | slot | flash_exec | flash_Y | flash_cause | flash_GT | gpt_Y | gpt_cause |
|---|---|---|---|---|---|---|---|---|
| `D01` | Locate | C1-intended | DONE | HIT | match | SUCCESS | HIT | match |
| `D02` | Locate | C2-intended | DONE | HIT | match | SUCCESS | HIT | match |
| `D03` | Locate | C1-intended | DONE | HIT | match | SUCCESS | HIT | match |
| `D04` | Locate | C2-intended | DONE | HIT | match | SUCCESS | HIT | match |
| `D05` | Locate | ordinary | DONE | HIT | match | SUCCESS | HIT | match |
| `D06` | Compute | C1-intended | DONE | HIT | match | SUCCESS | HIT | match |
| `D07` | Compute | C2-intended | DONE | ABSTAIN | no_claim | SUCCESS | HIT | match |
| `D08` | Compute | C1-intended | DONE | HIT | match | SUCCESS | HIT | match |
| `D09` | Compute | ordinary | DONE | HIT | match | SUCCESS | HIT | match |
| `D10` | Compute | C2-intended | DONE | HIT | match | SUCCESS | HIT | match |
| `D11` | Reconcile | C1-intended | DONE | HIT | match | SUCCESS | HIT | match |
| `D12` | Reconcile | C2-intended | DONE | HIT | match | SUCCESS | HIT | match |
| `D13` | Reconcile | C2-intended | DONE | HIT | match | SUCCESS | HIT | match |
| `D14` | Reconcile | C1-intended | DONE | HIT | match | SUCCESS | HIT | match |
| `D15` | Reconcile | ordinary | DONE | MISS | mismatch | SUCCESS | HIT | match |
| `D16` | Filter | C1-intended | DONE | HIT | match | SUCCESS | HIT | match |
| `D17` | Filter | C2-intended | DONE | HIT | match | SUCCESS | HIT | match |
| `D18` | Filter | ordinary | DONE | HIT | match | SUCCESS | HIT | match |
| `D19` | Filter | ordinary | DONE | HIT | match | SUCCESS | HIT | match |
| `D20` | Filter | C1-intended | DONE | HIT | match | SUCCESS | HIT | match |
| `D21` | Tally | C1-intended | DONE | HIT | match | SUCCESS | HIT | match |
| `D22` | Tally | C2-intended | DONE | HIT | match | SUCCESS | HIT | match |
| `D23` | Tally | ordinary | DONE | HIT | match | SUCCESS | HIT | match |
| `D24` | Tally | ordinary | DONE | MISS | mismatch | SUCCESS | HIT | match |
| `D25` | Tally | C2-intended | exception | None | None | SUCCESS | HIT | match |
| `D26` | Multi-step | C1-intended | DONE | HIT | match | SUCCESS | HIT | match |
| `D27` | Multi-step | C2-intended | DONE | HIT | match | SUCCESS | HIT | match |
| `D28` | Multi-step | ordinary | DONE | HIT | match | SUCCESS | HIT | match |
| `D29` | Multi-step | ordinary | DONE | HIT | match | SUCCESS | HIT | match |
| `D30` | Multi-step | ordinary | DONE | HIT | match | SUCCESS | HIT | match |

H2/H3 floors are on distinct Flash-eligible clusters, not 60 episodes.
NOT EVALUABLE on a required floor fails P4-C2. Corpus/gold/instruments were not modified.
Do not retune score_v2, wrapper, or H5 after seeing Form.

## Mechanism (not a retune)

H3 is the only failing gate. Designed C2-intended ∩ committed value (Y ∈ {HIT,MISS}) has **n_eligible = 8 < floor 10**, miss_rate = **0.0**. The eight committed C2-intended Flash claims (D02, D04, D10, D12, D13, D17, D22, D27) are all HIT: gold on C2-intended clusters is still the live correct value, and Flash reported it. D07 last-text is the bare gold `38.35` with no `CLAIM:` line → ABSTAIN `no_claim` (fail-closed; not eligible). D25 Flash is unscored (`http_400` empty-content from the provider after the sources were read). Do not rerun D25 or accept bare numbers to manufacture the floor. Even if n were 10, miss_rate 0 would still fail the 0.90 MISS threshold.

H5 PASS (Form 0.9333) means the declared-prose channel was used. H2 PASS (10/10 C1-intended ∩ A2=SUCCESS ∩ committed are HIT). H1 0 false HIT on DQ C3/C4 and on c3/c4 transforms of natural τ. Working-span H4 unchanged. GPT is paired only (Form 1, CC 1); do not switch primary after τ.

Ordinary MISS with A2=SUCCESS: D15 committed `63.95` (sum) vs gold `37.55` (live line); D24 committed `0` vs gold `18`. Those cells are correspondence working, not H3.

STOP. Do not lower H3. Do not open Phase 5. Do not patch `score_v2` or the wrapper.
