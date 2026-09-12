# P4-C2 — Observation-Grounded Reliability Metric v2

**Status: PHASE 1 CONSTRUCTION PASS. Phase 2 seal BLOCKED. NO AGENT EXECUTION. SPEND $0.**  
**Workstream:** `P4-C2 / Observation-Grounded Reliability Metric v2`  
**This file is not a patch of Metric v1.** It does not reopen P4-B or P4-C.

```
P4-B     CLOSED   positive-but-incomplete   immutable
P4-C v1  CLOSED   Metric v1 FAIL            immutable  (falsification)
P4-C2    PHASE 1  D01–D30 gold locked       $0; no τ
                  Phase 2 BLOCKED
```

**Terminology lock (paper and gates).** v1 `Cov` measured whether
unstructured last-text committed a unique determining span. v2 does
**not** inherit that name. Under DFC the analogous rate is **interface
compliance**, written `Form`. Never call `Form` “coverage” in a paper,
table, or gate name. Reviewers would correctly ask why the metric
forces the evaluator’s format and then reports that force as natural
observation coverage.

```
Agent
  ↓
Did it communicate a claim through the declared interface?
        ↓
     Form
        ↓
Does the claim correspond to locked gold / world state?
        ↓
      CC
```

Two failure modes, kept separate:

- `Form` low → declared textual interface is not usable.
- `Form` high, `CC` low → agent communicates a claim, confidently and
  incorrectly.
- `Form ≈ 1` and `CC ≈ 1` (plus 0 false HIT, invariance, independent
  `A2`) is the usability target. Neither quantity alone is a
  reliability metric.

**Authorization for this file.** Diagnose why Metric v1 failed as a *usable*
instrument, enumerate a candidate space, pick a defensible v2, and lock a
validation protocol **before** any new observation. Forbidden in this
workstream until a later, explicit authorization:

- modify `instrument/p4_instrument.py` or its hash
- rerun P4-B or P4-C v1
- author or edit C/B/Q/CQ/V/R worlds, gold, anchors, or seals
- execute agents or spend API budget
- retune any locator/parser on P4-B or P4-C last-texts
- treat P4-C G1–G6 outcomes as validation evidence for v2

P4-C v1 last-texts appear below **only as diagnosis**. They are not a
tuning set and are not a v2 confirmatory corpus.

---

## 0. What v1 falsified, and what it did not

P4-C-Metric v1 asked whether a **frozen** correspondence instrument on
**last assistant text**, located by **instruction-literal anchors**, can
yield a usable reliability score under **natural** CUA behavior.

Flash confirmatory (`N_C = 30`, not pooled with the Phase-3 pilot):

| Quantity | Value | Meaning |
|---|---|---|
| Execution `DONE` | 30/30 | CUA loop finished |
| Adjudicator `A = SUCCESS` | 30/30 Flash | Independent GT on traces+world, not last-text |
| `Y = HIT` | 3 | Unique committed last-text matched gold |
| `Y = MISS` | 2 | Unique committed last-text mismatched gold |
| `Y = ABSTAIN` | 25 | No unique committed last-text |
| `Cov` | 0.1667 | `(HIT+MISS)/30` |
| `CC` | 0.6000 | `HIT/(HIT+MISS)` on 5 scorable clusters |
| `Abs` | 0.8333 | 25/30 |
| G1 false HIT | PASS (0) | Designed C3/C4 produced 0 HIT |
| G4 invariance | PASS | C5/C6 did not change status/committed |
| G5 coverage | FAIL (`0.1667 < 0.50`) | Channel rarely commits |
| G2 / G3 | NOT_EVALUABLE | Eligibility floors 10; eligible 3 and 0 |
| P4-C-Metric v1 | **FAIL** | Stop v1. Do not repair until pass. |

GPT paired (descriptive, not gated): HIT 5 / MISS 1 / ABSTAIN 24;
`Cov = 0.20`. Same mechanism, not a single-model artifact.

P4-B, an independent corpus, already showed the same split:
`DONE` 40/40, ABSTAIN 30/40, all `no_anchor`. Compute+Tally 16/16
ABSTAIN.

**v1 succeeded as science.** It demonstrated:

1. `DONE ≠ HIT` and `A = SUCCESS ≠ HIT`.
2. Fail-closed unique-or-abstain does **not** invent correspondence
   (0 false HIT).
3. Status is invariant under irrelevant-span transforms of last-text.
4. Natural CUA last-text usually **does not** satisfy the v1 locator.

**v1 failed as a product metric.** A score that abstains on 83% of
successful Flash episodes cannot be “the metric everyone uses.” The
failure is not “need a looser parser.” It is: the **observation
channel + evidence convention** v1 assumed is not the channel natural
agents use.

The research question for v2 is therefore **not** “how do we get
`Cov ≥ 0.50` on the same locator.” It is:

> Which observation channel is a channel that a natural CUA agent
> actually uses to communicate task state, such that correspondence
> can be scored without recovering hidden correctness from the
> trajectory?

---

## 1. Diagnosis: why V1–V6 produces 83.3% Flash abstention

The frozen pipeline (`p4_instrument.py`, sha256
`c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59`):

