# Decision memo — Study 2 candidate sampling designs

**Status:** MEMO ONLY — no option selected · N not locked · no seed chosen · no preregistration edit · no matrix legs  
**Date:** 2026-09-06  
**Inputs:** `PAPER2_SPEC.md` §4–§6 + Cost; frozen analysis universe `|T|=25` (`out/paper2_analysis_universe.json`); sealed task `state_family` tags; Gate 0A roster `|M|=3`; cost envelopes in `out/study2_cost_per_leg.md`  
**Roster (fixed for all options):** `qwen/qwen3.8-flash`, `openai/gpt-5.5`, `anthropic/claude-opus-4.6`

---

## 0. Framing: what is “derived from Study 2” vs legacy carryover

| Design class | Meaning |
| --- | --- |
| **Legacy carryover** | Reuse the entire frozen analysis `|T|=25` and its pre-chosen `n_multiI=7`, yielding **57 legs/family**. This number is Study 1’s per-model count (`228/4`), not a new Study 2 sample. |
| **Study 2–objective designs** | Apply SPEC §4 stratum/`k` selection **on the frozen analysis task pool** (eligible IDs only), then set multi-I size by SPEC’s rule \(\min(8,\lceil 0.25|T|\rceil)\) with I2 only from tasks that already have surviving I2 variants. Sized for Study 2’s confirmatory goal (selection disagreement + family-wise STS), not for reconstructing Study 1’s 57. |

SPEC Cost (§ “Cost (derived, not a target)”, L253–263): legs are **derived after** \(\mathcal{M},\mathcal{T}\) are listed; if over budget, **shrink \(k\) in §4**, do not drop models after seeing outcomes.

---

## 1. Taxonomy inventory (critical ambiguity)

SPEC §4 defines **six** state-family strata (not seven):

`numeric` · `categorical / status` · `aggregation` · `temporal` · `relational / joint` · `preference / recommendation`

Among frozen analysis `|T|=25` (tags from `sealed_tasks.json` / semantic rows):

| state_family | n in \|T\|=25 | multi-I tasks in stratum (of 7) |
| --- | ---: | --- |
| relational_joint | 9 | 2 (`contradiction-f006`, `counterfactual-f002`) |
| aggregation | 5 | 1 (`aggregation-f040`) |
| numeric | 5 | 1 (`retrieval-f017`) |
| temporal | 4 | 2 (`contradiction-f011`, `counterfactual-f003`) |
| preference_recommendation | 2 | 1 (`preference_inference-f014`) |
| **categorical** | **0** | 0 — sole sealed categorical `situated_action-f029` is `REJECTED_NOT_IDENTIFIABLE` |

**Implication:** no confirmatory design inside `|T|=25` can balance or estimate a **categorical** family-wise STS. If a “seventh taxonomy type” was meant beyond SPEC’s six, it is **not defined in SPEC**; human must clarify before locking.

MyPCBench ID prefixes (aggregation/contradiction/… ) are **not** the SPEC strata; memo balances on **`state_family`**.

---

## 2. Shared mechanics (all Study 2–objective options)

**Eligible pool:** analysis `tasks` (25 IDs). Do not reintroduce rejected or Paper 1 tens.

**Stratum rule (SPEC §4):** for chosen \(k\) (pre-outcome), in each non-empty stratum  
`take all if n_stratum ≤ k else Random(seed).sample(k)`.  
**Seed:** must be newly declared at lock time (SPEC: new seed, not `20260826`; cell-order seed `20260904` is Study 1 execution order — do not silently reuse as subsample seed unless human explicitly so chooses).

**Multi-I rule (SPEC §4):** after \(\mathcal{T}\) frozen,
\(n_{\mathrm{multiI}}=\min(8,\lceil 0.25|\mathcal{T}|\rceil)\),
seed-select that many tasks from \(\mathcal{T}\).  
**Operational constraint:** only tasks in `multi_i_both_pass` have surviving I2 patches. So candidates = \(\mathcal{T} \cap\) that set (size ≤7). If \(|\mathcal{T}\cap multi|<n_{\mathrm{multiI}}\), take **all** available I2 tasks (coverage failure on multi-I count — report explicitly).

**Legs:**
\[
L = |\mathcal{M}|\times\big(2|\mathcal{T}| + n_{\mathrm{multiI}}\big),\quad |\mathcal{M}|=3.
\]
Per-family leg count \(N_{\mathrm{fam}}=2|\mathcal{T}|+n_{\mathrm{multiI}}\).

**Valid pair \(\mathcal{A}\):** both G0 and G1 `VALID_DONE` (canonical). G2 is robustness, not required for pair membership. Ranking requires \(|\mathcal{A}_i|\ge n_{\min}=3\) (universe + SPEC).

---

## 3. Non-transferable attrition reference (Study 1 Flash only)

Measured on `results/paper2_exec/qwen38-flash/CHECKPOINT*.jsonl` (57 legs):

