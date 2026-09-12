# P4-B pre-observation anti-circularity / task-design audit

**Audit date:** 2026-09-12  
**Workstream:** P4-B (independent CUA validation corpus)  
**Decision:** **GO WITH DOCUMENTATION**  
**Agents run during this audit:** 0  
**API spend during this audit:** $0  
**Frozen artifacts modified:** none

This audit asks whether P4-B was designed to obtain favorable results for
the frozen measurement instrument. Absence of all human bias is not
claimable. The supported claim is:

> Task construction was outcome-blind and independently constrained,
> rather than fully investigator-blind.

---

## 1. Scope and frozen-state declaration

**In scope:** design memo, Phase 1 construction, Phase 2 qualification,
`params_b.json`, `generate_b.py`, `qualify_b.py`, `transforms_b.py`,
`wordlists_{q,v,r,b}.txt`, sealed clusters/worlds/gold, frozen
`p4_instrument.py`, freeze commits and hashes.

**Out of scope / not performed:** Flash/GPT/Claude, E1–E4 scoring, any
OpenRouter call, corpus regeneration, `generate_b.main()`,
`qualify_b.py` (it rewrites the seal), instrument edits, adding/dropping
clusters.

**Frozen state used as ground truth (must still hold):**

| Object | Evidence |
|---|---|
| Instrument freeze | commit `c35e828db89a9c7eb9d479601215a29221f5d744` (2026-09-12 16:39 +0700) |
| `p4_instrument.py` sha256 | `c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59` |
| Phase 1 construction PASS | commit `54b48b7c012be5a2fd0fb181cab0a12367339a12` (2026-09-12 21:33 +0700) |
| Phase 2 seal PASS | commit `78cf36ca2ad7bba1447c0fc15acca794b8d2cd2d` (2026-09-12 21:37 +0700) |
| Seal file | `construction/sealed/P4B_PHASE2_SEAL.json` (`gate=PASS`, `agent_run=false`, `api_spend_usd=0`) |
| Clusters sha256 | `8c061c093185787cf98919ac14590064025e7f41283df11a9b0cb0285df0bed5` |
| Worlds sha256 | `9db6cbb94b933d0c7098dfcc0e257042e58a2c021870561966b5fe91e0e626b3` |
| Gold spec sha256 | `0e334b2c9a8ecae0998abd91476fc7ece67f2c732790ab4c987c25a745d1004f` |
| Transforms sha256 | `7a5ee93261d067d140681a8c539809d52725880ecd7f97c25e0749ef5af15ae6` |

This audit re-hashed those objects and replayed locator `L` on disk
worlds. All five hashes still match the seal. Locker replay matches
sealed gold on **20/20**.

Laptop file `construction/out/p4b_phase3_status.json` (untracked,
`BLOCKED` / no OpenRouter key, `agents_attempted=0`) is **not** a Phase 3
scientific result and was not treated as an observation.

---

## 2. Repository evidence inspected

| Artifact | Role |
|---|---|
| `P4_VALIDATION_CORPUS_DESIGN.md` | declared `N_B`, quotas, families, T1–T8, E1–E4, Phase 3 cap |
| `P4_PREREG.md` | V1–V6 and E1–E4 exist before P4-B (commit `c35e828`) |
| `construction/params_b.json` | authored world/instruction/anchor/locator table (no `gold` field) |
| `construction/generate_b.py` | world emit + `L(world)` locker; no `if cid == "Bxx"` |
| `construction/qualify_b.py` | Phase 2 replay, T1–T8, hashes, seal |
| `construction/transforms_b.py` | C3–C6/Chan templates; no per-id branch |
| `construction/wordlists_{q,v,r,b}.txt` | dialect split |
| `construction/slate/b/B01.json`–`B20.json` | sealed clusters (gold + locator; no `observations`) |
| `construction/slate/b/worlds/Bxx/` | fixtures; `world_meta.json` has locator, not gold |
| `construction/out/p4b_gold_spec.json` | locked gold table |
| `construction/sealed/P4B_PHASE2_SEAL.json` | freeze record |
| `instrument/p4_instrument.py` | V1–V6 scorer |
| `construction/P4_AUTHORSHIP.md` | Q/V/R authorship safeguard (**not** a P4-B second-author protocol) |
| git log on the files above | temporal order |
| `construction/audit_p4b_anticircularity.py` | this audit’s read-only replay (does not call `generate_b.main()`) |
| `construction/out/p4b_anti_circularity_audit.json` | machine record of the replay |