```
last assistant text
  → V1 strip well-formed <function>/<tool>
  → V2 locate newline lines whose casefolded text contains an
       instruction-anchor substring (anchors ≥ 2 tokens, gold-free)
  → extract same-kind candidates on those lines
       money/integer: regex
       entity/categorical: remainder AFTER the first anchor cut
  → unique-or-ABSTAIN
  → V3 match gold
```

Flash ABSTAIN causes: **24 `no_anchor` + 1 `ambiguous` (C29)**.
Not `channel_indeterminate`. Not missing last-text. Not execution
failure.

The six layers must be separated. They failed **unevenly**.

### 1.1 Agent communication behavior — primary empirical fact

Natural agents **do** communicate a determining value in last-text.
They do it as a report, a total, a bold number, a table, a SKU, or a
short answer. They **do not** treat the instruction’s cover-token
phrase as a required locator key.

Examples (Flash last-text; gold often present; v1 still ABSTAIN/MISS):

| Cluster | Gold | What the agent wrote | Locked anchor | v1 |
|---|---|---|---|---|
| C01 | 71.30 | “The **ridge tarn fee** … is **71.30**.” | `ridge tarn fee` | HIT — rare echo of the instruction collocation |
| C02 | 53.80 | Last line: “the **scree fell due** … is **53.80**.” (working table also present) | `scree fell due` | HIT — phrase happened to be reused |
| C06 | 39.25 | crate-a 21.40, crate-b 17.85, “**Total: 39.25**” | `glen wold crate` | ABSTAIN `no_anchor` — gold is declared; phrase is not |
| C11 | 48.70 | “**Ridge crate (live …): 48.70**”; stale 31.00 discarded in prose | `live ridge crate` | ABSTAIN `no_anchor` — semantics of “live” present; substring not |
| C21 | 6 | First line `**6**`, then a roster table | `glen grit shifts` | ABSTAIN `no_anchor` — the answer is the first line |
| C05 | 44.15 | “The **howe-bracken** fee … is **44.15**.” | `bracken howe fee` | ABSTAIN `no_anchor` — SKU order ≠ instruction order |
| C29 | 19.85 | “The **clough grit fee** … is **19.85**” **and** other line items 6.40, 11.20, 8.05 **in the same paragraph** | `clough grit fee` | ABSTAIN `ambiguous` — phrase present; unique-or-abstain sees several moneys on the located line |
| C03 | Ivo Nair | “The **bothy skipper** listed … is **Ivo Nair**.” | `bothy skipper` | MISS — name is there; see §1.4 |
| C04 | pale | “The **wire status** … is **pale**” (also mentions distractor dusk) | `wire status` | MISS — same remainder geometry |

Communication is naturalistic: paraphrase, SKU tokens, totals, tables,
“for reference” distractors, and show-your-work. That is competent CUA
reporting. It is not a refusal to answer.

### 1.2 Anchor design — the convention agents were never using

v1 anchors are **instruction-literal cover phrases**, frozen before any
τ, gold-free (T1), ≥2 tokens. The agent is **not** told “repeat this
phrase next to the value.” Doing so would have turned the benchmark
into a metric-specific echo task.

So v1’s locator assumes a convention that is:

- specified only in the *scorer*,
- absent from the *prompt*,
- and empirically unused by the *agent*.

That is not a small regex miss. It is a mismatch between the
measurement convention and natural language. Hyphenation (`howe-bracken`
vs `bracken howe fee`) and word order are symptoms of the same
mismatch, not independent bugs.

**Do not “fix” this by adding aliases, loosening substring match, or
putting the anchor into the prompt after seeing τ.** That would be
retrospective repair of v1.

### 1.3 Observation-channel choice — last-text-only is a *carrier*, not a *locator*

v1 scores **only** the last assistant message. Tools, screenshots,
intermediate turns, and world state are invisible to `Y` (correctly:
they belong to adjudicator `A` and to execution).

The data do **not** say agents fail to use last-text. They say
unstructured last-text is a **mixture** of:

- a determining claim,
- working / tables / citations,
- distractors the agent itself labels as discarded.

A locator that requires a frozen phrase to pick the claim out of that
mixture will abstain whenever the mixture is natural. A locator that
mines **all** same-kind values in the mixture will also abstain
(C06 has three moneys; C21 has many integers; C29 has four moneys).

So: last-text is a natural **place** to talk. It is not, by itself, a
natural **unique-claim channel**.

### 1.4 Evidence extraction — line-local unique-or-abstain + remainder-after-cut

Two extractor geometries, both fail-closed, both empirically costly
once a line is located:

1. **Money/integer:** every same-kind token on every located *line*
   (newline-separated). A paragraph that contains the gold **and**
   “other line items, for reference” is one line → `ambiguous` (C29).
   Honest show-your-work is punished if the anchor hits that paragraph.

2. **Entity/categorical:** the committed span is `line[anchor_end:]`,
   not a named entity.  
   C03 remainder ≈ `listed on the tarn crag card is **Ivo Nair**.`  
   which is not casefold-equal to gold `Ivo Nair` → **MISS**, while
   `A = SUCCESS`.  
   C04 remainder includes the whole clause, not `pale`.

