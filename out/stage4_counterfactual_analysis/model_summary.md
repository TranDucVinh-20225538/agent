# Primary P1

Valid pairs are restricted to frozen f001/f003. Execution failures are excluded from tracking and invariance denominators.

## Claude

- aggregation-f003: valid_pair=True; tracking_pair=True; scores 80→80; gold n_filed=2 combined=4871.70 → n_filed=2 combined=400.00; dissociation=True. 
- retrieval-f001: valid_pair=True; tracking_pair=True; scores 100→100; gold Gold Voyager / 38450 → Silver Voyager / 8620; dissociation=True. 

## GPT

- aggregation-f003: valid_pair=True; tracking_pair=True; scores 50→50; gold n_filed=2 combined=4871.70 → n_filed=2 combined=400.00; dissociation=True. 
- retrieval-f001: valid_pair=True; tracking_pair=True; scores 100→100; gold Gold Voyager / 38450 → Silver Voyager / 8620; dissociation=True. 

## Qwen3.5-35B-A3B

- aggregation-f003: valid_pair=False; tracking_pair=False; scores 75→0; gold n_filed=2 combined=4871.70 → n_filed=2 combined=400.00; dissociation=False. NO valid pair: all three CF attempts failed/incomplete; excluded from all semantic denominators
- retrieval-f001: valid_pair=True; tracking_pair=True; scores 100→100; gold Gold Voyager / 38450 → Silver Voyager / 8620; dissociation=True. 

Primary invariance among tracking-valid pairs: 5/5 (Clopper–Pearson 95% CI [0.478, 1.000]). Qwen3.5-35B-A3B contributes only the f001 pair.

# Size Ablation

Not pooled into primary P1.

## Qwen3.5-9B

- aggregation-f003: valid_pair=True; tracking_pair=True; scores 50→80; gold n_filed=2 combined=4871.70 → n_filed=2 combined=400.00; dissociation=False. 
- retrieval-f001: valid_pair=True; tracking_pair=True; scores 80→80; gold Gold Voyager / 38450 → Silver Voyager / 8620; dissociation=True. 

Invariance | tracking-valid: 1/2 (95% CI [0.013, 0.987]).

# Exploratory

Not pooled into primary P1. Does not replace Qwen3.5-35B-A3B.

## Qwen3.8-Flash

- aggregation-f003: valid_pair=True; tracking_pair=True; scores 80→100; gold n_filed=2 combined=4871.70 → n_filed=2 combined=400.00; dissociation=False. 
- retrieval-f001: valid_pair=True; tracking_pair=True; scores 100→100; gold Gold Voyager / 38450 → Silver Voyager / 8620; dissociation=True. 

Invariance | tracking-valid: 1/2 (95% CI [0.013, 0.987]).
