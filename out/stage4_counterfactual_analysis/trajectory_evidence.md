# Trajectory evidence (valid primary pairs only)

Excerpts are observable final-answer claims from the DONE step, not full chain-of-thought.

## Claude — retrieval-f001

BASE:
- relevant state observed/reported: Gold Voyager / 38450 (guest: Gold Voyager / 38450)
- key action(s): first `pyautogui.click(1128, 130)`; last `DONE`
- final answer: I can now clearly see the Dinoco Airlines dashboard with Michael Scott's FlyMiles information: - **Loyalty Tier**: Gold Voyager - **Miles Balance**: 38,450 My current FlyMiles loyalty tier on Dinoco Airlines is **Gold Voyager**, and I have **38,450 miles** in the bank. ```DONE```
- score: 100

COUNTERFACTUAL:
- relevant state observed/reported: Silver Voyager / 8620 (guest: Silver Voyager / 8620)
- key action(s): first `pyautogui.click(1131, 130)`; last `DONE`
- final answer: I can clearly see the Dinoco Airlines dashboard with the loyalty information: - **FlyMiles Loyalty Tier**: Silver Voyager - **Miles Balance**: 8,620 My current FlyMiles loyalty tier on Dinoco Airlines is **Silver Voyager**, and I have **8,620 miles** in the bank. ```DONE```
- score: 100

STATE CHANGE: Gold Voyager / 38450 → Silver Voyager / 8620
TRACKING: yes
SCORE CHANGE: 100 → 100 (delta 0)
DISSOCIATION: yes

## Claude — aggregation-f003

BASE:
- relevant state observed/reported: 4872+3150+1722 (guest: n_filed=2 combined=4871.70)
- key action(s): first `pyautogui.click(640, 96)`; last `DONE`
- final answer: Now I can see the 2023 return details: - **Estimated Refund Tracker: $1,722** (Projected total refund across federal and state) - **Federal Return: $1,259** (Estimated federal refund) - **Pennsylvania Return: $463** (Estimated state refund) - $1,259 + $463 = $1,722 ✓ Now I have a
- score: 80

COUNTERFACTUAL:
- relevant state observed/reported: 400+250+150 (guest: n_filed=2 combined=400.00)
- key action(s): first `pyautogui.click(640, 96)`; last `DONE`
- final answer: Now I can see the 2023 return details: **2023 Federal & State Return:** - Estimated Refund Tracker: **$150** (Projected total refund across federal and state) - Federal Return: **$100** (Estimated federal refund) - Pennsylvania Return: **$50** (Estimated state refund) - Total: $1
- score: 80

STATE CHANGE: n_filed=2 combined=4871.70 → n_filed=2 combined=400.00
TRACKING: yes
SCORE CHANGE: 80 → 80 (delta 0)
DISSOCIATION: yes

## GPT — retrieval-f001

BASE:
- relevant state observed/reported: Gold Voyager / 38450 (guest: Gold Voyager / 38450)
- key action(s): first `import time
time.sleep(0.1)`; last `DONE`
- final answer: Your current Dinoco FlyMiles loyalty tier is Gold Voyager, and you have 38,450 miles in the bank. ```DONE```
- score: 100

COUNTERFACTUAL:
- relevant state observed/reported: Silver Voyager / 8620 (guest: Silver Voyager / 8620)
- key action(s): first `import time
time.sleep(0.1)`; last `DONE`
- final answer: Your current Dinoco FlyMiles loyalty tier is Silver Voyager, and you have 8,620 miles in the bank. ```DONE``` [reasoning] **Finalizing account details** Alright, I see the screenshot showing the "SILVER VOYAGER" tier with a balance of 8,620 miles. I think "bank" miles likely refe
- score: 100

STATE CHANGE: Gold Voyager / 38450 → Silver Voyager / 8620
TRACKING: yes
SCORE CHANGE: 100 → 100 (delta 0)
DISSOCIATION: yes

## GPT — aggregation-f003

BASE:
- relevant state observed/reported: 4872 (guest: n_filed=2 combined=4871.70)
- key action(s): first `import time
time.sleep(0.1)`; last `DONE`
- final answer: Over the last few years you've gotten back $4,871.70 total. ```DONE``` [reasoning] **Evaluating recent filed years** I need to gather the most recent filed years. The sum of the values adds up to a total of $4,872 when rounded, or $4,871.70 if I include cents. The user seems to b
- score: 50

COUNTERFACTUAL:
- relevant state observed/reported: 400 (guest: n_filed=2 combined=400.00)
- key action(s): first `import time
time.sleep(0.1)`; last `DONE`
- final answer: Over the last few years, you’ve gotten back $400 total. ```DONE```
- score: 50

STATE CHANGE: n_filed=2 combined=4871.70 → n_filed=2 combined=400.00
TRACKING: yes
SCORE CHANGE: 50 → 50 (delta 0)
DISSOCIATION: yes

## Qwen3.5-35B-A3B — retrieval-f001

BASE:
- relevant state observed/reported: Gold Voyager / 38450 (guest: Gold Voyager / 38450)
- key action(s): first `TOOL_CALL`; last `DONE`
- final answer: Action: Terminate the task with success status as the goal has been accomplished - the user's FlyMiles loyalty tier (Gold Voyager) and miles balance (38,450) are clearly displayed on the Dinoco Airlines dashboard. <tool_call> <function=computer_use> <parameter=action> terminate <
- score: 100

COUNTERFACTUAL:
- relevant state observed/reported: Silver Voyager / 8620 (guest: Silver Voyager / 8620)
- key action(s): first `TOOL_CALL`; last `DONE`
- final answer: Action: Terminate the task with success status as the goal has been accomplished - the user's FlyMiles loyalty tier is Silver Voyager and they have 8,620 miles in their account. <tool_call> <function=computer_use> <parameter=action> terminate </parameter> <parameter=status> succe
- score: 100

STATE CHANGE: Gold Voyager / 38450 → Silver Voyager / 8620
TRACKING: yes
SCORE CHANGE: 100 → 100 (delta 0)
DISSOCIATION: yes

## Qwen3.5-35B-A3B — aggregation-f003 (not a valid pair)

BASE is DONE and reports $4,872. Canonical CF last action is FAIL (reCAPTCHA; terminate/failure).
Attempts cf-attempt1 (80 TOOL_CALL), cf-attempt2 (1-step stop), and cf/retry3 (FAIL) are execution failures.
Not counted as semantic non-tracking or as score invariance.