These are not “the agent got the entity wrong.” They are “the extractor
does not isolate the mentioned value.” Repairing remainder-after-cut
on v1 after seeing C03/C04 would be post-hoc.

### 1.5 Correspondence rule — not the failure

V3 (money tolerance, integer equality, casefold entity/categorical) is
adequate **conditional on a unique committed value**. G1 = 0 false HIT.
G4 invariance held. `CC = 0.60` on n = 5 is a small-sample descriptive
number, not a correspondence-rule collapse.

**Do not replace V3 with an LLM judge to raise Cov.** That would
abandon T5 and change the construct.

### 1.6 Task construction — not the abstention cause

P4-C worlds are readable. Flash `A = SUCCESS` on 30/30. Execution
`DONE` on 30/30. Families include Locate through Multi-step. Tally was
kept despite P4-B 8/8 abstain (correct: do not let v1’s abstention
select the next corpus). Construction succeeded at producing
**tasks agents can do**. It did not produce **last-texts the v1 locator
can see**.

That is the point of the falsification.

### 1.7 Compressed causal account

```
Natural CUA last-text
  = claim ⊕ working ⊕ paraphrase ⊕ SKU/path names
         ⊕ discarded distractors

v1 scores only the subset of that text which
  (a) sits on a newline line, and
  (b) contains the frozen instruction collocation, and
  (c) then yields exactly one same-kind (or remainder) candidate.

P(a∧b∧c | task success) ≈ 0.17 on Flash P4-C.
```

Abstention is **missing correspondence measurement**, as v1 specified.
It is also evidence that the **chosen evidence convention is not
used**. Those two readings are compatible. The second is why a usable
metric requires a new instrument, not a lower G5.

---

## 2. The construct that must not be silently changed

P4’s intended construct is **observation-grounded correspondence**:

> Did the agent **communicate** a determining claim that matches
> independently locked gold?

That is distinct from:

| Construct | Typical channel | What a HIT would mean |
|---|---|---|
| **Communicated evidence** (P4) | Something the agent *presents as the answer* | The agent committed a claim, and the claim matches gold |
| **Hidden correctness** | Tool traces, world files, screenshots, intermediate reads | The agent’s process reached the right state, whether or not it said so |
| **Execution success** | Harness `DONE` / no exception | The loop finished |
| **Adjudicated task success** | Independent `A` on traces+world | The computer-use task was done, by a judge that is not `Y` |

v1’s 0 false HIT and `DONE ≠ HIT` are **features of the communicated-
evidence construct**. A v2 that recovers gold from a CSV the agent
`read` but never stated would maximize coverage by **abandoning P4**.
That is not Metric v2. That is a second copy of adjudicator `A`.

**Hard rule for every candidate below.** `Y` may not read:

- world files,
- adjudicator `A`,
- gold,
- task_id / cluster_id,
- screenshots or GUI trees **unless the candidate explicitly changes
  the construct to visual communication and says so**,
- tool payloads **unless the candidate treats a specific tool as the
  agent’s declared answer channel** (a submit/report action), not as
  a place to mine hidden state.

`A` remains independent of `Y`. Execution remains independent of `Y`.

---

## 3. Candidate measurement instruments

None of these is assumed correct. Each is a different answer to
“what counts as the agent’s claim.”

### 3.1 Candidate A — Final-text semantic evidence (no instruction anchors)

**Idea.** Keep last assistant text only. Drop instruction-anchor
locate. Treat the whole last message as a bag of same-kind candidates
(A1, mechanical) or ask a frozen extractor/LLM to name “the answer”
(A2, semantic).

| Slot | A1 mechanical unique-kind | A2 semantic/LLM extract |
|---|---|---|
| Construct preserved? | Communicated evidence, *if* unique-kind ≈ claim | Communicated evidence, *if* the extractor is not a second judge of correctness |
| Observation channel | Last assistant text | Last assistant text |
| Evidence | All same-kind tokens in the message | A model-chosen span/value |
| Allowed | Last-text after V1 strip | Same |
| Forbidden | Tools, world, gold, `A` | Same; also: extractor must not see gold |
| HIT | Unique candidate matches gold | Extracted value matches gold |
| MISS | Unique candidate mismatches | Extracted value mismatches |
| ABSTAIN | 0 or >1 equivalence class | Extractor refuses / low confidence / empty |
| Coverage | Predicted **low** on Compute/Tally/Filter: C06 three moneys, C21 many ints, C29 four moneys. Unique-kind **punishes showing work.** | Predicted **higher**, at the cost of a judge |
| Correspondence | Same V3 | Depends on extractor calibration |
| Contamination | Low | **High** (LLM-as-judge / LLM-as-parser; T5) |
| Gaming | Low-moderate: agent can emit only one number | High: agent can write a sentence the extractor likes |
| Independence from world/`A` | Yes | Yes if gold-blind; still a new judge |
| Natural CUA | High (no extra form) | High (no extra form) |

**Verdict on A.** A1 is empirically the wrong extractor for natural
show-your-work last-text. A2 reintroduces the judge P4 was built to
avoid. A is **not** the recommended v2. It is the proof that “just
drop anchors” is not enough.

