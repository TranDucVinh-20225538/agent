# P4-D — Controlled Claim Challenge (design freeze)

**Status: FROZEN. Scientific design locked. Phase 1 not opened.**  
**File:** `P4_D_CCC_DESIGN.md` — **FROZEN**  
**Workstream:** `P4-D / Controlled Claim Challenge`  
**This file is not Phase 5 of P4-C2.** It does not reopen P4-B, P4-C v1, or P4-C2.

```
P4-B     CLOSED   positive-but-incomplete   immutable
P4-C v1  CLOSED   Metric v1 FAIL            immutable  (falsification)
P4-C2    CLOSED   DFC v2 FAIL               immutable  (H3 NOT_EVALUABLE)
P4-D     FROZEN   scientific design only    this file; no E worlds; $0
                  Phase 1 BLOCKED; no params_e / corpus / API
```

Six locks accepted. Two anti-repair points are part of the freeze:

- Instrument does **not** change: `score_v2` + wrapper keep C2 hashes.
- Estimand is the profile \(M=(\mathrm{Form},\;\mathrm{CC},\;\mathrm{Abs},\;I_{\mathrm{CC}})\). Do not redefine `Cov`.

**Name collision.** Older notes used “P4-D” for OSWorld / external CUA
transfer of a *passing* instrument. That workstream is **not** this
file. This P4-D is a new research question after C2. Do not shop
OSWorld here. Do not export C2’s H3 failure into an external suite.

**C2 is evidence, not a bug.** Flash confirmatory (`N_D = 30`):

| Object | Value | Reading |
|---|---|---|
| Form | 0.9333 | Declared `CLAIM:` channel is usable |
| CC | 0.9286 | Unique claims mostly matched gold |
| H1 / H2 / H4–H8 | PASS | 0 false HIT; C1 sensitivity; invariance; honesty |
| H3 | NOT_EVALUABLE | Designed C2-intended ∩ committed: n=8 < 10; miss_rate **0.0** (8/8 HIT) |
| Ordinary MISS | D15, D24 | Correspondence already produces MISS when the claim is wrong |
| GPT pair | 30/30 HIT | Descriptive only. Not a licence to switch primary |

C2 failed as a *validation protocol for negative claims*, not as an
interface. Agents did not manufacture enough committed errors on
C2-intended slots for H3’s 0.90 MISS quota. That quota mixed
**discrimination** (wrong unique claim → MISS) with **induced failure**
(those slots must mostly be wrong). P4-D keeps the first. It forbids
the second.

**Authorization for this file.** The six locks in §1 and the profile
in §2 are **accepted and frozen**. This freeze locks scientific design
only. It does **not** open Phase 1, does **not** author `params_e` or
worlds, does **not** spend API, and is **not** a corpus commit.

Forbidden until a later, explicit `GO TO P4-D PHASE 1`:

- modify `p4_instrument.py`, `p4_instrument_v2.py`, or the C2 wrapper
- edit B/C/D/Q/CQ/DQ/V/R worlds, gold, seals, or τ
- author E worlds, wordlists, or `generate_e.py`
- execute agents or spend API
- retune any regex, wrapper, or floor on C2 last-texts
- open P4-C2 Phase 5, Claude, or “H3 := HIT rate” repairs
- inject a wrong answer, ask the agent to err, or put gold in a prompt

**Frozen scientific lock (canonical).**

- **Target.** Observability of correspondence: whether natural-agent
  claims produce enough observations on both HIT and MISS for CC to
  be an interpretable quantity.
- **Unit.** Episode-component. `N = 30` Flash clusters `E01`–`E30`;
  10 families × 3 conditions (`plus`, `minus`, `pm`). Conditions are
  construction factors, not `N`.
- **Instrument.** Frozen C2 `score_v2` + wrapper. No new parser, no
  new anchors, no recovery.
- **Gold.** `L(world)` independent of last-text. A reuses
  `adjudicator_d.py`. `Y` does not read trajectory/traces.
- **Competence / anti-factory.** `plus`: HIT ≥ 0.90 when eligible
  n ≥ 10. No gold/competitor leakage. No MISS quota.
- **Observability.** \(I_{\mathrm{CC}}=1 \iff n_{\mathrm{HIT}}\ge 8
  \land n_{\mathrm{MISS}}\ge 8\). **No** gate \(\mathrm{CC}\ge 0.90\).
- **Descriptive only.** `n_MISS_designed` is not a gate. D cannot
  cheat by defining “MISS must come from a competitor.”
