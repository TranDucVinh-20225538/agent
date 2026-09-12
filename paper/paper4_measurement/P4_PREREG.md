# P4 — Observation-grounded correspondence (design-only pre-registration)

**Status: Phase-2 gold-lock FAIL 2026-09-12. n_locked = 3 < N_A = 11.
Freeze commit c35e828. Instrument unmodified. No agent validation.**
Authored 2026-09-12. Construction and Q scoring the same day.

P1–P3 stay frozen. This file does not edit them, does not enlarge `R`, does
not open G3 or the sealed corpus, does not reuse the 134 Study 2 rows, the
four-task C7 support, or the 16/28 cohort as validation, and does not ship
R-AGG / R-SCOPE / R-CHAN / ALL as a method.

P1–P3 are **design requirements**, not a validation set. Numbers cited below
are already published there; they constrain what P4 is allowed to measure.
They are not re-estimated.

---

## 1. Construct

Reliability, for P4, is **observation-grounded correspondence**: whether the
evidence an agent placed in a declared observation channel corresponds to an
independently locked determining state.

It is not a formula. It is a claim about a triple `(episode, gold, channel)`.

**Unit.** The atomic scored object is one **episode-component**: one model,
one task, one protocol run, one determining component. **`N` is the number of
independent task-clusters**, defined in §4. `N` is never legs, never
model–task pairs, never components, never controls, never observations.
Agents are not units. Legs, pairs, and raw texts are reported; they are not
`N`.

**Target.** Outcome correspondence under observation, not process reliability
and not “trustworthiness.” P4 does not score the path, the tool trace, or
whether the guest world actually changed. It scores whether the instrument,
reading only the declared channel, recovers the locked gold when the evidence
is there, withholds a pass when it is not, and stays put under irrelevant
variation. That is a validity property of a measurement, not a character
property of an agent.

**Observation conditions.** The scored channel is the last assistant text of
the episode (for designed clusters: the authored last-response). Screenshots,
harness logs, role metadata, and guest dumps are **not** in the channel.
Gold is locked before any observation in that cluster is written or scored.
Anchors (locator phrases) are part of the gold specification, authored from
the cluster’s instruction only, and hashed with gold. They are inputs, not a
hidden per-task table inside the instrument.

**Not success rate.** A rubric score `S` can stay high when gold is absent
from the channel (Study 1 Type B; Study 3: hundreds of money candidates and
none equal gold). `S` can move when tracking does not. Completion is a
separate classifier. STS is a separate, already-frozen construct from Paper 2.
P4 does not replace `S` or STS, does not average them, and does not treat
agreement with `S` as validity. Correspondence can be HIT while `S` is low,
and ABSTAIN while `S` is 100. Those are not contradictions; they are why P4
exists.

What P1–P3 require of this construct, and forbid mistaking for findings:

* recoverable evidence can be missed (39/59 on the development instrument);
* fail-closed aggregation can discard gold it already collected (13 M1a, 7 of
  them majority);
* a later layer cannot repair an earlier abstention (R-CMP inert);
* no tested repair dominated (R-AGG +8 correct / +18 wrong; R-SCOPE destroyed
  14/20 MATCH);
* a channel intervention can invert an ordering by destroying one lane
  (`n_eff = 1`);
* a locked grounded rule recovered 9/30 hand-written label components.

P4 is the instrument that is supposed to survive those failure modes. It is
not a retune of the instrument that produced them.

---

## 2. Measurement contract

Every arrow is a map with a validity condition. If the condition fails, the
episode-component is not scored as HIT. Cause codes are part of the output.

```
episode (or designed last-response)
        ↓  [V1 observation]
declared channel text
        ↓  [V2 evidence]
observable candidates
        ↓  [V3 correspondence]
committed value or abstention
        ↓  [V4 coverage]
eligible / ineligible for a decision
        ↓  [V5 measurement]
{HIT, MISS, ABSTAIN} + cause
        ↓  [V6 estimate]
cluster-level property tests, then summaries
```

