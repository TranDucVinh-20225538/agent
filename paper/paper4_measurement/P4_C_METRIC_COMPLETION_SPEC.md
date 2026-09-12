# P4-C — Metric completion specification (design freeze)

**Status: PHASE 3 FLASH PILOT PASS. P4-B immutable. Phase 4 BLOCKED.**  
Spec authored 2026-09-12. Phase 1–2 recorded 2026-09-12. Phase 3 Flash C01–C03 run 2026-09-12. `N_C`, floors, and G1–G6 are unchanged.

This file opens a **new workstream**. It does not amend `P4_PREREG.md` §2,
does not edit `p4_instrument.py`, does not change P4-B E1–E4, gold, worlds,
anchors, transforms, or quotas, and does not re-run P4-B.

```
P4-B  CLOSED   positive-but-incomplete validation   immutable
P4-C  OPEN     metric completion spec               this file; no τ yet
```

P4-B record (do not reinterpret):

| Item | Value |
|---|---|
| Status | `NULL_E3_NOT_EVALUABLE` |
| E1 / E2 | PASS / PASS |
| E3 / E4 | NOT_EVALUABLE / NOT_EVALUABLE |
| 40-run last-text | HIT 5 / MISS 5 / ABSTAIN 30 (all `no_anchor`) |
| Execution | 40/40 `DONE` |
| Commits | results `4c3d14bc`; post-hoc `bc947d5f` |
| Instrument sha256 | `c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59` |

P4-B’s 30/40 `no_anchor` is a **finding**, not a bug to patch. It must not
select P4-C tasks, anchors, or a coverage threshold.

---

## 0. The hard construct question (answered before any new τ)

**Is ABSTAIN missing measurement, or evidence of unreliability?**

It is **missing correspondence measurement**. It is **not** evidence that
the agent failed the computer-use task, and it is **not** silent success.

| Object | What it is | What ABSTAIN means |
|---|---|---|
| Trajectory / execution | Whether the CUA loop finished and what the world/tools show | Independent of P4. `DONE` ≠ HIT |
| Observable evidence | Candidates in the **declared channel** (last assistant text) | `no_anchor` / `absent` / `ambiguous` / `channel_indeterminate`: **no committed value** |
| Correspondence | Committed value vs independently locked gold | Defined only when a value is committed (HIT or MISS) |
| Reliability estimate | Population quantities below | Must **display** ABSTAIN via coverage; must not convert it to HIT |

So:

- At the **instrument** (V1–V6): ABSTAIN = the channel does not support a
  unique determining claim. Missing measurement.
- At a **leaderboard scalar that is only HIT/N**: that scalar estimates
  *demonstrated last-text correspondence*, which **treats ABSTAIN as
  not-HIT**. That is a different population quantity. It may be reported
  only **with** coverage. It is not “the agent is unreliable” and not
  “the task failed.”

P4-C does **not** choose a formula because 30/40 abstained. The
decomposition below is locked now, from the construct, not from that rate.

---

## 1. Research objective

Can a **frozen** observation-grounded correspondence instrument yield a
**valid, usable** measurement of agent reliability under natural
computer-use last-text — without collapsing execution, evidence,
correspondence, and the estimate?

Success is P4-C-Metric v1 passing the gates in §11 on a **new** corpus.
Failure is a scientific result. Do not iterate the scorer until a number
looks good.

---

## 2. Instrument vs metric (do not patch V1–V6)

| Layer | Object | Frozen? |
|---|---|---|
| Correspondence instrument | `p4_instrument.py` V1–V6 | **Yes** — same hash as P4-B. No edit to cut abstention |
| P4-C-Metric v1 | Estimators on `{HIT,MISS,ABSTAIN}` + independent GT | Specified **here**, implemented after this freeze, hashed before any P4-C agent τ |

If a later programme needs a different channel, locator, or V2 rule, that
is **Instrument v2**: new construct note, new hash, new Q/V, new
validation. It is not a P4-B or P4-C hot-fix.

---

## 3. P4-C-Metric v1 (locked before data)

**Inputs (one episode-component).** Frozen instrument output
`Y ∈ {HIT, MISS, ABSTAIN}` on last assistant text against locked
`(kind, gold, anchors)`.

**Independent unit.** Task-cluster. `N_C` clusters. Two models on one
cluster are **paired observations**, not `N_C + 1`.

**Primary model** for cluster-level gates: Flash
(`qwen/qwen3.8-flash`). GPT (`openai/gpt-5.5`) is paired / descriptive.
Do not rank models as a P4-C gate.

