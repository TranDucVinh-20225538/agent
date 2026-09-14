# Metamorphic testing: is it prior art for our intervention protocol?

## Short answer

Partially, as intellectual ancestry for the E0 → I → E1 paired-run design; not as prior art for the specific two-layer measurement (state-tracking correctness AND separate score-sensitivity to the same transition). No paper found — classical or LLM/agent-specific — checks both layers together.

## What classical metamorphic testing (MT) actually checks

Chen, Cheung & Yiu's original formulation (1998 tech report, republished arXiv:2002.12543) and the standard survey (Segura et al., ACM Computing Surveys 51(1), 2018) define a metamorphic relation (MR): given a source input/output pair, generate a follow-up input via a known transformation, and check that the *expected relation* holds between the two outputs (the canonical example: sin(x) = sin(π−x)). This is a **single-layer** check — the MR itself is the correctness oracle. There is no second, independently held-fixed scorer whose sensitivity to the same transformation is separately tested.

CheckList (Ribeiro, Wu, Guestrin & Singh, ACL 2020) applies the same single-layer logic to NLP models: INV (invariance) tests expect the output not to change under a meaning-preserving perturbation (paraphrase, typo, name swap); DIR (directional) tests expect a specific, known-direction change. Both operate on **input text**, not environment/world state, and again there is no second external score under test — the INV/DIR expectation itself is the test.

## What our protocol adds relative to classical MT

Paper 1's design can be described in MT vocabulary as: the metamorphic relation is "if the determining set D changes in a controlled way, the agent's state-dependent answer should change correspondingly" — this much is a fairly direct instance of a metamorphic/counterfactual relation applied to agent behavior, and should be cited as such (see `11_recommended_related_work.md`). The genuinely additional move is evaluating **two** things under the same intervention, not one:

1. Whether the agent's response satisfies the expected state-transition relation (the classical MT check — does the output obey the relation).
2. Whether an **external, held-fixed benchmark score/judge**, whose job it is to grade the agent's response, is itself sensitive to that same transition.

No metamorphic-testing paper found — classical, ML/DL-focused, or LLM-agent-focused — does (2) as a separate, explicitly measured axis alongside (1). The overwhelming pattern in the literature searched is that the metamorphic relation (or the counterfactual ground-truth-tracking check) *is* the sole correctness criterion; papers that also have an external "benchmark score" in the picture (Turk 2605.30590 being the closest) either fold the two into one metric (Turk's CSS is itself the tracking check) or don't recompute the external score under the intervened condition at all.

## Recent MT-adjacent work checked

- **Metamorphic testing of deep code models** (ACM TOSEM survey, 2026) and **AutoMT** (arXiv:2510.19438, autonomous-driving MT via LLM agents) — LLM agents are used here to *generate* metamorphic test cases for other software systems; the agents are the testing tool, not the system under test. Not relevant as prior art for Paper 1's design.
- **Gonzalez-Pumariega et al., "On the Reliability of Computer Use Agents"** (arXiv:2604.17849) — closest CUA-domain analogue to a metamorphic/consistency-testing framing: repeats OSWorld tasks under cosmetic environment perturbations (wallpaper, cursor size, dock position, timezone) and compares pass^k via McNemar/Wilcoxon tests. This is a consistency/robustness check (does success rate stay flat under a perturbation that should be irrelevant), the mirror image of Paper 1's design (Paper 1 perturbs a *relevant* determining set and checks whether the score *should* move but doesn't, or moves when it shouldn't be the deciding factor). No ground-truth state-tracking measurement, no separate score-sensitivity axis distinct from aggregate pass rate.
- **Weng, Feng & Xie, "Policy Invariance as a Reliability Test for LLM Safety Judges"** (arXiv:2605.06161) — the closest MT-flavored paper to a "does a held-fixed judge respond correctly to a controlled perturbation" design, but the perturbation is on the **judge's own policy/rubric text**, not on environment state, and there is no agent producing a trajectory under test at all — it is a pure judge-stability study.
- **Kaushik, Hovy & Lipton, "Counterfactually-Augmented Data"** (ICLR 2020, arXiv:1909.12434) — human-edited minimal-pair text used to test/train robustness of NLP classifiers; single-layer (does the prediction flip correctly), no environment state, no held-fixed external score.

## Verdict

Metamorphic/counterfactual testing is legitimate prior art for the *shape* of Paper 1's intervention design (paired original/transformed inputs with an expected relation) and should be cited in Related Work as the methodological lineage. It is not prior art for the specific contribution — the two-layer measurement that separately scores state-tracking correctness and the sensitivity of an independent, pre-existing benchmark's own score to the same transition, applied to computer-use agents. This distinction should be stated explicitly and precisely in Paper 1's Related Work rather than left implicit, since a reviewer familiar with metamorphic testing will otherwise reasonably ask "isn't this just metamorphic testing?" — the answer is "the E0/E1 pairing borrows from metamorphic/counterfactual testing; the score-sensitivity layer on top of it does not appear to be covered by that literature."
