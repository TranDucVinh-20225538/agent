# Quantitative claim audit (draft v0.5)

Every number in `draft/main.tex` must appear here. If it is not here, it is not licensed.
Reconciled against `EVIDENCE_MAP.md` and `CLAIM_LEDGER.md`. Populations are **not** pooled.

| Claim | Number | Artifact / source | Population | Where | Interpretation allowed | Forbidden interpretation |
|---|---|---|---|---|---|---|
| Shao scale (related work) | 2,385 traces / 15 benchmarks | arXiv:2607.22368 abs (verified 2026-09-13) | Shao's audit, not ours | main §2 | Shao's protocol-validity study is large | Our n is comparable; we audited 2,385 traces |
| Bean scale (related work) | 445 LLM benchmarks | arXiv:2511.04703 / NeurIPS 2025 D&B | Bean review | cited in RW, not restated as a numeral in v0.4 body except via citation | Construct-validity checklists already exist | We reviewed 445 CUA benches |
| Dong verdict audit | 150 FAIL traces; 15.3% wrong FAIL (10.7% FN, 4.7% broken, 3.3% unclear) | arXiv:2607.28367 | Dong's five-benchmark FAIL sample | main §2.3 | Dong's verdict-audit result | Our paper found 15.3% wrong scores |
| S1 valid pairs | 24; 35/92 execution fails | `b7b4203` | valid pairs / legs | app A | Existence sample | Prevalence of dissociation |
| S1 schedule | 46/50 cells; 92 legs | same | MyPCBench paired cells | app A | Executed sample size | 50-task prevalence |
| S1 Claude | valid 9; track-valid 7; A 6; sens 1; B 2; inv 0.857 [0.421,0.996] | `statistical_summary.json` | Claude primary | app A | Per-lane existence + wide CI | Most agents are Type A; pooled rate |
| S1 GPT-5.5 | 8 / 7 / 3 / 4 / 1; 0.429 [0.099,0.816] | same | GPT primary | app A | same | Ranking vs Claude |
| S1 Qwen 35B | 1 / 1 / 1 / 0 / 0; [0.025,1.000] | same | one pair | app A | Existence only | A third primary rate |
| S2 roster | 57 legs × 3 | tag `paper2-frozen` → `39cc662` | three agents, one protocol | app B | Coverage comparison | Rank 57 tasks |
| S2 DONE/\|A\| | 32/9, 29/8, 4/1 | AAMAS coverage table | DONE legs / valid pairs | app B | Eligibility | Agent quality ranking |
| S2 mean S⁰ / STS | 69.3/0.130; 95.8/0.229; 100/0 | same | on-A pairs; Claude n=1 | app B | Coverage-conditioned scores | Claude is best (n=1) |
| S2 binary Y | Y=0 on 18/18 | AAMAS | valid pairs | app B | No positive class for calibration | Agents never track |
| S2 selection | not evaluated (<3 ranked) | pre-registered | ranked roster | app B | Plan outcome | Selection experiment failed |
| S2 exploratory Δ | ΔS⁰=+46.5 [21.0,72.0]; ΔSTS=−0.042 [−0.125,0]; seed 20260904 B=5000 | AAMAS | 4-task ∩ | app B | Exploratory disagreement | Prevalence of ranking instability |
| S2 reversal | retrieval-f009; 3 ties | AAMAS | 4 tasks | app B | One-task carrier | General reversal |
| S2 excluded S | 46.4 / 44.9 / 26.1 vs 69.3 / 95.8 / 100; 2+2+1 cells S≥90 no DONE | AAMAS | excluded vs on-A | app B | Completion filter hides high-S non-DONE | Agents hide evidence (Gate 0) |
| S3 rows | 134 = 57×components | P3_0_CONCLUSION | rows | main §4 | Unit of analysis | 134 independent tasks |
| S3 categories | MATCH 20; RECALL_MISS 39; ABSENT 61 | 0.6 recall audit | 134 rows | main §4 | Category counts | Agent error mix |
| S3 R1 | 59=20+39; sens 20/59=0.339 | AAMAS S3 | R1-positive rows | main §4 | Instrument sensitivity | Agent recall |
| S3 miss causes | M1a 13; M1b 7; M2 9; M3 5; M4 5 | tab:causes | 39 misses | main Table 2 | Multi-mechanism | Single cause; injected-world story |
| S3 M1a majority | 7/13 | P3_0_CONCLUSION | M1a subset | main §4 | Gold was majority yet discarded | Parser is always wrong |
| S3 M1 on ABSENT | 25/61 | same | ABSENT rows | main §4 | M1 not exclusive to misses | 25 extra M1a |
| S3 extractor | `3242c30…` | P3_0 | frozen P | main Table 2 | Reproducibility | We retuned P |
| S3 repairs compact | FROZEN 20; R-AGG 28; ALL 10; MATCH dest 0/0/16 | tab:repairs | 59 R1 | main Table 3 | Signed diagnostic | Replacement method |
| S3 R-AGG signed | +8 / +18 (26 abstentions released) | AAMAS | R-AGG vs FROZEN | main §4 | Permissive repair non-dominance | Repair theorem; ship R-AGG |
| S3 full repairs | R-SCOPE 13; R-CMP 20; R-CHAN 15; Abst 89/63/56/89/104/79; M4 25/45 etc. | tab:repairs | 134 rows | app C Table 8 | Diagnostic | Always worse windowing as a law |
| S3 R-SCOPE dest. | 14/20 MATCH | same | MATCH rows | app C | Scope repair destroys correct | — |
| S3 R-CHAN dest. | 7 MATCH | same | MATCH rows | app C | — | — |
| S3 C7 | −0.0417 → +0.1667; GPT 0.250→0.042; n_eff=1 | AAMAS | 4-task ∩ | app C | Existence of ordering move | Ranking instability in general |
| S3 G2 recon | 9/30 FAIL; G1 100% | `1ed4215` | 30 labels | app C | Spec not reconstructed | Hand specs always wrong |
| S3 comparative gate | 16/28; need 20; not opened | `a54e8a9` | clusters | app C | Experiment not opened | Gate 0 / agents hide |
| P4-B | 20×2=40; 40 DONE; HIT 5 MISS 5 ABSTAIN 30 | `4c3d14b` | confirmatory episodes | main §5.1 | Completion ≠ determining E | Agents failed; metric broken |
| P4-C Flash | HIT 3 MISS 2 ABSTAIN 25; Cov 0.1667; gate ≥0.5 | `42e49a6` | N_C=30 Flash | main §5.1 | Sparse last-text | Flash incompetent |
| P4-C2 Flash | HIT 26 MISS 2 ABSTAIN 1 unscored 1; Form 0.9333; H3 N/E (8<10) | `2b1b8d6` | N=30 Flash | main §5.2 | Form ≠ two-sided ID | Form=validity; no MISS in nature |
| P4-D Flash | 30 HIT 0 MISS 0 ABSTAIN; Form 1.0000; I_CC=0 (needs 8+8); G2 10/10; minus/pm 10/10; W1; G3 | `c663cf8` | N=30 Flash | main §5.3 | Unidentifiable two-sided CC in this sample under locked rule | Flash 100% reliable; competence causes unidentifiability |
| S3 M1a×S join | 7/10 joinable S=100; 3 UNKNOWN; 9/9 in A have Y=0; earlier traj text 8/13 | `experiment_m1a_location/join.json` | 13 M1a rows | main §4 `tab:m1a-s100`; app D | Same-episode rubric S can be 100 after text discard | Screenshot contained gold; 171-N; Flash reliable |
| Path A FAIL split | 126 empty \(I\) vs 173 mismatch of 299 released FAIL | `experiment_path_a/RESULT.md`; `out/path_a_cells.csv` | WA+VWA string/url ELIGIBLE FAIL; not ARB-wide; not 498 | main §6; app E `tab:patha-fail` | Oracle FAIL mixes evidential absence and mismatch; ABSTAIN \(\neq\) MISS | 42% FAIL wrong; FAIL unjustified from \(I\); Dong FN rate |
| Path A WA/VWA FAIL | WA 52 empty / 93 determining of 145 FAIL; VWA 74 / 80 of 154 | same | same families, split | app E | Do not pool with AssistantBench | Single ARB FAIL rate |
| Path A AssistantBench emptiness | 62/115 FAIL empty last send_msg | same | AssistantBench ELIGIBLE FAIL; I-emptiness only | app E | Emptiness, not HIT/MISS | Pooled into 126/299 |
| Path A human FAIL contrast | 4/126 vs 50/173 unan. Successful | `out/human_crosstab.md` | WA+VWA ELIGIBLE FAIL; mostly 1 annotator | app E | Two FAIL kinds not exchangeable vs human | Unjustified-FAIL rate; our discovery of 50/173 |

