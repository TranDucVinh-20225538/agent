# Cross-instrument structural comparison (no E2 counts)

**Status:** Structural only. No eligible corpus; no E2 frequencies.  
**Not a ranking of instruments. Not a score comparison.**

| Property | MyPCBench P3 (frozen) | External candidates (this audit) |
|---|---|---|
| Trajectory | Yes (MyPCBench legs) | Often yes (OSWorld dumps, AgentRewardBench, CUAVerifierBench, WebJudge *judge products*) |
| Reference | Independent guest gold / determining set | Task JSON expected answers / DB diffs / human *task-level* labels |
| Intermediate R | `found` accumulator of typed spans | WebArena: last answer string (no accumulator). WAV: normalized JSON. OSWorld: getter state. WebJudge: per-screenshot Score list (released). UV: relevance matrix **not released**. τ-bench: per-output `found` flags |
| Discard stage | Fail-closed aggregation over `found` | WebJudge: threshold + `MAX_IMAGE=50`. UV: top-K (code; R not in HF columns). Others: conjunction / equality / assertion — not A(R) drop of collected gold |
| Post-collection discard (E2) | Yes — P3 M1a (13/39 misses) | **Not established** under the eligibility contract |
| Final verdict | MATCH / miss / absent at row grain | Benchmark 0/1, judge success, UV scalar |
| Evidence loss analogue | M1a | None admitted |

Closest *shape* (collect then filter): WebJudge and Universal Verifier.  
Closest *independence of gold*: WebArena/WAV/OSWorld/AppWorld/τ-bench task specs.  
No candidate jointly has both.
