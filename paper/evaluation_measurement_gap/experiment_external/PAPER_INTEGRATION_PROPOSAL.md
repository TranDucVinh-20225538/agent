# Paper integration proposal

**Experiment terminal:** STOP-NO-CORPUS (`TERMINAL_STOP.md`).  
**Do not auto-edit** `draft/main.tex`.

---

## Does this change novelty?

**No strengthening.** M1a remains demonstrated only in the frozen MyPCBench extractor. Cross-instrument transport was **not identified as possible under the declared contract**, not “shown false.”

The paper must **not** say:

- “we showed M1a does not transport”
- “other CUA evaluators preserve evidence”
- “public CUA artifacts are generally not measurement-ready” (already forbidden; still forbidden)
- any E2 rate

It **may** (optional, later human pass) say, in limitations:

> We attempted to locate an independently specified CUA evaluator in which determining gold enters an inspectable intermediate representation and is then discarded. No public instrument jointly satisfied that contract (independent gold at the grain of R, observable R, observable A(R), recorded episodes). WebJudge and the Universal Verifier have collect-then-filter *architecture*, but released gold is not at that grain.

That is a **limitations** sentence, not a new contribution.

---

## Claims that may be strengthened

None.

---

## Claims that must remain unchanged

- P3 M1a 13/39; R-AGG +8/−18; ALL worse than frozen.
- P4 constructive boundaries.
- P4-M demotion.
- External-validation STOP at `de66e0a` (different frozen I; this workstream does not reopen it).
- “M1a is instrument-specific until transported” — **keep**. This audit did not transport it.

---

## Recommended paragraph insertion

**None in the body until a human accepts the limitations sentence.** If accepted, one paragraph in §Limitations, citing this directory, not a new table of E2.

---

## Recommended table/figure

**None** for the manuscript now. `CROSS_INSTRUMENT_RESULT.md` is documentation only.

---

## Recommended limitations update (optional)

Keep the existing last-text / instrument-specific caveats. Add the STOP-NO-CORPUS sentence above if integrating. Do not replace the P4-M eligibility STOP with this result (different I, different question).

---

## Novelty / reviewer objection

The strongest remaining objection (“M1a may be instrument-specific”) is **not dissolved**. It is **documented as currently unanswerable** from public evaluator+gold+R dumps without changing protocol (new frame-level gold, or swapping in our parser).
