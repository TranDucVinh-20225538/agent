# Paper 2 — execution manifest (freeze before cell 1/228)

**Status:** EXECUTION_FROZEN — design closed; agent failure is data.  
**Analysis universe:** `out/paper2_analysis_universe.md` (amended: f024 rejected pre-cell-1)  
**Spec:** `paper/paper2_counterfactual_eval/PAPER2_SPEC.md`  
**Do not** edit \(\mathcal{M}\), \(\mathcal{T}\), \(D\), or this file after cell 1 starts, except dated infra stop (below).

---

## Commitment

| Quantity | Value |
| --- | --- |
| \(\|\mathcal{M}\|\) (sealed) | 4 |
| \(\|\mathcal{T}\|\) | 25 (seal 27 − f029 − f024) |
| Surviving variants | 32 |
| multi-I (I1+I2) | 7 |
| **Legs (if all 4 run)** | **228** = \(4\times25\times2 + 4\times7\) |
| **Live status** | see §0 status table; amendments §0.1–§0.6 |

From cell 1 onward: stop only for **infrastructure** severe enough to halt the whole experiment (Control API dead, disk full, systematic harness bug). Not for “model looks bad / expensive / empty XML rate.” **Exceptions, per-lane only, each requiring a dated amendment below:** per-model transport invalidity (§0.1, §0.2) and a demonstrated instrument defect that drops unambiguously intended actions (§0.3). Neither may be invoked from a rate alone.

---

## 0. API lane routing (operational — does not change \(\mathcal{M}\)/\(\mathcal{T}\)/\(D\))

Two OpenRouter-capable budget lanes. **No raw keys in repo/logs** — env vars only.

| Lane | Env (example) | Models |
| --- | --- | --- |
| `SMALL_KEY` | e.g. `OPENROUTER_API_KEY_SMALL` | `qwen/qwen3.5-9b`, `qwen/qwen3.8-flash` only |
| `LARGE_KEY` | Anthropic native; OpenRouter GPT key `008` via the frozen adapter (§0.2) | `claude-opus-4-6`, `gpt-5.5` |

**Model order / live status (as of 2026-09-08):**

| # | Model | Lane / host | Status |
| --- | --- | --- | --- |
| 1 | Qwen 3.5-9B | SMALL (exhausted) | **COMPLETE, pre-patch instrument** — §0.4 replay gate pending; rerun purchasable again on `008` (§0.8) |
| 2 | Qwen 3.8-Flash | SMALL exhausted; `008` funded | **NO VALID LEGS YET** — pre-patch invalidated (§0.3), post-patch `58369` died on key exhaustion (§0.7). §0.7 exclusion **withdrawn**; runnable as a fresh lane from leg 1 after Claude (§0.8) |
| 3 | GPT-5.5 | `008`, node30, `results/paper2_exec/study2-gpt` | **COMPLETE + FROZEN** — 57/57, 32 `DONE` / 25 `TERMINAL_FAIL`, 2026-09-09T06:37 ICT; `GPT_FROZEN.txt`, `out/study2_gpt_freeze.json`, archive `chmod a-w`; substituted substrate §0.2 |
| 4 | Claude Opus 4.6 | `008…9dd` **via generic XML bridge, not Anthropic native** | **RUNNING** — fresh 57 legs from leg 1, PID `920150`; substrate disclosure §0.8 |

Original order (9B → Flash → Claude → GPT) is superseded for **scheduling only** by §0.5. \(\mathcal{M}\), \(\mathcal{T}\), \(D\), and per-cell policy are unchanged.

**57 legs/model** when a model is runnable. Within a model lane, key assignment is immutable. Claude never uses `SMALL_KEY`. Exhausting `SMALL_KEY` mid-Qwen: checkpoint, stop, report — **no silent failover to `LARGE_KEY`**. Smoke/cost checks are **not** analysis legs.

### 0.1 Dated amendment — GPT PAUSED (2026-09-06)

**Decision:** Freeze GPT here. No resume native. Do not burn remaining GPT legs. Do not retry the 4 early GPT legs into results.

| Path | Status |
| --- | --- |
| OpenRouter GPT | **Invalid for measurement** — `openai_cuabash` multi-turn needs `previous_response_id` + computer tool / Responses server-side state; OpenRouter does not preserve that contract |
| Native `api.openai.com` | Host proxy **403**; OpenAI billing ≠ OpenRouter balance — not a key-swap fix |
| 4 early GPT legs | Label **`INVALID_INFRASTRUCTURE`** (stash only); **exclude** from benchmark / Layer A–B |

**Not allowed as “workarounds” (change methodology):**

- Clearing / resetting `previous_response_id` mid-episode → fresh-screenshot turns, lost trajectory context  
- Treating that as the primary GPT path without a frozen, validated state-reconstruction design  

**Resume GPT only after a separate engineering freeze:** design state reconstruction → prove trajectory semantics equivalent → controlled validation → freeze implementation → then schedule GPT legs. That is **not** a mid-run runner hotfix.

**Analysis consequence (reproducible, not outcome-fishing):** sealed \(\mathcal{M}\) still lists `gpt-5.5`; execution coverage reports GPT as transport-blocked. Layer B ranks only models with valid runnable transport and enough valid pairs (`n_min` per spec). Incomplete 4-model matrix is a **limitation / excluded-model** note, not a reason to invent a GPT path mid-experiment.

### 0.2 Dated amendment — GPT lane runs a *substituted scaffold*, not the adapter §0.1 required (2026-09-08)

