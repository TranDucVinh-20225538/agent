# P3-0.6 — Extractor Recall Audit (pre-registration)

Status: **FROZEN BEFORE EXECUTION.** Written after seeing P3-0.2 leg/component match
counts, and before computing any text-presence quantity on any leg.

This is an amendment to `P3_0_SPEC.md`. It does not modify Gate 0, Gate 1, the frozen
extractor `3242c30`, `out/study2_gold_path_lock.json`, `protocol/matching.py`, or any
archive. It adds one read-only derived quantity.

---

## 0. Why this step exists

P3-0.2 ran the frozen extractor on the 21 pre-registered legs outside `A`. Result:

* `full match` 0/21 — 0/16 `gate0`, 0/4 `dissoc_nondone`, 0/1 `unmatched_nondone`;
* `cells with both legs matching` 0/4 — the pre-registered new quantity,
  *pair-level component match under terminal-independent extraction*, is zero;
* no empty answers: `ans_ch` 249–2718, and the four non-DONE legs carry
  2567 / 2506 / 572 / 411 characters.

The original completion-dissociation hypothesis is therefore **not supported**.

Under §5c the firing pattern is **uninformative**, not *completion-dependent*, because
the terminating legs failed too. The reason is now identifiable. Recomputed from
`out/study2_hatd_legs.jsonl`, the same frozen extractor on `A` — the population Paper 2
used and trusted — yields:

| | `A` (36 legs, all VALID_DONE) | `gate0` (16 legs, all VALID_DONE, outside `A`) |
|---|---|---|
| zero components matched | 27/36 = 75% | 13/16 = 81% |
| at least one component | 9/36 = 25% | 3/16 = 19% |
| full match | 3/36 = 8% | 0/16 |

The two columns are not distinguishable. At an 8% full-match rate, 16 legs predict ~1.3
full matches, so observing 0 is unremarkable. The low rate is a property of the
extractor and it holds everywhere, inside `A` as much as outside it.

Two explanations remain, and the 0.2 numbers cannot separate them:

1. **Genuine Type B at scale.** The rubric does not pin the determining set, and the
   answers really do not contain the gold values. Paper 1 established by hand-coding
   that Type B is real, so this is not a remote possibility. Sharpest instance: 7
   `gate0` legs scored `S = 100` with zero components matched, and Claude's only valid
   pair `counterfactual-f013` has 16043- and 9388-character answers at `S = 100` with
   0/3 matched.
2. **Extractor blindness.** The gold values are present in the answer text and the
   label-window identification strategy fails to reach them.

Which of these is true changes what Paper 3 must build, and it changes how Paper 2's
`Y = 0` should be read. It is decidable mechanically. That is this step.

## 1. Question

For each leg and each keyed component: **is the frozen gold value literally recoverable
from that leg's final answer text under a pre-specified deterministic normalization
rule?**

Nothing else. No LLM judge, no embedding or semantic similarity, no screenshots, no
manual qualitative reading, no external labels, no post-hoc exceptions.

## 2. What this quantity is, and what it is not

`text_present` is a **ceiling on extractor recall**. It is the answer to "could any
label-free reader of the final answer have found this value at all?"

It is **not** ground truth about reliability. Binding constraints:

* Presence does **not** mean the agent tracked task-relevant state. The token may be
  coincidental — an unrelated number that happens to satisfy the money tolerance.
* Absence does **not** mean the agent was wrong about the world. It means the value is
  not in the final answer text, which is the only channel this construct observes.
* This step does not license any change to `Y`, to STS, to `A`, or to any Paper 2
  number. Paper 2 stays frozen at `paper2-frozen`.
* Observable correctness is still not actual environment correctness. The §1 terminology
  lock of `P3_0_SPEC.md` continues to apply in full.

## 3. Population

Union of, deduplicated by leg identity `(lane, task, leg)`:

| source | n | provenance |
|---|---|---|
| `A` — valid pairs | 36 | `out/study2_hatd_legs.jsonl` |
| `gate0` measurable | 16 | `out/p3_0_extracted.jsonl`, stratum `gate0` |
| dissociation non-DONE | 4 | `out/p3_0_extracted.jsonl`, stratum `dissoc_nondone` |
| pre-registered unmatched non-DONE | 1 | `out/p3_0_extracted.jsonl`, stratum `unmatched_nondone` |
| **total distinct legs** | **57** | |

The four strata are disjoint by construction: `gate0` disqualifies G0/G1 legs of cells in
`A`, G2 legs are never in `A`, and the five non-DONE legs are excluded from both `A` and
`gate0` because both require `valid_done`. The 4 terminating partners of the
dissociation cells are already inside the 16.

