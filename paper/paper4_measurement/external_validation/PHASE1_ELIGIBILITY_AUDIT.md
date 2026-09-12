# P4-M external validation — Phase 1 eligibility audit

**Status:** FAIL — no eligible public corpus under the frozen table.
**Date:** 2026-09-13
**Protocol:** `paper/paper4_measurement/P4_EXTERNAL_VALIDATION_DESIGN.md`
**This audit does not freeze a sample. Y / HIT / MISS / evaluator success were not used to keep or drop episodes.**

Scientific question (locked, not broadened):

> Can the P4-M observation/evidence distinction be transported to an independently sourced CUA trajectory corpus **without changing** the \(I\to P\to E\) pipeline after seeing outcomes?

## Method (what was and was not opened)

**Opened (public specs / docs / two demo schema files):**

- GitHub documentation and file trees for WebArena-Verified and official WebArena.
- Task-specification JSON only: `webarena-verified.json` (812 tasks) and `config_files/test.raw.json` (812 tasks). Used to count **field presence** (`eval` / `eval_types` / `reference_answers` / `expected.retrieved_data`) and evaluator **names**, not agent outcomes.
- WAV demo `examples/agent_logs/demo/{107,108}/` **directory listing** and **one** `agent_response.json` (task 108) to classify the dumped *schema*. `eval_result.json` was **not** fetched (evaluator outcome of the demo run).
- Hugging Face **dataset cards** for additional named dumps. No dataset download. Sean1999/webarena is access-gated (contact information required); files were not fetched.

**Not opened:**

- `merge_log.txt`, `SCORES.json`, `task_ids/` pass/fail lists, HIT/MISS, BrowserGym `reward`, or any success bit used as a sampling frame.
- Google Drive human/experiment trace zips.
- Hugging Face trajectory parquet/jsonl bodies.
- Live WebArena sites, docker, playwright, agents, OpenRouter.

**Inference rule:** if a required field is not documented, it is recorded as **not established**. Missing fields are not inferred into eligibility.

**Ineligible by design (not re-audited as candidates):** P4-B/C/C2/D/E slates, C2/D confirmatory \(\tau\), MyPCBench / P1–P3 legs.

---

## Candidate 1 — WebArena-Verified (ServiceNow)

| Item | Value |
|---|---|
| Source | https://github.com/ServiceNow/webarena-verified |
| Docs | https://servicenow.github.io/webarena-verified/ |
| Inspected commit | `6473f72db5dcefc97b5725b59e734504edc28a21` (2026-02-07, `main`) |
| Task JSON | `assets/dataset/webarena-verified.json` sha256 `d65275660814663375028e9017e1f929e3c38321041b125795e2713b52243d30` (812 objects) |
| License | Apache-2.0 (LICENSE sha256 `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`) |

Public artifact identity: **task + evaluator specification release**, not a trajectory corpus.

Task object keys observed: `task_id`, `sites`, `start_urls`, `intent`, `intent_template`, `intent_template_id`, `instantiation_dict`, `revision`, `eval`. No `kind` / `k` field.

`eval` is a list. Evaluator names counted over 812 tasks: `AgentResponseEvaluator` 812, `NetworkEventEvaluator` 663. `expected.retrieved_data` present in 811/812 task specs (field presence only; values not used as \(Y\)).

Public trajectory-like files: `examples/agent_logs/demo/` contains **exactly two** episode directories (`107`, `108`). Each demo directory documents `agent_response.json`, `eval_result.json`, `network.har`. Offline evaluation of *other* logs is described as consuming `agent_response.json` + `network.har`. Docker / live sites exist for running agents; that path is **KILL** under this protocol and was not used.

Demo `agent_response.json` for task 108 (schema only) is structured evaluator JSON (`task_type`, `status`, `retrieved_data`, `error_details`), **not** a final assistant natural-language message. Frozen \(I\) is **only** that NL message. Using this JSON as \(I\) would be evaluator-shaped structured output, not the declared channel. Using `network.har` as \(I\) would be network/DOM-adjacent, forbidden.

### Eligibility table

