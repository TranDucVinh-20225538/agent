# P4-C Phase 1 construction

status = **PASS**
n_pass = 30 / 30
api_spend_usd = 0
instrument_sha256 = `c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59`
construction_json_sha256 = `6bdf08b304387235255420a6b62ed527fb0789bf465ff74570c2f6a4920fc552`
params_c_sha256 = `0b576759272d0811b162054d25a0d93045204b92141ed7caa12722f019c720a9`
generate_c_sha256 = `0a1a9661a974242433d73d86ac7b9333aec0f732dc44efde1f085b1fc56848be`
wordlists_c_sha256 = `051c2a61e49d60594e98879d57231de7ac7a06892106e0e49d014dd48ab3be2f`

kind counts: {'money_usd': 12, 'entity': 5, 'categorical': 4, 'integer': 9}
family counts: {'Locate': 5, 'Compute': 5, 'Reconcile': 5, 'Filter': 5, 'Tally': 5, 'Multi-step': 5}
slot counts: {'C1-intended': 10, 'C2-intended': 10, 'ordinary': 10}

| id | family | slot | kind | gold | anchors | pass | failures |
|---|---|---|---|---|---|---|---|
| `C01` | Locate | C1-intended | money_usd | `71.30` | ['ridge tarn fee'] | True | [] |
| `C02` | Locate | C2-intended | money_usd | `53.80` | ['scree fell due'] | True | [] |
| `C03` | Locate | C1-intended | entity | `Ivo Nair` | ['bothy skipper'] | True | [] |
| `C04` | Locate | C2-intended | categorical | `pale` | ['wire status'] | True | [] |
| `C05` | Locate | ordinary | money_usd | `44.15` | ['bracken howe fee'] | True | [] |
| `C06` | Compute | C1-intended | money_usd | `39.25` | ['glen wold crate'] | True | [] |
| `C07` | Compute | C2-intended | money_usd | `39.25` | ['tor beck crate'] | True | [] |
| `C08` | Compute | C1-intended | integer | `16` | ['crag grit crate'] | True | [] |
| `C09` | Compute | ordinary | integer | `13` | ['kist clough shift'] | True | [] |
| `C10` | Compute | C2-intended | integer | `16` | ['beck peat crate'] | True | [] |
| `C11` | Reconcile | C1-intended | money_usd | `48.70` | ['live ridge crate'] | True | [] |
| `C12` | Reconcile | C2-intended | money_usd | `62.45` | ['live scree peat'] | True | [] |
| `C13` | Reconcile | C2-intended | entity | `Rune Pell` | ['live glen grit'] | True | [] |
| `C14` | Reconcile | C1-intended | categorical | `keen` | ['live kist peat'] | True | [] |
| `C15` | Reconcile | ordinary | money_usd | `36.90` | ['live bracken bin'] | True | [] |
| `C16` | Filter | C1-intended | money_usd | `27.40` | ['fell yard rush'] | True | [] |
| `C17` | Filter | C2-intended | money_usd | `33.50` | ['glen yard sealed'] | True | [] |
| `C18` | Filter | ordinary | entity | `Odas Wynn` | ['night tarn'] | True | [] |
| `C19` | Filter | ordinary | categorical | `still` | ['north tor dock'] | True | [] |
| `C20` | Filter | C1-intended | integer | `13` | ['rush fell watch'] | True | [] |
| `C21` | Tally | C1-intended | integer | `6` | ['glen grit shifts'] | True | [] |
| `C22` | Tally | C2-intended | integer | `7` | ['rush tarn notes'] | True | [] |
| `C23` | Tally | ordinary | integer | `8` | ['bothy peat shifts'] | True | [] |
| `C24` | Tally | ordinary | integer | `9` | ['fell kist crates'] | True | [] |
| `C25` | Tally | C2-intended | integer | `6` | ['wold grit notes'] | True | [] |
| `C26` | Multi-step | C1-intended | entity | `Sera Pell` | ['ridge bothy clerk'] | True | [] |
| `C27` | Multi-step | C2-intended | entity | `Bram Kist` | ['fell grit hand'] | True | [] |
| `C28` | Multi-step | ordinary | categorical | `raw` | ['tor peat mark'] | True | [] |
| `C29` | Multi-step | ordinary | money_usd | `19.85` | ['clough grit fee'] | True | [] |
| `C30` | Multi-step | ordinary | money_usd | `24.60` | ['howe bracken due'] | True | [] |

No construction errors.


P4-B was not modified. Phase 2 qualification is BLOCKED until authorized.
No agents. $0 API.
