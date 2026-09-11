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
| 1 | Qwen 3.5-9B | SMALL (exhausted), Study 1 runner | **COMPLETE but OUT of Layer B** — §0.4 replay PASS (0 hits / 0 parse changes); excluded for instrument + transport mismatch and \(\lvert\mathcal{A}\rvert=0\); coverage only (§0.10) |
| 2 | Qwen 3.8-Flash | `Vinh-` HPC post-patch | **COMPLETE + FROZEN** — 57/57, 29 `DONE` / 28 `TERMINAL_FAIL`, \(\lvert\mathcal{A}\rvert=8\); canonical `.../hpc-flash-small-gate0a-postpatch` (`dr-xr-xr-x`); no merge to `Vinh/` (not writable); §0.15 |
| 3 | GPT-5.5 | `Vinh` HPC (also was node30) | **COMPLETE + FROZEN** — 57/57, 32 `DONE` / 25 `TERMINAL_FAIL`, \(\lvert\mathcal{A}\rvert=9\); substituted substrate §0.2 |
| 4 | Claude Opus 4.6 | `Vinh` HPC, generic XML bridge | **COMPLETE + FROZEN** — 57/57, 4 `DONE` / 53 `TERMINAL_FAIL`, \(\lvert\mathcal{A}\rvert=1\); report only; §0.14 |

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

### 0.10 Dated resolution — 9B is out of Layer B; §0.4 replay PASS with one half inconclusive (2026-09-09)

Offline, no API, Claude untouched (PID `920150`, 18/57). Artifacts: `out/study2_section0_notes.md`, `out/study2_gate04_9b_nearmiss.json`.

**§0.4 replay on 9B.** 57 trajectories, 480 steps carrying a `response`, replayed OFF (`qwen35vl_agent.py` `f478ebe6…`, Gate −1 pin) against ON at `e8f6289` (`near_miss_xml.py` `c0723e43…`): **0 near-miss hits, 0 parse changes → PASS**. Adding near-miss does not change 9B's parses, so no lane needs rerunning on that account. **One half is inconclusive:** commit `0773242` — reported earlier as the Flash patch with parser SHA256 `fa7263d6…` — **is not present on the host**, so `e8f6289` vs `0773242` could not be compared. That is the second time this identifier has not survived checking, which is why §0.4 requires parser identity by **SHA256 of the loaded module**, never by commit subject. Until it resolves, no parity claim may cite `0773242`.

**9B does not enter Layer B**, on two independent grounds. Seven-item check:

| # | Check | 9B vs Study 2 |
| ---: | --- | --- |
| 1 | Universe \(\mathcal{T}\) | same (25 tasks / 57 legs) |
| 2 | Instrument | **different** — Study 1 runner, not the Study 2 bridge |
| 3 | Transport | **different** — SMALL / `call_llm`, not `008` chat-completions |
| 4 | Judge | same pin `cd88a37c…` |
| 5 | Terminal rule | same Gate −1.5; 0 mismatches |
| 6 | Gold | same analysis universe |
| 7 | \(\mathcal{A}\) definition | same (G0 ∧ G1 `VALID_DONE`) — but 9B has **0 valid pairs** |

Sharing \(\mathcal{T}\), judge, and gold does not repair an instrument and transport mismatch, and \(|\mathcal{A}_{9B}|=0\) makes the question moot regardless. 9B is **coverage, reported not ranked**.

**Roster arithmetic, and it now rests on Flash.** Ranked candidates are GPT (9 valid pairs) and Claude (≈3 projected). With 9B out, **Flash decides whether Layer B exists at all**: Flash with ≥3 valid pairs gives three ranked agents; Flash without them leaves two, and `PAPER2_SPEC.md` §6.1(c) then applies — Layer B is not evaluated and the paper reports Layer A, coverage, and the instrument. Flash has moved from "robustness" to load-bearing.

**§0.9 addendum — the prompt.** The `qwen_cuabash` path does tell the agent *how* to stop (`action=terminate`, `status=success|failure`, final answer written before the stop signal) but carries **no** `COMPLETION_DISCIPLINE` injection telling it not to stop early. So §0.9 may not be written as "the protocol pushed the model to exhaust the budget"; the modest wording stands. The 3-step aborts are an XML envelope problem, unrelated to the terminate instruction.