### 3.1 Episode state (A)

Unchanged from V5: `HIT` | `MISS` | `ABSTAIN` + cause.  
ABSTAIN is never rewritten to HIT or MISS.

### 3.2 Cluster-level estimands (B)

Let `i = 1…N_C` index clusters and `m ∈ {flash, gpt}` a confirmatory leg.
For cluster-level Flash quantities, use the Flash confirmatory episode
(not the P4-B pilot).

| Symbol | Name | Definition (Flash confirmatory, unless noted) |
|---|---|---|
| `Cov` | Observation coverage | `(# HIT + # MISS) / N_C` |
| `CC` | Conditional correspondence | `HIT / (HIT + MISS)` among clusters with `Y ∈ {HIT,MISS}`; **undefined** if `HIT+MISS = 0` |
| `Abs` | Abstention | `# ABSTAIN / N_C` |
| `DH` | Demonstrated-HIT rate | `# HIT / N_C`  (`= Cov × CC` when `CC` is defined) |

Paired GPT analogues are reported, not gated.

**What they estimate**

- `Cov`: probability that natural last-text **commits** a determining value.
- `CC`: probability that a **committed** last-text matches gold (specificity-of-commit among commits; not task success).
- `DH`: probability that last-text both commits and matches gold.

`DH` treats ABSTAIN as not-HIT. That is **missing demonstrated
correspondence**, not an execution fail.

### 3.3 Scalar (C) — only with coverage

**Primary public report is the pair `(Cov, CC)`.**  
If a ranking demands one number, report

```
DH (Cov = ·, CC = ·)
```

Never `DH` alone. Never `HIT / (HIT+MISS+ABSTAIN)` presented as “accuracy”
without naming it `DH`. Never `CC` presented as coverage.

**Rejected (not the metric):** `Reliability = HIT / N` as if ABSTAIN were
task failure; `Reliability = HIT / (HIT+MISS)` as if abstention were
outside the population; any post-hoc weighted blend fit to P4-B’s 25%
commit rate.

### 3.4 Natural C1 / C2 correspondence (gated)

Defined in §5–6. Not the same as `CC` on all committed clusters.

---

## 4. Sample, quotas, floors (locked now)

```
N_C = 30
```

IDs `C01`–`C30`. Reserve `RC01`–`RC10` same-kind replacement **before**
Phase-2 seal only. After seal, unused reserve discarded. Do not add `C31`.
Do not drop a scored ID after seeing τ. Do not import `B01`–`B20`.

**Family quota (5 each = 30)**

| Family | n |
|---|---|
| Locate / retrieval | 5 |
| Compute | 5 |
| Reconcile | 5 |
| Filter | 5 |
| Tally / count | 5 |
| Multi-step inspect | 5 |

**Kind quota**

| kind | n |
|---|---|
| `money_usd` | 12 |
| `integer` | 9 |
| `entity` | 5 |
| `categorical` | 4 |

Entity filename cap: at most one of five entity golds.

**Design-time C1 / C2 slots (world properties, before any agent)**

| Slot | n | World property (locked in params, not in τ) |
|---|---|---|
| C1-intended | 10 | Unique live determining cell; no equal-salience stale twin on the same field |
| C2-intended | 10 | A unique **wrong** same-kind value is at least as salient as gold (stale “live” label, or a distractor on the instruction’s named object) |
| Ordinary | 10 | Remainder; still T1–T8 |

These slots are **task design**, not labels on Y. Do not relabel slots
after seeing HIT/MISS.

**Analysis floors (do not lower)**

```
n_C1_eligible ≥ 10
n_C2_eligible ≥ 10
```

Eligibility: §5. If a floor is missed, that gate is **NOT EVALUABLE**
(P4-C incomplete / fail under §11), not a reduced floor.

---

## 5. Independent ground truth vs measurement

Two channels. No arrow from GT into P4 evidence extraction.

```
WORLD + tool trace  →  adjudicator A  →  GT ∈ {SUCCESS, FAIL, INDETERMINATE}
last assistant text →  frozen V1–V6   →  Y  ∈ {HIT, MISS, ABSTAIN}
```

**Adjudicator A (frozen in construction; no `task_id` branch; does not
call `p4_instrument.score`; does not read last assistant text).**

Read-only worlds (P4-C default):

