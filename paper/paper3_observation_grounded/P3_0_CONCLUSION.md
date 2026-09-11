# P3-0 — Conclusion and closure

Status: **P3-0 IS CLOSED.** No further gate is opened on the Study 2 archive under P3-0.
Gate 1 / item-timing (0.4) is deliberately **not run**; see §5.

This document records what each gate asked, what it answered, and which pre-registered
verdict fired. It is the citable summary of `P3_0_SPEC.md`,
`P3_0_RECALL_AUDIT_SPEC.md` and `P3_0_IDENTIFICATION_AUDIT_SPEC.md`. It adds no new
quantity and revises no earlier number.

---

## 1. What P3-0 set out to ask

Whether the trajectories Paper 2 excluded from $\mathcal{A}$ for not terminating
canonically nevertheless contain recoverable evidence of task-relevant state, such that
completion-conditioned evaluation is hiding reliability information rather than merely
lacking it.

The discipline fixed in advance: archive audit → hypothesis → construct → controls →
sealed validation → metric. No model run, no metric, no threshold tuning, no qualitative
cherry-picking, and no reinterpretation of observable correctness as actual environment
correctness.

## 2. Gate 0 — completion-filter recovery

**Verdict: did not establish completion-conditioned evidence dissociation, and the
negative result is instrument-limited.**

0.1 enumerated 171 legs over three frozen lanes at 57 each. Excluded `VALID_DONE` legs
numbered 29 at 14/13/2; of these 16 fall on keyed tasks and are measurable, 13 are
vacuous because their task carries no gold formula. Vacuous is never a mismatch, so
reporting unkeyed legs as misses would have manufactured a failure.

0.1 also established Gate 0's **structural** ceiling: any cell with both G0 and G1
terminating is in $\mathcal{A}$ by definition, with zero exceptions in the corpus. Gate 0
can therefore only ever yield leg-level positives, and the pair-level $Y=0$ question is
closed by construction rather than underpowered.

The same enumeration discovered four **matched dissociation cells** — one leg `DONE` at
$S=100$, the partner leg non-`DONE` at $S=100$ — which became a pre-registered scope
extension (§5c) before the extractor touched any non-terminating leg.

0.2 ran the frozen extractor `3242c30` on exactly the 21 registered legs
(16 `gate0` + 4 `dissoc_nondone` + 1 `unmatched_nondone`):

* full component match **0/21**;
* pair-level component match under terminal-independent extraction **0/4**;
* no empty answers anywhere, `ans_ch` 249–2718, the four non-`DONE` legs carrying
  2567 / 2506 / 572 / 411 characters.

Two corrections to how that `0/4` may be quoted, both established later and both binding:

1. **It was `0/3`, not `0/4`.** `gpt/preference_inference-f010` is vacuous by
   construction — the gold lock records `path: null` for both its components — so that
   cell could never have matched.
2. **Two of the three testable cells have every component text-present on both legs**:
   `flash/counterfactual-f005` and `gpt/retrieval-f010`. These are **leads, not
   evidence.** Presence is neither correctness nor reliability. `gpt/retrieval-f010` is
   the cleaner lead — a 306-character `DONE` leg whose `jamaica_trip_total` has exactly
   one money candidate in the whole answer equal to gold, plus `host_name` as an exact
   normalised substring — but it remains a lead.

The firing pattern under §5c is **uninformative**, not *completion-dependent*, because
the terminating legs failed too. The reason was identified in 0.6: on $\mathcal{A}$
itself, the population Paper 2 used and trusted, 27 of 36 legs match zero components and
only 3 of 36 match fully, so `gate0`'s 13/16 and 0/16 are indistinguishable from it. The
low rate belongs to the extractor and holds everywhere.

**Gate 0 is therefore not a refutation.** A test that misses a large share of recoverable
values cannot refute anything. The hypothesis is *not supported*, and re-asking it would
require a new instrument and a new pre-registration, not a reinterpretation of 0.2.

## 3. 0.6 — extractor recall audit

**Verdict: mixed, as §7 anticipated, with the split running by component kind.**

57 legs, 134 leg×component rows, `ANOMALY = 0`, and the frozen extractor reproduced every
recorded gold and match value. Raw categories: `MATCH` 20, `RECALL_MISS` 39, `ABSENT` 61,
`VACUOUS_GOLD` 14.

