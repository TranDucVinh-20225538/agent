# Quantitative claim audit (draft v0.3)

Every number in `draft/main.tex` must appear here. If it is not here, it is not licensed.
Reconciled against `EVIDENCE_MAP.md` and `CLAIM_LEDGER.md`. Populations are **not** pooled.

| Claim | Number | Artifact / source | Population | Interpretation allowed | Forbidden interpretation |
|---|---|---|---|---|---|
| Shao scale (related work) | 2,385 traces / 15 benchmarks | arXiv:2607.22368 abs (verified 2026-09-13) | Shao's audit, not ours | Shao's protocol-validity study is large | Our n is comparable; we audited 2,385 traces |
| Bean scale (related work) | 445 LLM benchmarks | arXiv:2511.04703 / NeurIPS 2025 D&B | Bean review | Construct-validity checklists already exist | We reviewed 445 CUA benches |
| Dong verdict audit | 150 FAIL traces; 15.3% wrong FAIL (10.7% FN, 4.7% broken, 3.3% unclear) | arXiv:2607.28367 HTML/PDF | Dong's five-benchmark FAIL sample | Dong's verdict-audit result | Our paper found 15.3% wrong scores; CUA benches are 15% invalid |
| S1 schedule | 46/50 cells; 92 legs | `out/stage4_counterfactual_analysis_final/paper_results.md` (`b7b4203`) | MyPCBench paired cells | Executed sample size | 50-task prevalence |
| S1 execution fail | 35/92 | same; `failure_audit.csv` | legs | Absent observations | Tracking misses / agent FNs |
| S1 valid pairs | 24/46 cells | same | valid pairs | Existence sample | Prevalence of dissociation |
| S1 Claude | valid 9; track-valid 7; A 6; sens 1; B 2; inv 0.857 [0.421, 0.996] | `statistical_summary.json` | Claude primary | Per-lane existence + wide CI | Most agents are Type A; pooled rate |
| S1 GPT-5.5 | 8 / 7 / 3 / 4 / 1; 0.429 [0.099, 0.816] | same | GPT primary | same | Ranking vs Claude |
| S1 Qwen 35B | 1 / 1 / 1 / 0 / 0; [0.025, 1.000] | same | one pair | Existence only | A third primary rate |
| S2 roster | 57 legs × 3 | tag `paper2-frozen` → `39cc662` | three agents, one protocol | Coverage comparison | Rank 57 tasks |
| S2 DONE/\|A\| | 32/9, 29/8, 4/1 | AAMAS coverage table | DONE legs / valid pairs | Eligibility | Agent quality ranking |
| S2 mean S⁰ / STS | 69.3/0.130; 95.8/0.229; 100/0 | same | on-A pairs; Claude n=1 | Coverage-conditioned scores | Claude is best (n=1) |
| S2 binary Y | Y=0 on 18/18 | AAMAS | valid pairs | No positive class for calibration | Agents never track |
| S2 selection | not evaluated (<3 ranked) | pre-registered | ranked roster | Plan outcome | Selection experiment failed |
| S2 exploratory Δ | ΔS⁰=+46.5 [21.0,72.0]; ΔSTS=−0.042 [−0.125,0]; seed 20260904 B=5000 | AAMAS | 4-task ∩ | Exploratory disagreement | Prevalence of ranking instability |
| S2 reversal | retrieval-f009; 3 ties | AAMAS | 4 tasks | One-task carrier | General reversal |
| S2 excluded S | 46.4 / 44.9 / 26.1 vs 69.3 / 95.8 / 100; 2+2+1 cells S≥90 no DONE | AAMAS | excluded vs on-A | Completion filter hides high-S non-DONE | Agents hide evidence (Gate 0) |
| S3 rows | 134 = 57×components | P3_0_CONCLUSION | rows | Unit of analysis | 134 independent tasks |
| S3 categories | MATCH 20; RECALL_MISS 39; ABSENT 61; (VACUOUS 14 not restated in v0.3 body except via 20+39+61) | 0.6 recall audit | 134 rows | Category counts | Agent error mix |
| S3 R1 | 59=20+39; sens 20/59=0.339 | AAMAS S3 | R1-positive rows | Instrument sensitivity | Agent recall |
| S3 miss causes | M1a 13; M1b 7; M2 9; M3 5; M4 5 | tab:causes | 39 misses | Multi-mechanism | Single cause; injected-world story |
| S3 M1a majority | 7/13 | P3_0_CONCLUSION | M1a subset | Gold was majority yet discarded | Parser is always wrong |
| S3 M1 on ABSENT | 25/61 | same | ABSENT rows | M1 not exclusive to misses | 25 extra M1a |
| S3 extractor | `3242c30…` | P3_0 | frozen P | Reproducibility | We retuned P |
| S3 repairs | FROZEN 20; R-AGG 28; R-SCOPE 13; R-CMP 20; R-CHAN 15; ALL 10 (sens/59) | tab:repairs | 134 rows / 59 R1 | Diagnostic interventions | Replacement method |
| S3 R-AGG signed | +8 / +18 (26 abstentions released) | AAMAS | R-AGG vs FROZEN | Permissive repair non-dominance | Repair theorem; ship R-AGG |
| S3 R-SCOPE dest. | 14/20 MATCH | same | MATCH rows | Scope repair destroys correct | Always worse windowing |
| S3 C7 | −0.0417 → +0.1667; GPT 0.250→0.042; n_eff=1 | AAMAS | 4-task ∩ | Existence of ordering move | Ranking instability in general |
| S3 G2 recon | 9/30 FAIL; G1 100% | `1ed4215` | 30 labels | Spec not reconstructed | Hand specs always wrong |
| S3 comparative gate | 16/28; need 20; not opened | `a54e8a9` | clusters | Experiment not opened | Gate 0 / agents hide |
| P4-B | 20×2=40; 40 DONE; HIT 5 MISS 5 ABSTAIN 30; all no_anchor; E3 4<5; E4 0 | `4c3d14b` | confirmatory episodes | Completion ≠ determining E | Agents failed; metric broken |
| P4-C Flash | HIT 3 MISS 2 ABSTAIN 25; Cov 0.1667; CC 0.6000; Abs 0.8333 | `42e49a6` | N_C=30 Flash | Sparse last-text | Flash incompetent |
| P4-C2 Flash | HIT 26 MISS 2 ABSTAIN 1 unscored 1; Form 0.9333; CC 0.9286; H3 N/E (8<10) | `2b1b8d6` | N=30 Flash | Form ≠ two-sided ID | Form=validity; no MISS in nature (D15/D24 exist) |
| P4-D Flash | 30 HIT 0 MISS 0 ABSTAIN; Form 1.0000; I_CC=0; G2 10/10; minus/pm 10/10; W1; G3 | `c663cf8` | N=30 Flash | Unidentifiable two-sided CC under competence | Flash 100% reliable; agent unreliable; P4-M proven |
| Ext WAV | 812 tasks; 2 demo logs | `de66e0a` | WAV public release | Not an NL last-text dump | WAV agents are unreliable |
| Ext | N/A/B/C n/a | same | none admitted | Eligibility STOP | Benchmarks generally not measurement-ready |

**Hygiene notes**

- Abstract 40 completed / 30 abstentions refers to P4-B 40/40 DONE + 30 ABSTAIN (not 40 HIT).
- Abstract omits S1 invariance percentages on purpose.
- Dong 15.3% is Dong's number, cited as Dong's, not ours.
- VACUOUS_GOLD 14 is in the evidence map but not restated in v0.3 body (20+39+61=120; 120+14=134). Allowed omission.
- GPT P4-C/C2/D descriptive counts are in the map; v0.3 body reports Flash confirmatory gates only. Allowed compression.
