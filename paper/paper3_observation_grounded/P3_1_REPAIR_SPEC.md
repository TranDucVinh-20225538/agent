# P3-1 — Auditable measurement repair (pre-registration)

Status: **FROZEN BEFORE IMPLEMENTATION. NOTHING HAS BEEN RUN.** No code exists for this
gate. Every decision rule, quantity, fixture and kill criterion below is fixed at the
commit that carries this file, and none may be altered afterwards except by a dated
amendment recorded in this document.

Follows `P3_0_CONCLUSION.md`, which closed P3-0. P3-1 modifies nothing that P3-0 touched:
not the frozen extractor at `3242c30`, not `protocol/matching.py`, not
`out/study2_gold_path_lock.json`, not any archive or trajectory, not any Paper 1 or
Paper 2 number. The repaired instrument is a **new, separately named** measurement layer
evaluated *against* the frozen one; the frozen one remains the published instrument.

The §1 terminology lock of `P3_0_SPEC.md` and §7 of `P3_0_CONCLUSION.md` apply in full.

---

## 0. Disclosures that bound what may be pre-registered

Pre-registration is worthless if the author already knows the answer and pretends not to.
Two specific contaminations exist and are recorded here so that §3, §4 and §6 can be
written around them rather than over them.

**D-1 — the ordering direction is partially known.** While assessing whether §4 was worth
designing, a partial hand computation was made on the Paper 2 common support. It was not
completed to an aggregate, but it indicated that plurality-style aggregation repair raises
GPT more than Flash on `retrieval-f009`, i.e. tends to **widen** GPT's STS advantage
rather than invert the ordering. Consequence, binding: **no directional hypothesis about
the ordering may be stated by this author, here or later.** §4 is two-sided, secondary,
and descriptive. The paper's headline may not depend on the ordering outcome.

**D-2 — the sealed set's prose has been read once.** `tracking_evidence.md` was read while
establishing that component-level human labels exist at all (§6). At least three legs were
noticed a priori in which the human coder scored an answer **correct** although it states
two different values for one quantity and explains the discrepancy — `aggregation-f018`
Claude CF, `retrieval-f030` GPT CF, `preference_inference-f004` Claude CF — together with
one contrast leg where an agent's cross-check produced the **same** value twice
(`retrieval-f029` Claude). No count, rate, or instrument output on that corpus has been
computed. Consequence: the §6.3 prediction is stated as a **quantified** claim whose count
is unknown, and it is explicitly labelled as informed by three observed instances. It is
not presented as a blind prediction.

**D-3 — all 134 Study 2 rows have been seen.** Nothing in the Study 2 archive is sealed.
The archive is therefore the **development** corpus only, and no claim of generalisation
may rest on it. §6 exists because of this.

---

## 1. Construct

P3-0 established that the quantity Paper 2 reported is not separable from the instrument
that produced it. A single reliability score confounds at least four distinct losses:

```
gold specification  ->  observation channel  ->  extraction  ->  comparison  ->  score
```

At each boundary information can be destroyed, and in the frozen instrument each boundary
was demonstrated to destroy some: unresolvable gold scored as agent error (14/134 vacuous
rows; `preference_inference-f010` vacuous on every leg of every lane); tool-call
scaffolding and runtime-generated spans of unidentifiable provenance entering the answer
channel (see §2, R-CHAN — these are *not* verbatim prompt echo, and the distinction is
load-bearing); label coverage, window scope and fail-closed aggregation losing recoverable
values; exact equality converting a correct-but-over-long extraction into a miss.

**The construct of P3-1 is the separability of observation failure from measurement
failure.** Observation failure means the agent did not put the evidence in the channel.
Measurement failure means the instrument did not recover evidence that was in the channel.
A non-auditable instrument returns one number in which these are indistinguishable. An
auditable instrument returns a decomposition in which they are distinguishable, and the
decomposition can itself be checked.

**What P3-1 claims.** That the decomposition is achievable by a repair family specified in
advance at the level of *failure categories*, not individual defects; and that the
decomposition's components can be estimated with sensitivity and precision measured
against human labels on a corpus the repair family never saw.

### 1.0 Why the requirement is not already satisfied

The underlying benchmark's own grading is `"type": "llm_judge"` on **every** rubric
criterion, and its task schema records that "Grading is rubric-only (LLM-as-judge);
programmatic checks were retired in an earlier revision."

This is citable, local, and is the motivation in one line: the field did not fail to adopt
auditable measurement, it **retired** it. The instrument whose intermediate state P3-0 was
able to read existed only because Paper 2 built a separate deterministic tracking layer
beside the judge. Had Paper 2 used the benchmark's own grading, every quantity in §1.1
would be unobtainable.

**What P3-1 does not claim.** Not that agents are more or less reliable than Paper 2
reported. Not that the repaired instrument is correct. Not that `text_present` is
correctness. The repaired instrument is a *better-characterised* instrument, not a true
one, and its own residual loss is reported rather than assumed away.

### 1.1 Frozen baseline, carried forward

From `P3_0_IDENTIFICATION_AUDIT_SPEC.md` §1 and `P3_0_CONCLUSION.md`, on 57 legs and 134
leg×component rows: `MATCH` 20, `RECALL_MISS` 39, `ABSENT` 61, `VACUOUS_GOLD` 14,
`ANOMALY` 0; five rows structurally unreadable, all five `ABSENT`.

`ANOMALY = 0` is load-bearing and must be restated wherever the denominator 59 appears.
It is the only evidence that `MATCH ⊆ R1-positive`. Were any row matched without the gold
string being R1-recoverable — possible in principle, since `match_money_usd` carries a
±1 tolerance — the denominator 59 would be invalid.

Three quantities, kept **separate** and never merged:

| quantity | frozen value | reading |
|---|---|---|
| R1 recoverable-evidence share among readable non-matches | 39/95 = **0.411** | *lower bound* on the share of the instrument's readable negatives that are provably false; 61 `ABSENT` rows are excluded from the numerator because their truth status is unknown, not because they are correct |
| instrument sensitivity on R1-recoverable evidence | 20/59 = **0.339** | of rows where the gold value is literally present in the answer, the instrument recovers one third |
| proven aggregation-discard rate | 13/59 = **0.220** | gold entered `found` and was discarded; `M1a` |

Cause decomposition among the 39 misses: `M1` 20 (of which `M1a` 13, `M1b` 7), `M2` 9,
`M3` 5, `M4` 5. Among the 61 absences: `M1` 25, `M2` 19, `M3` 2, `M4` 15. In 7 of 13 `M1a`
rows gold was a strict majority of accumulated candidates and was discarded anyway.

None of these is a false-negative *rate* in the statistical sense, and the phrase must not
be used for 0.411.

---

## 2. The repair family

Four repairs, one per layer boundary, each addressing a **category** in the P3-0 taxonomy.
Each is a decision rule stated completely here. None is parameterised, none is fit to
data, and none may be altered after this document is frozen.

### 2.0 Provenance parity — binding on every repair

> **No repair may use provenance unavailable to the baseline evaluator, unless that
> provenance is explicitly defined as part of the repaired instrument and declared here.**