Five rows are structurally unreadable and excluded from every share — three
`designated_booking_property` rows whose gold contains `(`, which `extract_entity` deletes
by `re.split(r"[(\[]", s)[0]`, and two `nyc_checkin_date` rows where `_DATE_RE` is
ISO-only so "no date" and "non-ISO date" are indistinguishable. All five are `ABSENT`, so
the exclusion **raises** the miss share and is not a neutral cleaning.

`RECALL_MISS / (RECALL_MISS + ABSENT)`, Wilson 95%:

| population | miss | absent | share | 95% CI |
|---|---|---|---|---|
| $\mathcal{A}$ | 24 | 39 | 0.381 | [0.271, 0.504] |
| outside $\mathcal{A}$ | 15 | 17 | 0.469 | [0.309, 0.636] |
| all 57 legs | 39 | 56 | **0.411** | [0.317, 0.511] |

The two strata are indistinguishable. By kind: `integer` **0.722** [0.491, 0.875],
`entity` 0.368, `money_usd` 0.345, `state` 0/3, and `categorical` has 2 `MATCH` and zero
interpretable non-matches, so it is non-informative. The `INT_RE` lookahead hazard was
checked and does not bind.

The `ABSENT` side carries its own strong evidence and must not be underplayed.
`claude/counterfactual-f013` G0 and G1 have 462 and 346 money candidates in 16043- and
9388-character answers at $S=100$, with all three gold values absent on both legs. With
that many candidates, absence is highly informative: the agent emitted hundreds of numbers
and none was right. That is the cleanest genuine instance in the corpus of the phenomenon
Paper 1 established by hand-coding, reached here by a fully automated route.

## 4. 0.7 — identification audit

**Verdict: §7 branch 2. The primary prediction held; the secondary prediction failed.**

Instrumentation, not reimplementation: `_unique_or_none` was wrapped by a recorder
returning the original value unchanged, and the frozen `extract_component` and
`gold_for_component` were called as `extract_leg` calls them. Both faithfulness guards
passed — every gold and reported value reproduced 0.6, and no recorded call returned a
value from an empty filtered list.

* **Primary — held.** `M1 / RECALL_MISS` = 20/39 = **0.513** [0.362, 0.661], the plurality
  cause against `M2` 9, `M3` 5, `M4` 5.
* **Secondary — FAILED, and reversed.** Predicted higher in the mechanism task family,
  observed lower: `counterfactual-*` + `contradiction-f004` 10/23 = 0.435 [0.256, 0.632]
  versus all other tasks 10/16 = 0.625 [0.386, 0.815]. The CIs overlap, so a reversal is
  not established either; the injected-world explanation is simply **unsupported**. No
  counterfactual story may be told about these misses.
* **Specificity — cuts hard.** `M1` also fires on 25 of 61 `ABSENT` rows, 0.410
  [0.295, 0.535]. Window disagreement is a general property of the extractor on this
  answer corpus, not a specific explanation of recall failure. `M1` alone explains little.

**The defensible core is `M1a`**: gold was among the values the extractor accumulated and
then discarded. `M1a` is 13/39 = **0.333** [0.206, 0.490] among misses and **0/61** among
`ABSENT`, where it is impossible by construction — gold cannot be among window candidates
if it is absent from the whole text, and `ANOMALY = 0` closes the window-boundary escape.
`M1a` is thus the one cause specific to recoverable-but-discarded evidence.

Its severity is the finding. `_unique_or_none` compares every value to `found[0]` and
demands unanimity, so one dissenting window overrides any majority. In **7 of the 13**
`M1a` rows the gold value was a strict majority of the accumulated candidates and was
still discarded, including 10 of 12 for `flash/retrieval-f009/G1/nyc_flight_confirmation`,
4 of 5 for `flash/aggregation-f020/G1/batbucks_cash`, and 3 of 4 on three further rows.

**No single replacement cause is established.** The verbatim `found` lists — pre-registered
to be printed precisely so their content could be checked — show the dissenting value
equals another keyed component's gold on the same leg in only **5 of 13** rows. That is a
minority, the remainder is heterogeneous, and cross-component contamination is therefore
recorded as an observation, not adopted as a mechanism. Pursuing it would need its own
pre-registration, and at 5/13 it does not merit one on this archive.

**The §2.1 control is partially falsified.** Both `gpt` rows on
`counterfactual-f005/gme_avg_cost` are `M2` as predicted, and the two `flash` rows are
`HIT`, proving the component works when the agent writes "avg cost". But `claude` on the
same component is `M1`, and `flash/contradiction-f004/G1` is `M2` despite carrying the
covering `average cost` label. The malformed label — `avg(erage)? cost` matches `avg cost`
and `avgerage cost` but not `average cost` — does bind, on two rows, and is not the
pattern that was predicted. This reinforces the refusal to tell a single-cause story.

