# P4 V* single sealed pass

freeze_commit = `c35e828db89a9c7eb9d479601215a29221f5d744`
instrument_sha256 = `c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59`
V seal = `26df37a1fe10b05ebb674fea28cf2ac03dcc7772227df9de902f4aed08cb4189`
qualification = PASS
clusters with all six properties = 20 / 20
API spend = $0
instrument modified = no
V* modified = no

| Cluster | kind | dialect | C1 | C2 | C3 | C4 | C5 | C6 | all_six |
|---|---|---|---|---|---|---|---|---|---|
| V01 | money_usd | tool | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match | True |
| V02 | money_usd | unterminated | HIT/match | MISS/mismatch | ABSTAIN/absent | ABSTAIN/channel_indeterminate | HIT/match | HIT/match | True |
| V03 | money_usd | sandbox | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match | True |
| V04 | money_usd | tool | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match | True |
| V05 | money_usd | unterminated | HIT/match | MISS/mismatch | ABSTAIN/absent | ABSTAIN/channel_indeterminate | HIT/match | HIT/match | True |
| V06 | money_usd | sandbox | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match | True |
| V07 | money_usd | tool | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match | True |
| V08 | money_usd | unterminated | HIT/match | MISS/mismatch | ABSTAIN/absent | ABSTAIN/channel_indeterminate | HIT/match | HIT/match | True |
| V09 | integer | sandbox | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match | True |
| V10 | integer | tool | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match | True |
| V11 | integer | unterminated | HIT/match | MISS/mismatch | ABSTAIN/absent | ABSTAIN/channel_indeterminate | HIT/match | HIT/match | True |
| V12 | integer | sandbox | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match | True |
| V13 | integer | tool | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match | True |
| V14 | integer | unterminated | HIT/match | MISS/mismatch | ABSTAIN/absent | ABSTAIN/channel_indeterminate | HIT/match | HIT/match | True |
| V15 | entity | sandbox | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match | True |
| V16 | entity | tool | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match | True |
| V17 | entity | unterminated | HIT/match | MISS/mismatch | ABSTAIN/absent | ABSTAIN/channel_indeterminate | HIT/match | HIT/match | True |
| V18 | categorical | sandbox | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match | True |
| V19 | categorical | tool | HIT/match | MISS/mismatch | ABSTAIN/absent | MISS/mismatch | HIT/match | HIT/match | True |
| V20 | categorical | unterminated | HIT/match | MISS/mismatch | ABSTAIN/absent | ABSTAIN/channel_indeterminate | HIT/match | HIT/match | True |

Hold-rate r_p = (1/20) sum H(p,c)

| property | holds | r_p |
|---|---|---|
| C1 | 20 / 20 | 1.00 |
| C2 | 20 / 20 | 1.00 |
| C3 | 20 / 20 | 1.00 |
| C4 | 20 / 20 | 1.00 |
| C5 | 20 / 20 | 1.00 |
| C6 | 20 / 20 | 1.00 |

ABSTAIN causes:
- `absent`: 20
- `channel_indeterminate`: 7

Failures:
- none

Agent validation not opened. Stop after this pass.
