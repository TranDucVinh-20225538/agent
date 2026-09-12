# P4-B Phase 1 construction

status = **PASS**
n_pass = 20 / 20
api_spend_usd = 0
instrument_sha256 = `c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59`
construction_json_sha256 = `2cdf016074bbaaca52547768727f8048ee25a35608424113a3f07fb75717c40c`
params_b_sha256 = `b4c610ba547c6222a619b6fbcc5014567d99760f6e501d7cf44d97c0102a8f26`
generate_b_sha256 = `f2375298f0d1532b54ad89b77060640ad8e128a43ee3564303e0698f977e19ae`
wordlists_b_sha256 = `3d7e5fd5e6a60a691a323df8518b87e554ed6f1de3000abf960f251b34c06f43`

kind counts: {'money_usd': 8, 'entity': 3, 'categorical': 3, 'integer': 6}
family counts: {'Locate': 4, 'Compute': 4, 'Reconcile': 4, 'Filter': 4, 'Tally': 4}

| id | family | kind | gold | anchors | pass | failures |
|---|---|---|---|---|---|---|
| `B01` | Locate | money_usd | `88.40` | ['apron chute fee'] | True | [] |
| `B02` | Locate | money_usd | `64.25` | ['mill hatch surcharge'] | True | [] |
| `B03` | Locate | entity | `Wren Cobb` | ['dory skipper'] | True | [] |
| `B04` | Locate | categorical | `hush` | ['wire status'] | True | [] |
| `B05` | Compute | money_usd | `65.30` | ['loft yard crate'] | True | [] |
| `B06` | Compute | money_usd | `46.25` | ['winch dory crate'] | True | [] |
| `B07` | Compute | integer | `14` | ['hatch mill crate'] | True | [] |
| `B08` | Compute | integer | `12` | ['spar ketch shift'] | True | [] |
| `B09` | Reconcile | money_usd | `55.90` | ['live winch cask'] | True | [] |
| `B10` | Reconcile | money_usd | `73.15` | ['live hopper bilge'] | True | [] |
| `B11` | Reconcile | entity | `Tov Gale` | ['live quay mill'] | True | [] |
| `B12` | Reconcile | categorical | `dim` | ['live cask loft'] | True | [] |
| `B13` | Filter | money_usd | `29.60` | ['gantry yard rush'] | True | [] |
| `B14` | Filter | money_usd | `37.80` | ['loft yard sealed'] | True | [] |
| `B15` | Filter | entity | `night_chute_card.txt` | ['night chute'] | True | [] |
| `B16` | Filter | categorical | `brisk` | ['north quay dock'] | True | [] |
| `B17` | Tally | integer | `3` | ['quay mill shifts'] | True | [] |
| `B18` | Tally | integer | `2` | ['rush hatch notes'] | True | [] |
| `B19` | Tally | integer | `4` | ['hopper bilge shifts'] | True | [] |
| `B20` | Tally | integer | `5` | ['dory ketch crates'] | True | [] |

No construction errors.


Phase 2 qualification is BLOCKED until authorized.
No agents. $0 API.