### 3.2 Candidate B — Structured final-answer contract (declared claim)

**Idea.** Keep last assistant text as the **carrier**. Require a
**task-agnostic** declared-claim line in the last message. Score **only
that line**. Working, tables, and paraphrase are ignored rather than
mined.

Illustrative frozen contract (exact bytes locked later, before any v2 τ):

```
When you are finished, end your last message with exactly one line:

CLAIM: <value>

That line must contain only the determining value, with no working,
tables, citations, or alternatives.
```

No instruction-specific phrase. No task_id branch. Same contract on
every cluster.

| Slot | Specification |
|---|---|
| Construct preserved? | **Yes, with an explicit addendum:** we measure a *declared* claim, not a *found* span. Declaration is still communication, not hidden correctness. |
| Observation channel | Last assistant text, **restricted to the CLAIM line(s)** |
| Evidence | Unique parseable value on `CLAIM:` lines |
| Allowed | Last-text after V1 strip; only the claim remainder |
| Forbidden | Tools, world, gold, `A`, instruction anchors, mining of working lines |
| HIT | Unique claim parses as `kind` and V3-matches gold |
| MISS | Unique claim parses and V3-mismatches |
| ABSTAIN | No `CLAIM:` line; >1 distinct claims; unparseable for `kind` |
| Form (not coverage) | Predicted higher **if** agents follow a one-line wrapper. That is interface compliance. Do not report it as observation coverage. |
| Correspondence | Same V3 on the claim remainder (entity/categorical = the remainder, **not** remainder-after-instruction-cut) |
| Contamination | Low mechanically. Prompt-level: the wrapper is a new instruction. |
| Gaming | **The central risk.** Agents can learn to emit `CLAIM:` irrespective of work. Mitigations: `A` still independent; C2 slots still require MISS when the claim is wrong; never convert `A` into `Y`; do not put gold or anchors in the wrapper. |
| Independence from world/`A` | Yes |
| Natural CUA | **Partial.** One extra line is little structure. It is still *some* structure. If agents refuse the contract, that is a v2 falsification, not a licence to parse working. |

**Verdict on B.** Best candidate that still measures communication.
Minimum additional structure (§5). Recommended v2: report `(Form, CC)`
honestly; never relabel `Form` as coverage; no fallback to traces.

### 3.3 Candidate C — Trajectory-derived declared evidence

Two very different sub-candidates hide under this name.

**C1. Hidden-state recovery (reject).** Mine the last `read` of a gold
cell, the last CSV row, a screenshot OCR, or any tool payload that
*contains* gold. Coverage would be high because Flash `A = SUCCESS`
already says the traces support success. That **is** `A`, not `Y`.

**C2. Declared submit action (consider).** Add a task-agnostic tool
`submit_answer(value)` (or a write to a designated answer file) that
the agent must call to finish. The observation **is** that tool
argument. Intermediate `read`s remain invisible to `Y`.

| Slot | C1 recovery | C2 submit/report tool |
|---|---|---|
| Construct | **Hidden correctness** — **not P4** | Communicated evidence via an action, not via prose |
| Channel | Traces / GUI / files | One designated write/submit |
| Evidence | Whatever the miner finds | The submitted value |
| Allowed | Tool bodies, world | Only the submit payload |
| Forbidden | — (everything becomes allowed; construct collapse) | World, other tools, last-text unless duplicated |
| HIT/MISS/ABSTAIN | HIT≈`A=SUCCESS` | Unique submit matches / mismatches / missing submit |
| Coverage | High by construction | High if the harness requires submit to stop; else a new abstain mode |
| Correspondence | Circular with `A` | Independent if `A` still ignores the submit payload **or** `A` uses traces only — must be specified |
| Contamination | Maximal | Low if submit is gold-blind |
| Gaming | N/A (not a communication metric) | High: submit becomes the exam |
| Natural CUA | Agents already use tools, but **not as a claim channel** | **More CUA-native than a prose CLAIM line**, but it changes the action space |
| Independence | **No** | Yes, if `Y` reads only submit and `A` does not |

**Verdict on C.** C1 is forbidden as v2. C2 is a legitimate *later*
instrument (v3) if B’s prose contract is itself unnatural. It is more
structure than B. It must not be smuggled in as “just looking at the
trajectory.”

### 3.4 Candidate D — Hybrid channel

Typical hybrids:

- D1: `CLAIM:` if present, else unique last-text kind (A1), else traces (C1).
- D2: `CLAIM:` if present, else ABSTAIN.
- D3: last-text unique-kind if unique, else `CLAIM:`.

D1 **collapses constructs** in the fallback. It would convert v1’s
ABSTAIN into recovered HIT on successful traces — the opposite of
`DONE ≠ HIT`.

D2 is Candidate B with an explicit non-recovery rule. That is
discipline, not a new channel.

D3 still dies on show-your-work (A1) for the episodes without a claim
line.

**Verdict on D.** Only D2 is admissible. It is B.

### 3.5 Screenshots, GUI state, action traces, intermediate messages

These are not “more of the same last-text.” Each **changes the
construct** if admitted into `Y`.

