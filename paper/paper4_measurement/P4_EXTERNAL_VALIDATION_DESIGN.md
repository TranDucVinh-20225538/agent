# P4-M external validation — design freeze only

**Workstream:** P4-M empirical *transport* check (not opened).  
**This file is not P4-E, not Phase 1, not a metric, not a proof of P4-M.**  
**Frozen theory:** `P4_M_CLAIM_JUSTIFICATION_DESIGN.md` (THEORY CLOSED).  
**Typed Soundness:** no-leakage lemma, not strong validity.  
**NL denotation:** OUT OF SCOPE.

```
P4-D                         FAIL / W1 / CLOSED     do not reopen
CC-natural                   CLOSED
P4-M / Design                ACCEPTED
P4-M / Formalization         AMENDED + ACCEPTED
P4-M / Non-triviality        PASS
P4-M / E-expressiveness      LOCALIZED
P4-M / §13                   ACCEPT
P4-M / Typed Soundness       ACCEPT (narrow lemma)
P4-M / NL denotation         OUT OF SCOPE
P4-M / Empirical impl.       NOT STARTED
Phase 1                      NOT OPENED
This study                   DESIGN ONLY
```

P4-B, P4-C, P4-C2, P4-D, P4-M theory artifacts, `score_v2`, and the C2
wrapper are **immutable**. This design does not edit them, does not
reuse B/C/D/E slates as the external corpus, and does not re-apply
P4-D’s \(I_{CC}\) / 8/8 MISS floor or C2-H3 quotas.

**Kill-if-project.** If eligibility or transport requires standing up
sites, re-running agents, writing a new parser, a reader study, a new
benchmark, or any change to frozen \(I\to P\to E\) after outcomes,
**stop**. That is a design-stage kill, not a smaller experiment.

---

## 1. Scientific question

**Lock.**

> Can the P4-M observation/evidence distinction be transported to an
> independently sourced CUA trajectory corpus **without changing**
> the \(I\to P\to E\) pipeline after seeing outcomes?

This is **transport / instantiation**, not:

| Not the question | Why |
|---|---|
| Is P4-M true / proven? | Typed Soundness is already a lemma; this cannot prove it |
| Which agent is reliable? | No ranking |
| Did we find a better metric? | No new \(R\), no CC-natural |
| Can we pass P4-C / C2 / D gates on new data? | Those workstreams are CLOSED |
| Can a looser parser raise coverage? | Forbidden rescue |

Success of the *study* is a classified transport outcome (A/B/C in
§11), including **stop**. Failure to instantiate is a valid result.

---

## 2. External corpus — eligibility, not assumed

**Do not commit to a corpus because it is convenient.** Candidate
*names* for a later eligibility audit (not performed in this task,
no download):

- WebArena task specs + any **independently published** trajectory
  dumps that attach to those specs (Zhou et al., ICLR 2024).
  “WebArena-Verified” is treated as a **label to verify exists as a
  public artifact**; if no such distinct dump is found at audit, do
  not invent one.
- Other public CUA traces **only if** they meet the table below
  without a new harness (e.g. a frozen BrowserGym/AgentLab log
  bundle already on disk for a third party — still must pass L).

P4 B/C/D/E worlds, MyPCBench legs used in P1–P3, and C2/D
confirmatory \(\tau\) are **ineligible** (not independently sourced
for this study).

### Eligibility table

| Requirement | Admissible evidence (at audit, not now) | Failure interpretation |
|---|---|---|
| Independently sourced | Third-party public release; license OK; not authored for P4-M | STOP: no eligible corpus |
| CUA trajectory | Per-episode actions and/or assistant messages, not scores-only leaderboards | STOP: insufficient trajectory |
| Task specification | Frozen intent / instruction / schema for kind \(k\) | STOP: no \(k\), \(E\) undefined |
| Observable communication | A declared field that can be mapped to \(I\) **before** labels | STOP or **C** (transport boundary) |
| Independent \(L\) | Measurand locked from task spec or world locator, **not** from this agent’s answer or evaluator copy of that answer | STOP: no independent \(L\) |
| Loss vs absence | Enough raw text/trace to see a kind-\(k\) fragment that \(I\) did not recover, vs nothing typed in \(\tau\) | If only aggregated success bits exist → **C** |
| Offline replay | Analysis from recorded files; no live site, no new agent | If docker/replay harness is required → **KILL (new project)** |
| Bounded | One corpus, \(N\in[30,50]\) if it supports it; else STOP or smaller with pre-specified \(N\) | Multi-corpus / new collection → **KILL** |

**Design-stage note (not an audit result).** From published WebArena
*papers/docs only* (no corpus fetch): many tasks evaluate **page/DB
state** (`program_html`), not a typed last-text value; `string_match`
tasks may carry `reference_answers` in the *task* JSON (candidate
\(L\)) if that field is not copied from the run. Official WebArena
releases **task configs**; full third-party **agent traces** are a
separate artifact. If traces are missing, STOP. If \(I\) is frozen
as DFC `CLAIM:` and traces have no `CLAIM:` line, that is **B** or
**C**, not a licence to widen \(P\). None of this is decided until
an authorized eligibility audit **without** outcome-based sampling.

