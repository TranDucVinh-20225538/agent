# P4-B — Independent CUA validation corpus (design memo)

**Status: Phase 1 construction PASS. Phase 2 BLOCKED. $0. No agents.**
Authored 2026-09-12.

This file is a **new workstream**. It does not amend `P4_PREREG.md` §2, does
not un-freeze the instrument, does not lower `N_A`, and does not reopen the
MyPCBench leftover 11.

**Record that stays:** MyPCBench Phase-2 gold-lock **FAIL**, n_locked = 3 <
`N_A` = 11, commit `58549515266a69e44c7e3262b34442c57dd920a6`, spec hash
`138a0b43582fa24c58f25b571ce6bee67aec6b71e965bc1af2c0327f756db854`. That
failure is a protocol-level finding about the **old validation target**, not
about the instrument. It is not repaired here.

**Frozen instrument (do not edit):**
- commit `c35e828db89a9c7eb9d479601215a29221f5d744`
- `p4_instrument.py` sha256
  `c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59`
- Q PASS 6/6; V* PASS 20/20, seal
  `26df37a1fe10b05ebb674fea28cf2ac03dcc7772227df9de902f4aed08cb4189`

P1–P3 remain frozen. Q, V*, R, the 184-task file, the leftover 11 (including
the three filename locks), Study 2 rows, C7 four, P3 16/28, Paper 1 replay,
and P3-1 S1–S10 are **forbidden as P4-B validation data**. R-AGG / R-SCOPE /
R-CHAN / ALL / `R` / FROZEN are not the method.

This memo does not spend the closed Phase-2 $400 on MyPCBench. Any later
agent spend is a **new licence**, capped at **$400** total, and opens only
after the gates below.

```
PHASE 0  design memo                 $0   ← this file
PHASE 1  corpus construction         $0
PHASE 2  corpus qualification/seal   $0
PHASE 3  Flash pilot                 API only if Phase 2 PASS
PHASE 4  Flash + GPT main            API only if Phase 3 PASS
PHASE 5  Claude external-validity    API only if Phase 4 complete
                                       and a remainder covers the
                                       pre-specified Claude legs
```

---

## 0. Why a new corpus

The leftover 11 MyPCBench tasks were independent under §4.1 and still failed
gold-lock: eight `llm_judge` specifications have success semantics without a
unique determining value; three lock only as unique `.txt` basenames. That is
not an instrument miss. It is a **corpus miss**: the benchmark was not built
so that an observation-grounded correspondence instrument can independently
lock gold before any last-text exists.

P4-B exists to supply **measurement targets** the old pool did not. It is not
a salvage of the 3/11, not a hunt through another public suite until 20 tasks
lock, and not a second Q/V slate of authored last-responses.

Instrument calibration (Q/V*) stays in force. Transfer to natural CUA
last-text is what this corpus is for.

---

## 1. Construct and determining component

**Construct.** Unchanged from `P4_PREREG.md` §1: observation-grounded
correspondence on a triple `(episode, gold, channel)`. P4-B does not
redefine reliability, does not score process, guest mutation, rubric `S`,
or STS, and does not treat agreement with `S` as validity.

**Determining component.** Every P4-B cluster has **exactly one**:

| Field | Rule |
|---|---|
| `component_id` | stable name; not a `task_id` branch in the instrument |
| `kind` | `money_usd` \| `integer` \| `entity` \| `categorical` |
| `gold` | unique non-null value of that kind, well-formed under frozen V3 |
| `anchors` | ≥1 phrase, each ≥2 whitespace tokens, **literal substring** of that cluster’s instruction; gold is not a substring of any anchor |

No second scored component. Episode status equals that component’s status
under frozen V5/V6: HIT iff HIT; MISS if any MISS; else ABSTAIN. Unique-or-
abstain identification is unchanged. ABSTAIN is not converted to HIT or MISS.

**Task truth vs observation vs measurement.** Three objects, never collapsed:

1. **Task truth** — sealed environment + instruction + locked
   `(kind, gold, anchors)`. Exists before any agent run.
2. **Agent observation** — last assistant text of one protocol run. Not used
   to author or edit gold.
3. **Measurement outcome** — `{HIT, MISS, ABSTAIN}` + cause from the frozen
   instrument on (2) against (1).

