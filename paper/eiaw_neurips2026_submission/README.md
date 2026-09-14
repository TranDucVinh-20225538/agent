# Frozen NeurIPS 2026 workshop submission

**Venue:** Evaluation of Interactive Agents @ NeurIPS 2026 (non-archival, double-blind).  
**Style:** official `neurips_2026.sty` with `[dblblindworkshop]`.  
**OpenReview:** https://openreview.net/group?id=NeurIPS.cc/2026/Workshop/IAEval  
**Deadline:** 29 August 2026 AoE.

Do not edit `main.tex` / `main.pdf` except camera-ready after acceptance.

## CFP / `bjdwqfdkyftc.pdf` (NeurIPS 2026 style) check

Workshop: full paper ≤9 pages **excluding** references and appendices; double-blind; NeurIPS 2026 sty.

| Rule | Status |
|---|---|
| `neurips_2026.sty`, no `final`/`preprint` | yes (`dblblindworkshop`) |
| `\workshoptitle{Evaluation of Interactive Agents}` | yes |
| US Letter, line numbers, Type 1 fonts | yes (612×792, pdffonts Type 1) |
| Anonymous title block | yes |
| Abstract = one paragraph | yes |
| Body ≤ 9 pages excl. refs | body ends ~p.4–5; refs then checklist |
| **NeurIPS Paper Checklist after refs** | **required by the official template PDF** (“desk rejected” if missing). Added; does not count toward the 9-page body limit. |
| No author/affiliation/acks/GitHub | pdftotext clean |


- Title block is NeurIPS anonymous (`Anonymous Author(s)`).
- No author name, affiliation, email, acknowledgments, git SHA, GitHub, or `tracking_evidence.md`.
- `pdftotext` check: Vinh / Hanoi / hust / github.com / b7b4203 absent.

## Length

6 pages total (body well under 9, excluding the spirit of the workshop limit; refs included in the 6-page PDF).

## Compile

```
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

Upload **`main.pdf`** on OpenReview. Authors/affiliations go in the OpenReview form, not in the PDF.