| Quantity | Raw checkpoint | Canonical (`CHECKPOINT.canonical.jsonl`) |
| --- | ---: | ---: |
| DONE legs | 27 | **23** (27→23 reclass) |
| TERMINAL_FAIL | 30 | 34 |
| **Valid pairs** (G0∧G1 both DONE) | — | **7** / 25 tasks |

Prior discourse sometimes cited “8 valid pairs”; **canonical file yields 7**. Memo uses **7**.

**Crude Flash rates (reference only — do not transfer to GPT/Claude/Study 2):**

- DONE/leg ≈ \(23/57 \approx 0.40\)
- Valid-pair / task ≈ \(7/25 \approx 0.28\)
- Flash cleared \(n_{\min}=3\) (had 7 pairs)

**Forbidden:** using Gate 0A turn counts or Flash rates as GPT/Claude Study 2 forecasts. Below, “Flash-like projection” is a **sensitivity bracket for the decision-maker**, not a prediction.

---

## 4. Cost unit rates (planning envelopes)

From `out/study2_cost_per_leg.md` (not invoices):

| | Flash | GPT-5.5 | Claude 4.6 | Mean/leg (equal mix) |
| --- | ---: | ---: | ---: | ---: |
| mid USD/leg | ~0.09 | ~3.05 | ~2.98 | **~$2.04** |
| high USD/leg | ~0.24 | ~8.58 | ~8.40 | **~$5.74** |

Totals below ≈ \(L \times\) mean/leg. SMALL remaining (~$28 at last pull) is a **funding** constraint, not a sampling rule.

---

## 5. Candidate options

### Option L — Legacy full-universe carryover (not Study 2–resampled)

| Field | Content |
| --- | --- |
| **(1) Sampling rule** | \(\mathcal{T}=\) entire frozen analysis 25; \(n_{\mathrm{multiI}}=7\) as already listed in universe (no new stratum/`k` draw). |
| **(2) \(N_{\mathrm{fam}}\) / total** | **57** / family · **171** total |
| **(3) Taxonomy / multi-I balance** | All 5 non-empty strata as in §1 table (categorical still empty). Multi-I: 7 fixed tasks spanning 5 strata (rel 2, temp 2, agg/num/pref 1). **Imbalance:** relational_joint 9/25. |
| **(4) Attrition (Flash ref only)** | Flash-like: ~7 valid pairs/family expected if identical rate — clears \(n_{\min}\). **GPT/Claude unknown.** |
| **(5) Inference target** | Strongest **coverage** of frozen confirmatory T. Can support pre-registered **top-1 \(S\) vs STS disagreement** *if* each model yields \(\ge3\) valid pairs. Family-wise STS estimable for 5 strata (unequal n). **Not** a new design justifying 57 from Study 2 objectives — it is Study 1 scale reuse. |
| **(6) Cost** | mid ~**$350** · high ~**$980** |
| **Class** | **Legacy carryover** |

---

### Option A — Spec \(k=1\) minimum stratum coverage (Study 2–objective, exploratory)

| Field | Content |
| --- | --- |
| **(1) Sampling rule** | On analysis pool, \(k=1\): one task per non-empty stratum → \(|T|=5\). Then \(n_{\mathrm{multiI}}=\min(8,\lceil 0.25\cdot5\rceil)=2\), seed-pick 2 from \(T\cap multi\) (≤5 candidates depending on draw). |
| **(2) \(N_{\mathrm{fam}}\) / total** | **12** / family · **36** total |
| **(3) Balance** | Exactly 1 task × 5 strata; categorical still 0. Multi-I ≤2; may miss some strata in G2. |
| **(4) Attrition (Flash ref only)** | Flash-like pairs ≈ \(0.28\times5\approx1.4\) → **likely below \(n_{\min}=3\)** for ranking. |
| **(5) Inference** | **Exploratory / qualitative coding** and harness-protocol smoke across strata. **Cannot** honestly claim powered selection disagreement. |
| **(6) Cost** | mid ~**$73** · high ~**$207** |
| **Class** | Study 2–objective (coverage floor) |

---

### Option B — Spec \(k=2\) balanced core (Study 2–objective)

| Field | Content |
| --- | --- |
| **(1) Sampling rule** | \(k=2\): `relational_joint` sample 2 of 9; `aggregation` 2/5; `numeric` 2/5; `temporal` 2/4; `preference_recommendation` take all 2 → \(|T|=10\). \(n_{\mathrm{multiI}}=\min(8,\lceil 2.5\rceil)=3\), seed from \(T\cap multi\). |
| **(2) \(N_{\mathrm{fam}}\) / total** | **23** / family · **69** total |
| **(3) Balance** | Equal 2 per populated stratum (pref saturated at 2). Multi-I 3 — better than A, still thin. |
| **(4) Attrition (Flash ref only)** | Flash-like pairs ≈ \(0.28\times10\approx2.8\) → **borderline / often below \(n_{\min}=3\)**. |
| **(5) Inference** | **Exploratory–pilot confirmatory:** can illustrate family-wise patterns; selection disagreement only if empirical \(|\mathcal{A}|\ge3\) (not guaranteed under Flash-like attrition). Prefer pre-registering “rank only if \(n_{\min}\) met; else coverage report.” |
| **(6) Cost** | mid ~**$141** · high ~**$396** |
| **Class** | Study 2–objective |