- **Profile.** \(M=(\mathrm{Form},\;\mathrm{CC},\;\mathrm{Abs},\;
  I_{\mathrm{CC}})\). Always report raw HIT / MISS / ABSTAIN /
  unscored. Form = interface compliance. CC interpretable iff
  \(I_{\mathrm{CC}}=1\). Abs = ABSTAIN rate.

---

## 0. What C2 already settled (do not re-ask)

1. A frozen DFC (`CLAIM:` line, `score_v2`, no anchors) can be
   **followed** (Form ≥ 0.80) and can **correspond** when a unique
   claim exists (H2 10/10 HIT; CC 0.93).
2. Wrong unique claims are already MISS (D15 `63.95` vs `37.55`; D24
   `0` vs `18`). V3 is not the blockage.
3. “C2-intended + committed → 90% MISS” is not a correspondence test.
   It is a task-failure quota. Natural Flash did the live join and HIT.
4. Bare gold without `CLAIM:` is `no_claim` (D07). Fail-closed. Do not
   relax that on C2 τ, and do not relax it here.

P4-D does **not** exist to make H3 pass. It exists because C2 left a
different question open.

---

## 1. Six locks (must be yes before corpus)

### Q1. Scientific question

**Lock.** P4-D tests whether **correspondence** under frozen DFC can be
**observed on both sides of the claim** — HIT and MISS — when the
*task distribution* varies **observability / decision difficulty**,
without changing the construct, the scorer, or inducing error.

C2 asked: *under natural CUA on a mixed C1/C2/ordinary slate, does DFC
yield a usable (Form, CC) and a C2-intended MISS quota?*  
Form and CC were usable. The MISS quota was not observable.

P4-D asks something C2 did not:

> Can we build **challenge conditions** such that a competent agent
> still produces correct committed claims on an easy condition, while
> the corpus as a whole has a **real chance** of incorrect committed
> claims — enough to interpret CC — without telling the agent to fail
> and without a D− MISS quota?

That is a question about **measurement observability**, not about
“making Flash look worse.”

**Not the question:** Is Flash reliable? Is GPT better? Can we pass
C2-H3 by writing harder C2-intended worlds? Should we patch `CLAIM:`?

**PASS claim (if later confirmatory passes the gates in §6):**

> Under frozen DFC, a challenge-conditioned corpus produced an
> interpretable CC (both HIT and MISS observed above floors) without
> collapsing easy-condition competence and without a negative-slot
> MISS quota.

**FAIL is allowed and is not a C2 patch ticket.** Too-weak challenge
(no MISS) or failure-factory (easy condition collapses) are both
scientific results. Do not then amp distractors or loosen the wrapper.

### Q2. Unit

**Lock.**

| Layer | Unit | What it is |
|---|---|---|
| Scored object `Y` | **episode-component** | one model, one world, one run, one `CLAIM` vs one gold |
| `N` | **30 Flash clusters** | `E01`–`E30`. Never 60 paired legs. GPT is paired, not `N` |
| Construction pairing | **family** `F01`–`F10` | three clusters per family: `plus` / `minus` / `pm` |
| Stratum | **condition** | report cells by condition; conditions are not `N` |

`N` is never families, never conditions, never HIT+MISS only, never
GPT. Families exist so a `minus` world is a **controlled variant** of
a `plus` world, not a random harder task.

One family = same `kind`, same locator `op`, same instruction
*template* (same identifying key language), **disjoint gold values**,
**disjoint in-world numbers/names**. `plus`/`minus`/`pm` differ only
in world geometry (where competitors sit, how close they are, how many
naive heuristics collide). Gold is always `L(world)` for *that* world.

### Q3. Negative opportunities without manufacturing errors

**Lock. Opportunity ≠ uptake ≠ quota.**

| Move | Allowed? | Why |
|---|---|---|
| Put a same-kind competitor in a readable file, not selected by `L` | Yes | Opportunity |
| Make the competitor *near* (same kind; money in a frozen magnitude band **or** entity/categorical string-near under a frozen rule) | Yes | Decision difficulty |
| Two candidates that a one-file heuristic would confuse; `L` still unique via the second source | Yes | `pm` |
| Put gold or competitor values in instruction, wrapper, or tool descriptions | **No** | Leak / teach |
| “The answer is not A”, “ignore the decoy”, “this is a trap” | **No** | Teaching the challenge |
| “Report a wrong value”, gold-as-wrong, or injecting A into the prompt | **No** | Manufacturing error |
| Gate: `minus` MISS rate ≥ 0.90 | **No** | Failure factory (C2-H3) |
| Post-hoc harder distractors after seeing Flash τ | **No** | Repair in place |

**Condition intents (construction, before τ):**