Q/V/R slates and `q_score_*.json` contain authored **qualification**
observations. They are a different object. They were inspected only to
confirm P4-B clusters do not copy those fields.

---

## 3. Findings A–I

### A. Temporal precommitment

| Requirement | Locked in prose? | First git evidence | Before any P4-B agent observation? |
|---|---|---|---|
| `N_B = 20` | Yes, design memo §2 | `54b48b7` (same commit as the 20 clusters) | Yes |
| Family quota 4×5 | Yes, §3 | `54b48b7` | Yes |
| Kind quota 8/6/3/3 | Yes, §2 | `54b48b7` | Yes |
| One determining component | Yes, §1 | `54b48b7` | Yes |
| Gold-lock via `L` | Yes, §5 | `54b48b7` (`generate_b.py` + clusters) | Yes |
| Anchors = instruction substrings | Yes, §2/§5 | `54b48b7` | Yes |
| Observation channel = last assistant text | Yes, memo §6; originally `P4_PREREG.md` V1 | `c35e828` then restated `54b48b7` | Yes |
| V1–V6 contract | `P4_PREREG.md` §2 | `c35e828` (16:39) | Yes (instrument freeze is ~5h before P4-B) |
| E1–E4 estimands/gates | `P4_PREREG.md` §8 then memo §11 | `c35e828` then `54b48b7` | Yes |
| Phase 3 = B01–B03 Flash, cap $30, ≥2/3 scorable | memo §14 | `54b48b7` (prose); runner `d19fdee` (21:47) | Yes |

**PASS WITH CAVEAT.** Everything that matters for later cherry-picking
after *agent* outcomes is locked in git before any τ exists. What git
does **not** show is a Phase-0-only commit: the design memo first
appears in `54b48b7` **bundled with** `params_b.json`, worlds, and gold.
The memo’s claim that `N_B` was “locked before any P4-B task is authored”
is a process claim, not a separately dated git object. Private iteration
before that commit is not inspectable. Unused reserve IDs `RB01`–`RB10`
were never committed as files; the sealed set is exactly `B01`–`B20`.

Instrument freeze (`c35e828`) and MyPCBench gold-lock FAIL (`5854951`,
17:00) both precede P4-B construction. That order is expected (new
corpus after a corpus miss) and is also why investigator-blindness is
not claimable: the author already knew the instrument and the failure
mode of the previous target.

### B. Outcome independence

Mechanical checks on `B01`–`B20` cluster JSON and `params_b.json`:

- no `observations`, `last_response`, `last_text`, `tau`, or
  `expected_status` fields;
- Phase 1/2 records: `agents_run = 0`, `api_spend_usd = 0`;
- E1–E4 in the qualification JSON are `NOT_OPENED` / `NOT_EVALUABLE`
  with `n_tau = 0`.

Strings such as `T4_no_observations` and `HIT`/`MISS`/`ABSTAIN` appear
in the **design/qualification protocol**, not as scored episode outcomes
on P4-B clusters.

Q/V/R `observations.*` exist under other slates. `generate_b.py` does
not read them. Construction only calls frozen `v3_match` so that locked
gold self-matches as its own kind (a well-formedness check), not to
score an agent.

**PASS.** There is no P4-B agent outcome to leak into construction.

### C. Instrument independence