An LLM judge, a rubric `S`, a human “looks right,” and a trajectory dump are
not gold.

---

## 2. Task-cluster unit and target `N`

**Unit.** One **task-cluster**: one instruction, one sealed environment
slice, one locked determining component, later zero or more model legs.
`N` counts clusters. `N` is never legs, never model–task pairs, never
components, never transforms, never observations.

Two Flash and GPT legs on one gold are **one** cluster. Claude does not
increase `N`.

**Target `N`, locked before any P4-B task is authored:**

```
N_B = 20
```

Kind quota on the 20, locked now:

| kind | n |
|---|---|
| `money_usd` | 8 |
| `integer` | 6 |
| `entity` | 3 |
| `categorical` | 3 |

IDs, pre-assigned: `B01`–`B20` scored; `RB01`–`RB10` construction reserve
(same-kind replacement only, in ID order, **before** Phase-2 seal). After
seal, unused reserve is discarded. Do not add `B21`. Do not promote a
forbidden ID. Do not drop a scored ID for usefulness.

If after reserve the sealed set is not exactly 20 with the kind quota,
**construction FAIL**. Stop. `$0` API. Do not lower `N_B`.

`N_B` is not `N_V`, not `n_Q`, not `N_A`. They are not pooled.

---

## 3. Task families

Families are **P4-B evidence jobs**, not MyPCBench prefixes. Quota locked
now (4 each = 20). Kind quota and family quota must both hold.

| Family | What the instruction asks | What must be unique in the sealed world |
|---|---|---|
| **Locate** | Report one typed field of a uniquely identified record | that field |
| **Compute** | Report one derived `money_usd` or `integer` from named records under one formula | the derived value |
| **Reconcile** | Two sources disagree; report the source the instruction names as live | the live value |
| **Filter** | Many records; a predicate in the instruction selects exactly one; report its typed field | that field |
| **Tally** | Count records matching a predicate stated in the instruction | that integer |

A cluster that needs “any of several answers,” “no particular answer,” or
an LLM judge to decide success is **not a family member**. It is an
exclusion.

**Entity cap.** At most **one** of the three `entity` clusters may have gold
that is a filename or path. The other entity golds must be ordinary names
or labels in records (vendor, room, title), not `*.txt` retrieval clones of
`retrieval-f020`.

**Compute / Tally** may only use `money_usd` or `integer`. **Categorical**
gold is a closed label set stated in the instruction (as Q06 does) **or**
a single live label in the world that is not listed as gold in the
instruction. Gold itself is not a literal substring of the instruction
(§6 T1).

---

## 4. Realistic CUA interaction requirements

P4-B environments are **authored desktop fixtures**, not rows from
MyPCBench `all_tasks_with_grading.json` and not Q/V one-line ledgers.

Each cluster’s sealed world is a filesystem snapshot containing at least
two of: mail (`.eml` / mbox), tabular finance (`.csv` / `.ods`), notes
(`.txt`), calendar (`.ics`), a local HTML receipt. The agent, when Phase 3
opens, is a computer-use agent that may open those objects through a
desktop. Screenshots, tool traces, and guest dumps are **not** the scored
channel.

**Anti-toy world checks** (mechanical, Phase 1; fail → void that ID):

| ID | Test |
|---|---|
| T1 | Gold is not a literal substring of the instruction |
| T2 | No file basename in `{answer, gold, result, label, p4}` |
| T3 | World contains ≥ 3 other values of the same kind as gold |
| T4 | No `observations.*` / last-response field exists on the cluster |
| T5 | Gold is not taken from an LLM-judge rubric |
| T6 | Cluster ID is not in any §8 exclusion set |
| T7 | Instruction uses no Q/V/R cover token as a whole word |
| T8 | Gold-path names ≥ 2 distinct environment objects (e.g. a mailbox **and** a spreadsheet) |

T8 is a property of the **locator**, not a process score on the agent. P4
still does not score the path.

A cluster that is “open `n.txt` and read the only number” fails T3 and T8
and is voided, not rescued by a nicer instruction.

---

## 5. Independent gold and anchor authorship

**Order, fail-closed:**

1. Author the world as ordinary records. The world contains **no** `gold`
   field.
2. Author the instruction, `component_id`, `kind`, anchors, and a
   **world locator** `L` (a tiny, cluster-local query over the world:
   which cell is determining). `L` is measurer state. The agent never
   sees `L`.
