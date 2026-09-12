# P4-C Phase 2 qualification

status = **PASS**
Object: C01–C30 worlds + gold specs + A + transforms_c. No agents. $0 API.
n_pass = 30 / 30
instrument_sha256 = `c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59`
adjudicator_c_sha256 = `595b02f50a2ad968b56051bb4d0b8d8686697a29a94ac39afaf2e1d53b97a8b2`
transforms_c_sha256 = `e6a000c62413be724d6452c27dbf755defac8baa173ed146ea7d092778d2bcd3`
gold_spec_sha256 = `dfe9e6a308bc5b21e59c8ca27f2182b7e7773441ba185012371dc2fc1fd8c2d8`
clusters_sha256 = `bd30104becac546169ce62f921e6079a3df758a9a0fccf95106f9aa59060352f`
worlds_sha256 = `b39c1e082a21c18f4a2b105e94586b3d0584b57af6c3a6904e50fa903ef75c4b`
qualification_sha256 = `22d5a6a34f162b519777594f4e69d7d6aeb6edd661979e82b33faf756aa84845`
seal_sha256 = `0acc7e73f8cae0e82bc8d1a7b7cc727163f1821b578fbfb2d7d79593e9ccd1ea`

## Conjunction

- `n30_and_quotas`: True
- `locker_replay`: True
- `t1_t8_and_anchors`: True
- `no_observations`: True
- `independence`: True
- `cq_pre_gate`: True
- `adjudicator_hashed_no_per_id`: True
- `transforms_hashed_no_per_id`: True
- `corpus_and_gold_hashed`: True
- `instrument_hash`: True
- `p4b_untouched`: True
- `reserve_discarded`: True

## G1–G6 (Phase 4 estimands; not scored here)

- scored_episodes = 0
- G1 = NOT_OPENED
- G2 = NOT_EVALUABLE (eligible 0 < floor 10)
- G3 = NOT_EVALUABLE (eligible 0 < floor 10)
- G4 = NOT_OPENED
- G5 = NOT_OPENED
- G6 = NOT_OPENED

G1–G6 are Phase-4 estimands on natural last-text τ. Phase 2 does not author or score last-responses. Zero τ ⇒ G2/G3 NOT EVALUABLE under the floor of 10; G1/G4/G5/G6 are NOT_OPENED. This does not fail Phase 2.

RC01–RC10 were not instantiated and are discarded at seal.

| id | family | slot | kind | gold | locker | qual | failures |
|---|---|---|---|---|---|---|---|
| `C01` | Locate | C1-intended | money_usd | `71.30` | True | True | [] |
| `C02` | Locate | C2-intended | money_usd | `53.80` | True | True | [] |
| `C03` | Locate | C1-intended | entity | `Ivo Nair` | True | True | [] |
| `C04` | Locate | C2-intended | categorical | `pale` | True | True | [] |
| `C05` | Locate | ordinary | money_usd | `44.15` | True | True | [] |
| `C06` | Compute | C1-intended | money_usd | `39.25` | True | True | [] |
| `C07` | Compute | C2-intended | money_usd | `39.25` | True | True | [] |
| `C08` | Compute | C1-intended | integer | `16` | True | True | [] |
| `C09` | Compute | ordinary | integer | `13` | True | True | [] |
| `C10` | Compute | C2-intended | integer | `16` | True | True | [] |
| `C11` | Reconcile | C1-intended | money_usd | `48.70` | True | True | [] |
| `C12` | Reconcile | C2-intended | money_usd | `62.45` | True | True | [] |
| `C13` | Reconcile | C2-intended | entity | `Rune Pell` | True | True | [] |
| `C14` | Reconcile | C1-intended | categorical | `keen` | True | True | [] |
| `C15` | Reconcile | ordinary | money_usd | `36.90` | True | True | [] |
| `C16` | Filter | C1-intended | money_usd | `27.40` | True | True | [] |
| `C17` | Filter | C2-intended | money_usd | `33.50` | True | True | [] |
| `C18` | Filter | ordinary | entity | `Odas Wynn` | True | True | [] |
| `C19` | Filter | ordinary | categorical | `still` | True | True | [] |
| `C20` | Filter | C1-intended | integer | `13` | True | True | [] |
| `C21` | Tally | C1-intended | integer | `6` | True | True | [] |
| `C22` | Tally | C2-intended | integer | `7` | True | True | [] |
| `C23` | Tally | ordinary | integer | `8` | True | True | [] |
| `C24` | Tally | ordinary | integer | `9` | True | True | [] |
| `C25` | Tally | C2-intended | integer | `6` | True | True | [] |
| `C26` | Multi-step | C1-intended | entity | `Sera Pell` | True | True | [] |
| `C27` | Multi-step | C2-intended | entity | `Bram Kist` | True | True | [] |
| `C28` | Multi-step | ordinary | categorical | `raw` | True | True | [] |
| `C29` | Multi-step | ordinary | money_usd | `19.85` | True | True | [] |
| `C30` | Multi-step | ordinary | money_usd | `24.60` | True | True | [] |

Corpus, gold, anchors, and worlds were not rewritten.
P4-B was not modified. Phase 3 Flash pilot is BLOCKED until authorized.
