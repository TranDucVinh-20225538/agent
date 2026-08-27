# Primary P1 (Claude, GPT, Qwen3.5-35B-A3B)

Only valid DONE pairs enter tracking/invariance. Qwen3.5-35B-A3B × f003 is listed as invalid.

| Agent/model | Task | Base gold | CF gold | Base score | CF score | Tracking | Valid pair | Dissociation | Interpretation |
|---|---|---|---|---|---|---|---|---|---|
| Claude | aggregation-f003 | n_filed=2 combined=4871.70 | n_filed=2 combined=400.00 | 80 | 80 | yes | yes | yes | Tracked the state change; conventional score unchanged (dissociation). |
| Claude | retrieval-f001 | Gold Voyager / 38450 | Silver Voyager / 8620 | 100 | 100 | yes | yes | yes | Tracked the state change; conventional score unchanged (dissociation). |
| GPT | aggregation-f003 | n_filed=2 combined=4871.70 | n_filed=2 combined=400.00 | 50 | 50 | yes | yes | yes | Tracked the state change; conventional score unchanged (dissociation). |
| GPT | retrieval-f001 | Gold Voyager / 38450 | Silver Voyager / 8620 | 100 | 100 | yes | yes | yes | Tracked the state change; conventional score unchanged (dissociation). |
| Qwen3.5-35B-A3B | aggregation-f003 | n_filed=2 combined=4871.70 | n_filed=2 combined=400.00 | 75 | 0 | n/a | no | n/a | Excluded: no valid CF cell (execution failure). Not semantic non-tracking. |
| Qwen3.5-35B-A3B | retrieval-f001 | Gold Voyager / 38450 | Silver Voyager / 8620 | 100 | 100 | yes | yes | yes | Tracked the state change; conventional score unchanged (dissociation). |
