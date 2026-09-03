# Paper 2 — design freeze (no runs)

**Status:** Phase 1–2 only. Paper 1 is frozen. Do not run agents, APIs, QEMU, or OpenRouter.

**Object:** a measurement protocol for the three variables Paper 1 separated
(completion ≠ tracking ≠ score sensitivity), plus a graded State Tracking Score
(STS) with an explicit gold-matching protocol.

**Not this paper:** a new OSWorld-scale harness, cross-harness baselines, or
“30–50 more tasks” as a KPI.

| Doc | What |
|---|---|
| `DESIGN.md` | Measurement object, matching, anti-goals |
| `PAPER2_SPEC.md` | Decision experiment: hypothesis, inclusion, STS, disagreement |
| `protocol/` | Executable matching + STS |
| `registry/paper1_replay.json` | Paper 1 \(D\) replay, not confirmatory \(\mathcal{T}\) |

```
python3 -m unittest discover -s paper/paper2_counterfactual_eval/protocol -q
python3 paper/paper2_counterfactual_eval/protocol/replay_paper1.py
```

Replay writes `out/paper1_sts_replay.csv` (24 pairs, no new agent runs).
