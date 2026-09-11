# Tracking evidence, per valid pair

Gold column is read from `*.guest.json` (`probe_before`/`probe_after`/`extra_probes_*`), never from writer `track` fields. Mechanism column is read from the agent's final answer (`messages.json` last assistant text block, or `traj.jsonl` last-step `response` field when no `messages.json` exists -- GPT and Qwen runs in this repo carry no `messages.json`).


## retrieval-f001 -- control (channel-invariant, point value)

**Claude** (base=100, cf=100, delta=0, class=type_a)

- Gold/D: loyalty.status/miles Gold/38450->Silver/8620
- Mechanism: Base reports Gold/38,450; CF reports Silver/8,620. Both correct.

**GPT** (base=100, cf=100, delta=0, class=type_a)

- Gold/D: loyalty.status/miles Gold/38450->Silver/8620
- Mechanism: Base reports Gold/38,450; CF reports Silver/8,620. Both correct.

**Qwen3.5-35B-A3B** (base=100, cf=100, delta=0, class=type_a)

- Gold/D: loyalty.status/miles Gold/38450->Silver/8620
- Mechanism: Base reports Gold/38,450; CF reports Silver/8,620. Both correct.

**Qwen3.5-9B** (base=80, cf=80, delta=0, class=type_a)

- Gold/D: loyalty.status/miles Gold/38450->Silver/8620
- Mechanism: Base reports Gold/38,450; CF reports Silver/8,620. Both correct.

**Qwen3.8-Flash** (base=100, cf=100, delta=0, class=type_a)

- Gold/D: loyalty.status/miles Gold/38450->Silver/8620
- Mechanism: Base reports Gold/38,450; CF reports Silver/8,620. Both correct (plus extra MQM detail).


## aggregation-f003 -- control (channel-invariant, aggregation)

**Claude** (base=80, cf=80, delta=0, class=type_a)

- Gold/D: combined filed refund 4871.70->400.00
- Mechanism: Base reports $4,872; CF reports $400. Both correct.

**GPT** (base=50, cf=50, delta=0, class=type_a)

- Gold/D: combined filed refund 4871.70->400.00
- Mechanism: Base reports $4,871.70; CF reports $400. Both correct; absolute rubric score lower (misses a year-count criterion in both conditions).

**Qwen3.5-9B** (base=50, cf=80, delta=30, class=sensitive)

- Gold/D: combined filed refund 4871.70->400.00
- Mechanism: Base reports $4,872; CF reports $400. Both correct (tracks); score moves 50->80 on an unrelated per-year-breakdown criterion.

**Qwen3.8-Flash** (base=80, cf=100, delta=20, class=sensitive)

- Gold/D: combined filed refund 4871.70->400.00
- Mechanism: Base reports $4,872; CF reports $400. Both correct (tracks); score moves 80->100.


## preference_inference-f018 -- designed Type B (joint D, Stage 4 lock)

**Claude** (base=100, cf=100, delta=0, class=type_b)

- Gold/D: joint D: GME shares 85->0 AND OddsMarket YES 200/active->0/settled
- Mechanism: CF answer correctly zeroes GME (0 sh, $0.00) but still lists OddsMarket GameStop-YES as 200 sh/$16.00, byte-identical to the base row. One of two D components tracked.


## counterfactual-f004 -- score-sensitive contrast (contradiction removal; score auxiliary)

**GPT** (base=87, cf=87, delta=0, class=type_b)

