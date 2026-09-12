# P4-D Phase 4 confirmatory validation

N = 30 Flash clusters E01–E30; confirmatory episodes = 60 / 60
models = Flash `qwen/qwen3.8-flash` (primary) + GPT `openai/gpt-5.5` (paired, not gated)
api_spend_usd_phase4 = 0.497182
api_spend_usd_cumulative = 0.49858 / 400.0
stopped = None
Phase-3 pilot τ not pooled. Claude not run. P4-B / P4-C v1 / P4-C2 not modified.
Measurement channel = last assistant text, CLAIM line only. Execution status is not HIT/MISS.
ABSTAIN is missing correspondence measurement, not task failure.
Form is interface compliance (parseable unique CLAIM). Never named coverage.
No minus MISS quota. No CC ≥ 0.90 gate. n_MISS_designed is descriptive only.

## Primary public profile (Flash confirmatory, N = 30)

- Form = **1.0000**  (30+0)/30
- CC = **1.0000 (descriptive, not interpretable; I_CC=0)**
- Abs = 0.0000  (0/30)
- I_CC = **0**
- DH = not reported (requires I_CC=1)

## Flash episode counts (not N)

- HIT = 30
- MISS = 0
- ABSTAIN = 0
- unscored = 0
- n_MISS_designed = 0 (descriptive only)

## Strata by condition (construction factors, not N)

- plus: HIT=10 MISS=0 ABSTAIN=0 unscored=0 Form=1.0000 CC=1.0000
- minus: HIT=10 MISS=0 ABSTAIN=0 unscored=0 Form=1.0000 CC=1.0000
- pm: HIT=10 MISS=0 ABSTAIN=0 unscored=0 Form=1.0000 CC=1.0000

## GPT paired (descriptive, not gated)

- HIT/MISS/ABSTAIN/unscored = 30/0/0/0
- Form = 1.0000
- CC = 1.0

## Gates (Flash confirmatory unless noted)

- G0 frozen DFC = **PASS**
- G1 false HIT = **PASS** (n_false_hit=0; designed C3/C4 HIT=[]; transform HIT=[])
- G2 plus sensitivity = **PASS** (eligible=10, floor=10, hit_rate=1.0)
- G3 two-sided observability = **FAIL** (I_CC=0, n_HIT=30, n_MISS=0, W1=True)
- G4 working-span invariance = **PASS** (n_changed=0; CLAIM-span named, not gated)
- G5 Form = **PASS** (overall=1.0000, plus=1.0000, gate≥0.8; not coverage)
- G6 honesty = **PASS**
- G7 anti-factory = **PASS** (F2=PASS, F3=PASS, F4=PASS, F5=PASS)
- G8 anti-circularity = **PASS**
- P4-D protocol = **FAIL**
- first_failing_gate = G3

## Per cluster (Flash primary / GPT pair)

| id | family_id | condition | flash_exec | flash_Y | flash_cause | flash_GT | gpt_Y | gpt_cause |
|---|---|---|---|---|---|---|---|---|
| `E01` | F01 | plus | DONE | HIT | match | SUCCESS | HIT | match |
| `E02` | F01 | minus | DONE | HIT | match | SUCCESS | HIT | match |
| `E03` | F01 | pm | DONE | HIT | match | SUCCESS | HIT | match |
| `E04` | F02 | plus | DONE | HIT | match | SUCCESS | HIT | match |
| `E05` | F02 | minus | DONE | HIT | match | SUCCESS | HIT | match |
| `E06` | F02 | pm | DONE | HIT | match | SUCCESS | HIT | match |
| `E07` | F03 | plus | DONE | HIT | match | SUCCESS | HIT | match |
| `E08` | F03 | minus | DONE | HIT | match | SUCCESS | HIT | match |
| `E09` | F03 | pm | DONE | HIT | match | SUCCESS | HIT | match |
| `E10` | F04 | plus | DONE | HIT | match | SUCCESS | HIT | match |
| `E11` | F04 | minus | DONE | HIT | match | SUCCESS | HIT | match |
| `E12` | F04 | pm | DONE | HIT | match | SUCCESS | HIT | match |
| `E13` | F05 | plus | DONE | HIT | match | SUCCESS | HIT | match |
| `E14` | F05 | minus | DONE | HIT | match | SUCCESS | HIT | match |
| `E15` | F05 | pm | DONE | HIT | match | SUCCESS | HIT | match |
| `E16` | F06 | plus | DONE | HIT | match | SUCCESS | HIT | match |
| `E17` | F06 | minus | DONE | HIT | match | SUCCESS | HIT | match |
| `E18` | F06 | pm | DONE | HIT | match | SUCCESS | HIT | match |
| `E19` | F07 | plus | DONE | HIT | match | SUCCESS | HIT | match |
| `E20` | F07 | minus | DONE | HIT | match | SUCCESS | HIT | match |
| `E21` | F07 | pm | DONE | HIT | match | SUCCESS | HIT | match |
| `E22` | F08 | plus | DONE | HIT | match | SUCCESS | HIT | match |
| `E23` | F08 | minus | DONE | HIT | match | SUCCESS | HIT | match |
| `E24` | F08 | pm | DONE | HIT | match | SUCCESS | HIT | match |
| `E25` | F09 | plus | DONE | HIT | match | SUCCESS | HIT | match |
| `E26` | F09 | minus | DONE | HIT | match | SUCCESS | HIT | match |
| `E27` | F09 | pm | DONE | HIT | match | SUCCESS | HIT | match |
| `E28` | F10 | plus | DONE | HIT | match | SUCCESS | HIT | match |
| `E29` | F10 | minus | DONE | HIT | match | SUCCESS | HIT | match |
| `E30` | F10 | pm | DONE | HIT | match | SUCCESS | HIT | match |

G2 floor is plus ∩ A=SUCCESS ∩ committed on Flash, n≥10. G3 is I_CC on Flash N=30.
NOT_EVALUABLE on a required floor fails P4-D. Corpus/gold/instruments/P4-B/P4-C/P4-C2 were not modified.
Do not retune score_v2, wrapper, distractors, or floors after seeing τ.
If G3 fails with plus competence held, the result is W1 — do not amp distractors.
