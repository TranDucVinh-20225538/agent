# Canonical primary results (Phase A locked + Phase B)

Snapshot `b7b4203`. Semantic inference uses only valid paired episodes.
Invariance rate = Type A / tracking-valid = P(ΔS=0 | agent tracked D).
The three-model union is **descriptive**, not a pooled common-rate estimate.
Qwen3.5-35B-A3B execution failures are not coded as non-tracking.

## Per-model invariance (preferred reporting unit)

- Claude: 6/7 = 0.857; 95% CI [0.421, 0.996]
- GPT: 3/7 = 0.429; 95% CI [0.099, 0.816]
- Qwen3.5-35B-A3B: 1/1 = 1.000; 95% CI [0.025, 1.000]

## Descriptive union (labelled, not a common rate)

- 10/15 = 0.667; 95% CI [0.384, 0.882]

## Type A

- claude retrieval-f001: 100→100
- claude retrieval-f003: 65→65
- claude retrieval-f016: 100→100
- claude retrieval-f029: 100→100
- claude aggregation-f003: 80→80
- claude aggregation-f018: 100→100
- openai retrieval-f001: 100→100
- openai retrieval-f003: 100→100
- openai aggregation-f003: 50→50
- qwen35a3b retrieval-f001: 100→100

## Score-sensitive

- claude preference_inference-f004: 100→79 (Δ -21)
- openai retrieval-f016: 100→85 (Δ -15)
- openai retrieval-f029: 33→100 (Δ 67)
- openai retrieval-f030: 53→100 (Δ 47)
- openai preference_inference-f004: 100→58 (Δ -42)

## Type B (incomplete tracking, score high and invariant)

- claude retrieval-f030: 100→100; base_items={"1099_amount": false, "1099_payer": true, "charitable": true}; cf_items={"1099_amount": true, "1099_payer": true, "charitable": true}
- claude preference_inference-f018: 100→100; base_items={"gme_shares": true, "om_yes_active": true}; cf_items={"gme_shares": true, "om_yes_active": false}
- openai counterfactual-f004: 87→87; base_items={"1099_or_improv_income": true}; cf_items={"1099_or_improv_income": false}

## Other valid incomplete-tracking


## Execution coverage

- claude: DONE 19/20 traj; valid pairs 9/10
- openai: DONE 17/20 traj; valid pairs 8/10
- qwen35a3b: DONE 5/20 traj; valid pairs 1/10

## Size ablation (Qwen3.5-9B) — not primary

- 1/2 = 0.500; 95% CI [0.013, 0.987]
- retrieval-f001: valid=True tracking=True 80→80 **Type A** items_cf={"tier": true, "miles": true}
- retrieval-f003: valid=False tracking=None 65→65 **execution_failure** items_cf={"w2_wages_2024": false}
- retrieval-f016: valid=True tracking=False 100→100 **Type B** items_cf={"cost_basis": true, "cash": true}
- retrieval-f029: valid=False tracking=None 0→33 **execution_failure** items_cf={}
- retrieval-f030: valid=False tracking=None 0→0 **execution_failure** items_cf={}
- aggregation-f003: valid=True tracking=True 50→80 **score-sensitive** items_cf={"combined_refund": true}
- aggregation-f018: valid=False tracking=None 0→0 **execution_failure** items_cf={}
- preference_inference-f004: valid=False tracking=None 0→0 **execution_failure** items_cf={}
- preference_inference-f018: valid=False tracking=None None→None **execution_failure** items_cf={}
- counterfactual-f004: valid=False tracking=None None→None **execution_failure** items_cf={}

## Exploratory (Qwen3.8-Flash) — not primary

- 1/2 = 0.500; 95% CI [0.013, 0.987]
- retrieval-f001: valid=True tracking=True 100→100 **Type A** items_cf={"tier": true, "miles": true}
- retrieval-f003: valid=False tracking=None 100→65 **execution_failure** items_cf={}
- retrieval-f016: valid=False tracking=None 100→100 **execution_failure** items_cf={"cost_basis": true, "cash": true}
- retrieval-f029: valid=True tracking=False 100→100 **Type B** items_cf={"wages": false, "fed_wh": true, "employer": true}
- retrieval-f030: valid=False tracking=None 0→0 **execution_failure** items_cf={}
- aggregation-f003: valid=True tracking=True 80→100 **score-sensitive** items_cf={"combined_refund": true}
- aggregation-f018: valid=False tracking=None 0→0 **execution_failure** items_cf={}
- preference_inference-f004: valid=False tracking=None 0→0 **execution_failure** items_cf={}
- preference_inference-f018: valid=False tracking=None None→None **execution_failure** items_cf={}
- counterfactual-f004: valid=False tracking=None None→None **execution_failure** items_cf={}

## What not to claim

- Do not report a single invariance rate as the paper headline without the per-model breakdown.
- Do not treat Qwen EMPTY_XML as Type B or as track=0.
- 9B/Flash remain ablation/exploratory and are not pooled with Claude/GPT/35B-A3B.
- Phase B 9B/Flash six-task lanes are not on origin/phase-a-results; do not impute them.

