# Paper evidence map (v0.3)

**Date:** 2026-09-13  
**Rule:** every number in the draft must appear in `QUANTITATIVE_CLAIM_AUDIT.md` with a source. If it is not there, it is not in the paper.

Repo HEAD when empirical locks were last frozen: `de66e0a` (external-validation STOP). Studies were not re-run for this revision.

---

## Evidence hierarchy (not equal novelty)

```
PRIMARY EMPIRICAL CONTRIBUTION
    P3  M1a (gold collected then discarded) + repair non-dominance
        39/59 misses; 13/39 M1a; R-AGG +8/−18; ALL worse than frozen

SECONDARY EMPIRICAL CONTRIBUTION
    P4 constructive boundaries / identifiability
        B: 40 DONE / 30 ABSTAIN
        C: Cov 0.1667
        C2: Form 0.9333; H3 NOT_EVALUABLE
        D: 30 HIT / 0 MISS; I_CC=0

SUPPORTING EVIDENCE
    P1  score ≉ outcome (24 valid pairs; existence)
    P2  evaluation/selection change evidential basis (|A|=9/8/1; Y=0 on 18/18)

FORMALIZATION (not a contribution)
    P4-M  M(τ,I) notation; justification ≠ truth; no-leakage implication

EXTERNAL
    eligibility STOP  (no corpus under frozen last-text typed I)
```

Shared empirical family for P1–P3: MyPCBench + paired counterfactual protocol. P4 uses a constructed desktop slate, not MyPCBench. Populations are **not added**.

---

## P1 — Score/outcome dissociation (supporting)

| Field | Locked value | Source |
|---|---|---|
| Design | 5×10 schedule; 50 intended cells; 4 never scheduled; 46 executed; 92 legs | `out/stage4_counterfactual_analysis_final/paper_results.md` (snapshot `b7b4203`) |
| DONE / execution fail | 57/92 DONE; 35/92 execution failures (not tracking misses) | same; `failure_audit.csv` |
| Valid pairs | 24/46 cells | same |
| Claude (primary) | valid 9; track-valid 7; Type A 6; sensitive 1; Type B 2; inv. 0.857 CI [0.421,0.996] | `statistical_summary.json` |
| GPT-5.5 (primary) | valid 8; track-valid 7; Type A 3; sensitive 4; Type B 1; inv. 0.429 CI [0.099,0.816] | same |
| Qwen3.5-35B-A3B | valid 1; Type A 1; CI [0.025, 1.000] | same |
| Size/exploratory | Qwen3.5-9B and Flash: 3 valid each; **not pooled** | same |
| Figures | `gold_state_change.png`, `score_pairs_primary.png` | `out/stage4_counterfactual_analysis_final/` |
| Claim | Existence of Type A and Type B; not a prevalence | ledger S1-1 |

**Do not headline** `primary_pooled` 18/15/10/5/3 in `statistical_summary.json`.

---

## P2 — Selection and coverage (supporting)

Locked heading: *Evaluation and selection can change the evidential basis of a reliability comparison.*

| Field | Locked value | Source |
|---|---|---|
| Roster | GPT-5.5, Qwen3.8-Flash, Claude Opus 4.6; 57 legs each | tag `paper2-frozen` → `39cc662` |
| Coverage | DONE/57: 32 / 29 / 4; \|A\| = 9 / 8 / 1 | AAMAS Table coverage |
| mean \(S^0\) | 69.3 / 95.8 / 100 (Claude = one pair) | same |
| mean STS | 0.130 / 0.229 / 0 | same |
| Binary Y | \(Y=0\) on all 18 valid pairs | AAMAS |
| Confirmatory selection | not evaluated (\(<3\) ranked agents) | AAMAS; pre-registered |
| Common support \(\mathcal{A}^{\cap}\) | 4 tasks | AAMAS |
| Exploratory \(\Delta S^0\) Flash−GPT | +46.5, 95% CI [21.0, 72.0], seed 20260904, B=5000 | AAMAS |
| Exploratory \(\Delta\mathrm{STS}\) | −0.042, 95% CI [−0.125, 0.000] | AAMAS |
| Per-task reversal | concentrated on `retrieval-f009` | AAMAS |
| Completion-conditioned | excluded mean S 46.4 / 44.9 / 26.1 vs on-A 69.3 / 95.8 / 100; 2+2+1 excluded cells S≥90 without DONE | AAMAS |

