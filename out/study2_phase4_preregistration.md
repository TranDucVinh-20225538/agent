# Study 2 — Phase 4 preregistration (DRAFT for human lock)

**Status:** DRAFT — method gate; **not** execution-frozen until human signs the lock block.  
**Depends on:** Gate 0A cross-family PASS + roster LOCK (`out/study2_roster_lock.md`).  
**Sources (carry-forward, do not silently rewrite):**  
`PAPER2_SPEC.md`, `DESIGN.md`, `out/paper2_analysis_universe.*`, `registry_semantic_frozen.json`, Gate −2 protocol spec.

This document answers: *exactly what we will run, how often, and how we committed to analyze it before seeing outcomes.*

---

## 0. Lock block (sign to freeze)

When signed, no further edits to \(\mathcal{M}\)/\(\mathcal{T}\)/\(D\)/sampling/analysis plan except dated infra stop.

| Field | Value | Sign-off |
| --- | --- | --- |
| Roster \(\mathcal{M}\) | Gate 0A Qualified trio (below) | ☐ |
| Task pool \(\mathcal{T}\) | Analysis universe \|T\|=25 (below) | ☐ |
| \(D\) / roles | `registry_semantic_frozen.json` surviving variants | ☐ |
| Sampling / cell order | `out/paper2_cell_order.json` seed `20260904` | ☐ |
| N / legs | **OPEN — see cost gate** | ☐ |
| Analysis plan | §7 below | ☐ |
| Signed by / date | | |

---

## 1. Taxonomy (locked carry-forward)

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

State-family strata tags (SPEC §4): numeric, categorical/status, aggregation, temporal, relational/joint, preference/recommendation.

**Gate 0A failure modes** (stdout-distrust, completion-recognition, etc.) are **qualitative taxonomy** for harness notes — not confirmatory Study 2 outcome labels.

---

## 2. Agent set \(\mathcal{M}\) (roster LOCK)

| Provider family | Model ID | Qualification |
| --- | --- | --- |
| Qwen | `qwen/qwen3.8-flash` | Gate 0A v1.1 PASS |
| OpenAI | `openai/gpt-5.5` | Gate 0A v1.1 PASS |
| Anthropic | `anthropic/claude-opus-4.6` | Gate 0A v1.1 PASS |

**Excluded from Study 2 confirmatory \(\mathcal{M}\):** `qwen/qwen3.5-9b` (Study 1 SMALL lane only; not Gate 0A–qualified on the generic executor roster).  
**Not ranked by DONE@.** No post-hoc drop after seeing Study 2 \(S\)/STS.

Protocol substrate: frozen Gate −2 prompt/XML `qwen_cuabash` path + OpenRouter **stateless** `/chat/completions` transport (no native CU tools / no `previous_response_id`).

---

## 3. Sampling rule / \(\mathcal{T}\)

**Confirmatory task pool:** the frozen analysis universe

- `|T| = 25` — `out/paper2_analysis_universe.md`
- Cell order: `out/paper2_cell_order.json` (`PAPER2_EXEC_SEED=20260904`)
- multi-I (I1+I2 both PASS): **7** tasks (same universe)

**Explicit exclusion:**

> plant-token-terminate is a qualification-only smoke task and is excluded from the preregistered Study 2 task pool.

(`out/gate0a_task_separation.md`)

Paper 1’s ten tasks remain calibration only — not re-entered.

---

## 4. \(D\) semantics

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

## 5. Moves / held / do-not-touch

| Class | Rule |
| --- | --- |
| **Moves** | `determining` components that \(I\) is designed to change across \(\ell\in\{0,1\}\) (and multi-I second axis where registered) |
| **Held** | Must match pre-registered value on **both** legs; \(I\) must not move them |
| **Do-not-touch** | Registry / harness surfaces agents must not be handed as gold; channel rescues that rewrite \(D\) after probe failure are forbidden (f024 precedent) |
| **Distractor** | Present in world; \(w_i=0\); not in STS denominator |

Interventions: primary locked \(I_j\) per task; multi-I subset as in frozen universe (7 tasks × I2).

---

## 6. Extra probes / identifiability gate

**Already applied (Study 1 / Paper 2 freeze):** inject-probe identifiability → analysis universe amendment.  
**Study 2 rule:** do not re-open \(D\) to rescue a model failure. New probe only for **infra** (guest gold unreadable) with dated amendment — never to flip a Type label.

Identifiability statuses live on registry rows (`pending_probe` historical; confirmatory set uses surviving variants only).

---

## 7. Analysis plan (pre-outcome)

1. Build valid-pair set \(\mathcal{A}_i\) per model: both legs `VALID_DONE` (`canonical_last_action == "DONE"`).
2. Compute \(\overline{S}_i\) on base legs in \(\mathcal{A}_i\); \(\overline{\mathrm{STS}}_i\) on pairs in \(\mathcal{A}_i\).
3. Primary test: selection disagreement among models with \(|\mathcal{A}_i|\ge 3\).
4. Report family-wise STS; do not headline a single pooled invariance rate.
5. Execution failures / incomplete / never-scheduled: coverage tables only — **not** \(Y=0\).
6. Gate 0A trajectories: qualitative harness taxonomy only — **not** mixed into \(\mathcal{A}\).
7. No model drop, prompt edit, or budget bump after seeing partial Study 2 outcomes.

---

## 8. Legs formula (N open)

If confirmatory matrix = full analysis \(\mathcal{T}\) × roster \(\mathcal{M}\):

\[
L = |\mathcal{M}|\times|\mathcal{T}|\times 2 + |\mathcal{M}|\times n_{\mathrm{multiI}}
= 3\times 25\times 2 + 3\times 7
= \mathbf{171}
\]

**N / budget lane / whether to subsample \(\mathcal{T}\)** remain open until `out/study2_cost_per_leg.md` is locked by human.

---

## 9. Explicitly not locked by this draft alone

- Final **N** and dollar cap
- Whether GPT/Claude Study 2 legs use SMALL vs LARGE OpenRouter keys (operational; must not change protocol)
- Any \(\mathcal{T}\) subsample (if cost forces: must be seed-pre-registered **before** any Study 2 \(\tau\))

---

## 10. Stop conditions

Same spirit as Study 1 manifest: stop for infrastructure only (Control API dead, disk, systematic harness bug) — not because a model looks expensive or bad mid-run (unless pre-registered budget-stop).
