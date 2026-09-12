# P4-D Phase 1 construction

status = **PASS**
n_pass = 30 / 30
api_spend_usd = 0
instrument_v2_sha256 = `a87ac636a729d99852eb837583b24bce372ff49c196f2be7e39e4f750622fcf3`
wrapper_sha256 = `2a028f2b95a7bc1ce815ac4b01dcb1fc7c8814ded7a5f3f38489d4ffe70e8e08`

kind counts: {'money_usd': 12, 'integer': 9, 'entity': 6, 'categorical': 3}
family counts: {'Locate': 9, 'Compute': 6, 'Reconcile': 6, 'Filter': 3, 'Tally': 3, 'Multi-step': 3}
condition counts: {'plus': 10, 'minus': 10, 'pm': 10}

| id | family_id | family | condition | kind | gold | pass | failures |
|---|---|---|---|---|---|---|---|
| `E01` | F01 | Locate | plus | money_usd | `44.80` | True | [] |
| `E02` | F01 | Locate | minus | money_usd | `51.30` | True | [] |
| `E03` | F01 | Locate | pm | money_usd | `34.10` | True | [] |
| `E04` | F02 | Locate | plus | integer | `31` | True | [] |
| `E05` | F02 | Locate | minus | integer | `36` | True | [] |
| `E06` | F02 | Locate | pm | integer | `41` | True | [] |
| `E07` | F03 | Locate | plus | entity | `Nima Kest` | True | [] |
| `E08` | F03 | Locate | minus | entity | `Palu Orth` | True | [] |
| `E09` | F03 | Locate | pm | entity | `Yara Nolt` | True | [] |
| `E10` | F04 | Compute | plus | money_usd | `33.60` | True | [] |
| `E11` | F04 | Compute | minus | money_usd | `35.60` | True | [] |
| `E12` | F04 | Compute | pm | money_usd | `32.60` | True | [] |
| `E13` | F05 | Compute | plus | integer | `31` | True | [] |
| `E14` | F05 | Compute | minus | integer | `35` | True | [] |
| `E15` | F05 | Compute | pm | integer | `33` | True | [] |
| `E16` | F06 | Reconcile | plus | money_usd | `66.20` | True | [] |
| `E17` | F06 | Reconcile | minus | money_usd | `73.40` | True | [] |
| `E18` | F06 | Reconcile | pm | money_usd | `82.15` | True | [] |
| `E19` | F07 | Reconcile | plus | entity | `Eben Tulk` | True | [] |
| `E20` | F07 | Reconcile | minus | entity | `Lumen Brant` | True | [] |
| `E21` | F07 | Reconcile | pm | entity | `Yara Nolt` | True | [] |
| `E22` | F08 | Filter | plus | categorical | `keyed` | True | [] |
| `E23` | F08 | Filter | minus | categorical | `capped` | True | [] |
| `E24` | F08 | Filter | pm | categorical | `reeded` | True | [] |
| `E25` | F09 | Tally | plus | integer | `21` | True | [] |
| `E26` | F09 | Tally | minus | integer | `32` | True | [] |
| `E27` | F09 | Tally | pm | integer | `23` | True | [] |
| `E28` | F10 | Multi-step | plus | money_usd | `47.20` | True | [] |
| `E29` | F10 | Multi-step | minus | money_usd | `54.05` | True | [] |
| `E30` | F10 | Multi-step | pm | money_usd | `61.80` | True | [] |

No construction errors.


P4-B, P4-C v1, P4-C2, score_v2, and wrapper were not modified. $0 API. No agents.
Conditions are construction factors, not N. Form is not coverage.
