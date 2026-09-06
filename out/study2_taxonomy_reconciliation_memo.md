# Taxonomy reconciliation memo — Study 2 strata (7 / 6 / 5)

**Status:** RECONCILIATION ONLY — no universe change · no resample · no preregistration edit · no N lock · no legs  
**Date:** 2026-09-06

---

## 1. Exact source of the 7 / 6 / 5 discrepancy

| Number | What it counts | Where it comes from | In frozen SPEC / seal / analysis? |
| ---: | --- | --- | --- |
| **7** | “taxonomy types” checklist item | **Human Task B prompt** (2026-09-06): audit checklist bullet `* 7 taxonomy types` — later echoed in sampling-design asks (“balance across the seven taxonomy types”). | **No.** Not in `PAPER2_SPEC.md`, `DESIGN.md`, `seal_manifest.md`, `out/study2_phase4_preregistration.md`, or the sealed/analysis JSON. Phase 4 draft lists **six** SPEC strata (prereg L44). Audit correctly marked “7” as **GAP** (`out/study2_phase4_preregistration_audit.md` L15). |
| **6** | SPEC **state-family** strata | `PAPER2_SPEC.md` §4 L120–127 table: numeric; categorical/status; aggregation; temporal; relational/joint; preference/recommendation. Seal realizes all six (`seal_manifest.md` “By state family”; `sealed_tasks.json` counts: rel 9, agg 5, temporal 5, numeric 5, pref 2, **categorical 1**). | **Yes — canonical stratification vocabulary.** |
| **5** | Non-empty **analysis** strata after rejects | Frozen `|T|=25` (`out/paper2_analysis_universe.json`): after removing `situated_action-f029` and `contradiction-f024` from confirmatory T. Counts on remaining tasks: relational_joint 9, aggregation 5, numeric 5, temporal **4**, preference_recommendation 2, **categorical 0**. | **Yes — canonical confirmatory coverage set.** |

### Why 6 → 5 (not a SPEC rewrite)

| Rejected ID | Seal `state_family` | Effect on analysis strata |
| --- | --- | --- |
| `situated_action-f029` | **categorical** (semantic row + seal) | Removes the **only** categorical task → categorical stratum **empty** in analysis T. Verdict `REJECTED_NOT_IDENTIFIABLE` (tier3; universe L92–96, L119–120). |
| `contradiction-f024` | **temporal** | temporal 5→4 in analysis T; stratum remains **non-empty**. |

No new category was created; no SPEC row was deleted. Empty categorical is **coverage consequence of reject**, not a seventh/fifth taxonomy invention.

---

## 2. Objects that must not be conflated

| Object | Count | Role for Study 2 |
| --- | ---: | --- |
| SPEC state-family strata | **6** | **Canonical task-stratum labels** for sampling / family-wise STS language |
| Non-empty analysis strata in \|T\|=25 | **5** | **Canonical strata with estimable confirmatory coverage** |
| MyPCBench `category` on seal (aggregation, contradiction, …, situated_action) | 6 prefixes | Benchmark labels; **not** SPEC strata (contradiction≠relational_joint one-to-one) |
| DESIGN Alignment 2×2 outcome cells | 4 | Track×ΔS **outcome** taxonomy — not task sampling strata |
| Component `kind: categorical` inside \(D\) | many rows | Gold-matching kind — **≠** state_family `categorical` |
| Checklist “7 taxonomy types” | — | **Prompt artifact only** — not a frozen design object |

---

## 3. Canonical taxonomy Study 2 can legitimately use

**Based only on frozen artifacts:**

1. **Stratification vocabulary (must match SPEC):** the **six** state families in `PAPER2_SPEC.md` §4 L122–127.  
2. **Confirmatory analysis strata (what \|T\| can support):** the **five** non-empty families in the frozen analysis universe.  
3. **`categorical`:** remains a SPEC stratum name but is **vacant** in confirmatory \(\mathcal{T}\) because `situated_action-f029` exited the analysis set. It may appear only as a **reported coverage gap / seal rejection**, not as a family-wise STS denominator with \(n\ge1\).  
4. **Do not** treat “7 types,” MyPCBench categories, Alignment 2×2, or component `kind` as the sampling taxonomy unless a **new dated SPEC amendment** says so (out of scope here).

---

## 4. Required wording for the preregistration (drop-in; not applied)

Use language that separates vocabulary from coverage:

> **Task strata (canonical).** Study 2 uses the six state-family strata defined in `PAPER2_SPEC.md` §4: numeric; categorical/status; aggregation; temporal; relational/joint; preference/recommendation.  
> **Confirmatory coverage.** The frozen analysis universe `|T|=25` has non-empty support for five of those six strata. The categorical/status stratum is empty in confirmatory \(\mathcal{T}\) because its only sealed member, `situated_action-f029`, is `REJECTED_NOT_IDENTIFIABLE` and listed in `sealed_minus_analysis`. Family-wise STS and stratum-balanced sampling statements apply only to strata with \(n\ge1\) in analysis \(\mathcal{T}\).  
> **Non-taxonomy.** Checklist language referring to “seven taxonomy types” is not part of the frozen SPEC and is not used. MyPCBench task `category` prefixes and DESIGN Alignment 2×2 cells are not sampling strata.

Also delete or replace any prereg/checklist bullet that says “7 taxonomy types” with the paragraph above when the human next edits the draft (this memo does **not** edit it).

---

## 5. One-line verdict

**7 = external checklist wording with no frozen source; 6 = SPEC state families (canonical vocabulary); 5 = non-empty analysis strata after f029 (and f024) rejection (canonical confirmatory coverage).** Study 2 must preregister **6-name vocabulary + 5-stratum coverage**, not invent a seventh type or pretend categorical is populated.
