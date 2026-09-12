# P4 Phase-2 gold-lock

Task-side instruction + rubric criteria only. No agents. $0 API.
Instrument not modified.

N_A declared = 11
n_attempted = 11
n_locked = 3
gate (n_locked == N_A) = **FAIL**

instrument_sha256 = `c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59`
phase2_gold_lock_sha256 = `138a0b43582fa24c58f25b571ce6bee67aec6b71e965bc1af2c0327f756db854`
phase2_taskside_source_sha256 = `42bc7fa326c34accd47bc2f3656ad62672f01624df67a755d457bfc7ae3a8ad3`
seal_sha256 = `17bc87a447915f258c9622662b406c002f8a94ea6a8c1cec19a61e50ab36f616`

Task-side instruction + rubric criteria only. Lock iff exactly one unique P4 money_usd match XOR exactly one unique .txt/.m3u basename (kind entity). Integers in llm_judge prose never lock. No task_id branch. No guest probe. No agent observation.

| id | locked | kind | gold | anchors | reason |
|---|---|---|---|---|---|
| `contradiction-f013` | FALSE |  | `` | [] | no_unique_allowed_kind_value |
| `contradiction-f015` | FALSE |  | `` | [] | no_unique_allowed_kind_value |
| `contradiction-f016` | FALSE |  | `` | [] | no_unique_allowed_kind_value |
| `contradiction-f021` | FALSE |  | `` | [] | no_unique_allowed_kind_value |
| `contradiction-f023` | FALSE |  | `` | [] | no_unique_allowed_kind_value |
| `counterfactual-f008` | FALSE |  | `` | [] | no_unique_allowed_kind_value |
| `counterfactual-f014` | FALSE |  | `` | [] | no_unique_allowed_kind_value |
| `retrieval-f020` | TRUE | entity | `Threat_Level_Midnight_Sequel_Notes.txt` | ['Threat Level Midnight sequel'] | unique_txt_or_m3u_basename |
| `retrieval-f032` | TRUE | entity | `Dundies_2026_Categories.txt` | ['the Dundies 2026 categories'] | unique_txt_or_m3u_basename |
| `retrieval-f033` | TRUE | entity | `Somehow_I_Manage_Chapter_1.txt` | ["book, 'Somehow I Manage'."] | unique_txt_or_m3u_basename |
| `retrieval-f035` | FALSE |  | `` | [] | nonunique_file |

No IDs added or removed from the leftover 11.
If FAIL: do not lower N_A. Do not start agents. Construction fail of Phase 2.
