# External protocol (frozen before any E2 count)

**Status:** FROZEN. No E2 frequencies were computed.  
**Date:** 2026-09-13  
**Workstream:** cross-instrument evidence-loss audit (new experiment; not P3/P4).  
**This file is the analysis contract.** If a later run wants to count E2, it must freeze a new protocol that names an **ELIGIBLE** instrument. This freeze produced none.

---

## Scientific question

**Primary.** Does an independently specified CUA evaluation instrument exhibit post-collection evidence discard analogous to P3 M1a?

**Secondary.** If yes, in how many of the audited eligible units? Report `n_E2 / n_eligible` only. Not population prevalence.

P3 M1a (unchanged, not re-run): gold entered the frozen MyPCBench extractor's `found` accumulator and was subsequently discarded (13 of 39 recall misses).

Analogous target (mechanism, not variable names):

```
determining evidence exists in τ
    → instrument observes/collects it into intermediate representation R
    → a later instrument transformation A discards it from R
    → final measurement misses recoverable evidence
```

Call this **POST-COLLECTION DISCARD (E2)** only after an instrument-specific taxonomy is frozen.

---

## What this experiment is not

Not a leaderboard, metric validation, agent comparison, P4-M validation, or replacement metric.  
Not a rerun of P3's extractor on external trajectories.  
If the external evaluator must be replaced by our parser: **STOP** (not cross-instrument).

---

## Candidate corpus (search set, not admitted set)

WebArena; WebArena-Verified; OSWorld / OSWorld-Verified dumps; VisualWebArena; AppWorld; τ-bench; WebJudge / Online-Mind2Web evaluation dumps; AgentRewardBench; CUAVerifierBench / Universal Verifier; WeaveBench (docs only).

Admission is per `ELIGIBILITY_AUDIT.md`. Only **ELIGIBLE** proceeds.

---

## Inclusion / exclusion

Include only if **all** of the following hold (hard STOP otherwise):

1. Independently sourced (not P1–P4 / MyPCBench).
2. Public recorded episode/trajectory (or equivalent).
3. Public evaluator implementation or spec.
4. Independently defined reference/gold (not reconstructed from that evaluator's verdict).
5. Observable intermediate evidence state **R**.
6. Observable final evaluator outcome.
7. Offline inspection.
8. No agent rerun.
9. No evaluator modification.
10. Evidence presence establishable independently of the final verdict.
11. Discard establishable from the evaluator transformation A(R).
12. ≥ 30 eligible episode-components, **or** a complete instrument-level corpus with explicit justification if smaller.

UNCERTAIN is not promoted to ELIGIBLE.

---

## Unit

One evaluation decision / episode-component for which (a)–(e) in the workstream brief hold.

---

## Observation / intermediate / discard (generic; not instantiated)

- **I:** the external evaluator's declared observation channel.
- **R:** the external evaluator's inspectable intermediate candidate/evidence representation.
- **A:** aggregation/filter/uniquify/threshold/top-k/truncation applied to R.
- **Y/S:** external final decision.

**Evidence-presence rule (generic):** gold/reference is present in τ and independently shown to have entered R, without using Y/S.

**Post-collection discard rule (generic):** gold/reference is in R, then absent from A(R), before Y/S is inspected.

**Independent reference rule:** task spec, released reference, or environment-state gold. Evaluator output of the same instrument is not gold for auditing that instrument.

---

## Outcome-blind procedure (not opened)

Phase A: evidence-presence and intermediate-state facts.  
Phase B: classify discard.  
Phase C: only then inspect final verdict.

No sampling was frozen because no ELIGIBLE frame existed. Preferred: complete enumeration of an eligible corpus.

---

## No-leakage

Do not use final verdict, benchmark score, or agent success label to decide whether evidence existed.

---

## Stopping rules

- No ELIGIBLE candidate → **STOP-NO-CORPUS**.
- Eligible corpus exists but causal E2 classification requires protocol change (new gold, new parser, agent rerun, evaluator edit) → **STOP-INCOMPATIBLE**.
- Eligible but n too small without justification → **STOP-INSUFFICIENT**.
- Do not relax gates to obtain a positive result.

---

## Exact analysis procedure executed

1. Inspect primary evaluator source (not README-only).
2. Inspect public trajectory/result schemas.
3. Fill `ELIGIBILITY_AUDIT.md`.
4. Promote none to ELIGIBLE.
5. Do **not** apply E0–E4 frequencies.
6. Record terminal STOP.

---

## Analysis code

`inspect_sources.py` in this directory (schema/hash inspection only; no E2 classifier).  
Hash recorded in `TERMINAL_STOP.md` after the file is written.