3. Run a **frozen locker** with no `if task_id == …` and no instrument
   edit: `L(world)` must return exactly one value; that value must parse
   as `kind` under frozen V3; that value becomes `gold`.
4. Construction-audit anchors against the instruction (§2 table).
5. Hash. Only then may any observation exist.

If `L(world)` is empty, non-unique, or the wrong kind, the ID is void.
Replace from reserve or fail `N_B`. Do not hand-set gold to “make it lock.”

**Anchors** are authored from the instruction only, before any last-text.
They are locator phrases the instrument already knows how to use. They are
not a hidden per-task table inside `p4_instrument.py`.

**Dialect split.** Corpus authorship is not Q/V restyled.

- Q/V/R word-lists stay forbidden as whole words in P4-B instructions and
  worlds (`rebate`, `ledger`, `kiln`, `quartz`, `harbour`, `vendor`,
  `invoice`, `filament`, `linden`, `pewter`, `oxbow`, `thresh`, `navy`,
  `ivory`, `olive`, and the V/R lists).
- P4-B uses a new word-list `wordlists_b.txt`, hashed with the slate,
  pairwise disjoint from Q/V/R.
- World instantiation is a generator from `params_b.json` with **no
  per-id branch**. Hand-editing a generated world after first generation
  voids that ID.
- The instrument author does not write P4-B instructions. The corpus
  generator does not import or copy `p4_instrument.py` parsers into
  per-task branches. Correspondence checks may **call** the frozen module
  as a library to test that gold self-matches; they may not patch it.

Forbidden gold strings (P1–P3 / construction audit) remain forbidden in
P4-B worlds: `4820.50`, `1205.00`, `700.00`, `318.75`, `2450.00`, `77.10`,
`6100.00`, `3910.00`, `990.00`, `512.00`, `42.12`, `3570.0`, `3570`, and
substrings `jamaica`, `sandals`, `gme`, `oddsmarket`, `batbucks`,
`nyc_flight`, `settlement_total`.

---

## 6. Observation channel

Unchanged from frozen §2 V1.

- Scored channel = last assistant text.
- Strip well-formed `<function…></function>` / `<tool…></tool>` (and the
  self-close forms). Unterminated opener → ABSTAIN `channel_indeterminate`.
  Do not delete-to-end.
- Locate on newline-terminated lines containing an anchor hit.
- Kind parsers: frozen `money_usd` / `integer` / `entity` / `categorical`.
- HIT only on unique committed match under V3. MISS = committed wrong.
  ABSTAIN is valid.

Harness logs, screenshots, `L`, gold, and the world dump are not in the
channel. The instrument still refuses `construction/sealed/v`.

---

## 7. Independence from old objects

Forbidden as any P4-B validation object, including “same instruction, new
answers” and “new last-text on an old ID”:

* MyPCBench 184-task file and every ID in it, including leftover
  `contradiction-f013` … `retrieval-f035` and the three locked filenames;
* Study 2: 134 rows, 57/171 legs, 25-task `paper2_cell_order.json`;
* C7 four; P3 slate of 28 and 16 survivors; Paper 1 ten; P3-1 S1–S10;
* `preference_inference-*`; `contradiction-f024`;
* Q01–Q06, V01–V20, R01–R10, their params, word-lists as cover tokens,
  and their observations;
* any guest probe or trajectory produced for P1–P3.

P1–P3 numbers may be cited only as **design requirements** (failure modes
in §9). They are not re-estimated and not mixed into `N_B`.

Do not shop OSWorld, WebArena, or any other public CUA suite until a task
locks. That is the same selection bias this memo exists to avoid. If a
later amendment names another suite, it must do so **before** any of that
suite’s traces are read, and it is a different file.

---

## 8. Inclusion and exclusion (mechanical)

A candidate **enters** the Phase-1 slate iff all of:

1. ID in `B01`–`B20` or an unused reserve ID of the same kind;
2. family in {Locate, Compute, Reconcile, Filter, Tally} and family quota
   not exceeded;
3. `kind` allowed and kind quota not exceeded;
4. `L(world)` unique and V3-self-matching;
5. T1–T8 pass;
6. every anchor is a ≥2-token **literal** substring of that instruction;
7. gold is not a substring of any anchor;
8. no exclusion ID, no forbidden gold, no Q/V/R cover token;
9. cluster JSON has no observation / last-text / expected-status field.

