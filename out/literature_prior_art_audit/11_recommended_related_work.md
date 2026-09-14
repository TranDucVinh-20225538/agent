# Recommended Related Work treatment for Paper 1

Concrete drafting guidance, not final prose — for whoever revises `paper/paper1_counterfactual_cua/main.tex`'s Related Work section (currently §7, citing Xie/Zhou/Koh/Jang/Shao/Turk/Bellibatlu/Pearl per Round 28's build). `turk2026counterfactualclinical` (arXiv:2605.30590) is already in `references.bib` — this audit found it needs a dedicated differentiating paragraph, not just a citation in a list.

## Paragraph 1 — the closest prior art, addressed head-on

Cite and explicitly distinguish Turk (arXiv:2605.30590). Suggested content, not verbatim prose: state that concurrent/prior work in clinical LLM/agent evaluation (Turk, 2026) independently demonstrates that a coverage-based score can rank models in nearly the opposite order from a purpose-built state-responsiveness score under paired, pre-registered case-mutation interventions — the same qualitative phenomenon Paper 1 studies. Then state the two concrete differences precisely: (1) domain — clinical case-file text reasoning vs. computer-use/GUI environment state; (2) construct separation — Turk's tracking measure (CSS) is itself the metric compared against a *different*, baseline-only metric (CMS) via cross-model rank correlation, whereas Paper 1 recomputes the *same* pre-existing benchmark's own score on both legs of each paired run and reports a per-instance delta (S_CF − S_Base), and additionally separates three constructs (completion, tracking, score-sensitivity) rather than two.

## Paragraph 2 — the closest CUA-domain paper, addressed head-on

Cite and distinguish Dong et al. (arXiv:2607.28367, "How Benchmarks Mis-Score Computer-Use Agents") explicitly, given the title's proximity to Paper 1's own framing. State plainly that this paper audits 150 pre-existing, already-recorded FAIL-scored trajectories across five CUA benchmarks and relabels evaluator false negatives (finding 15.3% of FAIL verdicts wrong), whereas Paper 1 runs forward, controlled, paired interventions on a pre-specified determining set of environment state and separately measures ground-truth tracking versus the benchmark's own score sensitivity — a controlled-experiment design rather than a retrospective-audit one.

## Paragraph 3 — the broader "success ≠ what it seems" cluster, grouped briefly

Group and cite together, briefly, without individual deep-dives: Cao, Driouich & Thomas's "corrupt success" (arXiv:2603.03116), Advani's "false success" (arXiv:2606.09863), Lù et al.'s AgentRewardBench (arXiv:2504.08942), and Xue et al.'s Online-Mind2Web/WebJudge (arXiv:2504.01382) — noting that all detect score-unfaithfulness via retrospective analysis of existing trajectories or via judge-accuracy-vs-human-label auditing, not via a forward paired state-intervention design, and none separates state-tracking from score-sensitivity as independently measured constructs.

## Paragraph 4 — metamorphic/counterfactual testing as methodological lineage

Cite classical metamorphic testing (Chen, Cheung & Yiu; Segura et al.'s CSUR survey) and/or CheckList (Ribeiro et al., ACL 2020) as the methodological ancestry for the E0→I→E1 paired-transformation design, and state explicitly that this literature checks only whether an output obeys a known relation under transformation (a single-layer check) — Paper 1 adds a second, independently measured layer (does a held-fixed external score respond to the same transformation), which this literature does not address. This preempts the "isn't this just metamorphic testing?" reviewer question directly (see `06_metamorphic_testing.md`).

## Paragraph 5 (optional, if space allows) — Luo & Peng's AcquaBench

Cite Luo & Peng (arXiv:2607.24054, already a known ancestor to this research program per Round 11 of the project's own history) as a paired, fixed-instruction/UI design with reported score deltas, distinguishing it by manipulated variable: information availability (does the agent have access to correct/incorrect target information mid-trajectory) rather than a determining set of environment/world state, and noting its SHAM condition is constructed to be the wrong ground truth by design rather than an independently verified state change.

## What to avoid in the revised text

- Do not write or imply "we are the first to show a benchmark score can be insensitive to a real state change" — Turk already shows this. Scope the claim to the CUA/GUI domain and the specific three-way separable-construct argument.
- Do not cite Dong et al. or the "corrupt success"/"false success" cluster only as a passing "see also" — given title/topic proximity, a reviewer will read a thin citation as evasive. Each needs its differentiating sentence.
- Do not adopt "false success," "corrupt success," or "counterfactual audit" as Paper 1's own headline phrase without a defining sentence on first use — none is an established cross-adopted term (see `05_terminology_audit.md`), and unqualified reuse risks readers assuming alignment with those specific papers' different definitions.
