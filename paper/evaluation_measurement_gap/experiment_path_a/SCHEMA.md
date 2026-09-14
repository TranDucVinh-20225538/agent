# AgentRewardBench annotation schema (not a Path A result)

**Source:** Hugging Face `McGill-NLP/agent-reward-bench` file `data/annotations.csv`  
**Fetched:** 2026-09-13  
**sha256:** `5fef3f9f996ec664f5eb371409a708ebac613991d38fa11c9fa6e27a57f3bef9`

Columns: `annotator_name`, `benchmark`, `task_id`, `model_name`, `exp_name`, `trajectory_success`, `trajectory_side_effect`, `trajectory_optimality`, `trajectory_looping`.

| Count | Value |
|---|---|
| Annotation rows | 1408 |
| Unique trajectory keys | 1302 |
| Keys with >1 annotator row | 106 |
| Keys with success-label disagreement | 13 |
| `trajectory_success` | Successful 395 / Unsuccessful 1012 / Unsure 1 |
| Benchmarks (rows) | webarena 501, workarena 475, visualwebarena 300, assistantbench 132 |

These numbers describe the public CSV. They are not published-vs-justified rates. Do not copy them into `draft/main.tex`.

Human `trajectory_success` is a **sensitivity** label (Lù), not primary correspondence gold and not \(V\).
\(V\) is `summary_info.cum_reward` on the released trajectory.