A candidate is **excluded** with a recorded reason if any check fails.
Reasons are logged. IDs are not silently dropped for usefulness. If
exclusions leave `n < N_B` after reserve, Phase 1 **FAIL**, `$0`.

---

## 9. Positive / negative / distractor / contradiction cases

These are **evidence structures** for the frozen instrument’s known
failure modes. They are not extra families and not extra `N`.

**In the sealed world (before any run):**

| Structure | Requirement | P1–P3 mode |
|---|---|---|
| Same-kind distractors | T3: ≥3 other values of gold’s kind | distractors; aggregation pressure |
| Reconcile split | Reconcile family: a stale source and a live source, gold = live | contradiction; stale evidence |
| Multi-record compute | Compute family: formula uses ≥2 records | aggregation (gold is one derived value, not a vote) |

**On the natural last-text `τ`, after Phase 3/4 runs, mechanical
transforms hashed before `τ` is read** (templates frozen in Phase 2; no
per-id branch):

| Transform | Operation on `τ` | Required status |
|---|---|---|
| C3-del | delete gold span; keep anchors | ABSTAIN (`absent` or `no_anchor`), never HIT |
| C4-stale | gold appears only inside deleted markup or an unanchored line; committed context is wrong or empty | not HIT |
| C5-irr | C-positive text plus a same-kind distractor on an unanchored line | same status and committed value as unscored-positive geometry would demand; for transfer, **invariance** of status/value vs `τ` when `τ` already HIT |
| C6-stab | two C5 variants, anchored line identical | same status and committed value |
| Chan | unterminated `<function` or `<tool` opener | ABSTAIN `channel_indeterminate` |

The **natural** `τ` is never authored. Transforms are applied to whatever
last-text the agent produced. If `τ` has no gold span, C3-del is a no-op
and that transform is **NOT EVALUABLE** for C3, not a licence to rewrite
`τ`.

**Primary transfer properties** (computed only in Phase 4 on natural `τ`,
instrument freeze unchanged):

* **E1 False HIT.** Among `{τ}` with gold absent from the V1-cleaned
  channel, HIT count = 0. Any such HIT → P4-B FAIL.
* **E2 Invariance.** Status and committed value on `τ` equal those on the
  C5 and C6 transforms of that `τ`. Any change → FAIL.
* **E3 Natural C1.** Eligible if gold lies in an anchored line of `τ` and
  no other same-kind candidate lies in located lines. If eligible count
  `< 5`, **NOT EVALUABLE** (not FAIL, not PASS). If ≥ 5, all must be HIT
  or FAIL.
* **E4 Natural C2.** Eligible if a unique non-gold same-kind value lies in
  an anchored line and gold is absent from the cleaned channel. Floor 5;
  else NOT EVALUABLE.

E3/E4 floors are locked **now**, before any `τ`. Do not hunt eligible
clusters. Do not rank Flash against GPT. Per-model tables are descriptive.

Missing evidence (Study 1 Type B), fail-closed unique-or-abstain (Study 3
aggregation), stale/markup coincidence (C4), and channel artifacts (P3-1)
are tested by E1–E4 plus the transforms. They are not tested by reusing
P1–P3 traces.

---

## 10. Natural-agent execution protocol

**Not opened in Phase 0–2.**

When a later phase opens:

1. Agent receives only the instruction and the mounted sealed world.
2. Agent does not receive gold, `L`, anchors, kind, family, or this memo.
3. One uninjected leg per named model per cluster. `max_steps = 40`.
   Completion (`DONE`) is not required. Channel = last assistant text at
   `DONE` or `max_steps`.
4. Models named **now**, before any run: **Flash** then **GPT** for
   Phases 3–4. Claude is Phase 5 only (§15).
5. Do not add, remove, replace, or reorder `B01`–`B20` after seeing `τ`.
6. Do not modify the instrument. Do not modify gold. Do not enlarge
   markup strip lists after seeing `τ`. Runtime paraphrases become
   `channel_indeterminate` or uncleaned distractors.
7. Spend is recorded every 5 legs. If projected completion of the
   **declared** `N_B` × models in the open phase exceeds the remaining
   cap, **stop** and report incomplete. Incomplete is not a lowered `N_B`.

