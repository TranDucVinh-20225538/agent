# Paragraph-to-ledger audit

**Superseded for v0.3.** Use `CLAIM_LEDGER.md` + `QUANTITATIVE_CLAIM_AUDIT.md`. The line map below was for draft v0.2 and is not maintained.

---

# (archived) Paragraph-to-ledger audit (draft v0.2)

**File:** `paper/evaluation_measurement_gap/draft/main.tex`  
**Rule:** every paragraph maps to a claim-ledger ID, or is tagged `META` (protocol/limit/positioning with no empirical claim).  
**Forbidden if untagged:** new metric, agent ranking, “benchmarks are wrong.”

Line numbers are 1-indexed in the current file.

## Checklist vs the five jobs

| Job | Status |
|---|---|
| 1. Paragraph → ledger | This file (v0.2, not v0.1) |
| 2. Intro + §§2–3 thesis-first | Done: spine is §1 sentence 1; RW is §2; measurement is §3 |
| 3. Argument-based related work, verified cites only | Done: `RELATED_WORK_VERIFICATION.md` |
| 4. Figure 1 + evidence-chain tables | `fig:gap`, `tab:gaps`, `tab:chain` + study tables |
| 5. Abstract last | Present; numbers from evidence map only |

## Abstract (lines 39–51)

| Lines | Text job | IDs |
|---|---|---|
| 40–43 | Spine + pipeline | T0 T1 |
| 45 | Outcome gap numbers | U1 S1-1 S2-1 S2-3 |
| 46 | Observation gap numbers | U2 S3-1 S3-2 B1 C1 |
| 47 | Justification gap numbers | U3 C2-1 D1 |
| 48–50 | Not a replacement metric; object is justification | M1 |

## §1 Introduction

| Lines | Job | IDs |
|---|---|---|
| 56–57 | Locked spine | T0 |
| 59–68 | Leaderboards observe the pipeline, not the task | T0 T1 |
| 70–104 | Figure 1 | T1 U1 U2 U3 |
| 106–110 | P4-B worked example 40 DONE / 5–5–30 | B1 |
| 112–128 | Three-gap table; populations not added | U1 U2 U3 META |
| 131–136 | Study roles; P4 not four failed metrics; M not a score | S1-1 S2 heading S3-1 M1 |
| 138–140 | Object of evaluation | M1 |
| 142 | What we do not claim | META / limits |

## §2 Related work

| Lines | Job | IDs |
|---|---|---|
| 147–148 | Positioning: operationalize, do not invent validity | T1 META |
| 152–158 | CUA eval as success/state/judge | META (RW-A) |
| 160–161 | Question is before the score | T0 |
| 165–171 | Kane/Messick/Cronbach; M is not a psychometric R | T1 T2 M1 |
| 175–180 | Artifact literature | META (RW-C) |
| 182–184 | We audit transformations, not only pass/fail flips | U2 META |

No paragraph in §2 asserts an empirical result from this programme.

## §3 Measurement problem

| Lines | Job | IDs |
|---|---|---|
| 189–194 | Definitions I,P,E,Y,S | T1 |
| 198–203 | Justification ≠ negation | T2 |
| 205–208 | Observable_τ ≠ Observable_I | M2 |
| 210–218 | Definition of M; not R(τ) | M1 |

## §4 Study 1

| Lines | Job | IDs |
|---|---|---|
| 223 | Question | S1-1 |
| 225–230 | Protocol; execution fail ≠ tracking miss | META / S1-1 |
| 232–236 | n=24; no pooled rate | S1-2 S1-3 (counts later) |
| 238–240 | Shared MyPCBench protocol | META |
| 249–263 | Table per-lane | S1-2 S1-3 |
| 265–272 | Phenomenon, not prevalence; CIs wide | S1-1 S1-2 S1-3 |
| 274–278 | Score-pair figure | S1-1 |

## §5 Study 2

| Lines | Job | IDs |
|---|---|---|
| 284–285 | Locked question (evidential basis) | S2 heading |
| 287–289 | Roster; pre-registered n_min | S2-1 S2-2 |
| 291–305 | Coverage table | S2-1 |
| 307–310 | Selection not evaluated; no 57-task rank | S2-1 S2-2 |
| 312–315 | Y=0 on 18/18 | S2-3 |
| 317–320 | Exploratory 4-task; n_eff caution | S2-4 |
| 322–326 | Completion filter; S≥90 non-DONE | S2-5 |
| 328 | Wrap: weak correspondence + unevaluable selection | S2-1 S2-3 |

## §6 Study 3

| Lines | Job | IDs |
|---|---|---|
| 333–340 | Unit 134/59; not agent FN rate | S3-1 |
| 342–343 | 39/59 | S3-1 |
| 345–361 | Cause table | S3-2 S3-3 |
| 363–367 | M1a; no single-cause; secondary FAILED | S3-2 S3-3 |
| 369–372 | Repairs are diagnostics | S3-4 |
| 374–391 | Repair table | S3-4 |
| 393–400 | Signed effects; R-CMP inert | S3-4 |
| 402–404 | C7 existence; n_eff=1 | S3-5 |
| 406–410 | 9/30 reconstruction | S3-6 |
| 412 | Comparative gate not opened (16/28) | META (not S3-7; not Gate 0) |
| 414–415 | Parser permissiveness is not a fix | S3-4 |

S3-7 (Gate 0) is **absent** from the draft, as required.

## §7 Study 4

| Lines | Job | IDs |
|---|---|---|
| 420–425 | Construction bounds, not four failed metrics | META / P4 heading |
| 429–433 | 40 DONE; 5/5/30; no_anchor | B1 |
| 451–454 | E1/E2 pass; E3/E4 floors; positive-but-incomplete | B2 B1 |
| 458–463 | Cov 0.1667; v1 FAIL | C1 |
| 467–473 | Form 0.9333; H3 N/E; ordinary MISS exists | C2-1 C2-2 |
| 477–485 | 30/0; I_CC=0; W1; G2 10/10; not agent indictment | D1 D2 |

## §8–9 P4-M + lemma

| Lines | Job | IDs |
|---|---|---|
| 490–493 | M is justification, not a reliability computer | M1 |
| 495–501 | Observable_τ ≠ I; measurement loss | M2 |
| 503–507 | Kind-only E; NL out of scope | M4 |
| 509–511 | D 30/30 is not a proof of M | D1 M1 |
| 516–520 | Typed soundness | M3 |
| 522–523 | What theory does not establish | M4 M3 |

## §10 External

| Lines | Job | IDs |
|---|---|---|
| 528–529 | Eligibility audit, no new agents | X1 |
| 531–533 | WAV / official WA / HF cards | X2 X1 |
| 535–538 | STOP; not agent ranking | X1 |

## §11–14 Discussion, framework, limits, close

| Lines | Job | IDs |
|---|---|---|
| 543–560 | Three gaps restated | U1 U2 U3 |
| 562–563 | Why not a metric hunt | M1 |
| 565–582 | Evidence-chain table | U1 U2 U3 (all empirical IDs) |
| 587–613 | Eight-point reporting list | M1 META |
| 618–626 | Limitations | M4 X1 G-VENUE G-P4M-EMP |
| 631–632 | Closing question | T0 M1 |

## Violations found in this pass

None that require cutting a result.

**Hygiene only (fixed in this pass if still present in tex):**
- File banner still said “v0.1 / abstract deferred” → update to v0.2.
- Ledger U2 still listed P4-M as observation evidence → align to P3 + P4-B/C.
- Figure 1 callouts said P3 / P4-M only → align observation with P3+P4-B/C and justification with P4-D/M.