| # | Requirement | Finding | Pass? |
|---|---|---|---|
| 1 | Independent third-party source | Yes. ServiceNow public GitHub, Apache-2.0. Not authored for P4-M. | YES |
| 2 | Per-episode trajectory availability | Task JSON is not a trajectory. Public git contains 2 demo logs, not ≥30 episodes. | NO |
| 3 | Final assistant NL message | Not present as a declared field in the 812-task dump. Demo `agent_response.json` is structured eval JSON, not NL stop/say text. HAR is not NL. | NO |
| 4 | Task specification | Yes: `intent` (+ template) on 812 tasks. | YES |
| 5 | Typed kind \(k\) | No `kind` field. Intent text does not by itself freeze \(\mathrm{kind}(L)\) into {money, integer, entity, categorical}. **Not established** from schema. | NO (not established) |
| 6 | Independent \(L\) | Task spec contains `eval[].expected.retrieved_data` (and related expected fields) **independent of a later agent run**. That is a candidate locator **if** it is a typed \(\mathrm{Val}_k\) value and \(I\) exists. Without trajectories, \(L\) cannot be paired to an episode under frozen \(I\). | Partial / unused |
| 7 | \(L\) independent of this agent's answer/evaluator output | Spec gold is independent of *this* overnight agent's output (none was run). Demo `eval_result.json` was not opened. Using evaluator copies of the agent response as \(L\) would be inadmissible; that path was not taken. | YES for spec field; N/A for sample |
| 8 | Distinguish loss vs absence | Not with the public 812-task file (no \(\tau\)). Two demos are evaluator JSON + HAR, not a raw NL channel in which a typed fragment could be shown to exist outside \(I\). | NO |
| 9 | Offline replay | Task JSON: yes (read-only). Full intended eval uses HAR + agent_response; live sites / docker exist but were not started. No N≥30 recorded \(\tau\) to replay. | NO for this study |
| 10 | License / redistribution | Apache-2.0. Redistribution of the task JSON would be allowed; **not done** because the dump is ineligible as \(\tau\). | OK, unused |
| 11 | \(N\ge 30\) eligible episodes | Public trajectory n=2. Prefer STOP if \(N<20\). | NO |
| 12 | Sampling frozen before outcome inspection | No eligible frame. No sample. Success labels not used to build a frame. | N/A (no sample) |

**Verdict:** FAIL. WebArena-Verified is not an eligible trajectory corpus under frozen \(I\). Existence of the evaluator release does **not** confer eligibility.

---

## Candidate 2 — Official WebArena (Zhou et al. / `web-arena-x/webarena`)

| Item | Value |
|---|---|
| Source | https://github.com/web-arena-x/webarena |
| Inspected commit | `dce04686a56253aefba7b18a4fa0937cf1dc987b` (2025-11-26, `main`) |
| Task JSON | `config_files/test.raw.json` sha256 `7b50386fd69163dbc05d615d834df4c6ed2c35596e97a1b10d17451c02537652` (812 tasks) |
| License | Apache-2.0 (same LICENSE hash as WAV) |

Task keys include `eval.eval_types`, `reference_answers`, `program_html`, `reference_url`, etc. Counts of **eval type tags** (a task may have more than one): `string_match` 335, `url_match` 205, `program_html` 411. All 335 `string_match` tasks have a `reference_answers` field present. That field is a **candidate \(L\)** in the *task spec*, consistent with the design-stage note. Values were **not** catalogued and were **not** used to sample.

`url_match` / `program_html` evaluation is page/DB/URL state, closer to harness \(A\) than to P4-M typed last-text \(L\). Those tasks are **out of frame** unless a typed \(\mathrm{Val}_k\) is also locked in the spec. This audit does **not** promote URL/HTML locators into \(L\).

Published **trajectory** artifacts (from `resources/README.md`, not downloaded):

- Human trajectories (~179) as Playwright trace zips on Google Drive. Viewing path documented as `playwright show-trace`. Contains HTML, network traffic, screenshots.
- Experiment traces (v1/v2) on Google Drive: `render_*.html` (a11y observations, raw prediction, parsed action, **screenshot**) plus `trace/` Playwright zips plus `merge_log.txt` recording pass/fail.

Frozen \(I\): final assistant NL message only. **Not** screenshots, DOM, action JSON, evaluator logs. Design: if docker/replay harness required → KILL. Overnight hard stop: do not start docker/browser; do not use only screenshots/DOM/tool traces as the channel.