### 0.11 Dated issue — near-miss coverage is asymmetric across dialects (2026-09-09)

**Fact.** Claude's two 3-step legs (`counterfactual-f002` G0 and G2) are `EMPTY_XML` ×2 → `NO_ACTION_ABORT`, labelled **`EMPTY_XML_ABORT`**: the model emitted `<function=left_click>` and `<function=triple_click>` instead of the `computer_use` envelope, the parser closed, no action issued, rubric 0.0. G1 of the same task ran the full 80 steps, so the environment was alive. Near-miss did **not** rescue these (`codes = []`).

**Why this is more than a label.** §0.3 licensed stopping and patching Flash precisely because *an unambiguously intended action was being discarded on an envelope technicality*. `<function=left_click>` is the same category. But the enumerated canonicalisation was built from **Flash-derived fixtures**, so the parser is now more forgiving of Flash's dialect than of Claude's. That is a **per-model instrument advantage**, the exact hazard §0.4 exists to prevent, and it would flow straight into \(\overline{S}\) and \(\overline{\mathrm{STS}}\) through which legs reach `DONE`.

**Not resolved by patching now.** Extending the enumeration to Claude's shapes would require rerunning Claude from leg 1 (§0.3 terms), and patching mid-lane is forbidden. Consistency is therefore restored in **analysis**, not in the harness.

**Pre-registered, before any pair count.** Report per lane the count of `NEAR_MISS_CANONICALIZED` actions and of `MALFORMED_REJECTED` shapes with unambiguous intent, and run Layer A/B **twice**: once as executed, and once with near-miss rescues **treated as rejected**, recomputing terminal outcomes from the archived trajectories with the replay machinery. If the two agree, the asymmetry is immaterial and that is stated. If they disagree, the as-executed ranking is **not** reported as confirmatory, because part of it would rest on which model's dialect happened to be in the fixture set. Neither version may be chosen after seeing which is more favourable.

**Also required:** the same replay must report the rescue count for the **GPT** lane, which ran with near-miss ON. A large GPT rescue count against zero for Claude is the same asymmetry in a second place.

### 0.12 Dated verification — judge frame handling is sound, and \(S\) is exactly re-derivable offline (2026-09-09)

**Why this was checked.** §0.11 established that per-model instrument advantages flow into \(\overline{S}\). The score itself is produced by `MYPCBENCH_JUDGE_FLAVOR=per_step` from screenshots, so the *frame-selection* path is part of the instrument and had never been audited. Three failure modes were plausible and all would have moved \(S\) silently: lexicographic frame ordering, frame-count asymmetry under a max-reduce, and step-budget asymmetry under a max-reduce.

**Frame ordering — clean.** Host-reported code path: `build_rubric_bundle` → `_index_steps_traj_layout` reads `traj.jsonl` line by line and takes each row's own `screenshot_file` as authoritative, falling back to a directory glob only when that field is empty; it then sorts **numerically** on `step_num` with a stable sort, so rows sharing a `step_num` keep trajectory order. The lexicographically-sorted `artifacts.screenshots` list belongs to the legacy `context/` layout and is **empty** on Paper 2 lanes. There is therefore no `step_10 < step_2` hazard. `step_num` is **not unique** — one `predict()` emitting several GUI actions writes one traj row and one PNG per action at the same `step_idx` — so any downstream re-measurement must join on `screenshot_file`, never on `step_num` alone (recorded in `P3_HARNESS_CONSTRAINTS.md`).

**Frame-count asymmetry — mechanism real, effect exactly zero.** Frames per distinct step differ materially by model across the 94 locally-archived Paper 1 / Phase-B cells that carry `per_step_scores`: `openai` 1.224, `qwen35-9b` 1.183, `qwen35-a3b` 1.066, `qwen38-flash` 1.013, `claude` 1.007. Because scoring is a max-reduce, extra frames are weakly score-increasing, which is a per-model advantage of the §0.11 class. Re-reducing every cell with **one frame per `step_num`** (first-frame and last-frame policies both) changes \(S\) in **0 of 94 cells**, mean shift 0.00 for every model. The duplicate frames are intra-`predict()` pairs such as `moveTo`+`scroll`, i.e. near-identical screens, so no rubric item was ever carried by the extra frame alone. Recorded as immaterial; no analysis branch needed.