Measurement failure in this instrument is **multi-mechanism**: `M1` 20, `M2` 9, `M3` 5,
`M4` 5 among misses, and `M1` 25, `M2` 19, `M3` 2, `M4` 15 among absences. The extractor
reported a confidently wrong value 20 times in total, including `3570.0` where gold was
`42.12`.

## 5. The construct-level finding, and why 0.4 was not run

The most consequential single observation in 0.7 is not about the aggregation rule.

`gpt/retrieval-f010/G1` — a non-terminating leg — has a `found` list containing the task
prompt verbatim (`"Provide the Jamaica booking total, host name, and amenities from the
booking record"`) and the markup `"</function>"`. The extractor is reading tool-call
scaffolding as answer content, which is expected for a leg whose last response sits
mid-tool-call. Several `entity` `M1b` rows likewise carry gold as a *substring* of an
over-long extraction (`"Sandals Resorts Concierge; amenities All-inclusive, Pool, ..."`),
which `match_categorical`'s exact equality converts into a miss.

So the final-answer observation channel is **not clean on exactly the population Gate 0
needed it to be clean on**. That is a construct-level limit, more fundamental than
`_unique_or_none`, and it bounds what this archive can support.

**0.4 / `p3_0_item_timing.py` is not run.** It is written, validated at 94/94 score
reproduction on Paper 1 cells, and left unexecuted on purpose: timing is not the question
0.7 opened, and running it now would dilute a result whose limit has already been
identified at a deeper level. Opening further gates on this archive would be fishing.

## 6. What Paper 3 is, and is not

**Not:** *"Agents exhibit completion/evidence dissociation."* P3-0 did not establish that,
and says so.

**Is:** reliability measurement for computer-use agents is itself a **layered measurement
problem**. Observable evidence can be discarded by an aggregation rule; a parser's label
coverage, window scope and segmentation can create false misses; and protocol-terminal
outputs can contaminate the observation channel. The Study 2 archive is used as a
**corpus for failure analysis of a measurement instrument**, not as evidence for a new
phenomenon about agents.

The contribution is accordingly the taxonomy, the diagnostic protocol, and the failure
analysis — not a new trajectory metric, and not a better regex.

## 7. What remains forbidden

Carried forward from all three specs and still binding:

* Gate 0's hypothesis is **not** revived by 0.6 or 0.7. Re-asking it needs a new
  instrument and a new pre-registration.
* `text_present` is a **recall ceiling**, never a measure of correctness or reliability.
  Presence may be coincidental; absence concerns only the final-answer channel.
* The construct is **observation-grounded reliability** / trajectory-level observability
  of task-relevant state. It is never called "state transition reliability", and
  observable correctness is never silently promoted to actual environment correctness.
* No single-cause story about `RECALL_MISS`. No counterfactual/injected-world story.
* No threshold may be introduced retrospectively to convert any of these into a verdict.
* Paper 2 stays frozen. `paper2-frozen` is the annotated tag `e42cb70` on commit
  `39cc662` and does not move; errata E-1 is recorded, not corrected.

## 8. Provenance

Pre-registrations and records, in order: `f737d24` P3-0 spec plus its two read-only
scripts, `50205ea` voiding the first 0.1 run and fixing the G2 undercount, `0c3327a` the
0.2 scope extension, `241266e` the 0.2 driver, `47e69a5` the recall-audit
pre-registration, `4b06098` the Paper 2 errata, `65f384d` the identification-audit
pre-registration with the 0.6 baseline frozen inside it.

Specs: `P3_0_SPEC.md`, `P3_0_RECALL_AUDIT_SPEC.md`, `P3_0_IDENTIFICATION_AUDIT_SPEC.md`.
Scripts: `p3_0_enumerate_legs.py`, `p3_0_extract_population.py`, `p3_0_recall_audit.py`,
`p3_0_identification_audit.py`, and the unexecuted `p3_0_item_timing.py`.
Host artifacts: `out/p3_0_legs.jsonl`, `out/p3_0_extracted.jsonl`,
`out/p3_0_recall_audit.jsonl`, `out/p3_0_identification_audit.jsonl` and its
`.stdout.txt`.

Every run was executed once on the host under `env_nf2` Python 3.12.3 against the frozen
extractor `3242c30a1423f9ef90754809e50cd2698c5560b5`, with no archive, lock, extractor or
`matching.py` modification, and no optional stopping.
