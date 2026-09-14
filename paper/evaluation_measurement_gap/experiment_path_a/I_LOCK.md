# I_LOCK — Path A family admission (AgentRewardBench)

**Status:** LOCKED 2026-09-13.  
**No ABSTAIN / HIT / MISS rates in this file.**  
**Corpus:** AgentRewardBench only. Dong 150 is not in the frame.

Selection rule (locked before rates): reconstruct the **official evaluator observation** of that task family from released artifacts. If the official channel is a live getter / Playwright / `program_html` JS / page-image query that is not stored as that getter’s output → **STOP-INCOMPATIBLE**. Do not substitute last-answer or axtree.

Released oracle \(V\) on a trajectory is `summary_info.cum_reward` in cleaned JSON. Wording: *released oracle \(V\) on this trajectory*, not “WebArena published score.” Unused on STOP families.

**498/1302 is admission, not an ARB-wide rate.** Do not headline 498 as “we audited AgentRewardBench.” The admitted slice is string/URL (the easy official \(I\)); 804 STOP is HTML/DB/image. `string_url` n=4 (WA) and n=6 (VWA) stay ADMIT and are **not** an abstract stratum.

---

## Inspected samples (schema only)

| File | sha256 | Notes |
|---|---|---|
| `webarena.400.json` | `7a261094…d722` | `eval_types=program_html` (STOP family). Last action `goto`; no `send_msg_to_user`. |
| `visualwebarena.resized.372.json` | `eca97393…936d` | Metadata `program_html` after stripping `.resized` → STOP family. File still has `send_msg_to_user`; that does not admit it. |
| `workarena.…multi-chart-value-retrieval.json` | `3d67eacb…e22f` | Last action is `send_msg_to_user`. Official WorkArena \(I\) is still `validate(page, chat)` on a live instance. |
| `assistantbench.…13.json` | `79ed0d67…e7d109` | Crash (`err_msg`). **EXEC_FAIL** under `EPISODE_ELIGIBILITY.md`, not ABSTAIN. |

Top-level keys (all four): `benchmark`, `agent`, `model`, `valid`, `experiment`, `goal`, `seed`, `model_args`, `flags`, `summary_info`, `package_version`, `steps`.  
Step keys include `action`, `url`, `chat_messages`, `axtree` / `axtree_pruned`. Getter **outputs** are not a field.

Eval-type metadata (BrowserGym CSVs shipped with ARB):

| File | sha256 |
|---|---|
| `schema/webarena.csv` | `2d5ed053ece894d09cd17485f53cb6c3d4da2a4b7dec92603356dfcd09b7c962` |
| `schema/visualwebarena.csv` | `71d1823acdb54ab3877eaf81e4c4d61b5f4d995d112e2970b57b19ed30f740a4` |

ARB unique trajectory keys (from `SCHEMA.md`): webarena 398, visualwebarena 300, workarena 472, assistantbench 132.

---

## Family table

Unit: unique `(benchmark, task_id, model_name, exp_name)` in the annotation CSV.

| Family | Official \(I\) | In cleaned JSON? | Status | n unique traj | Locked observation if admitted |
|---|---|---|---|---|---|
| WebArena `string_match` only | last assistant answer (`send_msg_to_user` / last chat assistant message) | yes (action + `chat_messages`) | **ADMIT** | 144 | last assistant message string; empty → ABSTAIN |
| WebArena `url_match` only | last page URL | yes (`steps[-1].url`) | **ADMIT** | 32 | last URL; missing → ABSTAIN |
| WebArena `string_match` + `url_match` only | conjunction of answer + URL | yes | **ADMIT** | 4 | both channels; either empty/missing → ABSTAIN |
| WebArena any `program_html` | JS getter on live page | **no** (axtree ≠ getter output) | **STOP-INCOMPATIBLE** | 218 | — |
| VWA `string_match` only | last assistant answer | yes | **ADMIT** | 117 | same as WA string |
| VWA `url_match` only | last page URL | yes | **ADMIT** | 63 | same as WA URL |
| VWA `string_match` + `url_match` only | conjunction | yes | **ADMIT** | 6 | same as WA string+url |
| VWA any `program_html` or `page_image_query` | live HTML JS and/or page image | **no** (screenshots not in JSON; JS output not stored) | **STOP-INCOMPATIBLE** | 114 | — |
| AssistantBench | last reported answer (Yoran); gold not in JSON | last answer yes | **ADMIT for I-emptiness only** | 132 | ABSTAIN-vs-\(V\) after episode eligibility. HIT/MISS only with official gold file, never ARB human labels |
| WorkArena | `task.validate(page, chat_messages)` (DB / URL / page / chat; live instance) | chat+URL+axtree present; **live validate payload not stored** | **STOP-INCOMPATIBLE** | 472 | do not treat `send_msg_to_user` as official \(I\) |

**Admitted n (unique traj):** \(144+32+4+117+63+6+132 = 498\).  
**STOP-INCOMPATIBLE n:** \(218+114+472 = 804\).  
These are admission counts, not an ARB-wide rate and not an unjustified-FAIL rate. Confirmatory tables use **ELIGIBLE** rows only (`EPISODE_ELIGIBILITY.md`). Do not pool AssistantBench with WA/VWA into 126/299 or into one HIT/MISS column.

VWA task ids in ARB use `.resized.` (`visualwebarena.resized.372`). Join to metadata by deleting `.resized`.

Mixed eval strings in the CSV are space-separated (`url_match program_html`).

---

## Locked after admission (still no rates)

- Episode eligibility: `EPISODE_ELIGIBILITY.md`
- Extractor: `EXTRACTOR.md` + `extract_i.py` (`python3 test_extract_i.py` = 12 OK)
- Admitted path list: `schema/admitted_keys.csv` (498 rows)

## Still before rates

1. Download cleaned JSON for admitted keys only (no screenshots).
2. Gold files: WA/VWA `reference_answers` / `reference_url`; AssistantBench official gold only if opening that HIT/MISS column.
3. Then count. Do not retune families.

Human ARB `trajectory_success` is sensitivity only (Lù object), not primary correspondence gold.

---

## Explicitly not this lock

- Dong 150
- Path B / WebJudge Score
- P3 extractor `3242c30`
- Using axtree as a stand-in for `program_html`
- Using last-answer as a stand-in for WorkArena `validate()`
