# P4-M external validation — Phase 6 consistency / replication audit

**Status:** N/A on a result table (none exists). Protocol checks below apply to this overnight pass.

| Check | Result |
|---|---|
| Every HIT has independent \(L\) | N/A — no HIT assigned |
| Every MISS has independent \(L\) | N/A — no MISS assigned |
| No HIT/MISS on NONDETERMINING evidence | N/A |
| No C silently converted into MISS | N/A — no C rows |
| No B silently converted into agent failure | N/A — no B rows |
| No sampled episode removed as inconvenient | Confirmed: none sampled, none dropped |
| No outcome-dependent code path | No analysis code path against external \(\tau\). Frozen `score_v2` not invoked on an external sample. |
| Counts reconcile to N | N/A |
| Source provenance reproducible | Eligibility sources and hashes recorded in `PHASE1_ELIGIBILITY_AUDIT.md` and `public_source_hashes.json` |
| Frozen artifact hashes still match | Yes — `frozen_artifact_hashes.json` |

No adapter was written. No parser was edited after (or before) outcomes, because outcomes were not computed.
