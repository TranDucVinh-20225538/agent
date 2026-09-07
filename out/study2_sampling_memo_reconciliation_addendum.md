# Addendum — sampling decision memo reconciliation (evidence-only)

**Status:** ADDENDUM ONLY — does **not** modify `out/study2_sampling_design_decision_memo.md` or Phase 4 preregistration · no option chosen · no N/seed lock · no SPEC/taxonomy amend · no legs  
**Date:** 2026-09-06  
**Companion memos:** `out/study2_sampling_design_decision_memo.md`, `out/study2_taxonomy_reconciliation_memo.md`

---

## A. Valid-pair count: 7 vs 8 — denominator and pairing semantics

### A1. Canonical SPEC pairing semantics

`PAPER2_SPEC.md` §5 L163: \(\mathcal{A}\) = valid pairs (**both** `DONE`) for that agent on \(\mathcal{T}\).  
Primary pair for selection is the **base+CF pair** (G0, G1), not “any two DONE legs.”

Gate −1.5 measurement rule (Flash audit): `VALID_DONE ⇔ canonical_last_action == "DONE"`  
(`results/paper2_exec/qwen38-flash/canonical_audit.md` L5).

### A2. Exact counts on Study 1 Flash (57 legs, \|T\|=25)

| Definition | Count | Source |
| --- | ---: | --- |
| Raw checkpoint: G0∧G1 `status==DONE` | **8** | `CHECKPOINT.jsonl`; tasks include `contradiction-f006` |
| Canonical checkpoint: G0∧G1 `status==DONE` **and** `canonical_final_action==DONE` | **7** | `CHECKPOINT.canonical.jsonl` |
| Canonical audit DONE legs (all G0/G1/G2) | 27→**23** | `canonical_audit.md` L8–9 |
| Non-SPEC alternate: G0 DONE ∧ (G1∨G2) DONE (canonical) | 8 | Same files; **not** SPEC \(\mathcal{A}\) |

**Lost pair (8→7):** `contradiction-f006`  
- Raw: G0 DONE, G1 DONE, G2 DONE  
- Canonical: G0 DONE; **G1 → TERMINAL_FAIL** (`canonical_final_action=PREDICT_CRASH`; was false DONE); G2 still DONE  
- Listed in `canonical_audit.md` mismatches L17  

Canonical G0∧G1 pair list (n=7):  
`aggregation-f020`, `contradiction-f004`, `counterfactual-f005`, `counterfactual-f013`, `retrieval-f002`, `retrieval-f009`, `retrieval-f010`.

### A3. Denominator semantics

| Quantity | Denominator | Meaning |
| --- | --- | --- |
| 8 / 25 | tasks in analysis \(\mathcal{T}\) | Raw (pre–Gate −1.5) G0∧G1 DONE pairs |
| 7 / 25 | same | **Measurement-valid** G0∧G1 pairs under canonical DONE |
| 23 / 57 | scheduled legs | Canonical DONE legs (not pairs) |
| 27 / 57 | scheduled legs | Raw DONE legs (inflated by false DONE) |

### A4. Resolution for citations

| Claim | Verdict |
| --- | --- |
| “8 valid pairs” | True **only** for **raw** G0∧G1 DONE (or non-SPEC G0∧(G1∨G2)) |
| “7 valid pairs” | True for **canonical / SPEC-aligned** G0∧G1 both VALID_DONE |
| Which Study 2 must use as reference | **7**, plus explicit note that raw 8 is obsolete after Gate −1.5 |

**Not an inconsistency in SPEC** — a **documented measurement remediation** (27→23 DONE; one destroyed raw pair).

---

## B. Taxonomy 7 / 6 / 5 and the meaning of multiI=7

### B1. Taxonomy (see also `out/study2_taxonomy_reconciliation_memo.md`)

| Number | Object | Verdict |
| ---: | --- | --- |
| **7** (checklist “taxonomy types”) | Prompt-only Task B wording | **Not** in frozen SPEC/seal/prereg — **not** a design object |
| **6** | SPEC §4 state-family vocabulary (L122–127) | **Canonical stratification names** |
| **5** | Non-empty strata in analysis \|T\|=25 | **Canonical confirmatory coverage** after rejects |

