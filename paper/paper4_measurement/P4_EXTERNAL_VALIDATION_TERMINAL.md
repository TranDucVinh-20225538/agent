P4-M EXTERNAL VALIDATION — TERMINAL
====================================

STATUS
------
STOP (eligibility). Phases 2–5 not opened.

RESULT
------
No eligible independently sourced public CUA trajectory corpus under
frozen I (final assistant natural-language message only). Transport
could not start. This stop is the scientific result. Not a proof of
P4-M. Not a metric. Not an agent ranking.

CORPUS
------
none admitted
audited: WebArena-Verified (tasks + 2 demo eval/HAR logs);
official WebArena (task configs; Drive Playwright/HTML traces not
fetched); HF named dumps (cards only, not downloaded)

N
-
n/a (no sample frozen; eligible frame = 0)

A
-
n/a (no sampled episodes)

B
-
n/a (no sampled episodes)

C
-
n/a (no sampled episodes)

STOP/KILL reason
----------------
STOP: no eligible public dump.
Contributing established facts (not workarounds):
- WAV public git is a task+evaluator spec (812), not N>=30 trajectories.
- WAV demo n=2 < 20; agent_response.json is structured evaluator JSON,
  not final assistant NL; HAR is not I.
- Official WA traces, as published, are Playwright/HTML/screenshot
  bundles; frozen I forbids those channels; not present locally.
- Typed kind k is not a field of the public task JSON.
- Promoting action JSON / DOM / screenshots / HAR into I, or editing
  score_v2, or starting docker/live sites/agents, is forbidden.

FROZEN ARTIFACT STATUS
----------------------
UNCHANGED
p4_instrument.py
  c43a920a1501bed5e3fab0c56290d8ba30ded1e5f0693ef6b9affe24083e7d59
p4_instrument_v2.py
  a87ac636a729d99852eb837583b24bce372ff49c196f2be7e39e4f750622fcf3
p4c2_claim_wrapper.txt
  2a028f2b95a7bc1ce815ac4b01dcb1fc7c8814ded7a5f3f38489d4ffe70e8e08
No P4-B/C/C2/D/M theory files modified.
No score_v2 execution on an external sample.

NON-LEAKAGE STATUS
------------------
PASS for this pass: no sample, no Y, no outcome-based keep/drop.
eval_result.json / merge_log.txt / SCORES.json not opened.
See external_validation/PRE_OUTCOME_NONLEAKAGE_AUDIT.md

SCIENTIFIC INTERPRETATION
-------------------------
The external corpus could not instantiate the required measurement
stage; this identifies a transport boundary at eligibility.
Do not read as "P4-M proven", "P4-M false", "WebArena agents
unreliable", or "our metric beats existing metrics".

NEXT HUMAN DECISION
-------------------
Accept this STOP as the external-validation result, or separately
authorize a new project that first obtains a dump which already
satisfies the frozen eligibility table (final NL I, typed k,
independent L, N>=30, offline, no parser change). Do not reopen
P4-C/C2/D, do not edit score_v2, do not treat this as P4-E.
