# Interim rubric audit

Only pairs that are currently **semantically valid** (both legs DONE, inject artifacts present where required).
Rubric wording is taken from `cf/phase_b_registry.json` and observed `rubric_result.json` per-criterion max vectors.
Do not treat registry `score_dependency` predictions as results.

## claude / retrieval-f001

- Determining evidence D (registry): ['loyalty.status', 'loyalty.miles']
- Rubric (registry): Live Dinoco profile: tier (0.4) + miles (0.4) + report both (0.2). Does not name Gold or 38450.
- Observed scores (INTERIM): 100 → 100 (delta=0)
- Tracking pair: true
- Registry score_dependency text: expected_invariant_if_judge_does_not_pin_Gold — Stage 4: 100→100 on 3 primary agents
- Should score theoretically be sensitive to changed evidence?: possibly invariant — rubric text does not name the seed numbers that I changes
- Observed score response vs that expectation: classification **Type A**; invariant=true
- base per_rubric_max: [1, 1, 1] (judge model claude-sonnet-4-6)
- cf per_rubric_max: [1, 1, 1] (judge model claude-sonnet-4-6)

## claude / retrieval-f003

- Determining evidence D (registry): ['tax_year=2024 filed W-2 wages']
- Rubric (registry): Pick most-recent filed prior year (0.3); read W-2 not refund (0.35); report wages as a dollar figure (0.35). Does not name 136320.
- Observed scores (INTERIM): 65 → 65 (delta=0)
- Tracking pair: true
- Registry score_dependency text: unknown_a_priori — rubric does not pin 136320; Type A if tracks and ΔS=0
- Should score theoretically be sensitive to changed evidence?: possibly invariant — rubric text does not name the seed numbers that I changes
- Observed score response vs that expectation: classification **Type A**; invariant=true
- base per_rubric_max: [1, 1, 0] (judge model claude-sonnet-4-6)
- cf per_rubric_max: [1, 1, 0] (judge model claude-sonnet-4-6)

## claude / retrieval-f016

- Determining evidence D (registry): ['sum(shares*avg_cost)', 'portfolio.cash']
- Rubric (registry): Cost-basis sum shares×avg_cost (0.4) + cash separately (0.3) + cost-basis framing (0.15) + reconcile rows (0.15). Does not name 8213.25 or 420.
- Observed scores (INTERIM): 100 → 100 (delta=0)
- Tracking pair: true
- Registry score_dependency text: unknown_a_priori — rubric does not pin the numbers; Type A if tracks and ΔS=0
- Should score theoretically be sensitive to changed evidence?: possibly invariant — rubric text does not name the seed numbers that I changes
- Observed score response vs that expectation: classification **Type A**; invariant=true
- base per_rubric_max: [1, 1, 1, 1] (judge model claude-sonnet-4-6)
- cf per_rubric_max: [1, 1, 1, 1] (judge model claude-sonnet-4-6)

## claude / retrieval-f029

- Determining evidence D (registry): ['TY2025 W-2 wages', 'TY2025 federal_withholding', 'employer name', 'w2_summary.txt wages+withholding']
- Rubric (registry): Open SpeedTax W-2 (0.33); report gross wages AND Dunder Mifflin as employer (0.33, value-class pin); report federal withholding and cross-check w2_summary.txt (0.33).
- Observed scores (INTERIM): 100 → 100 (delta=0)
- Tracking pair: true
- Registry score_dependency text: mixed — employer pin may keep partial credit; wages/withholding criteria should move if tracking. Contrast class vs f001, not a reason to drop.
- Should score theoretically be sensitive to changed evidence?: mixed — some criteria are value-class pins (employer / wages)
- Observed score response vs that expectation: classification **Type A**; invariant=true
- base per_rubric_max: [1, 1, 1] (judge model claude-sonnet-4-6)
- cf per_rubric_max: [1, 1, 1] (judge model claude-sonnet-4-6)

## claude / aggregation-f003

- Determining evidence D (registry): ['sum(federal_refund+state_refund) over filed tax_year < current']
- Rubric (registry): Filed prior years only (0.25); both federal and state (0.25); single combined total + year count (0.30); relative-year framing (0.20). Does not name 4871.70.
- Observed scores (INTERIM): 80 → 80 (delta=0)
- Tracking pair: true
- Registry score_dependency text: expected_invariant_if_judge_does_not_pin_4871 — Stage 4 Claude/GPT Type A; 35B CF invalid; 9B/Flash score-sensitive (ablation only)
- Should score theoretically be sensitive to changed evidence?: possibly invariant — rubric text does not name the seed numbers that I changes
- Observed score response vs that expectation: classification **Type A**; invariant=true
- base per_rubric_max: [1, 1, 1, 0] (judge model claude-sonnet-4-6)
- cf per_rubric_max: [1, 1, 1, 0] (judge model claude-sonnet-4-6)

## claude / preference_inference-f018