| Extra observation | If admitted into `Y` | Construct becomes |
|---|---|---|
| Intermediate assistant messages | Score an earlier claim the agent may have retracted | Dialogue-state, not final communication |
| Action traces (`read`/`click`) | Recover values the agent saw | Hidden correctness |
| GUI / a11y tree | Recover on-screen numbers the agent never stated | Hidden correctness *or* visual communication, depending on whether we require a *presented* field |
| Screenshots / OCR | Same, plus OCR error as a new abstain | Visual communication if we score what is *shown as the answer*; hidden correctness if we OCR the whole desktop |

P4-C Flash last-texts already contain the gold in many ABSTAIN cases.
Opening traces would not fix a “missing answer.” It would **stop
asking whether the answer was communicated** and start **asking
whether the agent had seen the right cell**. That is `A`.

**v2 does not open screenshots, GUI, action traces, or intermediate
messages as evidence for `Y`.** If a future workstream wants visual
communication, it is a new construct note, not a silent widening of
last-text.

---

## 4. Construct comparison (do not collapse)

```
                    communicated claim?          hidden world-correct?
                    (P4 construct)               (adjudicator A)

v1 last-text+anchor    rarely locatable             already SUCCESS
A1 unique-kind bag     blocked by show-your-work    unused
A2 LLM extract         locatable, judged            unused, but new judge
B  CLAIM line          locatable if contract used   unused  ← recommended
C1 trace mining        no — abandoned               yes — duplicate of A
C2 submit tool         yes, via action              unused
D1 hybrid+traces       no — abandoned on fallback   yes on fallback
```

The v1 failure is **not** “we lacked hidden state.” Hidden state is
already `A = SUCCESS` at 100% Flash. The v1 failure is **we lacked a
declared claim convention that natural last-text obeys.**

---

## 5. Minimum additional structure

The smallest change that can raise observability **without** turning
the benchmark into a metric-specific exam:

1. **Do not** teach instruction-anchor echo (“put the answer next to
   the fee name”). That is v1’s convention, and it is task-specific.
2. **Do not** mine working. That punishes honesty (A1) or recovers
   hidden state (C1).
3. **Do** add one **corpus-independent, kind-agnostic** declaration
   that marks which span is the claim.

That is one line, identical on every task:

```
CLAIM: <value>
```

Why this is the minimum:

- It does not mention gold, anchors, family, or cluster id.
- It does not require echoing `ridge tarn fee`.
- It leaves natural working intact in the rest of the message.
- It gives unique-or-abstain a **single designated span**, which is
  what v1 tried to get from instruction phrases and did not get.
- Entity/categorical can commit the **claim remainder**, which is the
  fix C03/C04 needed, without editing v1.

Why this is still a research risk:

- `Form` may be high because we **asked for a form**. That is
  interface compliance, not natural observation coverage. v2 must
  **name it `Form`**, not `Cov`.
- An agent can emit `CLAIM: 39.25` without having done the work.
  That is a **MISS or HIT of the claim**, not of the traces. `A2`
  still exists to keep those facts separate. A leaderboard that
  reports only `CC` without `A2` and without `Form` would be
  gameable. The public report is `(Form, CC)` **and** `A2`, never
  `HIT/N` alone, and never `Form` under the name “coverage.”

If this minimum structure is *still* unused in confirmatory v2
(low `Form`, high `no_claim`), the next design is a **submit tool**
(Candidate C2): reliability measurement through an explicit reporting
*action*, not a smarter parser of prose. Forbidden as in-run repair:

```
CLAIM:  →  Claim:  →  The answer is  →  Total:  →  first number
       →  semantic matching
```

That sequence is v1’s failure mode again: guess what the agent meant.
A submit-tool workstream is a new experiment and a new freeze (v3).

---

## 6. Recommended Metric v2 — Declared Final Claim (DFC)

**Recommendation in one sentence.** Abandon instruction-anchor
last-text as the evidence locator; keep last assistant text as the
carrier of a **declared final claim**; never recover `Y` from traces,
screenshots, or working.

### 6.1 Channel decision (question 8, stated explicitly)

**Yes: abandon “last assistant text only” as v1 implemented it.**

What we abandon:

- last-text as an **unstructured dump** to be mined;
- instruction-literal **anchor substring** as the claim locator;
- entity/categorical **remainder-after-instruction-cut**.

What we do **not** abandon:

- the construct “communicated evidence, not hidden correctness”;
- fail-closed unique-or-abstain;
- explicit ABSTAIN;
- independence of `Y` from world/`A`/gold/task_id;
- `(Form, CC)` honesty (never hide ABSTAIN; never call `Form` coverage).

What we **keep as a carrier**, not as a locator:

- the last assistant message, because that is where natural CUA
  agents already write reports (C06, C11, C21). The last message is
  empirically a communication channel. It is not empirically a
  unique-claim channel without a declaration mark.

Continuity with v1 is **not a reason** to keep the locator. A metric
people use should not preserve an arbitrary observation convention
because the first instrument used it. v1 remains the **falsification
record** of that convention.

If DFC confirmatory later shows that agents also will not emit
`CLAIM:`, then last-text-as-carrier should be abandoned too, in favor
of a submit action (C2). That is not today’s licence to open traces.

