# P4 Q qualification

instrument_sha256 = `c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59`
V seal (unopened) = `26df37a1fe10b05ebb674fea28cf2ac03dcc7772227df9de902f4aed08cb4189`
bugfix-to-spec = False
qualification = PASS
V* scored = no
API spend = $0

| Cluster | kind | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|---|
| Q01 | money_usd | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match |
| Q02 | money_usd | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match |
| Q03 | integer | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match |
| Q04 | integer | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match |
| Q05 | entity | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match |
| Q06 | categorical | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match |

Spec-trace mismatches:
- none

Property failures:
- none

Licensed to score V* = yes (after freeze commit)
Stop after Q. V* not opened.