The reason is a specific attack a reviewer can make. R-CHAN must decide which spans are
scaffolding and which are agent evidence. If it were permitted to consult a metadata field
the frozen instrument never had — a recorded tool-call boundary, a role tag, a harness
event log — then the repair would be receiving **oracle information** about provenance, and
any gain it showed would be an artefact of privileged access rather than of the repair
rule. The measured improvement would not be reproducible by anyone whose instrument reads
the same channel the frozen one read.

Applied to the four repairs as specified: R-AGG reads only the `found` list the frozen
function already built; R-SCOPE reads only the answer string; R-CMP reads only `gold` and
`reported`; R-CHAN reads only the answer string and the literal markup tokens inside it.
**All four operate on strictly the same inputs as `FROZEN`.** No repair consults the
trajectory, the task definition, the harness log, or any role/turn metadata.

This is also why the dropped prompt-echo rule could not simply be rescued by reading
`instruction` from the task registry. Even setting aside that the observed span is not the
instruction (§2, R-CHAN), the frozen instrument never read the task definition, so a repair
that did would violate parity. The correct conclusion is the one recorded: channel
provenance is **not determinable from the channel**, which is an argument for exposing
intermediate reads rather than for granting the repair extra inputs.

### R-AGG — aggregation (targets `M1a`)

Replace `_unique_or_none`'s unanimity requirement with **plurality over the frozen
equivalence classes**.

Group the filtered `found` list by the equivalence relation `_unique_or_none` already uses
internally — `Decimal` equality for `money_usd` and `integer`, casefolded string equality
otherwise — and return the modal group's value. **On an exact tie for the modal group,
abstain and return `None`.** The equivalence relation is imported unchanged; only the
decision rule changes.

The frozen `match_money_usd` ±1 tolerance is *not* used for grouping, because it is not
transitive and therefore not an equivalence relation. This is the reason the minimal
change is to the decision rule and not to the relation.

### R-SCOPE — observation scope (targets `M3`)

Generate candidates over the **whole answer** instead of the ±120-character label window.
This is the scope of rule R1, already frozen in `P3_0_RECALL_AUDIT_SPEC.md` §4.

Rationale, established in 0.6 and not a conjecture: the window candidate set is not a
subset of the whole-text set, because `MONEY_RE`'s `(?<![A-Z])` and `INT_RE`'s `(?<![\d.,])`
lose context at a slice boundary — verified on `"SM-88431"`, which yields `+88431` from the
full text and `−88431` from a window cut inside the token. Whole-answer scope removes the
boundary artefact rather than trading one for another.

### R-CMP — comparison (targets entity `M1b` segmentation)

For `categorical`/entity components only, replace exact equality with **one-directional
containment**: gold matches if `norm(gold)` is a contiguous substring of `norm(reported)`.

The direction is asymmetric and the asymmetry is the principle: an agent that says more
than gold has still reported gold, whereas an agent whose report is a strict prefix of
gold has not. Consequently this repair does **not** rescue the three
`designated_booking_property` rows, where `extract_entity`'s `re.split(r"[(\[]", s)[0]`
truncates the candidate to a prefix of gold. Those rows remain structurally unreadable and
remain excluded, exactly as in 0.6.

### R-CHAN — observation channel (targets scaffolding contamination)

Before extraction, delete from the answer text any span delimited by
`<function`…`</function>`, `<tool`…`</tool>`, or their self-closing forms.

R-CHAN is the only repair that can **reduce** the candidate set. It can therefore only
lower sensitivity and raise precision, and its effect is reported separately from the
other three for exactly that reason.

**A prompt-echo rule was drafted and removed. The removal is a finding, not a
simplification.** 0.7 recorded a `found` list on `gpt/retrieval-f010/G1` containing
`"Provide the Jamaica booking total, host name, and amenities from the booking record"`,
which was described as prompt echo. A read-only check of the local task definitions
disproves that description. `retrieval-f010`'s actual `instruction` is:

> "What was the total cost of my Jamaica trip — pull the trip total from the booking. Also
> tell me the host name on file and what amenities the property comes with so I know what
> I'm getting."

The observed span appears in **none** of `all_tasks.json`,
`all_tasks_with_grading.json` or `mypcbench_clean.json`, and is not a rubric criterion
either. It is a runtime-generated restatement of **unidentifiable provenance**.

Consequence for the repair: a literal-echo rule cannot match it, and matching a paraphrase
would require semantic similarity, which is forbidden. Rule (1) is therefore dropped.

Consequence for the construct, which is the larger point: **the observation channel cannot
be deterministically cleaned, because the spans that contaminate it are generated at
runtime and are not enumerable from the task definition.** A verbatim prompt echo would be
trivially removable; a runtime paraphrase is not. This strengthens rather than weakens the
construct-validity finding of `P3_0_CONCLUSION.md` §5, and it is a direct argument for the
auditability requirement: since a clean channel cannot be guaranteed, the minimum
obligation is that the instrument's reads be **visible**.

### 2.1 What is deliberately NOT repaired, and why this is the point

Three known defects are left in place:

| defect | why not repaired |
|---|---|
| `avg(erage)? cost` does not match `average cost` | a typo in one label; no category-level generalisation. Fixing it is "finding a bug in an extractor" and is precisely the objection P3-1 must not invite. |
| `_DATE_RE` is ISO-only | a coverage gap in one kind's parser; same reason. |
| `extract_entity` truncates at `(` / `[` | a defect in one candidate generator; R-CMP's asymmetry is what keeps it out of scope. |

These three become an **internal negative control**. `M2` rows are caused by label
coverage, and no repair in the family addresses label coverage. Therefore:

> **Leakage guard.** If any configuration recovers an `M2` row, the repair family is not
> operating at the category level it claims, the implementation is wrong or the taxonomy
> is wrong, and the run is void. This fires on 9 development rows and is checkable before
> any headline quantity is read.

### 2.2 Configurations, fixed in advance

Six, and only six. No post-hoc subset, no additional ablation.

`FROZEN` · `R-AGG` · `R-SCOPE` · `R-CMP` · `R-CHAN` · `ALL`

---

## 3. Primary quantities

All computed for all six configurations, on the development corpus (134 rows) and on the
sealed corpus (§6). Wilson 95% throughout. No threshold is declared here and none may be
invented afterwards.

**Instrument properties — primary.**

1. Sensitivity on R1-recoverable evidence: `MATCH / (MATCH + RECALL_MISS)`. Frozen 0.339.
2. Abstention rate: share of rows where the instrument returns `None`.
3. Confident-wrong rate: `M4 / (rows where the instrument reports a value)`. Frozen: 20
   `M4` rows in total across misses and absences, including `3570.0` reported where gold
   was `42.12`.
4. Residual cause decomposition `M1a`/`M1b`/`M2`/`M3`/`M4` per configuration.

Quantity 3 is as important as quantity 1 and is reported beside it in the same table.
R-AGG trades abstention for commitment; a repair that raises sensitivity by reporting more
wrong values is not a repair, and the design must be able to say so.

**Precision — only measurable on the sealed corpus.** The development corpus has no
component-level human label, so precision is not estimable on it. This asymmetry is stated
rather than papered over: on Study 2 the instrument's sensitivity can be bounded and its
precision cannot.

**Explicitly not a primary quantity:** any agent-level reliability estimate.

---

## 4. Ordering analysis — two-sided, secondary, descriptive

Constrained by **D-1**. The hypothesis carries no sign:

> The repaired instrument yields per-leg STS, pair STS, `Y`, and a model ordering on the
> Paper 2 common support that differ from the frozen instrument.

Pre-committed reporting, identical in all four outcomes (ordering unchanged / widened /
narrowed / inverted): ΔSTS with Wilson or bootstrap 95% under `FROZEN` and under each
configuration, the sign, and whether the argmax moved. The frozen value is
ΔSTS = −0.042, CI [−0.125, 0.000], a margin that touches zero.

Three statements fixed now so that no outcome can be spun:

* ordering **inverts** → measurement artefact can invert agent selection. Strong, and
  reported as secondary, not as the headline.
* ordering **widens** → the artefact was *masking* disagreement, not creating it. This is
  a result, not a disappointment, and is the outcome D-1 makes more likely.
* ordering **unchanged** → the artefact does not propagate to selection at this n. Also a
  result, and the honest one to report if it occurs.

`Y` is computed but is expected to remain degenerate; it is reported, not interpreted.
Paper 2's published numbers are not restated or corrected. Errata E-1 stands as recorded.

---

## 5. Synthetic control cases

Authored **before** implementation, from the taxonomy, and frozen with this document. Each
repair gets cases where it must help **and** cases where it must hurt; a suite that only
contains cases favourable to the repair measures nothing. Ground truth is known by
construction because the answer text is written here in full.

### 5.0 What the suite is for

The suite is **not a vote**. Every fixture carries a `required outcome` fixed below, and
harm cases are *expected* to harm — that is their required outcome, and it prices the
repair rather than vetoing it. The suite's only function is to verify that each repair,
as implemented, behaves exactly as specified on inputs whose ground truth is known by
construction. See K2, which fires on a **mismatch between actual and required outcome**,
not on a tally of help versus harm. The decision to drop a repair belongs to §7 K4 on real
data, never to a count of fixtures the author chose to write.

### 5.1 Construction rules

All fixtures use the synthetic task id `synthetic-s000`, which exists in no corpus.
Component ids are chosen so that no entry exists in the frozen `LABELS` table and the
documented default applies: `re.escape(component_id.replace("_", " "))`. Every label
phrase and every entity name below was verified **corpus-absent** before freezing, by
case-insensitive search over the whole repository — `settlement total`, `payout total`,
`transfer total`, `rebate total`, `closing balance`, `wire total`, `lodging site`,
`Cedarline Lodge`, `Cedar Lodge`, `Cedar Lodge Annex`, `Harbour Point`: zero files each.
This is what prevents a reviewer from arguing the fixtures were reverse-engineered from an
observed row. (`refund amount` and `booking property` were drafted first and rejected at
54 and 2 files.)

**Window arithmetic must be controlled explicitly, because the frozen extractor appends
`ms[0]` — the *first* candidate in each ±120-character label window.** In short text the
windows overlap and every window yields the same first candidate, which would silently
turn an intended disagreement fixture into a unanimous one. Fixtures therefore separate
label occurrences with a filler defined as

```
FILL(n) = ("the account notes contain no further figures. " * k)[:n]
```

which contains no digit, no currency symbol and no label substring. `FILL(250)` between
consecutive labels makes the ±120 windows disjoint. `+` below denotes concatenation.

### 5.2 The fixtures

`+` = repair must help · `−` = repair must harm, and the harm is the priced cost ·
`=` = repair must change nothing, verifying a rule

| id | target | component / kind / gold | answer text | required outcome |
|---|---|---|---|---|
| **S1** | R-AGG **+** | `settlement_total` / `money_usd` / `4820.50` | `"Settlement total: $4,820.50."` + FILL(250) + `"Settlement total confirmed at $4,820.50."` + FILL(250) + `"An older draft lists settlement total $3,910.00 (stale)."` | `found=[4820.50, 4820.50, 3910.00]`. `FROZEN` not unanimous → `None` → miss. `R-AGG` modal 2-of-3 → `4820.50` → **match** |
| **S2** | R-AGG **−** | `payout_total` / `money_usd` / `1205.00` | `"Payout total: $1,205.00."` + FILL(250) + `"Payout total shown as $990.00."` + FILL(250) + `"Payout total again $990.00."` | `found=[1205.00, 990.00, 990.00]`. `FROZEN` → `None`, abstains. `R-AGG` modal → `990.00` → **confident-wrong caused by the repair**. Gold was the minority and plurality cannot recover it |
| **S3** | R-AGG **=** | `transfer_total` / `money_usd` / `700.00` | `"Transfer total $700.00."` + FILL(250) + `"Transfer total $700.00."` + FILL(250) + `"Transfer total $512.00."` + FILL(250) + `"Transfer total $512.00."` | exact 2–2 tie. Both `FROZEN` and `R-AGG` return `None`. Verifies the tie rule abstains rather than picking `found[0]` |
| **S4** | R-SCOPE **+** | `rebate_total` / `money_usd` / `318.75` | `"Rebate total is stated below."` + FILL(260) + `"The credited figure is $318.75."` | no money inside the label window → `found=[]` → `FROZEN` `None`, cause `M3`. `R-SCOPE` scans the whole answer → `318.75` → **match** |
| **S5** | R-SCOPE **−** | `closing_balance` / `money_usd` / `2450.00` | `"Unrelated invoice total $77.10."` + FILL(260) + `"Closing balance: $2,450.00."` | `FROZEN` window contains only `2450.00` → **HIT**. `R-SCOPE` appends the whole answer's *first* money → `77.10` → **turns a correct match into a confident-wrong**. See §5.3 |
| **S6** | R-CMP **+** | `lodging_site` / `categorical` / `Cedarline Lodge` | `"Lodging site Cedarline Lodge, amenities Pool, Wifi, Parking."` (colon removed, A-2.2) | candidate is gold plus a trailing list. `FROZEN` exact equality → miss (`M1b`-style). `R-CMP` `norm(gold) ⊆ norm(reported)` → **match** |
| **S7** | R-CMP **−** | `lodging_site` / `categorical` / `Cedar Lodge` | `"Lodging site Cedar Lodge Annex."` (colon removed, A-2.2) | a genuinely different property whose name contains gold. `FROZEN` correctly misses. `R-CMP` → **false positive caused by the repair**. Both names are invented and corpus-absent per §5.1 |
| **S8** | R-CMP **=** | `lodging_site` / `categorical` / `Harbour Point (North Wing)` | `"Lodging site Harbour Point (North Wing)."` (colon removed, A-2.2) | `extract_entity` splits at `(`, so `reported = "Harbour Point"`, a strict prefix of gold. `norm(gold) ⊄ norm(reported)`. **Neither recovers.** Verifies R-CMP's one-directional asymmetry and that the paren defect stays unrepaired per §2.1 |
| **S9** | R-CHAN **+** | `wire_total` / `money_usd` / `6100.00` | `"I could not retrieve the figure."` + `"<function=lookup>{\"wire total\": \"$6,100.00\"}</function>"` | the only label hit and the only money are inside scaffolding. `FROZEN` reports `6100.00` → **spurious HIT on a value the agent never reported**. `R-CHAN` deletes the span → `None` → **correctly abstains** |
| **S10** | R-CHAN **−** | `wire_total` / `money_usd` / `6100.00` | `"<function=lookup>{\"q\": \"wire\"}"` + `" The wire total is $6,100.00."` | unterminated opener, legitimate prose after it. `FROZEN` → **HIT**. `R-CHAN` deletes to end of text → `None` → **loses a recoverable value** |