The runner **must abort** if the deduplicated count is not exactly 57, or if any leg ID
appears in two strata. No cells, lanes, tasks, or external labels may be added.

## 4. The normalization rule (rule R1)

Frozen here, before execution.

```
norm(s):
  1. s = str(s)
  2. delete every character in the set  * _ ` #      (the markdown set the frozen
                                                      extractor itself strips)
  3. map U+2013 EN DASH and U+2014 EM DASH to '-'    (the frozen _CONF_RE accepts both)
  4. casefold()
  5. collapse every run of whitespace to a single ' '
  6. strip whitespace, then strip trailing '.'
```

Steps 2 and 3 exist because the frozen extractor performs the same two cleanups before
matching. Without them R1 would be *weaker* than the frozen matcher and would report
false absences on values the extractor did in fact read.

### 4.1 Candidate enumeration and presence, per component kind

The **only** thing R1 changes relative to the frozen extractor is the **search scope**:
the frozen extractor searches a ±120-character window around task-specific labels, R1
searches the whole answer text. The **equality relation is the frozen one, unchanged** —
every presence test below calls `protocol/matching.py` directly.

| kind | candidates over the full answer | `text_present` iff |
|---|---|---|
| `money_usd` | `study2_hatd_extract.parse_moneys(answer)` | `∃ v : match_money_usd(gold, v)` |
| `integer` | every `INT_RE` capture in `answer` | `∃ v : match_integer(gold, v)` |
| `categorical` with `date` in the component id | every `_DATE_RE` capture in `answer` | `∃ v : match_categorical(gold, v)` |
| `entity`, other `categorical` | not tokenizable | `norm(gold) != "" and norm(gold) in norm(answer)` |
| `state` | per key, by that key's own kind | every key in `key_kinds` is present under its own rule |

For `entity` and `categorical` the test is normalized substring containment. This is
deliberately **weaker** than `match_categorical`, which demands full string equality.
That is correct for a recall ceiling: if the gold string is not even a substring of the
normalized answer, no label strategy could have recovered it.

If `gold is None` the component is **vacuous** — gold was not resolvable from that leg's
guest file. Vacuous components are reported separately and are excluded from every
presence tally. They are never counted as absences. This is the §2 rule of
`P3_0_SPEC.md` carried forward: unkeyed and unresolvable are vacuous, never mismatches.

### 4.2 Component scope and `state` key vacuity

`out/study2_gold_path_lock.json` keys 31 components over 13 tasks with roles
`determining` 28 and `held` 3, and **no** `distractor`. Every keyed component therefore
carries positive weight, so this audit covers exactly the component set that `Y` and STS
are defined over, with no weight filter needed and none applied.

Kinds present: `money_usd` 16, `entity` 7, `integer` 6, `state` 1, `categorical` 1. The
single `categorical` is the date component `retrieval-f009.nyc_checkin_date`, which the
frozen `extract_component` routes to the date branch, so the "other `categorical`" row of
the §4.1 table is empty in practice and is retained only for completeness.

For the single `state` component, vacuity is evaluated per key: a key whose gold is
`None` is vacuous, the component is `VACUOUS_GOLD` if *every* key is vacuous, and
otherwise `text_present` requires every **non-vacuous** key to be present under its own
kind's rule. Per-key detail is reported.

## 5. Categories reported per leg × component

Exactly one applies.

| category | `extractor_match` | `text_present` | meaning |
|---|---|---|---|
| `MATCH` | yes | yes | consistent; the extractor found it |
| `RECALL_MISS` | no | yes | **the diagnostic cell** — value is in the text, extractor did not reach it |
| `ABSENT` | no | no | consistent; the value is not in the final answer |
| `VACUOUS_GOLD` | — | — | `gold is None`; excluded from tallies |
| `ANOMALY` | yes | no | see §5.1 |

Each row also reports: gold value, `norm(gold)`, kind, `n_candidates` (how many
candidate values of that kind the full answer contains), the frozen `reported` value,
`extractor_match`, `text_present`, and `stratum`.

### 5.1 `ANOMALY` is a self-check on R1, not a finding

`ANOMALY` means the frozen extractor matched a value that R1 says is not in the text.
That is a statement about R1, never about a leg. There are exactly two mechanisms, both
identified a priori by reading the frozen code rather than from any result, and each has
its consequence fixed here.

**(a) Window-boundary lookbehind, for `money_usd` and `integer`.** The frozen
`extract_money` and `extract_int` parse a *slice* of the answer, and `MONEY_RE` /
`INT_RE` carry negative lookbehinds — `(?<![A-Z])` and `(?<![\d.,])` — whose context is
destroyed at a slice boundary. The frozen candidate set over a window is therefore not
a subset of R1's candidate set over the full answer. Verified concretely on
`"Confirmation: SM-88431 is booked."`: the full answer yields the single money candidate
`+88431`, because at the `-` the lookbehind sees `M` and the match restarts at `8`, while
a window beginning at `-88431` yields `-88431`. A gold value of `-88431` would then be
matched by the frozen extractor and reported absent by R1. This sign and boundary
divergence is the only way a numeric `ANOMALY` can arise.

Consequence: such rows are reported individually and **excluded from both the numerator
and the denominator** of the recall-miss quantity, where the §6.3 denominator
`RECALL_MISS + ABSENT` already places them. The kind is **not** voided, because the
mechanism is understood in advance and it cannot change the classification of any other
row. R1 is not relaxed to absorb them: dropping the lookbehinds would manufacture false
*presence* across every numeric component, which is the wrong direction for a recall
ceiling.

**(b) Constructed substring, for `entity` and `categorical`.** The frozen
`extract_entity` builds `reported` by splitting a line on `:`, stripping markdown, and
splitting on `(` or `[`. If R1's normalized containment nevertheless fails on such a
row, R1 is weaker than the frozen matcher in a way not anticipated by §4, which is a
genuine rule defect.

Consequence: **if `ANOMALY` count > 0 for `entity` or `categorical`, R1 is declared
inadequate for that kind and that kind's recall numbers are void**, reported as a rule
failure with the offending rows listed. It is not reported as a result, and R1 is not
patched after seeing which rows tripped it.

## 6. Reporting, fixed in advance

1. The 57×component table, every row, no filtering.
2. Category counts, overall and split by stratum, by component kind, and by task.
3. The primary quantity: **recall-miss share of non-matches**,
   `RECALL_MISS / (RECALL_MISS + ABSENT)`, with a Wilson 95% interval, reported
   separately for `A` and for the 21 legs outside `A`.
4. The distribution of `n_candidates`, and the category counts cross-tabulated against
   it, so the coincidence hazard of §2 is visible rather than argued about.
5. The 7 `S = 100` zero-match `gate0` legs and Claude's `counterfactual-f013` pair,
   itemized, because they are where the two explanations of §0 diverge most sharply.

No threshold is set. Consistent with the standing rule of this project, no `3/5`, no
`50%`, no cutoff is declared in advance and none may be invented afterwards to produce
a verdict.

## 7. Pre-registered reading, both directions

Both outcomes are reportable and **neither is a win**. This is written down so that the
result cannot be rescued in either direction after the fact.

* **`ABSENT` dominates.** The extractor is behaving correctly and the gold values really
  are not in the answers. Then Paper 2's `Y = 0`, its STS floor, and the 7 high-`S`
  zero-match legs are genuine, the phenomenon is Type B at scale, and it corroborates
  Paper 1 by an independent automated route. Gate 0's *uninformative* verdict stands as
  a true negative: the discarded trajectories contain no recoverable final-answer
  evidence.
* **`RECALL_MISS` dominates.** The frozen extractor has an identification problem. Then
  Paper 2's `Y = 0` and STS floor are substantially instrument artifacts — which Paper 2
  already flags as unvalidated against any positive instance, so this contradicts no
  published claim — Gate 0's *uninformative* verdict is explained by instrument
  insensitivity rather than by absence of signal, and Paper 3's first contribution must
  be identification, not a new trajectory metric.
* **Mixed.** Report per kind and per task. No single verdict. In particular a split that
  runs one way for `entity` and the other for `money_usd` is a plausible and acceptable
  outcome, and must be reported as such rather than collapsed into an average.

A `RECALL_MISS`-dominant result does **not** revive the completion-dissociation
hypothesis of Gate 0. That hypothesis was tested and was not supported. It would only
mean the test lacked the sensitivity to detect it, which requires a new instrument and a
new pre-registration, not a reinterpretation of 0.2.

## 8. Order of work and hard stops

1. Freeze this document. Commit before running.
2. Run `scripts/p3_0_recall_audit.py` **once**.
3. Stop.

Do **not** run Gate 1 / `p3_0_item_timing.py` (0.4). Do not modify the frozen extractor,
`matching.py`, the gold lock, the archive, or any Study 2 trajectory. Do not commit on
the host. Do not add cells, lanes, or external labels. No model runs. No optional
stopping: the audit is run once on all 57 legs, and its output is reported whole.
