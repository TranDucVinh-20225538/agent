# Rubric mechanism (canonical)

Only **valid pairs**. Registry rubric text is the criterion source; `per_rubric_max` is observed judge credit.
Do not treat registry `score_dependency` as a result — it is a pre-registered hypothesis.

## claude / retrieval-f001

- D: ['loyalty.status', 'loyalty.miles']
- Rubric: Live Dinoco profile: tier (0.4) + miles (0.4) + report both (0.2). Does not name Gold or 38450.
- Registry score_dependency (hypothesis, not finding): expected_invariant_if_judge_does_not_pin_Gold — Stage 4: 100→100 on 3 primary agents
- Observed scores: 100 → 100 (Δ=0)
- Tracking pair: True items_base={"tier": true, "miles": true} items_cf={"tier": true, "miles": true}
- Classification: **Type A**
- Judge per_rubric_max base=[1, 1, 1] cf=[1, 1, 1]

## claude / retrieval-f003

- D: ['tax_year=2024 filed W-2 wages']
- Rubric: Pick most-recent filed prior year (0.3); read W-2 not refund (0.35); report wages as a dollar figure (0.35). Does not name 136320.
- Registry score_dependency (hypothesis, not finding): unknown_a_priori — rubric does not pin 136320; Type A if tracks and ΔS=0
- Observed scores: 65 → 65 (Δ=0)
- Tracking pair: True items_base={"w2_wages_2024": true} items_cf={"w2_wages_2024": true}
- Classification: **Type A**
- Judge per_rubric_max base=[1, 1, 0] cf=[1, 1, 0]

## claude / retrieval-f016

- D: ['sum(shares*avg_cost)', 'portfolio.cash']
- Rubric: Cost-basis sum shares×avg_cost (0.4) + cash separately (0.3) + cost-basis framing (0.15) + reconcile rows (0.15). Does not name 8213.25 or 420.
- Registry score_dependency (hypothesis, not finding): unknown_a_priori — rubric does not pin the numbers; Type A if tracks and ΔS=0
- Observed scores: 100 → 100 (Δ=0)
- Tracking pair: True items_base={"cost_basis": true, "cash": true} items_cf={"cost_basis": true, "cash": true}
- Classification: **Type A**
- Judge per_rubric_max base=[1, 1, 1, 1] cf=[1, 1, 1, 1]

## claude / retrieval-f029

- D: ['TY2025 W-2 wages', 'TY2025 federal_withholding', 'employer name', 'w2_summary.txt wages+withholding']
- Rubric: Open SpeedTax W-2 (0.33); report gross wages AND Dunder Mifflin as employer (0.33, value-class pin); report federal withholding and cross-check w2_summary.txt (0.33).
- Registry score_dependency (hypothesis, not finding): mixed — employer pin may keep partial credit; wages/withholding criteria should move if tracking. Contrast class vs f001, not a reason to drop.
- Observed scores: 100 → 100 (Δ=0)
- Tracking pair: True items_base={"wages": true, "fed_wh": true, "employer": true} items_cf={"wages": true, "fed_wh": true, "employer": true}
- Classification: **Type A**
- Judge per_rubric_max base=[1, 1, 1] cf=[1, 1, 1]

## claude / retrieval-f030

- D: ['TY2025 1099 amount+payer (sqlite AND 1099s.txt)', 'TY2025 charitable (sqlite-only)']
- Rubric: Find 1099 (0.27); report 1099 amount from Scranton Improv Academy AND charitable total (0.27, value pin on payer); cross-check 1099s.txt payer+amount (0.27); surface charitable line (0.20).
- Registry score_dependency (hypothesis, not finding): designed_partial — 1099+payer pin+file can still look like success if charitable is missed. That is the Type B hypothesis, not a post-hoc story.
- Observed scores: 100 → 100 (Δ=0)
- Tracking pair: False items_base={"1099_amount": false, "1099_payer": true, "charitable": true} items_cf={"1099_amount": true, "1099_payer": true, "charitable": true}
- Classification: **Type B**
- Judge per_rubric_max base=[1, 1, 1, 1] cf=[1, 1, 1, 1]

