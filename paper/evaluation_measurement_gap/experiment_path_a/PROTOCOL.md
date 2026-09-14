# Path A — public I + ABSTAIN (frozen before any unjustified-rate)

**Status:** **STOPPED.** Admission + extractor frozen. Licensed reading locked. `webarena.723` gpt-4o remains QC_OPEN (unexplained; closed). Do not retune. Do not count another rate.  
**Date:** 2026-09-13  
**This is a new experiment.** It does not reopen `8680588` STOP-NO-CORPUS, does not transport M1a, and does not run the P3 extractor.

Path A is closed on this contract. A later rate requires a dated successor that names the change; this file is not a license to retune or to count again.

**Licensed Path A sentence (RESULT):** On 299 released FAIL (WA/VWA string·url, ELIGIBLE), the oracle collapses 126 empty \(I\) and 173 candidate-then-mismatch into one number. ABSTAIN \(\neq\) MISS. \(V=0\) does not say which.

Retired reading: “126/299 FAIL are not justified from \(I\).” Empty \(I\) \(\to\) FAIL is spec-correct for this oracle. No human \(L\) \(\Rightarrow\) no \(\neg\mathrm{Justifiable}(\text{agent-failed})\). Not Dong.

---

## Why this is not the old external experiment

`experiment_external/` asked: does an independent instrument expose intermediate `R` and then discard `A(R)`?  
Eligibility required inspectable `found`-like state. **ELIGIBLE N = 0** was the correct stop under that contract.

Path A asks a different question that does **not** require intermediate `found`:

> Under a frozen observation channel \(I\) that the published evaluator actually uses (last-answer / last-URL on the admitted slice), how many released FAIL mix **empty \(I\)** with **candidate-then-mismatch**? Does \(V=0\) separate them?

ABSTAIN means locked \(I\) is empty/missing. ABSTAIN is not FAIL, not MISS, and not “the FAIL verdict is unjustified from \(I\).” From empty \(I\), oracle FAIL is the spec-correct verdict. The unlicensed claim is “the agent failed in the world” (no human \(L\), no state).

Dong asks whether a published FAIL is *correct* (human/trace review).  
Lù et al. ask whether a rule-based/LLM judge agrees with expert success.  
Path A asks whether a published FAIL is **heterogeneous in \(I\)**.

---

## Scientific question

**Primary tables (do not pool AssistantBench HIT/MISS into WA/VWA):**

| Table | Universe | Counted |
|---|---|---|
| ABSTAIN vs released oracle \(V\) | ELIGIBLE among 498 ADMIT | \(I\) empty/missing? |
| HIT/MISS vs official gold | ELIGIBLE WA/VWA string/url only, after `reference_answers` / `reference_url` | correspondence |
| AssistantBench HIT/MISS | ELIGIBLE among 132, only with official Yoran gold | never ARB human labels |

\(V\) = `summary_info.cum_reward` on **this released trajectory**. Not “WebArena published score.”

Human `trajectory_success` is a **sensitivity** slice (Lù), not primary \(L\).

498/1302 is admission, not an ARB-wide audit rate. `string_url` n=4 and n=6 are not an abstract stratum.

---

## Corpus (admitted search set)

**Primary corpus:** AgentRewardBench (`McGill-NLP/agent-reward-bench`).  
Public trajectories + expert `trajectory_success` + official rule-based evaluation as the published \(V\).

Schema inspected from `data/annotations.csv` (sha256 `5fef3f9f996ec664f5eb371409a708ebac613991d38fa11c9fa6e27a57f3bef9`):

- 1408 annotation rows / 1302 unique `(benchmark, task_id, model_name, exp_name)`
- benchmarks: webarena 501, workarena 475, visualwebarena 300, assistantbench 132
- `trajectory_success`: Successful / Unsuccessful / Unsure

These schema counts are **not** Path A results. They do not go in the paper until a licensed RESULT exists.

**Not used as Path A corpus:** Who&When, TRAIL, AgentProcessBench, SWE Lucky-Pass dumps. Those label *agent* faults, not published CUA \(I\)-justification.

**Dong 150:** FAIL-only by construction. May be used later as a sensitivity slice. Not the primary frame (would look like Dong).

**OSWorld-Verified:** official \(I\) is a VM state getter. Offline `traj.jsonl` is not that getter. Admit only if getter payloads are reconstructible without rerunning the VM; otherwise **STOP-INCOMPATIBLE** for that slice, do not switch \(I\) to last-text.

---

## Frozen objects

| Object | Definition | Forbidden substitute |
|---|---|---|
| \(I\) | Official observation of the admitted family, via `extract_i.py` | P3 extractor; axtree-as-html; last-answer as WorkArena validate |
| \(L\) primary | Official task gold (`reference_answers` / `reference_url` / Yoran file) | ARB human `trajectory_success` |
| \(L\) sensitivity | ARB expert success, drop Unsure/disagreements | Primary correspondence gold |
| \(V\) | Released oracle `summary_info.cum_reward` on this trajectory | “WebArena published score”; human label |
| Episode | EXEC_FAIL vs ELIGIBLE (`EPISODE_ELIGIBILITY.md`) | Coding crash as ABSTAIN |
| \(E\) | DETERMINING iff locked \(I\) has a checkable candidate; else ABSTAIN | Using \(V\) or human \(L\) to decide emptiness |

HIT/MISS only on DETERMINING rows against official task gold, not ARB human labels. WorkArena gold is irrelevant (family STOP).

---

## Instantiating \(I\) (locked in `I_LOCK.md`)

Family admission is `I_LOCK.md` (2026-09-13). Do not retune after rates.
Admitted: WebArena/VWA `string_match` and/or `url_match` only, plus AssistantBench last-answer.
STOP-INCOMPATIBLE: any `program_html` / `page_image_query`, and all WorkArena.

---

## Procedure (outcome-blind)

1. Episode eligibility (`EPISODE_ELIGIBILITY.md`).
2. Extractor (`EXTRACTOR.md`); tests must not read \(V\).
3. Download cleaned JSON for `schema/admitted_keys.csv` only. No screenshots.
4. Gold files for HIT/MISS columns (WA/VWA; AssistantBench only if that column opens).
5. Classify \(E\) on ELIGIBLE rows without reading \(V\) or human \(L\). Then join \(V\). Then gold. Stop. Do not retune \(I\) or families.

---

## What this experiment is not

- Not M1a transport.
- Not a new reliability metric.
- Not judge accuracy (that is AgentRewardBench / Lù).
- Not “public benches are not measurement-ready.”
- Not running extractor `3242c30` on public last-answers.
- Not Path B (WebJudge human decisive-frame). Do not count E2 on WebJudge Score.

---

## Stopping rules

- Cannot reconstruct official \(I\) from released traces → **STOP-INCOMPATIBLE** for that family.
- \(V\) missing and not imputable without \(L\) → UNKNOWN_V, drop from the primary table, report \(n\).
- \(n<100\) admitted episodes after family locks → **STOP-INSUFFICIENT** unless the admitted set is a complete locked family with justification.
- Do not relax ABSTAIN into FAIL to enlarge a headline gap.

---

## Paper integration rule

Nothing from Path A enters `draft/main.tex` except claims copied into `CLAIM_LEDGER.md`.  
Licensed for the manuscript: 126 vs 173 FAIL split; WA/VWA appendix split; AssistantBench 62/115 I-emptiness (not pooled).  
Forbidden in the manuscript: 126/299 as unjustified FAIL; eight SUCCESS ABSTAIN; “we audited AgentRewardBench” / 498 prevalence.