An earlier draft of this section claimed GPT resumed via a frozen `ResponseStateAdapter` that met §0.1's resume condition. **That is withdrawn as factually wrong.** Host verification (node30, 2026-09-08T05:26:30Z) shows no such component exists: `git ls-files` and `git log --all -- '*adapter*'` are empty, and the only occurrences of the name are §0.1's resume text and a guard line in `scripts/paper2_gpt_gate0_tool_ownership.py` ("Fail → stop; do not implement ResponseStateAdapter"). **§0.1's chain (Gate 0 → frozen adapter → amended hash → approval) never closed.**

**What actually ran.** The `openai_cuabash` native computer-use scaffold was abandoned after its Gate 0 failed, and `gpt-5.5` was instead run through the **generic XML executor over OpenRouter chat-completions** (`qwen_cuabash` + `OpenRouterChatCompletionsTransport`) — the same scaffold class as the Qwen lanes, not the Responses API.

| Fact | Value (host-reported) |
| --- | --- |
| Executor SHA frozen at start | `e8f6289` (`e8f628916d0a3e8a23d4af65a23dad296a36f6af`), committed `2026-09-07T09:18:20Z` |
| Last transport commit before it | `1eea06b` @ `2026-09-07T08:43:08Z` (`generic_executor/`) |
| `gpt_leg1_started_utc` | `2026-09-07T10:19:59+00:00` (`…/study2-gpt/retrieval-f010/G0/run_started.txt`) |
| Freeze → leg 1 | **1h 01m 39s before**, corroborated by launch log `HEAD=e8f6289` (L7) and leg 1/57 at L19 |
| Resume at `15:50:32Z` (PID 4188554) | Same `HEAD=e8f6289` (L8773); not leg 1 |
| Mutation after leg 1 | **None** — `git log --since=2026-09-07T10:19:58Z -- generic_executor/ scripts/study2_run_mypcbench.py scripts/study2_exec_run.sh` is empty; worktree clean on those paths |
| Branch | `generic-executor-phase1` |

So *freeze-before-leg-1* and *no-mutation-after-leg-1* both hold **for the substituted scaffold**. The poolability question is therefore not §0.2's mid-lane-edit clause; it is scaffold substitution itself.

**Gate 0 vs Gate 0A — two different artifacts, not interchangeable.**

*Gate 0 (native `openai_cuabash`, the one §0.1 named) — **FAIL***. `results/paper2_exec/gpt-5.5-gate0/GATE0_REPORT.json`, verdict `FAIL` in `GATE0_VERDICT.txt`, `2026-09-06T09:07:18Z`→`09:19:13Z`. The token was planted in our QEMU (`GATE0-44c08e8674284a87`, `plant.returncode=0`, host `scranton-pc`), but turn 1 already contained a `shell_call_output`: the **provider pre-executed the tool**. There is no turn 2 and therefore no proof that a client-issued action ran on our machine. This is precisely the failure §0.1 predicted.

*Gate 0A (generic executor, the class that Study 2 actually runs) — **PASS**, narrowly*. `results/paper2_exec/gate0a-gpt/gate0a_report.json` + `traj.jsonl`, finished `2026-09-06T15:57:37Z`. Turn 1 issues `cat /tmp/GATE0A_GPT_TOKEN.txt`; our QEMU returns `GPTGATE0A-870c4f11d7e14264`; turn 2's instruction contains that token; `token_sha256 == agent_reported_token_sha256 = fafdef4c…`. Tool ownership is therefore established **for bash stdout only** — `p2_screenshot_changed: false`, three identical `shot_hashes` (`1beaa3…`), so **GUI/screenshot round-trip ownership is not demonstrated**, which matters because the task set is largely GUI.

**Two gaps between that smoke and the matrix run, both to be stated rather than glossed:** Gate 0A ran at `freeze_sha=dd43cbe` with `routing.lane=SMALL`, whereas the matrix runs at `e8f6289` on the LARGE `008` key, and **five `generic_executor/` commits** (retry, near-miss XML, family bind, …) sit between the two — all before leg 1, but the smoke is not pinned to the SHA that executed the legs, and the actual lane routing was never smoke-tested.