---

## 11. Primary estimands

Instrument hold-rate `r_p` on Q/V* is **already closed**. It is not
recomputed as a P4-B estimand.

On P4-B, after Phase 4 (or earlier stop):

| ID | Estimand | Gate |
|---|---|---|
| E1 | False HIT count among gold-absent `τ` | PASS iff 0 |
| E2 | Invariance of status and committed value under C5/C6 transforms | PASS iff no cluster changes |
| E3 | HIT rate among eligible natural-C1 `τ` | PASS iff eligible ≥ 5 and all HIT; else NOT EVALUABLE or FAIL |
| E4 | MISS rate among eligible natural-C2 `τ` | PASS iff eligible ≥ 5 and all MISS; else NOT EVALUABLE or FAIL |

Diagnostics, not gates: sensitivity `HIT/(HIT+MISS)` among non-ABSTAIN
natural `τ`; abstention `ABSTAIN/all`. No threshold may convert FAIL or
NOT EVALUABLE into “mostly holds.” No model ranking. No pooling with `N_V`.

**P4-B PASS** (constructive transfer) iff E1 and E2 PASS and E3 is PASS
(not merely NOT EVALUABLE). E4 FAIL fails P4-B. E4 NOT EVALUABLE does not
fail P4-B by itself; it is reported.

**P4-B null:** construction FAIL; qualification FAIL; pilot observability
FAIL; E1/E2 FAIL; E3 FAIL; spend cap hit before `N_B` complete. Report as
null. Do not repair.

---

## 12. Qualification criteria (Phase 2, still $0)

Object: the sealed `B01`–`B20` worlds + gold specs. Not Q, not V*, not
agents.

Phase 2 **PASS** iff all of:

1. `n = 20` and kind quota and family quota hold;
2. locker replay on each sealed world reproduces the sealed gold;
3. T1–T8 and anchor/correspondence checks PASS on all 20;
4. no observation field exists on any cluster;
5. independence exclusions hold;
6. transform templates for C3–C6/Chan are hashed and have no per-id
   branch;
7. combined corpus hash and gold-spec hash recorded;
8. `p4_instrument.py` hash still
   `c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59`.

Phase 2 does **not** score C1–C6 authored last-responses (that was Q/V*).
It does not open Flash.

If Phase 2 FAIL: stop. `$0` API. Do not retune §2. Do not rewrite gold
after a failed locker replay except via reserve **before** the failed
seal attempt; a failed **sealed** pass is terminal for that seal.

On PASS, freeze together: corpus, gold, anchors, instrument hash, `N_B`,
estimands, pass/fail criteria, transform templates.

---

## 13. Kill criteria

**Stop at $0 (no API):**

* Phase 1 construction FAIL (`n < N_B` after reserve, quota fail,
  independence fail, toy-test fail);
* Phase 2 qualification FAIL;
* any edit to `p4_instrument.py` or to sealed gold after Phase 2 PASS;
* attempt to reopen MyPCBench leftover / P1–P3 / Q / V* as P4-B data.

**Stop API spend (do not complete the phase):**

* Phase 3 observability FAIL (§14);
* cumulative P4-B API spend reaches **$400**;
* projected remaining Phase-4 legs to finish declared `N_B` × 2 models
  exceed the remainder — stop, report incomplete, do not lower `N_B`;
* E1 or E2 FAIL on the scored prefix — do not spend the rest to “average
  it out.”

**Do not:** lower `N_B`; fold in 3/11; shop another benchmark; convert
ABSTAIN; ship R-AGG/R-SCOPE/R-CHAN/ALL; rank models; change §2 because
natural ABSTAIN looks high.

If P4-B dies or is null, Q/V* and the 3/11 finding remain the publishable
P4 record. P1–P3 remain publishable.

---

## 14. Phase 3 — cheap Flash pilot (API only after Phase 2 PASS)

**Pre-specified. Not opened now.**

* Object: `B01`, `B02`, `B03` in ID order. One Flash leg each.
  `max_steps = 40`. Gold and instrument frozen.
* Purpose: are natural last-texts **technically obtainable** and
  scorable under V1 (a string exists; the frozen scorer returns a
  well-formed `{status, cause, committed}`)?