**f029** (`situated_action-f029`, seal `state_family=categorical`) → `REJECTED_NOT_IDENTIFIABLE` → categorical empty in analysis T.  
**f024** (`contradiction-f024`, temporal) → rejected → temporal 5→4; stratum still non-empty.

**Evolution vs inconsistency:** **Documented evolution** of the *analysis set*, not a SPEC contradiction. SPEC still lists six names; confirmatory coverage has five populated.

### B2. What multiI=7 is (and is not)

| Claim | Evidence | Verdict |
| --- | --- | --- |
| `n_multi_i_both_pass = 7` in universe | `out/paper2_analysis_universe.json` L21, L83–90; seven task IDs with surviving I1+I2 | Count of **tasks with both multi-I variants PASS** |
| SPEC multi-I **size rule** | SPEC §4 L135–136: after \(\mathcal{T}\) frozen, subset size \(\min(8,\lceil 0.25\|T\|\rceil)\) | For \|T\|=25: \(\lceil 6.25\rceil=7\), \(\min(8,7)=7\) |
| Match | Formula on \|T\|=25 **equals** stored `n_multiI=7` | **Consistent** — not a clash with “6 strata” or “5 non-empty” |
| multiI=7 vs taxonomy 6/5 | Different objects: **intervention robustness count** vs **state-family labels/coverage** | Must not be conflated with “seventh taxonomy type” |

Seal multi-I seed `20260903` (`seal_manifest.md` / `sealed_tasks.json`) selected which tasks get G2; inject-probe then left **7** with both variants PASS. That is **documented pipeline evolution**, aligned with SPEC’s size formula at \|T\|=25.

**Human amendment required?** **No**, for multiI=7 vs 6/5 — unless someone wants to *change* SPEC strata or revive categorical into confirmatory T (that would be a new dated amendment; out of scope).

---

## C. Provenance of N=57 — SPEC formula only (no attrition ratios)

SPEC Cost (L258–259):
\[
N_{\mathrm{fam}} = 2|\mathcal{T}| + n_{\mathrm{multiI}},\quad
n_{\mathrm{multiI}}=\min\bigl(8,\lceil 0.25|\mathcal{T}|\rceil\bigr)
\]
(with Study 2 \(|\mathcal{M}|=3\) ⇒ total legs \(L=3\,N_{\mathrm{fam}}\)).

**Direct application** (no Flash pair-rate inference):

| Design \|T\| (from memo options) | \(n_{\mathrm{multiI}}=\min(8,\lceil 0.25\|T\|\rceil)\) | \(N_{\mathrm{fam}}=2\|T\|+n_{\mathrm{multiI}}\) | \(L=3 N_{\mathrm{fam}}\) |
| ---: | ---: | ---: | ---: |
| 5 (k=1) | 2 | **12** | 36 |
| 10 (k=2) | 3 | **23** | 69 |
| 14 (k=3) | 4 | **32** | 96 |
| 18 (k=4) | 5 | **41** | 123 |
| **25 (full analysis)** | **7** | **57** | **171** |

**Therefore:** \(N=57\) is exactly SPEC’s cost formula on \(|T|=25\) with the SPEC multi-I size rule — **not** “57 because Flash had 57 legs” as an independent empirical choice, though Study 1 used the same frozen T and thus the same arithmetic.

Operational note (not used to alter the formula numbers above): I2 patches exist only for the seven `multi_i_both_pass` IDs; for \(|T|<25\), realized multi-I ≤ \(\min(n_{\mathrm{multiI}}, |T\cap multi|)\).

---

## Summary table

| Apparent conflict | Resolution |
| --- | --- |
| 8 vs 7 valid pairs | Raw vs **canonical** G0∧G1 DONE; lost `contradiction-f006` at Gate −1.5 |
| 7 vs 6 vs 5 taxonomy | Checklist “7” / SPEC **6** names / analysis **5** populated; documented |
| multiI=7 vs 6 strata | Different object; formula-consistent with \|T\|=25 |
| N=57 | SPEC \(2\cdot25+7\); carryover of frozen T, not ratio-inferred |