| Condition | Agent still does | Gold | What the world adds |
|---|---|---|---|
| `plus` | Read sources; emit `CLAIM:` | `L` = A | Competitors exist but are far (different key, different field, or out of the near-band) |
| `minus` | Same instruction template | `L` = B | A near competitor C ≠ B is visible; instruction still names the determining key, never B or C |
| `pm` | Same | `L` unique | ≥2 same-kind candidates a naive scan could take; join/second source determines one |

The agent always chooses the claim. `minus` gold is **B**, the live
determining value, not “we hope they say the distractor.” Committing C
is MISS because C ≠ gold, not because we wanted failure.

**Construction tests (Phase 1, $0), not agent tests:**

- `T_opp`: every `minus` and `pm` world contains ≥1 locked competitor
  `C` with `not v3_match(kind, C, gold)`, present in a non-hidden file.
- `T_far`: every `plus` competitor is outside the frozen near-rule.
- `T_near`: every `minus` competitor is inside the frozen near-rule.
- `T_prompt`: instruction, wrapper, and tool schemas contain neither
  gold nor any locked competitor.
- `T_L`: `L` unique on each world; `plus`/`minus`/`pm` of a family
  share `op` and template, not gold.

Near-rule (freeze numerically at Phase 1, **not** from C2 τ):

- `money_usd`: competitor in `[0.5·gold, 2.0·gold]` and not
  `v3_match` to gold (band is construction geometry, not a scorer
  change).
- `integer`: competitor in `{gold±1, …, gold±3}` excluding gold, or
  the same-kind count from a competing filter; pick one rule at Phase 1
  and hash it.
- `entity` / `categorical`: competitor shares the cover-token
  *namespace* (same roster file) but is a different locked string;
  no minimum edit distance that was fit on C2 names.

These tests guarantee **someone who mis-reads could commit C**. They
do not guarantee that Flash will. If confirmatory still yields too few
MISS, P4-D fails as an observability protocol. That is C2’s lesson,
honestly rerun, not C2 repaired.

### Q4. Independently determined gold

**Lock.** Same construct as C2, new ids.

- Gold = `L(world)`, locked before any E last-text exists.
- `L` is mechanical (join / sum / count / live-not-stale / three-file
  select). No LLM judge. No gold field in the world the agent can
  `read_file`.
- Worlds contain no `gold` key. `world_meta.json` is hidden from tools
  as in C2.
- Independent adjudicator **A** (reuse frozen `adjudicator_d.py` by
  hash; it has no per-id branch). Traces + world, ignores last-text,
  does not call `score_v2`. Conservative `INDETERMINATE` stays.
- `Y` does not read traces, worlds, A, gold, or `task_id`.
- New dialect / new cover tokens. Confirmatory ids `E*`. Intersection
  with `{B*, C*, D*, Q*, CQ*, DQ*, V*, R*}` is empty.

**Scorer.** P4-D does **not** write a new locator. It uses frozen
C2 DFC as a black box:

- `p4_instrument_v2.py` sha256
  `a87ac636a729d99852eb837583b24bce372ff49c196f2be7e39e4f750622fcf3`
- wrapper sha256
  `2a028f2b95a7bc1ce815ac4b01dcb1fc7c8814ded7a5f3f38489d4ffe70e8e08`

The *new* object is the **challenge protocol** (conditions, families,
estimands, gates), sealed as its own Phase-2 JSON. Calling this a
“new instrument” means new **measurement design**, not a new regex.
A new `CLAIM` parser would be a C2 repair. Forbidden.

### Q5. What counts as eligible MISS

**Lock. Two layers; only the first is `Y`.**

**Instrument `Y` (unchanged DFC).** Unique parseable `CLAIM`
remainder; `v3_match` → HIT; else MISS. ABSTAIN is not MISS.
Garbage claims (`CLAIM: 0` when gold is 18) are MISS. That is
correspondence, not a designed-competitor check.

**Eligible MISS for the observability floor `I_CC`:** `Y = MISS` on a
Flash confirmatory cluster. Not restricted to `minus`/`pm`. Not
restricted to “committed value equals locked C”. Restricting the floor
to designed competitors would discard D15-style errors and would push
authors to farm competitor-uptake. Report **as descriptive**:

- `n_MISS` — all instrument MISS
- `n_MISS_designed` — MISS whose committed value `v3_match`es a locked
  competitor

Gate on `n_MISS`. Do not gate on `n_MISS_designed`.

**Not eligible:** ABSTAIN, unscored, GPT legs, C2 τ, Phase-3 E pilot τ,
`Y = HIT`.

### Q6. Gate that D is not a failure factory