**Step-budget asymmetry — no inflation.** A max-reduce over 80 steps grants more draws than one over 9, which would reward long flailing episodes. It does not: \(\mathrm{corr}(\text{steps}, S) = -0.275\) over the 94 cells, and cells in the 61+ step bucket average \(S = 23.3\) against 62–67 for the 1–10, 11–30 and 31–60 buckets. Long episodes are long because the agent is failing, and the max-reduce does not overturn that. This is the opposite sign of the hazard, so `MAX_STEPS_NO_DONE` legs are **not** score-inflated.

**Score formula, reproduced exactly.** \(S = 100 \sum_i w_i \max_{\text{frames}} s_i\), with \(w_i\) from `rubrics[i].weight` and \(s_i\) the per-frame binary item score. This reproduces the stored `score` on **94/94 cells with zero deviation**. Consequence: every re-reduction robustness analysis — dropping frames, restricting to pre-`DONE` steps, reweighting, dropping items — is computable from the archived `rubric_result.json` at **zero judge cost**. §0.11's dual analysis needs replay only for terminal-outcome recomputation, not for rescoring.

**Scope.** These numbers come from the 94 locally-archived Paper 1 / Phase-B cells, not the Study 2 corpus, which lives on the run hosts. The harness is the same, so the mechanism findings carry; the three quantities (frames per step by lane, dedup shift, step–score correlation) must be recomputed on the Study 2 archives after `LANE_COMPLETE`, which is free and requires no API calls.

### 0.13 Dated amendment — roster arithmetic at 35/57, recorded before the Claude lane closes (2026-09-10)

**Why now.** §0.9's "roster consequence" paragraph was written when 9B was still a candidate for ranking. §0.10 then removed 9B from Layer B. The arithmetic in §0.9 is therefore stale, and the correct arithmetic must be on paper **before** the Claude lane reaches `LANE_COMPLETE`, so that whichever branch of `PAPER2_SPEC.md` §6.1(c) fires was fixed in advance of the count.

**Host-reported state, 2026-09-10 ~02:21 UTC.** Claude lane 35/57: **2 `DONE`**, 33 `TERMINAL_FAIL`. The two `DONE` legs are legs 8 and 9, both on `counterfactual-f013` (G0 and G1) — i.e. **one** valid pair, not two. Legs 10–35 added **zero** `DONE`; legs 21–35 all burned the budget. Now on leg 36 (`aggregation-f040` G0), ~21 legs and ~14 h remaining at the observed pace.

**Not a `max_steps` breach.** `counterfactual-f003` G0/G1/G2 report 87–91 steps against `max_steps = 80`. This is the §0.6 metering difference: the checkpoint counts `traj.jsonl` rows, which include tool-rounds, while the budget is enforced on `step_idx`. §0.12 confirmed the same one-row-per-round layout. No knob moved.

**Consequence, stated in advance.** \(n_{\min} = 3\) valid pairs is required to rank. Claude currently holds 1. Its `DONE` events are clustered by task rather than independent (§0.9: termination coincides with solving), so reaching 3 would require **two further tasks with both G0 and G1 terminating** inside the remaining ~7 tasks, after 26 consecutive legs with none. The realistic landing point is **Claude below \(n_{\min}\), reported but not ranked**.

With 9B out (§0.10), the ranked roster is then **GPT + Flash = 2 agents**, which is fewer than three and therefore triggers `PAPER2_SPEC.md` §6.1(c): **Layer B is not evaluated.** Paper 2 in that branch reports Layer A, coverage, the completion-conditional bias analysis, and the instrument findings of §§0.2–0.12, and states that agent *selection* could not be tested at this \(n\) — it does not report a two-agent ranking as if it were the pre-registered Layer B result.

**What is forbidden here.** Lowering \(n_{\min}\), counting G2 into pairs, admitting non-`DONE` legs as \(Y = 0\), re-ranking on \(\overline{S}\) alone, or stopping the Claude lane early to reallocate budget. `PAPER2_SPEC.md` §6.1 bars optional stopping, and 1/57 is a far stronger reported number than 1/35. The lane runs to 57.