Public documentation does **not** establish a frozen per-episode **declared final-NL field** in a local file. Extracting `div.raw_parsed_prediction` from `render_*.html` would be HTML scraping of a mixed screenshot/DOM bundle that is not on disk here. `playwright show-trace` is a browser/trace viewer, not the declared \(I\). `merge_log.txt` is an outcome file sitting beside traces; it was not downloaded, and would have to be ignored even if traces were fetched.

No official WebArena trajectory dump exists in this workspace.

### Eligibility table

| # | Requirement | Finding | Pass? |
|---|---|---|---|
| 1 | Independent third-party source | Yes. Official WebArena GitHub + paper. | YES |
| 2 | Per-episode trajectory | Task configs: yes as specs. Trajectory zips: documented on Drive, **not present locally**, not fetched. | NO (this study) |
| 3 | Final assistant NL | Not established in the in-repo artifact. Published traces are Playwright/HTML/screenshot bundles. `stop [answer]` is described in the **paper's agent prompt**, not as a frozen dumped field in a local corpus. | NO (not established) |
| 4 | Task specification | Yes: `intent` on 812 tasks. | YES |
| 5 | Typed kind \(k\) | No `kind` field. `string_match` is an **evaluator type**, not \(\mathrm{kind}(L)\in\{\mathrm{money,integer,entity,categorical}\}\). Mapping every `string_match` gold string into a DFC kind would be a new kind rule, not a schema map. **Not established.** | NO |
| 6 | Independent \(L\) | `reference_answers` exists on all 335 `string_match` specs (field presence). `program_html` / `url_match` locators are not typed last-text \(L\). | Partial on specs; unused |
| 7 | \(L\) vs this agent/eval copy | Spec `reference_answers` is independent of this overnight run. `merge_log.txt` (pass/fail of published experiments) was not opened. | YES for spec; N/A for sample |
| 8 | Loss vs absence | Not without a raw NL \(\tau\) on disk. Playwright/HTML traces, if used as \(I\), would violate the frozen channel. | NO |
| 9 | Offline replay | Task JSON: yes. Trajectory replay as documented requires Drive fetch + Playwright/HTML. Live WebArena sites exist for *new* runs — not used; that path is KILL. | NO under frozen \(I\) |
| 10 | License | Apache-2.0 for the GitHub repo. Drive trace license/redistribution **not established** from the README alone (files not fetched). | Incomplete for traces |
| 11 | \(N\ge 30\) | No local eligible \(\tau\). Human zip count (~179) is not an admissible frame until \(I\) and \(k\) pass. | NO |
| 12 | Outcome-blind sampling | No sample. Pass/fail logs not used. | N/A |

**Verdict:** FAIL for this overnight study. Do not treat Drive Playwright bundles as the frozen final-text channel. Do not scrape `render_*.html` as a workaround.

---

## Candidate 3 — `Sean1999/webarena` (Hugging Face)

Dataset card inspected. Files **not** downloaded.

Documented contents: 100 tasks × five attention methods; `llm_calls.jsonl` `output` = **browser-use structured action JSON**; `task_<id>.json` includes `answer`, `is_done`, steps/actions; `input.json` has `eval.reference_answers`; `SCORES.json` / `task_ids/` are official and lenient pass/fail lists; scoring judge Llama-3.3-70B; map site points at **live** openstreetmap.org; access requires agreeing to share contact information; total size ~768 MB.

Frozen \(I\) forbids promoting action JSON / tool calls as fallback. Outcome files are co-located with trajectories (must not be used to sample). Live OSM is a live-site dependency for *re-running*; recorded files might still be readable offline, but the declared model output is not NL final-text.

### Eligibility table (from the card only)