| Check | Result |
|---|---|
| `p4_instrument.py` contains `B01`–`B20` | no |
| `p4_instrument.py` contains MyPCBench leftover IDs | no |
| AST `task_id` / `cluster_id` / `"Bxx"` literals in instrument, `generate_b.py`, `transforms_b.py` | none |
| `generate_b.py` imports MyPCBench / `all_tasks_with_grading` | no |
| Per-id `if cid == …` in generator | no; loop over `B01`–`B20` applying `FAMILY_OP[family]` |
| MyPCBench IDs in `generate_b.py` | exclusion **blocklist** only (`EXCLUSION_IDS`) |
| Instrument hash vs freeze | identical |
| `params_b.json` is a per-id table | yes — this is the authored parameter file, not a scorer branch |

Construction **calls** the frozen module as a library (`parse_money`,
`v3_match`). That is allowed by the design memo and is not a per-task
parser patch.

**PASS WITH CAVEAT.** No structural instrument tuning against P4-B IDs.
The remaining caveat is construct-aware *task* authorship (anchors,
kinds, unique gold) by someone who had already frozen and qualified the
instrument on Q/V*. That is documented in §I, not an instrument-source
finding.

### D. Gold independence

Order in `generate_b.py`: emit world files from params (no `gold` key) →
write `world_meta.json` without gold → `gold = apply_locator(tables, L, kind)`.

This audit’s independent replay (disk world → parse → `L` → format):

- **20/20** `replay == sealed gold`
- `gold` absent from all 20 `params_b` rows
- `gold` absent from all 20 `world_meta.json` files
- gold-spec hash matches the Phase 2 seal

**PASS.** Gold is a function of sealed world + locator, locked before
any last-assistant-text. Residual: the human who wrote the cells in
`params_b.json` could compute `L` in their head. That is authorship
knowledge of task truth, not leakage from agent τ.

### E. Anchor independence

All 20 anchors are ≥2-token **literal substrings** of that cluster’s
instruction; gold is never a substring of the anchor. Anchors live in
`params_b.json` next to the instruction, not in `p4_instrument.py`.

They are rule-shaped (`<cover tokens> + fee/surcharge/crate/shifts/…`),
not selected from agent answers (none exist).

**PASS WITH CAVEAT.** Anchors were written by someone who knew V2 locate
uses instruction phrases. Distinctive two-token phrases make HIT
*possible*. That is contract-aware design, not post-hoc extraction
tuning.

### F. Independent authorship

Evidence that **does** exist:

- `wordlists_b.txt` (15 tokens: apron, bilge, cask, chute, dory, gantry,
  hatch, hopper, ketch, loft, marsh, mill, quay, spar, winch) is
  pairwise disjoint from Q, V, and R word-lists (audit: all pairwise
  intersections empty).
- No Q/V/R cover token appears as a whole word in any P4-B instruction
  or world blob (`qvr_in_blob = []` on all 20).
- Instructions use a dock/mill dialect, not Q’s rebate/ledger/kiln
  dialect.
- `P4_AUTHORSHIP.md` locks Q vs V generator roles; it does **not** name
  a second human for P4-B.

Evidence that does **not** exist:

- a second author, a split-role log, or a commit in which the design
  memo exists without `params_b.json`.

**PASS WITH CAVEAT.** Dialect split is real and mechanical. “Independent
authorship” in the strong (second-person) sense is **not** evidenced.
Do not cite `P4_AUTHORSHIP.md` as covering P4-B.

### G. Adversarial / non-trivial structure

Families map onto four locator operators (Locate and Filter share
`select_join`; Filter uses a tighter `left_where`):