**V1 — Observation.** The instrument reads exactly the declared channel. It
does not consult gold, `S`, STS, the trajectory body, or the task id as a
branch key. Markup spans `<function…>`, `<tool…>` and their closed forms are
removed as a **definition of the channel**, not as a repair of FROZEN.
An unterminated opener makes the channel indeterminate: **ABSTAIN
(`channel_indeterminate`)**. The instrument does not delete to end of text.

**V2 — Evidence.** The located unit is the **newline-terminated line**
containing an anchor hit, not a `.!?` sentence (decimal money must not
split). Candidates are taken from the **union of such lines**, after
casefold and whitespace collapse.

Kind parsers are **new**, declared with the implementation hash, and are
not commit `3242c30` and not `R`. `money_usd`: a match must carry a `$`
prefix **or** a decimal point (optional thousands-commas; optional `$`
with `.` + 1–2 decimals). Bare digit runs are not money — otherwise the
integer overlap rule in this paragraph is empty. `integer`: digit runs
that do not overlap a money match. `entity` / `categorical`: the remainder
of the located line **after the first anchor hit on that line**, stripped;
that remainder is one candidate, not a search for gold. An anchor that is not a literal substring of that cluster’s
instruction is a construction void, not a scored miss. No anchor hit →
ABSTAIN (`no_anchor`). No candidate in the located lines → ABSTAIN
(`absent`). Whole-answer first-hit is not a rule. Window-from-`found[0]`
is not a rule.

**V3 — Correspondence.** Equivalence is the Paper 2 kind rule already frozen
as a matching protocol: `money_usd` within $1 or same whole dollar;
`integer` exact; `categorical` / `entity` casefold-and-strip exact. No
containment repair. No ±1 grouping as an equivalence for identification
(it is not transitive). Gold is compared only after a value is committed.

**V4 — Coverage.** A decision is eligible only if identification returns
exactly one equivalence class. Zero classes: ABSTAIN (`absent`). Two or more:
ABSTAIN (`ambiguous`). The instrument never plurality-picks, never returns
`found[0]` under dissent, and never converts ABSTAIN into MISS. ABSTAIN is a
valid measurement outcome.

**V5 — Measurement.** If a unique value is committed: HIT iff it matches gold
under V3, else MISS. HIT is the only pass. MISS is a committed wrong.
ABSTAIN is not a pass and is not a committed wrong.

**V6 — Estimate.** No scalar is allowed to hide ABSTAIN inside a success
rate. Episode status over determining components: HIT iff every component is
HIT; MISS if any component is MISS; else ABSTAIN. Cluster summaries, reported
separately and never mixed: sensitivity `HIT/(HIT+MISS)` among non-ABSTAIN;
abstention `ABSTAIN/all`. These are instrument diagnostics. They are not a
leaderboard and not ΔSTS.

The P4 instrument is this contract. It is not R-AGG, R-SCOPE, R-CHAN, R-CMP,
ALL, `R`, or FROZEN with a different `LABELS` table.

---

## 3. Designed HIT / MISS controls

The six properties are **necessary conditions** on the instrument. Each
cluster instantiates all six with authored observations against the same
gold. A property fails the cluster if the observed status is not in the
allowed set. One cluster-level fail fails that property for qualification.
There is no threshold tuning.

| ID | Control | Designed observation | Required status |
|---|---|---|---|
| C1 | True success + valid evidence | Unique gold in an anchored line; no distractor of that kind in located lines | **HIT** |
| C2 | True failure + valid evidence | Unique wrong value of the same kind in an anchored line; gold absent from channel | **MISS** |
| C3 | Success + evidence deleted | Same text as C1 with the gold span removed; anchors still present | **ABSTAIN** (`absent` or `no_anchor`), never HIT |
| C4 | Failure + misleading evidence | Agent-wrong committed context; gold string appears only inside deleted markup, a stale/draft disclaimer, or an unanchored line | **not HIT** (MISS or ABSTAIN) |
| C5 | Irrelevant inject | C1 text plus a same-kind distractor on an unanchored line, and a different-kind token anywhere | **HIT**, identical cause to C1 |
| C6 | Stability | Two C5 variants whose irrelevant spans differ and whose anchored line is identical | **same status and same committed value** |

