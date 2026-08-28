# Phase B.1 intervention validation

Written 2026-08-28T05:45:59.259733+00:00.
Dummy guest. No agent. Frozen I. Snapshot restored between tasks.

**10/10 interventions validated.**

| task_id | ok | gold_moved | fails |
| --- | --- | --- | --- |
| `retrieval-f001` | True | True |  |
| `retrieval-f003` | True | True |  |
| `retrieval-f016` | True | True |  |
| `retrieval-f029` | True | True |  |
| `retrieval-f030` | True | False |  |
| `aggregation-f003` | True | True |  |
| `aggregation-f018` | True | True |  |
| `preference_inference-f004` | True | True |  |
| `preference_inference-f018` | True | True |  |
| `counterfactual-f004` | True | True |  |

`retrieval-f030` `gold_moved=False` is the registered Type B check: the 1099 probe must not move; charitable moves in the extra probe.

B.2 (Claude / GPT / Qwen 35B × the six unrun tasks) may start. Do not rewrite I. Reuse Stage 4 cells for the four already-run IDs.