---

## P3 — Evidence loss and repair (PRIMARY)

| Field | Locked value | Source |
|---|---|---|
| Unit | 134 rows = 57 legs × components | P3_0_CONCLUSION |
| Categories | MATCH 20; RECALL_MISS 39; ABSENT 61; VACUOUS_GOLD 14 | 0.6 recall audit |
| R1-positive | 59 = 20+39; sensitivity 20/59 = 0.339 | AAMAS Study 3 |
| Split among 39 misses | M1a 13; M1b 7; M2 9; M3 5; M4 5 | AAMAS tab:causes |
| M1a majority discard | 7/13 | P3_0_CONCLUSION |
| M1 also on ABSENT | 25/61 | same |
| Frozen extractor | `3242c30a1423f9ef90754809e50cd2698c5560b5` | P3_0_CONCLUSION |
| Repairs (134 rows) | FROZEN 20/59; R-AGG 28; R-SCOPE 13; R-CMP 20; R-CHAN 15; ALL 10 | AAMAS tab:repairs |
| R-AGG signed | +8 correct / +18 wrong | same |
| R-SCOPE | destroys 14/20 MATCH | same |
| R-CHAN \(\Delta\mathrm{STS}\) | frozen −0.0417 → +0.1667; \(n_{\mathrm{eff}}=1\) | AAMAS; C7 existence only |
| Portability R | G1 100%; G2 9/30 FAIL | P3-2 commit `1ed4215` |
| Comparative gate | 16/28 survived; **not opened** | `a54e8a9` |
| Gate 0 | not a paper contribution | P3_0_CONCLUSION |

---

## P4-B / C / C2 / D — Constructive boundaries (SECONDARY)

| Stage | Locked value | Commit |
|---|---|---|
| P4-B | 40/40 DONE; HIT 5 MISS 5 ABSTAIN 30; E3/E4 N/E; positive-but-incomplete | `4c3d14b` |
| P4-C | Flash HIT 3 MISS 2 ABSTAIN 25; Cov 0.1667; metric v1 FAIL on coverage gate | `42e49a6` |
| P4-C2 | Flash HIT 26 MISS 2; Form 0.9333; H3 NOT_EVALUABLE; ordinary MISS D15/D24 | `2b1b8d6` |
| P4-D | Flash 30 HIT / 0 MISS; \(I_{CC}=0\); G2 10/10; W1; G3 | `c663cf8` |

Instruments frozen: v1 `c43a920a…7d59`; v2 `a87ac636…fcf3`; wrapper `2a028f2b…e8e08`. Not modified this revision.

---

## P4-M — Formalization only

Object \(\mathcal{M}(\tau,\mathcal{I})\). THEORY CLOSED. Empirical implementation NOT STARTED. Typed correspondence is a no-leakage implication, not a validity theorem. P4-D 30/30 is not a proof of P4-M.

---

## External validation — eligibility STOP

| Field | Locked value | Source |
|---|---|---|
| Status | STOP; Phases 2–5 not opened | `de66e0a` |
| N, A, B, C | n/a | same |
| Light re-audit (2026-09-13, card/docs only) | `markov-ai/computer-use` (OSWorld successes + screenshots/a11y; score-filtered); AgentTrove (mixed terminus-2). Neither satisfies typed \(k\) + independent \(L\) + last-text \(I\) without an adapter. **STOP kept.** | public cards; no download, no `score_v2` run |
| Frozen I/P/E | unchanged | `frozen_artifact_hashes.json` |

Defensible sentence: we did not identify a public corpus satisfying this specific frozen last-text typed observation contract.

---

## What this map does **not** contain

- Any number computed after `de66e0a` except literature-citation figures from Dong/Shao/Bean.
- Agent rankings.
- A pooled “overall reliability.”
- A new experiment.
