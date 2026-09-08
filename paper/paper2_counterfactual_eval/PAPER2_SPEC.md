# Paper 2 specification — freeze before any new cell

Paper 1 is frozen. This document closes **six decisions**. It does **not**
close agent IDs, a 30-task quota, or a 350-episode budget. Those are derived
after (3) and (4) are instantiated, never the other way around.

No new \(\tau\) until this file is agreed. Replay of Paper 1’s 24 pairs is
calibration **pilot**, not the confirmatory selection test.

Matching, guest gold, and Type labels: `DESIGN.md`. \(\Delta S\) is not a
reliability metric.

---

## 0. Claim boundary (strengthen Paper 2; leave Paper 1 alone)

Advisor split of the story into two messages. Paper 2 **owns only (1)** as a
*decision* question; it does **not** claim (2).

| # | Message | Paper 2? |
|---|---|---|
| **(1)** | Benchmark score can overestimate / fail to certify grounding in the determining state that actually holds | **Yes** — Layer A (calibration) + Layer B (top-1 disagreement \(\arg\max \overline{S}\) vs \(\arg\max \overline{\mathrm{STS}}\)) on a frozen confirmatory universe |
| **(2)** | In a live episode, the agent overlooks updated data and acts on a *stale* belief (revise mid-task / mid-memory) | **No** — out of scope. Base and CF remain **independent** episodes, same as Paper 1. Mid-episode update, memory invalidation, and adversarial stale-state attacks are Paper 3+ / adjacent literature (e.g. STALE, arXiv:2605.06527); pre-registration draft at `PAPER3_STALE_PILOT_SPEC.md` (DRAFT_NOT_FROZEN) |

**How Paper 2 answers the scale critique of Paper 1.** Paper 1 was an
existence / separability audit (small \(n\), few Type B cells). Paper 2 does
**not** re-estimate a Type B rate from those 3 cells. It runs a
**pre-registered selection experiment** on the frozen analysis universe
(\(|\mathcal{M}|=4\), \(|\mathcal{T}|=25\), 228 legs after inject-probe;
see `out/paper2_analysis_universe.md`). Nulls in §6 remain publishable:
alignment of top-1 is a scientific answer, not a failed paper.

**Adjacent, not the same object.** BenchJack / grader-gaming audits
(arXiv:2605.12673) show high scores without solving via *reward hacks on the
judge*. Paper 2 keeps the judge fixed and moves *task-relevant guest gold*
\(D\); the failure mode is score–tracking disagreement and possible
**model-selection** error, not exploit construction against the harness.

**Deployment wording (keep narrow).** Target decision (§2): pick one CUA for
a workflow where determining records can change **between episodes**. Do not
sell Paper 2 as “agents ignore updates during an ongoing task.”

---

## 1. Primary hypothesis

**Decision question.** If a lab must pick one CUA for a stateful environment,
does selecting by conventional benchmark score pick the same agent as selecting
by state-grounded reliability?

**Confirmatory (Layer B).** On a pre-registered agent set \(\mathcal{M}\) and
task universe \(\mathcal{T}\),

\[
\arg\max_{i\in\mathcal{M}} \overline{S}_i
\;\neq\;
\arg\max_{i\in\mathcal{M}} \overline{\mathrm{STS}}_i
\]

when both means are computed on the **same analysis set** (below).

**Secondary (Layer A).** Across valid cells, \(S\) (base-leg rubric) does not
well-calibrate \(P(Y=1)\) (binary track on the pair, Paper 1 definition).

Neither layer is licensed by Paper 1’s 6/7 vs 3/7. Those rates are not a
ranking.

---

## 2. Target deployment decision

**Who:** a lab choosing **one** CUA to run on a personal-desktop / stateful
workflow where determining records can change between episodes.

**Action if hypothesis holds:** do not rank deployable CUAs by completion
score alone; report a reliability profile and select on STS (or a
pre-registered function of the profile).

**Action if it fails:** Paper 1’s split can remain a measurement finding
without a selection error at this scale (Cases 1–2 in §6). Paper 3 is then
not justified by decision consequence.

Out of scope: choosing among finance vs medical products; predicting
production harm (Paper 3+).

---

## 3. Agent inclusion rule

Freeze a **list of model IDs** before any Paper 2 \(\tau\). Do not drop or
add an ID after seeing \(S\) or STS.

**Minimum design (not a shopping list):** at least **four** CUAs that can
run the Paper 1 harness (MyPCBench + computer-use), spanning at least two
provider APIs and at least one open-weight hosted lane.

