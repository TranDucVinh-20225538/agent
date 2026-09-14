# Path A RESULT — heterogeneous FAIL, not unjustified FAIL

**STOPPED.** Do not retune. Do not count another rate.  
**Date:** 2026-09-13  
**Licensed finding (one sentence):** on 299 released FAIL (WA/VWA string·url, ELIGIBLE), the oracle collapses **126 empty \(I\)** and **173 candidate-then-mismatch** into one number. ABSTAIN \(\neq\) MISS. \(V=0\) does not say which.

Copy into `CLAIM_LEDGER.md` only the rows marked SAFE there.  
**Not** an AgentRewardBench-wide rate. Admission was 498/1302 string/URL (+ AssistantBench emptiness). 804 STOP families are out. Do not headline 498.

Dong 150 is not in this \(n\). Path B is closed. Human ARB labels are not Table 2 gold.

---

## Pipeline (frozen, then run)

| Step | Artifact |
|---|---|
| Family admission | `I_LOCK.md` (498 ADMIT / 804 STOP) |
| Episode eligibility | `EPISODE_ELIGIBILITY.md` |
| Extractor | `extract_i.py` (`test_extract_i.py` 12 OK) — **not retuned** |
| Download | 498/498 cleaned JSON, no screenshots, `data/admitted/` (~9.2G, not committed) |
| Classify | `classify_path_a.py` → `out/path_a_cells.csv` |
| QC of 8 SUCCESS∩ABSTAIN | `out/qc_success_abstain.md` (interpretation overlay; cells unchanged) |

`out/path_a_cells.csv` sha256 `614416284d3854183afeea330d4611c2f514612aafb263034721f0d3362fd516`

\(V\) = `summary_info.cum_reward` on **this trajectory** (`SUCCESS` iff \(>0\)). Not a leaderboard headline.

Official \(I\) on this admitted slice **is** last-answer / last-URL. Empty \(I\) → `string_match`/`url_match` FAIL is **correct spec of the oracle**, not a gap. Without human \(L\) or world state, \(\neg\mathrm{Justifiable}(\text{agent-failed})\) is not licensed.

---

## Episode eligibility

| | n |
|---|---|
| Family-ADMIT unique traj | 498 |
| EXEC_FAIL | 4 (all AssistantBench `err_msg`) |
| ELIGIBLE confirmatory | **494** |

EXEC_FAIL is not ABSTAIN.

---

## Table 1 — ABSTAIN vs released oracle \(V\) (ELIGIBLE)

ABSTAIN = locked \(I\) empty/missing. Not FAIL. Not “FAIL unjustified from \(I\).”

### 1a. WebArena + VisualWebArena (string / url / string_url)

ELIGIBLE \(n=366\) (all 180 WA + 186 VWA ADMIT were ELIGIBLE).

| | \(V=\)SUCCESS | \(V=\)FAIL | row |
|---|---|---|---|
| DETERMINING | 59 | 173 | 232 |
| ABSTAIN | 8 | 126 | 134 |
| col | 67 | 299 | 366 |

**Licensed split (FAIL column only):** 126 empty \(I\) vs 173 candidate then mismatch, of 299 released FAIL.

Do **not** publish \(126/299\approx 0.42\) as a rate of wrong or unjustified FAIL. That ratio is almost mechanical: no candidate \(\Rightarrow\) oracle FAIL.

WA only (180): ABSTAIN\|FAIL \(52/145\) vs 93 DETERMINING FAIL; ABSTAIN\|SUCCESS \(7/35\).  
VWA only (186): ABSTAIN\|FAIL \(74/154\) vs 80 DETERMINING FAIL; ABSTAIN\|SUCCESS \(1/32\).

`string_url` is inside this table (\(n=10\) ELIGIBLE), not a separate abstract stratum.

Do **not** pool AssistantBench into 126/299.

### 1b. AssistantBench (I-emptiness only; no HIT/MISS)

ELIGIBLE \(n=128\) / ADMIT 132.

| | \(V=\)SUCCESS | \(V=\)FAIL | row |
|---|---|---|---|
| DETERMINING | 13 | 53 | 66 |
| ABSTAIN | 0 | 62 | 62 |
| col | 13 | 115 | 128 |

Licensed: **62/115** released FAIL have empty last `send_msg_to_user` (I-emptiness). Not pooled with 126/299. No HIT/MISS. AssistantBench 0/13 SUCCESS with empty \(I\) is consistent with SUCCESS usually requiring `send_msg_to_user`.

