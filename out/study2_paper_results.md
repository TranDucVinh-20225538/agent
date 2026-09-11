# Study 2 results (workshop draft; EXPLORATORY)

Computer-use agents were ranked two ways on the same frozen Study 2 matrix: conventional base-leg rubric \(S^0\) (0–100, on-disk judge, no re-judge) and pair STS / binary track \(Y\) after a locked hat-D extractor (`3242c30`). Valid pairs \(\mathcal{A}\) require G0 and G1 both canonical `DONE`. G2 is ignored. Execution failure is not recoded as \(Y=0\). Ranked roster = {GPT, Flash} because Claude has only one pair. **Layer B is not confirmatory.**

**Coverage.** GPT 32/57 DONE, `|A|=9`. Flash 29/57 DONE, `|A|=8`. Claude 4/57 DONE, `|A|=1` (report only). Flash near-miss dual: as-executed `|A|=8`; treating last-step rescues as rejected → 7. Judge-frame: 0 missing rubrics on DONE.

**Layer A.** \(Y=0\) on every pair in A. \(S^0\) cannot separate \(Y=1\) vs \(Y=0\) because there is no \(Y=1\). Mean \(S^0\) on A is 69.3 (GPT) vs 95.8 (Flash) vs 100 (Claude coverage). High score on A is not evidence of state tracking.

**§6.1(e).** Excluded cells do not enter \(\arg\max\). Mean \(S\) off A is 46.4 / 44.9 / 26.1 (GPT / Flash / Claude). Cells with \(S\ge 90\) and no canonical DONE: 2 / 2 / 1. Unpaired DONE (one leg or G2) can still score high; they stay out of A.

**§6.1(g).** Two supports, both reported:

- Common 4 tasks: mean \(S^0\) Flash−GPT = +46.5, 95% CI \([21.0,\,72.0]\); mean STS Flash−GPT = −0.042, 95% CI \([-0.125,\,0.000]\). \(\arg\max S^0\) = Flash; \(\arg\max\) STS = GPT. **STS strictly prefers GPT on 1 of 4 tasks (`retrieval-f009`, \(\Delta\mathrm{STS}=-0.167\)) and is tied on the other 3** — the earlier "sign disagreement 4/4" counted \(\operatorname{sign}(0)\neq\operatorname{sign}(+)\) as disagreement and is not quoted (manifest §0.16 correction). The \(\arg\max\) flip therefore rests entirely on `retrieval-f009`, which is the same task whose leave-out ties STS (LOPO fragile).
- Each agent’s own A: Flash higher on both \(S^0\) and STS. That **flips** relative to common-4 STS. Neither denominator is selected post hoc.

STS is near the floor and \(Y=0\) everywhere, so the common-4 \(\arg\max\) disagreement is a ranking of small residuals, not a claim that GPT is more reliable than Flash.

Artifacts: `out/study2_layerA.md`, `out/study2_completion_conditional.md`, `out/study2_selection_g.md`, `out/study2_sts_pairs.md`.
