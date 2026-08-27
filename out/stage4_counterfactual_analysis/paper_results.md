# Results (Stage 4 paired CUA)

We distinguish three outcomes: (i) whether a cell is a valid DONE trajectory with verified guest state, (ii) whether the agent's final report tracks that state (counterfactual state tracking), and (iii) whether the conventional rubric score is invariant when tracking succeeds.

**Primary P1** (Claude, GPT, Qwen3.5-35B-A3B; frozen retrieval-f001 and aggregation-f003). There are 5 valid paired episodes. Qwen3.5-35B-A3B × f003 has no valid counterfactual: three CF attempts fail as execution (80-step TOOL_CALL loop; one-step stop; reCAPTCHA terminate/FAIL) and are excluded from tracking and invariance denominators. They are not semantic non-tracking. Across the 5 tracking-valid pairs, 5 are score-invariant and 0 are score-sensitive (invariance rate 5/5; Clopper–Pearson 95% CI [0.478, 1.000]). All 5 tracking-valid invariant pairs are dissociation events: the agent reported the manipulated world state while the 0–100 task score was unchanged. Exact paired scores: Claude f001 100→100, Claude f003 80→80, GPT f001 100→100, GPT f003 50→50, Qwen3.5-35B-A3B f001 100→100.

Successful completion and counterfactual state sensitivity are separable properties. In valid paired episodes, agents could track substantial changes in the underlying task state while retaining the same conventional task score.

**Size ablation** (Qwen3.5-9B; not in primary P1). Both f001 and f003 pairs are valid and tracking-valid. Scores: f001 80→80 (invariant); f003 50→80 (score-sensitive). Invariance among tracking-valid pairs: 1/2 (95% CI [0.013, 0.987]).

**Exploratory** (Qwen3.8-Flash; not in primary P1; does not replace Qwen3.5-35B-A3B). Both pairs are valid and tracking-valid. Scores: f001 100→100 (invariant); f003 80→100 (score-sensitive). Invariance among tracking-valid pairs: 1/2 (95% CI [0.013, 0.987]).

These counts are descriptive. The sample is small; we do not claim that all computer-use agents behave this way, nor do we treat execution failure as evidence about state tracking.