- Determining evidence D (registry): ['BatBucks GME shares', 'OddsMarket WILL-GME-100-YEAREND YES active']
- Rubric (registry): Surface GME shares+basis (0.21); surface OM GameStop-above-$100 YES (0.21, value); cost basis only (0.16); lean-INTO rebalance (0.21); cite both (0.11); specific lean-in proposal (0.11). Advice-shaped: a plausible lean-in can still score high if one conjunct is missed.
- Observed scores (INTERIM): 100 → 100 (delta=0)
- Tracking pair: false
- Registry score_dependency text: designed_joint — Stage 4 Claude: GME 0 tracked, YES still asserted, 100→100. GPT/Qwen CF not DONE (technical, not track=0).
- Should score theoretically be sensitive to changed evidence?: unknown from artifacts
- Observed score response vs that expectation: classification **Type B candidate**; invariant=true
- base per_rubric_max: [1, 1, 1, 1, 1, 1] (judge model claude-sonnet-4-6)
- cf per_rubric_max: [1, 1, 1, 1, 1, 1] (judge model claude-sonnet-4-6)

## openai / retrieval-f001

- Determining evidence D (registry): ['loyalty.status', 'loyalty.miles']
- Rubric (registry): Live Dinoco profile: tier (0.4) + miles (0.4) + report both (0.2). Does not name Gold or 38450.
- Observed scores (INTERIM): 100 → 100 (delta=0)
- Tracking pair: true
- Registry score_dependency text: expected_invariant_if_judge_does_not_pin_Gold — Stage 4: 100→100 on 3 primary agents
- Should score theoretically be sensitive to changed evidence?: possibly invariant — rubric text does not name the seed numbers that I changes
- Observed score response vs that expectation: classification **Type A**; invariant=true
- base per_rubric_max: [1, 1, 1] (judge model claude-sonnet-4-6)
- cf per_rubric_max: [1, 1, 1] (judge model claude-sonnet-4-6)

## openai / retrieval-f003

- Determining evidence D (registry): ['tax_year=2024 filed W-2 wages']
- Rubric (registry): Pick most-recent filed prior year (0.3); read W-2 not refund (0.35); report wages as a dollar figure (0.35). Does not name 136320.
- Observed scores (INTERIM): 100 → 100 (delta=0)
- Tracking pair: true
- Registry score_dependency text: unknown_a_priori — rubric does not pin 136320; Type A if tracks and ΔS=0
- Should score theoretically be sensitive to changed evidence?: possibly invariant — rubric text does not name the seed numbers that I changes
- Observed score response vs that expectation: classification **Type A**; invariant=true
- base per_rubric_max: [1, 1, 1] (judge model claude-sonnet-4-6)
- cf per_rubric_max: [1, 1, 1] (judge model claude-sonnet-4-6)

## openai / retrieval-f016

- Determining evidence D (registry): ['sum(shares*avg_cost)', 'portfolio.cash']
- Rubric (registry): Cost-basis sum shares×avg_cost (0.4) + cash separately (0.3) + cost-basis framing (0.15) + reconcile rows (0.15). Does not name 8213.25 or 420.
- Observed scores (INTERIM): 100 → 85 (delta=-15)
- Tracking pair: true
- Registry score_dependency text: unknown_a_priori — rubric does not pin the numbers; Type A if tracks and ΔS=0
- Should score theoretically be sensitive to changed evidence?: possibly invariant — rubric text does not name the seed numbers that I changes
- Observed score response vs that expectation: classification **score-sensitive**; invariant=false
- base per_rubric_max: [1, 1, 1, 1] (judge model claude-sonnet-4-6)
- cf per_rubric_max: [1, 1, 1, 0] (judge model claude-sonnet-4-6)

## openai / retrieval-f029

- Determining evidence D (registry): ['TY2025 W-2 wages', 'TY2025 federal_withholding', 'employer name', 'w2_summary.txt wages+withholding']
- Rubric (registry): Open SpeedTax W-2 (0.33); report gross wages AND Dunder Mifflin as employer (0.33, value-class pin); report federal withholding and cross-check w2_summary.txt (0.33).
- Observed scores (INTERIM): 33 → 100 (delta=67)
- Tracking pair: true
- Registry score_dependency text: mixed — employer pin may keep partial credit; wages/withholding criteria should move if tracking. Contrast class vs f001, not a reason to drop.
- Should score theoretically be sensitive to changed evidence?: mixed — some criteria are value-class pins (employer / wages)
- Observed score response vs that expectation: classification **score-sensitive**; invariant=false
- base per_rubric_max: [1, 0, 0] (judge model claude-sonnet-4-6)
- cf per_rubric_max: [1, 1, 1] (judge model claude-sonnet-4-6)

## openai / retrieval-f030

