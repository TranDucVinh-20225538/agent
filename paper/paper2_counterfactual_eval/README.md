# Paper 2 — counterfactual evaluation (decision experiment)

**Status:** Analysis universe frozen (`out/paper2_analysis_universe.md`);
execution manifest in `EXECUTION_MANIFEST.md`. Paper 1 left as-is.

**Owns:** claim (1) — does \(\arg\max \overline{S}\) equal \(\arg\max\) STS on
a confirmatory universe? **Does not own:** claim (2) mid-episode stale
revision (STALE-like). Details: `PAPER2_SPEC.md` §0.

| Doc | What |
|---|---|
| `PAPER2_SPEC.md` | Hypothesis, inclusion, STS, disagreement, claim boundary §0 |
| `DESIGN.md` | Measurement object, matching, anti-goals |
| `EXECUTION_MANIFEST.md` | Harness / seed / API lanes before cell 1 |
| `protocol/` | Executable matching + STS |
| `registry/` | Sealed \(\mathcal{M}\)/\(\mathcal{T}\), semantic \(D\) |

```
python3 -m unittest discover -s paper/paper2_counterfactual_eval/protocol -q
python3 paper/paper2_counterfactual_eval/protocol/replay_paper1.py
```

Replay writes `out/paper1_sts_replay.csv` (24 pairs, no new agent runs).
