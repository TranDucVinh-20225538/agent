# Size ablation (Qwen3.5-9B)

Not pooled into primary P1.

| Agent/model | Task | Base gold | CF gold | Base score | CF score | Tracking | Valid pair | Dissociation | Interpretation |
|---|---|---|---|---|---|---|---|---|---|
| Qwen3.5-9B | aggregation-f003 | n_filed=2 combined=4871.70 | n_filed=2 combined=400.00 | 50 | 80 | yes | yes | no | Tracked the state change; conventional score moved (score-sensitive). |
| Qwen3.5-9B | retrieval-f001 | Gold Voyager / 38450 | Silver Voyager / 8620 | 80 | 80 | yes | yes | yes | Tracked the state change; conventional score unchanged (dissociation). |