**Hard exclusions**

- Do not include a model only because Paper 1 showed Type A or Type B on it.
- Do not run ten models and publish the two that invert.
- Qwen3.5-35B-A3B is eligible only if the inclusion list says so *a priori*;
  its Paper 1 \(n=1\) is not a reason to drop or keep it after the fact.
- Analysis of selection uses only agents with **at least one valid pair**
  on \(\mathcal{T}\). Agents with zero valid pairs are execution coverage,
  reported separately, **not** entered into \(\arg\max\).

Paper 1 Claude / GPT-5.5 may appear on the frozen list because they already
run in-harness, not because of their invariance fractions.

**Amendment log (§3).** Freeze means: from the point a section is frozen,
any change needs a stated reason and a visible trail — not that the text is
immutable forever. Before any Paper 2 confirmatory execution, the model list
may still be amended if the stated reason is operational (feasibility,
budget, harness compatibility) and not derived from a Paper 2 outcome (no
Paper 2 outcome exists yet to derive anything from). Once confirmatory
execution begins, the model list is frozen for real — no further changes,
for any reason.

- **2026-09-03 — Qwen3.5-35B-A3B replaced by Qwen3.8-Flash, before any
  Paper 2 execution.** Reason: execution feasibility and budget efficiency
  within the existing harness (Qwen3.8-Flash already has a validated lane;
  see `scripts/stage4_qwen_openrouter_9b_then_flash.sh`), not a Paper 2
  outcome — none has been observed. Paper 1 execution history for both
  models (A3B: 1/10 valid pairs, 9/10 execution failures, mostly
  `EMPTY_XML`; Flash: 3 valid pairs on a smaller exploratory run) is
  recorded here as the operational context motivating the swap, per the
  hard-exclusion two bullets above — it is disclosed, not used to argue
  Flash is the scientifically preferable model. The original slot (A3B)
  is recorded, not silently dropped.

- **2026-09-08 — `gpt-5.5` keeps its slot; its *execution substrate*
  changes.** The sealed row (`agent_type: openai_cuabash`, OpenAI Responses)
  describes the **Paper 1 / native** instrument. Study 2 measures
  `openai/gpt-5.5` on the **frozen generic XML CUA protocol**
  (`qwen_cuabash` + OpenRouter `chat/completions`, no `tools`, no
  `previous_response_id`), because native CUA Gate 0 on the run host
  **FAILED** — the provider pre-executed the tool
  (`shell_call_output` inside turn 1), so client-side tool ownership could
  not be established and that path was never used. Evidence, identity
  split, and the claim boundary: `EXECUTION_MANIFEST.md` §0.2.

  This is a change of **substrate**, not of the model list: \(\mathcal{M}\)
  still contains the id `gpt-5.5`, and nothing was added, dropped, or
  reordered after seeing an outcome. `registry/sealed_models.json` is
  **not** rewritten to match runtime — a seal edited to agree with what
  happened is no longer evidence of what was promised.

  **Comparability consequence.** Study 2's roster is compared *within the
  generic-executor instrument* (Flash / GPT / Claude on the same XML loop),
  **not** against Paper 1's native GPT. Any \(\mathcal{M}\) table that
  prints `openai_cuabash` without the substrate footnote invites a
  native-CUA reading, which is not poolable with the generic lanes; the
  footnote is mandatory wherever the roster appears.

---

## 4. Task / state-family inclusion rule

**Substrate:** MyPCBench (executed). New eligibility is **not** Paper 1 A–E
(that ten-task set is exhausted). Channel invariance is **not** required.

**Keep a task** only if all of:

1. mapped sqlite (guest \(D\) possible);
2. determining state readable from the final answer (`dv_from_answer`);
3. instruction does not pin the gold dollar amount;
4. not LibreOffice `gui_artifact`;
5. not `cua_required` (same harness as Paper 1);
6. ID not in Paper 1’s ten.

**Strata (state families), not a quota of 30.** Each included task is tagged
with exactly one primary family before run:

| Family | `kind` stress |
|---|---|
| numeric | `money_usd` / `integer` |
| categorical / status | `categorical` |
| aggregation | derived total |
| temporal / current vs stale | year or “most recent” |
| relational / joint | two components, one `state` or two keys |
| preference / recommendation | `entity` |

**Selection:** pre-registered seed (new seed, not `20260826`). Within each
non-empty stratum, take all if \(n_{\mathrm{stratum}}\le k\), else
`Random(seed).sample(k)`. **\(k\) is chosen before looking at agent
outcomes**, to cover families, not to target 20–40 as a success criterion.

