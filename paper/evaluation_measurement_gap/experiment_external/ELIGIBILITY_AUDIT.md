# Eligibility audit — cross-instrument post-collection discard

**Date:** 2026-09-13  
**Protocol:** `EXTERNAL_PROTOCOL.md` (frozen).  
**Question:** can an analogous observation/evidence-loss mechanism (gold enters intermediate R, then A discards it) be identified in an independently specified CUA evaluator?  
**P3 extractor / repairs / P4 / score_v2 / de66e0a STOP:** not modified, not re-run.

Allowed statuses: **ELIGIBLE** / **INELIGIBLE** / **UNCERTAIN**.  
UNCERTAIN is not promoted. **No candidate is ELIGIBLE.**

Primary sources inspected: official GitHub evaluator files, released result schemas, dataset cards. Blog posts were not used as evidence.

---

## Candidate: WebArena String/URL/HTML evaluators

| Field | Value |
|---|---|
| Independent source | Yes. `web-arena-x/webarena` `evaluation_harness/evaluators.py` sha256 `e23edb390c4e39b3fff97dfd456fb04f7a59a0fb1ea30a4f2fa42bcb77e00c22` |
| Trajectory available | Official Drive traces exist as Playwright/HTML/screenshot bundles (prior P4-M audit). AgentRewardBench also holds WebArena trajectories. Not used as I for *our* parser. |
| Reference/gold available | Yes. Task JSON `eval.reference_answers` / `reference_url` / `program_html` independent of a later run. |
| Evaluator code available | Yes. `StringEvaluator`, `URLEvaluator`, `HTMLContentEvaluator`, multiplicative `EvaluatorComb`. |
| Intermediate representation | Last action `answer` string, or `page.url`, or JS `selected_element`. No candidate **accumulator** analogous to P3 `found`. |
| Intermediate observable | The pred string / URL / selected HTML can be logged; released public dumps typically store the **final score**, not a collected-then-filtered candidate list. |
| Final decision observable | Binary/multiplicative score. |
| Evidence-presence test | Substring / exact / fuzzy LLM match against gold. Gold never “enters found then leaves.” |
| Discard test | Fail-closed **conjunction** across required phrases (`score *=`) is not post-collection discard of an already-collected gold span. Issue #139 (per-item fuzzy_match AND) is a matching-rule FN, i.e. closer to E3 than E2. |
| Offline / no agent rerun / no eval modify | Offline possible on recorded last-answer; would still not expose E2. |
| Sample size | N/A for E2 (architecture mismatch). |
| Outcome-blind feasibility | N/A. |
| **Status** | **INELIGIBLE** |
| **Reason** | No inspectable R that collects gold and then drops it. Final-string match is not an accumulator. Using our P3 extractor on WebArena answers is forbidden (would not be cross-instrument). |

---

## Candidate: WebArena-Verified (ServiceNow)

| Field | Value |
|---|---|
| Independent source | Yes. Apache-2.0. `AgentResponseEvaluator` sha256 `8ae2caf59c6fafecf4ec259ea67bf79d27f19c7fcbdc33a312cea730c4e54c31` |
| Trajectory available | Task specs n=812. Public recorded episodes in-repo: **2 demos** (`examples/agent_logs/demo/{107,108}`). |
| Reference/gold available | Yes. `eval[].expected` in the task JSON, independent of agent output. |
| Evaluator code available | Yes. Four-step: extract → expected → normalize → structural compare. Intermediate: `actual_normalized` / `retrieved_data`. |
| Intermediate representation | Normalized agent-response JSON. Normalization is coercion, not a fail-closed unique-candidate drop of gold already in R. |
| Intermediate observable | Demo eval writes `eval_result.json` (not opened for Y). Schema documents `actual` vs `actual_normalized`. |
| Final decision observable | Yes, when logs exist. |
| Evidence-presence test | Would require N≥30 `agent_response.json` + HAR. Public n=2. |
| Discard test | Not established as A(R) discard of collected gold. |
| Offline / no rerun / no modify | Offline eval exists; we did not run it (insufficient n; would not satisfy E2 architecture). |
| Sample size | 2 public episodes. Gate 12 fails (prefer STOP if n<20). |
| Outcome-blind feasibility | No eligible frame. |
| **Status** | **INELIGIBLE** |
| **Reason** | Independent gold + code exist, but public τ n=2, and the intermediate is type-normalization, not post-collection discard. Same STOP as `de66e0a` on corpus size; this workstream additionally requires observable discard of collected evidence. |

---

## Candidate: OSWorld state checkers