| # | Requirement | Finding | Pass? |
|---|---|---|---|
| 1 | Independent third-party | Named public HF dataset (gated). Not P4-authored. | YES, with access gate |
| 2 | Per-episode trajectory | Card claims `llm_calls.jsonl` per task. **Not verified on disk.** | Not established (files not fetched) |
| 3 | Final assistant NL | Card says `output` is structured **action JSON**. NL stop/say **not established**. | NO (as documented) |
| 4 | Task spec | Card claims `input.json` intent/eval. Not verified on disk. | Not established |
| 5 | Typed kind \(k\) | Not documented. | Not established |
| 6–7 | Independent \(L\) | Card claims `reference_answers` in `input.json`. Also LLM-judge lenient scores — inadmissible as \(L\). Files not fetched; values not used. | Not established / mixed |
| 8 | Loss vs absence | Not established without NL channel. | NO |
| 9 | Offline replay | Card exists; dataset gated; live OSM noted for map tasks. No local files. | NO |
| 10 | License / redistribution | **Not established** (gated; LICENSE not retrieved). | Not established |
| 11 | \(N\ge 30\) | Card claims 100 tasks/method. Eligibility of those 100 as \(I\)-admissible episodes is not established. | Not established |
| 12 | Outcome-blind sampling | Would require ignoring `SCORES.json` / `is_done`. Not sampled. | N/A |

**Verdict:** FAIL / not established. Fetching a gated dump whose documented `output` is action JSON would be a workaround that violates frozen \(I\). Not done.

---

## Candidate 4 — Other named public dumps (cards only)

Inspected only as names + dataset-card text. **No download.**

### `HaoranLiu/WebArena`

BrowserGym / AgentLab-style rollouts with **embedded screenshot images** and OpenAI-style `messages`. Frozen \(I\) forbids screenshots as the channel. Whether a final assistant NL field exists independently of images/tool calls is **not established**. Reward/eval columns are typical of such dumps; they were not opened. **FAIL / not established.**

### `toeunkim/matm-trajectories` (WebArena splits)

Card documents `trajectory` as `{action, observation, reasoning, ...}` and a success field. Final assistant NL **not established**. Independent typed \(L\) **not established**. Success co-located. **FAIL / not established.**

### `cx-cmu/agent_trajectories`

Benchmarks listed: tau2bench, swebench, terminalbench, mathhay, search, mcpbench — **not** a WebArena CUA last-text dump. Card: trajectories end with an assistant message; `reward` is in the same record. Typed \(\mathrm{kind}(k)\) and independent last-text \(L\) for P4-M correspondence **not established**. Using `reward` as \(Y\) would redefine \(Y\) as task success (forbidden). **FAIL / not established.**

### `Agent-Eval-Refine/Agent-Trajectories` and similar large corpuses

Named in search only. Size (~31 GB class) and schema **not established** from a retrieved card in this pass. Downloading tens of GB to discover whether \(I\) exists would be a fishing expedition, not eligibility. **Not established; not fetched.**

---

## Local ineligible sets (explicitly excluded)

| Corpus | Why ineligible |
|---|---|
| P4-B / C / C2 / D confirmatory \(\tau\) | Frozen design: not independently sourced for this study |
| P1–P3 MyPCBench trajectory CSVs | Same; also not this question |
| WAV 812-task JSON | Specs, not \(\tau\) |
| WAV demo n=2 | \(N<20\); channel is not NL \(I\) |

---

## Sampling

**Not performed.** Frame size under frozen \(I\) = 0 eligible episodes.

The pre-specified size rule was therefore not applied to any ID list. No salt. No hash draw. No stratification. No interesting-example pick.

---

## Hard-stop triggers that fired

| Trigger (frozen) | Fired? |
|---|---|
| No eligible public dump | **YES** |
| No usable final assistant text in an admissible dump | **YES** (as established) |
| Only screenshots/DOM/tool traces as published trajectory form | **YES** for official WA Drive traces (docs) |
| Parser modification would be required to accept action JSON / HAR / HTML scrape as \(I\) | Would fire if we “fixed” I; **not done** |
| Live site / docker / new agents | Not started; required for *creating* \(\tau\), which is KILL |
| Outcome-dependent sampling | Not done |
| Leakage | No \(Y\) computed |
| Frozen P4 artifact modification | Not done |

**Did not invent a workaround.** STOP is the scientific result of Phase 1.

## Phase 1 decision

**Do not open Phase 2 (freeze sample), Phase 3 (adapter), or Phase 5 (transport A/B/C analysis).**

Those phases are recorded as **not reached**, not as A=0/B=0/C=0 on a hidden sample.
