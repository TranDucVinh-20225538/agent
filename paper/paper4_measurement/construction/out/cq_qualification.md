# P4-C CQ qualification

instrument_sha256 = `c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59`
qualification = PASS
V* scored = no
Q* re-scored = no
API spend = $0

| Cluster | kind | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|---|
| CQ01 | money_usd | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match |
| CQ02 | money_usd | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match |
| CQ03 | integer | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match |
| CQ04 | integer | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match |
| CQ05 | entity | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match |
| CQ06 | categorical | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match |

Property failures:
- none

C1–C6 vs frozen instrument. Phase 2 seal is BLOCKED until authorized.
P4-B and Q/V were not modified.