C4 is the coincidence trap Study 3 named: gold present in the file is not
gold reported. C5–C6 are invariance, not extra recall. If C5 is implemented
by widening scope until the distractor is swallowed, C4 or C2 will fail on
the same cluster; that is the point of bundling all six on one gold.

Qualification **PASS** for the instrument requires C1–C6 on every
qualification cluster (`Q01`–`Q06` only). Any C1 miss, C2-not-MISS, C3-HIT,
C4-HIT, C5 change, or C6 disagreement **blocks freeze**. Freeze is not
reached by dropping a property. The freeze procedure is §5. Confirmatory
`N` is §4.

---

## 4. Corpus and `N`

`N` counts **task-clusters**. It does not count legs, model–task pairs,
components, C1–C6 rows, or observations. Two models on one gold are one
cluster. Six controls on one gold are one cluster.

Two cluster kinds exist. They are not pooled.

| Kind | What one cluster is | What it is for |
|---|---|---|
| **Control-cluster** | One instruction + one locked determining component (id, kind, gold, anchors) + one C1–C6 last-response bundle | Qualification and confirmatory instrument validity |
| **Agent-cluster** | One task specification + one locked gold (same component schema) + models named before any run | Transfer to naturally occurring last-responses, only if §9 opens it |

G0/G1, a two-model ranking roster, and ΔSTS are **not** part of either
cluster. Those were the P3 comparative gate. P4 does not inherit that
experiment, its 16/28 shortfall, or its `n ≥ 20` as a ranking threshold.
P4 **does** keep the P3 unit lesson: independent unit = task-cluster, locked
before outcome.

### 4.1 Independence and exclusion

Forbidden as any P4 validation object, including “same task, new answers”:

* Study 2: 134 leg×component rows; 57/171 legs; the 25-task universe in
  `out/paper2_cell_order.json`;
* C7 four: `counterfactual-f010`, `preference_inference-f014`,
  `retrieval-f002`, `retrieval-f009`;
* P3 slate of 28 and the 16 gold-locked survivors;
* Paper 1 / sealed cells (`paper1_replay.json` ten tasks);
* P3-1 fixtures S1–S10 and their gold values;
* `preference_inference-*`; id prefixes or category
  `situated_action` / `long_horizon` / `cua_only` / `hard_app`;
* `contradiction-f024`.

P1–P3 numbers may be cited only as design requirements (§1).

### 4.2 Control-clusters: selection without outcomes

**Minimum confirmatory `N_V = 20` control-clusters.** This is the
validation `N`. It is locked before any cluster is authored. It is reachable
because the clusters are authored, not guest-probed. Qualification is
separate and smaller (`n_Q = 6`, §5). `n_Q` is not added into `N_V`.

Kind quota on the 20, locked now: `money_usd` 8, `integer` 6, `entity` 3,
`categorical` 3.

IDs and roles, pre-assigned: `Q01`–`Q06` qualification; `V01`–`V20`
held-out; `R01`–`R10` construction reserve (same-kind replacement only).
Reserve may replace a voided ID **before freeze**, in ID order, for
construction defects only. After freeze, unused reserve is discarded.
If after reserve `n_Q < 6` or `N_V < 20`, **construction FAIL**: stop.
Do not reshuffle roles. Do not add `V21`. Do not promote a forbidden ID.

Each control-cluster is selected by ID order, not by how easy C1 looks.
Held-out `V01`–`V20` are authored and hashed **before** the instrument is
frozen, then sealed. No observation in `V*` is read to edit anchors, gold,
parsers, or rules.