### 5.3 Two hazards the fixtures expose, recorded before implementation

**S5 shows that R-SCOPE's benefit does not transfer from presence to selection, and this
was not obvious.** Rule R1 in 0.6 asked only *"is gold anywhere in the answer"*, a
presence question for which whole-answer scope is strictly better. Extraction asks a
different question — *"which candidate do you pick"* — and the frozen `extract_money`
answers it positionally, by `ms[0]`. Widening the window to the whole answer therefore
makes the pick the **first money in the document**, which can be a distractor that the
narrow window correctly excluded. R-SCOPE can convert a `HIT` into a wrong report.

This hazard is recorded and the rule is **not changed**. Retuning R-SCOPE now — to a wider
but still bounded window, or to a nearest-candidate pick — would be fitting the repair to
a hazard the author just noticed, which is exactly the discipline P3-1 exists to avoid.
S5 prices the rule as specified; if the price is high, that is the result.

**S9 and S10 show that R-CHAN's two directions of error are both real and are driven by
the same rule.** S9 is a spurious `HIT` the frozen instrument produces by reading
scaffolding; S10 is a real value R-CHAN destroys by deleting an unterminated span to end
of text. Unterminated openers are the **common** case on non-terminating legs, since such
a leg stops mid-tool-call, so S10 is not an edge case. The deletion rule is fixed as
stated in §2 and priced here rather than hidden.

---

## 6. Sealed validation

### 6.1 The set

`out/stage4_counterfactual_analysis_final/tracking_evidence.md` — Paper 1's hand-coded
classification of all 24 valid pairs, read from the agent's final-answer text against
guest gold (`probe_before`/`probe_after` in `*.guest.json`), described in Paper 1's
Limitations section as "hand-coded from final-answer text against guest gold
(`tracking_evidence.md`); traceable, not automated".

It qualifies as sealed on four grounds, each of which must be stated in the paper:

1. **Disjoint corpus.** Paper 1's Stage 4 cells, five models including Qwen3.5-9B,
   Qwen3.5-35B-A3B and Qwen3.8-Flash, not the Study 2 archive from which the taxonomy was
   derived.
2. **Temporally sealed.** Hand-coded and published on arXiv before P3 existed. The labels
   cannot have been influenced by the repair family.
3. **Component-level, with values.** The prose transcribes what the agent reported *and*
   what gold was, e.g. `"reports total cost basis $8,788.75 -- does not match true
   baseline gold $8,213.25"` and `"reports 'Total Income $91,200' […] does not match true
   CF gold $90,000 (off by exactly $1,200)"`.
4. **Contains negatives with specified wrong values**, which is what makes precision
   estimable at all — see §3.

**Paper 1's rubric `score` is LLM-judged and is not ground truth.** Only the hand-coded
Mechanism prose is. These must never be conflated, and the `score` column is not used.

### 6.2 Transcription protocol

The prose must be transcribed into a structured label table. This is the one place where
author discretion enters a corpus that is otherwise sealed, so it is constrained:

1. Transcription copies only values **literally stated** in the prose. No inference from
   the trajectory, no re-reading of the archive, no judgement about correctness.
2. A leg whose prose does not state a component value literally is marked
   `UNTRANSCRIBABLE` and **excluded**, with the count reported.
3. The mapping from Paper 1 component descriptions to component ids is written and frozen
   **before** any instrument is run on this corpus.
4. The table is committed and hashed before the first run. `tracking_evidence.md` is an
   immutable committed artefact and the transcription is diffable against it and against
   the arXiv PDF, so a third party can check step 1.
5. **No subgroup analysis.** At roughly 50–80 transcribable component observations the
   set supports one sensitivity and one precision estimate with wide intervals, nothing
   more. By model, by task family, or by kind is forbidden.

### 6.3 The prediction, informed by D-2

Stated as a quantified claim whose count is unknown, and labelled as informed by three
a-priori observed instances rather than as blind:

> Among sealed-corpus legs that the human coder scored as **correctly tracking**, there is
> a non-empty subset in which the answer states two or more disagreeing values for one
> quantity — typically because the agent surfaced a channel inconsistency it was right to
> surface. On that subset the frozen instrument abstains (`M1`) and R-AGG recovers.

The contrast subset is legs where an agent's cross-check produced the *same* value twice,
e.g. `retrieval-f029` Claude, on which the frozen instrument should not abstain and R-AGG
should change nothing. Reporting both subsets is what distinguishes a mechanism from a
one-sided illustration.

If confirmed, the transferable statement is not about a regex. It is that **an agent which
surfaces a data inconsistency — behaviour a human evaluator credits — is penalised by a
fail-closed measurement layer.** That is a property of the measurement design, and it is
what P3-1 would contribute beyond a defect report.

---

## 7. Kill criteria

Pre-committed. Each is checkable, and each has a stated consequence that is not "weaken
the claim and continue".

* **K0 — faithfulness guard, not a finding.** R-AGG must recover exactly the `M1a` rows in
  which gold is the modal group. That count is known from 0.7 to be **7 of 13**, so it is
  used as an implementation guard, not as a result. A different set means the
  implementation is unfaithful; abort and fix before anything else is read.
* **K1 — stated on the sealed corpus, because on the development corpus it cannot fire.**
  An earlier draft of K1 read "R-AGG does not drive `M1a` to zero". That was **incoherent
  and is corrected here before freezing**: plurality recovers only those `M1a` rows in
  which gold is the modal group, known from 0.7 to be 7 of 13, so `M1a` must fall to 6 and
  not to 0, and the old K1 would have contradicted K0 and fired on a correct
  implementation. More fundamentally, the mechanism is already *established* on the
  development corpus, so no development-corpus outcome can falsify it. The real, currently
  unknown question is whether it **generalises**. K1 therefore reads: if on the sealed
  corpus R-AGG recovers **no** human-credited leg in which the agent stated disagreeing
  values for one quantity, then §6.3 has failed and the mechanism does not generalise
  beyond the corpus that produced it. Report that in one sentence; do not weaken it to a
  contributing factor.
* **K2 — a fixture-level outcome mismatch, not a tally.** K2 fires when any §5.2 fixture's
  actual outcome differs from its stated `required outcome`, which means the repair is
  mis-specified or mis-implemented. Fix the implementation, or amend the specification
  *before* the archive is touched and record the amendment here. K2 explicitly does **not**
  fire because harm cases outnumber help cases: harm is the required outcome of S2, S5, S7
  and S10, and the suite's composition was chosen by the author, so a tally of it would
  measure nothing but that choice.
* **K3** — any configuration recovers an `M2` row → leakage per §2.1; the run is void.
* **K4** — on the sealed corpus the family's sensitivity/precision is not better than
  `FROZEN` → the repair family does not generalise beyond the corpus that produced the
  taxonomy. Report as failed. Paper 3 scopes down to a diagnostic/methods contribution and
  the prescriptive claim is dropped.
* **K5** — transcription is impossible on more than 20% of sealed legs → sealed validation
  is **not available**. Do not substitute a weaker set, do not hold out part of Study 2
  (nothing there is sealed, per D-3), and do not run new models to manufacture one.
  Paper 3 scopes down as in K4.