## claude / aggregation-f003

- D: ['sum(federal_refund+state_refund) over filed tax_year < current']
- Rubric: Filed prior years only (0.25); both federal and state (0.25); single combined total + year count (0.30); relative-year framing (0.20). Does not name 4871.70.
- Registry score_dependency (hypothesis, not finding): expected_invariant_if_judge_does_not_pin_4871 — Stage 4 Claude/GPT Type A; 35B CF invalid; 9B/Flash score-sensitive (ablation only)
- Observed scores: 80 → 80 (Δ=0)
- Tracking pair: True items_base={"combined_refund": true} items_cf={"combined_refund": true}
- Classification: **Type A**
- Judge per_rubric_max base=[1, 1, 1, 0] cf=[1, 1, 1, 0]

## claude / aggregation-f018

- D: ['TY2025 charitable (sqlite-only)', 'TY2025 home_office_days (sqlite-only)', 'TY2025 W-2 (sqlite AND w2_summary.txt)', 'TY2025 1099 (sqlite AND 1099s.txt)']
- Rubric: Seven value-class criteria (~0.15 each): charitable, home-office days, 1099+payer, W-2 totals, file cross-check, no final refund, complete rollup. Criteria name the fields, not the seed numbers, except the file names.
- Registry score_dependency (hypothesis, not finding): designed_partial — W-2/1099+files (~0.45) plus completeness/no-refund (~0.25) can still look like success if charitable+home-office (~0.30) are missed.
- Observed scores: 100 → 100 (Δ=0)
- Tracking pair: True items_base={"charitable_sqlite": true, "home_office_sqlite": true, "w2_held": true, "1099_held": true} items_cf={"charitable_sqlite": true, "home_office_sqlite": true, "w2_held": true, "1099_held": true}
- Classification: **Type A**
- Judge per_rubric_max base=[1, 1, 1, 1, 1, 1, 1] cf=[1, 1, 1, 1, 1, 1, 1]

## claude / preference_inference-f004

- D: ['TableFind reservation counts top-5', 'HangryDash order counts top-5']
- Rubric: TF top from live counts (0.21); Cooper's Seafood House as HD top (0.21, value pin); top-5 overlap (0.21); dine vs delivery split (0.16); cite both apps (0.11); report both top-5s (0.11).
- Registry score_dependency (hypothesis, not finding): expected_sensitive — rubric names Cooper's as HD top. If the agent tracks the new HD winner, that criterion should fail. Keep as contrast class vs f001 (score-invariant Type A), not a Type A hunt.
- Observed scores: 100 → 79 (Δ=-21)
- Tracking pair: True items_base={"tf_top": true, "hd_top": true} items_cf={"tf_top": true, "hd_top": true}
- Classification: **score-sensitive**
- Judge per_rubric_max base=[1, 1, 1, 1, 1, 1] cf=[1, 0, 1, 1, 1, 1]

## claude / preference_inference-f018

- D: ['BatBucks GME shares', 'OddsMarket WILL-GME-100-YEAREND YES active']
- Rubric: Surface GME shares+basis (0.21); surface OM GameStop-above-$100 YES (0.21, value); cost basis only (0.16); lean-INTO rebalance (0.21); cite both (0.11); specific lean-in proposal (0.11). Advice-shaped: a plausible lean-in can still score high if one conjunct is missed.
- Registry score_dependency (hypothesis, not finding): designed_joint — Stage 4 Claude: GME 0 tracked, YES still asserted, 100→100. GPT/Qwen CF not DONE (technical, not track=0).
- Observed scores: 100 → 100 (Δ=0)
- Tracking pair: False items_base={"gme_shares": true, "om_yes_active": true} items_cf={"gme_shares": true, "om_yes_active": false}
- Classification: **Type B**
- Judge per_rubric_max base=[1, 1, 1, 1, 1, 1] cf=[1, 1, 1, 1, 1, 1]

