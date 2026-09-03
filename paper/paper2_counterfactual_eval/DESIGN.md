# Paper 2 design note — what we are measuring

Paper 1 (frozen) showed that a completion score can fail to reflect a
gold-moving intervention even when the agent tracks, and can stay high when
tracking is incomplete. Paper 2 does **not** start from “6/7 invariant, therefore
metric X.” It starts from the decomposition:

\[
\text{completion} \;\neq\; \text{state tracking} \;\neq\; \text{score sensitivity}.
\]

The deliverable of this phase is a **closed measurement object** and a
**gold-matching protocol**. Validation runs, a larger registry, and other
harnesses are out of scope until the object is frozen.

Working title (not locked): *How Should We Evaluate Computer-Use Agents When
Completion Scores Are Not Enough?*

---

## 1. Inputs and outputs

For task \(t\), environment \(E^0\), locked intervention \(I\), \(E^1=I(E^0)\),
agent \(A\), instruction \(T\), judge \(J\):

\[
\tau^\ell = A(T, E^\ell),\qquad \ell\in\{0,1\}.
\]

| Symbol | Read from | Never from |
|---|---|---|
| \(\mathrm{done}(\tau)\) | last trajectory action literally `DONE` | writer flags, `result.txt` presence |
| \(S(\tau)=J(\tau)\) | rubric score in \(\{0,\ldots,100\}\) | tracking |
| Gold \(D^\ell\) | guest probes (`*.guest.json` / SQL after inject) | writer `track` fields, registry prose, agent memory |
| \(\hat D^\ell\) | final-answer text (same channel as Paper 1) | judge score, writer |

A pair is **valid** iff both legs are `DONE`. Never-scheduled cells are not
execution failures. Execution failures are not tracking misses.

**Portable spec (on paper):** any lab that can produce \((E^0,I,A,T,J)\) and
guest gold can compute the metrics below. **Executed substrate for a later
phase:** MyPCBench, because it already runs. That is an implementation choice,
not a claim that the object only exists there.

---

## 2. Determining set as a typed record

\(D\) is not “a fact.” It is a finite list of **components** frozen before any
Paper 2 agent run:

```
component:
  id:        string
  kind:      money_usd | integer | categorical | entity | state
  role:      determining | held | distractor
  gold_path: guest probe key (not writer)
  weight:    positive rational, frozen with D
```

- **determining:** \(I\) is designed to move this component (or the pair of
  values across \(\ell\) encodes the move).
- **held:** must stay at the pre-registered value on both legs (Paper 1
  `retrieval-f030` TY2025 1099 \( \$1{,}200 \)).
- **distractor:** present in the world, not scored in STS (GME held on
  `retrieval-f016`).

Joint \(D\) (Paper 1 `preference_inference-f018`) is two determining
components, not one blob. STS on that pair is exactly why binary Type B was
lossy: GME can match while OddsMarket YES does not.

Weights \(w_i\) are **role-based and pre-registered**, never fit to a model.
Default for this freeze: every `determining` and `held` component has \(w_i=1\);
`distractor` has \(w_i=0\) (excluded from the denominator). Equal weights until
a written exception exists in the registry row. No exception may be added after
seeing \(\hat D\).

---

## 3. Gold-matching protocol

The indicator \(\mathbf{1}[\hat d_i = d_i]\) is **not** string equality on the
raw answer. Matching is a function of `(kind, gold, reported)` after
**extraction**. Extraction and matching are separate.

### 3.1 Extraction (coder protocol)

Until a locked extractor exists, \(\hat d_i\) is coded from the final answer
the same way Paper 1 coded tracking: last assistant text / last `traj.jsonl`
response. Rules:

1. Code against guest gold for that leg, not against the other leg.
2. If the answer states two conflicting values for the same component, code
   **mismatch** (do not pick the one that matches gold).
3. Rounding that the coder must accept is listed under `kind` below — not
   improvised per trajectory.
4. No LLM-as-judge for \(\hat d_i\). That would re-enter the failure mode
   Paper 1 isolated.

### 3.2 Match by `kind`

| `kind` | Match | Paper 1 stress test |
|---|---|---|
| `money_usd` | \(\lvert \hat d - d \rvert \le \$1\) **or** both round to the same whole dollar | `aggregation-f003`: \(\$4{,}872\) matches \(\$4{,}871.70\); `retrieval-f029` Flash: \(\$91{,}200\) does **not** match \(\$90{,}000\) |
| `integer` | exact | share counts (GME 85 vs 0) |
| `categorical` | case-fold, strip, enum membership | loyalty Gold / Silver |
| `entity` | case-fold, strip; no paraphrase table unless frozen on the registry row | HangryDash winner names |
| `state` | every **required key** matches under its own kind | OddsMarket YES: `{shares: integer, status: categorical ∈ {active, settled}}` |

