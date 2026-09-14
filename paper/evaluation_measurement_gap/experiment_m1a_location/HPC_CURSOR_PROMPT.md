# HPC Cursor prompt — M1a location join (paste this)

Copy everything under **PROMPT** into Cursor on the HPC checkout.
Do not run this analysis on a laptop. Paper-2 `traj.jsonl` is host-only.

Local laptop commit of the paper tree: `8f58a3c` (or later). Sync that tree onto the host first if the host checkout is behind.

---

## PROMPT

```
REVIEW-ONLY SCIENCE ON FROZEN ARTIFACTS. THEN WRITE RESULT FILES. DO NOT EDIT THE PAPER.

PROJECT
-------
Paper: "From Trajectories to Evidence" (evaluation_measurement_gap, v0.4).
Core result already locked: M1a = gold entered the frozen extractor found set and was discarded (13/39 of 59 R1-positive misses); R-AGG +8/−18.

This workstream is a NARROW post-hoc join on those 13 rows.
It is NOT a 171-trajectory audit.
It is NOT an Evidence Availability Matrix over screenshots.
It is NOT transport of M1a.
It is NOT a new metric.
It is NOT Gate 0 revival.

ABSOLUTE DO-NOT
---------------
- Do not rerun agents.
- Do not modify P3 extractor (3242c30), matching.py, gold lock, P4-B/C/C2/D/M, score_v2, C2 wrapper.
- Do not OCR or open PNG/JPEG screenshots.
- Do not treat screenshot_file paths as evidence content.
- Do not invent gold presence from S, Y, or DONE.
- Do not impute UNKNOWN S as 0 or 100.
- Do not expand to 57 legs or 171 legs.
- Do not edit draft/main.tex, refs.bib, or P3/P4 frozen specs.
- Do not commit unless the user asks.
- Do not chmod/write Paper-2 archives.

QUESTION
--------
On the 13 locked M1a rows, for the same (lane, task, leg):

1. What locked screenshot-rubric S and pair-level Y join from Study 2 tables?
2. If traj.jsonl exists: does the gold STRING appear in TEXT fields of steps BEFORE the last traj line?

(1) can be answered from tables even if traj is missing.
(2) is extra. If any of the 13 traj files is missing, report STOP-NO-TRAJ for those rows; do not skip the S/Y join.

POPULATION (exact, closed)
--------------------------
13 M1a rows from paper/paper3_observation_grounded/P3_1_REPAIR_SPEC.md §A-9.3:

flash  counterfactual-f010 G0 liquid_cash                  gold 66493.59
flash  counterfactual-f013 G0 batbucks_dividends           gold 64.88
flash  counterfactual-f013 G0 gringotts_savings            gold 16413.28
flash  counterfactual-f013 G1 gringotts_savings            gold 3282.656
flash  retrieval-f009      G1 nyc_flight_confirmation      gold DN-87856
flash  retrieval-f010      G1 host_name                    gold Sandals Resorts Concierge
gpt    aggregation-f020    G0 batbucks_cash                gold 420.0
gpt    retrieval-f009      G0 nyc_hotel_confirmation       gold GH-29481
gpt    retrieval-f009      G1 nyc_flight_confirmation      gold DN-87856
flash  counterfactual-f005 G1 gme_shares                   gold 170.0
claude counterfactual-f005 G0 gme_avg_cost                 gold 42.12
claude counterfactual-f005 G0 gme_shares                   gold 85.0
flash  aggregation-f020    G1 batbucks_cash                gold 420.0

WHERE FILES LIVE ON THIS HOST
-----------------------------
Repo roots used historically:
  VINH- = /data2/hpcshared/Vinh-/agent
  VINH  = /data2/hpcshared/Vinh/agent

Resolve paths in this order. Do not guess a lane directory if a jsonl already stores traj/guest:

A-stratum traj/guest:
  out/study2_hatd_legs.jsonl
  (fields: lane, task, leg, traj, guest)

Non-A P3 legs (several M1a rows are outside A):
  out/p3_0_extracted.jsonl
  out/p3_0_recall_audit.jsonl
  out/p3_0_identification_audit.jsonl
  out/p3_0_legs.jsonl

Study-2 score tables (read-only):
  out/study2_valid_pairs.csv
  out/study2_layerA.csv
  out/study2_sts_pairs.json
  out/study2_completion_conditional.json

If out/ is empty, look under VINH-/out or VINH/out. Print the absolute paths you used.

Flash lane on host was NOT always results/paper2_exec/study2-flash.
scripts/study2_hatd_apply.py maps:
  gpt    -> VINH/results/paper2_exec/study2-gpt
  claude -> VINH/results/paper2_exec/study2-claude
  flash  -> VINH-/results/paper2_exec/hpc-flash-small-gate0a-postpatch
Prefer the traj path recorded in the jsonl over this map.

PART 1 — S/Y JOIN (mandatory, one shot)
---------------------------------------
For each of the 13 rows:

gold_in_answer = TRUE          # definitional M1a/R1
gold_in_found = TRUE           # definitional M1a
extractor_match = FALSE        # definitional M1a

in_A = (lane, task) in study2_valid_pairs.csv

If in_A:
  DONE = true
  S_leg = s0 if G0 else s1 from valid_pairs
  Y_pair = Y from layerA.csv
  Optionally record sts_pairs matches0/matches1[component] (must be false if present)
Else if (lane, task, leg) in completion_conditional.json high_S_no_DONE_cells:
  DONE = false
  S_leg = that score
  Y_pair = N/A
  record terminal reason
Else:
  S_leg = UNKNOWN
  DONE = UNKNOWN
  Y_pair = N/A
  Do not look up S from rubric_bundle or re-judge.

Summaries (joinable = rows with numeric S_leg):
  n_joinable_S / 13
  n_S100 among joinable   # denominator = joinable only
  n_in_A, n_in_A with Y=0
  n_not_DONE and S=100 from the locked high-S list

Licensed sentence if numbers support it:
  "On M1a rows that join to a locked Study-2 score, screenshot-rubric S can be 100 on the same leg where the frozen text extractor discarded collected gold."

Forbidden sentences:
  171 trajectories, screenshots contained gold, Flash is reliable, prevalence, P4-D.

PART 2 — TRAJ TEXT BEFORE LAST LINE (only if files exist)
---------------------------------------------------------
For each of the 13 rows, locate traj.jsonl.

If missing: traj_status = STOP-NO-TRAJ. Still keep Part 1.

If present: parse jsonl. Each line is one JSON object.
NEVER read screenshot_file as bytes.
Haystack for a step = text of these keys if present, stringified:
  action, response
  info only if it is a dict/str without embedding image bytes
Skip keys: screenshot_file, screenshot, image, png.

Define:
  last_line = last non-empty jsonl line  (this is the extractor's answer channel; already TRUE)
  earlier = all preceding lines

Literal gold presence, conservative:
  entity: casefold(gold) in casefold(haystack)
  money: any of {"66493.59","64.88","16413.28","3282.656","420.0","420","42.12"}
         as appropriate to THAT row's gold; also allow $ and commas
         e.g. 420.0 also matches 420.00 and $420
  integer 170 / 85: require a digit-boundary regex, not a bare substring
         (do not let 85 match 850 or 1985)

Record booleans:
  gold_in_last_response_text     # expect TRUE; if FALSE, ABORT that row and report
  gold_in_earlier_traj_text      # the only new quantity

Do not interpret earlier-text hits as "the agent tracked" or "screenshot had gold".
They only mean: the gold string appeared in recorded action/response text before the final answer.

If gold_in_last_response_text is FALSE on a row claimed M1a, STOP and do not invent a repair. That would mean path/gold mismatch, not a new finding.

OUTPUT (write only these)
-------------------------
Create if missing:
  paper/evaluation_measurement_gap/experiment_m1a_location/

Write:
  RESULT.md     human report
  join.json     machine record of the 13 rows + summaries
  RUN.txt       absolute paths used, file sha256 of every input table/jsonl, python version

Do not write into results/paper2_exec/.
Do not overwrite out/p3_0_*.jsonl.
Do not edit main.tex.

RESULT.md must contain:
- n_joinable_S, n_S100/joinable, UNKNOWN list
- table of 13 rows
- traj_status per row
- n_gold_in_earlier_traj_text among rows with traj present
- licensed reading / not established
- "denominator is joinable M1a rows, not 171"

WHEN DONE
---------
Print a 10-line terminal block:

STATUS:
JOINABLE S:
S=100 / JOINABLE:
UNKNOWN S:
IN A Y=0:
TRAJ PRESENT:
GOLD IN EARLIER TEXT:
FILES WRITTEN:
FROZEN ARTIFACTS TOUCHED: no
PAPER TEX TOUCHED: no

Then stop. No follow-up experiments. No screenshot protocol. No 171 expansion.
```

---

## After HPC finishes

Copy back to the laptop:

- `paper/evaluation_measurement_gap/experiment_m1a_location/RESULT.md`
- `join.json`
- `RUN.txt`

Do **not** merge into `main.tex` until those three files exist and the numbers match the protocol denominators.