**Independent V authorship (safeguard, locked before any last-response).**
One operator must not freely author `V*` in the Q dialect. `V01`–`V20`
last-responses are a pure function of `construction/params_v.json` and
`construction/generate_slate.py`. Those two files, plus disjoint word-lists
`wordlists_{q,v,r}.txt`, are authored and hashed **before** any observation
text exists. Q uses only the Q word-list and `params_q.json`. V uses only
the V word-list and `params_v.json`. The generator has no per-id branch.
Hand-editing a V last-response after generation voids the seal. Reserve
`R*` uses `params_r.json` and the same generator. Details:
`construction/P4_AUTHORSHIP.md`.

**Q vs V dialect split**, locked now so held-out is not the same template
with new numbers:

* Q markup: well-formed `<function …></function>` only.
* V markup, disjoint: `<tool …></tool>`, unterminated `<function`, and a
  `sandbox` wrapper. Each V cluster uses exactly one of these three, cycling
  in ID order.
* Q cover tokens and V cover tokens are disjoint word-lists, hashed with
  the slate.
* C5/C6 fillers are on **separate lines** from the anchored line.

Construction checks (mechanical, before any score): every anchor is a
≥2-token literal substring of that cluster’s instruction; gold is not a
substring of any anchor; anchors do not appear in C4/C5 irrelevant spans;
C1 entity/categorical remainder equals gold exactly; bundle has all six
controls. Scoring is deterministic. No LLM judge.

### 4.3 Agent-clusters: reachability locked before spend

P3’s 4-family pool arithmetic, after Study 2, sealed, preference, `f024`,
and the 28-slate, leaves **at most ~12** leftover IDs. `N_A = 20`
agent-clusters is therefore **not reachable** without relaxing §4.1.
This file does not relax §4.1.

**Phase-2 leftover listing, materialised 2026-09-12 (IDs/categories only).**
From the pinned 184-task file minus §4.1: **L = 11.** Gate L ≥ 8 **PASS**.
**N_A = min(L, 20) = 11**, declared before gold-lock. Lexicographic leftover:
`contradiction-f013`, `contradiction-f015`, `contradiction-f016`,
`contradiction-f021`, `contradiction-f023`, `counterfactual-f008`,
`counterfactual-f014`, `retrieval-f020`, `retrieval-f032`,
`retrieval-f033`, `retrieval-f035`. Record: `construction/out/phase2_leftover.md`.

**Phase-2 gold-lock, materialised 2026-09-12.** Task-side instruction +
rubric criteria only. No guest probe. No agent observation. No I1. No
G0/G1. Uniform lock: unique P4 `money_usd` XOR unique `.txt`/`.m3u`
basename (`entity`). Integers in `llm_judge` prose never lock. All 11
attempted; none added or dropped for usefulness. **n_locked = 3**
(`retrieval-f020`, `retrieval-f032`, `retrieval-f033`). Survivors **3 <
N_A = 11**. Gate **FAIL**. Do not lower `N_A`. Do not add IDs. Do not
spend API budget. Construction fail of Phase 2. Seal:
`construction/sealed/PHASE2_GOLD_LOCK_SEAL.json`
(`phase2_gold_lock_sha256 =
138a0b43582fa24c58f25b571ce6bee67aec6b71e965bc1af2c0327f756db854`).

Models named before any run: **Flash and GPT**, one uninjected leg each.
A third model does not increase `N_A`. Completion (`DONE`) is not required.
The scored channel is last assistant text at `DONE` or `max_steps`.

Phase 2, if opened, is transfer. It is not `N_V` and not a replacement
wave of C1–C6 authorship.

---

## 5. Qualification protocol

**Object.** `Q01`–`Q06` authored control-clusters. Not agent-generated.
Kind quota: `money_usd` 2, `integer` 2, `entity` 1, `categorical` 1.

**Purpose.** Answer only: does the implementation of §2 realise C1–C6 on
the qualification bundle? Not sensitivity. Not ranking. Not transfer.

**Order.**

1. Author `Q*` and `V*` and `R*` as the slate. Seal `V*`. Do not score `V*`.
2. Construction-audit the Q spec-traces: applying §2 by hand to each Q
   observation must yield the required C1–C6 status. Fail → reserve, no
   code.
