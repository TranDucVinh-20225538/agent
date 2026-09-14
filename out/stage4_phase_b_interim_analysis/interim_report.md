# Phase B Interim Audit

**INTERIM rolling audit.** Snapshot git `800eab6` (local already matched `origin/phase-a-results`). Phase B is still running. These counts are not paper statistics.

Path note vs a Stage-4-only layout: the four reused IDs live under `results/stage4-*`; the six new IDs live under `results/phaseb-<lane>-*`. Abandoned `results/stage4-qwen35-*` (27B) is ignored. 9B/Flash are not pooled.

## Current coverage

- total expected pair-slots (3 primary × 10 tasks): **30**
- total expected trajectories (×2 conditions): **60**
- cells currently present (`traj.jsonl`): **55**
- DONE cells (last action `DONE`): **36**
- incomplete / not-DONE / missing trajectories: **24**
- valid paired cells (both DONE + inspectable gold artifacts): **15**

Claude `retrieval-f030` CF: `retrieval-f030.guest.json` and `sql-patch.json` exist; `traj.jsonl` is not on this snapshot. `results/phase_b_claude_run.log` shows the CF agent started after inject. Treat as **currently running**, not as semantic non-tracking.
Claude `aggregation-f018` and `preference_inference-f004` dirs are absent (not started on this snapshot).

## Primary model status

### Claude

- Trajectories DONE: 14 / 20
- Trajectories present: 15 / 20
- Missing traj: retrieval-f030/cf, aggregation-f018/base, aggregation-f018/cf, preference_inference-f004/base, preference_inference-f004/cf
- Valid pairs (INTERIM): 6 / 10
- Pair classifications: retrieval-f001 Type A=100→100, retrieval-f003 Type A=65→65, retrieval-f016 Type A=100→100, retrieval-f029 Type A=100→100, aggregation-f003 Type A=80→80, preference_inference-f018 Type B candidate=100→100

- `retrieval-f001` base: DONE steps=6 score=100
- `retrieval-f001` cf: DONE steps=5 score=100
- `retrieval-f003` base: DONE steps=33 score=65
- `retrieval-f003` cf: DONE steps=48 score=65
- `retrieval-f016` base: DONE steps=9 score=100
- `retrieval-f016` cf: DONE steps=9 score=100
- `retrieval-f029` base: DONE steps=26 score=100
- `retrieval-f029` cf: DONE steps=26 score=100
- `retrieval-f030` base: DONE steps=83 score=100
- `retrieval-f030` cf: RUNNING/no-traj steps=0 score=None
- `aggregation-f003` base: DONE steps=14 score=80
- `aggregation-f003` cf: DONE steps=17 score=80
- `aggregation-f018` base: MISSING steps=0 score=None
- `aggregation-f018` cf: MISSING steps=0 score=None
- `preference_inference-f004` base: MISSING steps=0 score=None
- `preference_inference-f004` cf: MISSING steps=0 score=None
- `preference_inference-f018` base: DONE steps=24 score=100
- `preference_inference-f018` cf: DONE steps=6 score=100
- `counterfactual-f004` base: INCOMPLETE last=pyautogui.click(660, 618) steps=80 score=0
- `counterfactual-f004` cf: DONE steps=11 score=87

### GPT

- Trajectories DONE: 17 / 20
- Trajectories present: 20 / 20
- Missing traj: none
- Valid pairs (INTERIM): 8 / 10
- Pair classifications: retrieval-f001 Type A=100→100, retrieval-f003 Type A=100→100, retrieval-f016 score-sensitive=100→85, retrieval-f029 score-sensitive=33→100, retrieval-f030 score-sensitive=53→100, aggregation-f003 Type A=50→50, preference_inference-f004 score-sensitive=100→58, counterfactual-f004 Type B candidate=87→87

- `retrieval-f001` base: DONE steps=13 score=100
- `retrieval-f001` cf: DONE steps=9 score=100
- `retrieval-f003` base: DONE steps=34 score=100
- `retrieval-f003` cf: DONE steps=63 score=100
- `retrieval-f016` base: DONE steps=14 score=100
- `retrieval-f016` cf: DONE steps=20 score=85
- `retrieval-f029` base: DONE steps=41 score=33
- `retrieval-f029` cf: DONE steps=56 score=100
- `retrieval-f030` base: DONE steps=55 score=53
- `retrieval-f030` cf: DONE steps=35 score=100
- `aggregation-f003` base: DONE steps=28 score=50
- `aggregation-f003` cf: DONE steps=21 score=50
- `aggregation-f018` base: DONE steps=31 score=100
- `aggregation-f018` cf: INCOMPLETE last=EMPTY_XML steps=71 score=0
- `preference_inference-f004` base: DONE steps=32 score=100
- `preference_inference-f004` cf: DONE steps=37 score=58
- `preference_inference-f018` base: INCOMPLETE last=TOOL_CALL steps=19 score=0
- `preference_inference-f018` cf: INCOMPLETE last=TOOL_CALL steps=16 score=0
- `counterfactual-f004` base: DONE steps=65 score=87
- `counterfactual-f004` cf: DONE steps=40 score=87