* **Not** a licence to estimate E1–E4. **Not** a licence to drop IDs,
  retune anchors, or patch the instrument.
* Pilot outcomes do not edit gold.

**Pilot gate PASS** iff ≥ 2 of the 3 legs yield a last-text that the
frozen instrument scores without harness exception.

**Pilot FAIL / kill** iff < 2 scorable last-texts, or the failure is an
already-named kill (channel definition abandoned, gold edited, instrument
edited, MyPCBench IDs substituted). Stop. Do not open Phase 4.

Report actual USD and the three `{status, cause}` only as diagnostics.

Expected cost: 3 Flash CUA legs, on the order of **$3–$15**. Hard cap for
Phase 3: **$30**. If Flash cannot be run inside $30, Phase 3 is
**BLOCKED** (spend), not a lowered `N_B`.

---

## 15. Phase 4 — main validation; Phase 5 — Claude

**Phase 4** opens only on Phase 3 PASS.

* Models: Flash and GPT, one uninjected leg each, all `B01`–`B20` in ID
  order. 40 scored episodes. `N_B` remains 20.
* Compute only §11 estimands. No ranking. No gold/instrument edits.
* Expected cost: Flash 20 × ~$1–$3; GPT 20 × ~$6–$15; central estimate
  **~$280**, envelope **$160–$400**. If a pre-flight projection (same
  prices as the pilot’s actual Flash burn, GPT quoted at ≤ 5× Flash per
  leg unless a listed public price is lower) exceeds remaining budget,
  **do not start Phase 4**. Incomplete-not-lowered-N applies if spend
  hits $400 mid-run.

**Phase 5 (optional).** Claude is used only for this hypothesis, copied
in kind from the old §9 E-ext and **not** to grow `N`:

> On P4-B last-text, does E1 still hold (false HIT = 0) for a
> markup-heavy, often non-terminating model family?

Pre-specified object: `B01`, `B02`, `B03` only, one Claude leg each, and
only if Phase 4 is complete and remaining budget covers 3 Claude legs
without crossing $400. Not a cluster for `N_B`. Not a ranking slot. If
the remainder cannot cover 3 legs, Phase 5 is **NOT EVALUABLE**.

---

## 16. Budget and run count (declared before authorship)

| Phase | Runs | API |
|---|---|---|
| 0 Design | 0 | $0 |
| 1 Construction | 0 | $0 |
| 2 Qualification / seal | 0 | $0 |
| 3 Flash pilot | 3 Flash | cap $30; expect $3–$15 |
| 4 Main | 20 Flash + 20 GPT | remainder; expect ~$280; hard total cap $400 |
| 5 Claude E-ext | 0 or 3 | only from remainder after Phase 4 |

**Minimum agent runs if every gate PASS and Phase 5 NOT EVALUABLE:** 43
(3 + 40). **Minimum to claim E1–E4 on `N_B`:** 40 Phase-4 legs (pilot is
observability, not confirmatory `N`). **Maximum USD:** 400. The closed
MyPCBench Phase-2 spend stays $0; this cap is not a reason to reopen it.

---

## 17. What this memo does not do

* Does not probe guests or run agents.
* Does not edit `p4_instrument.py`, Q, V*, or `P4_PREREG.md` §2.
* Phase 1 authored `B01`–`B20` worlds and locked gold from `L`; it did not
  author last-responses.
* Does not treat the three MyPCBench filename locks as a starter kit.

---

## 18. Phase 0 gate

Phase 0 is **PASS** if and only if this file exists, declares `N_B = 20`
before authorship, names families, quotas, inclusion/exclusion, estimands,
kill criteria, and the $400 cap, and orders later phases behind
construction and qualification.

**Phase 1 construction, 2026-09-12: PASS.** `n = 20` with locked family and
kind quotas. Gold locked from `L` on authored worlds. No observations. No
agents. `$0`. Record: `construction/out/p4b_phase1_construction.md`.

Phase 2 qualification remains **BLOCKED** until authorized.

```yaml
phase: 1
workstream: P4-B
status: PASS
next: PHASE_2_QUALIFICATION
next_status: BLOCKED
N_B: 20
n_pass: 20
api_spend_usd: 0
instrument_modified: false
my_pcbench_phase2: FAIL_RECORDED
agents_run: 0
```