| Field | Value |
|---|---|
| Independent source | Yes. `xlang-ai/OSWorld` metrics (`desktop_env/evaluators/metrics/*.py`). |
| Trajectory available | Multiple public dumps (`xlangai/ubuntu_osworld_verified_trajs`, `UI-MOPD/OSWorld-Eval-Results`, etc.): `traj.jsonl` + `result.txt` + screenshots. |
| Reference/gold available | Task JSON expected files / rules, independent of the agent. |
| Evaluator code available | Yes. Getter extracts VM state; metric compares to expected. |
| Intermediate representation | Getter output (file contents, a11y XML, terminal text). Not a multi-candidate `found` list that is later uniquified. Known issues are **loose substring FPs** (GitHub #518) and **oracle FNs** (Dong), i.e. matching error, not post-collection discard. |
| Intermediate observable | Dumps typically expose `result.txt` (final), not getter payloads. |
| Final decision observable | Yes. |
| Evidence-presence / discard | Gold in the VM may never enter the getter (E1) or may fail equality (E3). Not E2. |
| Offline / no rerun | Replay of getters generally needs the VM snapshot, not just `traj.jsonl`. Offline-from-text is not the official evaluator identity. |
| Sample size | Large dumps exist, but ineligible on mechanism + replay identity. |
| **Status** | **INELIGIBLE** |
| **Reason** | Final-state checkers. No collected-then-discarded candidate R. Replaying our text parser on `response` fields would change the evaluator. |

---

## Candidate: VisualWebArena

| Field | Value |
|---|---|
| Independent source | Yes. Shares WebArena-style `StringEvaluator` / HTML / URL harness (Context7 / upstream VWA tree). |
| Trajectory / gold / code | Same family as WebArena. |
| Intermediate / discard | Same: no gold-accumulator discard. |
| **Status** | **INELIGIBLE** |
| **Reason** | Same architecture as WebArena string/HTML match. |

---

## Candidate: AppWorld

| Field | Value |
|---|---|
| Independent source | Yes. `StonyBrookNLP/appworld` `world.evaluate()` / state-diff unit tests. |
| Trajectory available | Experiment outputs if a third party released them; official release is the engine + tasks, not an N≥30 public CUA last-text dump with intermediate test accumulators. |
| Reference/gold | Ground-truth DB diffs / unit tests independent of the agent. |
| Evaluator | Assertions on `changed_records()` etc. Failures are assertion failures, not discard of an intermediate candidate list. |
| **Status** | **INELIGIBLE** |
| **Reason** | State-based unit tests. No post-collection candidate discard. Public recorded CUA episodes with inspectable intermediate R not established. |

---

## Candidate: τ-bench

| Field | Value |
|---|---|
| Independent source | Yes. `sierra-research/tau-bench` `tau_bench/envs/base.py` `calculate_reward` sha256 `1ad0402073f0ac9ca6b527efa0706e2aa8836dd2e5c1d453ed414ecb768c6d21` |
| Trajectory available | Not a public N≥30 frozen dump inspected here; code is enough to reject the mechanism. |
| Reference/gold | `task.outputs` and gold action sequence for DB hash; independent of the evaluated episode. |
| Intermediate representation | `outputs[output] = found` booleans from scanning RESPOND actions; plus DB hash. |
| Discard test | If gold substring is found, it stays `found=True`. Reward may still be 0 from **DB mismatch** (conjunction of two channels). That is not A(R) dropping gold from the output accumulator. |
| **Status** | **INELIGIBLE** |
| **Reason** | Substring scan + DB equality. Conjunction across channels ≠ post-collection discard of collected gold. |

---

## Candidate: WebJudge / Online-Mind2Web (closest architecture)

| Field | Value |
|---|---|
| Independent source | Yes. `OSU-NLP-Group/Online-Mind2Web` `src/methods/webjudge_online_mind2web.py` sha256 `e3cd499b7c1fc92cbd51d3c4216c95ebab774c2c2cd998c5ad6dad94710780c4` |
| Trajectory available | Released **judge products**, not full screenshot τ, in `data/evaluation_results/.../webjudge_o4-mini/*.json` (JSONL). `agente_results.json` sha256 `23c04410958bb488397b39d8d08a0138c0a87feaf304f9ae63c11e726a49bf26`, 299 lines. Fields: `task_id`, `confirmed_task`, `final_eval`, `image_judge_record` (list of `{Response, Score}`), `key_points`, `evaluation_details`. |
| Reference/gold available | Task-level `human_label.json` exists. **No** independently released determining gold at **screenshot** grain. `key_points` are generated by the same judge model, not independent L. |
| Evaluator code available | Yes. Score each screenshot 1–5; keep `score >= score_threshold`; then `whole_content_img = whole_content_img[:MAX_IMAGE]` (50). This **is** a collect-then-filter architecture. |
| Intermediate representation | `image_judge_record` / per-image Score. Observable in the released JSONL. |
| Intermediate observable | Yes (scores + free-text reasoning). Screenshot bytes are **not** in this JSONL. |
| Final decision observable | `final_eval` present. **Not used** (would leak). |
| Evidence-presence test | **Fails independence.** Using Score≥threshold as “evidence was collected” makes R define gold. Using `final_eval` is forbidden. Using human task-success does not identify which screenshot was determining. Without images + independent frame gold, cannot show gold ∈ R then gold ∉ A(R). |
| Discard test | Threshold and MAX_IMAGE exist in code. Cannot attribute a discarded frame to independently known determining evidence. |
| Offline / no rerun / no modify | Schema inspection only. Re-running WebJudge would call an LLM judge (not needed; still would not create independent gold). |
| Sample size | 299 judge records for one agent file; still ineligible on gold grain. |
| Outcome-blind feasibility | Could ignore `final_eval`, but E2 still undefined. |
| **Status** | **INELIGIBLE** (architecture tempting; causal E2 not supportable without protocol change → would be STOP-INCOMPATIBLE if forced through) |
| **Reason** | Filter-after-score is the right *shape*, but determining reference is not independent at the unit of R. Promoting this would recreate gold from the judge. |

---

## Candidate: AgentRewardBench

| Field | Value |
|---|---|
| Independent source | Yes. McGill-NLP/agent-reward-bench; 1302 trajectories; expert labels for success / side effects / repetition. |
| Trajectory available | Yes (HF). |
| Reference/gold | Human expert labels — independent of automatic judges. Task-level, not candidate-span gold. |
| Evaluator | LLM judges + rule-based WebArena-family scores. |
| Intermediate | Judge free text / binary labels. No collected-then-discarded gold accumulator. |
| **Status** | **INELIGIBLE** |
| **Reason** | Verdict-audit corpus (Dong-adjacent: rule-based under-reports success). Not post-collection discard inside an accumulator. |

---

## Candidate: CUAVerifierBench / Universal Verifier (Rosset et al.)

| Field | Value |
|---|---|
| Independent source | Yes. `microsoft/CUAVerifierBench` (HF, MIT); UV code `microsoft/fara`. 260 trajectories; human outcome/process labels. |
| Trajectory available | Yes: screenshots + web_surfer log + final answer. |
| Reference/gold | Human **task-level** outcome/process. Not screenshot×criterion gold. |
| Evaluator | UV scores screenshot×rubric relevance matrix then keeps **top-K per criterion** (collect-then-truncate). Released trajectory fields include `uv_rubric_score` / `uv_outcome_success`, **not** the relevance matrix itself (dataset README). |
| Intermediate observable | Final UV scalars released; the R that top-K acts on is **not** in the public column list. |
| Evidence-presence / discard | Same independence failure as WebJudge, plus R not even released. |
| **Status** | **INELIGIBLE** |
| **Reason** | Top-K is the right *shape*, but public artifacts are verifier–human agreement, not inspectable A(R) with independent determining gold. |

---

## Candidate: WeaveBench

| Field | Value |
|---|---|
| Independent source | Paper/arXiv:2606.09426 (preprint). Trajectory-aware vs outcome-only grading. |
| Trajectory / intermediate R / independent span gold | Not established as a public dump with inspectable candidate accumulators in this audit. |
| **Status** | **INELIGIBLE** |
| **Reason** | Documents outcome-only vs trajectory-aware disagreement (verdict/process), not post-collection discard. No eligible public R dump found. |

---

## Gate summary

| Candidate | Status |
|---|---|
| WebArena evaluators | INELIGIBLE |
| WebArena-Verified | INELIGIBLE |
| OSWorld checkers | INELIGIBLE |
| VisualWebArena | INELIGIBLE |
| AppWorld | INELIGIBLE |
| τ-bench | INELIGIBLE |
| WebJudge / Online-Mind2Web | INELIGIBLE |
| AgentRewardBench | INELIGIBLE |
| CUAVerifierBench / UV | INELIGIBLE |
| WeaveBench | INELIGIBLE |

**ELIGIBLE count: 0.**

Hard STOP conditions 1–12 are not jointly satisfied by any candidate. Closest architectural matches (WebJudge threshold+MAX_IMAGE; UV top-K) fail independent gold at the grain of R, and/or fail released observability of R.