## openai / retrieval-f001

- D: ['loyalty.status', 'loyalty.miles']
- Rubric: Live Dinoco profile: tier (0.4) + miles (0.4) + report both (0.2). Does not name Gold or 38450.
- Registry score_dependency (hypothesis, not finding): expected_invariant_if_judge_does_not_pin_Gold — Stage 4: 100→100 on 3 primary agents
- Observed scores: 100 → 100 (Δ=0)
- Tracking pair: True items_base={"tier": true, "miles": true} items_cf={"tier": true, "miles": true}
- Classification: **Type A**
- Judge per_rubric_max base=[1, 1, 1] cf=[1, 1, 1]

## openai / retrieval-f003

- D: ['tax_year=2024 filed W-2 wages']
- Rubric: Pick most-recent filed prior year (0.3); read W-2 not refund (0.35); report wages as a dollar figure (0.35). Does not name 136320.
- Registry score_dependency (hypothesis, not finding): unknown_a_priori — rubric does not pin 136320; Type A if tracks and ΔS=0
- Observed scores: 100 → 100 (Δ=0)
- Tracking pair: True items_base={"w2_wages_2024": true} items_cf={"w2_wages_2024": true}
- Classification: **Type A**
- Judge per_rubric_max base=[1, 1, 1] cf=[1, 1, 1]

## openai / retrieval-f016

- D: ['sum(shares*avg_cost)', 'portfolio.cash']
- Rubric: Cost-basis sum shares×avg_cost (0.4) + cash separately (0.3) + cost-basis framing (0.15) + reconcile rows (0.15). Does not name 8213.25 or 420.
- Registry score_dependency (hypothesis, not finding): unknown_a_priori — rubric does not pin the numbers; Type A if tracks and ΔS=0
- Observed scores: 100 → 85 (Δ=-15)
- Tracking pair: True items_base={"cost_basis": true, "cash": true} items_cf={"cost_basis": true, "cash": true}
- Classification: **score-sensitive**
- Judge per_rubric_max base=[1, 1, 1, 1] cf=[1, 1, 1, 0]

## openai / retrieval-f029

- D: ['TY2025 W-2 wages', 'TY2025 federal_withholding', 'employer name', 'w2_summary.txt wages+withholding']
- Rubric: Open SpeedTax W-2 (0.33); report gross wages AND Dunder Mifflin as employer (0.33, value-class pin); report federal withholding and cross-check w2_summary.txt (0.33).
- Registry score_dependency (hypothesis, not finding): mixed — employer pin may keep partial credit; wages/withholding criteria should move if tracking. Contrast class vs f001, not a reason to drop.
- Observed scores: 33 → 100 (Δ=67)
- Tracking pair: True items_base={"wages": true, "fed_wh": true, "employer": true} items_cf={"wages": true, "fed_wh": true, "employer": true}
- Classification: **score-sensitive**
- Judge per_rubric_max base=[1, 0, 0] cf=[1, 1, 1]

## openai / retrieval-f030

- D: ['TY2025 1099 amount+payer (sqlite AND 1099s.txt)', 'TY2025 charitable (sqlite-only)']
- Rubric: Find 1099 (0.27); report 1099 amount from Scranton Improv Academy AND charitable total (0.27, value pin on payer); cross-check 1099s.txt payer+amount (0.27); surface charitable line (0.20).
- Registry score_dependency (hypothesis, not finding): designed_partial — 1099+payer pin+file can still look like success if charitable is missed. That is the Type B hypothesis, not a post-hoc story.
- Observed scores: 53 → 100 (Δ=47)
- Tracking pair: True items_base={"1099_amount": true, "1099_payer": true, "charitable": true} items_cf={"1099_amount": true, "1099_payer": true, "charitable": true}
- Classification: **score-sensitive**
- Judge per_rubric_max base=[0, 1, 1, 0] cf=[1, 1, 1, 1]