### Qwen3.5-35B-A3B

- Trajectories DONE: 5 / 20
- Trajectories present: 20 / 20
- Missing traj: none
- Valid pairs (INTERIM): 1 / 10
- Pair classifications: retrieval-f001 Type A=100→100

- `retrieval-f001` base: DONE steps=7 score=100
- `retrieval-f001` cf: DONE steps=7 score=100
- `retrieval-f003` base: INCOMPLETE last=pyautogui.click(88, 93) steps=80 score=65
- `retrieval-f003` cf: INCOMPLETE last=EMPTY_XML steps=2 score=0
- `retrieval-f016` base: DONE steps=10 score=100
- `retrieval-f016` cf: INCOMPLETE last=EMPTY_XML steps=2 score=0
- `retrieval-f029` base: INCOMPLETE last=EMPTY_XML steps=2 score=0
- `retrieval-f029` cf: INCOMPLETE last=EMPTY_XML steps=2 score=0
- `retrieval-f030` base: INCOMPLETE last=EMPTY_XML steps=59 score=0
- `retrieval-f030` cf: INCOMPLETE last=EMPTY_XML steps=2 score=0
- `aggregation-f003` base: DONE steps=14 score=75
- `aggregation-f003` cf: INCOMPLETE last=FAIL steps=26 score=0
- `aggregation-f018` base: INCOMPLETE last=EMPTY_XML steps=80 score=0
- `aggregation-f018` cf: INCOMPLETE last=FAIL steps=22 score=0
- `preference_inference-f004` base: INCOMPLETE last=EMPTY_XML steps=14 score=0
- `preference_inference-f004` cf: INCOMPLETE last=EMPTY_XML steps=93 score=0
- `preference_inference-f018` base: DONE steps=14 score=100
- `preference_inference-f018` cf: INCOMPLETE last=PREDICT_CRASH steps=29 score=21
- `counterfactual-f004` base: INCOMPLETE last=WAIT steps=85 score=0
- `counterfactual-f004` cf: INCOMPLETE last=TOOL_CALL steps=91 score=0

## Currently observed outcomes

### Type A (valid pair, tracking_pair, score_delta=0)

- claude / retrieval-f001: 100 → 100
- claude / retrieval-f003: 65 → 65
- claude / retrieval-f016: 100 → 100
- claude / retrieval-f029: 100 → 100
- claude / aggregation-f003: 80 → 80
- openai / retrieval-f001: 100 → 100
- openai / retrieval-f003: 100 → 100
- openai / aggregation-f003: 50 → 50
- qwen35a3b / retrieval-f001: 100 → 100

### score-sensitive (valid pair, tracking_pair, score_delta≠0)

- openai / retrieval-f016: 100 → 85 (delta -15)
- openai / retrieval-f029: 33 → 100 (delta 67)
- openai / retrieval-f030: 53 → 100 (delta 47)
- openai / preference_inference-f004: 100 → 58 (delta -42)

### Type B candidates (valid pair, incomplete tracking, score unchanged/high)

- claude / preference_inference-f018: 100 → 100; base_state=GME 85; GME 0?; OM YES mentioned cf_state=OM YES mentioned
- openai / counterfactual-f004: 87 → 87; base_state=You’re both, but the ongoing thing to quit is student/enrollment:  - Student side: active Scranton Improv bill pay is $189/month. - Teaching side: the 1099-NEC is a $1,200 guest-instructor stipend from the same academy.  cf_state=You’re both, but for this decision you should treat it as quitting a class/enrollment, not leaving a regular teaching job.  - Evidence I found: you’re enrolled in Scranton Improv Academy / Improv 201 / Level 3 and have a

### execution failures (one or both legs not DONE / invalid)

- claude / retrieval-f030: base_done=true last=DONE; cf_done=false last=
- claude / counterfactual-f004: base_done=false last=pyautogui.click(660, 618); cf_done=true last=DONE
- openai / aggregation-f018: base_done=true last=DONE; cf_done=false last=EMPTY_XML
- openai / preference_inference-f018: base_done=false last=TOOL_CALL; cf_done=false last=TOOL_CALL
- qwen35a3b / retrieval-f003: base_done=false last=pyautogui.click(88, 93); cf_done=false last=EMPTY_XML
- qwen35a3b / retrieval-f016: base_done=true last=DONE; cf_done=false last=EMPTY_XML
- qwen35a3b / retrieval-f029: base_done=false last=EMPTY_XML; cf_done=false last=EMPTY_XML
- qwen35a3b / retrieval-f030: base_done=false last=EMPTY_XML; cf_done=false last=EMPTY_XML
- qwen35a3b / aggregation-f003: base_done=true last=DONE; cf_done=false last=FAIL
- qwen35a3b / aggregation-f018: base_done=false last=EMPTY_XML; cf_done=false last=FAIL
- qwen35a3b / preference_inference-f004: base_done=false last=EMPTY_XML; cf_done=false last=EMPTY_XML
- qwen35a3b / preference_inference-f018: base_done=true last=DONE; cf_done=false last=PREDICT_CRASH
- qwen35a3b / counterfactual-f004: base_done=false last=WAIT; cf_done=false last=TOOL_CALL

