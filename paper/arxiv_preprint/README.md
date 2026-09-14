# ArXiv preprint

Named preprint of the counterfactual CUA audit.
Scientific text matches `paper/eiaw_neurips2026_submission/` (EIAW @ NeurIPS 2026, non-archival), without double-blind formatting, line numbers, or the NeurIPS paper checklist.

## Compile

```
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

Upload to arXiv: `main.tex`, `neurips_2026.sty`, `references.bib`, `table_primary.tex`, `figs/score_pairs_primary.png`.
Do not upload the workshop checklist or the anonymous PDF.

## ArXiv form (suggested)

See `arxiv_metadata.txt`.

- **Primary category:** `cs.AI`
- **Cross-list:** `cs.LG`
- **License:** choose at upload (CC-BY 4.0 is typical if you want reuse)
- **Comments:** `Preprint. A version is under review at the Evaluation of Interactive Agents workshop at NeurIPS 2026 (non-archival).`

The workshop is non-archival, so a concurrent arXiv posting is compatible with that CFP.
Do not list this as a NeurIPS *conference* paper.

Author block in the PDF: Vinh Duc Tran, Hanoi University of Science and Technology, `tranducvinh2004@gmail.com`.
Edit `main.tex` if that should change before upload.