**Interventions.** Primary: one locked \(I_j\) per task (\(G_0,G_1\)).
**Multi-\(I\) subset:** after \(\mathcal{T}\) is frozen, a seed-selected
subset of size \(\min(8,\lceil 0.25\,|\mathcal{T}|\rceil)\) gets one extra
leg \(G_2\) (second direction or magnitude). Extra legs are a robustness
check, not a way to fish an inversion.

Paper 1’s ten tasks are **not** re-entered into confirmatory \(\mathcal{T}\).
They remain the measurement-object calibration set.

---

## 5. STS definition

Per component, match \(M_i^\ell\) as in `DESIGN.md` (guest gold, typed
`kind`, no LLM judge, no writer `track`).

**Pair binary track** \(Y_{ij}=1\) iff every positive-weight component
matches on **both** legs (Paper 1 `track`).

**Pair STS** \(=\frac12(\mathrm{STS}^0+\mathrm{STS}^1)\).

**Agent STS** (selection):

\[
\overline{\mathrm{STS}}_i
=
\mathrm{mean}\{\mathrm{STS}_{ij}: (i,j)\in\mathcal{A}\}
\]

\(\mathcal{A}\) = valid pairs (both `DONE`) for that agent on \(\mathcal{T}\).

Also report **family-wise** \(\overline{\mathrm{STS}}\) (no pooling as a
headline rate). A single 80% must not hide a 50% family.

**Not STS:** \(\Delta S\), completion rate, “score moved so they tracked.”

**Conventional score** (selection), pre-registered:

\[
\overline{S}_i
=
\mathrm{mean}\{S_{ij}^{0}: (i,j)\in\mathcal{A}\}
\]

Use the **base-leg** rubric only — the number a leaderboard would report on
the unmodified world. Do not average \(S^0\) and \(S^1\) (that mixes score
attachment into “success”). Do not invent a new aggregate to manufacture
inversion.

Same \(\mathcal{A}\) for \(\overline{S}\) and \(\overline{\mathrm{STS}}\) so
the two ranks are comparable. Incomplete / never-scheduled / execution
failure: exclude from \(\mathcal{A}\); do not recode as \(Y=0\).

---

## 6. Selection disagreement criterion

**Primary (deploy-one):** disagreement iff

\[
\arg\max_i \overline{S}_i \;\neq\; \arg\max_i \overline{\mathrm{STS}}_i
\]

among agents with \(|\{j:(i,j)\in\mathcal{A}\}|\ge n_{\min}\). Freeze
\(n_{\min}=3\) valid pairs before run. Below that, the agent is reported,
not ranked.

Ties on \(\arg\max\): disagreement iff the two argmax **sets** differ.

**Secondary:** Spearman \(\rho(\overline{S},\overline{\mathrm{STS}})\) on
the ranked agents; report, do not use to drop agents.

**Family-wise top-1** is exploratory unless a family-level \(\arg\max\)
rule is added to this file **before** run.

**Nulls (all publishable)**

| Case | Reading |
|---|---|
| \(S\) calibrates \(Y\); top-1 agrees | phenomenon can exist locally without selection error |
| Weak calibration; top-1 agrees | measurement issue \(\neq\) decision problem at this scale |
| Top-1 disagrees (primary) | decision consequence; Paper 3 justification |

Fishing: no post-hoc restriction of \(\mathcal{T}\) or \(\mathcal{M}\) to
produce Case 3.

### 6.1 Amendment log (§6) — power, rank stability, extension (2026-09-08)

**Why now.** §6 pre-registers a *per-agent* inclusion threshold
(\(n_{\min}=3\)) but no rule for the case where **every** agent is thin, and
no rule against extending the run until a result appears. Partial execution
coverage has made both cases plausible, so the rules are fixed here before
any STS, \(Y\), or cross-agent rank exists.

**Disclosed state at the time of writing.** *Observed:* per-leg terminal
reasons and per-leg judge scores \(S\) for the in-progress GPT lane
(25/57 checkpointed, 11 `DONE`); the pre-patch Flash lane (stopped and
archived as an invalidated instrument corpus); GPT valid-pair yield of **2**
on the first 12 tasks touched. *Not observed and not computed:* any
\(D\)-matching, any \(Y\), any STS, any \(\overline{S}\), any rank, any
cross-agent comparison. No agent has been added, dropped, or reordered, and
\(\mathcal{T}\), \(D\), and the interventions are untouched.

**(a) Per-agent inclusion — unchanged.** \(n_{\min}=3\) valid pairs to be
ranked; below that the agent is reported, not ranked. §3 hard exclusions
still apply.

