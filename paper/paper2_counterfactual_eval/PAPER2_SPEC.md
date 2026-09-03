# Paper 2 specification — freeze before any new cell

Paper 1 is frozen. This document closes **six decisions**. It does **not**
close agent IDs, a 30-task quota, or a 350-episode budget. Those are derived
after (3) and (4) are instantiated, never the other way around.

No new \(\tau\) until this file is agreed. Replay of Paper 1’s 24 pairs is
calibration **pilot**, not the confirmatory selection test.

Matching, guest gold, and Type labels: `DESIGN.md`. \(\Delta S\) is not a
reliability metric.

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
