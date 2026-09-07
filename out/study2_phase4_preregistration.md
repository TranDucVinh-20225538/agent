# Study 2 — Phase 4 preregistration (LOCKED)

**Status:** **LOCKED / SIGNED** — execution-frozen method gate. No further edits to \(\mathcal{M}\)/\(\mathcal{T}\)/\(D\)/sampling/N/analysis plan except dated infra stop.  
**Sampling class:** **Option L** — legacy full-universe carryover of frozen analysis \(\mathcal{T}\) (`out/study2_sampling_design_decision_memo.md`).  
**Depends on:** Gate 0A cross-family PASS + roster LOCK (`out/study2_roster_lock.md`).  
**Execution-funding assumption (ops):** Study 2 main-matrix OpenRouter traffic bills credential fingerprint **`sk-or-v1-008…9dd`** via `scripts/study2_bind_execution_key.sh` (source slot `OPENROUTER_API_KEY_LARGE`). `OPENROUTER_API_KEY_SMALL` (`c86…37a`) is **forbidden** for main-matrix legs. Binding verify PASS recorded in `out/study2_execution_key_binding_recheck.md`.  
**Sources (carry-forward, do not silently rewrite):**  
`PAPER2_SPEC.md`, `DESIGN.md`, `out/paper2_analysis_universe.*`, `registry_semantic_frozen.json`, Gate −2 protocol spec.  
**Reconciliation carry-forward (do not silently rewrite):**  
`out/study2_taxonomy_reconciliation_memo.md`, `out/study2_sampling_memo_reconciliation_addendum.md`.

This document answers: *exactly what we will run, how often, and how we committed to analyze it before seeing outcomes.*

---

## 0. Lock block (SIGNED)

When signed, no further edits to \(\mathcal{M}\)/\(\mathcal{T}\)/\(D\)/sampling/analysis plan except dated infra stop.

| Field | Value | Sign-off |
| --- | --- | --- |
| Roster \(\mathcal{M}\) | Gate 0A Qualified trio (below) | ☑ |
| Task pool \(\mathcal{T}\) | Analysis universe \|T\|=25 (Option L; below) | ☑ |
| \(D\) / roles | `registry_semantic_frozen.json` surviving variants | ☑ |
| Sampling / cell order | `out/paper2_cell_order.json` seed `20260904` (carry-forward) | ☑ |
| N / legs | **Option L fixed matrix:** \(N_{\mathrm{fam}}=57\), total \(L=171\) | ☑ |
| Analysis plan | §10 below (incl. fixed-N attrition) | ☑ |
| Execution OpenRouter key | fingerprint `sk-or-v1-008…9dd` only (bind script; not SMALL) | ☑ |
| Signed by / date | Cursor agent (authorized pre-launch sequence) / 2026-09-06T16:58:24Z | ☑ |

---

## 1. Outcome taxonomy (locked carry-forward)

From `DESIGN.md` Alignment 2×2 + STS:

|  | \(\Delta S=0\) | \(\Delta S\neq 0\) |
| --- | --- | --- |
| track=1 | Type A | score-sensitive |
| track=0 | Type B (audit; high-score cutoff operational) / low-score miss | score-moved miss |

Primary selection metrics (from `PAPER2_SPEC.md`):

- \(\overline{S}_i\): mean **base-leg** rubric on valid pairs \(\mathcal{A}\)
- \(\overline{\mathrm{STS}}_i\): mean pair STS on the **same** \(\mathcal{A}\)
- Hypothesis: \(\arg\max \overline{S} \neq \arg\max \overline{\mathrm{STS}}\) among agents with \(\ge n_{\min}\) valid pairs
- \(n_{\min}=3\) (frozen)

**Gate 0A failure modes** (stdout-distrust, completion-recognition, etc.) are **qualitative taxonomy** for harness notes — not confirmatory Study 2 outcome labels.

---

## 2. Canonical state-family / taxonomy structure

**Separate from multi-intervention accounting (§3) and from Alignment 2×2 (§1).**

### 2.1 SPEC vocabulary (6 state families)

Study 2 uses the six state-family strata in `PAPER2_SPEC.md` §4:

1. numeric  
2. categorical / status  
3. aggregation  
4. temporal  
5. relational / joint  
6. preference / recommendation  

Checklist language referring to “seven taxonomy types” is **not** part of the frozen SPEC and is **not** used.

### 2.2 Confirmatory coverage in sealed analysis \|T\|=25 (5 populated strata)

The frozen analysis universe `|T|=25` (`out/paper2_analysis_universe.*`) has **non-empty support for five** of those six strata. The categorical/status stratum is **empty** in confirmatory \(\mathcal{T}\) because its only sealed member, `situated_action-f029`, is `REJECTED_NOT_IDENTIFIABLE` and listed in `sealed_minus_analysis`. (`contradiction-f024` reduced temporal count but left temporal non-empty.)

