# Gate 0A instrument fixes — regression before/after

## Scope

Harness/bridge only: near-miss XML normalize (5 evidenced shapes), screenshot
no-op, `NO_ACTION_ABORT` / `EXECUTOR_EXCEPTION` terminal rows. No frozen prompt /
grammar / max_steps / stopping-semantics changes beyond those instrument markers.

## Fixtures

`tests/fixtures/gate0a_near_miss/` — raw responses from Flash diagnostic trajs
(contradiction-f022/G1, aggregation-f036/G1, contradiction-f014/G1,
counterfactual-f002/G1, preference_inference-f010/G0, screenshot from
aggregation-f036/G1).

## BEFORE (pristine parser / pristine bash extract)

| Case | Result |
|------|--------|
| shape1 `function=tool_call`+wait | empty codes |
| shape2 `parameter=computer_use` | empty codes |
| shape3 mcp bash via tool_call | pristine extract = None |
| shape4 orphan command | pristine extract = None |
| shape5 `parameter=bash` | pristine extract = None |
| screenshot action | empty codes |
| silent G0/G1 trajs | no PREDICT_CRASH / EMPTY abort terminal |

## AFTER (`normalize_near_miss_xml` + `apply_screenshot_noop` + harness markers)

| Case | Result |
|------|--------|
| shape1 | → `WAIT` |
| shape1 key | → `pyautogui.*` |
| shape2 | → `pyautogui.click` |
| shape3/4/5 | bash command extracted |
| screenshot alone | → `WAIT` no-op |
| click+screenshot | click preserved |
| clean computer_use | untouched |

`unittest tests.test_gate0a_instrument_fixes`: **16 OK**.

## Silent-death provenance

See `out/gate0a_instrument_silent_death_provenance.md` — control-flow gap in
`run_mypcbench` empty-action loop (not an uncaught exception). Fixed with
`NO_ACTION_ABORT` traj row + `EXECUTOR_EXCEPTION` around `env.step`.

## Screenshot corpus

See `out/gate0a_instrument_screenshot_corpus.md` — **22** matches / **18** files
(recurring) → no-op added.
