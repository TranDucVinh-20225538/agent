# Conceptual map and novelty assessment

## Part 1 — Conceptual map

### A. Benchmark validity
**Solved:** general frameworks exist for asking whether a benchmark measures what it claims to (construct validity — Bean et al. arXiv:2511.04703; Freiesleben & Zezulka arXiv:2510.23191). **Unresolved:** these frameworks are observational/philosophical, not paired-intervention experiments; they diagnose validity problems in prose/survey form, not by manipulating state and measuring a score's response. **Where Paper 1 sits:** provides one concrete, executable instrument (paired counterfactual intervention + score-delta measurement) that operationalizes a construct-validity question for CUA benchmarks specifically.

### B. LLM-as-a-judge reliability
**Solved:** extensively — judge accuracy vs. human labels on fixed trajectories (AgentRewardBench, arXiv:2504.08942), judge stability under prompt paraphrase (JudgeSense, arXiv:2604.23478), judge policy-perturbation sensitivity (Weng et al., arXiv:2605.06161), judge bias/consistency at scale (Norman et al., arXiv:2606.19544). **Unresolved:** none of these test judge/score sensitivity to a *ground-truth environment-state change*, only to surface-level input variation (paraphrase, policy wording) or accuracy against static human relabeling. **Where Paper 1 sits:** treats the judge/score as a black box under test against a real, verified state change, not against wording variation or human relabeling.

### C. Trajectory/process-aware evaluation
**Solved:** decomposing a single trajectory into process-quality dimensions beyond final outcome (AgentProcessBench arXiv:2603.14465, TRAJECT-Bench arXiv:2510.04550, WindowsWorld's S_int/S_final gap, Cao et al.'s procedural-integrity gating arXiv:2603.03116). **Unresolved:** all of these analyze a single execution; none pairs two executions of the same task under a controlled state intervention. **Where Paper 1 sits:** adjacent but orthogonal — process-awareness looks *within* one trajectory; Paper 1 looks *across* a paired pair of trajectories differing only in a determining set of state.