| Object | Count | Role |
| --- | ---: | --- |
| SPEC state-family names | **6** | Canonical stratification vocabulary |
| Populated strata in analysis \|T\|=25 | **5** | Confirmatory coverage / family-wise STS denominators with \(n\ge1\) |

Family-wise STS and stratum-balanced sampling statements apply only to strata with \(n\ge1\) in analysis \(\mathcal{T}\). Categorical/status may appear only as a **reported coverage gap**, not as a family-wise STS denominator.

MyPCBench task `category` prefixes are **not** SPEC sampling strata.

---

## 3. Multi-intervention accounting

**Separate from state-family taxonomy (§2).**

- \(n_{\mathrm{multiI}}=\mathbf{7}\) means **seven tasks** in the frozen analysis universe have **at least two** intervention instances with both variants PASS (`multi_i_both_pass` in `out/paper2_analysis_universe.json`).  
- This count is the SPEC Cost / §4 multi-I size for `|T|=25`: \(\min(8,\lceil 0.25\cdot 25\rceil)=7\).  
- **Unrelated** to the six SPEC state-family names and to the five populated analysis strata. It is **not** a seventh taxonomy type.

Option L uses the universe’s already-listed multi-I set of 7 (no new multi-I draw).

---

## 4. Agent set \(\mathcal{M}\) (roster LOCK)

| Provider family | Model ID | Qualification |
| --- | --- | --- |
| Qwen | `qwen/qwen3.8-flash` | Gate 0A v1.1 PASS |
| OpenAI | `openai/gpt-5.5` | Gate 0A v1.1 PASS |
| Anthropic | `anthropic/claude-opus-4.6` | Gate 0A v1.1 PASS |

**Excluded from Study 2 confirmatory \(\mathcal{M}\):** `qwen/qwen3.5-9b` (Study 1 SMALL lane only; not Gate 0A–qualified on the generic executor roster).  
**Not ranked by DONE@.** No post-hoc drop after seeing Study 2 \(S\)/STS.

Protocol substrate: frozen Gate −2 prompt/XML `qwen_cuabash` path + OpenRouter **stateless** `/chat/completions` transport (no native CU tools / no `previous_response_id`).

---

## 5. Sampling rule / \(\mathcal{T}\) (Option L)

**Human-selected class:** Option L — reuse the **entire** frozen analysis universe (not a new SPEC §4 `k` subsample).

**Confirmatory task pool:**

- `|T| = 25` — `out/paper2_analysis_universe.md` / `.json`
- Cell order: `out/paper2_cell_order.json` (`PAPER2_EXEC_SEED=20260904` carry-forward; **this draft does not choose a new seed**)
- multi-I (I1+I2 both PASS): **7** tasks (§3)

**Explicit exclusion:**

> plant-token-terminate is a qualification-only smoke task and is excluded from the preregistered Study 2 task pool.

(`out/gate0a_task_separation.md`)

Paper 1’s ten tasks remain calibration only — not re-entered.

---

## 6. Fixed matrix (Option L) — N locked

After \(\mathcal{M}\) and \(\mathcal{T}\) are listed, SPEC Cost:

\[
N_{\mathrm{fam}} = 2|\mathcal{T}| + n_{\mathrm{multiI}}
= 2\cdot 25 + 7
= \mathbf{57}
\]

\[
L = |\mathcal{M}|\times N_{\mathrm{fam}}
= 3\times 57
= \mathbf{171}
\]

equivalently \(L = |\mathcal{M}|\times|\mathcal{T}|\times 2 + |\mathcal{M}|\times n_{\mathrm{multiI}} = 3\cdot25\cdot2 + 3\cdot7 = 171\).

| Quantity | Value |
| --- | ---: |
| \|T\| | 25 |
| \(n_{\mathrm{multiI}}\) | 7 |
| \(N_{\mathrm{fam}}\) (legs per family) | **57** |
| \|M\| (locked roster families) | 3 |
| Total legs \(L\) | **171** |

**Provenance of 57:** Independently derived by applying the frozen SPEC Cost formula to the Option L Study 2 design (\(|T|=25\), \(n_{\mathrm{multiI}}=7\), \(|M|=3\)). It **coincidentally matches** Study 1’s per-model leg count under the same frozen \(\mathcal{T}\) and multi-I set; it is **not** justified by copying Study 1’s observed attrition, DONE rate, or valid-pair rate.

**§0 lock block is signed.** \(N_{\mathrm{fam}}=57\) / \(L=171\) are execution-frozen.

---

## 7. \(D\) semantics

Carry-forward from `DESIGN.md` + `registry_semantic_frozen.json`:

- \(D\) = typed component list frozen **before** Study 2 agent runs
- Roles: `determining` | `held` | `distractor`
- Weights: determining/held \(w_i=1\); distractor \(w_i=0\); no post-hoc refit
- Gold from **guest probes**, never writer `track`
- \(\hat D\) from final-answer extraction; **no LLM-as-judge** for match bits
- Match by `kind` (`money_usd` ≤$1 or same whole dollar; `integer` exact; etc.)

Surviving variants after inject-probe: **32** (universe doc).  
Rejected (not in confirmatory \(\mathcal{A}\) eligibility via task drop): `situated_action-f029`, `contradiction-f024`.

---

## 8. Moves / held / do-not-touch

| Class | Rule |
| --- | --- |
| **Moves** | `determining` components that \(I\) is designed to change across \(\ell\in\{0,1\}\) (and multi-I second axis where registered) |
| **Held** | Must match pre-registered value on **both** legs; \(I\) must not move them |
| **Do-not-touch** | Registry / harness surfaces agents must not be handed as gold; channel rescues that rewrite \(D\) after probe failure are forbidden (f024 precedent) |
| **Distractor** | Present in world; \(w_i=0\); not in STS denominator |

Interventions: primary locked \(I_j\) per task; multi-I subset as in frozen universe (7 tasks × I2).

---

## 9. Extra probes / identifiability gate

**Already applied (Study 1 / Paper 2 freeze):** inject-probe identifiability → analysis universe amendment.  
**Study 2 rule:** do not re-open \(D\) to rescue a model failure. New probe only for **infra** (guest gold unreadable) with dated amendment — never to flip a Type label.

Identifiability statuses live on registry rows (`pending_probe` historical; confirmatory set uses surviving variants only).

---

## 10. Analysis plan (pre-outcome)

1. Build valid-pair set \(\mathcal{A}_i\) per model: both G0 and G1 legs `VALID_DONE` (`canonical_last_action == "DONE"`). G2 is robustness / multi-I, not required for pair membership in \(\mathcal{A}\).
2. Compute \(\overline{S}_i\) on base legs in \(\mathcal{A}_i\); \(\overline{\mathrm{STS}}_i\) on pairs in \(\mathcal{A}_i\).
3. Primary test: selection disagreement among models with \(|\mathcal{A}_i|\ge n_{\min}=3\).
4. Report family-wise STS on the **five** populated analysis strata (§2.2); do not headline a single pooled invariance rate; do not invent a categorical family-wise denominator.
5. Execution failures / incomplete / never-scheduled: coverage tables only — **not** \(Y=0\).
6. Gate 0A trajectories: qualitative harness taxonomy only — **not** mixed into \(\mathcal{A}\).
7. No model drop, prompt edit, or budget bump after seeing partial Study 2 outcomes (except pre-registered infra / budget-stop).

### 10.1 Historical valid-pair sensitivity (reference only; not a Study 2 target)

On Study 1 Flash under the same frozen \(\mathcal{T}\):

| Count | Semantics |
| ---: | --- |
| **7** | Canonical SPEC-aligned: G0∧G1 both `VALID_DONE` (measurement SoT) |
| **8** | Non-canonical: raw G0∧G1 `DONE` before Gate −1.5, **or** G0∧(G1∨G2) DONE |

Study 2 analysis uses the **canonical** pair definition only. The non-canonical **8** must not be used as \(n_{\min}\) evidence or as a design target.

### 10.2 Fixed-N attrition rule (Option L)

Under Option L the matrix size is **fixed** at \(|T|=25\), \(N_{\mathrm{fam}}=57\), \(L=171\):

- **No** expansion of \(\mathcal{T}\), **no** resampling, **no** mid-stream \(k\)/N adjustment in response to observed attrition, DONE rate, or valid-pair count.
- Families (roster models) with \(|\mathcal{A}_i| < n_{\min}=3\) canonical valid pairs remain **coverage-only**: reported in execution/coverage tables; **excluded only** from analyses that require \(n_{\min}\) (primary selection / ranking among agents with \(\ge n_{\min}\) pairs).
- Coverage-only status is **not** grounds to add tasks, drop models, or reopen sampling after outcomes.

---

## 11. Locked; remaining ops-only

§0 is **signed**. Method content in this file is frozen.

Still ops-only (must not rewrite protocol / roster / universe / N / seed):

- Exact dollar cap monitoring during the run (funding headroom was verified pre-launch on `008…9dd`)
- Host scheduling / tmux / QEMU infra
- Launch manifest: `out/study2_launch_manifest.md`

---

## 12. Stop conditions

Same spirit as Study 1 manifest: stop for infrastructure only (Control API dead, disk, systematic harness bug) — not because a model looks expensive or bad mid-run (unless pre-registered budget-stop). Attrition alone is **not** a stop-or-expand trigger (§10.2).
