# Paper 2 — NeurIPS 2026 workshop submission (frozen)

**Venue:** Evaluation of Interactive Agents @ NeurIPS 2026 (non-archival, double-blind).
**Style:** official `neurips_2026.sty` with `[dblblindworkshop]`, copied unmodified from the Paper 1 submission.

Paper 1 lives in `paper/eiaw_neurips2026_submission/` and is frozen. It is a **different
submission**; do not edit it, and do not merge the two `main.tex` files.

Do not edit `main.tex` / `checklist.tex` / `main.pdf` except camera-ready after acceptance.

## Provenance of every number

Prose was transferred from a frozen analysis package. No experiment was run, no cell was
re-judged, no archive was touched, and the state-tracking extractor was not retuned, for
this write-up.

| Claim in paper | Source artifact |
|---|---|
| Coverage, DONE rates, `\|A\|` (Table 1) | `out/study2_completion_conditional.md` §(i) |
| Mean `S⁰` and mean STS on each agent's `A`, `Y=0` everywhere | `out/study2_layerA.md` |
| Common-4 means, ΔS⁰ / ΔSTS + bootstrap CIs, LOPO | `out/study2_selection_g.md` |
| Per-task values (Table 2) | `out/study2_selection_g_sts.md` / `.csv` |
| Mean `S` off `A` (46.4 / 44.9 / 26.1), `S≥90` non-DONE (2 / 2 / 1) | `out/study2_completion_conditional.md` §(i) |
| Near-miss dual: Flash `\|A\|` 8 as-executed vs 7 rescue-as-rejected | `out/study2_gate011_nearmiss_dual.md` (§0.11) |
| Judge/terminal channel independence, fail-closed extractor | `EXECUTION_MANIFEST.md` §§0.12, 0.17 |
| Pre-registered rules cited in text (`n_min=3`, §6.1(c)/(e)/(g), no optional stopping) | `PAPER2_SPEC.md` §6.1 |

Two framings are **deliberately excluded** and must not be reintroduced:

- the raw "4/4 sign disagreement" count, which treats `sign(0) ≠ sign(+)` as a disagreement
  (see `EXECUTION_MANIFEST.md` §0.16 correction). The paper reports 1 strict / 3 tied.
- Claude's `S⁰ = 100` as a standalone number. It always carries `n = 1`.

ΔSTS interval notation follows the locked convention: prose and tables use
`ΔSTS = −0.042, 95% CI [−0.125, 0.000]`; two-decimal tables would use `[−0.13, 0.00]`.

## CFP check

Workshop: full paper ≤9 pages **excluding** references and appendices; double-blind; NeurIPS 2026 sty.

| Rule | Status |
|---|---|
| `neurips_2026.sty`, no `final`/`preprint` | yes (`dblblindworkshop`) |
| `\workshoptitle{Evaluation of Interactive Agents}` | yes |
| US Letter, line numbers, Type 1 fonts | yes (612×792; `pdffonts` → all Type 1) |
| Anonymous title block | yes (`Anonymous Author(s)`, identical to Paper 1) |
| Abstract = one paragraph | yes |
| Body ≤ 9 pages excl. refs | **body ends p.5**; References p.6; checklist p.7–14 |
| NeurIPS Paper Checklist after refs | yes — required by the template ("desk rejected" if missing); does not count toward the body limit |
| No author/affiliation/acks/commit SHA | `pdftotext` scan clean |

Anonymity scan covered author names, institution, city, email, GitHub, OpenReview, host
paths, cluster identifiers, and 7–40 char hex tokens. The only hex-like token in the PDF is
`20260904`, which is the bootstrap seed, not a commit hash. There is no acknowledgments
section.

## Length and figures

14 pages total: ~5 pages body, references, then the 8-page checklist.

`figs/` is intentionally empty. The common support has four tasks, and Table 2 shows all
four per-task values directly; a scatter of four points would carry less information than
the table it replaced.

## Compile

```
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

Last clean build: 0 errors, 0 undefined citations, 0 undefined references, 0 overfull boxes.

Upload **`main.pdf`** on OpenReview. Authors/affiliations go in the OpenReview form, not in the PDF.