- Determining evidence D (registry): ['TY2025 1099 amount+payer (sqlite AND 1099s.txt)', 'TY2025 charitable (sqlite-only)']
- Rubric (registry): Find 1099 (0.27); report 1099 amount from Scranton Improv Academy AND charitable total (0.27, value pin on payer); cross-check 1099s.txt payer+amount (0.27); surface charitable line (0.20).
- Observed scores (INTERIM): 53 → 100 (delta=47)
- Tracking pair: true
- Registry score_dependency text: designed_partial — 1099+payer pin+file can still look like success if charitable is missed. That is the Type B hypothesis, not a post-hoc story.
- Should score theoretically be sensitive to changed evidence?: partial — some criteria pin held dual-channel fields; sqlite-only conjuncts may be missed without collapsing score
- Observed score response vs that expectation: classification **score-sensitive**; invariant=false
- base per_rubric_max: [0, 1, 1, 0] (judge model claude-sonnet-4-6)
- cf per_rubric_max: [1, 1, 1, 1] (judge model claude-sonnet-4-6)

## openai / aggregation-f003

- Determining evidence D (registry): ['sum(federal_refund+state_refund) over filed tax_year < current']
- Rubric (registry): Filed prior years only (0.25); both federal and state (0.25); single combined total + year count (0.30); relative-year framing (0.20). Does not name 4871.70.
- Observed scores (INTERIM): 50 → 50 (delta=0)
- Tracking pair: true
- Registry score_dependency text: expected_invariant_if_judge_does_not_pin_4871 — Stage 4 Claude/GPT Type A; 35B CF invalid; 9B/Flash score-sensitive (ablation only)
- Should score theoretically be sensitive to changed evidence?: possibly invariant — rubric text does not name the seed numbers that I changes
- Observed score response vs that expectation: classification **Type A**; invariant=true
- base per_rubric_max: [1, 1, 0, 0] (judge model claude-sonnet-4-6)
- cf per_rubric_max: [1, 1, 0, 0] (judge model claude-sonnet-4-6)

## openai / preference_inference-f004

- Determining evidence D (registry): ['TableFind reservation counts top-5', 'HangryDash order counts top-5']
- Rubric (registry): TF top from live counts (0.21); Cooper's Seafood House as HD top (0.21, value pin); top-5 overlap (0.21); dine vs delivery split (0.16); cite both apps (0.11); report both top-5s (0.11).
- Observed scores (INTERIM): 100 → 58 (delta=-42)
- Tracking pair: true
- Registry score_dependency text: expected_sensitive — rubric names Cooper's as HD top. If the agent tracks the new HD winner, that criterion should fail. Keep as contrast class vs f001 (score-invariant Type A), not a Type A hunt.
- Should score theoretically be sensitive to changed evidence?: yes — registry states rubric pins a value that I moves (HD Cooper's)
- Observed score response vs that expectation: classification **score-sensitive**; invariant=false
- base per_rubric_max: [1, 1, 1, 1, 1, 1] (judge model claude-sonnet-4-6)
- cf per_rubric_max: [1, 0, 0, 1, 1, 1] (judge model claude-sonnet-4-6)

## openai / counterfactual-f004

- Determining evidence D (registry): ['Gringotts improv income transactions', 'SpeedTax 1099 amount from same payer']
- Rubric (registry): Cross-source student-vs-teacher contradiction plus net savings, calendar time, mail. Judge score is expected to drop on CF if the agent correctly stops flagging a contradiction that no longer exists — that drop is not the attribution DV.
- Observed scores (INTERIM): 87 → 87 (delta=0)
- Tracking pair: false
- Registry score_dependency text: expected_sensitive_if_tracking — CF removes the contradiction the rubric rewards flagging. Keep as contradiction cell, not a Type A hunt. Stage 4: mostly not DONE.
- Should score theoretically be sensitive to changed evidence?: yes — registry states rubric pins a value that I moves (HD Cooper's)
- Observed score response vs that expectation: classification **Type B candidate**; invariant=true
- base per_rubric_max: [1, 1, 1, 1, 0, 1] (judge model claude-sonnet-4-6)
- cf per_rubric_max: [1, 1, 1, 1, 0, 1] (judge model claude-sonnet-4-6)

## qwen35a3b / retrieval-f001

- Determining evidence D (registry): ['loyalty.status', 'loyalty.miles']
- Rubric (registry): Live Dinoco profile: tier (0.4) + miles (0.4) + report both (0.2). Does not name Gold or 38450.
- Observed scores (INTERIM): 100 → 100 (delta=0)
- Tracking pair: true
- Registry score_dependency text: expected_invariant_if_judge_does_not_pin_Gold — Stage 4: 100→100 on 3 primary agents
- Should score theoretically be sensitive to changed evidence?: possibly invariant — rubric text does not name the seed numbers that I changes
- Observed score response vs that expectation: classification **Type A**; invariant=true
- base per_rubric_max: [1, 1, 1] (judge model claude-sonnet-4-6)
- cf per_rubric_max: [1, 1, 1] (judge model claude-sonnet-4-6)

