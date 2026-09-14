# Search strategy

## Method

Five parallel search agents were run, each with WebSearch + WebFetch, instructed adversarially ("try to kill the novelty claim," never fabricate a citation, verify every paper via a real fetch of the abstract/HTML/PDF rather than from training memory). After the parallel sweep, the two most decision-relevant papers (Turk 2605.30590 and Dong et al. 2607.28367) were independently re-fetched a second time by the orchestrating session directly — not just trusted from the subagent report — because the novelty verdict hinges on them. This mirrors the standing discipline used throughout this research program (Rounds 1–31 of `claude/decision-objects-audit-2026-08.md`): never repeat a claim that hasn't been independently checked.

## The five clusters

1. **Priority named papers** — arXiv:2607.28367, "Beyond Task Completion... Corrupt Success," ReliabilityBench, AgentHorizon, LLM-agent evaluation surveys, trajectory/process-aware evaluation, LLM-as-judge reliability.
2. **CUA/agent benchmark landscape** — OSWorld/OSWorld-Verified, WebArena, BrowserGym, WorkArena, Online-Mind2Web, VisualWebArena, AssistantBench, τ-bench, AppWorld, GAIA, MyPCBench, WeaveBench, plus any other CUA/desktop benchmark surfaced organically. For each: what counts as success, what the judge observes, whether state is perturbed, whether score can stay flat under a state change.
3. **Metamorphic / counterfactual / perturbation testing** — classical metamorphic testing origins and surveys, MT for ML/DL/LLM agents, counterfactual evaluation of NLP/ML systems and of agents specifically, perturbation-based robustness evaluation.
4. **Reward hacking / Goodhart / benchmark validity** — specification gaming, benchmark/metric gaming, reward misspecification, Goodhart's law in ML, proxy metric failure, construct validity, measurement validity in ML/NLP evaluation.
5. **False success / judge reliability / process-aware terminology** — direct term search for candidate names ("false success," "silent failure," "corrupt success," "evaluator blindness," "judge blindness," "state grounding," "state-score dissociation," "counterfactual audit," etc.), classifying each as ESTABLISHED / ONE-OFF / NOT FOUND.

## Verification standard applied

- A citation is reported only if a real URL (arXiv abstract/HTML/PDF, ACL Anthology, OpenReview, official project page, or conference proceedings page) was actually opened by WebFetch or returned as a live search result — not recalled from training data.
- Similarity levels (0–3, defined in `09_novelty_assessment.md`'s companion matrix files) were assigned per-paper based on what the paper's own abstract/method section actually describes, not on title-keyword overlap alone. Several titles with strong keyword overlap ("AgentHorizon"-adjacent names, "state grounding," "environment corruptions") turned out on inspection to address a different mechanism and were downgraded accordingly (see `04_prior_art_matrix.md`).
- Two papers (Turk 2605.30590, Dong et al. 2607.28367) were re-fetched a second, independent time directly by the orchestrating session, including pulling the full HTML body text of Turk's paper to resolve the single most load-bearing technical question: whether its coverage metric is recomputed on intervened cases. Confirmed directly: it is not (see `08_direct_prior_art.md`).
- "AgentHorizon," one of the four named priority artifacts, could not be verified as a real paper or benchmark under that exact name after real searching. Distinct, differently-named artifacts were found (UltraHorizon, the HORIZON Leaderboard, AgentLAB) but none matches "AgentHorizon." Reported as NOT FOUND rather than substituted silently.

## Known limitations of this audit

- Coverage is bounded by what a live web search surfaces in August 2026; a paper published in the days immediately before this audit, or one indexed only on a venue site not covered by search, could be missed.
- A small number of papers surfaced by title/abstract only were not deep-read in full (flagged individually in `04_prior_art_matrix.md` and the cluster reports where this applies) — they are reported as lower-confidence, not silently upgraded to a firm Level rating.
- This audit does not re-derive or re-run any of the cited papers' own experiments; classifications rest on what each paper's own text states about its method.