| Family | n | Operator | What the world actually requires |
|---|---|---|---|
| Locate | 4 | `select_join` | Unique field of a keyed record; second file is a membership gate; same-kind distractors on the sheet; Locate money also has a **stale mail amount** (e.g. B01 `16.80` vs gold `88.40`) |
| Compute | 4 | `sum_join` | Sum ≥2 joined rows; **gold is not a cell** in any of the 4 (audit `n_compute_gold_not_cell = 4`); extra unused html/ics files |
| Reconcile | 4 | `live_not_stale` | Live sheet vs stale mail; values differ; gold = live |
| Filter | 4 | `select_join` + 2-clause where | Predicate (yard+rush, yard+seal, tag, dock+length) selects one row |
| Tally | 4 | `count_join` | Count after join/filter; golds `3,2,4,5` are **not** stored as cells |

`n_gold_as_cell = 12` = Locate+Reconcile+Filter. Compute and Tally golds
must be derived.

Entity filename cap: **1** (`B15` `night_chute_card.txt`). Others are
person/label values.

**PASS WITH CAVEAT.** The five families are not a single “read the only
number in `n.txt`” template: T3 (≥3 same-kind distractors) and T8 (two
environment objects) hold, Compute/Tally require derivation, Reconcile
is a live/stale split. Residual limitations that belong in the paper:

1. Worlds are **small authored fixtures** (typically 2–3 files, 4–6
   rows), not OSWorld-scale desktops.
2. Within-family items are **near-isomorphic** (B01≅B02, B09≅B10,
   B13≅B14, B17≅B19). Variation is real at family grain, thin at item
   grain.
3. Locate still reduces to “read the matching cell” after a join gate.

This is meaningful measurement-target structure, not a hardness claim
about CUA agents.

### H. Anti-cherry-picking

Selecting the current 20 **after seeing favorable agent behavior** is
**not possible in this repository**: there are no P4-B τ, scores, or
HIT/MISS/ABSTAIN episode records. Phase 2 forbids adding `B21`, dropping
IDs, or ranking models. The Phase 3 object (`B01`–`B03`) was named in
the design memo before any run.

Selecting among **uncommitted construction candidates** before
`54b48b7` is **NOT TESTABLE**. Git shows one successful 20. No voided
IDs, no reserve files, no construction-failure log.

**PASS** for outcome cherry-picking. **NOT TESTABLE** for pre-commit
construction shopping.

### I. Pre-observation blindness boundary

Supported:

- The author knew the P4 construct, V1–V6, Q/V* PASS, and the MyPCBench
  leftover-11 FAIL before writing P4-B. That is conceptual /
  instrument knowledge.
- The author did **not** have P4-B validation outcomes (none exist).
- Constraints that are independent of outcomes: `N_B=20`, quotas, T1–T8,
  word-list disjointness, `L`-locker, frozen instrument hash, no
  per-id scorer branches, forbidden P1–P3 gold strings.

Unsupported:

- “Blind authorship.”
- “Tasks written without knowledge of how HIT is assigned.”

**PASS** for the defensible sentence in §1.

---

## 4. Circularity risk scorecard

| Risk | Evidence | Status | Residual concern |
|---|---|---|---|
| Outcome leakage | No `observations`/`τ` on B clusters; Phase 1/2 `agents_run=0`; E1–E4 unopened | **PASS** | Laptop BLOCKED Phase-3 stub is not an observation |
| Task-specific instrument tuning | Instrument hash frozen 5h earlier; no B-id / `task_id` branches; transforms have no per-id literals | **PASS** | Author knew the contract and wrote tasks the contract can score |
| Gold leakage | Replay 20/20; gold not in params or world_meta; gold-spec hash matches seal | **PASS** | `world_meta.json` still stores **locator** `L` (see below) |
| Anchor tuning | Anchors are instruction substrings in params, not scorer tables; no τ to tune on | **PASS WITH CAVEAT** | Two-token phrases are contract-aware |
| Selection / cherry-picking | No agent outcomes; `B01`–`B20` sealed as a block | **PASS** (outcomes) / **NOT TESTABLE** (pre-commit drafts) | Reserve IDs never materialized in git |
| Wording contamination | `wordlists_b` ∩ {Q,V,R} = ∅; no Q/V/R tokens in B blobs | **PASS WITH CAVEAT** | Same operator, not a second author; template cloning |
| Trivial extraction | T3/T8; Compute/Tally gold not in cells; Reconcile live≠stale | **PASS WITH CAVEAT** | Small fixtures; Locate is still a cell lookup; within-family clones |
| Post-hoc corpus modification | Seal hashes still match; this audit did not regenerate; `d19fdee` changed memo **status** and added a runner, not gold/worlds | **PASS WITH CAVEAT** | Design-memo status line is not a frozen hash object; keep corpus hashes as the freeze, not the memo header |