| GT | Mechanical rule |
|---|---|
| SUCCESS | Gold-bearing **live** object was `read_file`d and the gold token appears in that tool result; for Reconcile, the stale object is not the only determining read |
| FAIL | A unique non-gold same-kind token from a **competing** object was read as the last determining read, and the live gold-bearing object was never read |
| INDETERMINATE | Otherwise (including Compute/Tally where gold is not a stored cell: SUCCESS iff both source files were read **and** the tool traces contain every summand/member used by `L`; else INDETERMINATE — not FAIL) |

A is trajectory-grounded **execution** adjudication. It is allowed to be
conservative (many INDETERMINATE). It must not be tuned on P4 Y.

**C1 eligible (analysis)** iff all of:

1. Cluster is in the C1-intended slot **or** GT = SUCCESS;
2. GT ≠ FAIL;
3. Last-text **geometry** (not Y): gold string lies in an anchored line
   and no other same-kind candidate lies in located lines
   (same geometry as P4-B E3, applied to P4-C τ only).

(3) uses τ because C1’s definition includes “final observation contains
valid determining evidence.” It does **not** use the HIT label. Do not
flip (3) after seeing Y.

**C2 eligible (analysis)** iff all of:

1. Cluster is in the C2-intended slot **or** GT = FAIL;
2. Last-text geometry: unique non-gold same-kind value in an anchored
   line; gold absent from V1-cleaned channel (P4-B E4 geometry).

**Required measurement on eligible sets**

- C1 eligible → `Y = HIT` (else G2 fail)
- C2 eligible → `Y = MISS` (else G3 fail)

Do not manufacture eligibility by editing gold/anchors after τ.

---

## 6. Designed controls (qualification, $0, before agents)

Authored last-responses on a **new** Q/C slate (`CQ01`–`CQ06`), not P4-B
B-worlds, not Q01–Q06 copies. Same C1–C6 contract as `P4_PREREG.md` §3
against **frozen** `p4_instrument.py`. PASS 6/6 required before P4-C
Phase 1 worlds are sealed for agents.

Transforms C5/C6/Chan on natural τ: same `transforms` family as P4-B
(new file `transforms_c.py`, no per-id branch, hashed at P4-C seal).
Do not copy P4-B τ into C5 tests.

---

## 7. Observation channel

Unchanged: last assistant text. Strip well-formed function/tool markup
(V1). No screenshots, clicks, tool traces, or GT in the scorer.

Agent prompt: ordinary task instruction only. No P4, anchors, gold, or
“put the answer next to the fee name.”

Execution status (`DONE` / `max_steps` / exception) is stored and
**never** mapped to Y.

---

## 8. Anti-circularity / authorship

- This memo is the Phase-0 freeze for P4-C **design**. Corpus hashes
  appear at Phase-2 seal (not yet).
- Outcome-blind construction. Not investigator-blind: authors have seen
  P4-B.
- New dialect: `wordlists_c.txt` pairwise disjoint from Q, V, R, **and
  B**. Generator `generate_c.py` with **no** `if cid == "Cxx"`.
- Forbidden: P4-B IDs, MyPCBench leftovers, Q/V/R cover tokens, P4-B
  gold strings, shopping public suites until a task locks.
- T1–T8 as in P4-B memo (gold not in instruction; no toy basenames;
  ≥3 same-kind distractors; no observations field; two sources; etc.).
- Do not use P4-B HIT/MISS/ABSTAIN tables to pick C01–C30 families
  (e.g. do not drop Tally because P4-B Tally was 8/8 abstain). Family
  quota is locked in §4 **including** Compute and Tally.

---

## 9. External validity

P4-C worlds remain authored desktop fixtures (mail, csv, notes, ics,
html) so gold can lock from `L`. They are **not** P4-B worlds and not a
promise of OSWorld. Multi-step inspect (5 clusters) requires ≥3
environment objects on the gold path. If a later amendment names a
public CUA suite, it must do so **before** reading that suite’s traces,
in a different file.

---

## 10. Statistical analysis (locked)

**Primary (cluster, Flash confirmatory):** false-HIT count on
gold-absent last-text; C1 HIT rate; C2 MISS rate; `Cov`; `Abs`; `CC`
when defined.

**Secondary:** GPT pair; family; kind; percentile bootstrap at the
**cluster** (resample 30 clusters; keep both model legs together).

Do not inflate `N_C` to 60. Do not pool P4-B.

---

## 11. Acceptance (locked now; not from P4-B 25% coverage)

P4-C-Metric v1 **PASS** iff **all** of G1–G6 PASS. NOT EVALUABLE on a
required floor **fails** P4-C (incomplete), except G5 is a coverage
gate, not a C1 floor.

