# P4-C2 Phase 1 construction

status = **PASS**
n_pass = 30 / 30
api_spend_usd = 0
instrument_v1_sha256 = `c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59`
instrument_v2_sha256 = `a87ac636a729d99852eb837583b24bce372ff49c196f2be7e39e4f750622fcf3`
wrapper_sha256 = `2a028f2b95a7bc1ce815ac4b01dcb1fc7c8814ded7a5f3f38489d4ffe70e8e08`
construction_json_sha256 = `5a6b20713c292dce25b75646644e43875fd84528978e9ac40964ff11d6376219`
params_d_sha256 = `e0be495b2b28cb69de03ec51fe5131fd57bd0ad9de2a71f1510a1a43b4e56e97`
generate_d_sha256 = `bf2f52ee6242c2fa8552f84b197ce12fecaaaf8db9e10f35a4b850187547fb47`
wordlists_d_sha256 = `cfa969477845bc7ad2391f2c0b9c03c7493bbd0e0188e717d0fd1357db6c59d3`

kind counts: {'money_usd': 12, 'entity': 5, 'categorical': 4, 'integer': 9}
family counts: {'Locate': 5, 'Compute': 5, 'Reconcile': 5, 'Filter': 5, 'Tally': 5, 'Multi-step': 5}
slot counts: {'C1-intended': 10, 'C2-intended': 10, 'ordinary': 10}

| id | family | slot | kind | gold | pass | failures |
|---|---|---|---|---|---|---|
| `D01` | Locate | C1-intended | money_usd | `81.60` | True | [] |
| `D02` | Locate | C2-intended | money_usd | `46.75` | True | [] |
| `D03` | Locate | C1-intended | entity | `Tesfaye Holm` | True | [] |
| `D04` | Locate | C2-intended | categorical | `foxed` | True | [] |
| `D05` | Locate | ordinary | money_usd | `63.20` | True | [] |
| `D06` | Compute | C1-intended | money_usd | `52.10` | True | [] |
| `D07` | Compute | C2-intended | money_usd | `38.35` | True | [] |
| `D08` | Compute | C1-intended | integer | `25` | True | [] |
| `D09` | Compute | ordinary | integer | `28` | True | [] |
| `D10` | Compute | C2-intended | integer | `27` | True | [] |
| `D11` | Reconcile | C1-intended | money_usd | `68.40` | True | [] |
| `D12` | Reconcile | C2-intended | money_usd | `41.25` | True | [] |
| `D13` | Reconcile | C2-intended | entity | `Anouk Veld` | True | [] |
| `D14` | Reconcile | C1-intended | categorical | `taut` | True | [] |
| `D15` | Reconcile | ordinary | money_usd | `37.55` | True | [] |
| `D16` | Filter | C1-intended | money_usd | `55.15` | True | [] |
| `D17` | Filter | C2-intended | money_usd | `26.45` | True | [] |
| `D18` | Filter | ordinary | entity | `Joren Pike` | True | [] |
| `D19` | Filter | ordinary | categorical | `bound` | True | [] |
| `D20` | Filter | C1-intended | integer | `19` | True | [] |
| `D21` | Tally | C1-intended | integer | `10` | True | [] |
| `D22` | Tally | C2-intended | integer | `11` | True | [] |
| `D23` | Tally | ordinary | integer | `15` | True | [] |
| `D24` | Tally | ordinary | integer | `18` | True | [] |
| `D25` | Tally | C2-intended | integer | `20` | True | [] |
| `D26` | Multi-step | C1-intended | entity | `Saskia Bel` | True | [] |
| `D27` | Multi-step | C2-intended | entity | `Oren Falk` | True | [] |
| `D28` | Multi-step | ordinary | categorical | `slack` | True | [] |
| `D29` | Multi-step | ordinary | money_usd | `72.80` | True | [] |
| `D30` | Multi-step | ordinary | money_usd | `29.15` | True | [] |

No construction errors.


P4-B and P4-C v1 were not modified. Phase 2 qualification/seal is BLOCKED until authorized.
No agents. $0 API.
Public v2 quantities remain Form and CC; Form is not coverage.