**K4 and K5 are not failure modes of the paper.** A demonstration that no category-level
repair dominates — that sensitivity and precision trade off and the instrument cannot be
fixed without a cost — is itself the prescriptive finding, and is reportable as the main
result. The paper must be written so that this outcome is publishable, otherwise §4 and §6
are not really pre-registered.

---

## 8. Order of work and hard stops

Everything required before freezing is closed, and each item is recorded rather than
merely asserted:

* **D-2 scope — decided.** §6.3 is retained and carries its informed-prediction label. It
  is not presented as blind, and the three a-priori instances are named in D-2.
* **R-CHAN implementability — checked, read-only, and it changed the repair.** The
  prompt-echo rule is dropped and the reason is recorded in §2 under R-CHAN. No archive,
  trajectory, extractor or lock was read or touched; only local task definitions under
  `external/MyPCBench-main/tasks/final/`.
* **§5 synthetic suite — authored.** All ten fixtures are concrete text in §5.2, with
  label and entity corpus-absence verified in §5.1 and the two hazards they expose recorded
  in §5.3.
* **Two internal contradictions found in review and corrected before freezing**, recorded
  so the correction is auditable: the old K1 would have fired on a correct implementation
  because plurality cannot recover minority-gold `M1a` rows, and the old K2 would have
  auto-dropped repairs by tallying fixtures the author chose to write. Both are restated in
  §7.

Remaining:

1. Implement the repaired instrument as a **new module**, by wrapping the frozen one where
   possible, with the same faithfulness discipline as 0.7: every `FROZEN` configuration
   output must reproduce the 0.6/0.7 record exactly, or abort. Provenance parity per §2.0
   is a hard constraint on the implementation, not a guideline.
2. Run the synthetic suite. Apply K2.
3. Freeze the §6.2 transcription and hash it.
4. Run all six configurations once on the development corpus, then once on the sealed
   corpus. Report whole.

Do **not**: modify the frozen extractor, `matching.py`, the gold lock, any archive or any
trajectory; modify Paper 1's or Paper 2's submission directories; run Gate 1 / `0.4`; run
any model; use an LLM judge, semantic similarity, screenshots, or manual qualitative
reading of trajectories; add cells, lanes, tasks or external labels; use a partner score
to select or exclude cases; commit on the host; stop early or extend the run after seeing
a partial result.

---

## 9. Amendment A-1 — 2026-09-12, after the K5 pre-check

Authorised by the status line's reservation for dated amendments. The K5 pre-check was run
**read-only** before any implementation: no HPC, no Study 2 archive, no trajectory read, no
frozen extractor or `matching.py` or gold-lock access. It changed §6 in four ways and
confirmed K5.

### A-1.1 K5 verdict: PASS

The sealed corpus is 10 tasks, 24 hand-coded cells, 48 legs, over five models
(Claude 9, GPT 8, Qwen3.5-9B 3, Qwen3.8-Flash 3, Qwen3.5-35B-A3B 1) — enumerated
mechanically, matching Paper 1's "all 24 valid pairs".

Transcribability was assessed under two rules fixed before counting. **STRICT**: the value
must appear as a literal numeral or string attributed to that leg. **LENIENT**: STRICT plus
an explicitly stated cross-leg identity such as "byte-identical to the base row".

| rule | transcribable | untranscribable | failure rate |
|---|---|---|---|
| STRICT | 46/48 | 2 | **4.2%** |
| LENIENT | 47/48 | 1 | **2.1%** |

K5's threshold is a failure rate above 20%. **K5 passes under both rules**, so no author
discretion is load-bearing. The two failures are named rather than absorbed:

* `GPT / counterfactual-f004 / base` — fails under **both** rules, and it is a *gold-side*
  failure, not a report-side one. The hand-coded gold reads "1099_amount_0 for
  TY2023/2024/2025 all ->0", stating only the post-image. The base-leg pre-image is never
  literally given. This is the same gold-specification failure mode as `VACUOUS_GOLD` in
  §1.1, now observed independently in the sealed corpus, which is worth reporting.
* `Claude / preference_inference-f018 / base` — fails under STRICT only. The base-leg value
  is recoverable solely through the stated identity "byte-identical to the base row".

### A-1.2 The authoritative label source is source code, not prose

`out/stage4_counterfactual_analysis_final/tracking_evidence.md` is **generated**. Its labels
originate in the `CLASS` dictionary of
`out/stage4_counterfactual_analysis_final/build_final.py`, under the verbatim header
`HAND-DERIVED CLASSIFICATIONS for the 24 valid pairs (both legs DONE)`, with `gold` and
`mech` as hand-written one-line strings per cell.

§6.1 and §6.2 are amended to cite `build_final.py::CLASS` as authoritative; the `.md` is a
rendering of it. This is **strictly better** for auditability than the prose §6.2 assumed,
and it directly substantiates Paper 1's Limitations claim that the classification is
"hand-coded […] traceable, not automated".

### A-1.3 Answer text must come from the trajectory, never from either rendering

A second, divergent copy exists: `out/stage4_counterfactual_analysis/tracking_evidence.md`,
688 lines, self-titled "Tracking evidence (canonical)", generated by the now-deleted
`build_audit.py`. It carries per-leg blocks with a `Traj:` path, a per-leg `Gold:` line, and
a fenced block of the agent's answer text — and it covers all 48 sealed legs.

**Its answer text is truncated and must not be used as instrument input.** Measured: 34 of
57 bodies are exactly 400 characters and 6 more are 399, with tails cut mid-token
(`"**Ca"`, `"| 142,"`, `"w2_summa"`), and no ellipsis marker. `build_audit.py` also
truncates elsewhere at 280 characters. Two legs are degenerate excerpts of 6 and 7
characters (`'136,320'`, `'80,000'`).

Answer text is therefore read from the `traj.jsonl` / `messages.json` paths that the
canonical rendering records, by the same route `final_answer_from_traj` uses. This is also
required by **§2.0 provenance parity**: the repaired instrument must read the same channel
the frozen one reads, not a curated excerpt.

### A-1.4 `Item tracking` is automated and is excluded

The canonical rendering's `Item tracking: {...} → tracking=True` field is the output of
`build_audit.py::tracking_for_cell(task, condition, text, done)` — a function over the
answer text, i.e. **another instrument**, not a human label.

It is excluded for exactly the reason §6.1 already excludes Paper 1's rubric `score`:
validating an instrument against an instrument of uncharacterised quality measures nothing.
Only `CLASS` is ground truth. Three sources, three statuses, and they must never be
conflated: `CLASS` hand-derived; `score` LLM-judged; `Item tracking` automated.

### A-1.5 §6.2 step 4 was factually wrong, and the sealing claim is weakened

Step 4 asserted that `tracking_evidence.md` "is an immutable committed artefact" and is
"diffable against it and against the arXiv PDF, so a third party can check step 1". **Both
halves are false**, verified: neither copy is tracked by git or appears anywhere in history,
and Paper 1's PDF mentions the filename but contains none of the values
(`38,450`, `8,213.25`, `Backyard` all absent).

What actually supports temporal sealing, stated at its real strength and no higher:

* Paper 1's published Limitations section asserts the hand-coding, so the *claim* is
  date-stamped even though the *content* is not.
