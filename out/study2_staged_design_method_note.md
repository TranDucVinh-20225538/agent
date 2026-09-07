# Method note — preregistered staged design for Study 2 confirmatory claims

**Status:** METHOD NOTE ONLY — no option selected · no N/seed lock · no preregistration edit · no legs  
**Date:** 2026-09-06  
**Depends on:** SPEC §4–§6 + Cost; taxonomy reconciliation (`out/study2_taxonomy_reconciliation_memo.md`); sampling addendum (`out/study2_sampling_memo_reconciliation_addendum.md`)

---

## 1. Question

Could a **preregistered staged** design (small \(k\) first, then expand) support Study 2’s **intended confirmatory claims** (chiefly Layer B: top-1 \(\overline{S}\) vs \(\overline{\mathrm{STS}}\) disagreement among models with \(|\mathcal{A}|\ge n_{\min}=3\)), and what expansion rule must be fixed **in advance**?

---

## 2. What confirmatory claims require

From SPEC:

- Same analysis set \(\mathcal{A}\) for \(\overline{S}\) and \(\overline{\mathrm{STS}}\) (valid pairs = both DONE).  
- Rank only agents with \(|\mathcal{A}_i|\ge n_{\min}=3\).  
- No post-hoc restriction of \(\mathcal{T}\) or \(\mathcal{M}\) to produce disagreement (SPEC §6 “Fishing”).  
- If over budget: shrink \(k\) in §4 **before** outcomes drive the choice; do not drop models after seeing results (Cost L262–263).

A stage that is too small (e.g. \(k=1\), \(|T|=5\)) is, under Flash-like brackets, likely to yield \(|\mathcal{A}|<3\) — then the stage can support **coverage / qualitative coding**, not a confirmatory selection claim.

---

## 3. When staging can support confirmatory claims

Staging is methodologically defensible **only if** all of the following are locked **before any Study 2 \(\tau\)**:

1. **Stage-0 (pilot) claim ceiling:** explicitly “exploratory / coverage / attrition measurement only — not Layer B.”  
2. **Confirmatory stage identity:** which \(k\) / \(|T|\) / \(n_{\mathrm{multiI}}\) (via SPEC formula) constitutes the **sole** pre-registered Layer B analysis set.  
3. **Expansion trigger:** a rule that does **not** depend on observed \(S\), STS, Type labels, or which model “looks bad.”  
4. **One-way gate:** expansion may add pre-listed tasks; it may **not** drop tasks or models after seeing outcomes.  
5. **Analysis set rule:** either  
   - **(Strict)** Layer B uses **only** the confirmatory-stage \(\mathcal{T}\) (pilot legs excluded from \(\mathcal{A}\)), or  
   - **(Inclusive)** Layer B uses pilot∪confirmatory **only if** that union was named as the analysis \(\mathcal{T}\) at lock time.  
   Mixing “pilot for exploration then silently fold into confirmatory \(\mathcal{A}\)” without pre-registration is fishing-adjacent.

Under those constraints, staging can (a) spend little compute learning **operational** attrition, then (b) run the pre-declared confirmatory matrix — without treating Stage-0 as the selection test.

---

## 4. Expansion rules that are **allowed** if fixed in advance

Examples of **outcome-blind** triggers (illustrative — human must pick one; this note does not select):

| Rule ID | Trigger (must be numeric/operational, not semantic) | Expand to |
| --- | --- | --- |
| E1 | After Stage-0 completes all scheduled legs (regardless of DONE rate) | Pre-declared confirmatory \(k^\star\) |
| E2 | If Stage-0 valid-pair count \(<\ n_{\min}\) **for every** roster model (coverage failure), expand once | Pre-declared \(k^\star\) |
| E3 | Budget remaining ≥ pre-declared USD floor after Stage-0 invoice reconciliation | Pre-declared \(k^\star\) or full \|T\|=25 |

**Forbidden triggers (must not be used):** expand because disagreement is absent; shrink because one model dominates; add tasks in strata where Type B appeared; exclude tasks where Flash failed.

**Pre-declared target set:** the confirmatory \(\mathcal{T}\) (or the algorithm that produces it from seed + \(k^\star\) on the frozen analysis pool) must be written at lock time. Seed for stratum sampling must be declared then (SPEC: new seed, not outcome-touched).

---

## 5. What staging **cannot** do by itself

- It cannot create categorical confirmatory coverage (stratum empty after f029).  
- It cannot turn Gate 0A or Flash attrition into GPT/Claude predictions.  
- It cannot rescue \(n_{\min}\) by post-hoc redefining DONE (canonical rule already fixed).  
- A Stage-0 with \(N_{\mathrm{fam}}=12\) (k=1) does **not** become confirmatory merely by “looking promising.”

---

## 6. Minimal preregistration block (wording template; not applied)

> **Staged execution (optional).** Stage-0 uses SPEC §4 sampling with \(k=k_0\) on the frozen analysis pool; its scientific claim is limited to coverage and operational attrition. Layer B confirmatory analysis uses only the pre-declared Stage-1 design \((k=k^\star,\;n_{\mathrm{multiI}}=\min(8,\lceil 0.25|T|\rceil),\;\mathrm{seed}=s)\). Expansion from Stage-0 to Stage-1 occurs iff \<E-rule\>, which does not depend on \(S\), STS, or Type labels. Models and tasks are never dropped after outcomes. Pilot legs are \<excluded from / included in\> \(\mathcal{A}\) as locked here.

---

## 7. Verdict

A preregistered staged design **can** support the intended confirmatory claims **only** as a two-claim structure: Stage-0 exploratory + Stage-1 pre-declared Layer B matrix, with an **outcome-blind** expansion rule and a fixed analysis-set membership rule. Without that lock text, staging risks fishing and should not be treated as confirmatory.
