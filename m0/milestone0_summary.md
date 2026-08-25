# Milestone 0 scan - MyPCBench

Tasks: 184. Seeded values in variables.json: 213.
Tasks quoting at least one seeded value: 103.

## Rubric class

| class | n | meaning for a counterfactual |
| --- | --- | --- |
| pinned | 53 | rubric quotes the current value, must be rewritten with the seed |
| seed_relative | 42 | rubric names the seed as source, survives the change, judge recomputes |
| mixed | 63 | both kinds of criteria in one task |
| procedural_only | 18 | only checks interaction, a personal counterfactual changes nothing |
| unclear | 8 | needs hand reading |

## Category x rubric class

| category | n | pinned | seed_relative | mixed | procedural_only | unclear |
| --- | --- | --- | --- | --- | --- | --- |
| long_horizon | 57 | 21 | 10 | 18 | 8 | 0 |
| situated_action | 54 | 21 | 9 | 19 | 4 | 1 |
| aggregation | 20 | 5 | 4 | 6 | 1 | 4 |
| contradiction | 16 | 0 | 5 | 6 | 3 | 2 |
| retrieval | 14 | 4 | 5 | 5 | 0 | 0 |
| preference_inference | 11 | 0 | 8 | 3 | 0 | 0 |
| counterfactual | 9 | 1 | 1 | 5 | 1 | 1 |
| cua_only | 2 | 0 | 0 | 1 | 1 | 0 |
| hard_app | 1 | 1 | 0 | 0 | 0 | 0 |
