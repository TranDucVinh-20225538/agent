# Counterfactual run — evidence

Agent: `claude_cuabash` / `claude-opus-4-6`  
Backend: QEMU TCG (`-cpu qemu64`, no `-enable-kvm`)  
Host date (UTC): 2026-08-25

`hard_app-f033` was not run in this file.

---

## Task

- id: `retrieval-f001`
- instruction: What's my current FlyMiles loyalty tier on Dinoco and how many miles do I have in the bank?
- apps: Dinoco Airlines
- task file: `external/MyPCBench-main/tasks/cf_retrieval/one.json`
- source: `cf/tasks/retrieval-f001.json`

Rubric criteria (weights 0.4 / 0.4 / 0.2):

1. Agent reads Michael's FlyMiles loyalty tier directly from the live Dinoco profile (not inferred from email or other apps)
2. Agent reads Michael's current FlyMiles miles balance directly from the live Dinoco profile
3. Agent reports the loyalty tier and miles balance together in a single answer

---

## Intervention

Applied only on the after run, after `_prewarm_lazy_dbs`, before the first agent action, via `scripts/cf_inject.py` (guest `sqlite3` through Control API `POST /execute`).

```
UPDATE loyalty SET status = 'Silver Voyager', miles = 8620, miles_ytd = 8620 WHERE user_email = 'michael.scott@dundermifflin.com'
```

Probe:

```
SELECT status, miles, miles_ytd FROM loyalty WHERE user_email = 'michael.scott@dundermifflin.com'
```

Database: `/data/dinoco-airlines.sqlite`  
Record: `results/cf-retrieval-f001/retrieval-f001.guest.json`  
`gold_moved`: true

Before-run used the same probe with `--probe-only` (no UPDATE).

---

## Comparison

| Item | Before | After |
|------|--------|-------|
| Database value | `Gold Voyager`, miles `38450`, miles_ytd `14280` | `Silver Voyager`, miles `8620`, miles_ytd `8620` |
| Agent answer | FlyMiles Loyalty Tier: Gold Voyager. Miles Balance: 38,450. | Loyalty Tier: Silver Voyager. Miles Balance: 8,620. |
| Rubric score | 100 (`final_fraction` 1.0) | 100 (`final_fraction` 1.0) |
| Pass/fail | pass | pass |
| Completion `result.txt` | 1.0 | 1.0 |
| Judge | per-step max-reduce, `claude-sonnet-4-6`, 4/4 steps scored | per-step max-reduce, `claude-sonnet-4-6`, 6/6 steps scored |
| per_rubric_max | [1, 1, 1] | [1, 1, 1] |

---

## Before

### Database

`cf_inject.py --probe-only` stdout during prewarm:

```
probe before: [{"status":"Gold Voyager","miles":38450,"miles_ytd":14280}]
```

Copy: `results/base-retrieval-f001/retrieval-f001.guest.json`

### Agent answer (traj step 3, action `DONE`)

```
The Dinoco Airlines dashboard is now loaded and shows the information clearly:

- **FlyMiles Loyalty Tier:** Gold Voyager
- **Miles Balance:** 38,450

Your current FlyMiles loyalty tier on Dinoco Airlines is **Gold Voyager**, and you have **38,450 miles** in the bank.
```

### Trajectory

`external/MyPCBench-main/results/base-retrieval-f001/retrieval-f001/traj.jsonl`

| step | action | screenshot |
|------|--------|------------|
| 1 | `pyautogui.click(1128, 130)` | `step_1_20260825@184205891265.png` |
| 2 | `pyautogui.click(640, 96)` | `step_2_20260825@184218784373.png` |
| 2 | `pyautogui.tripleClick(640, 96)` | `step_2_20260825@184224007146.png` |
| 3 | `DONE` | `step_3_20260825@184234392633.png` |

Also: `messages.json`, `usage.json` (`input_tokens` 12, `output_tokens` 349).

### Screenshots

Directory: `external/MyPCBench-main/results/base-retrieval-f001/retrieval-f001/`

- `step_1_20260825@184205891265.png`
- `step_2_20260825@184218784373.png`
- `step_2_20260825@184224007146.png`
- `step_3_20260825@184234392633.png`

### Rubric

