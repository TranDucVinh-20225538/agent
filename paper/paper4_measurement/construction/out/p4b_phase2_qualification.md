# P4-B Phase 2 qualification

status = **PASS**
Object: B01–B20 worlds + gold specs. No agents. $0 API.
n_pass = 20 / 20
instrument_sha256 = `c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59`
transforms_b_sha256 = `7a5ee93261d067d140681a8c539809d52725880ecd7f97c25e0749ef5af15ae6`
gold_spec_sha256 = `0e334b2c9a8ecae0998abd91476fc7ece67f2c732790ab4c987c25a745d1004f`
clusters_sha256 = `8c061c093185787cf98919ac14590064025e7f41283df11a9b0cb0285df0bed5`
worlds_sha256 = `9db6cbb94b933d0c7098dfcc0e257042e58a2c021870561966b5fe91e0e626b3`
qualification_sha256 = `79b38c52b016b28bc07b572265ad8af5c36f3d146d6c22c6555edd69a672152e`
seal_sha256 = `72eb33f718a616b1494fcec3dde512aceed5b9c61be112d611453696efaa4c54`

## §12 conjunction

- `n20_and_quotas`: True
- `locker_replay`: True
- `t1_t8_and_anchors`: True
- `no_observations`: True
- `independence`: True
- `transforms_hashed_no_per_id`: True
- `corpus_and_gold_hashed`: True
- `instrument_hash`: True

## E1–E4 (Phase 4 estimands; not scored here)

- scored_episodes = 0
- abstain_by_cause = {}
- E1 = NOT_OPENED
- E2 = NOT_OPENED
- E3 = NOT_EVALUABLE (eligible 0 < floor 5)
- E4 = NOT_EVALUABLE (eligible 0 < floor 5)

E1–E4 are Phase-4 estimands on natural last-text τ. Phase 2 does not author or score last-responses. Zero τ ⇒ E3/E4 NOT EVALUABLE under the floor of 5; E1/E2 are NOT_OPENED. This does not fail §12.

| id | family | kind | gold | locker | qual | failures |
|---|---|---|---|---|---|---|
| `B01` | Locate | money_usd | `88.40` | True | True | [] |
| `B02` | Locate | money_usd | `64.25` | True | True | [] |
| `B03` | Locate | entity | `Wren Cobb` | True | True | [] |
| `B04` | Locate | categorical | `hush` | True | True | [] |
| `B05` | Compute | money_usd | `65.30` | True | True | [] |
| `B06` | Compute | money_usd | `46.25` | True | True | [] |
| `B07` | Compute | integer | `14` | True | True | [] |
| `B08` | Compute | integer | `12` | True | True | [] |
| `B09` | Reconcile | money_usd | `55.90` | True | True | [] |
| `B10` | Reconcile | money_usd | `73.15` | True | True | [] |
| `B11` | Reconcile | entity | `Tov Gale` | True | True | [] |
| `B12` | Reconcile | categorical | `dim` | True | True | [] |
| `B13` | Filter | money_usd | `29.60` | True | True | [] |
| `B14` | Filter | money_usd | `37.80` | True | True | [] |
| `B15` | Filter | entity | `night_chute_card.txt` | True | True | [] |
| `B16` | Filter | categorical | `brisk` | True | True | [] |
| `B17` | Tally | integer | `3` | True | True | [] |
| `B18` | Tally | integer | `2` | True | True | [] |
| `B19` | Tally | integer | `4` | True | True | [] |
| `B20` | Tally | integer | `5` | True | True | [] |

Corpus, gold, anchors, and worlds were not rewritten.
Phase 3 Flash pilot is BLOCKED until authorized.
