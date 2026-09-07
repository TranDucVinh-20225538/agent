# Study 2 — Phase 4 preregistration audit

**Status:** AUDIT ONLY — does **not** modify `out/study2_phase4_preregistration.md`, does **not** sign the lock block, does **not** run models.  
**Audited draft:** `out/study2_phase4_preregistration.md`  
**Checked against:** `paper/paper2_counterfactual_eval/PAPER2_SPEC.md`, `DESIGN.md`, `out/paper2_analysis_universe.*`, `out/paper2_cell_order.json`, `registry/seal_manifest.md`, `registry/registry_semantic_frozen.json` (by reference)

Legend: **OK** = draft covers with clear pointer · **PARTIAL** = mentioned but thin/ambiguous · **GAP** = missing or not explicit · **OPEN** = correctly left unlocked

---

## Checklist

| # | Required item | Draft status | Notes |
| --- | ---: | --- | --- |
| 1 | **7 taxonomy types** | **GAP / needs human clarify** | Draft §1 gives DESIGN **Alignment 2×2** (4 outcome cells) + SPEC §4 **6 state-family strata** (numeric, categorical/status, aggregation, temporal, relational/joint, preference/recommendation). Seal manifest uses the same 6 families. DESIGN Phase-3 operator list is also **6** (numeric replace, entity swap, deletion, temporal, joint state, held-channel). **No source in SPEC/DESIGN enumerates a canonical “7 taxonomy types.”** Draft does not claim 7. |
| 2 | **Sampling rule** | **PARTIAL** | Draft adopts frozen analysis `|T|=25` + cell order seed `20260904`. It does **not** restate SPEC §4 stratum/`k` sampling procedure that *produced* the seal — it **carry-forwards the post-probe analysis set**. OK if Study 2 explicitly reuses that freeze; not a new draw. |
| 3 | **Patch-generation rule** | **GAP** | SPEC §7: each multi-I variant needs own probe / **patch** / `expect` via `cf_inject.py`; reject≠rewrite D. Draft §5–6 mention interventions + identifiability but **never states the patch-generation / inject machinery rule** explicitly. |
| 4 | **Semantic D** | **OK** | §4: typed components, roles, weights, guest gold, no LLM match — points at DESIGN + `registry_semantic_frozen.json`. |
| 5 | **Moves / held / do-not-touch** | **OK** | §5 table; f024 do-not-touch precedent cited. |
| 6 | **Extra probes** | **PARTIAL** | §6: inject-probe already applied; Study 2 only infra re-probe. Does not list *which* extra/robustness probes (if any) remain scheduled beyond multi-I. |
| 7 | **Identifiability gate** | **OK** | §6 + rejected f029/f024; aligns with SPEC §7 spirit (reject, don’t rewrite D). |
| 8 | **Inclusion / exclusion** | **PARTIAL** | Roster inclusion OK (Gate 0A trio; exclude 9b). Task exclusion: Gate 0A plant-token + Paper 1 ten. **Missing explicit restatement of SPEC §4 keep-task eligibility bullets** (sqlite, dv_from_answer, no pin gold, etc.) — historically already applied to sealed set, but draft doesn’t restate. |
| 9 | **Analysis plan** | **OK** | §7: \(\mathcal{A}\), \(\overline{S}\), STS, \(n_{\min}=3\), coverage vs Y=0, no Gate 0A mix-in. |
| 10 | **Final N** | **OPEN (correct)** | Lock block marks N OPEN; §8–9 say not locked. |
| 11 | **Matrix shape** | **PARTIAL** | §8 gives \(L=|\mathcal{M}|\times|\mathcal{T}|\times2+|\mathcal{M}|\times n_{\mathrm{multiI}}\) with **illustrative** \(3\times25\times2+3\times7=171\). Shape formula matches SPEC Cost section; **numeric 171 is conditional**, not signed. |

---

## Special question: is N=57/family from frozen sampling, or Study 1 carryover?

**Arithmetic identity (frozen analysis universe):**

\[
57 = |T|\times 2 + n_{\mathrm{multiI}} = 25\times 2 + 7
\]

This per-model count is exactly what Study 1 used for each of 4 models (`legs` in `out/paper2_analysis_universe.json`: formula `|M|*|T|*2+|M|*n_multiI`, with `|T|=25`, `n_multiI=7`).

**Interpretation for Study 2:**

| Claim | True? |
| --- | --- |
| 57 is a **new** sample size drawn from a Study 2–specific sampling rule in the Phase 4 draft | **No** |
| 57 is the **leg count per model implied by reusing the frozen analysis \(\mathcal{T}\)** (25 tasks × base+CF + 7 multi-I extras) | **Yes — conditional** |
| 57 / 171 is **preregistered / locked** for Study 2 today | **No** — draft lock block leaves N OPEN; 171 is “if full T × roster M” |

So: **not an independent Study 2 sampling conclusion**; it is **carry-forward of Study 1’s frozen |T| and multi-I set into the SPEC cost formula**, pending human lock that Study 2’s confirmatory \(\mathcal{T}\) is that same analysis universe (no subsample).

---

## Gaps to close before signing (recommended edits — do not apply in this audit)

1. Clarify which object “7 taxonomy types” refers to, or drop the “7” requirement if strata=6 + alignment=4 was intended.  
2. Add explicit **patch-generation / inject** paragraph (SPEC §7 + `cf/paper2_interventions.json` PASS variants only).  
3. Label §8 numbers as **conditional planning identity**, not locked N (align with cost artifact).  
4. Optionally restate SPEC §4 inclusion bullets as “already satisfied by sealed analysis T” for auditability.

---

## Audit verdict

Draft is a **usable skeleton** for semantic D / held / analysis plan / roster, but **not sign-ready** until taxonomy-count ambiguity, patch-generation rule, and N-vs-carryover wording are resolved by human — without treating 57/171 as locked.