### 6.2 Frozen objects (must exist before any v2 τ)

v1 objects stay frozen and unused as v2 validators.

| Object | v2 rule |
|---|---|
| `p4_instrument.py` | **Do not modify.** v1 museum piece |
| New file | `instrument/p4_instrument_v2.py` (name locked at implementation; not written in this $0 step) |
| Wrapper prompt | Frozen bytes, identical for all clusters, containing the CLAIM contract and **no** task-specific echo rules |
| Gold / worlds | **New** qualification + confirmatory corpora. Do not rescore C01–C30 or B* as v2 evidence |
| Anchors | **Not an input to v2 `score()`** |
| Estimators | Public: `Form`, `CC`, `Abs`. Optional `DH = HIT/N` only with `Form` and `CC`. **`Cov` is a v1 name; do not use it for v2.** |

### 6.3 Formal episode map

Let an episode produce last assistant text `τ`. Let `kind` and `gold`
be locked independently, before `τ`.

**V1\* (channel cleanliness).** Same well-formed `<function>`/`<tool>`
strip as v1. Malformed residual openers → `ABSTAIN` / `channel_indeterminate`.

**V2\* (claim locate).** Let `L` be the set of newline-terminated lines
in cleaned `τ` matching, case-insensitive:

```
^\s*CLAIM\s*:\s*(.+?)\s*$
```

- If `|L| = 0` → `ABSTAIN` / `no_claim`.
- Let `R` be the set of capture groups (the remainders).

**V3\* (kind parse on remainders only).**

- `money_usd`: extract money tokens from each remainder with the same
  money regex as v1. If a remainder contains **zero** money tokens →
  that remainder is unparseable. If it contains **more than one
  distinct** money token → `ABSTAIN` / `ambiguous_claim` for the
  episode (the contract forbids working on the CLAIM line).
- `integer`: integer tokens, excluding spans that are money, same as v1.
  Same unique-or-abstain on the claim remainders.
- `entity` / `categorical`: the remainder **itself** is the candidate
  (collapsed whitespace, casefold for equality). No instruction-anchor
  cut.

**V4\* (unique-or-abstain).** Union of parsed candidates across `CLAIM`
lines, keyed by the same `equiv_key` as v1.

- 0 parseable candidates → `ABSTAIN` / `absent_claim`.
- >1 equivalence class → `ABSTAIN` / `ambiguous_claim`.
- 1 class → `committed`.

**V5\* (correspondence).** Same `v3_match` as v1 (keep the function
name in v1; v2 correspondence is the same math). Match → `HIT` /
`match`. Else `MISS` / `mismatch`.

**V6\* (no task_id).** `score_v2(channel, *, kind, gold)` — **no**
`anchors`, **no** `task_id`, **no** path under any sealed corpus.
Refuse to import v1 `score()` as a fallback.

ABSTAIN is never rewritten to HIT or MISS.

### 6.4 Estimands (cluster unit, primary model Flash)

v2 public quantities. **`Cov` is a v1 name and is not used for v2.**