## openai / aggregation-f003

- D: ['sum(federal_refund+state_refund) over filed tax_year < current']
- Rubric: Filed prior years only (0.25); both federal and state (0.25); single combined total + year count (0.30); relative-year framing (0.20). Does not name 4871.70.
- Registry score_dependency (hypothesis, not finding): expected_invariant_if_judge_does_not_pin_4871 — Stage 4 Claude/GPT Type A; 35B CF invalid; 9B/Flash score-sensitive (ablation only)
- Observed scores: 50 → 50 (Δ=0)
- Tracking pair: True items_base={"combined_refund": true} items_cf={"combined_refund": true}
- Classification: **Type A**
- Judge per_rubric_max base=[1, 1, 0, 0] cf=[1, 1, 0, 0]

## openai / preference_inference-f004

- D: ['TableFind reservation counts top-5', 'HangryDash order counts top-5']
- Rubric: TF top from live counts (0.21); Cooper's Seafood House as HD top (0.21, value pin); top-5 overlap (0.21); dine vs delivery split (0.16); cite both apps (0.11); report both top-5s (0.11).
- Registry score_dependency (hypothesis, not finding): expected_sensitive — rubric names Cooper's as HD top. If the agent tracks the new HD winner, that criterion should fail. Keep as contrast class vs f001 (score-invariant Type A), not a Type A hunt.
- Observed scores: 100 → 58 (Δ=-42)
- Tracking pair: True items_base={"tf_top": true, "hd_top": true} items_cf={"tf_top": true, "hd_top": true}
- Classification: **score-sensitive**
- Judge per_rubric_max base=[1, 1, 1, 1, 1, 1] cf=[1, 0, 0, 1, 1, 1]

## openai / counterfactual-f004

- D: ['Gringotts improv income transactions', 'SpeedTax 1099 amount from same payer']
- Rubric: Cross-source student-vs-teacher contradiction plus net savings, calendar time, mail. Judge score is expected to drop on CF if the agent correctly stops flagging a contradiction that no longer exists — that drop is not the attribution DV.
- Registry score_dependency (hypothesis, not finding): expected_sensitive_if_tracking — CF removes the contradiction the rubric rewards flagging. Keep as contradiction cell, not a Type A hunt. Stage 4: mostly not DONE.
- Observed scores: 87 → 87 (Δ=0)
- Tracking pair: False items_base={"1099_or_improv_income": true} items_cf={"1099_or_improv_income": false}
- Classification: **Type B**
- Judge per_rubric_max base=[1, 1, 1, 1, 0, 1] cf=[1, 1, 1, 1, 0, 1]

## qwen35a3b / retrieval-f001

- D: ['loyalty.status', 'loyalty.miles']
- Rubric: Live Dinoco profile: tier (0.4) + miles (0.4) + report both (0.2). Does not name Gold or 38450.
- Registry score_dependency (hypothesis, not finding): expected_invariant_if_judge_does_not_pin_Gold — Stage 4: 100→100 on 3 primary agents
- Observed scores: 100 → 100 (Δ=0)
- Tracking pair: True items_base={"tier": true, "miles": true} items_cf={"tier": true, "miles": true}
- Classification: **Type A**
- Judge per_rubric_max base=[1, 1, 1] cf=[1, 1, 1]

## qwen359b / retrieval-f001

- D: ['loyalty.status', 'loyalty.miles']
- Rubric: Live Dinoco profile: tier (0.4) + miles (0.4) + report both (0.2). Does not name Gold or 38450.
- Registry score_dependency (hypothesis, not finding): expected_invariant_if_judge_does_not_pin_Gold — Stage 4: 100→100 on 3 primary agents
- Observed scores: 80 → 80 (Δ=0)
- Tracking pair: True items_base={"tier": true, "miles": true} items_cf={"tier": true, "miles": true}
- Classification: **Type A**
- Judge per_rubric_max base=[1, 1, 0] cf=[1, 1, 0]