**Still live (at writing of §0.13).** Flash had not started its fresh lane. Both branches were written down; neither may be selected after the count. **Superseded by §0.14:** Claude closed at \(\lvert\mathcal{A}\rvert=1\).

### 0.14 Dated freeze — Claude lane COMPLETE (2026-09-10)

**Host-reported terminal state.** 57/57 legs. **4 `DONE` / 53 `TERMINAL_FAIL`.** Archive write-locked (`chmod a-w`); CHECKPOINT overwrite blocked. Marker `results/paper2_exec/study2-claude/CLAUDE_FROZEN.txt`; checksum `out/study2_claude_freeze.json` (`62774f95…`); locked: Claude archive, log, pid, `paper2-study2-claude-*`. Flash not touched (`study2-flash` still `755`). GPT remains frozen from earlier.

**Valid-pair count (authoritative).** The four `DONE` legs are `counterfactual-f013` G0, `counterfactual-f013` G1, `counterfactual-f005` G0, `contradiction-f014` G1. Only **one** task has both G0 and G1 `DONE` → \(\lvert\mathcal{A}_{\text{Claude}}\rvert = 1\). Below \(n_{\min}=3\): Claude is **reported, not ranked**.

**Roster consequence (now factual, not projected).** With 9B out (§0.10) and Claude out of ranking, the only agents that can enter Layer B are **GPT + Flash**. If Flash reaches \(n_{\min}\), ranked roster = 2 → `PAPER2_SPEC.md` §6.1(c) fires (**Layer B not evaluated**); §6.1(g) signed-difference may be reported as **exploratory** only. If Flash also fails \(n_{\min}\), ranked roster ≤ 1 → same §6.1(c) reading, and (g) is void (needs two ranked agents).

**Forbidden.** Resume / rewrite / re-judge any Claude cell. No lowering \(n_{\min}\), no admitting non-`DONE` as \(Y=0\), no counting G2 into pairs, no optional stopping of Flash.

**Next.** Flash continues its fresh lane. Offline work that needs Claude archive (judge-frame audit, near-miss rescue counts for §0.11, completion-conditional §6.1(e)) waits until Flash also freezes, or may start read-only on the locked Claude tree now — never mutating it.

### 0.15 Dated freeze — Flash lane COMPLETE; Study 2 execution closed (2026-09-11)

**Host-reported.** Flash 57/57 frozen at canonical path  
`/data2/hpcshared/Vinh-/agent/results/paper2_exec/hpc-flash-small-gate0a-postpatch` (`dr-xr-xr-x`). GPT/Claude untouched under `Vinh/`. No re-judge, no merge of pre-patch Flash corpora. Copy into `Vinh/` skipped (tree not writable). Host analysis commit `be1c4c6` (docs/tables only, no PNG, not pushed).

**Final \(\lvert\mathcal{A}\rvert\)** (G0∧G1 `VALID_DONE`, G2 ignored, \(n_{\min}=3\)):

| Lane | Cells | DONE/FAIL | \(\lvert\mathcal{A}\rvert\) | Rank |
| --- | --- | --- | --- | --- |
| GPT | 57 | 32/25 | **9** | exploratory (with Flash) |
| Flash | 57 | 29/28 | **8** | exploratory (with GPT) |
| Claude | 57 | 4/53 | **1** | report only |

**Roster.** Exactly two agents at \(n_{\min}\) → `PAPER2_SPEC.md` §6.1(c): **Layer B not evaluated**. §6.1(g) applies.

**§6.1(g) partial (host).** Common support \(\lvert\mathcal{A}^\cap\rvert=4\) tasks. Mean base-leg \(S\) difference Flash−GPT = **+46.5** (bootstrap CI 21–72). **\(\Delta\mathrm{STS}\) / \(Y\) not computed** — no locked \(\hat D\) extractor yet (`DESIGN.md` §3.1). Rubric \(S\) is on disk; matching code exists under `protocol/matching.py` but extraction from final-answer text is still coder-protocol, not sealed.

**Next (blocking for a complete §6.1(g)).** Lock extractor → code \(\hat D\) on all valid-pair legs for GPT+Flash (+ Claude coverage) against guest gold → run `protocol/matching.py` → fill \(\Delta\mathrm{STS}\), sign disagreement frequency, LOPO. Do not invent STS from \(\Delta S\) or judge text.