---

### Option C — Spec \(k=3\) (Study 2–objective, mid scale)

| Field | Content |
| --- | --- |
| **(1) Sampling rule** | \(k=3\): rel 3/9, agg 3/5, num 3/5, temp 3/4, pref all 2 → \(|T|=14\). \(n_{\mathrm{multiI}}=\min(8,\lceil 3.5\rceil)=4\). |
| **(2) \(N_{\mathrm{fam}}\) / total** | **32** / family · **96** total |
| **(3) Balance** | Near-equal across 5 strata (pref still 2). Multi-I 4. |
| **(4) Attrition (Flash ref only)** | Flash-like pairs ≈ \(0.28\times14\approx3.9\) → **near \(n_{\min}\)**; one unlucky family of models could fail ranking entry. |
| **(5) Inference** | Plausible **pre-registered selection test** *conditional* on hitting \(n_{\min}\), with modest family-wise STS. Still weak for precise calibration curves / small CI on disagreement. |
| **(6) Cost** | mid ~**$196** · high ~**$551** |
| **Class** | Study 2–objective |

---

### Option D — Spec \(k=4\) (Study 2–objective, \(n_{\min}\)-aware)

| Field | Content |
| --- | --- |
| **(1) Sampling rule** | \(k=4\): rel 4/9, agg 4/5, num 4/5, temp all 4, pref all 2 → \(|T|=18\). \(n_{\mathrm{multiI}}=\min(8,\lceil 4.5\rceil)=5\). |
| **(2) \(N_{\mathrm{fam}}\) / total** | **41** / family · **123** total |
| **(3) Balance** | Stronger within-stratum replication where pool allows; pref still capped at 2; categorical still absent. Multi-I 5/7 available. |
| **(4) Attrition (Flash ref only)** | Flash-like pairs ≈ \(0.28\times18\approx5.0\) → more margin above \(n_{\min}=3\). |
| **(5) Inference** | Better support for **confirmatory top-1 disagreement** under Flash-like attrition brackets, plus family-wise STS for 5 strata. Still not a large-N power study; disagreement is a **point decision**, not a precise effect-size estimate. |
| **(6) Cost** | mid ~**$251** · high ~**$706** |
| **Class** | Study 2–objective |

---

### Option L vs A–D (summary)

| Option | Class | \|T\| | multiI | \(N_{\mathrm{fam}}\) | Total L | Flash-like \|A\|≈ | Inference posture | mid $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| **L** | Legacy carryover | 25 | 7 | 57 | 171 | ~7 | Full-T confirmatory *if* pairs accrue | ~350 |
| **A** | Study 2 \(k=1\) | 5 | 2 | 12 | 36 | ~1.4 | Exploratory / qualitative | ~73 |
| **B** | Study 2 \(k=2\) | 10 | 3 | 23 | 69 | ~2.8 | Pilot; ranking fragile | ~141 |
| **C** | Study 2 \(k=3\) | 14 | 4 | 32 | 96 | ~3.9 | Conditional confirmatory | ~196 |
| **D** | Study 2 \(k=4\) | 18 | 5 | 41 | 123 | ~5.0 | Stronger confirmatory bracket | ~251 |

---

## 6. Uncertainties & assumptions the human must resolve

1. **Taxonomy count:** SPEC has **6** strata; analysis T has **5** non-empty; **categorical empty**. What did “seven types” mean?  
2. **Is reuse of analysis `|T|=25` allowed without re-sampling?** Option L says yes (carryover). Options A–D say Study 2 should re-apply §4 `k` on that pool.  
3. **Seed:** must be chosen at lock; memo does not pick one. Reusing `20260904` vs new seed is a human call.  
4. **Multi-I candidate restriction** to surviving I2 variants — accept possible shortfall vs formula \(n_{\mathrm{multiI}}\).  
5. **Attrition:** Flash 23 DONE / 7 pairs is **non-transferable**. GPT/Claude Study 2 could be better or worse; designs A–B are fragile if attrition ≥ Flash.  
6. **Primary claim vs coverage:** If the paper’s primary is selection disagreement, designs that likely miss \(n_{\min}\) should be pre-registered as **coverage-only** or backed by a contingency (e.g. escalate `k` only via dated rule **before** outcomes — SPEC forbids outcome-driven fishing).  
7. **Budget vs method:** SMALL remaining cannot fund L at mid/high; funding lane is operational and must not silently rewrite \(\mathcal{M}\) or protocol.  
8. **Gate 0A:** qualification only; not an attrition prior.

---

## 7. What this memo does *not* do

- Select or recommend a single option  
- Lock N, seed, or Phase 4  
- Modify protocol, roster, or task universe  
- Run any Study 2 / matrix legs  

**Next human step:** pick a class (legacy L vs Study 2 `k∈{1,2,3,4}`), resolve taxonomy/categorical gap, declare seed + funding lane, then sign Phase 4 N.