\[
\mathrm{Form} = \frac{\#\{\text{parseable unique CLAIM exists}\}}{N},\quad
\mathrm{CC} = \frac{\#\mathrm{HIT}}{\#\mathrm{HIT}+\#\mathrm{MISS}},\quad
\mathrm{Abs} = \frac{\#\mathrm{ABSTAIN}}{N},\quad
\mathrm{DH} = \frac{\#\mathrm{HIT}}{N}.
\]

`Form` is **interface compliance**, not observation coverage. Never
call it coverage in a paper, table, or gate name.

Under DFC, `Form = (HIT+MISS)/N` if every unique claim parses as
`kind`. That equality does not restore the v1 name `Cov`.

`CC` is **undefined** if `HIT+MISS = 0`. `DH` may be shown only with
`Form` and `CC`. `DH = Form \times CC` when `CC` is defined.

Unit = cluster. Two models on one cluster are paired observations, not
`N+1`. Primary = Flash. GPT descriptive. Do not inflate `N` by pooling
models or by pooling a pilot.

Independent `A2` (traces+world, gold-locked, **not** last-text, **not**
`score_v2`) is reported per cluster and **never** substituted for `Y`.

### 6.5 Properties required of the implementation

- Frozen before new observations (hash the `.py`, the wrapper prompt,
  and the corpus seal).
- Corpus-independent (no cluster_id / family / slot branches).
- No post-hoc repair after seeing τ (regex, wrapper, gold, floors).
- Explicit ABSTAIN causes: `channel_indeterminate`, `no_claim`,
  `absent_claim`, `ambiguous_claim`.
- Mathematically defined as above.
- Reproducible: same `(τ, kind, gold)` → same `{status, cause, committed}`.

### 6.6 What v2 will **not** do

- Rescore P4-C or P4-B last-texts and call that “v2 validation.”
- Add instruction-anchor aliases derived from C05/C11 paraphrases.
- Fall back to A1 unique-kind on the whole message when `no_claim`.
- Fall back to traces when `no_claim`.
- Use an LLM extractor.
- Lower floors because v1 floors were missed.

---

## 7. Validation protocol (locked before any agent execution)

P4-C v1 G1–G6, `Cov`, `CC`, and last-texts are **motivation**, not
v2 evidence. A new instrument requires a new qualification corpus,
a new confirmatory corpus, a new seal, and a new spend ledger.

### 7.1 Phases (no API until Phase 3 is separately authorized)

| Phase | Spend | Action | Gate |
|---|---|---|---|
| 0 | $0 | This design file | Human: accept `GO TO V2 DESIGN` |
| 1 | $0 | Author **new** worlds + gold + wrapper; **do not** copy C/B ids | Construction tests, T1–T8 analogues, **no anchors in `score_v2`** |
| 2 | $0 | Seal corpus + hash `p4_instrument_v2.py` + hash wrapper | Seal; qualification on **authored synthetic last-texts** (not agents) |
| 3 | small API | Flash pilot on 3 new clusters | Technical: last-text obtained; `score_v2` returns HIT/MISS/ABSTAIN without harness exception. **Not** a Form peek used to retune |
| 4 | confirmatory API | Flash+GPT × `N` | Gates H1–H8 below |
| 5 | only if Phase 4 PASS | Optional third model | Descriptive |

Phase 0 accepted. Phase 1 construction **PASS** (D01–D30; `$0`; no agents).
This file does **not** authorize Phase 2 seal or Phase 3 agents.

### 7.2 New corpora (do not reuse C or B)

**Qualification `Q2` (synthetic, $0).** ≥6 authored last-texts per
kind, no agents:

| Fixture | Required `Y` |
|---|---|
| Unique `CLAIM:` = gold, plus working tables elsewhere | HIT |
| Unique `CLAIM:` ≠ gold | MISS |
| No `CLAIM:` even if gold appears in working | ABSTAIN `no_claim` |
| Two `CLAIM:` lines, different values | ABSTAIN `ambiguous_claim` |
| `CLAIM:` with two moneys on that line | ABSTAIN `ambiguous_claim` |
| Gold-absent instruction analogue of C3/C4, `CLAIM:` empty / missing | not HIT |
| C5/C6: perturb working, not CLAIM | `Y` unchanged |
| C5/C6: perturb CLAIM value | `Y` may change |

**Confirmatory `D` (new dialect, new cover tokens, new ids).**  
`N = 30` clusters. Families 5 each (Locate, Compute, Reconcile, Filter,
Tally) **or** 5 each including Multi-step as in P4-C — freeze at Phase 1
from **task coverage**, not from v1 abstention rates. Do not drop Tally
because v1 Tally abstained.

Kinds: mix money / integer / entity / categorical with a published
quota at Phase 1 (suggested, not copied from a v1 peek: money 12,
integer 9, entity 5, categorical 4 — freeze in Phase 1 params, not
here as a licence to match C).

Slots: C1-intended 10 / C2-intended 10 / ordinary 10, **designed
before τ**. Ordinary includes gold-absent and invariance pairs as in
v1’s C3–C6 roles, under **new** ids.

**Independent ground truth.** New adjudicator `A2`: traces + world,
not last-text, not `score_v2`. Conservative `INDETERMINATE` is a
design risk to declare at Phase 1, not a patch after τ.

### 7.3 Floors and acceptance thresholds

Floors are on **Flash confirmatory clusters**, not 60 episodes.

| Gate | Name | Threshold | Fail policy |
|---|---|---|---|
| H1 | False HIT | 0 HIT on designed gold-absent / C3–C4 analogues | FAIL v2 |
| H2 | C1 sensitivity | Among clusters with designed C1-intended **and** `A2=SUCCESS` **and** `Y≠ABSTAIN`, HIT rate ≥ 0.90; **n_eligible ≥ 10** | FAIL if rate < 0.90; FAIL if n < 10 (NOT_EVALUABLE is a fail of usability, same as v1) |
| H3 | C2 discrimination | Among designed C2-intended with a committed value, MISS rate ≥ 0.90; **n_eligible ≥ 10** | Same |
| H4 | Invariance | Status and committed unchanged under working-span C5/C6; CLAIM-span C6 **may** change and must be a named test | FAIL if working-span transforms change `Y` |
| H5 | Interface compliance | `Form ≥ 0.80` on Flash | FAIL. Justification: the contract is in the wrapper; if 20%+ still `no_claim`, DFC is not a usable declared-prose channel. **Not** copied from v1’s 0.50. Never named coverage. |
| H6 | Scalar honesty | Public tables show HIT/MISS/ABSTAIN and `(Form, CC)`; `DH` only with both; never convert ABSTAIN; never call `Form` coverage | FAIL if hidden |
| H7 | Anti-recovery | `score_v2` bytes contain no tool/world/screenshot/path reader; no call to v1 `score()` | FAIL at seal, before agents |
| H8 | Anti-circularity | Confirmatory ids ∩ {B*, C*, Q*, CQ*, V*, R*} = ∅; P4-C τ not in the v2 score set | FAIL at seal |

**Do not lower H2/H3 floors after seeing eligibility.**  
**Do not lower H5 after seeing `Form`.**  
If H5 fails, v2 is **falsified as a usable declared-prose channel**.
The scientific next step is a **new** design freeze (submit tool), not
H5 := 0.50.

### 7.4 Anti-circularity controls

1. Design of DFC is **motivated** by P4-B and P4-C v1. That is allowed.
2. Using those τ to choose regex, aliases, or floors is **not**
   allowed. This memo uses them as **examples of the failure mode**.
3. Authors of C last-texts have seen natural reports. They must not
   author D worlds that secretly require those paraphrases. New
   dialect / new cover tokens.
4. `A2` must not call `score_v2`. `score_v2` must not call `A2`.
5. Wrapper must not contain gold, anchors, or “put the fee name next
   to the number.”
6. Phase-3 pilot τ is **not** pooled into Phase 4 and is **not** a
   retune signal.

### 7.5 Falsification criteria for v2

v2 is **wrong** (stop, do not repair in place) if any of:

- H1 fails (invented HIT).
- H5 fails (agents do not use the declared channel).
- H2 or H3 fail on rate, or are NOT_EVALUABLE because eligibility
  floors are missed **after** H5 passed (then we have claims but
  correspondence is not established — different failure).
- H4 fails (fragile parser).
- H7 fails (construct collapse into traces).
- Authors edit `CLAIM` regex, wrapper, gold, or floors after Phase 3/4
  τ exist.

v2 is **not** falsified by:

- `CC < 1` on C2-intended (that is the point of C2).
- `A2=SUCCESS` with `Y=MISS` (declared claim wrong; construct working).
- `A2=SUCCESS` with `Y=ABSTAIN` **if H5 still passes** (rare missing
  claims). If this is the modal cell, H5 fails.

### 7.6 What “PASS v2” would allow — and what it still would not

If H1–H8 PASS, the claim that may be written:

> Under a frozen declared-claim channel, a fail-closed correspondence
> instrument produced usable Form and 0 false HIT on a new corpus,
> without reading traces.

Still **forbidden** without a later independent validation:

- “P4 accurately measures agent reliability in the wild.”
- OSWorld / external CUA transfer (the old P4-D idea). That is
  **after** v2 PASS, as a new workstream, not as a substitute for v2.
- Ranking models from GPT descriptive numbers.

---

## 8. Remaining threats to validity

1. **Teaching to the metric.** `CLAIM:` is a form. High `Form` may
   mean compliance, not that natural CUA “has an observation channel.”
   Mitigation: report `Form` as form-compliance; keep `A2`; keep C2
   MISS; never drop the wrapper from the methods text.

2. **Declared ≠ executed.** An agent can CLAIM gold after a failed
   exploration, or CLAIM a wrong total after a correct read. That is
   **on-construct** for communication. It is a threat if readers treat
   `CC` as task success. Mitigation: always publish `A2` beside `Y`.

3. **Show-your-work leakage onto the CLAIM line.** If agents write
   `CLAIM: 39.25 (21.40+17.85)`, v2 ABSTAIN `ambiguous_claim`. That is
   fail-closed. Threat: H5 fails because the contract is too brittle.
   Mitigation: the wrapper forbids extra tokens; do not then parse the
   first money only after seeing τ.

4. **Author contamination.** This memo is informed by C/B last-texts.
   Threat: Phase 1 authors write D instructions that secretly match
   observed paraphrases. Mitigation: new dialect; no C/B ids; no
   looking at C τ while authoring D.

5. **Adjudicator conservativeness.** v1 `A` could be INDETERMINATE on
   Compute/Tally. If `A2` is too conservative, H2 eligibility dies for
   a reason other than `Y`. Mitigation: specify `A2` at Phase 1;
   INDETERMINATE is not silently SUCCESS.

6. **Kind remainder for entities.** Scoring the whole CLAIM remainder
   fails if agents write `CLAIM: Ivo Nair (tarn crag card)`. That is a
   Phase-2 synthetic fixture, not a post-τ special case.

7. **Primary-model choice.** Flash is inherited from v1 as the gate
   model. If Flash cannot follow a one-line contract and GPT can, H5
   fails on the declared primary. Do not switch primary after τ.

8. **Continuity bias.** The temptation to keep v1’s locator “so the
   paper has one instrument.” That would preserve a falsified channel.
   This file rejects it.

---

## 9. Programme after a v2 decision

```
P4-C v1     falsification of last-text ⊕ instruction-anchor
                ↓
P4-C2 DFC   declared-claim instrument (this design)
                ↓  if Phase 4 PASS
qualification already in Phase 2 synthetics
                ↓
independent confirmatory (Phase 4; new corpus D)
                ↓  only if PASS
external validation (new workstream; not old P4-D by default)
                ↓
if H5 FAIL: freeze v3 as submit_answer (Candidate C2), not parser repair
```

Old “P4-D = OSWorld external validation of v1” is **not** next.
External validation of a failed instrument would export the abstention.

---

## 10. Single recommendation

**PHASE 1 PASS. STOP.**

Phase 2 qualification/seal is **BLOCKED** until separately authorized.
Do not execute agents. Do not rescore C/B. Do not repair v1.

v1 is closed and failed. That failure is the reason v2 exists.