**Hygiene notes**

- Abstract 10 vs 20 is ALL vs FROZEN sensitivity on 59 R1-positive rows.
- Abstract omits S1 invariance percentages, P4-B 40/30, Cov 0.1667, and Form 0.9333 on purpose. Abstract may mention screenshot S=100 qualitatively; 7/10 stays in §4.
- Dong 15.3% is Dong's number, cited as Dong's, not ours.
- Path A 126 vs 173 is a FAIL-column split, not \(P(\mathrm{ABSTAIN}\mid\mathrm{FAIL})\) as a headline. The 8 SUCCESS∩ABSTAIN cell is **not** in the manuscript (QC overlay; 7 EXTRACTOR_LAG; 1 QC_OPEN unexplained, closed). Path A stopped.
- Path A Table 2 HIT/MISS and NO_GOLD 29 stay in `RESULT.md` only.
- Path A human sensitivity (4/126 vs 50/173 among FAIL) is appendix-only; not CORE; not Table 2 gold.
- VACUOUS_GOLD 14 is in the evidence map but not restated in v0.4 body (20+39+61=120; 120+14=134). Allowed omission.
- GPT P4-C/C2/D descriptive counts are in the map; v0.4 body reports Flash confirmatory gates only. Allowed compression.
- Bean 445 is cited, not restated as a numeral in v0.4 prose.
