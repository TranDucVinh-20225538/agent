# Preflight C — Is “171 legs” a preregistered design or planning estimate?

**Mode:** evidence-only · **no** Study 2 execution · **no** N lock · **no** subsample seed  

**Sources**

| File | Role |
| --- | --- |
| `out/study2_cost_per_leg.md` | Cost envelope wording |
| `out/study2_phase4_preregistration.md` | Method draft N row |
| `out/paper2_analysis_universe.json` | Frozen Study 1 legs object |
| `paper/paper2_counterfactual_eval/PAPER2_SPEC.md` L253–263 | Cost = derived |

---

## C1. What “171” is

\[
171 = 3 \times 25 \times 2 + 3 \times 7 = 3 \times 57
\]

| Ingredient | Origin | Locked for Study 2? |
| --- | --- | --- |
| 25, 7 | Analysis universe freeze (`out/paper2_analysis_universe.json` L19, L21, L108–115) | Frozen as **Study 1 / Paper 2 analysis T**; Study 2 adoption still ☐ in prereg L19 |
| 3 | Gate 0A roster size | Roster qualified; Phase 4 M sign-off still ☐ (prereg L18) |
| Formula | SPEC “Cost (derived, not a target)” L253–259 | Formula frozen in SPEC; **instance** 171 not signed |

Study 1 used the **same formula** with \|M\|=4 → **228** legs (`universe.json` L115), i.e. **57 legs/model** already.

---

## C2. How cost / prereg files currently classify 171

| File | Classification | Lines |
| --- | --- | --- |
| `out/study2_cost_per_leg.md` | “COST ENVELOPE ONLY — **not** a matrix lock; **not** a methodological N lock”; \(L_{full}=171\) = **Planning identity only** | L3–15, L55 |
| `out/study2_phase4_preregistration.md` | N/legs **OPEN**; \(L_{planning}=171\) with caution not signed | L22, L133–145 |

**Finding:** On-disk artifacts already treat 171 as **carryover planning estimate**, not preregistered design.

---

## C3. Binary verdict

| Claim | Verdict |
| --- | --- |
| 171 is a **justified preregistered Study 2 matrix** | **False** |
| 171 is a **conditional planning estimate** (IF reuse analysis T ∧ IF \|M\|=3 ∧ SPEC formula) | **True** |
| Cost dollars attached to 171 in `study2_cost_per_leg.md` are invoices / locks | **False** — scenario envelopes only |

---

## C4. Cost figures under that planning IF (not a lock)

From `out/study2_cost_per_leg.md` (OpenRouter list prices 2026-09-06; engineering token scenarios):

| Scenario | Est. total API $ **if** \(L=171\) |
| --- | --- |
| low | ~$105 |
| mid | ~$350 |
| high | ~$980 |

SMALL key remaining ≈ $28 at pull → funding/lane is operational and **orthogonal** to whether 171 is methodologically locked.

Alternative locked \(L'\) (subsample) is **not** costed as a chosen design here — no seed selected (per instruction).

---

## C5. Required human action before treating 171 as design

1. Sign Phase 4 lock rows for \(\mathcal{M}\), \(\mathcal{T}\), sampling/cell order.  
2. Explicitly sign **N/legs** (171 or a different seed-locked \(L'\)).  
3. Only then attach budget lane + contingency to that signed N.

Until then: **171 remains carryover planning estimate.**