**Validation inventory (host-verified; supersedes the earlier draft's list).**

| Kind | Exists? | What it actually is |
| --- | --- | --- |
| Protocol fixtures | Yes | `tests/fixtures/gate0a_near_miss/` (5 XML shapes, `screenshot_noop`, 2 silent trajectories — **Flash-derived, not GPT**); `tests/fixtures/paper2_terminal/` (10 classifier cases); fake-model scripts in `test_generic_executor_fake.py` |
| Multi-turn smoke | Yes, **2 turns** live | Gate 0A `n_predict_rounds: 2`, plus mock multi-turn tests. Native Gate 0 stopped at 1 turn and **FAILED**; it does not count as smoke |
| Semantic trajectory tests | **No** | No test scores \(D\) / gold / `registry_semantic_frozen.json` against any trajectory. **Removed from the support list** |
| Pass–fail record | Yes (unit + smoke only) | Gate 0A PASS, native Gate 0 FAIL, 54 mock unittests OK. The Study 2 matrix itself is **not** validation |

**Canonical reporting sentence (settled 2026-09-08; use verbatim in method, host notes, and result tables).**

> Study 2 GPT lane measures **`openai/gpt-5.5` on the frozen generic XML CUA protocol** (`qwen_cuabash` + OpenRouter `chat/completions`, no `tools`, no `previous_response_id`). It is **not** the sealed Paper 1 instrument (`gpt-5.5` / `openai_cuabash` / OpenAI Responses). Native CUA Gate 0 on this host **FAIL**ed (provider-pre-executed `shell_call_output`); that path was never used. Comparability is **within the Study 2 generic-executor roster** (Flash / GPT / Claude on the same XML loop), not vs Paper 1 native GPT.

**Identity split — seal is history, not runtime.**

| | Seal (`registry/sealed_models.json`) | Lane as executed |
| --- | --- | --- |
| Model id | `gpt-5.5` | `openai/gpt-5.5` |
| `agent_type` | `openai_cuabash` | CLI `qwen_cuabash`; factory **drops** `agent_type` |
| Provider / API | OpenAI native | OpenRouter chat-completions, LARGE `008…9dd` |
| Protocol | Responses computer/shell tools | Frozen XML `<tool_call>` / `computer_use` + `bash` |
| Slug | — | `study2-gpt` |
| Gate | Paper 1 harness | Gate 0A generic **PASS**; Gate 0 native **FAIL** |

Runtime records `model=openai/gpt-5.5` with `agent=qwen_cuabash+OpenRouterChatCompletions`. The harness still prints `Qwen35VL Output` — that is the **shared XML parser**, not a Qwen model.

**May claim:** GPT-5.5 weights on the **same** Study 2 instrument as Flash (and Claude if on the same bridge); this lane's `DONE`, judge scores, and STS are results for **generic-executor GPT**.

**May not claim:** "GPT CUA native", `openai_cuabash`, "Paper 1 GPT replicated", Responses `previous_response_id` semantics, a state adapter, native-OpenAI equivalence, GUI-level ownership from Gate 0A (bash stdout only), semantic trajectory validation, or any pooling with the archived `results/paper2_exec/gpt-5.5-invalid-openrouter-transport/` legs.

**Seal is not rewritten.** `registry/sealed_models.json` was sealed `2026-09-03` and its `agent_type` stays as-is: the seal row describes the Paper 1 / native instrument, not this matrix. Study 2 keeps the model **id** `gpt-5.5` and changes the **execution substrate**; that is recorded here and in `PAPER2_SPEC.md` §3, never by editing the seal to match runtime.

**Footnote is mandatory, not optional.** Any §0.2 or \(\mathcal{M}\) table that prints `openai_cuabash` without the substrate footnote reads as native CUA, and a native-CUA reading is **not poolable** with the Flash generic lane.

**The 4 early GPT legs stay `INVALID_INFRASTRUCTURE`.** Archived at `results/paper2_exec/gpt-5.5-invalid-openrouter-transport/`, excluded from coverage and Layer A–B, never retried into results and never pooled with `study2-gpt`. The current lane counts from its own leg 1.

**Lane progress (snapshot, will age).** 26/57 unique `(task, leg)` at `2026-09-08T05:26:30Z`; last finished `contradiction-f017` G1 `DONE` at `05:06:10Z` (56 steps); `retrieval-f002` G0 in flight (runner PID 4188554 alive).

### 0.3 Dated amendment — Flash lane STOPPED as Gate 0A instrument defect (2026-09-08)

**Decision.** HPC Slurm job `58337` (Qwen 3.8-Flash) is stopped and its partial corpus is **invalidated as measurement**. It is retained read-only (`dr-xr-xr-x`) as a frozen pre-patch diagnostic corpus at `results/paper2_exec/_audit/gate0a_flash_prepatch_diagnostic_partial_29of57_20260908T040034Z/`, with the pre-patch live output root `hpc-flash-small/` carrying a `DO_NOT_RESUME.txt`. It must never be merged with post-patch results. Population labels, which are three different things and were briefly conflated: **29/57** checkpoints in the archive, **20** of those `TERMINAL_FAIL`, and an earlier **26/57** progress snapshot taken before the stop.

**Why this is an instrument stop, not a “bad model” stop.** The Commitment section forbids stopping for an “empty XML rate,” and that prohibition is upheld here. The stop is licensed by evidence of a **harness defect**: read-only inspection of the first 29 checkpoints found 20 `TERMINAL_FAIL` distributed as 13 `NO_ACTION_ABORT` / `empty_action_limit`, 5 `MAX_STEPS_NO_DONE`, 2 `PREDICT_CRASH`, **0 `EXECUTOR_EXCEPTION`** — and the aborts trace to the parser discarding model output whose action intent is **explicit and unambiguous** but whose tags are near-miss (e.g. `<function=tool_call>` with `action=bash`, or `<parameter=bash>` where the function tag belongs). Losing an unambiguously intended action is instrument attrition, not agent behaviour. Corroboration that the executor and environment are healthy: on the same tasks the G0 leg reaches `DONE` while G1/G2 abort.

**Order of operations (already followed).** Stop (reversible) → inventory the exact malformed shapes with counts from the *whole* partial corpus → only then decide whether to patch. The inventory defines the failure surface; intuition does not.

**Patch scope.** Canonicalise a **small, enumerated** list of observed, semantically unambiguous tag confusions, narrow enough to print every newly accepted shape in the paper. Forbidden: fuzzy matching, permissive regex over arbitrary tag permutations, inferring intent from prose, accepting under-specified GUI actions, inventing coordinates, falling back to a previous action, touching `DONE` semantics / `inspect_last_action` / terminal parity, and changing the prompt, action grammar, `max_steps`, task matrix, or QEMU config. Ambiguous shapes stay malformed.

**Rerun terms.** New output root, never resumed from the pre-patch corpus, same 57-cell matrix from leg 1, same model / `SMALL_KEY` / task set / `max_steps` / QEMU config / readiness gates / terminal rule. The only intended difference is the enumerated canonicalisation. The post-run report compares pre- and post-patch failure distributions and states how many malformed shapes were recovered into continued trajectories.

**Patch as executed (host-reported).** Commit `0773242053e66fe2391f960d9a0baa1e6198db92`, *Wire near-miss parser on paper2_exec PYTHONPATH for Gate 0A Flash* — 12 files, +427/−1: a `PYTHONPATH` export in `scripts/paper2_exec_run.sh`, `classify_parse_event` **audit labels only** in `generic_executor/near_miss_xml.py`, a dated infra-stop note in this manifest, and a 237-line regression test with 7 fixtures. Unchanged: screenshot handling, `DONE`, `max_steps`, prompt, retry, terminal classifier. Regression at that tree: 74 unittests OK, `study2_plumbing_dry_validate.py` → `ALL_DRY_VALIDATE_PASS`.

**Mechanism wording (kept honest).** The defect is recorded as an **environment-matched reproduction**: the launch configuration allowed the near-miss module to fail silently through an `ImportError` handler. It is *not* claimed that job 58337's log directly evidences the `ImportError`. Audit trail: `out/gate0a_flash_importerror_reproduction.md`, `…_no_action_abort_recovery.md`, `…_screenshot_hook_provenance.md`.

**Post-patch rerun (live at the time of writing).** Slurm job `58369` `hpc-flash-g0a-pp`, node002 (TCG), leg 1/57 `retrieval-f010/G0`; `OUT_ROOT=results/paper2_exec/hpc-flash-small-gate0a-postpatch`; run manifest `results/paper2_exec/_audit/gate0a_flash_postpatch_run_manifest.json`. Recorded identity: executor `0773242…`, parser SHA256 `fa7263d63934cb94e817d7c91f40c72386a4040182deb39a835343deb2c76b2f`, qcow2 `7c2ddcf2…`, cell-order SHA256 `9e77c0ff61c41dbb904d2063b449d2f54e893164e8da8a0fcc3c0e90b7bed667`, `qwen/qwen3.8-flash` on SMALL, `max_steps=80`, `empty_limit=3`, retry `1eea06b` (15×/600 s, 429/5xx/timeout only), QEMU 8.2.2 TCG.

**Undecided on purpose.** Whether residual `NO_ACTION_ABORT` counts as agent execution failure or as model–harness incompatibility is **not** settled here; `empty_limit=3` is unchanged. §0.6 fixes the criterion by which that label will be chosen.

### 0.4 Dated amendment — parser equivalence gate, now material for every lane (2026-09-08)

An earlier draft of this section assumed the GPT lane was immune because it used typed `computer_call` items. **That assumption is withdrawn:** §0.2 establishes that `gpt-5.5` runs the *same generic XML executor* as the Qwen lanes, so the near-miss parser sits on the GPT path too. The hazard is not hypothetical instrument drift; it is a **known parser-availability difference between lanes**.

What differs across lanes is not only parser *logic* but whether the near-miss module was **importable and hooked at launch**. An earlier draft of this section guessed that the GPT lane lacked the wiring; **host verification reversed that** — the two launch scripts were the wrong way round:

| Fact (host-verified at `e8f6289`) | Status |
| --- | --- |
| `scripts/study2_exec_run.sh` L60 exports `PYTHONPATH="$H/agent-harness:$A/scripts:$A…"` | GPT lane **has** the wiring |
| `scripts/study2_run_mypcbench.py` L154–158 calls `apply_all()` → `apply_near_miss_parser()` → monkeypatch of `agents.qwen_cua`, **before** `rmb.main` | Hook applied per cell |
| Import failure behaviour | **Raises** — the cell cannot start, so a silent `ImportError` is impossible on this path |
| Live GPT process `313088` env | `PYTHONPATH=…/agent-harness:…/scripts:…/agent` |
| `paper2_exec_study2-gpt.log` | `near_miss_parser: True` from **leg 1** (`10:19:59Z`), 58 occurrences |
| `scripts/paper2_exec_run.sh` at `e8f6289` | **No** `PYTHONPATH` export, no near-miss call — this was the unwired path the §0.3 patch fixed |

So the whole GPT lane is instrument-homogeneous with near-miss **ON**, and no cell of it silently lost the module.

**Resulting pooling groups.**

| Group | Lanes | Near-miss |
| --- | --- | --- |
| A | GPT `study2-gpt` (leg 1 → now) at `e8f6289`; Flash post-patch job `58369` from leg 1 | **ON** |
| B | Flash pre-patch 26 checkpointed cells (finished `2026-09-07T05:58:52Z`, resume HEAD `aa060b2`, zero `near_miss_parser` lines) | **OFF** |
| ? | Qwen 3.5-9B — status not yet verified | **open** |

Group B is already invalidated by §0.3, so its exclusion costs nothing. **Group A pooling still needs one proof**, because `e8f6289` and `0773242` are different trees: the patch is claimed to add `classify_parse_event` audit labels only, so replay must show per-step parse results and terminal reasons **byte-identical** across the two parser versions. Audit labels may differ; decisions may not.

**The remaining scope question is 9B, not GPT.** If the 9B lane ran with near-miss OFF it belongs to group B and is not poolable with GPT or post-patch Flash, which would force a 9B rerun. Verify 9B **first** — it decides the rerun scope, exactly as before, but for the opposite reason from the one this section originally gave.

**Do not resume the remaining Flash legs.** Continuing the pre-patch output root under `e8f6289` would produce a corpus split across two parser configurations inside one lane — precisely what archiving the pre-patch corpus was meant to prevent. The fresh job `58369` from leg 1 is the correct construction; §0.3's no-resume rule and `DO_NOT_RESUME.txt` stand.

Claude is covered by the same replay proof, or by showing the canonicalisation cannot execute on the Claude path — whichever is evidenced, not asserted.

**One identifier to pin.** Earlier host reporting named the patch as `0773242` (*Wire near-miss parser on paper2_exec PYTHONPATH*, parser SHA256 `fa7263d6…`), while this round refers to a near-miss patch `e74ff99` @ `08:21Z`. These are presumably the implementation and the wiring commits, but the parser version per lane must be recorded by **SHA256 of the loaded module**, not by commit subject.

### 0.5 Dated amendment — two hosts in parallel (2026-09-08)

§0 originally required one model at a time with no interleaving. Superseded for **scheduling only**: Flash ran on HPC while GPT runs on node30, and Claude may start on the LARGE lane while the Flash rerun proceeds on SMALL. This changes nothing about \(\mathcal{M}\), \(\mathcal{T}\), \(D\), cell order, or per-cell policy, and no lane may read another lane's outcomes.

Comparability is only preserved if every lane, on every host, is verified identical on: qcow2 sha256 `7c2ddcf2c2e180d07af3a7971b97d45746605005040d74271fb3e494d2f43f59`, execution commit, parser SHA256 **and near-miss import status** (§0.4), `max_steps=80`, `empty_limit=3`, `timeout=7200`, `PAPER2_EXEC_SEED=20260904`, and the cell-order file (post-patch Flash records SHA256 `9e77c0ff61c41dbb904d2063b449d2f54e893164e8da8a0fcc3c0e90b7bed667`). Record this parity check per lane in the archive; a mismatch on any row makes that lane's legs non-poolable.

**Known mismatches already on the record**, to be resolved or disclosed rather than averaged over: the GPT lane runs executor `e8f6289` with a substituted scaffold (§0.2) while the Flash post-patch lane runs `0773242`; the Gate 0A smoke that established tool ownership ran at `dd43cbe` on the SMALL key, not at either matrix SHA or on the LARGE `008` lane; and the retry policy referenced by the post-patch run manifest is pinned to `1eea06b`. The `0773242` commit also edited this manifest on the host, so the finalising documentation commit must reconcile with that edit instead of appending over it.

### 0.6 Dated amendment — failure taxonomy and provider errors (2026-09-08)

**Per-cell logging.** Every cell records a terminal reason from `DONE` / `MAX_STEPS_NO_DONE` / `NO_ACTION_ABORT` / `PREDICT_CRASH` / `EXECUTOR_EXCEPTION`, plus, per action, one of `CANONICAL_PARSE` / `NEAR_MISS_CANONICALIZED` / `MALFORMED_REJECTED` / `EMPTY_ACTION`. This is audit metadata; it does not alter the canonical terminal rule (`VALID_DONE` iff the canonical last action is `DONE`), and a trajectory that solves the task without emitting `DONE` still has `valid_done=false`.

**Step metering differs by model and must be recorded, not normalised.** GPT counts tool-rounds, so `max_steps=80` yielded observed counts of 86–120, while the Qwen lanes count GUI actions. Log both step and round counts per cell. Consequence for reporting: non-`DONE`-at-budget rates are **not** directly comparable across models, and GPT received the *larger* effective budget, so its non-`DONE` count is not inflated relative to Qwen. Do not retune `max_steps` mid-experiment to equalise this.

**Provider-side errors are not model task failures.** The two Flash `PREDICT_CRASH` cases were Alibaba HTTP **400 `data_inspection_failed`** (content inspection, not 429, not transient). Policy: at most **one** infra retry on the same seed and cell id per §3; if it recurs, the leg is a technical failure recorded with the raw provider error, the retry attempted, and its final classification. It is never silently converted to `NO_ACTION_ABORT` and is always reported separately from agent-side formatting failures in the coverage table.

**Criterion (not the verdict) for the residual empty-action label.** The choice between *agent execution failure* and *model–harness incompatibility* for residual `NO_ACTION_ABORT` will be made from the post-rerun **taxonomy** — the share of `MALFORMED_REJECTED` shapes still unambiguous versus genuinely empty or ambiguous responses — and made **before** any STS, \(Y\), or rank is computed for that model. It may not be decided from the model's STS or its position in a ranking. Consequences of each label (coverage-only versus excluded-with-reason) follow `PAPER2_SPEC.md` §3 and §6.1.

### 0.7 Dated amendment — OpenRouter funding lost; Flash excluded, roster shrinks to three (2026-09-09)

**Facts (billing, not outcomes).** `SMALL_KEY` was exhausted mid-run, which is what produced the burst of 1-step `TERMINAL_FAIL` legs in post-patch Flash job `58369` (legs 5, 16, 17, 18 and neighbours). The LARGE OpenRouter key `008` is no longer available either. The only funded lane is **Anthropic native**. None of this derives from any score, STS, or rank — no analysis has been computed.

**Consequences, in order of importance.**

1. **The 1-step Flash legs are `INVALID_INFRASTRUCTURE`**, not agent failures and not evidence about the §0.3 patch. Key exhaustion, not the parser, killed them; the patch is not implicated. They are archived and excluded.
2. **Qwen 3.8-Flash has zero valid legs and no funded transport.** Pre-patch corpus invalidated (§0.3), post-patch run dead on billing. Flash is therefore **excluded-with-reason** — transport/billing unavailable, the same reproducible category §0.1 applied to GPT — not dropped for its scores, which were never computed. Its pre-patch corpus stays as **instrument-attrition evidence**, which the paper can report as a finding about the harness rather than about the model.
3. **The §0.4 gate changes meaning for 9B.** It was a *rerun-scope* question while SMALL was funded. With SMALL dead and `008` gone, a 9B rerun is impossible, so the gate now decides **whether 9B is poolable at all**: pass → 9B stays in the roster; fail → 9B is disclosed as instrument-incompatible and excluded.
4. **Roster arithmetic.** Ranked agents become 9B + GPT + Claude = **exactly three**, the minimum for a top-1 comparison. If 9B fails the §0.4 gate the roster is **two**, and per `PAPER2_SPEC.md` §6.1(c) Layer B is **not evaluated** and the paper reports Layer A, coverage, and the instrument with an under-powered reading. That is a stated outcome, reached by billing and instrument facts, not by looking at ranks.

**Action.** Run the Claude lane now on the Anthropic key, full 57 legs from leg 1, all other frozen knobs unchanged (§1–§3). Do not substitute a cheaper model for Flash's slot: adding an agent at this stage, after outcomes exist for two lanes, is exactly the post-hoc roster editing §3 forbids. If OpenRouter funding returns, Flash may be run **only** as a fresh lane from leg 1, disclosed with its funding gap and its own parity record.

### 0.8 Dated amendment — `008` is funded after all; Claude also runs the generic substrate (2026-09-09)

Two facts from the run host supersede parts of §0.7, which was written from a chat report of the funding state rather than from a balance record.

**(a) OpenRouter `008…9dd` is live with ≈ $1013.** §0.7's premise — "no funded transport" — therefore does **not** hold for Flash. Consequences: Flash is **runnable again as a fresh lane from leg 1** (never a resume of `58337`/`58369`), so its exclusion in §0.7 is **withdrawn as premature**; and the §0.4 gate for 9B reverts to a *rerun-scope* question, since a 9B rerun is purchasable again. Roster can be four. **Funding status must be read from a recorded balance at lane start, not from prose** — this section exists because the reverse happened.

**(b) The Claude lane is not Anthropic native.** As launched: `model=anthropic/claude-opus-4.6` through the **same generic XML bridge over OpenRouter chat-completions** (`qwen_cuabash`, key `008…9dd`), PID `920150`, log `results/paper2_exec_study2-claude.log`, leg 1 `retrieval-f010` G0, `max_steps=80`, seed `20260904`, 57 legs, no partial filter, no resume of Flash/GPT state. §1's frozen row (`claude-opus-4-6` / `claude_cuabash` / Anthropic) describes the **Paper 1** instrument, exactly as the seal does for GPT; it is **not** rewritten to match runtime.

**What this buys and what it costs.** All Study 2 lanes now share one instrument — generic XML protocol over OpenRouter chat-completions — so the roster is compared with the **harness held constant**, which is cleaner than the sealed plan and is the honest way to describe it. The cost is that `PAPER2_SPEC.md` §3's design minimum "at least two provider APIs" is satisfied only by counting **upstream** providers (Alibaba, OpenAI, Anthropic) behind a **single API surface**. State it that way; do not claim two API surfaces.

**Canonical sentence for the Claude lane** (parallel to §0.2, mandatory wherever the roster appears):

> The Study 2 Claude lane measures **`anthropic/claude-opus-4.6` on the frozen generic XML CUA protocol** (OpenRouter `chat/completions`, no `tools`). It is **not** the sealed Paper 1 instrument (`claude-opus-4-6` / `claude_cuabash` / Anthropic native). Comparability is within the Study 2 generic-executor roster.

**Budget hazard to monitor (operational, not a design change).** On chat-completions the client resends the whole trajectory each step, so per-leg cost grows roughly with the square of step count, and Opus-class pricing with screenshots makes 57 × up to 80 steps the most expensive lane by a wide margin. Record spend after the first ~5 legs and extrapolate before assuming 57 legs fit in $1013. If the balance cannot cover both, **Claude is the primary lane and takes priority**; Flash is cheap and can be secured afterwards from whatever remains. Do **not** run Flash concurrently on the same key while Claude is live: shared-key 429s would be charged to Claude's legs as infra retries under §3, and the primary lane must not be degraded to save queue time.

**Unchanged by this section.** GPT stays frozen and complete (57/57, `GPT_FROZEN.txt`, checksums in `out/study2_gpt_freeze.json`, archive `chmod a-w`); the invalidated Flash corpora stay invalid; §0.6 taxonomy and §6.1 analysis rules stand.

### 0.9 Dated finding — Claude does not terminate; diagnosed as behaviour, not parser (2026-09-09)

Legs 1–4 of the Claude lane all burned the full budget (81, 80, 80, 80 steps) with rubric scores 0.00, 0.75, 0.75, 0.30 and **zero** `DONE`. Because an agent that scores while never closing the episode is exactly the shape of a terminal-detection defect, the lane was diagnosed read-only before accumulating more legs.

**Verdict: genuine non-termination, not a swallowed `DONE`.** Across those legs: 0 occurrences of `action=terminate`, 0 of `action=answer` (which also maps to `DONE`), 0 literal `DONE` in any raw response, 0 `traj.action == "DONE"`. The last five steps of every leg are still `left_click` / `key` / `type` / `wait` / bash — navigating, opening consoles, scraping — with no prose completion claim and no malformed terminate tag. An initial "complete" hit was a false positive from an autocomplete widget.

**The bridge is not blind to Claude.** The canonical form the parser accepts is `<function=computer_use><parameter=action>terminate</parameter><parameter=status>success</parameter>`, and **Claude emitted exactly that in its Gate 0A smoke** (`results/paper2_exec/gate0a-claude/`, P4 `valid_done=true`, step 3 `action: DONE`). GPT emits it too on the same task (`retrieval-f017` G0, step 25). So the failure is Claude-in-this-matrix declining to terminate, not a parser gap.

**Actions: none.** The lane keeps running to 57. `DONE` semantics, `inspect_last_action`, and Gate −1.5 parity are untouched, and near-miss is **not** extended to prose "finished/complete" — §0.3's prohibition on converting a missing action into `DONE` stands. Only a **malformed `terminate` XML** would reopen hypothesis (b); no such case exists.

**Reporting rule (pre-registered here, before any pair count).** The rubric is judged per-step from screenshots and is independent of `VALID_DONE`, so these legs are the sharpest instance in the project of *score without completion* — an agent earning 0.75 while never closing the episode. Two constraints on how it is written:

1. It is a statement about **model × protocol**, not about Claude's capability: the generic XML prompt and its termination instruction were not authored for Claude. Any claim must read "Claude Opus 4.6 under the Study 2 generic XML protocol did not terminate", never "Claude cannot complete these tasks". Whether the system prompt instructs termination explicitly is an **open read-only check**; the answer changes how strong the statement may be, and it must be resolved before the finding is written up.
2. Legs without `DONE` remain **invalid pairs**. They are coverage, not \(Y=0\), and no pair is manufactured from a high rubric score.

**Roster consequence.** If non-termination persists across the lane, Claude has 0 valid pairs, is **reported but not ranked** (§3, \(n_{\min}=3\)), and the primary lane contributes nothing to Layer B. Ranked agents would then be 9B + GPT (+ Flash if it runs), which makes the §0.4 gate on 9B and the Flash lane decisive for whether Layer B is evaluable at all under `PAPER2_SPEC.md` §6.1(c). Running all 57 legs is still correct: 0/57 is a far stronger statement than 0/4, and the schedule is pre-registered.

**Update, same day — the lane-wide reading is withdrawn.** Leg 8 `counterfactual-f013` G0 terminated: `DONE` at **21 steps** with rubric **1.00**. So Claude does emit the canonical terminate form inside the matrix, and the finding is **not** "Claude never terminates under this protocol". Through 8 legs the pattern is that termination coincides with *solving*: the one `DONE` is short and perfect, while the seven non-terminating legs each ran the full budget at 0.00–0.75. Provisional reading, to be settled on the full 57: **non-termination is a symptom of not solving, not a protocol quirk** — the agent keeps verifying when it has not converged. That is a weaker claim about the protocol and a more ordinary one about the agent, and it must replace the earlier wording wherever the finding is written.

**Analysis consequence, and it cuts against Claude's own numbers.** If termination coincides with solving, then for Claude the valid-pair filter selects its *successful* subset far more sharply than it does for GPT, whose `DONE` legs span a wide score range. Claude could therefore enter Layer B with very few pairs, all scoring near 1.00, and take \(\arg\max\overline{S}\) purely because it was scored only on its wins. This is exactly the failure mode §6.1(f) was pre-registered for, so the common-support analysis and the printed \(|\mathcal{A}_i|\) are not optional here — they are what stops that artefact from being read as a result. §6.1(e)'s completion-conditional reporting applies with extra force to this lane.

---

## 1. Harness freeze

| Knob | Frozen value |
| --- | --- |
| Branch / analysis commit | `phase-a-results` @ `4f45faf` (or later **execution-only** commits that do not change \(\mathcal{M}\)/\(\mathcal{T}\)/\(D\)) |
| Models | `claude-opus-4-6` / `claude_cuabash` / Anthropic (`LARGE_KEY` lane) |
|  | `gpt-5.5` — sealed as `openai_cuabash` / OpenAI direct (Paper 1 instrument), **executed in Study 2** as `openai/gpt-5.5` on the frozen generic XML protocol (`qwen_cuabash` + OpenRouter chat-completions, no `tools`, no `previous_response_id`) at `e8f6289`, `LARGE_KEY` `008`. Substrate footnote is mandatory: §0.2 (2026-09-08) |
|  | `qwen/qwen3.8-flash` / `qwen_cuabash` / OpenRouter (`SMALL_KEY` lane) |
|  | `qwen/qwen3.5-9b` / `qwen_cuabash` / OpenRouter (`SMALL_KEY` lane) |
| Runner pattern | Paper 1 Stage-4 / Phase-B shells: `run_mypcbench.py --backend qemu` |
| `max_steps` | **80** |
| `timeout` | **7200** s |
| `MYPCBENCH_VM_READY_TIMEOUT` | **3600** |
| `MYPCBENCH_SKIP_QCOW2_REFRESH` | **1** |
| Inject | `scripts/cf_inject.py` + `cf/paper2_interventions.json` (PASS variants only) |
| Parser | Pre-patch for the 9B and GPT lanes; post-patch (enumerated Qwen canonicalisation, §0.3) for the Flash rerun and Claude — poolable only if the §0.4 equivalence gate passes. Record the parser version per lane |
| Judge | `judge_results.py`, `MYPCBENCH_JUDGE_FLAVOR=per_step` (score only; not STS) |
| Persona | `michael.scott@dundermifflin.com` |
| Image | Record `MYPCBENCH_QCOW2` path + sha256 **before cell 1** on the run host (fill below) |

**Image (fill on run host before cell 1):**

```
MYPCBENCH_QCOW2=/mnt/data2/Vinh/agent/external/MyPCBench-main/mypcbench-vm/mypcbench.qcow2
sha256=7c2ddcf2c2e180d07af3a7971b97d45746605005040d74271fb3e494d2f43f59
recorded_at_utc=2026-09-04T07:55:32Z
host=node30
```

Pinned base qcow2 for all 228 cells (Paper 1 / Phase B image). Overlays are per-boot ephemeral; do not swap this base mid-run. `MYPCBENCH_SKIP_QCOW2_REFRESH=1` keeps the pin from auto-refresh.

System prompt / tool config: whatever each `*_cuabash` agent ships in this checkout at the tagged execution commit — do not edit agent wrappers mid-run.

---

## 2. Seed freeze

| Seed | Value | Role |
| --- | --- | --- |
| `PAPER2_EXEC_SEED` | **20260904** | Master seed (new; not `20260826`, not multi-I inventory seed alone) |
| Task order | `Random(PAPER2_EXEC_SEED).shuffle(sorted(T))` once, written to `out/paper2_cell_order.json` **before** cell 1 | Fixed schedule |
| Multi-I order | For each multi-I task: legs `G0` → `G1`(I1) → `G2`(I2) in that order; tasks still follow cell order | No fishing I2 first |
| Episode / env RNG | If harness exposes a seed, set from `PAPER2_EXEC_SEED` + `(model, task, leg)` hash; if not, record “harness-default” per leg | No silent mid-run change |

Write `out/paper2_cell_order.json` and this filled image block **before** the first agent call.

---

## 3. Cell execution policy

| Rule | Frozen choice |
| --- | --- |
| Runs per cell | **1** (one trajectory per `(M, T, leg)`) |
| Legs per task | Base: `G0` then `G1` (I1). Multi-I: then `G2` (I2). Clean guest / snapshot restore between legs (same hygiene as inject-probe) |
| Infra retry (Control API down, QEMU won’t boot, disk I/O) | **At most 1** retry, **same** seed / same cell id; log `infra_retry=1` |
| Agent failure (EMPTY_XML, STEP_LIMIT, AGENT_FAIL, non-DONE) | **No retry** — record as execution failure; not tracking miss; not a reason to drop model |
| API 429 / transient provider error | Treat as infra: ≤1 retry same seed; if still fail → technical failure for that leg |
| Provider content-inspection reject (e.g. Alibaba 400 `data_inspection_failed`) | Same ≤1 retry, then technical failure with the raw error logged; reported separately from agent formatting failures, never recoded as `NO_ACTION_ABORT` (§0.6) |
| Interrupted mid-leg | **Rerun from start** of that leg on clean guest; do not resume mid-trajectory |
| Partial schedule | Do not drop remaining models/tasks to “finish faster.” Pause whole experiment if needed; resume same cell order |

Valid pair (analysis): both legs of a scheduled pair `DONE` (Paper 1 definition). Incomplete ≠ \(Y=0\).

---

## 4. Workflow

1. Tag: `paper2-exec-freeze` on the commit that contains this file + filled image sha + `paper2_cell_order.json`.  
2. Run legs per the §0 status table. GPT continues under §0.2; Flash reruns from leg 1 after the §0.3 validation package is reviewed; Claude starts when the LARGE lane frees.  
3. Run the §0.4 parser equivalence gate — **9B first**, since it fixes the rerun scope — and the §0.5 host parity check for every lane.  
4. Collect raw artifacts under a single tree (e.g. `results/paper2_exec/`), each lane tagged with execution commit, parser version, adapter freeze commit (GPT), qcow2 sha, seed, cell order, host. Keep the 4 `INVALID_INFRASTRUCTURE` GPT legs and the invalidated Flash pre-patch corpus out of every analysis table.  
5. Classify valid pairs / coverage with the §0.6 taxonomy; settle the residual empty-action label by the §0.6 criterion.  
6. **Then** open Layer A, then Layer B, under `PAPER2_SPEC.md` §6 and §6.1 (per-agent \(n_{\min}=3\), leave-one-pair-out stability, no optional stopping, completion-conditional reporting).

Allowed mid-run monitors: API health, disk, QEMU, corrupted artifacts, terminal-reason coverage.  
Forbidden mid-run: STS, \(\Delta S\), ranks, \(D\)-matching, swapping models, rewriting \(D\) or interventions, editing a lane's executor or transport after its leg 1, broadening the parser patch beyond the enumerated shapes, and extending the leg set to improve yield.

---

## 5. Infra stop (only halt condition)

Stop the full experiment if and only if continuing would invalidate comparability (wrong image, wrong inject file, systematic harness corruption). File a dated note; do not quietly change \(\mathcal{M}\) or \(\mathcal{T}\).

**Per-lane stop (narrower, used twice so far).** A single lane may stop without halting the others when the defect is provably confined to that lane's transport (§0.1, §0.2) or to an instrument that discards unambiguously intended actions (§0.3). Requirements, all of them: a dated amendment in this file; the partial corpus archived and labelled invalid rather than deleted or merged; the defect evidenced from artifacts, not from a failure rate; and the lane restarted from leg 1 rather than resumed. A lane may never be stopped because of its scores, its STS, or its rank.

---

## 6. Amendment index

| § | Date | Subject |
| --- | --- | --- |
| 0.1 | 2026-09-06 | GPT paused — OpenRouter transport invalid, native 403 |
| 0.2 | 2026-09-08 | GPT lane ran a **substituted substrate** (generic XML protocol / chat-completions); no adapter exists; native Gate 0 FAILED; §0.1 chain never closed; canonical reporting sentence + mandatory substrate footnote; seal not rewritten |
| 0.3 | 2026-09-08 | Flash stopped as Gate 0A instrument defect; pre-patch corpus invalidated |
| 0.4 | 2026-09-08 | Parser equivalence gate; GPT lane verified near-miss **ON** from leg 1; pooling groups; 9B status is the open scope question |
| 0.5 | 2026-09-08 | Two hosts in parallel; per-lane parity check |
| 0.6 | 2026-09-08 | Failure taxonomy, step metering, provider 400s, empty-action criterion |
| 0.7 | 2026-09-09 | OpenRouter funding lost; Flash excluded-with-reason; 9B gate becomes in/out; roster = 3 (or 2 → Layer B not evaluated); run Claude |
| 0.8 | 2026-09-09 | `008` funded after all → §0.7 exclusion of Flash **withdrawn**; Claude also runs the generic XML substrate, not Anthropic native; single API surface; budget hazard |
| 0.9 | 2026-09-09 | Claude non-termination diagnosed as behaviour, not a swallowed `DONE`; no patch; model × protocol reporting rule; roster consequence if it persists |
| `PAPER2_SPEC.md` §6.1 | 2026-09-08 | Power, rank stability, no optional stopping, completion-conditional reporting |