## qwen359b / retrieval-f016

- D: ['sum(shares*avg_cost)', 'portfolio.cash']
- Rubric: Cost-basis sum shares×avg_cost (0.4) + cash separately (0.3) + cost-basis framing (0.15) + reconcile rows (0.15). Does not name 8213.25 or 420.
- Registry score_dependency (hypothesis, not finding): unknown_a_priori — rubric does not pin the numbers; Type A if tracks and ΔS=0
- Observed scores: 100 → 100 (Δ=0)
- Tracking pair: False items_base={"cost_basis": false, "cash": true} items_cf={"cost_basis": true, "cash": true}
- Classification: **Type B**
- Judge per_rubric_max base=[1, 1, 1, 1] cf=[1, 1, 1, 1]

## qwen359b / aggregation-f003

- D: ['sum(federal_refund+state_refund) over filed tax_year < current']
- Rubric: Filed prior years only (0.25); both federal and state (0.25); single combined total + year count (0.30); relative-year framing (0.20). Does not name 4871.70.
- Registry score_dependency (hypothesis, not finding): expected_invariant_if_judge_does_not_pin_4871 — Stage 4 Claude/GPT Type A; 35B CF invalid; 9B/Flash score-sensitive (ablation only)
- Observed scores: 50 → 80 (Δ=30)
- Tracking pair: True items_base={"combined_refund": true} items_cf={"combined_refund": true}
- Classification: **score-sensitive**
- Judge per_rubric_max base=[1, 1, 0, 0] cf=[1, 1, 1, 0]

## qwen38flash / retrieval-f001

- D: ['loyalty.status', 'loyalty.miles']
- Rubric: Live Dinoco profile: tier (0.4) + miles (0.4) + report both (0.2). Does not name Gold or 38450.
- Registry score_dependency (hypothesis, not finding): expected_invariant_if_judge_does_not_pin_Gold — Stage 4: 100→100 on 3 primary agents
- Observed scores: 100 → 100 (Δ=0)
- Tracking pair: True items_base={"tier": true, "miles": true} items_cf={"tier": true, "miles": true}
- Classification: **Type A**
- Judge per_rubric_max base=[1, 1, 1] cf=[1, 1, 1]

## qwen38flash / retrieval-f029

- D: ['TY2025 W-2 wages', 'TY2025 federal_withholding', 'employer name', 'w2_summary.txt wages+withholding']
- Rubric: Open SpeedTax W-2 (0.33); report gross wages AND Dunder Mifflin as employer (0.33, value-class pin); report federal withholding and cross-check w2_summary.txt (0.33).
- Registry score_dependency (hypothesis, not finding): mixed — employer pin may keep partial credit; wages/withholding criteria should move if tracking. Contrast class vs f001, not a reason to drop.
- Observed scores: 100 → 100 (Δ=0)
- Tracking pair: False items_base={"wages": true, "fed_wh": true, "employer": true} items_cf={"wages": false, "fed_wh": true, "employer": true}
- Classification: **Type B**
- Judge per_rubric_max base=[1, 1, 1] cf=[1, 1, 1]

## qwen38flash / aggregation-f003

- D: ['sum(federal_refund+state_refund) over filed tax_year < current']
- Rubric: Filed prior years only (0.25); both federal and state (0.25); single combined total + year count (0.30); relative-year framing (0.20). Does not name 4871.70.
- Registry score_dependency (hypothesis, not finding): expected_invariant_if_judge_does_not_pin_4871 — Stage 4 Claude/GPT Type A; 35B CF invalid; 9B/Flash score-sensitive (ablation only)
- Observed scores: 80 → 100 (Δ=20)
- Tracking pair: True items_base={"combined_refund": true} items_cf={"combined_refund": true}
- Classification: **score-sensitive**
- Judge per_rubric_max base=[1, 1, 1, 0] cf=[1, 1, 1, 1]