- Gold/D: 1099_amount_0 for TY2023/2024/2025 all ->0 (this commit's patch zeroes all three; TY2025 was the whitespace-bug victim in the Stage-4-era commit, now fixed)
- Mechanism: Base and CF answers are near-identical: both state the 1099-NEC is $1,200 and both subtract it from net savings (~$1,068/yr). CF does not reflect the zeroed 1099 field.


## retrieval-f003 -- control (single sqlite channel)

**Claude** (base=65, cf=65, delta=0, class=type_a)

- Gold/D: TY2024 filed W-2 wages 136320->80000
- Mechanism: Base reports $136,320; CF reports $80,000. Both correct.

**GPT** (base=100, cf=100, delta=0, class=type_a)

- Gold/D: TY2024 filed W-2 wages 136320->80000
- Mechanism: Base reports 136,320; CF reports 80,000. Both correct.


## retrieval-f016 -- control (single-app aggregation, distractor channel held constant)

**Claude** (base=100, cf=100, delta=0, class=type_a)

- Gold/D: VTI shares 5->0 / cash 420->50 (cost-basis total 8213.25->7114.20); GME held constant
- Mechanism: Base reports $8,213.25 total / $420 cash; CF reports $7,114.20 / $50. GME unchanged in both. Both correct.

**GPT** (base=100, cf=85, delta=-15, class=sensitive)

- Gold/D: VTI shares 5->0 / cash 420->50 (cost-basis total 8213.25->7114.20); GME held constant
- Mechanism: Base reports $8,213.25 / $420; CF reports $7,114.20 / $50. Both correct (tracks); score moves 100->85.

**Qwen3.5-9B** (base=100, cf=100, delta=0, class=type_b)

- Gold/D: VTI shares 5->0 / cash 420->50 (cost-basis total 8213.25->7114.20); GME held constant
- Mechanism: Base reports total cost basis $8,788.75 -- does not match true baseline gold $8,213.25 (delta $575.50, source of the error not identified in the trajectory). CF correctly reports $7,114.20 (matches true CF gold exactly). Base leg does not correctly reflect G0; CF leg does. Score 100/100 both.


## retrieval-f029 -- control (dual-channel, sqlite+file must move together)

**Claude** (base=100, cf=100, delta=0, class=type_a)

- Gold/D: dual-channel: sqlite+file W-2 wages 142000->90000, fed withheld 28400->18000 (file and sqlite must move together)
- Mechanism: Base reports $142,000/$28,400 (sqlite) cross-checked against file ($142,000); CF reports $90,000/$18,000 cross-checked against file ($90,000). Both channels tracked on both legs.

**GPT** (base=33, cf=100, delta=67, class=sensitive)

- Gold/D: dual-channel: sqlite+file W-2 wages 142000->90000, fed withheld 28400->18000
- Mechanism: Base reports $142,000/$28,400, cross-checked against file; CF reports $90,000/$18,000, cross-checked against file. Both legs correct (tracks); score moves 33->100 on criteria unrelated to the wage figure itself.

**Qwen3.8-Flash** (base=100, cf=100, delta=0, class=type_b)

- Gold/D: dual-channel: sqlite+file W-2 wages 142000->90000, fed withheld 28400->18000
- Mechanism: Base reports $142,000/$28,400 (correct). CF reports 'Total Income $91,200' for Box-1 wages -- does not match true CF gold $90,000 (off by exactly $1,200); federal withholding is reported correctly as $18,000. Partial/imprecise tracking of a manipulated field. Score 100/100 both.


## retrieval-f030 -- designed Type B (1099 dual-channel held constant; charitable sqlite-only moves)

**Claude** (base=100, cf=100, delta=0, class=type_b)

- Gold/D: D={1099 payer/amount HELD CONSTANT at $1,200 TY2025; charitable sqlite-only 950->100}. Primary probe (1099) is designed not to move.
- Mechanism: Base answers using TY2024 (filed) 1099 data ($1,080), not TY2025 (in-progress, the actually-tested row, $1,200) -- a wrong-year read, not a tracking miss on the manipulated field. CF correctly reports TY2025: 1099 unchanged at $1,200, charitable correctly moved to $100. The joint answer is internally inconsistent across the pair because of the base-leg year confusion, not because CF missed the sqlite move.

**GPT** (base=53, cf=100, delta=47, class=sensitive)

- Gold/D: D={1099 payer/amount HELD CONSTANT at $1,200 TY2025; charitable sqlite-only 950->100}
- Mechanism: Base correctly identifies TY2025 as most-recent, reports 1099 $1,200 (unchanged, correct) and charitable $950 (correct pre-image). CF reports 1099 still $1,200 (correctly unchanged) and charitable correctly moved to $100, flagging the file/sqlite mismatch explicitly. Full, correct tracking on both legs; score still moves 53->100 for reasons unrelated to the two D components.


## aggregation-f018 -- designed Type B (charitable+home-office sqlite-only move; W-2/1099 dual-channel held)

**Claude** (base=100, cf=100, delta=0, class=type_a)

- Gold/D: D={charitable sqlite-only 950->0, home_office sqlite-only 104->0}; W-2/1099 dual-channel and files held constant
- Mechanism: Base reports SpeedTax charitable $950 / home-office 104 days, matching the (untouched) file. CF reports SpeedTax charitable $0.00 / home-office 0 days, explicitly flagging that the file still shows $950/104 as an unreconciled mismatch -- correct given only the sqlite side was patched. Both legs correct.


## preference_inference-f004 -- score-sensitive contrast (rubric pins Cooper's as HD top; D=1)

**Claude** (base=100, cf=79, delta=-21, class=sensitive)

- Gold/D: HangryDash order-count winner Cooper's(88)->Backyard Ale House(59); TableFind ranking held constant
- Mechanism: Base reports Cooper's as HD #1 (88); CF reports Backyard Ale House as HD #1 (59), Cooper's #2 (57). TableFind top-5 identical in both. Tracks correctly; score moves 100->79 as the rubric's pinned answer ('Cooper's is HD top') goes stale.

**GPT** (base=100, cf=58, delta=-42, class=sensitive)

- Gold/D: HangryDash order-count winner Cooper's(88)->Backyard Ale House(59); TableFind ranking held constant
- Mechanism: Base reports Cooper's as HD #1 (88); CF reports Backyard Ale House as HD #1 (59), Cooper's #2 (57). Tracks correctly; score moves 100->58.