* File mtimes place the labels and their generator at 2026-08-29 22:10 and Paper 1's PDF at
  2026-08-29 22:46, against P3's first commit `f737d24` at 2026-09-12 01:21 — a two-week
  gap, and the PDF postdates the labels.
* This amendment commits and hashes the sealed set **before any repaired instrument
  exists**, which is the property K5 actually needs: the labels cannot change after repair
  results are seen.

What is **not** claimed: any cryptographic or third-party-checkable proof that the labels
predate P3-1. They lived in an uncommitted working tree until this commit. The sealed-set
argument rests on the three points above and must be written that way in the paper.

Hashes frozen here, SHA-256:

```
f00dbcdd33c944bf8429a40ee13d05160cdbac98997a2e9c879ede203b343531  build_final.py
0ee3f96fc74b80869b4f100a80eae73ebe17f7e8b3359d67ce6eddb9fffd6b8d  _final/tracking_evidence.md
39b4d779a66b40054fe9a31b396251c134e4892f1648b9b7bdd9c4fd50fc9d49  canonical tracking_evidence.md
```

### A-1.6 What did not change

No repair rule, no configuration, no primary quantity, no fixture, and no kill criterion is
altered by this amendment. §2 through §5 and §7 stand as frozen at `b6edbba`. K5 is
resolved as PASS; K4 remains open and is the gate that still matters.

---

## 10. Amendment A-2 — 2026-09-12, implementation and the synthetic gate

`scripts/p3_1_repair.py` implements §2 with gates enforced in the order
`parity -> synthetic -> run`; `run` refuses unless both prior gates are recorded as
passed. Configurations compose by patching attributes of the frozen module, and
**`FROZEN` patches nothing**, which is what makes the parity gate exact.

### A-2.1 Reading the frozen source corrected two descriptions. Neither rule changed.

**SPEC-NOTE 1 — "the ±120-character label window" does not exist.** §2 R-SCOPE and §5.1
inherited that phrase from the 0.6/0.7 specs. The frozen source has **four different
scopes**: `extract_money` scans `text[m.end():m.end()+100]` after a `\n\s*Breakdown`
cutoff; `extract_int` scans `+80`; `extract_entity` uses `text[m.start():m.end()+160]`
plus a line-delimited branch plus `text[m.end():m.end()+160]`; and only `extract_date`
calls `_window()`, which is itself **asymmetric** at `m.start()-40` to `m.end()+120`.

The R-SCOPE *rule* is unaffected — it replaces whatever local slice the frozen code took
with the whole answer — but the description of the baseline was wrong and is corrected
here. §5.1's `FILL(250)` separator remains valid, for a different reason than stated: the
largest forward scope is 160, not 120, and 250 still exceeds it.

**SPEC-NOTE 2 — "whole answer" means the entire string, not "after the label".** The
ambiguity is settled by the spec's own cross-reference, "This is the scope of rule R1",
and R1 was presence over the entire answer. The consequence is deliberate and was
predicted in §5.3: the pick becomes the first candidate in the document. S5 confirms it
empirically — `FROZEN` reports `2450.00` and matches, `R-SCOPE` reports `77.10` and does
not.

**A structural consequence found only at implementation, pre-registered here as a
prediction for the run.** Under R-SCOPE every label hit scans the same text and therefore
yields the same first candidate, so `found` is always unanimous and `_unique_or_none`
cannot abstain on disagreement: **R-SCOPE alone should drive `M1` to zero.** A label hit
is still required, so an empty candidate list still returns `None` and **`M2` rows cannot
be recovered**, which means the §2.1 leakage guard (K3) holds by construction rather than
by luck.

### A-2.2 K2 fired on S6 and S7, and S8 passed for the wrong reason

First run: 8 of 10 fixtures met their required outcome. S6 and S7 both produced
`FROZEN reported = None` instead of an over-long entity. Diagnosis, from the verbatim
`found` lists:

```
"Lodging site: Cedarline Lodge, amenities Pool, Wifi, Parking."
  found -> ['Cedarline Lodge, amenities Pool, Wifi, Parking',
          ': Cedarline Lodge, amenities Pool, Wifi, Parking']   -> None
"Lodging site Cedarline Lodge, amenities Pool, Wifi, Parking."
  found -> ['Cedarline Lodge, amenities Pool, Wifi, Parking']    -> reports
```

Extraction here is the frozen `extract_entity` **untouched**, because R-CMP changes only
the comparison. The implementation is therefore faithful and the **fixture text was
wrong**: it assumed `Label: value` yields one candidate. Per K2 the specification is
amended and the implementation is not: the colon is removed from S6, S7 and **S8**.

S8 is the more instructive failure. It *passed* its required outcome `(no match, no match)`
— but for the wrong reason, abstaining on self-disagreement rather than exercising R-CMP's
one-directional asymmetry. A suite that passes for the wrong reason is worse than one that
fails. After correction S8 reports `Harbour Point` under both configurations and genuinely
tests the asymmetry against gold `Harbour Point (North Wing)`.

Second run: **10 of 10**. Recorded as passed.

### A-2.3 A new sub-mechanism, pre-registered now: `M1c` self-disagreement

The diagnosis above is a finding, not only a fixture bug. On `Label: value` — the canonical
way an agent formats a structured answer — the frozen `extract_entity` emits two candidates
from two branches of the same function, differing only by a leading `": "`, and the
unanimity rule discards both. The disagreement is **internal to the instrument**: it is not
two world values, and it is not cross-component contamination.

`M1c` is defined here, before the run: an `M1` row in which the disagreeing values are
equal under R1 normalisation after stripping leading punctuation, i.e. the instrument
disagreed with itself about formatting rather than about content. It is reported alongside
`M1a` and `M1b` at run time.

Two constraints. First, `M1c` is **not** retrofitted onto 0.7: those counts are frozen and
`M1a` 13 / `M1b` 7 stand as published. Second, `M1c` is a candidate explanation for part of
the `M1b` set and must be reported as such only if the run supports it; the 0.7 refusal to
tell a single-cause story about `RECALL_MISS` continues to apply.

### A-2.4 What has NOT been verified

**The parity gate has not been run.** It requires `out/p3_0_recall_audit.jsonl` and the
Study 2 trajectories, which live on the host; locally it aborts with exit 3 as designed,
and `run` then refuses with exit 5. The synthetic suite exercises `FROZEN` only on ten
constructed strings, which is **weak** evidence of wrapper faithfulness. Until FROZEN
reproduces all 134 recorded `gold`, `reported` and `matched` values, the wrapper is
unverified and no repair number may be quoted.

The frozen extractor is not in this branch's working tree; it was read from git object
`3242c30:scripts/study2_hatd_extract.py` and, for the local synthetic run only, staged
outside the repository at `/tmp/p3_1_local/`. Nothing was checked out into `scripts/` and
no copy is committed, so the freeze at `3242c30` is untouched.

### A-2.5 What did not change

No repair rule, no configuration, no primary quantity, no kill criterion. §2.2's six
configurations, §3's quantities, §4's two-sided ordering analysis, §6's sealed protocol and
§7's K0/K1/K3/K4/K5 stand as frozen at `b6edbba` and amended at `fa4a642`. Only three
fixture strings in §5.2 are corrected, under the authority K2 grants.

