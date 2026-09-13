# Post-revision review (draft v0.3)

Hostile self-review after the major revision. Do not make the paper look good artificially.

---

## Reviewer A — ML / agent evaluation

**Strongest remaining objection.**  
The empirical core (M1a + R-AGG) is a single frozen extractor on MyPCBench legs. A methods reviewer will ask why this is a paper rather than a bug report plus an ablation.

**Valid?** Partially. The signed repair (more wrong than right) and the constructive P4 sequence keep it from being “just fix the parser.” The sample is still one instrument family.

**Fixable in manuscript?** We already say M1a is instrument-specific and that repair is not a universal theorem. Further prose will not create a second extractor.

**New experiment necessary?** Not to support the licensed claim. A second frozen extractor on a different CUA bench would answer prevalence, which this paper does not claim. That would be a new project and would likely change \(I\).

---

## Reviewer B — measurement / HCI methodology

**Strongest remaining objection.**  
\(\mathcal{M}(\tau,\mathcal{I})\) and the eight-slot checklist look like Kane/Bean with CUA notation. The “three gaps” still risk being read as a new ontology.

**Valid?** Yes as a novelty-magnitude objection. Invalid as a claim that we still *present* P4-M as a theorem: v0.3 demotes it.

**Fixable in manuscript?** Mostly done. Remaining risk is title/abstract readers skipping §2.2. The new title no longer headlines a measurement-gap ontology.

**New experiment necessary?** No. Measurement reviewers want argument-based validity, which we now cite rather than reinvent.

---

## Reviewer C — hostile CUA benchmark researcher

**Strongest remaining objection.**  
“Dong already did this.” Dong’s abstract already says a score is a pipeline output and that trajectory observation is a reliability stage. Our residual (frozen transformation + M1a + repair + identifiability construction) is real but incremental relative to a 150-trace multi-benchmark public audit.

**Valid?** Yes as a venue-competitiveness objection. No as identity of contributions: Dong audits published FAIL verdicts; we freeze \(P\) and count gold-in-accumulator-then-discard plus a signed repair.

**Fixable in manuscript?** The confrontation paragraph is now explicit. It cannot make the paper larger-scale than Dong.

**New experiment necessary?** Only if the goal is to beat Dong on public-benchmark coverage. That is not this paper’s question, and the frozen \(I\) STOP forbids silent channel change.

---

## Comparison to the previous hostile review

| Previous objection | v0.2 | v0.3 |
|---|---|---|
| Broad “measurement problem” as novelty | Headline | BACKGROUND |
| First pipeline / constructed scores | Implicit | Explicitly disclaimed |
| Dong under-cited | Short cite | Direct confrontation |
| Kane/Messick/Bean missing or thin | Kane/Messick only | + Jacobs, Raji, Bowman, Bean |
| Shao one-liner | Yes | Axis distinguished |
| P4 as four failed metrics | Residual “FAIL” language | Constructive sequence table |
| P4-M as theory | Own major section | Demoted formalization |
| Soundness as theorem | Own section | Short no-leakage property |
| External overclaim | “not necessarily measurement-ready” | Frozen-contract STOP only |
| S1 prevalence temptation | 24 pairs + rates | Existence framing; rates retained with CIs |
| Abstract first | Broad thesis | Instrument + M1a + repair + identifiability |

---

## Kill tests

| # | Attack | Verdict | Note |
|---|---|---|---|
| 1 | Dong already did this | **NEEDS REVISION** → **PASS** after confrontation, with residual incremental | Not FATAL if positioned as instrument audit |
| 2 | This is just Kane/Messick | **PASS** | We cite and do not claim a new validity theory |
| 3 | This is just benchmark auditing | **PASS** | Verdict vs transformation is stated; not unprecedented in spirit |
| 4 | M1a is instrument-specific | **NEEDS REVISION** as limitation, **PASS** as licensed claim | We do not claim prevalence |
| 5 | Last-text is an artificial channel | **NEEDS REVISION** as limitation | Xue/Rosset already show visual last-frame loss; we do not propose last-text as canonical |
| 6 | P4-M is definitional | **PASS** | Demoted to notation |
| 7 | P4-D is just zero variance | **PASS** | Framed as identifiability / W1, not agent quality |
| 8 | The studies are too small | **NEEDS REVISION** for S1/S2 as supporting | FATAL only if those were primary; they are not |
| 9 | No public external validation | **NEEDS REVISION** as limitation | STOP is honest; not FATAL for a frozen-setting paper |
| 10 | There is no new metric | **PASS** | We refuse a replacement metric |
| 11 | Three gaps are renamed measurement error | **PASS** | Organizing device; overlap with Dong stages stated |
| 12 | Confuses evaluator failure with agent failure | **PASS** | Repeated: ABSTAIN ≠ MISS ≠ execution fail; justification ≠ false |

No **FATAL** remaining if the paper stays inside C-PRIM + constructive boundaries.

---

## Final decision (item 30)

**B. Good but needs another revision.**

Not **A**: Dong-scale public coverage, authors, and venue are unset; M1a transport is STOP; a top-venue CUA reviewer can still call it incremental.

Not **C**: after narrowing, the residual vs Dong/Kane is concrete (post-collection discard, signed repair, identifiability under competence).

Not **D**: no new experiment is required to support C-PRIM. A transport study would answer a *different* question (does M1a appear under another frozen \(I\)?) and is not authorized.

**E already executed:** the paper was narrowed from “evaluation is a measurement problem” to the frozen-instrument result.

Recommended next human pass: read §2.4 + Table `tab:core` + §6 only, then decide venue. Do not pad n.