3. Implement §2. Hash is not yet freeze.
4. Score Q **once** against the observations. Code must match the
   spec-trace on `{status, cause, committed value}` for every Q control.
5. **Mismatch to spec-trace** = implementation bug. Fix code to match §2,
   re-score Q. This is the only allowed re-score. The observations do not
   change. The spec does not change.
6. **Match to spec-trace, but a required C1–C6 status fails** — cannot
   occur if step 2 passed. If it does, construction was wrong: **stop**.
   Do not retune §2.
7. **Change §2 because Q “looks bad”** = tuning. Forbidden. A dated
   amendment that changes §2 **voids Q**. New Q clusters from reserve
   roles are then required; the old Q observations never become
   validation.

**Freeze.** The instrument is frozen when all of these exist in one commit:
hashed §2 implementation, hashed Q observations, Q PASS on every control
of all 6 clusters, hashed sealed `V01`–`V20` (unscored). Freeze hash is
the object later scoring must name.

A **single** Q control failure after bugfix-to-spec **blocks freeze**.
No property may be dropped. No Q cluster may be excluded because it failed.

---

## 6. Validation protocol after freeze

Opened only on freeze. One pass.

* No instrument change after freeze. No parser, window, line rule,
  unique-or-abstain, or cause-code edit.
* No new anchors or gold values after any validation observation is read.
* No task-specific branch (`if task_id == …`, per-id `LABELS`, per-id
  anchors inside code). Anchors are cluster inputs, processed uniformly.
* No post-hoc exclusion by P4 status. Construction voids before freeze
  only. After freeze, an execution failure is an absent observation:
  reported, not MISS, not replaced, not dropped to beautify `N`.
* `V01`–`V20` scored once against the freeze hash. Failures are the
  result.
* Phase 2, if opened, uses the same freeze hash. Gold and anchors for
  agent-clusters are locked before trajectory 1. Last-responses may be
  transformed **mechanically** into C3–C6 variants (delete gold span;
  wrap gold in V-dialect markup; append unanchored distractor line;
  second distractor line). Those transforms are hashed before trajectory 1.
  They are not rewritten after seeing statuses.

---

## 7. Primary estimands and pass/fail

P4’s primary claim is **measurement validity**, not model ranking.
No leaderboard. No `argmax`. No ΔSTS. Sensitivity and abstention are
reported and are not optimised.

**Primary — confirmatory control-clusters (`N_V = 20`).**

Let `H(p, c) ∈ {0,1}` be 1 iff property `p ∈ {C1,…,C6}` holds on
cluster `c` under the freeze hash.

* Estimand: hold-rate `r_p = (1/20) ∑_c H(p,c)` for each `p`.
* **PASS** iff `r_p = 1` for all six `p` (120/120 controls).
* **FAIL** iff any `H(p,c) = 0`. Reported as a negative result.
  The instrument is not shipped. §2 is not patched and re-scored on `V*`.

Diagnostics, not gates: sensitivity `HIT/(HIT+MISS)` on C1∪C2 observations;
abstention `ABSTAIN/all` on C3∪C4. No threshold may be introduced to
convert a FAIL into a “mostly holds.”

**Secondary — agent transfer, only if §4.3 opens Phase 2.**

On each agent-cluster, the natural last-response `τ` and its pre-hashed
C3–C6 transforms are scored. Independent of P4’s commit: `gold_in_clean(τ)`
is literal gold-string presence in the V1-cleaned channel.

* **E1 False HIT (primary for transfer).** Among `{τ}` with
  `gold_in_clean = 0`, HIT count = 0. Any such HIT → transfer FAIL.
* **E2 Invariance.** Status and committed value on `τ` equal those on the
  C5 and C6 transforms. Any change → transfer FAIL.
* **E3 Natural C1.** Eligible if gold lies in an anchored line of `τ` and
  no other same-kind candidate lies in located lines (line/anchor geometry
  only, not the commit). If eligible count `< 5`, **NOT EVALUABLE**, not
  FAIL, not PASS. If ≥ 5, all must be HIT or transfer FAIL.