---

## Table 2 — HIT/MISS vs official gold (WA/VWA DETERMINING only)

**Secondary. Do not headline.** Mechanical only: `exact_match` equality, `must_include` substring, URL substring after unquote.  
`fuzzy_match`-only → `CORR_UNEVALUABLE` (no LLM). AssistantBench HIT/MISS **not opened** (no Yoran gold file used).

WA DETERMINING \(n=121\): HIT 21, MISS 83, CORR_UNEVALUABLE 17.  
VWA DETERMINING \(n=111\): HIT 4, MISS 77, NO_GOLD 29, CORR_UNEVALUABLE 1.

HIT 21 / MISS 83 on exact/`must_include` is the Dong-surface (paraphrase dies).  
VWA `NO_GOLD` 29 is intent-join failure against per-site raw configs, not a correspondence miss. Do not pool `NO_GOLD` with HIT/MISS or with the 17+1 `CORR_UNEVALUABLE`.

---

## Licensed reading (lock)

On 299 released FAIL (WA/VWA string·url, ELIGIBLE), the oracle collapses two different things into one number: **126 have no candidate in \(I\)** and **173 have a candidate then mismatch**. ABSTAIN \(\neq\) MISS. \(V=0\) does not say which.

That is Path A: **the oracle does not separate evidential absence from mismatch.** Not “42% FAIL are wrong.” Not ARB-wide. Not 498.

Empty \(I\) \(\to\) FAIL is the spec-correct oracle verdict. The claim that is *not* licensed (no human \(L\), no state) is “the agent failed the task in the world” for those 126 rows. That is not Dong: Dong reviewed traces and said some FAIL were *incorrect*; this experiment has empty \(I\) and does not say FAIL is unjustified.

WA/VWA split in appendix of the paper: 52/145 vs 93 DETERMINING FAIL (WA); 74/154 vs 80 (VWA).

---

## Eight SUCCESS ∩ ABSTAIN — QC, not a finding

See `out/qc_success_abstain.md`. Extractor frozen. Cells frozen.

| n | Recode (overlay only) |
|---|---|
| 7 | **EXTRACTOR_LAG.** No `send_msg_to_user` anywhere; last action `report_infeasible`. BrowserGym \(I\) is the infeasible-stop mapped to `N/A`; locked \(I\) is send_msg-only. Six confirmed WebArena `fuzzy_match` gold `N/A`. |
| 1 | **QC_OPEN** — unexplained; closed. `webarena.723` gpt-4o: no send, no `report_infeasible`, \(V=1\), gold `N/A`. Not a finding. Do not reopen the extractor. |

Eight SUCCESS ∩ ABSTAIN stay out of the PDF. Do not recode ABSTAIN \(\to\) FAIL. Do not retune the extractor from these eight.

**STOP Path A.** Do not retune. Do not count another rate.

---

## Optional sensitivity (not Table 2, not a CORE finding)

Full join (366/366 WA/VWA ELIGIBLE; `out/human_crosstab.md`).
Most trajectories have one annotator (318/366), so “unanimous” is often a single label.

Among released FAIL, ARB `trajectory_success` unanimous Successful is **4/126** on empty \(I\) and **50/173** on candidate-then-mismatch (any: 5/126 vs 53/173). Fisher two-sided \(p\approx 1.5\times 10^{-9}\).

Empty-\(I\) FAIL is **not** the hidden-success pocket. Human-labeled success concentrates in the mismatch cell — the Lù/Dong surface. Licensed: the two FAIL kinds are not exchangeable vs human labels. Not licensed: unjustified-FAIL rate; 50/173 as this paper’s discovery.

---

## Forbidden

- 126/299 as “FAIL not justified from \(I\)”
- Eight SUCCESS ABSTAIN as a published finding
- “We audited AgentRewardBench” / 498 as a prevalence corpus
- Pooling 804 STOP families
- Using ARB human success as correspondence gold
- Recoding ABSTAIN as FAIL
- Opening WorkArena because some traces have `send_msg_to_user`
- Shipping a new metric
- Pooling AssistantBench into 126/299

---

## Gold files

| File | Role |
|---|---|
| `schema/webarena_test.raw.json` | WA `eval` by `task_id` (sha256 `7b50386fd69163dbc05d615d834df4c6ed2c35596e97a1b10d17451c02537652`) |
| `schema/vwa_{classifieds,reddit,shopping}.raw.json` | VWA eval via site (from `visualwebarena.csv`) + intent match to `goal` |
