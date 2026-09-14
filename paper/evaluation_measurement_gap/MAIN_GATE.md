# Main-track gate (lab note, not a paper claim)

**Date:** 2026-09-13  
**Manuscript:** still **one CORE**: M1a + signed repair. Path A licensed sentence is in Discussion + Appendix E (heterogeneous FAIL, 126 vs 173). Not a second CORE.

## Reviewer questions v0.4 did not answer

1. Does this move a number people already cite?
2. Does it happen outside our extractor?
3. What should a new benchmark do differently?

v0.5 answers (3) with the eight-slot table and a local (1) on MyPCBench via \(S=100\) vs discarded gold. Path A answers a slice of (2): on admitted public last-answer/URL FAIL, \(V=0\) mixes empty \(I\) and mismatch. It does **not** transport M1a.

## What is in v0.5

- Compact \(S=100\) table in §4 (7/10 joinable; 9/9 in \(\mathcal{A}\) have \(Y=0\)).
- P1/P2 out of the body (Appendix A–B only).
- One sentence fencing failure-attribution literature (Who&When): we audit \(I\), not which agent step failed.

## What is not in v0.5

Path A 126 vs 173 is in the PDF. Dong 15.3% remains Dong's. 498/804 admission counts are not manuscript prevalence. Eight SUCCESS∩ABSTAIN are not in the PDF.

## Ordered work

| Track | Status | Role |
|---|---|---|
| Path A | **STOPPED.** Licensed 126 vs 173; `webarena.723` QC_OPEN unexplained, closed | Discussion/Appendix only; does not carry main alone |
| Path A human join | **DONE.** 4/126 vs 50/173 Successful among FAIL; empty \(I\) is not the hidden-success cell | Appendix sensitivity; not CORE; not 50/173 as our discovery |
| Path B | **B1 DONE.** 10/1790 T=3 cap-hits, all Operator. B2 sample frozen (30 ep / 1065 items); **blocked on screenshots + humans** | Not in the PDF until B2 gold exists; never use WebJudge Score as gold; B1 ≠ M1a transport |
| Path UV | **OPEN.** CUAVerifierBench screenshots public; R not released. U1 = n>K upper bound only | Not M1a transport; U2 needs UV re-run (`U_RERUN.md`) + humans; do not use `uv_*` as gold |
| Path C | Cards drafted, UNCERTAIN blanks | Findings/D&B practice; not a main contribution alone |

Path A is done and stopped. Heterogeneous FAIL is a Discussion/Appendix paragraph; it does not carry NeurIPS/ICLR main by itself. v0.5 + Path A is still a narrow increment. TMLR / NeurIPS D&B / ACL Findings remain the honest venue if no further public-\(I\) or cited-number work lands.

## Hard locks (unchanged)

Do not: add MyPCBench cells; ship a new metric; amp P4-D distractors; run extractor `3242c30` on public \(\tau\); rewrite `STOP-NO-CORPUS` as “benches are not measurement-ready”; thicken \(\mathcal{M}(\tau,I)\); treat Who&When/TRAIL/AgentProcessBench as Path A corpora.