* **E4 Natural C2.** Eligible if a unique non-gold same-kind value lies in
  an anchored line and gold is absent from the cleaned channel. Same
  evaluability floor of 5; else NOT EVALUABLE.

E3/E4 floors are locked before any `τ` is read. Do not hunt eligible
clusters. Do not rank Flash against GPT. Per-model tables are descriptive.

---

## 8. Kill criteria

**P4 unsuccessful (instrument not shipped), reportable as negative/null:**

* Q does not PASS (§5), after the one allowed bugfix-to-spec;
* construction FAIL (`n_Q < 6` or `N_V < 20` after reserve);
* `V*` FAIL on any property (§7);
* freeze hash does not exist.

**Stop spending compute (API/HPC):**

* any unsuccessful bullet above, before Phase 2 starts;
* Phase 2 not opened (`L < 8`, or gold-lock survivors `< N_A`);
* cumulative Phase-2 API spend reaches **$400**;
* 2027-03-01 AoE arrives without freeze + `V*` scoring **started**.

**Calendar kill (P4 dies as a program):** no hashed freeze and no `V*`
scoring started by **2027-03-01 AoE**. “Started” = freeze hash exists and
the `V01`–`V20` scoring job has been launched against that hash.

**Report as negative/null, do not rescue:** Q fail; `V*` property fail;
Phase 2 E1/E2 fail; Phase 2 not opened for reachability. Do not lower
`N_V` or `N_A` after seeing statuses. Do not fold in 134 / C7 / 16/28 /
sealed. Do not enlarge `R`. Do not reopen G3. Do not ship a P3
configuration. Do not convert ABSTAIN into a success numerator.

If P4 dies or is null, P1–P3 remain the publishable result.

---

## 9. Budget-aware execution (~$400)

Do not assume the $400 must be spent. Qualification and `V*` scoring are
local and **$0 API**.

| Phase | What | Spend |
|---|---|---|
| 0 | This spec; slate authorship; construction audit | $0 |
| 1 | Implement §2; Q once (+ one bugfix re-score if needed); freeze | $0 |
| 1b | Score sealed `V01`–`V20` once | $0 |
| 2 | Leftover listing + gold-lock | $0 API (probe only) |
| 2b | Flash + GPT, one uninjected leg, `max_steps = 40`, last text scored with or without `DONE` | only if 1b PASS and §4.3 opens; cap **$400** |
| 2c | Claude | only if 2b complete and remaining budget can cover ≤ 3 legs without exceeding $400 |

**Claude’s pre-specified external-validity question, and no other:**
Study 2 Claude last-responses were often non-terminating and markup-heavy.
E-ext: on those ≤ 3 leftover clusters, does E1 still hold (false HIT = 0)
on Claude last-text? Not a cluster for `N_A`. Not a ranking slot. If
remaining budget cannot cover 3 Claude legs, E-ext is **NOT EVALUABLE**.

Stop rules inside 2b: record spend every 5 legs; if projected completion
of the declared `N_A` × 2 models exceeds the remainder, **stop** and
report incomplete transfer. Incomplete is not a lowered `N_A`. Do not
start Claude to “use up” the remainder.

---

## 10. Threats to validity

* **Authored last-response vs natural trajectory output.** C1–C6 on `V*`
  test the protocol on designed text. They do not prove the same statuses
  on CUA traces. Phase 2 exists for that gap and may never open (§4.3).
  A PASS on `V*` with Phase 2 unopened is instrument validity, not CUA
  field validity.
* **Anchor dependence.** Correspondence is locator-constrained. An agent
  who states gold without the instruction’s phrase will ABSTAIN. That is
  fail-closed, and it can inflate ABSTAIN on natural text (E3 not
  evaluable). It is not licensed as “the agent failed.”
* **Synthetic controls.** Disjoint Q/V dialects mitigate template copy.
  They do not create linguistic diversity of real agents. Overfit to line
  layout remains possible.
