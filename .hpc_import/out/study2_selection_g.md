# §6.1(g) exploratory selection (Study 2 CLOSED)

**Label: EXPLORATORY. Layer B is NOT confirmatory** (§6.1(c): ranked roster is GPT + Flash only; Claude `|A|=1` coverage, not ranked). \(n_{\min}=3\) unchanged. G2 ignored. Non-DONE is not \(Y=0\). Hat-D extractor frozen at `3242c30`; no retune after STS.

Two analysis sets are reported. Neither is chosen because it “looks better.”

| Set | Definition | Use |
|---|---|---|
| \(\mathcal{A}_i\) (agent A) | that agent’s valid G0∧G1 pairs | Layer A; each agent’s own mean S / STS |
| \(\mathcal{A}_\cap\) (common 4) | tasks in both GPT A and Flash A | paired ΔS / ΔSTS, bootstrap, LOPO, sign table |

Common 4: `counterfactual-f010`, `preference_inference-f014`, `retrieval-f002`, `retrieval-f009`.

## Common-4 paired comparison

| | GPT | Flash |
|---|---:|---:|
| mean \(S^0\) | 49.5 | **96.0** → \(\arg\max S^0\) **Flash** |
| mean pair-STS | **0.250** | 0.208 → \(\arg\max\) STS **GPT** |
| \(Y\) (binary track) | 0/4 | 0/4 |

- \(\operatorname{sign}(\Delta S^0)\neq\operatorname{sign}(\Delta\mathrm{STS})\) on **4/4** tasks (\(\Delta=\) Flash−GPT).
- Paired bootstrap (seed 20260904, 5000): mean(\(S^0_\mathrm{Flash}-S^0_\mathrm{GPT}\)) = **+46.5** (95% CI 21.0–72.0); mean(\(\mathrm{STS}_\mathrm{Flash}-\mathrm{STS}_\mathrm{GPT}\)) = **−0.042** (95% CI −0.125–0.0).
- **LOPO fragile:** leave-out `retrieval-f009` → \(\arg\max\) STS = tie; other three leave-outs keep Flash on \(S^0\) and GPT on STS.

Per-task: `out/study2_selection_g_sts.csv`.

## Agent-A means (not the same task mix)

| | GPT \(\mathcal{A}\) (n=9) | Flash \(\mathcal{A}\) (n=8) |
|---|---:|---:|
| mean \(S^0\) | 69.333 | 95.750 |
| mean pair-STS | 0.130 | 0.229 |
| \(Y=1\) | 0/9 | 0/8 |

On **full A**, Flash is higher on both \(S^0\) and STS. On **common 4**, Flash is higher on \(S^0\) and GPT is higher on STS. That is a **support flip**, not a reason to pick one denominator.

Claude (not ranked): `|A|=1` (`counterfactual-f013`), \(S^0=100\), STS=0, \(Y=0\).

## Y=0 caveat (Layer A)

Binary track \(Y=0\) on **all** of A. STS sits near the floor. \(\arg\max\) STS on four tasks is a ranking of small residuals, not of agents that tracked. Layer A calibration of \(S^0\) vs \(P(Y=1)\) is **degenerate** (`out/study2_layerA.md`). Do not read this as “GPT is more reliable than Flash.”

## Pointers (already frozen; not redone)

- §0.11 near-miss dual (no rescoring): `out/study2_gate011_nearmiss_dual.md` — Flash as-executed `|A|=8`; rescue-as-rejected `|A|=7`. GPT/Claude parser-not-applied.
- §0.12 judge-frame: `out/study2_judge_frame_audit.md` — 0 missing `rubric_result.json` on VALID_DONE.
- §6.1(e) completion-conditional: `out/study2_completion_conditional.md` — excluded cells do not enter \(\arg\max\).