### 0.16 Dated analysis — \(\hat D\) locked; §6.1(g) filled; exploratory sign disagreement (2026-09-11)

**Extractor / STS commits (host).** \(\hat D\) extractor locked at `3242c30`. STS/\(Y\) tables at `71a405d`. Archives not mutated; no re-judge; extractor **not** retuned after seeing STS.

**Layer A (degenerate).** \(Y=0\) on every pair of every \(\mathcal{A}\), so \(S^0\) cannot separate \(Y=1\) from \(Y=0\) — there is no \(Y=1\). Mean \(S^0\) on \(\mathcal{A}\): GPT **69.333** (n=9), Flash **95.750** (n=8), Claude **100** (n=1, coverage only). Mean pair-STS on \(\mathcal{A}\): GPT **0.130**, Flash **0.229**, Claude **0**. High \(S\) on \(\mathcal{A}\) is not evidence of state tracking.

**§6.1(g) on \(\mathcal{A}^\cap\), exploratory only.** \(\mathcal{A}^\cap = \{\)`counterfactual-f010`, `preference_inference-f014`, `retrieval-f002`, `retrieval-f009`\(\}\), \(|\mathcal{A}^\cap|=4\).

| | GPT | Flash |
| --- | --- | --- |
| mean \(S^0\) | 49.5 | **96.0** → \(\arg\max\) **Flash** |
| mean pair-STS | **0.250** | 0.208 → \(\arg\max\) **GPT** |
| \(Y\) (binary track) | 0/4 | 0/4 |

\(\operatorname{sign}(\Delta S^0)\neq\operatorname{sign}(\Delta\mathrm{STS})\) on **4/4** tasks (\(\Delta=\) Flash−GPT). Paired bootstrap, seed `20260904`, \(B=5000\): \(\Delta S^0 = \mathbf{+46.5}\) (95% CI 21.0–72.0); \(\Delta\mathrm{STS} = \mathbf{-0.042}\) (95% CI −0.125–0.0). **LOPO fragile:** leaving out `retrieval-f009` makes \(\arg\max\) STS a **tie**; the other three leave-outs keep Flash on \(S^0\) and GPT on STS. Per §6.1(b)/(g) this is exploratory; Layer B remains **not evaluated** (§6.1(c)).

**Mandatory caveats (do not drop in write-up).**

1. \(Y=0\) on **every** valid pair in \(\mathcal{A}\) (GPT 9, Flash 8, Claude 1). STS is near-floor; much of the mass is `reported=None` (fail-closed extract) or G1 inject surface (e.g. `SM-88431` vs `SM-88431-CF`).
2. **Full-\(\mathcal{A}\) vs common-support flip (§6.1(f)).** On full \(\mathcal{A}\), Flash is higher on **both** \(S^0\) and STS (0.229 vs 0.130). On \(\mathcal{A}^\cap\), GPT is higher on STS. That is a **support flip** and is itself a reported result: selection is sensitive to which tasks each agent finished. It is not licence to pick the prettier denominator.
3. \(\Delta\mathrm{STS}\) CI reaches 0.0 and the magnitude is small against the \(S\) gap; the common-4 \(\arg\max\) disagreement ranks **small residuals**, not agents that tracked. Claim language: *signed-difference exploratory disagreement on common support*, never “Layer B confirms decision consequence” and never “GPT is more reliable than Flash”.

**Artifacts (imported to local, §0.17):** `out/study2_layerA.md`, `out/study2_completion_conditional.md`, `out/study2_selection_g.md`, `out/study2_selection_g_sts.*`, `out/study2_sts_pairs.*`, `out/study2_valid_pairs.*`, `out/study2_hatd_extractor_lock.*`, `out/study2_gold_path_lock.*`, `out/study2_hatd_legs.jsonl`, `out/study2_paper_results.md`.

**Paper 2 status.** Execution closed. Selection claim stays under-powered / exploratory. Layer A + completion-conditional (§6.1(e)) + instrument §§0.2–0.15 + this §0.16 package are the confirmatory-adjacent deliverables. The \(Y=0\) / near-floor STS pattern is primary fuel for Paper 3's measurement-interface claim, not a reason to reopen extractor knobs.