* **Model-specific formatting.** Flash/GPT/Claude emit different markup
  and termination behaviour. The channel cleaner is a finite token list.
  Runtime paraphrases of tools are not enumerable (P3-1). Those become
  `channel_indeterminate` or uncleaned distractors, not a reason to
  enlarge the token list after seeing `τ`.
* **Cluster dependence.** Multiple observations in one control-cluster
  share gold; independence is across gold-locks. Agent-clusters that share
  an app or schema are still one-ID-one-cluster; they are not assumed i.i.d.
* **ABSTAIN inflation.** Unique-or-abstain will abstain under ambiguity.
  That can look like a cautious high-quality instrument while never HIT-ing
  on natural text. E1/E2 still bind. E3 NOT EVALUABLE must be reported,
  not filled by loosening locators.
* **Construct validity.** P4 measures observation-grounded correspondence
  under a declared channel. It does not measure guest-world correctness,
  process reliability, or rubric `S`. Agreement with `S` or STS is not
  validity.
* **Generalisation beyond the selected family.** Control-clusters are
  synthetic typed fields. Leftover MyPCBench 4-family, if Phase 2 opens,
  is still one benchmark. Other CUA suites are out of scope unless a new
  amendment names them before any of their traces are read.

---

## 11. P4 readiness checklist

Items are PASS only if the artefact exists and is hashed, or the rule is
locked in this file. This checklist is scored **now**, before any
validation run.

| Item | Status now |
|---|---|
| Construct frozen | **PASS** (§1) |
| Measurement contract frozen | **PASS** (§2, line-located V2; money requires `$` or a decimal) |
| Qualification controls frozen | **PASS** (C1–C6; §5) |
| Corpus independent | **PASS** as a rule (§4.1); leftover L = 11 materialised |
| `N` frozen | **PASS** (`N_V = 20` control-clusters; `n_Q = 6`; `N_A` rule §4.3) |
| Estimands frozen | **PASS** (§7) |
| Pass/fail criteria frozen | **PASS** (§7) |
| Kill criteria frozen | **PASS** (§8) |
| Budget cap frozen | **PASS** ($400 Phase 2 only; $0 until `V*` PASS) |
| Independent V authorship | **PASS** (`construction/P4_AUTHORSHIP.md`; generator is V author) |
| Construction audit | **PASS** (`construction/out/construction_audit.md`; Q spec-traces only) |
| `V*` sealed | **PASS** (`construction/sealed/V_SEAL.json`; unopened this step) |
| §2 implemented | **PASS** (`instrument/p4_instrument.py`) |
| Q scored once | **PASS** (`construction/out/q_qualification.md`) |
| Bugfix-to-spec | **not used** |
| Q qualification | **PASS** (6/6 clusters, 36/36 controls) |
| Freeze | **PASS** (`c35e828db89a9c7eb9d479601215a29221f5d744`) |
| `V*` scored once | **PASS** (`construction/out/v_qualification.md`; 20/20, r_p=1) |
| Agent validation | **not opened** (gold-lock survivors 3 < N_A 11) |
| Phase-2 leftover listing | **PASS** (L = 11 ≥ 8; N_A = 11 declared) |
| Phase-2 gold-lock | **FAIL** (n_locked = 3 < N_A = 11; seal `PHASE2_GOLD_LOCK_SEAL.json`) |

**Checklist verdict: gold-lock FAIL. Phase 2 closed. $0 API.**

---

## 12. Phase-2 gold-lock (closed)

**2026-09-12 V* scoring: PASS.** One pass against freeze
`c35e828db89a9c7eb9d479601215a29221f5d744`. Instrument hash
`c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59`
unchanged.

**2026-09-12 Phase-2 leftover listing: L = 11 ≥ 8.** N_A = 11 declared.

**2026-09-12 Phase-2 gold-lock: FAIL.** 11/11 attempted from task-side
specification. 3 locked (entity file basename). 8 unlockable (no unique
allowed-kind value, or nonunique file). Survivors 3 < N_A 11. Agents not
run. API spend $0.

**Stop.** Do not lower N_A. Do not add IDs. Do not open Flash/GPT/Claude.
Do not spend the $400.