If no corpus meets the table: **design-stage / execution-stage STOP.**
Do not author a replacement slate.

---

## 3. Unit

**Atomic scored object:** one **episode-component**: one recorded
trajectory, one declared \(I\), one specification-kind \(k\), one
independent \(L\) (when \(L\) exists).

**Scientific \(N\):** number of **pre-specified sampled episodes**
(trajectories), not HIT+MISS, not legs×models, not WebArena
“sites,” not plus/minus/pm families.

Clustering (P4-D families) is **not** imported. Use clustering only
if the external dump is already grouped and the sample frame is
those groups; default is the episode.

Do not import P4-D conditions or the 8/8 MISS floor.

---

## 4. Sampling

**If** eligibility passes and the dump has at least 30 usable
episodes with a spec-kind \(k\) that \(\mathrm{parse}_k\) can see
(money / integer / entity / categorical — **or** a pre-declared
subset of WebArena `string_match` tasks whose \(L\) is a typed
string in \(\mathrm{Val}_k\)):

- Frame: all eligible episode IDs after eligibility, **before**
  opening evaluator success labels or \(Y\).
- Size: \(N=30\) if \(30\le n_{\mathrm{frame}}<50\); \(N=50\) if
  \(n_{\mathrm{frame}}\ge 50\); if \(n_{\mathrm{frame}}<30\), STOP
  or take **all** with \(N=n_{\mathrm{frame}}\) only if that rule
  is written **before** seeing labels (prefer STOP if \(<20\)).
- Draw: hash episode ID with a frozen salt written in the
  eligibility note; take the first \(N\) in hash order. No
  stratification on HIT/MISS, success, or “interesting” traces.

**Forbidden:** picking examples to populate taxonomy cells;
oversampling MISS; dropping measurement-loss episodes.

---

## 5. Frozen observation channel \(I\)

**Declared \(I\) for transport (freeze before analysis):**

The observation channel is **only** the episode’s **final assistant
natural-language message** (WebArena: `stop` / last `say` /
equivalent dumped field). Not screenshots, not DOM, not action
JSON arguments, not evaluator logs, not `world_meta`.

**DFC syntax is not required of the external agent.** Mapping
“final assistant text” → \(I(\tau)\) is a **schema transport**,
frozen here. It is **not** a more permissive *parser*.

**If the dump has no final assistant text:** STOP / **C**. Do not
promote `click(id=…)` argument strings into \(I\) after seeing
that last-text is empty.

**If a later authorized execution finds last-text exists but never
contains `CLAIM:`:** that is expected. \(P\) still runs on the
whole final message as the channel bytes (see §6). Do not add
wrapper-forcing or rewrite traces.

Harness / `A` / site success **is not** in \(I\to P\to E\).

---

## 6. Parser \(P\)

Reuse P4-M’s conceptual boundary: from \(I(\tau)\) recover **at
most one** unique span \(s\) that is a candidate string for
\(\mathrm{parse}_k\), using the **same kind-parse family as frozen
DFC `score_v2` / `v3_match` inputs** (canonical money / integer /
entity / categorical), **without** editing `p4_instrument_v2.py`.

Operational meaning for this study (still no code in this task):

- Apply the existing kind parser to the **final-text channel**.
- Unique recoverable typed span → \(s\).
- None or two+ competing typed spans of kind \(k\) → no unique
  \(s\) (\(E,Y\) undefined), not a new disambiguator.

**Forbidden:** NLP “the balance is X” recovery beyond what
\(\mathrm{parse}_k\) already does on the channel string; HTML
scraping; reading tool results; post-hoc regex after labels.

**Schema mismatch** (no text channel, or only screenshots):
**C**, not a repaired \(P\).

---

## 7. Evidence \(E\)

\[
E(s)=\mathrm{DETERMINING}
\iff
\mathrm{parse}_k(s)\neq\bot.
\]

`38.35` and `10.00` can both be DETERMINING for `money_usd`.
`finished successfully` → NONDETERMINING, \(Y\) undefined.

\(E\) **must not** consume \(\mathrm{value}(L)\), evaluator
output, success labels, or notes written after outcomes.

World-dependent English denotation stays **OUT OF SCOPE**.

---

## 8. Independent \(L\)

\(L\) is taken from the **task specification** (or a world locator
in that spec that does not read this episode’s assistant text or
eval-of-this-run).

**Inadmissible as \(L\):** evaluator fields that copy the agent’s
stop string; “gold” generated from the trace; success/fail bits;
LLM-as-judge explanations; P4 confirmatory last-texts.

If the only number in a WebArena eval is “whether locators match
live DOM,” that is **world/harness state**, closer to \(A\) than
to P4-M’s typed last-text \(L\). Those tasks are **out of frame**
unless the spec also locks a typed \(\mathrm{Val}_k\) value
independent of the trace. Do not redefine \(Y\) as task success.

If no independent \(L\): **STOP**.

---

## 9. Correspondence

Reuse frozen \(\leftrightarrow_k\) (same relation family as
`v3_match` for kind \(k\)). No English/world denotation match.