- bundle: `rubric_bundle.json`
- judge raw: `rubric_judge_result.json` → `{"result": 100}`
- detail: `rubric_result.json`
- aggregate: `../scores.json` → `avg_score` 1.0, `perfect` 1
- pass/fail: pass

Harness wall (UTC): start `2026-08-25T18:30:45Z`, QEMU `18:30:49`, Control API `18:41:05`, completion `18:42:41`, exit 0.

---

## After

### Database

Guest sqlite3 via Control API, same probe, immediately after UPDATE and before the agent:

```
probe before: [{"status":"Gold Voyager","miles":38450,"miles_ytd":14280}]
probe after:  [{"status":"Silver Voyager","miles":8620,"miles_ytd":8620}]
```

`gold_moved`: true  
File: `results/cf-retrieval-f001/retrieval-f001.guest.json`

### Agent answer (traj step 6, action `DONE`)

```
I can now clearly see the Dinoco Airlines dashboard with Michael Scott's FlyMiles information:

- **Loyalty Tier:** Silver Voyager
- **Miles Balance:** 8,620

My current FlyMiles loyalty tier on Dinoco Airlines is **Silver Voyager**, and I have **8,620 miles** in the bank.
```

### Trajectory

`external/MyPCBench-main/results/cf-retrieval-f001/retrieval-f001/traj.jsonl`

| step | action | screenshot |
|------|--------|------------|
| 1 | `pyautogui.click(1131, 130)` | `step_1_20260825@185518196930.png` |
| 2 | `pyautogui.click(640, 96)` | `step_2_20260825@185528098519.png` |
| 3 | `pyautogui.sleep(2)` | `step_3_20260825@185536240180.png` |
| 4 | `pyautogui.press('esc')` | `step_4_20260825@185547295548.png` |
| 5 | `pyautogui.click(640, 444)` | `step_5_20260825@185555737252.png` |
| 6 | `DONE` | `step_6_20260825@185605780840.png` |

Also: `messages.json`, `usage.json` (`input_tokens` 15, `output_tokens` 538).

### Screenshots

Directory: `external/MyPCBench-main/results/cf-retrieval-f001/retrieval-f001/`

- `step_1_20260825@185518196930.png`
- `step_2_20260825@185528098519.png`
- `step_3_20260825@185536240180.png`
- `step_4_20260825@185547295548.png`
- `step_5_20260825@185555737252.png`
- `step_6_20260825@185605780840.png`

### Rubric

- bundle: `rubric_bundle.json`
- judge raw: `rubric_judge_result.json` → `{"result": 100}`
- detail: `rubric_result.json`
- aggregate: `../scores.json` → `avg_score` 1.0, `perfect` 1
- pass/fail: pass
- per-step scores: steps 1–3 all `[0,0,0]`; step 4 `[1,1,0]`; step 5 `[1,1,0]`; step 6 `[1,1,1]`

Harness wall (UTC): start `2026-08-25T18:43:26Z`, QEMU `18:43:43`, Control API `18:53:54`, inject `18:55:06`, completion `18:56:12`, exit 0.

---

## Unexpected behavior

- `/dev/kvm` exists but is not writable. QEMU stderr: `Could not access KVM kernel module: Permission denied`; then `falling back to tcg`. Both runs used `-cpu qemu64` and no `-enable-kvm`.
- Pinned qcow2 warning on both runs: image baked `2026-08-21T05:00:12Z`, age ~110h, `MYPCBENCH_SKIP_QCOW2_REFRESH=1`.
- `GEMINI_API_KEY` unset. `judge_results.py` used the Anthropic fallback (`MYPCBENCH_JUDGE_FLAVOR` per-step, model `claude-sonnet-4-6`), not `gemini-3.1-flash-lite-preview`.
- `cf_inject.py --probe-only` prints the SELECT result and does not write `{task}.guest.json`. Baseline probe was copied from harness stdout into `results/base-retrieval-f001/retrieval-f001.guest.json`.
- `result.txt` = `1.0` is the harness completion marker, not the rubric score. Rubric lives in `rubric_result.json` / `scores.json`.
- Verified patch also sets `miles_ytd = 8620`; it is not only `status` and `miles`.
- Baseline traj has two rows with `step_num` 2 (click then tripleClick).
- During TCG boot, Control API execute returned `Connection reset by peer` three times before `/health`; same pattern as the dummy sanity boot.
