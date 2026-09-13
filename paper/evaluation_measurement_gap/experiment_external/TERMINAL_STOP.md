# Terminal stop — cross-instrument evidence-loss audit

**STATUS:** `STOP-NO-CORPUS` (terminal state C)

**Date:** 2026-09-13  
**Paper commit at start:** `9b1b4ab`  
**This workstream does not reopen P3/P4 or `de66e0a`.**

---

## Result

No independently sourced CUA evaluation instrument jointly satisfied the eligibility gate:

independent source + public recorded episodes + public evaluator + independent gold + **inspectable intermediate R** + **discard A(R) of collected gold** + offline + no agent rerun + no evaluator modification + independent evidence-presence + n≥30 (or justified complete corpus).

**ELIGIBLE N = 0.** E2 was not counted.

This is a valid scientific result. The protocol was not relaxed.

---

## Why not “no E2 found” (state B)

State B requires an eligible instrument that preserves evidence. We did not admit an instrument. Absence of E2 counts is **not** evidence that instruments preserve gold.

Closest near-misses (still INELIGIBLE):

| Near-miss | Why it is not B |
|---|---|
| WebJudge | Collect-then-filter exists; independent determining gold is not at screenshot grain; using Score as gold is circular. Would be STOP-INCOMPATIBLE if forced. |
| Universal Verifier | Top-K exists in code; relevance matrix not in the public dataset columns; gold is task-level human labels. |
| WebArena-Verified | Independent gold + normalizer R; public τ n=2. |

If E2 is “not found,” the honest residual causes are **B/C/D mixed at the candidate level** (architecture differs; R not observable; evidence presence not independently establishable) — not “instrument preserves evidence.”

---

## Why not run our P3 extractor on public τ

That would answer a different question (does *our* parser lose gold on *their* text?) and is forbidden as cross-instrument replication.

---

## Scientific audit (attacks)

| # | Attack | Verdict |
|---|---|---|
| 1 | Just another parser bug | **PASS** — no parser was applied; P3 untouched |
| 2 | Selected only failures | **PASS** — no case sample |
| 3 | Gold from the evaluator | **PASS** — WebJudge/UV rejected for this reason |
| 4 | Evidence inferred from final verdict | **PASS** — `final_eval` not used as gold |
| 5 | Changed the external evaluator | **PASS** — none modified |
| 6 | Evaluator not independent | **PASS** — candidates were third-party; none admitted |
| 7 | Intermediate R is not evidence | **PASS** — this is why WebJudge scores were not treated as independent gold |
| 8 | Mechanism is implementation-specific | **PASS** as remaining objection — transport unanswered |
| 9 | Corpus too small | **PASS** — we did not use n=2 WAV demos as the result |
| 10 | Claiming prevalence | **PASS** — no rate claimed |

No FATAL process violation.

---

## Reproducibility

| Artifact | sha256 / id |
|---|---|
| `webjudge_online_mind2web.py` | `e3cd499b7c1fc92cbd51d3c4216c95ebab774c2c2cd998c5ad6dad94710780c4` |
| `agente_results.json` (WebJudge o4-mini) | `23c04410958bb488397b39d8d08a0138c0a87feaf304f9ae63c11e726a49bf26` |
| WebArena `evaluators.py` | `e23edb390c4e39b3fff97dfd456fb04f7a59a0fb1ea30a4f2fa42bcb77e00c22` |
| WAV `agent_response_evaluator.py` | `8ae2caf59c6fafecf4ec259ea67bf79d27f19c7fcbdc33a312cea730c4e54c31` |
| τ-bench `envs/base.py` | `1ad0402073f0ac9ca6b527efa0706e2aa8836dd2e5c1d453ed414ecb768c6d21` |
| `inspect_sources.py` | `f04c2dec80f757871af8fa2edd86ada539c8f81e5d41136faf3306c88370983e` |

Schema inspection: WebJudge JSONL n=299 for `agente_results.json`; record keys `task_id`, `confirmed_task`, `final_eval`, `image_judge_record`, `key_points`, `evaluation_details`; `image_judge_record[]` keys `Response`, `Score`.

---

## Frozen artifacts

Not touched: P3 extractor/repairs, P4-B/C/C2/D/M, `score_v2`, C2 wrapper, `de66e0a` external-validation freeze, experiment outputs under `out/`.
