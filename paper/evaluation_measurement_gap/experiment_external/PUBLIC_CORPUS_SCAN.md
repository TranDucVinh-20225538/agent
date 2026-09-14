# Public-corpus eligibility scan — 2026-09-13

**Contract:** same gates as `EXTERNAL_PROTOCOL.md` / `ELIGIBILITY_AUDIT.md`
(inspectable intermediate evidence state R, separate from the final
verdict, grain enough to define a discard set; independent reference;
public τ; no protocol change). Docs and released schemas only. **No
API spend.**

**Question:** is there a *new* public bench that satisfies the frozen
eligibility contract, beyond the N=0 audit already on file?

**ELIGIBLE count this pass: 0.**

That does **not** refute the Limitations sentence (“No corpus satisfied
the frozen eligibility contract”). It repeats it on a wider 2026 list.

Closest *architecture* (collect-then-filter) remains WebJudge-family and
top-K-per-criterion verifiers. Closest still fail released R, independent
frame-grain gold, and/or public evidence bytes joined to that R.

Prior Path B: WebJudge JSON is `{Response, Score}` only; screenshot
request to `xue.681@osu.edu` is still outstanding. Not re-opened here.

---

## Start list (novelty-search leads, re-checked)

| Candidate | Status | Why |
|---|---|---|
| WebJudge / Online-Mind2Web (OSU) | **not eligible** | Code is collect-then-filter (score, threshold, `MAX_IMAGE`). Released judge dumps still lack screenshot bytes; HF `osunlp/Online-Mind2Web` is the **task** set, not the scored trajectories. Frame-grain independent gold absent. Author image request not satisfied as of this scan. |
| AgentRewardBench | **not eligible** | Public τ + expert *task-level* labels. Judges emit verdicts, not an inspectable collected-then-filtered candidate R. Verdict-audit corpus, not discard-set grain. |
| WebArena-Verified (ServiceNow) | **not eligible** | Gold + evaluator code exist. Intermediate is type-normalization, not post-collection discard. Public in-repo episodes n=2. Unchanged vs `ELIGIBILITY_AUDIT.md`. |
| Mind2Web 2 (agentic search; arXiv:2506.21506) | **not eligible** | Agent-as-a-Judge on **answer text + cited pages**. Extractor/Verifier tools score claims, not a trajectory-frame discard set. Time-varying search answers; no public collect-then-filter R on CUA screenshots. |
| ELT-Bench-Verified (arXiv:2603.29399) | **not eligible** | Warehouse table / SQL comparison. Auditor-Corrector fixes GT and scripts (benchmark error). No screenshot/candidate accumulator that a later A(R) truncates. |
| RLVR / verifier false-negative cluster (arXiv:2609.01354 and kin) | **not eligible** | Math/LaTeX (and similar) string verifiers reject equivalent forms. Matching FN, not collect-then-filter of an intermediate evidence list. Not a CUA trajectory instrument. |

---

## Additional 2026 CUA / agent benches (docs/schema)

| Candidate | Status | Why |
|---|---|---|
| CUAVerifierBench / Universal Verifier (HF, MIT; arXiv:2604.06240) | **not eligible** *as released* | Screenshots public; relevance matrix R **not** in HF columns. Task-level `uv_*` / human outcome are not frame gold. Reconstructing R is our workstream, not a newly published eligible dump. |
| CUAJudge / ACuRL (arXiv:2602.10356) | **not eligible** | WebJudge-shaped key-point → key-screenshot → outcome. Papers report agreement on OSWorld / RL rollouts. No public joined dump of per-frame scores + images + independent frame gold found. |
| SeekJudge + CUAStepBench (arXiv:2607.23263; `ZJUSCL/CUAStepBench`) | **not eligible** | 278 trajs with screenshots and **human** success/step labels. That is verdict/step gold, not a released judge keep-list R. SeekJudge intermediates not in the dataset card. |
| WebTailBench v2 (2026-05 refresh) | **not eligible** | Public **tasks + precomputed rubrics**. Not recorded episodes with inspectable A(R). |
| WeaveBench (arXiv:2606.09426) | **not eligible** | Trajectory-aware vs outcome-only **disagreement**. No public candidate-accumulator dump. Already INELIGIBLE in `ELIGIBILITY_AUDIT.md`. |
| OSWorld / OSWorld-Verified | **not eligible** | Final-state getters. FN/FP are matching / oracle issues, not post-collection discard of a collected list. Unchanged. |
| VAGEN / agentic reward modeling (arXiv:2602.00575) | **not eligible** | Human audit of OSWorld-Verified FNs (task success). No inspectable collect-then-filter R. |
| WebArena string/URL/HTML | **not eligible** | Last-answer match; no accumulator. Unchanged. |
| VisualWebArena | **not eligible** | Same family as WebArena. Unchanged. |
| AppWorld | **not eligible** | State unit tests. Unchanged. |
| τ-bench | **not eligible** | Substring + DB hash conjunction. Unchanged. |

---

## Gate summary

**New ELIGIBLE: 0.** Cumulative public ELIGIBLE under the frozen
contract remains **0**.

If a later dump joins (a) evidence bytes, (b) the evaluator’s
intermediate keep/discard lists, and (c) an independent reference at
that grain, freeze a new protocol and re-open. Do not relax gates to
obtain a positive.

STOP-NO-CORPUS stands.