### D. False/corrupt success
**Solved:** naming and measuring the general phenomenon that reported success can mask real failure (Advani's "false success" arXiv:2606.09863; Cao et al.'s "corrupt success" arXiv:2603.03116; Dong et al.'s evaluator-false-negative audit arXiv:2607.28367). **Unresolved:** all detect the gap via retrospective auditing of existing, already-recorded trajectories/verdicts — none via a forward, controlled, paired state intervention. **Where Paper 1 sits:** offers a controlled-experiment alternative to retrospective auditing for the same underlying concern.

### E. Agent reliability under perturbation
**Solved:** measuring aggregate success-rate stability under cosmetic/UI perturbation (Gonzalez-Pumariega et al. arXiv:2604.17849) or environment corruption (AgentHijack arXiv:2605.25707). **Unresolved:** these perturb *presentation* (wallpaper, resolution, pop-ups), not a task-relevant determining set of world state that changes the correct answer; none separately measures ground-truth state-tracking. **Where Paper 1 sits:** the mirror image — perturbs task-relevant state (not presentation) and checks both whether the agent tracks it and whether the score notices.

### F. Metamorphic testing
**Solved:** the single-layer paradigm (transform input, check output obeys a known relation) is decades-old and well-established, including recent LLM/agent adaptations for test-case generation. **Unresolved:** no paper found adds the second layer (a held-fixed external score's sensitivity to the same transformation, checked separately from whether the transformation's own relation is satisfied). **Where Paper 1 sits:** borrows the paired-transformation design, adds the second (score-sensitivity) layer — see `06_metamorphic_testing.md`.

### G. Counterfactual evaluation
**Solved:** paired-intervention designs with fixed instruction/interface exist and have been shown to reveal hidden capability gaps, in clinical LLM/agent QA (Turk, arXiv:2605.30590) and in information-access settings for web/retrieval agents (Luo & Peng's AcquaBench, arXiv:2607.24054). **Unresolved:** neither is in the CUA/GUI domain; neither recomputes a pre-existing third-party benchmark's own score on both legs of the pair and differences it per instance (Turk conflates tracking-metric and compared-metric into a two-way CSS/CMS rank comparison; Luo & Peng manipulate information availability, not world state, and their "SHAM" condition is by construction the wrong ground truth rather than an independent third variable). **Where Paper 1 sits:** applies the same design lineage to a new domain (CUA/GUI world state) with a distinguishing technical choice (external score treated as a black box, recomputed and differenced per instance).

### H. State/evidence grounding
**Solved:** whether an agent's perception/observation modality (screenshots vs. program state) affects grounding accuracy (StateAct, arXiv:2607.22798); whether claimed state changes are evidentially supported (Gao & Zhou's evidence bounds, arXiv:2605.10448). **Unresolved:** neither asks whether an external score is sensitive to a *deliberately manipulated* ground-truth state change. **Where Paper 1 sits:** uses ground-truth state (from guest probes / intervention artifacts) as the tracking oracle, consistent with this literature's general use of ground truth, but applies it inside a paired-intervention design these papers don't use.

## Part 2 — Candidate-contribution novelty test (A–I)

**A. Paired counterfactual intervention of the underlying environment state.**
**PARTIALLY NOVEL.** The design pattern (paired E0/E1 runs under a controlled intervention, instruction/interface held fixed) is established in an adjacent domain (Turk, clinical case data) and a related one (Luo & Peng, information access). Its application to CUA/GUI *environment* state (files, application databases, accessibility-tree-observable facts) was not found elsewhere.

**B. Keeping instruction/UI/rubric/judge fixed while changing only determining state.**
**PARTIALLY NOVEL.** Same reasoning as A — the fixed-everything-else-vary-one-thing design is not new in the abstract (also present in Turk; also the core idea of classical metamorphic testing), but its specific instantiation with a UI/interface held literally fixed (not just an instruction template) for computer-use agents was not found elsewhere.

**C. Separately measuring counterfactual state tracking from benchmark score.**
**NOVEL** in the CUA context; **PARTIALLY NOVEL** relative to the general design-pattern precedent set by Turk. The specific move of treating tracking and score as two genuinely independent measurements — rather than folding them into one bespoke sensitivity metric (as CSS does) or auditing/relabeling the score itself (as Dong et al. and AgentRewardBench do) — was not found instantiated this way anywhere in the literature searched.

**D. Measuring score sensitivity conditional on successful tracking.**
**NOVEL.** No paper found conditions its score-sensitivity measurement on whether tracking succeeded first (i.e., computing/reporting score_delta specifically within the tracked-correctly subset, which is what makes the score-sensitivite vs. Type-A distinction possible). This conditional framing was not found anywhere in the search.

**E. Three-way taxonomy: Type A / score-sensitive / Type B.**
**NOVEL.** No paper found produces this exact three-way classification (tracked+invariant / tracked+score-moves / not-tracked+score-stays-high). Turk's design is fundamentally two-way (CSS vs. CMS, compared across models). Cao et al.'s "corrupt success" is a binary flag, not a three-way taxonomy crossing tracking and score-movement.

**F. Trajectory + guest-state evidence chain: G0 → intervention → G1 → final answer → rubric → ΔS.**
**PARTIALLY NOVEL.** The general pipeline shape (mutate state → observe response → score → compare) is present in Turk's design (mutate case → recommendation → CSS). The specific instantiation with trajectory-based agents, guest-state ground-truth files, and a rubric-based judge producing a scalar that is itself differenced (ΔS) was not found for CUA agents specifically.

**G. Showing the same intervention can produce different classes across agents.**
**UNCLEAR / PARTIALLY NOVEL.** This is a fairly natural corollary once a paired-intervention design is run across multiple models (Turk's paper does report cross-model differences in CSS, though not framed as "same intervention, different taxonomy class per agent"). No paper found frames it explicitly this way, but it is not a large conceptual leap from a multi-model paired-intervention study, so this should be presented as a genuine but modest contribution, not a headline one.

**H. Showing the same agent can exhibit both invariant and score-sensitive behavior.**
**PARTIALLY NOVEL.** Implicit in any paired-intervention study with more than one task (a model's behavior naturally varies by task), and Turk's per-intervention-family breakdown shows something structurally similar (models fail specifically on surgery-status interventions but not others). Not found framed explicitly as "the same agent occupies more than one taxonomy cell," which is Paper 1's specific framing.

**I. Using this to argue that completion, tracking, and score sensitivity are separable.**
**PARTIALLY NOVEL.** The general shape of the argument ("these things can dissociate, therefore a single scalar is an inadequate measurement") is established by Turk in an adjacent domain and echoed in spirit by the entire benchmark-validity/false-success literature. Paper 1's specific three-way (not two-way) separation, demonstrated for CUA agents using an existing benchmark's own score as the object under test, is the part not found elsewhere.

## Bottom line

Nothing in A–I is fully and cleanly NOVEL in the sense of having zero conceptual precedent anywhere. Several items (D, E) were not found instantiated anywhere in the searched literature and can be argued as novel with reasonable confidence. The rest are best described as novel combinations/applications of design patterns and partial claims that already exist individually elsewhere (mostly in Turk 2605.30590), rather than wholly unprecedented ideas. This is a normal and defensible position for a methods paper to be in — the recommended framing (see `01_executive_summary.md` and `11_recommended_related_work.md`) is to claim the specific combination and the CUA-domain instantiation, not the general insight that scores can be blind to state.