## Qwen execution coverage

Qwen3.5-35B-A3B failures are **execution / adapter** issues unless last action is `DONE`. EMPTY_XML / NO_ACTION are not semantic non-tracking.

- `retrieval-f003` base: last=`pyautogui.click(88, 93)` steps=80 fail=NOT_DONE
- `retrieval-f003` cf: last=`EMPTY_XML` steps=2 fail=PARSER_FAILURE
- `retrieval-f016` cf: last=`EMPTY_XML` steps=2 fail=PARSER_FAILURE
- `retrieval-f029` base: last=`EMPTY_XML` steps=2 fail=PARSER_FAILURE
- `retrieval-f029` cf: last=`EMPTY_XML` steps=2 fail=PARSER_FAILURE
- `retrieval-f030` base: last=`EMPTY_XML` steps=59 fail=PARSER_FAILURE
- `retrieval-f030` cf: last=`EMPTY_XML` steps=2 fail=PARSER_FAILURE
- `aggregation-f003` cf: last=`FAIL` steps=26 fail=OTHER_EXECUTION_FAILURE
- `aggregation-f018` base: last=`EMPTY_XML` steps=80 fail=PARSER_FAILURE
- `aggregation-f018` cf: last=`FAIL` steps=22 fail=OTHER_EXECUTION_FAILURE
- `preference_inference-f004` base: last=`EMPTY_XML` steps=14 fail=PARSER_FAILURE
- `preference_inference-f004` cf: last=`EMPTY_XML` steps=93 fail=PARSER_FAILURE
- `preference_inference-f018` cf: last=`PREDICT_CRASH` steps=29 fail=OTHER_EXECUTION_FAILURE
- `counterfactual-f004` base: last=`WAIT` steps=85 fail=NOT_DONE
- `counterfactual-f004` cf: last=`TOOL_CALL` steps=91 fail=TOOL_CALL_FAILURE

Qwen DONE cells at snapshot: 5.
- `retrieval-f001` base tracking=true state=Gold; 38450 score=100
- `retrieval-f001` cf tracking=true state=Silver; 8,620; 8620 score=100
- `retrieval-f016` base tracking=false state=market? 9376.08; cash~420 score=100
- `aggregation-f003` base tracking=true state=The scroll action successfully revealed the 2023 Federal & State Return that was previously hidden below the viewport. Now I can see both filed returns clearly displayed on the pag score=75
- `preference_inference-f018` base tracking=true state=GME 85; GME 0?; OM YES mentioned score=100

## Rubric observations

Only what the current valid pairs support:

- `retrieval-f003` rubric does not name 136320; Claude both legs DONE and report 136320 vs 80000 with scores **65 → 65**. Judge `per_rubric_max` on Claude base was `[1,1,0]` — the third criterion (dollar-figure formatting) can fail while wages still track.
- `retrieval-f016` rubric does not name 8213.25; Claude **100 → 100** with cost 8213.25/420 vs 7114.20/50. GPT **100 → 85** with the same numeric tracking; CF `per_rubric_max` `[1,1,1,0]` so one criterion (likely row-reconcile / framing) failed after I, which is score movement without implying non-tracking.
- `retrieval-f029` rubric pins Dunder Mifflin and asks for wages+withholding. GPT tracked 142000/28400 vs 90000/18000 but scores **33 → 100** (`per_rubric_max` base `[1,0,0]`). Score moved; tracking_pair true. Not Type B.
- `retrieval-f030` registry: 1099+file held, charitable sqlite-only. GPT reported 1200 both legs and charitable 950 vs 100 (**53 → 100**). That is tracking the moved conjunct, not a Type B miss. Base judge `[0,1,1,0]`.
- `preference_inference-f004` rubric pins Cooper's as HD top. GPT CF reports HD **Backyard 59 / Cooper's 57** and scores **100 → 58**, with CF `per_rubric_max` second criterion 0 — consistent with a score-sensitive pin, not invariance.
- Type B is only assigned when both legs are DONE and tracking of joint D is incomplete while the score stays unchanged/high. Execution failures are listed separately.

## Ablation models (not in primary statistics)

No `results/phaseb-qwen359b-*` or `results/phaseb-qwen38flash-*` on this snapshot.
Stage-4 exploratory dirs exist (`stage4-qwen359b-*`, `stage4-qwen38flash-*` for f001 / aggregation-f003 only). They are **not** pooled into the counts above.

## What cannot yet be concluded

- Phase B is still running (Claude CF f030 in progress; Claude still missing aggregation-f018 and preference_inference-f004).
- Current proportions of Type A / score-sensitive / Type B / execution failure are **not** final and must not be used as paper estimates.
- No Clopper-Pearson CI, invariance rate, hypothesis test, or pooled primary estimate is computed.
- Missing cells are not extrapolated from Phase A or from other models.
- Qwen EMPTY_XML cannot be read as evidence that Qwen does not track D.