`state` exists so Paper 2 does not pretend OddsMarket is a dollar field.
A component matches iff all required keys match.

### 3.3 Leakage

The registry that stores \(D\) must not be readable by the agent as a file in
\(E^\ell\). Guest gold is collected by a probe the agent does not run.
Writer-side `track` is not an input to STS.

---

## 4. Metrics

Let \(M_i^\ell \in \{0,1\}\) be the match bit for component \(i\) on leg
\(\ell\), after §3. Let \(W=\sum_i w_i\) over components with \(w_i>0\).

**STS (per leg)**

\[
\mathrm{STS}^\ell = \frac{\sum_i w_i M_i^\ell}{W}.
\]

**STS (pair)** — mean of legs, only defined on valid pairs:

\[
\mathrm{STS} = \tfrac12(\mathrm{STS}^0 + \mathrm{STS}^1).
\]

**Binary track** (Paper 1 throughline, not replaced):

\[
\mathrm{track}=1 \iff \forall i \text{ with } w_i>0,\; M_i^0=M_i^1=1.
\]

So Claude `preference_inference-f018` is \(\mathrm{track}=0\) with
\(\mathrm{STS}<1\) (GME hit, OddsMarket miss on CF). Binary Type B is the
special case \(\mathrm{track}=0\) and high invariant \(S\); STS says *how*
incomplete.

**Score sensitivity** (dimension, not reliability):

\[
\Delta S = S^1 - S^0,\qquad \text{invariant iff } \Delta S=0
\]
(exact equality, no tolerance — same as Paper 1).

**Alignment 2×2** — same four cells as Paper 1’s taxonomy plus the empty cell,
not a rebrand:

|  | \(\Delta S=0\) | \(\Delta S\neq 0\) |
|---|---|---|
| \(\mathrm{track}=1\) | Type A | score-sensitive |
| \(\mathrm{track}=0\) | Type B if both scores \(\ge 80\) (operational high-score cutoff, not a law); otherwise “low-score miss, invariant” | **score-moved miss** (defined; unobserved on Paper 1’s valid pairs) |

Type B remains an **audit label** with an operational cutoff. STS is reported
alongside the cell, not instead of it.

Do not promote \(\Delta S\) into a quality score. Do not headline a pooled
invariance rate.

---

## 5. Anti-goals

1. Do not justify the protocol by Paper 1’s 6/7 or 3/7.
2. Do not run agents in this phase.
3. Do not take “30–50 tasks” as a success criterion. A later registry is sized
   by **coverage of `kind` / intervention operators**, not by CI width on
   invariance.
4. Do not commit Paper 2 to a new CUA harness or to Gemini/open-source agents
   as a required baseline. Portable spec yes; executed cross-harness is Paper 3
   / future work.
5. Do not use an LLM to decide \(M_i\).
6. Do not read writer `track` as gold.
7. Do not add `perception vs report` as a required metric until a frozen
   trajectory-coding protocol exists. Final-answer STS is the v1 object.
8. Do not call the fourth 2×2 cell a “fundamental CUA failure mode.”

---

## 6. What Phase 3 must look like (gate, not a plan to start now)

Allowed to start only after:

- this note is agreed (including `money_usd` tolerance),
- a registry **row schema** is filled for each candidate task **before** any
  new \(\tau\) is collected,
- \(D\), `kind`, `role`, \(w_i\) are frozen on those rows,
- designed intervention **operator** (numeric replace, entity swap, deletion,
  temporal, joint state, held-channel) is listed without predicted Type label
  as an outcome.

Forbidden as Phase 3 KPI: maximizing valid pairs, maximizing Type A count,
or replicating Paper 1’s ten tasks with more models only.

Replay of Paper 1’s existing 24 valid pairs through STS (no new runs) is
allowed now; that is a metric check, not a new experiment.

---

## 7. Literature posture (to read in Phase 1, not to cite-dump)

Paper 2 measures whether a **gold-moving intervention** appears in the answer
and whether \(S\) moves. Adjacent but different:

- protocol validity / shortcut necessity (intended capability still required
  for the score),
- judge sensitivity to prompt paraphrase,
- clinical/counterfactual update failures under coverage scores.

We do not identify model internals. We do not claim all CUA benchmarks are
broken.
