# P4-C2 Phase 2 qualification

status = **PASS**
Object: D01–D30 worlds + gold specs + A2 + transforms_d + Q2. No agents. $0 API.
n_pass = 30 / 30
instrument_v1_sha256 = `c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59`
instrument_v2_sha256 = `a87ac636a729d99852eb837583b24bce372ff49c196f2be7e39e4f750622fcf3`
wrapper_sha256 = `2a028f2b95a7bc1ce815ac4b01dcb1fc7c8814ded7a5f3f38489d4ffe70e8e08`
adjudicator_d_sha256 = `d8b1b27ff0e0a1dbd261896c778dfeb78aef82de1d7071190c546382ebd3dab1`
transforms_d_sha256 = `bb4a216bfba2f8bb5c914941c9b5d8faf4dd776c8ca30b40a8d3a3dfe9abaf9c`
gold_spec_sha256 = `4ab761090209dfba04251da6c23fc5b945e1f927576ebab89cd5d556403b201d`
clusters_sha256 = `3a3bc2ed61faea0f4bf02a4a1594ce0d618569f656ba323654506cbd84499d3e`
worlds_sha256 = `babd49ad1d5220c243a32cfa551fe411791920ea7f6d62ac2ef4d112d4babe1e`
qualification_sha256 = `9673b6ec88080bcf499f07da388fd64a5f189a6c81bc57262a6924900e005adf`
seal_sha256 = `61a438e05a63d0b3d14667c38a5e8a23bc726b8bd66e9a70bbd299aba0ab077a`

## Conjunction

- `n30_and_quotas`: True
- `locker_replay`: True
- `t1_t8_no_anchors`: True
- `no_observations`: True
- `independence`: True
- `dq_pre_gate`: True
- `adjudicator_hashed_no_per_id`: True
- `transforms_hashed_no_per_id`: True
- `corpus_and_gold_hashed`: True
- `instrument_v1_hash`: True
- `instrument_v2_hash`: True
- `p4c_untouched`: True
- `p4b_untouched`: True
- `h7_anti_recovery`: True
- `h8_ids`: True
- `reserve_discarded`: True

## H1–H8 (Phase 4 estimands; not scored here except H7/H8 seal checks)

- scored_episodes = 0
- H1 = NOT_OPENED
- H2 = NOT_EVALUABLE (eligible 0 < floor 10)
- H3 = NOT_EVALUABLE (eligible 0 < floor 10)
- H4 = NOT_OPENED
- H5 = NOT_OPENED (Form gate 0.8; Form is not coverage)
- H6 = NOT_OPENED
- H7 = SEAL_CHECK pass=True
- H8 = SEAL_CHECK pass=True

H1–H8 are Phase-4 estimands on natural last-text τ under DFC. Phase 2 does not author or score natural last-responses. Zero τ ⇒ H2/H3 NOT EVALUABLE under the floor of 10; H1/H4/H5/H6 are NOT_OPENED. This does not fail Phase 2. Form is interface compliance, not coverage.

| id | family | slot | kind | gold | locker | qual | failures |
|---|---|---|---|---|---|---|---|
| `D01` | Locate | C1-intended | money_usd | `81.60` | True | True | [] |
| `D02` | Locate | C2-intended | money_usd | `46.75` | True | True | [] |
| `D03` | Locate | C1-intended | entity | `Tesfaye Holm` | True | True | [] |
| `D04` | Locate | C2-intended | categorical | `foxed` | True | True | [] |
| `D05` | Locate | ordinary | money_usd | `63.20` | True | True | [] |
| `D06` | Compute | C1-intended | money_usd | `52.10` | True | True | [] |
| `D07` | Compute | C2-intended | money_usd | `38.35` | True | True | [] |
| `D08` | Compute | C1-intended | integer | `25` | True | True | [] |
| `D09` | Compute | ordinary | integer | `28` | True | True | [] |
| `D10` | Compute | C2-intended | integer | `27` | True | True | [] |
| `D11` | Reconcile | C1-intended | money_usd | `68.40` | True | True | [] |
| `D12` | Reconcile | C2-intended | money_usd | `41.25` | True | True | [] |
| `D13` | Reconcile | C2-intended | entity | `Anouk Veld` | True | True | [] |
| `D14` | Reconcile | C1-intended | categorical | `taut` | True | True | [] |
| `D15` | Reconcile | ordinary | money_usd | `37.55` | True | True | [] |
| `D16` | Filter | C1-intended | money_usd | `55.15` | True | True | [] |
| `D17` | Filter | C2-intended | money_usd | `26.45` | True | True | [] |
| `D18` | Filter | ordinary | entity | `Joren Pike` | True | True | [] |
| `D19` | Filter | ordinary | categorical | `bound` | True | True | [] |
| `D20` | Filter | C1-intended | integer | `19` | True | True | [] |
| `D21` | Tally | C1-intended | integer | `10` | True | True | [] |
| `D22` | Tally | C2-intended | integer | `11` | True | True | [] |
| `D23` | Tally | ordinary | integer | `15` | True | True | [] |
| `D24` | Tally | ordinary | integer | `18` | True | True | [] |
| `D25` | Tally | C2-intended | integer | `20` | True | True | [] |
| `D26` | Multi-step | C1-intended | entity | `Saskia Bel` | True | True | [] |
| `D27` | Multi-step | C2-intended | entity | `Oren Falk` | True | True | [] |
| `D28` | Multi-step | ordinary | categorical | `slack` | True | True | [] |
| `D29` | Multi-step | ordinary | money_usd | `72.80` | True | True | [] |
| `D30` | Multi-step | ordinary | money_usd | `29.15` | True | True | [] |

Corpus, gold, and worlds were not rewritten.
P4-B and P4-C v1 were not modified. Phase 3 Flash pilot is BLOCKED until authorized.
