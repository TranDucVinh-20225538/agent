# Paper 3 — mid-episode staleness pilot (pre-registration; DRAFT_NOT_FROZEN)

**Status: DRAFT — not agreed, not frozen. No code (`cf_inject_midrun.py` or
equivalent) may be written against this file until a human (Khai and/or
Vinh) marks it frozen, per the standing discipline in `PAPER2_SPEC.md`
("freeze before any new cell").**

This file exists separately from `PAPER2_SPEC.md` on purpose. Paper 2's
Layer A/B tests claim (1): does a conventional score calibrate/rank agents
by state-tracking reliability across independent episodes. This file tests
claim (2): does an agent notice and act on state that changes *during* an
ongoing episode. Conflating the two — e.g. by calling this a "Layer C" of
Paper 2 — lets a small pilot read as a Paper 2 finding it is not. Keep
separate: separate hypothesis, separate task/model pool where feasible,
separate compute lane, separate reporting (Paper 3, or an explicitly
labeled appendix — never a Paper 2 result).

---

## 1. Hypothesis

An agent that correctly tracks a determining set \(D\) when \(D\) is
patched **before** episode start (Paper 1/2's design) may still act on
stale \(G_0\) when \(D\) is patched **during** an ongoing episode at a
fixed step \(k\), without being told.

Primary DV: **stale-answer rate** = \(P(\text{final answer matches } G_0
\text{ rather than } G_1 \mid D \text{ patched mid-episode at step } k)\).

This is adjacent to STALE (arXiv:2605.06527)'s "Recognition-Action
Disconnect" (models that identify outdated information under explicit
questioning still comply with it when a query presupposes the outdated
state) — same phenomenon class, first application to a CUA/GUI agent
executing a real desktop task rather than a dialogue/memory-recall probe.

## 2. Relation to Paper 1 / Paper 2

- Not a Layer of `PAPER2_SPEC.md`. Independent pre-registration.
- Reuses Paper 1/2 registry \(D\) components where possible — do not
  invent new \(D\) for this pilot; a task's determining set is whatever
  was already reviewed and frozen for it.
- Reported as Paper 3, or an appendix explicitly labeled as a separate,
  smaller-N pilot — never merged into Paper 2's Layer A/B tables or rates.
- Eventual merge: if all three become one paper, this stays its own
  section (phenomenon → consequence → solution/mitigation-probe), not
  folded into the consequence section's own claim.

## 3. Mechanism

`scripts/cf_inject_midrun.py` (new, does not exist yet): fires the same
kind of relative SQL patch already used in the P1/P2 registries, but
triggered at a fixed step-count \(k\) into the episode instead of before
warm-up.

- **v1: step-count trigger only.** Choose \(k\) per task, blind, before
  any run (e.g. from a prior baseline trajectory's median step count for
  a first read of the relevant field, not from the run being scored).
- **Not v1: event-based trigger** (fire the instant the agent's own
  action log shows it has read the determining field). More precise, but
  needs live Control-API monitoring of the running trajectory — real
  additional engineering. Explicit future work; do not build this to
  ship v1 faster.
- Same guest-hygiene discipline as Tier 1-3: clean snapshot per leg, no
  chained patches.

## 4. Task / model pool

- Small: a handful of long-horizon tasks already in a P1/P2 registry
  whose \(D\) is plausibly read early and reused later in the
  trajectory (multi-step tasks, not single-lookup tasks like
  `retrieval-f001`). Task list to be frozen here, by ID, before any run —
  not "whichever tasks look long."
- 1-2 models. Freeze the list here before any run, same discipline as
  `PAPER2_SPEC.md §3` (a model is not added or dropped after seeing a
  result).
- \(n\) and a stop rule are fixed **before** run (Phase C/D style, per
  `PHASE_C.md`/`PHASE_D.md` precedent) — a null result (agent uses
  \(G_1\), not \(G_0\)) is publishable and is not a reason to add
  more cells to chase a different outcome.

## 5. Gate

Same inject-probe discipline as `PAPER2_SPEC.md §7`: the probe may
**REJECT** (patch didn't land cleanly, or fired at a step that never
occurred in a given trajectory) but may never trigger a rewrite of the
task's frozen \(D\), and never a retry with different SQL to force a
different verdict. Technical failure (infra fault) is recorded and
retried once on a clean guest, same as Tier 1-3; not conflated with
REJECT.

## 6. Cost / compute lane

Runs only after the Paper 2 228-leg pipeline (`EXECUTION_MANIFEST.md`) is
either complete or explicitly moved to a separated API lane/host — this
pilot does not compete with Paper 2's compute or schedule, and does not
delay Paper 2 cell 1.

## 7. Out of scope for v1

- No adversarial-attack framing (this is a natural-episode staleness
  probe, not a red-team exercise on any deployed system).
- No claim about real deployed benchmarks' judges.
- No pooled rate across models — same per-model, no-pooling discipline as
  Paper 1/2.
- No promise that step-count triggering generalizes to event-based
  triggering; report it as what it is (a coarser, blind proxy).

## Next

1. Khai/Vinh review and mark this file frozen (or amend and re-propose).
2. Only after freeze: pick the task IDs and model IDs into §4 by name.
3. Only after §4 is filled and frozen: write `cf_inject_midrun.py`.
4. Run, gate, report — same order as Paper 1/2, nothing skipped.