**(b) Confirmatory Layer B requires rank stability, not a larger \(n\).**
A disagreement (§6 primary) is **confirmatory** only if it survives
leave-one-pair-out: for every ranked agent \(i\) and every pair
\((i,j)\in\mathcal{A}\), recomputing both means without that pair still
gives \(\arg\max\overline{S}\neq\arg\max\overline{\mathrm{STS}}\).
Also report a paired bootstrap over tasks within agent (\(B=10{,}000\))
frequency of disagreement. A disagreement that a single pair can erase is
reported as **exploratory**, with the leave-one-out result stated.
The rule is symmetric: if *agreement* flips under leave-one-pair-out, top-1
is called **indeterminate at this \(n\)** — not "aligned".

**(c) If fewer than three agents reach \(n_{\min}\).** Layer B is not
evaluated. The paper reports Layer A, coverage, and the instrument, and the
§6 null table gains the reading *under-powered for the selection test at
this scale*. That is a stated outcome, not a failed experiment.

**(d) No optional stopping.** Low yield does not license extending the
current experiment. Any extension — more tasks, larger step budget, or
re-running non-`DONE` cells — is a **separate, newly pre-registered**
experiment with its own dated section and seed, reported alongside and
never merged into the frozen leg set. An extension may be motivated by
coverage/yield only, never by which agent is currently \(\arg\max\).

**(e) Completion-conditional bias must be reported.** \(\mathcal{A}\)
conditions on both legs being `DONE`, and `DONE` correlates with task
difficulty and agent capability, so \(\overline{\mathrm{STS}}\) is a
completion-conditional quantity. Report these pre-registered descriptive
companions to Layer A: (i) valid-pair count and `DONE` rate per agent;
(ii) mean \(S\) on cells excluded from \(\mathcal{A}\), split by terminal
reason; (iii) the count of excluded cells scoring \(S\ge 0.9\) with no
canonical `DONE`. Item (iii) is descriptive evidence about score
attachment — the valid-pair filter removes exactly the cells where the
rubric is most detached from completion, which makes Layer A
**conservative**. None of (i)–(iii) is STS and none enters \(\arg\max\).

---

## 7. Inject-probe gate

Probe may **REJECT** a task (`rejected_not_identifiable`) but may **never**
trigger a rewrite of that task's frozen \(D\). A rejected task exits the
confirmatory analysis set; it does not return to semantic review.

A rejected task is coverage of the semantic universe, not a reason to
narrow \(D\) so the world becomes easier to inject.

**Exception (semantic-freeze bug, not injection difficulty).** If, while
building the probe, \(D\) is found to be mis-specified against the
**rubric itself** (wrong field, missing a component the answer must
ground, invented component the rubric does not require) — and *not*
because the guest is hard to patch — that is a freeze bug. File it as a
**new dated amendment** to `registry/registry_semantic_frozen.json` (same
discipline as §3's amendment log). Silent edits are forbidden. “World
hard to inject” is not this exception.

Reuse Paper 1 inject machinery (`scripts/cf_inject.py`, `--probe-only`).
Do not build a second engine. Multi-\(I\) tasks need **one spec row per
variant** (I1, I2), each with its own probe / patch / `expect`, not a
single PASS/REJECT for the task. A variant that fails does not remove
the task from analysis nor relabel it as single-\(I\); it is reported
as intervention coverage failure for that variant, and the task's
confirmatory contribution reflects only the variants that passed. Each
surviving variant is counted as its own unit in every downstream
denominator (§5 valid-pair count, §6 \(n_{\min}\)); a rejected variant
contributes zero, not a partial task.

---

## Cost (derived, not a target)

After \(\mathcal{M}\) and \(\mathcal{T}\) are listed:

\[
\text{legs} \approx |\mathcal{M}|\times|\mathcal{T}|\times 2
+ |\mathcal{M}|\times n_{\mathrm{multiI}}
\]

If that exceeds what the lab can run without dropping IDs mid-stream, **shrink
\(k\) in §4**, do not shrink \(\mathcal{M}\) after seeing outcomes.

---

## Next

1. ~~Agree this file.~~  
2. ~~Sealed \(\mathcal{M}\), \(\mathcal{T}\).~~ Semantic \(D\) frozen
   (`registry/registry_semantic_frozen.json`).  
3. Inject-probe (§7) on the **analysis** universe; then count legs.  
4. Then agents. Do not count confirmatory legs on the semantic 27 until
   the probe gate has run.
