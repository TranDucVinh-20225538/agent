# Rubric mechanism notes

Per-criterion `per_rubric_max` arrays for cells whose score behavior is otherwise unexplained by the tracking classification alone. Source: `rubric_result.json` in each run directory.

| Model | Task | Condition | Score | per_rubric_max |
|---|---|---|---:|---|
| Claude | retrieval-f003 | base | 65 | [1, 1, 0] |
| Claude | retrieval-f003 | cf | 65 | [1, 1, 0] |
| GPT | aggregation-f003 | base | 50 | [1, 1, 0, 0] |
| GPT | aggregation-f003 | cf | 50 | [1, 1, 0, 0] |
| Qwen3.5-9B | aggregation-f003 | base | 50 | [1, 1, 0, 0] |
| Qwen3.5-9B | aggregation-f003 | cf | 80 | [1, 1, 1, 0] |
| Qwen3.8-Flash | aggregation-f003 | base | 80 | [1, 1, 1, 0] |
| Qwen3.8-Flash | aggregation-f003 | cf | 100 | [1, 1, 1, 1] |
| GPT | retrieval-f029 | base | 33 | [1, 0, 0] |
| GPT | retrieval-f029 | cf | 100 | [1, 1, 1] |
| Qwen3.5-9B | retrieval-f016 | base | 100 | [1, 1, 1, 1] |
| Qwen3.5-9B | retrieval-f016 | cf | 100 | [1, 1, 1, 1] |
| Claude | preference_inference-f018 | base | 100 | [1, 1, 1, 1, 1, 1] |
| Claude | preference_inference-f018 | cf | 100 | [1, 1, 1, 1, 1, 1] |

## Reading

- **GPT `aggregation-f003`**: `[1,1,0,0]` in both conditions -- the two criteria that move with the combined-refund figure are satisfied both times (Type A here is not a rubric-blindness artifact on those two items specifically); the other two criteria (a year-count/format check) are never satisfied, in either condition, so they contribute nothing to the base->CF comparison.
- **Qwen3.5-9B `aggregation-f003`**: `[1,1,0,0]`->`[1,1,1,0]` -- one additional criterion is satisfied only under CF. Score-sensitivity here traces to a single rubric item, not a wholesale change in competence.
- **Qwen3.8-Flash `aggregation-f003`**: `[1,1,1,0]`->`[1,1,1,1]` -- same pattern, one additional item.
- **Claude `retrieval-f003`**: `[1,1,0]` in both conditions -- a fixed third criterion is never satisfied in either condition; irrelevant to the base/CF contrast, but explains the non-100 score under a fully-tracked, fully-invariant pair.
- **GPT `retrieval-f029`**: `[1,0,0]`->`[1,1,1]` -- the wage-figure criterion (index 0) is satisfied in *both* conditions; the two criteria that move are unrelated to the manipulated field itself, so the large score swing (33->100) is not evidence about D-tracking.
- **Qwen3.5-9B `retrieval-f016`**: `[1,1,1,1]` in both conditions (100/100) despite the base answer reporting an incorrect total cost basis ($8,788.75 vs. true $8,213.25). The rubric evidently does not check the reported grand total against the gold value at the precision this would require -- a concrete instance of rubric insensitivity to the exact manipulated figure, not an aggregation-masking or task-structure explanation.

No case in this audit required an aggregation-masking or task-structure explanation beyond what is stated above; where the mechanism is unclear from the available criteria it is reported as such rather than guessed.