Locator-in-`world_meta` is a **future execution** leak if a harness
mounts that file. The Phase 3 runner already hides `world_meta.json`
from `list_dir`/`read_file`. That is an operational control, not a
Phase-2 construction defect.

---

## 5. Exact residual limitations (document in the paper)

1. **Outcome-blind, not investigator-blind.** Instrument and MyPCBench
   FAIL were known before P4-B authorship.
2. **No dated Phase-0 git object.** Design memo and the 20 tasks share
   commit `54b48b7`.
3. **Word-list disjointness ≠ independent human authorship.**
4. **Small, template-cloned fixtures.** Family structure is real; item
   diversity is limited.
5. **`L` lives on disk in `world_meta.json`.** Must stay hidden from the
   agent at run time.
6. **Pre-commit construction iteration is unobservable.** Do not claim
   the first 20 candidates authored were the 20 sealed.

Do not claim: fully blind design; OSWorld-scale difficulty; a second
author; that git proves `N_B` was locked before the first world file
was written.

---

## 6. Final decision

**GO WITH DOCUMENTATION.**

No blocking circularity is present in the sealed corpus, gold, or
instrument. Phase 3 may proceed on the already-frozen B01–B03 Flash
pilot without changing `N_B`, quotas, gold, worlds, transforms, or
`p4_instrument.py`.

The paper (or the P4-B methods paragraph) must state the §5 residuals,
especially outcome-blind ≠ investigator-blind, and must not treat
word-list split as second-author independence.

---

## 7. Commit / hash references

| Ref | Meaning |
|---|---|
| `c35e828db89a9c7eb9d479601215a29221f5d744` | Instrument + Q freeze; V1–V6 and E1–E4 enter `P4_PREREG.md` |
| `58549515266a69e44c7e3262b34442c57dd920a6` | MyPCBench leftover gold-lock FAIL (`N_A=11`, n_locked=3) |
| `54b48b7c012be5a2fd0fb181cab0a12367339a12` | P4-B design memo + Phase 1 corpus |
| `78cf36ca2ad7bba1447c0fc15acca794b8d2cd2d` | Phase 2 qualification + seal |
| `d19fdee3a624b80306137fafdc2be3514a0d4bb4` | Phase 3 HPC runner (does not edit gold/worlds/instrument) |
| Instrument sha256 | `c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59` |
| `params_b.json` sha256 | `b4c610ba547c6222a619b6fbcc5014567d99760f6e501d7cf44d97c0102a8f26` |
| `generate_b.py` sha256 | `f2375298f0d1532b54ad89b77060640ad8e128a43ee3564303e0698f977e19ae` |
| `wordlists_b.txt` sha256 | `3d7e5fd5e6a60a691a323df8518b87e554ed6f1de3000abf960f251b34c06f43` |
| Seal file sha256 | `72eb33f718a616b1494fcec3dde512aceed5b9c61be112d611453696efaa4c54` |
| Machine audit | `construction/out/p4b_anti_circularity_audit.json` |

---

## 8. Audit execution notes

- Read-only replay: `python3 construction/audit_p4b_anticircularity.py`
- Did not call `generate_b.main()` or `qualify_b.py`
- Did not import OpenRouter or run `p4b_flash_pilot.py` except that
  this audit did not execute it
- `n_replay_match = 20`, `errors = []`, `api_spend_usd = 0`