**Lock.** A failure factory is a corpus whose easy condition no longer
supports competence, or whose pass rule is “the model must be wrong.”

C2-H3 was the second. P4-D forbids it.

**Factory-fail (any one fails the protocol as factory, not as “Flash
is bad”):**

| Id | Criterion |
|---|---|
| F1 | `plus` ∩ committed ∩ A=SUCCESS HIT rate **< 0.90** with n_eligible ≥ 10 (easy competence collapsed) |
| F2 | Any instruction/wrapper/tool schema contains gold or a locked competitor |
| F3 | A gate of the form “`minus` MISS ≥ 0.90” exists in the confirmatory spec (this freeze forbids writing one) |
| F4 | `Form` on `plus` < 0.80 while overall Form is “saved” by other strata (channel broken where the task is easy) |
| F5 | Authors added trap language after this freeze (“avoid decoys”, “not the first number”) |

**Weak-challenge fail (observability, not factory):**

| Id | Criterion |
|---|---|
| W1 | `I_CC = 0` after confirmatory: `n_HIT < 8` or `n_MISS < 8` on Flash `N = 30` |

W1 is an allowed FAIL. If confirmatory shows **high `plus` HIT** and
`minus`/`pm` still **all HIT**, do **not** increase distractors.
The conclusion is:

> W1 — challenge weak / correspondence remains unobservable under
> this protocol.

The opposite, if `n_HIT ≥ 8` and `n_MISS ≥ 8` **and** `plus` keeps
competence, is the first empirical basis for:

> CC is empirically two-sided observable under a controlled
> natural-agent protocol.

That sentence is independent of C2. It is not “H3 passed.”

**Anti-factory pass requires F1–F5 pass.** Interpretable CC requires
W1 pass (`I_CC = 1`). Protocol PASS = anti-factory ∧ `I_CC` ∧ the
ordinary DFC gates (0 false HIT, working-span invariance, Form overall
≥ 0.80, honesty, frozen hashes, E-only ids). **No CC ≥ 0.90 gate.**
CC is a profile coordinate, not a leaderboard quota. D does not aim
to prove Flash reliable. It aims to prove CC can be observed on
both sides.

---

## 2. Public outcome profile (not a scalar)

v1 `Cov` is **not** a P4-D public name. Under DFC,
`Form = (HIT+MISS)/N` already. Reintroducing `Cov` would relabel Form
and undo C2’s terminology lock.

**Locked public vector:**

\[
M = (\mathrm{Form},\; \mathrm{CC},\; \mathrm{Abs},\; I_{\mathrm{CC}})
\]

with the cell counts always printed: `n_HIT`, `n_MISS`, `n_ABSTAIN`,
`n_unscored`.

