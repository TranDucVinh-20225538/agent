# P4-D TERMINAL STOP

**Status: FAIL. Frozen. Do not repair or rerun.**

| Field | Value |
|---|---|
| Phase reached | Phase 4 confirmatory (complete, 60/60) |
| Protocol | FAIL |
| First failing gate | **G3** two-sided observability |
| Classification | **W1** — challenge weak / correspondence remains unobservable |
| Exact rule | `I_CC = 1` iff `n_HIT ≥ 8` and `n_MISS ≥ 8` on Flash `N = 30` |
| Evidence | Flash HIT=30, MISS=0, ABSTAIN=0, unscored=0 → `I_CC = 0` |
| Plus competence | G2 PASS: plus ∩ A=SUCCESS ∩ committed HIT rate = 1.0, n=10 |
| minus / pm | HIT=10/10 each, MISS=0 |
| Form / CC / Abs / I_CC | 1.0000 / 1.0000 (descriptive, not interpretable) / 0.0000 / 0 |
| GPT pair | 30/30 HIT (descriptive, not gated) |
| Spend | Phase 4 $0.497182; cumulative with Phase 3 $0.498580 / $400 |
| Pilot pooled | no |
| Frozen artifacts changed | no (v1/v2/wrapper/A/T hashes match C2; P4-B / P4-C v1 / P4-C2 untouched) |

G0, G1, G2, G4, G5, G6, G7, G8 PASS. Protocol fails on the first scientific gate that did not pass (G3).

Per freeze: do not increase distractors, redesign worlds, modify the parser, introduce a MISS quota, switch primary to GPT, or open Phase 5.