| ID | Gate | PASS iff |
|---|---|---|
| G1 | False HIT | 0 HIT among Flash confirmatory τ with gold absent from V1-clean; and 0 HIT on designed C3/C4 |
| G2 | C1 sensitivity | `n_C1_eligible ≥ 10` and HIT rate on that set ≥ **0.90** |
| G3 | C2 discrimination | `n_C2_eligible ≥ 10` and MISS rate on that set ≥ **0.90** |
| G4 | Invariance | Flash confirmatory: status and committed value unchanged on C5 and both C6 transforms of each τ that has a last-text |
| G5 | Coverage | Flash `Cov ≥ 0.50` |
| G6 | Scalar honesty | Published numbers are `(Cov, CC)` and optional `DH (Cov, CC)`; no table that treats ABSTAIN as HIT |

**G5 justification (use case, not P4-B):** a practical reliability
**score** must commit on at least half of clusters under the primary
model. 0.50 is the minimum “more often committed than silent.” It is
**not** `1 − 30/40`. If G5 fails, that is a validity/usability fail of
this instrument+channel on this corpus — report it; do not retune V2.

Designed C1–C6 on `CQ*` must PASS before agents (pre-gate).

---

## 12. If PASS

Freeze and write (later, not now):

- `P4_METRIC_SPEC.md`
- `P4_METRIC_VALIDATION.md`
- `P4_METRIC_LIMITATIONS.md`

Hash estimator code + this spec + corpus seal + 30-cluster results.

---

## 13. If FAIL

Stop. Name the failed G. Do not patch V1–V6, gold, or floors. Do not
open P4-D in this file.

---

## 14. Phases (agents only after seal)

| Phase | Work | API |
|---|---|---|
| 0 | This spec | $0 |
| 1 | `CQ*` + `generate_c` + worlds + gold from `L` | $0 |
| 2 | Qualify/seal `C01`–`C30`; hash A, transforms_c | $0 |
| 3 | Flash pilot `C01`–`C03`, cap $30, observability only | if Phase 2 PASS |
| 4 | Confirmatory: Flash+GPT × 30 = 60 legs; cap remaining of **$400** P4-C (new licence, not P4-B reopen) | if Phase 3 PASS |
| 5 | Claude only if Phase 4 complete and remainder covers 3 legs; not in `N_C` | optional |

**Do not execute Phase 3–5 until Phase 0–2 are committed PASS.**  
This commit is Phase 0 only.

Kill: hash drift; gold/instrument edit; projected spend > cap; protocol
ambiguity that would change Y’s definition.

Models: Flash then GPT, `max_steps = 40`, same tool-loop family as P4-B
Phase 4 (ordinary instruction; last-text channel). No QEMU required for
the licensed loop; do not silently switch harness after τ.

---

## 15. Internal consistency audit (10 questions)

1. **Construct?** Observation-grounded correspondence on
   `(episode, gold, last-text)`, plus named estimators `Cov`, `CC`, `DH`.
   Not process reliability, not `S`, not STS, not execution `DONE`.
2. **Observed?** Last assistant text only.
3. **Measured?** `Y ∈ {HIT,MISS,ABSTAIN}` via frozen V1–V6; then cluster
   estimators in §3.
4. **Population quantity?** `Cov` = P(commit); `CC` = P(match | commit);
   `DH` = P(commit and match). Unit = P4-C task-cluster under the named
   protocol.
5. **HIT / MISS / ABSTAIN?** HIT = unique committed match; MISS =
   unique committed mismatch; ABSTAIN = no unique commit. ABSTAIN is
   missing measurement at V5; in `DH` it is not-HIT and must be visible
   as `1 − Cov`.
6. **C1 independently?** Design slot + adjudicator A (no last-text, no
   `score()`) + τ geometry without using the HIT label (§5).
7. **C2 independently?** Design slot or GT FAIL + E4-style geometry (§5).
8. **Unit?** `N_C = 30` clusters. Paired models ≠ extra N.
9. **Thresholds?** G1–G6 in §11. C1/C2 floors 10. `Cov ≥ 0.50`. C1 HIT
   rate ≥ 0.90. C2 MISS rate ≥ 0.90.
10. **Falsifiers?** Any G fail; floor miss; false HIT; C5/C6 change;
    publishing `DH` without `Cov`; editing P4-B; lowering floors after τ.

**Unresolved (must not be papered over)**