\[
\mathrm{Form} = \frac{\#\{\text{parseable unique CLAIM}\}}{N},\quad
\mathrm{CC} = \frac{\#\mathrm{HIT}}{\#\mathrm{HIT}+\#\mathrm{MISS}},\quad
\mathrm{Abs} = \frac{\#\mathrm{ABSTAIN}}{N}.
\]

\[
I_{\mathrm{CC}} = \mathbf{1}[n_{\mathrm{HIT}} \ge 8 \;\wedge\; n_{\mathrm{MISS}} \ge 8].
\]

- `CC` is **undefined** if `HIT+MISS = 0`.
- If `CC` is defined but `I_CC = 0`, print CC as **descriptive,
  not interpretable**. Do not use it as a reliability ranking.
- Optional `DH = HIT/N` only with Form, CC, **and** `I_CC = 1`.
- Also report `M` **by condition** (`plus` / `minus` / `pm`) as
  strata. Stratum CC with n_MISS = 0 is descriptive.

ABSTAIN is missing correspondence measurement. Never convert it to HIT
or MISS. Never call Form coverage.

---

## 3. Challenge invariance (construct, not difficulty theatre)

Let `T` map a `plus` world to a `minus` or `pm` world in the same
family.

**`T` may change:** which rows are near, how many same-kind values a
single file contains, which object is the live determining row, join
fan-in.

**`T` may not change:** `score_v2`, wrapper bytes, gold-lock
procedure, A, CLAIM syntax, fail-closed causes, primary model, floors
in this freeze.

**`T` may not add:** evaluative warning, gold, competitor literals,
“use CLAIM” beyond the frozen system wrapper (already on every
cluster, identical).

Invariance tests after τ (same family as C2 H4, not a new parser):

- Working-span distractor lines that are **not** `CLAIM:` lines must
  not change `{status, committed}`.
- Rewriting the `CLAIM` remainder **may** change `Y` (named test).
- Applying `T` in construction is **not** scored as an invariance
  transform of τ; it is a new episode with a new gold.

---

## 4. Programme (no phase after 0 is authorized here)

| Phase | Spend | Action | Gate |
|---|---|---|---|
| 0 | $0 | This file | Human: `GO TO P4-D PHASE 1` |
| 1 | $0 | `params_e` + `generate_e` + E01–E30 + gold from `L` | Construction tests in Q3–Q4; no observations; no agents |
| 2 | $0 | Seal hashes; Q3 synthetics on DFC (HIT/MISS/C3/C4/working vs CLAIM-span) | Seal PASS; Q3 6/6; F3 still absent |
| 3 | small API | Flash on **one** family (3 clusters) | Scorable last-text; **not** an `I_CC` peek used to retune near-rules |
| 4 | confirmatory API | Flash+GPT × 30 | §6 gates; primary Flash `qwen/qwen3.8-flash` |

Phase 5 (third model) only if Phase 4 protocol PASS, separately
authorized. Not a C2 continuation.

Do not pool C2 D01–D30. Do not pool a Phase-3 E family into `N`.

**Primary model stays Flash.** GPT may again Form=1, CC=1; that does
not move the gate. Do not switch after τ.

---

## 5. What Phase 1 must look like (still not authorized)

When (only when) Phase 1 is authorized:

- New cover-token dialect, disjoint from Q/V/R/B/C/D.
- Quotas: 10 families × 3 conditions = 30. Kinds: freeze a quota in
  `params_e` (suggested, not copied from a C2 peek: money 12 / integer
  9 / entity 5 / categorical 4, allocated across families).
- Families 10, ops mixed (Locate / Compute / Reconcile / Filter /
  Tally / Multi-step) without dropping Tally because C2 Tally MISS’d
  once.
- No `C1-intended` / `C2-intended` slot names. Those names carried
  H3’s quota. Conditions are `plus` / `minus` / `pm` only.
- Authors of E worlds must not open C2 `*_tau.txt` while writing
  instructions. C2 numbers in this memo are diagnosis, not a palette.

---

## 6. Confirmatory gates (written now, not opened)

Floors on **Flash** clusters, `N = 30`. NOT_EVALUABLE on a required
floor fails the protocol. Do not lower after seeing `I_CC`.

| Gate | Name | Pass | Fail policy |
|---|---|---|---|
| G0 | Frozen DFC | v2 + wrapper hashes match C2 seal | FAIL (this is a C2 repair in disguise) |
| G1 | False HIT | 0 HIT on new Q3 C3/C4 analogues **and** on `c3_drop_claim` / `c4_markup` of natural τ | FAIL scorer misuse |
| G2 | `plus` sensitivity | `plus` ∩ A=SUCCESS ∩ Y≠ABSTAIN HIT rate ≥ 0.90; **n ≥ 10** | Factory (F1) |
| G3 | Two-sided observability | `n_HIT ≥ 8` **and** `n_MISS ≥ 8` (`I_CC = 1`) | Weak challenge (W1). **Not** a `minus` MISS quota |
| G4 | Working-span invariance | status+committed unchanged under working-span C5/C6 | FAIL parser fragility |
| G5 | Form | overall Form ≥ 0.80 **and** `plus` Form ≥ 0.80 | FAIL interface; not named coverage |
| G6 | Honesty | print `M`, cells, strata; CC interpretable iff `I_CC`; ABSTAIN shown | FAIL if hidden |
| G7 | Anti-factory | F2–F5 hold; no `minus` MISS quota in the runner | FAIL factory |
| G8 | Anti-circularity | E-only ids; C2/B/C τ not scored | FAIL |

**P4-D protocol PASS** iff G0–G8 are PASS.  
`CC` itself has **no** threshold.

---

## 7. Explicit non-goals

- Not P4-C2 Phase 5.
- Not “fix H3.”
- Not submit-tool v3 (C2 H5 passed; that branch is not forced).
- Not OSWorld.
- Not ranking Flash vs GPT.
- Not mining D15/D24 τ to clone those mistakes into E.
- Not lowering C2 floors retroactively.

---

## 8. Single recommendation

**SCIENTIFIC DESIGN FROZEN. STOP.**

Phase 1 is **not** opened. No `params_e`, no corpus, no worlds, no
API, no scorer copy-with-edits. The next human line, if any, is
`GO TO P4-D PHASE 1`.

C2 remains the historical result that DFC can be used and can
correspond, and that a negative *quota* on natural success is the
wrong gate. P4-D is a new question: observability of two-sided
correspondence under controlled natural-agent claims. It is not
the continuation of C2.