### 0.17 Dated import — host history landed locally; §0.4/§0.10 debt CLOSED; two manifests reconciled (2026-09-12)

**How it landed.** GitHub push from the run host is impossible (deploy key is read-only), so the host produced `generic-executor-phase1-8197110.bundle` (66 KB) plus a 24 KB tarball of `out/`. `git bundle verify` PASS; prerequisite `e8f6289` was already present locally; fetched to `refs/remotes/hpc/generic-executor-phase1`, tip `8197110`. Five commits: `0773242` → `be1c4c6` → `3242c30` → `71a405d` → `8197110`. Tables copied into `out/` (host's `out/paper_results.md` renamed `out/study2_paper_results.md` to avoid collision with the Paper 1 file of that name).

**§0.4 / §0.10 debt is closed by evidence, not assertion.** §0.10 recorded `0773242` as *absent on host*, leaving the Flash half of the parser-equivalence gate **inconclusive**. The commit is now in hand: `0773242053e66fe2391f960d9a0baa1e6198db92`, committed **2026-09-08T12:28:15+07:00**, author *Dao Quang Toan*, message *"Wire near-miss parser on paper2_exec PYTHONPATH for Gate 0A Flash."* Read directly, it does two things:

1. `scripts/paper2_exec_run.sh` (+5 lines): exports `PYTHONPATH="${A}:…"` so `qwen_cua`'s try-import of `generic_executor.near_miss_xml` resolves after the script `cd`s into MyPCBench. The inline comment states it changes no prompt, no `DONE`, no `max_steps`, no task order — consistent with §0.3's account of the patch as an **instrument bind**.
2. `generic_executor/near_miss_xml.py` (+34/−1): adds `classify_parse_event` plus the labels `CANONICAL_PARSE` / `NEAR_MISS_CANONICALIZED` / `MALFORMED_REJECTED` / `EMPTY_ACTION`. This is an **audit-only taxonomy** — it labels a stored `response` offline and, per its own docstring, "does not change `VALID_DONE` / last-action" and "never maps a missing action to `DONE`". It cannot alter which actions executed.

So §0.3's characterisation stands, with one precision the earlier wording lacked: the patch was wiring **plus an audit classifier that cannot affect actions or termination**, not wiring alone. The §0.11 dual analysis draws its rescue labels from exactly this taxonomy (`out/study2_gate011_nearmiss_dual.md`: Flash \(\lvert\mathcal{A}\rvert\) 8 as-executed vs 7 with rescues treated as rejected; GPT/Claude parser-not-applied).

**Two manifests, and this one is canonical for the amendment chain.** `git merge-base` of local `HEAD` and the host branch is `7cb434f`; `e8f6289` is **not** an ancestor of local `HEAD`. The host's `EXECUTION_MANIFEST.md` is therefore not an older copy of this file but a **parallel document** (220 lines vs ~490 here) with disjoint content in both directions:

- **Only here:** the whole §0.1–§0.16 amendment chain, including the pre-registrations that must be timestamp-checkable (`21c5618` for §6.1(g)).
- **Only on host:** three dated operational notes of 2026-09-06 (GPT hard-block, Claude OpenRouter SMALL compatibility smoke, Gate −1.5 measurement remediation) and the §0.15/§0.16 summary tables.

This file stays the record of record. Host-only content is folded in **additively** below; the file is never resolved by a git merge of the two branches, because a careless resolution would silently drop one side's chain.

**Imported from host, because it is materially about measurement — Gate −1.5 remediation (2026-09-06).** Not a change to \(\mathcal{M}\)/\(\mathcal{T}\)/\(D\). False-`DONE` root cause: `cell_has_done` matched `"done": true`, which is **also** set by `FAIL` and `PREDICT_CRASH` rows in `traj`. Canonical rule adopted: \(\texttt{VALID\_DONE} \iff \texttt{canonical\_last\_action} = \texttt{DONE}\), via tracked `scripts/paper2_traj_terminal.py`. Offline reclassification (`scripts/canonical_audit_paper2.py` → `CHECKPOINT.canonical.jsonl`) moved **Flash from 27 to 23 `DONE`** with 4 mismatches; the original `CHECKPOINT.jsonl` is retained as historical. Later checkpoints call the canonical helper; harness pin in `out/paper2_harness_pin.json`. **Study 1 analysis must use `CHECKPOINT.canonical.jsonl`**, not raw pre-remediation `DONE` counts. This is the earliest instance in the project of the hazard §0.12 later audited on the judge side, and it belongs in any write-up of the instrument.

**Imported but SUPERSEDED — host's GPT hard-block resume condition (2026-09-06).** That note lists a resume path through "frozen `ResponseStateAdapter` … this manifest amended with adapter freeze hash". §0.2 (2026-09-08) **withdrew** the adapter: none was ever built, and the GPT lane ran the substituted generic XML scaffold. The host row is retained here only as history and must not be cited as the GPT lane's provenance. Likewise its Claude row ("57 legs remain unstarted … official lane still planned as native") is superseded by §0.8.

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
| 0.10 | 2026-09-09 | 9B replay PASS but excluded from Layer B (instrument + transport mismatch, \(\lvert\mathcal{A}\rvert=0\)); `0773242` absent on host → that half inconclusive; Flash becomes load-bearing; prompt has no completion-discipline injection |
| 0.11 | 2026-09-09 | Near-miss enumeration is Flash-derived, so Claude's `EMPTY_XML_ABORT` dialect is unrescued → per-model instrument advantage; mandatory dual analysis with rescues treated as rejected |
| 0.12 | 2026-09-09 | Judge frame path audited: ordering clean (join on `screenshot_file`, not `step_num`); frame-count asymmetry real but shifts \(S\) in 0/94 cells; \(\mathrm{corr}(\text{steps},S)=-0.275\) so no max-reduce inflation; \(S\) re-derived exactly on 94/94 → all re-reductions are free |
| 0.13 | 2026-09-10 | Roster arithmetic corrected for 9B's exclusion, recorded at 35/57: Claude's 2 `DONE` are one pair; likely below \(n_{\min}\) → ranked roster GPT + Flash = 2 → §6.1(c) fires, **Layer B not evaluated**; 87–91-step legs are §0.6 metering, not a breach; both branches fixed in advance |
| 0.14 | 2026-09-10 | Claude **FROZEN** 57/57: 4 `DONE` / 53 `TERMINAL_FAIL`, \(\lvert\mathcal{A}\rvert=1\) (only `f013` G0+G1); reported not ranked; Flash continues untouched; Layer B path = GPT+Flash under §6.1(c)/(g) |
| 0.15 | 2026-09-11 | Flash **FROZEN** 57/57: \(\lvert\mathcal{A}\rvert=8\); GPT 9 / Claude 1; Layer B not confirmatory; §6.1(g) partial (\(\Delta S\) only, common support 4); **STS blocked on unlocked \(\hat D\) extractor** |
| 0.16 | 2026-09-11 | Extractor `3242c30`, STS `71a405d`; common-4 sign disagreement (Flash \(\arg\max S\), GPT \(\arg\max\) STS); \(Y=0\) all \(\mathcal{A}\); full-\(\mathcal{A}\) STS order flips vs \(\mathcal{A}^\cap\); LOPO fragile; Layer B still not confirmatory |
| 0.17 | 2026-09-12 | Host history imported by bundle (`8197110`, 5 commits) since push is blocked by a read-only deploy key; **`0773242` found and read → §0.4/§0.10 inconclusive half CLOSED** (PYTHONPATH bind + audit-only parse taxonomy, cannot change actions or `VALID_DONE`); host manifest identified as a **parallel document**, this file declared canonical, host-only Gate −1.5 remediation imported, host adapter/native rows marked superseded by §0.2/§0.8 |
| `PAPER2_SPEC.md` §6.1 | 2026-09-08 | Power, rank stability, no optional stopping, completion-conditional reporting |
| `PAPER2_SPEC.md` §6.1(g) | 2026-09-10 | Two-ranked-agent branch fixed in advance: §6.1(c) unchanged (Layer B not evaluated), but a signed-difference comparison on common support with paired bootstrap may be reported as **exploratory**; void if ≥3 agents reach \(n_{\min}\); written before the Flash lane and before any STS exists |