---

## 11. Amendment A-3 — 2026-09-12, parity gate corrected before its first run

The host reported that `scripts/p3_1_repair.py` was absent; the file was pushed, and that
prompted a check of the parity gate against the actual 0.6 record **before** spending a
host run. Three defects were found in A-2's parity implementation. All three would have
produced a spurious ABORT or a false mismatch.

1. **Wrong field names.** `out/p3_0_recall_audit.jsonl` writes `component_id` and
   `extractor_match`; A-2 read `component` and `matched`.
2. **The audit file has no path fields at all.** A-2 read `r["traj"]` and `r["guest"]`,
   which do not exist. Paths must be rejoined on `(lane, task, leg)` from
   `out/study2_hatd_legs.jsonl` and `out/p3_0_extracted.jsonl`, exactly as
   `P3_0_IDENTIFICATION_AUDIT_SPEC.md` §3 requires and as 0.7's driver does.
3. **The comparison was reimplemented instead of wrapped.** A-2 rebuilt `match_one`'s
   logic with a broader `except Exception`. It now **imports the frozen `match_one`** from
   `study2_hatd_apply` and calls it unchanged, so under `FROZEN` the gate compares the
   frozen comparison against its own recorded output rather than against a look-alike.
   R-CMP can then only ever *add* a match. This is the §2.0 parity principle applied to
   the gate itself.

Two further changes, neither affecting any rule:

* Value comparison now uses `json.dumps(x, sort_keys=True, default=str)` on both sides,
  the idiom 0.7's faithfulness guard used, because the audit file was written with
  `default=str` and Decimals are recorded as strings.
* Archive reachability is checked as a separate step, so an unresolvable path reports as
  one legible error rather than surfacing as 134 value mismatches. This matters because
  the recorded `traj` paths and the recorded `gold_lock` path differ in their root
  (`/data2/hpcshared/Vinh/` against `/data2/hpcshared/Vinh-/`); 0.7 proved they resolve on
  the host, and if they ever stop resolving that is a finding about the archive, not a
  parity failure.

The synthetic gate was re-run after wiring in the frozen `match_one` and still passes
**10/10**. Parity remains **unrun**; §A-2.4 stands in full.

---

## 12. Amendment A-4 — 2026-09-12, the lineage did not contain the instrument it cites

The parity run aborted on the host with `ModuleNotFoundError: study2_hatd_extract`. The
cause is structural and predates P3-1, and A-2.4 recorded the symptom without drawing the
consequence — it noted the extractor was absent from this working tree and treated that as
a local quirk instead of realising the host would hit the same absence. That error cost one
host run and is recorded as such.

### A-4.1 The facts, after correcting a misread of my own evidence

An earlier check used the glob `*study2_hatd_extract*`, which also matches
`out/study2_hatd_extractor_lock.*` and wrongly suggested the script was on this lineage.
Checking the exact path instead:

| question | answer |
|---|---|
| commits touching `scripts/study2_hatd_extract.py` | exactly one, `3242c30` |
| branches containing `3242c30` | `generic-executor-phase1` only |
| `3242c30` an ancestor of this lineage | **no** |
| `4a2f6d6`, which is on this lineage | touched only `study2_hatd_extractor_lock.*` and `study2_hatd_legs.jsonl`, not the script |
| script present at `65f384d` or at `b6edbba..6e8a44a` | **no, at neither** |

So `out/study2_hatd_extractor_lock.json` on this lineage records
`extractor: scripts/study2_hatd_extract.py`, `git_sha: 3242c30a...` while the lineage
**does not carry that file**. 0.6 and 0.7 therefore did not run because the file was in the
tree; they ran because the host had it by some other route. `git checkout` does not delete
untracked files, so the instruction issued for this run cannot have removed the host's copy.

### A-4.2 Fix: the exact frozen blobs are now on the lineage

`scripts/study2_hatd_extract.py` and `scripts/study2_hatd_apply.py` are committed with
content taken from `3242c30` and `71a405d`. This is **not** a modification of the frozen
extractor: the blobs are content-addressed and verified byte-identical.

```
438a4eafb175785376fa714a3cbc1a8564f327ba  scripts/study2_hatd_extract.py   (= 3242c30:...)
cafd8a6252febd0bf2fb88b7376884a5c5ff0484  scripts/study2_hatd_apply.py     (= 71a405d:...)
```

Anyone can check with `git hash-object`. Two files were needed, not one: `match_one` lives
in the apply module, which is likewise off-lineage.

### A-4.3 A second hazard found while fixing the first, and now checked

`study2_hatd_apply` hardcodes two host roots and mutates the import path at module scope:

```
VINH        = Path("/data2/hpcshared/Vinh-/agent")
VINH_FROZEN = Path("/data2/hpcshared/Vinh/agent")
sys.path.insert(0, str(VINH / "scripts"))
```

This is the origin of the two-root discrepancy noted in A-3: recorded `traj` paths sit under
`Vinh/` while `gold_lock` sits under `Vinh-/`. Consequence: **"the frozen extractor" is not
automatically the copy in this tree.** This script imports `study2_hatd_extract` before
`study2_hatd_apply`, so the former is already in `sys.modules` when that path insert runs —
but that is import-order luck, not design, and import-order luck is exactly what cost the
previous run.

It is now a checked property. `check_provenance()` runs before any gate, recomputes the git
blob hash of every loaded frozen module, and aborts with exit 6 if either differs from
§A-4.2. Verified in both directions: it passes on the real blobs, and with a deliberately
wrong expected hash it fires and names the file it actually loaded. A guard that cannot fail
is not a guard.

### A-4.4 State

The lineage is self-contained: the synthetic suite now runs with no import-path help and
still passes **10/10**. Parity remains **unrun**; §A-2.4 stands. No repair rule,
configuration, quantity, fixture or kill criterion is changed by this amendment.

---

## 13. Amendment A-5 — 2026-09-12, the parity gate aborted on its own comparison

Parity aborted with exit 3 on the host at `fe845a9`:

```
ABORT: population disagrees with the frozen baseline
  - categories {'ABSENT': 61, 'MATCH': 20, 'RECALL_MISS': 39, 'VACUOUS_GOLD': 14}
      != {'MATCH': 20, 'RECALL_MISS': 39, 'ABSENT': 61, 'VACUOUS_GOLD': 14, 'ANOMALY': 0}
```

### A-5.1 The population does not disagree

Every category present matches the frozen baseline exactly — `MATCH` 20, `RECALL_MISS` 39,
`ABSENT` 61, `VACUOUS_GOLD` 14, summing to 134 over the audit's 134 lines. The sole
difference is that the frozen dict carries `ANOMALY: 0` while the observed dict has **no
`ANOMALY` key**. A count of zero and an absent key denote the same fact.

The defect was in the comparison, not the data: the observed counts were built by
incrementing, so a category with no rows never acquired a key, and the check then used
`!=` on whole dicts. The gate was aborting on its own representation choice.

This is a correction of code to the criterion, not of the criterion to the code. §3 requires
`ANOMALY = 0`; the data satisfies it, with zero rows so categorised; the gate evaluated a
satisfied criterion as violated.

### A-5.2 What the abort simultaneously confirmed

Three other guards did **not** fire, which is positive evidence:

- `len(rows) == 134` and `len(legs) == 57`.
- no leg lacked a traj/guest path, so the A-3 two-file rejoin is correct. The 57 legs are
  split 36 in `study2_hatd_legs.jsonl` and 21 in `p3_0_extracted.jsonl`; reading only one,
  as the pre-A-3 code did, would have failed here.

### A-5.3 `ANOMALY = 0` has teeth, and keeps them

Worth recording because §3 leans on it. 0.6 computes
`ANOMALY = extractor_match and not text_present` per row — the instrument matching where R1
cannot locate the gold, precisely the condition that would break `MATCH ⊆ R1-positive` and
collapse the denominator 59. So `ANOMALY = 0` is an empirical result over 134 rows, not a
constant true by construction.

The replacement compares per category over the union of keys with absent meaning zero, so
the assertion is preserved at full strength. Verified against three adversarial populations,
each of which must and does abort:

| perturbation | reported |
|---|---|
| `ANOMALY` 3, taken from `MATCH` | `ANOMALY 3 vs 0`, `MATCH 17 vs 20` |
| `RECALL_MISS` 39 to 38 | `RECALL_MISS 38 vs 39`, `ABSENT 62 vs 61` |
| a category 0.6 has never emitted | `NEW 1 vs 0`, `VACUOUS_GOLD 13 vs 14` |

The message now names the differing category and both counts instead of printing two dicts
for the reader to diff by eye — the reason this cost a round trip to identify.

### A-5.4 State

Parity is still **unrun** in substance: it aborted in the population precheck and never
reached the per-row faithfulness replay, so nothing is yet known about whether `FROZEN`
reproduces 0.6/0.7 output. Synthetic re-verified at **10/10** after the change. Input bytes
are pinned by the host's sha256: `p3_0_recall_audit.jsonl` `3afd3316…69b71`,
`p3_0_extracted.jsonl` `fb6d0891…6b6ce`, `study2_hatd_legs.jsonl` `c42b14ce…6da7d`. No
repair rule, configuration, quantity, fixture or kill criterion is changed.

---

## 14. Amendment A-6 — 2026-09-12, the measurement run is implemented

Both gates are green on the host at `c2d5612`: parity reproduced every gold, reported and
matched value of 0.6 across 134 rows over 57 legs with the archive reachable, and the
synthetic suite returned 10/10 with per-fixture reported values identical to the local run,
which also confirms cross-machine determinism.

`run` was a stub until now, and deliberately so — `f79042a` shipped the gates without the
measurement because implementing it then would have preceded the amendment recording
SPEC-NOTE 1 and 2. One consequence is worth stating because it is stronger than a promise:
both gates, **including the two defects in my own code that they exposed**, were fixed while
no result could exist. Not by self-discipline but by construction. The four repairs have been
frozen since `f79042a`; `run` only measures them.

### A-6.1 Two faithfulness gates inside `run`, before any repaired number is printed

Both are checks against numbers 0.7 already published, so neither is author discretion.

1. **Instrumentation is pass-through.** The cause taxonomy needs the `filtered` and
   `returned` value of every aggregation decision, so `_unique_or_none` is wrapped. The
   wrapper returns `fn(vals)` untouched, and `run` proves it by re-verifying that FROZEN
   reproduces 0.6's reported and matched values for all 134 rows **with instrumentation
   active**. Mismatch exits 7.
2. **The taxonomy reproduces 0.7.** Under FROZEN the decomposition must equal §1.1 as
   published — `RECALL_MISS`: `M1` 20 (`M1a` 13, `M1b` 7), `M2` 9, `M3` 5, `M4` 5;
   `ABSENT`: `M1` 25, `M2` 19, `M3` 2, `M4` 15. Mismatch exits 8, because every
   per-configuration delta would otherwise be a delta against an unknown baseline.

`K0` is then checked before anything else is read, and `K3` is evaluated over the FROZEN
`M2` set for all six configurations.

### A-6.2 0.7's classifier is imported, not reimplemented

`classify`, `gold_among` and `wilson` come from `p3_0_identification_audit`, for the same
reason `match_one` is imported: the taxonomy must be compared against 0.7's own classifier
rather than a look-alike of mine. That makes it load-bearing, so its blob is pinned beside
the other two — `86820e4a63870256154b7b71c5e1af4e7685bcf8` — and `check_provenance` now
covers three modules.

One decision worth recording: the classifier separates `M3` from `M2` by searching the text
for a label, so it is given **the text the extractor actually saw** — `chan_clean(answer)`
under R-CHAN, the raw answer otherwise. Under FROZEN that is the raw answer, which is what
0.7 classified.

`M1c` is implemented per A-2.3 as an orthogonal flag reported beside the `M1a`/`M1b` split,
which stands as published.

### A-6.3 Gate records now pin what they verified

`out/p3_1_gates.json` is untracked, so it survives `git checkout`. A bare
`{"parity": true, "synthetic": true}` therefore could authorise a run on a tree whose
instrument or inputs had changed — the same disease as A-4, one layer up. Each gate now
records the blob hashes of the three frozen modules and, for parity, the sha256 of the
three inputs; `run` recomputes and refuses on any difference.

Deliberately **not** pinned: this harness's own hash, which changes whenever the run path
is extended and is not what parity proved.

Verified against the real threat model — a gate recorded while a different module was
loaded, or against different input bytes — and each case refuses by name. The host's
existing bool-format record is rejected as unpinned, so **both gates must be re-run**.

### A-6.4 The invocation boundary is split; no quantity changes

`run` covers §3 on the development corpus. §4 ordering and §6 sealed validation are
separate invocations. This changes no quantity, no repair rule and no criterion; it
*strengthens* the once-only constraint by making the sealed corpus a distinct deliberate
run rather than a side effect of the development sweep.

### A-6.5 A refactor that requires parity to be re-run

Population loading is now shared between `parity` and `run`, so the sweep cannot operate
on a population differing from the one parity verified. The logic is unchanged, but because
a gate that has already passed was touched, parity must be re-run as a regression check
before `run`. The gate pin of A-6.3 forces this anyway.

### A-6.6 State

Nothing has been measured. `run` has never executed against the archive: locally there is
no archive, and on the host it is refused until both gates are re-recorded with dependency
pins. Synthetic re-verified 10/10 after all changes.

---

## 15. Amendment A-7 — 2026-09-12, K3's consequence was printed but not enforced

Both gates passed on the host at `4e31323` with dependency pins recorded, so `run` was
authorised. A final read of `cmd_run` before running it found that `K3` printed
"the run is VOID" and then **continued**: it computed the §3 quantities, wrote
`out/p3_1_run_development.json` and exited 0.

That is the wrong direction of the principle this document is built on. A voided run would
have left behind an artefact that later reads as a valid result, with the voiding recorded
only in console output nobody keeps.

`K3` now aborts with exit 10 and writes nothing, naming the configuration and the recovered
`M2` rows. `K0` is evaluated first and aborts with exit 9, because if the implementation is
unfaithful then `K3`'s verdict is not trustworthy either.

Exit codes, so an abort is never ambiguous: 3 population, 5 gates, 6 module provenance,
7 instrumentation not pass-through, 8 taxonomy does not reproduce 0.7, 9 `K0`, 10 `K3`.

No repair rule, configuration, quantity, fixture or criterion changes. Nothing has been
measured.