\(Y=\mathrm{HIT}\) iff \(E=\mathrm{DETERMINING}\), \(L\)
independent, and \(\mathrm{parse}_k(s)\leftrightarrow_k L\);
else `MISS` when DETERMINING and independent; else \(Y\)
undefined.

Typed Soundness is **not re-proved**. Reports of HIT/MISS are
descriptive transport cells.

---

## 10. Non-leakage

Before any \(Y\):

- \(I,P,E\) code/path does not read gold files, `reference_answers`
  values, or success labels.
- Kind \(k\) from task spec schema only, not from \(s\) to make
  \(E\) fire.
- No retune of parse / mapping after opening outcomes.
- Eligibility and sample IDs frozen in a note **before** \(Y\).

Leakage discovered → **STOP** (valid result). No workaround.

---

## 11. Three transport outcomes

| Code | Meaning | Not |
|---|---|---|
| **A** | Pipeline instantiates: unique \(s\), \(E\) defined, and independent \(L\) so \(Y\in\{\mathrm{HIT},\mathrm{MISS}\}\) | Agent is good |
| **B** | Kind-\(k\) fragment in \(\tau\) (loss rule, §13.7) not recovered by frozen \(I/P\) = **measurement loss** | Agent made no claim; agent failed |
| **C** | Dump cannot expose the relevant stage (no text channel, no \(L\), no \(k\)) = **transport boundary** | Parser should be relaxed |

Do not collapse B or C into agent failure or into DFC `MISS`.

---

## 12. Boundary replication (descriptive, no quotas)

Look for, and **count if present**:

- typed DETERMINING candidate;
- NONDETERMINING final text;
- measurement loss (B);
- typed HIT / MISS when independent \(L\) exists;
- \(Y\) undefined (no span / NONDETERMINING / no \(L\)).

If a cell is empty, report **absent**. Do not manufacture
examples. No MISS floor, no Form gate, no CC.

---

## 13. One-way protocol

```
corpus candidacy
  -> eligibility audit (no outcome-based keep/drop)
  -> freeze I mapping, P, E, L source, ↔_k, sample frame
  -> draw N
  -> analysis (A/B/C + descriptive cells)
  -> STOP
```

No parser change after outcomes. Transport fail → stop and report
the boundary.

**Authorization gate (human):** this file does **not** authorize
the eligibility audit download/execution. A later line must say
`GO TO P4-M EXTERNAL ELIGIBILITY AUDIT` (still no parser edits).

---

## 14. Stop rules

| Trigger | Result |
|---|---|
| No eligible public dump | STOP: no corpus |
| No independent \(L\) | STOP |
| No observable final-text channel | STOP / C |
| Cannot keep frozen \(I\to P\to E\) without a new parser/harness | **KILL (new project)** |
| Leakage | STOP |
| Outcome-dependent sampling | STOP (protocol breach) |
| Need live WebArena sites / new agents / >$50 / reader study | **KILL** |
| Temptation to reopen C2/D gates or amp coverage | STOP; do not |

A stop is a scientific result.

---

## 15. Budget

- No training, no new model, no reader study, no new benchmark.
- Prefer **$0** offline replay of recorded traces.
- Cap **$50** only if a later authorization requires a documented
  fetch of a public archive (storage), not inference.
- Any plan that needs OpenRouter, site docker, or `score_v2` edits:
  **KILL**.

---

## 16. Separation from P4-M theory

This study **cannot prove P4-M**. Typed Soundness stays a narrow
lemma. This is only a transport/instantiation check.
NL denotation remains out of scope. Empty taxonomy cells do not
falsify §13.

---

## 17. Separation from P4-B/C/C2/D

No frozen artifact modified. No prior P4 slate as this corpus.
No failed gate reopened. No P4-D CC / 8/8. No P4-C/C2 Form or H3
thresholds. No P4-E.

---

## 18. Deliverables

**This task:** `P4_EXTERNAL_VALIDATION_DESIGN.md` only.

Later (not authorized): eligibility note; frozen sample ID list;
analysis table of A/B/C. Not a runner, not `score_v2`, not a
commit.

### Decision table (summary)

| Requirement | Admissible evidence | Failure interpretation |
|---|---|---|
| Independent source | Public third-party dump | STOP |
| Trajectories + final text | Mapped to \(I\) before labels | C or STOP |
| Spec kind \(k\) | Schema, not \(s\) | STOP |
| Independent \(L\) | Spec/locator, not agent/eval copy | STOP |
| Unique \(s\), DETERMINING, \(Y\) | A | Descriptive only |
| Typed fragment in \(\tau\), not in \(I/P\) | B measurement loss | Not agent fail |
| Missing channel / \(L\) / harness needed | C or KILL | Not a parser ticket |
| Leakage / post-hoc \(P\) | STOP | No workaround |

---

## 19. Commit policy

DO NOT COMMIT. Do not alter frozen files. Do not modify code. Do
not download or execute an external corpus in this task.

STATUS
-------
Design only.
No experiment authorized.
No corpus execution authorized.
No frozen artifact changes authorized.
No commit authorized.
