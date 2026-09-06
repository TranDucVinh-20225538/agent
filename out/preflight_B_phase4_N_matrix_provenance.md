# Preflight B — Phase 4 N / matrix-shape completeness & provenance

**Mode:** audit-only · **no** lock-block signature · **no** edits to protocol, roster, task universe, N, seed, or model config  

**Audited draft:** `out/study2_phase4_preregistration.md`  
**Frozen references:** `paper/paper2_counterfactual_eval/PAPER2_SPEC.md`, `out/paper2_analysis_universe.json`, `out/paper2_analysis_universe.md`, `out/paper2_cell_order.json`

---

## B1. What the draft claims about N / shape

| Location | Text (summary) | Lock state |
| --- | --- | --- |
| prereg L22 | `N / legs \| **OPEN — see cost gate**` | Explicitly **unsigned** |
| prereg L133–145 | §8 “Legs formula (N open)” with \(L_{planning}=3\times25\times2+3\times7=171\) | Labeled planning / caution; not signed |
| prereg L18–21 | Roster / T / D / cell-order rows still ☐ | Not locked |

**Finding:** Draft does **not** assert a signed Study 2 N. Numeric 171 appears only as conditional planning arithmetic.

---

## B2. Provenance of the arithmetic factors

### Factor \|T\|=25 and \(n_{multiI}=7\)

| Quantity | Frozen source | Lines |
| --- | --- | --- |
| `n_tasks: 25` | `out/paper2_analysis_universe.json` | L19 |
| `n_multi_i_both_pass: 7` | same | L21 |
| `legs.formula` | `"|M| * |T| * 2 + |M| * n_multiI"` | L108–109 |
| `legs.n_multiI: 7`, `legs.total: 228` | same (Study 1 \|M\|=4) | L112, L115 |
| Human-readable legs | `out/paper2_analysis_universe.md` | L12–14 (`4×25×2+4×7=228`) |
| Cell order \|T\|=25, seed | `out/paper2_cell_order.json` | L2–3 `PAPER2_EXEC_SEED=20260904`, `n_tasks: 25`; L31 note frozen |

These values are the **post inject-probe analysis universe** (Study 1 / Paper 2 freeze), not a new Study 2 sample.

### Factor \|M\|=3

| Claim | Source | Status |
| --- | --- | --- |
| Gate 0A Qualified trio | `out/study2_roster_lock.md` / prereg §2 | Roster LOCK for qualification; Phase 4 lock-block still ☐ (prereg L18) |
| Study 1 \|M\|=4 | universe.json L18 `n_models: 4` | Includes `qwen/qwen3.5-9b`; **not** Gate 0A Study 2 roster |

### Cost formula (SPEC)

| Claim | Source |
| --- | --- |
| Legs derived after M and T listed | `PAPER2_SPEC.md` L253–259 section **“Cost (derived, not a target)”** |
| Shrink \(k\) in §4 if over budget — not drop M after outcomes | SPEC L262–263 |
| Count legs after inject-probe on analysis universe | SPEC L272–273 |

SPEC treats leg count as **derived**, not an a-priori KPI.

---

## B3. Is 57/family from a Study 2 sampling rule?

**Identity:**

\[
57 = 25\times 2 + 7 = |T|\times 2 + n_{\mathrm{multiI}}
\]

| Interpretation | Verdict |
| --- | --- |
| New Study 2 sampling draw in Phase 4 draft | **No** — draft does not re-run SPEC §4 stratum/`k` sampling |
| Per-model leg count **implied by reusing frozen analysis T** + SPEC cost formula | **Yes, conditional** |
| Same per-model count Study 1 used (228/4 = 57) | **Yes** — carryover of frozen T × formula; Study 1 total 228 used \|M\|=4 (universe.json L115) |
| Signed / preregistered for Study 2 | **No** — prereg L22 OPEN |

**Answer:** \(N=57\)/family is **Study 1 frozen-universe carryover arithmetic**, not an independently justified Study 2 sampling conclusion. It becomes methodological N **only if** humans sign “Task pool = analysis \|T\|=25” **and** lock N/legs in the Phase 4 block.

---

## B4. Completeness checklist (N/matrix-relevant only)

| Item | In draft? | Provenance gap? |
| --- | --- | --- |
| Cost/leg formula matching SPEC | Yes (prereg §8) | OK as formula |
| Explicit \|T\|, multiI pointers | Yes (§3) | OK |
| Cell-order seed citation | Yes (L21, §3) | OK |
| Statement that 57/171 are unsigned | Yes (L22, L143 caution) | OK |
| Restatement of SPEC §4 sampling that created seal | Thin | **PARTIAL** — adopts post-probe T rather than re-deriving |
| Patch-generation / inject rule (SPEC §7) | Missing in draft body | **GAP** (method completeness; not an N number) |
| Signed final N | No | **OPEN** (correct) |

---

## B5. Audit verdict

| Question | Verdict |
| --- | --- |
| Is matrix shape formula grounded in SPEC + sealed analysis universe? | **Yes** |
| Is \(171=57\times3\) a complete, locked Study 2 design? | **No** — planning identity only; lock block unsigned |
| Must humans treat 57 as preregistered sampling output? | **No** until Phase 4 N row is signed |

No matrix start authorized by this audit.