- A is conservative on Compute/Tally (many INDETERMINATE). Floors might
  miss even with N=30; that fails P4-C rather than loosening A after τ.
- No second human author. Dialect split (`wordlists_c`) ≠ investigator
  blindness.
- Authored fixtures ≠ OSWorld. External validity is limited by §9.
- G5 = 0.50 is a use-case stipulation; a different product (archive-only
  instrument) would choose another number **in a different spec**, not
  after seeing P4-C `Cov`.
- C1 analysis step (3) still inspects τ geometry. Fully output-blind C1
  is only the design slot; the correspondence test cannot ignore the
  channel.

**Consistency:** G2/G3 require floors that P4-B missed; that is the
point of a new corpus, not a repair of B. Family quota still includes
Compute/Tally so P4-B’s abstention pattern cannot delete families.
Instrument hash unchanged so G5 failure cannot be “fixed” by V2 edits
inside P4-C.

---

## 16. Phase 0 gate

PASS iff this file exists, answers §0 and §15, locks `N_C`, quotas,
floors, G1–G6, ABSTAIN treatment, and forbids agents until Phase 2 seal.

```yaml
phase: 0
workstream: P4-C
status: SPEC_FROZEN
next: PHASE_1_CONSTRUCTION
next_status: BLOCKED
N_C: 30
c1_floor: 10
c2_floor: 10
coverage_gate: 0.50
instrument_modified: false
p4b_modified: false
agents_run: 0
api_spend_usd: 0
```

---

## 17. Phase 1 gate (construction; $0)

PASS iff CQ01–CQ06 hit C1–C6 against frozen `p4_instrument.score`, and
C01–C30 lock gold from `L` with T1–T8, quotas, and disjoint C dialect.
No agents. No instrument edit. No P4-B edit.

```yaml
phase: 1
workstream: P4-C
status: PASS
next: PHASE_2_QUALIFICATION
next_status: BLOCKED
N_C: 30
construction_n_pass: 30
cq_pass: 6
instrument_modified: false
p4b_modified: false
agents_run: 0
api_spend_usd: 0
```

---

## 18. Phase 2 gate (seal; $0)

PASS iff C01–C30 locker-replay gold, T1–T8, quotas, CQ pre-gate 6/6, and
hashed `adjudicator_c.py` + `transforms_c.py` with no per-id branch.
No agents. No natural-τ scoring. Corpus not rewritten. RC unused discarded.

Seal: `construction/sealed/P4C_PHASE2_SEAL.json`

```yaml
phase: 2
workstream: P4-C
status: SEALED
next: PHASE_3_FLASH_PILOT
next_status: BLOCKED
N_C: 30
n_pass: 30
instrument_modified: false
p4b_modified: false
corpus_modified: false
agents_run: 0
api_spend_usd: 0
instrument_sha256: c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59
adjudicator_c_sha256: 595b02f50a2ad968b56051bb4d0b8d8686697a29a94ac39afaf2e1d53b97a8b2
transforms_c_sha256: e6a000c62413be724d6452c27dbf755defac8baa173ed146ea7d092778d2bcd3
clusters_sha256: bd30104becac546169ce62f921e6079a3df758a9a0fccf95106f9aa59060352f
worlds_sha256: b39c1e082a21c18f4a2b105e94586b3d0584b57af6c3a6904e50fa903ef75c4b
gold_spec_sha256: dfe9e6a308bc5b21e59c8ca27f2182b7e7773441ba185012371dc2fc1fd8c2d8
```

---

## 19. Phase 3 gate (Flash observability; C01–C03)

PASS iff ≥2 of 3 Flash legs produce a last-text the frozen instrument
scores (HIT/MISS/ABSTAIN all count), spend ≤ $30, corpus/instrument
unchanged. Not confirmatory `N_C`. G1–G6 not estimated. Phase 4 remains
BLOCKED until separately authorized.

```yaml
phase: 3
workstream: P4-C
status: PASS
next: PHASE_4_CONFIRMATORY
next_status: BLOCKED
model: qwen/qwen3.8-flash
pilot_ids: [C01, C02, C03]
n_scorable: 3
api_spend_usd: 0.00113
G1_G6: not_estimated
instrument_modified: false
p4b_modified: false
corpus_modified: false
```

Observability (not a gate, not a reason to edit V1–V6 or C04–C30):
C01 HIT; C02 ABSTAIN `no_anchor`; C03 MISS (entity remainder after
anchor). Adjudicator A: SUCCESS on all three traces. `DONE`/`SUCCESS` ≠ HIT.
