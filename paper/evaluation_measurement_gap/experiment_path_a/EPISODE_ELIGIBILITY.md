# Episode eligibility (locked before extractor / rates)

**Status:** LOCKED 2026-09-13.  
Applies only to **family-ADMIT** trajectories (`I_LOCK.md`). Family membership does not change.

Confirmatory rates use the **eligible** subset, not 498.

---

## Codes

| Code | When | In confirmatory ABSTAIN-vs-\(V\) denominator? |
|---|---|---|
| EXEC_FAIL | harness/episode crash, not an observation outcome | **No** |
| ELIGIBLE | episode can be observed under locked \(I\) | **Yes** |

EXEC_FAIL is not ABSTAIN and not MISS. Same role as P1 execution failures.

---

## Rule (evaluated before \(I\), without \(V\) or human \(L\))

An admitted trajectory is **EXEC_FAIL** if any of:

1. top-level `valid` is `False`
2. `summary_info.err_msg` is a non-empty string (after strip); `None` / `""` are not crashes
3. `steps` is missing or `len(steps) == 0`

Otherwise **ELIGIBLE**.

Not EXEC_FAIL (do not over-fire):

- trailing step with `action is None` after real actions (BrowserGym terminal observation)
- `n_steps == 1` with a real action (e.g. only `goto`)
- empty last answer on an otherwise intact episode → later **ABSTAIN**, still ELIGIBLE

The AssistantBench sample with `err_msg` set is EXEC_FAIL even if `valid is True` and steps exist.

---

## Columns (do not pool)

| Table | Universe | Counted |
|---|---|---|
| ABSTAIN vs released oracle \(V\) | ELIGIBLE among 498 ADMIT | \(I\) empty/missing? |
| HIT/MISS vs official gold | ELIGIBLE WA/VWA `string_match`/`url_match` only, after `reference_answers` / `reference_url` | correspondence |
| AssistantBench HIT/MISS | ELIGIBLE among 132, **only** with official Yoran gold file | not human ARB labels |

Human `trajectory_success` is a **sensitivity** slice (Lù object), not primary \(L\).

\(V\) = `summary_info.cum_reward` on **this released run**. Wording: *released oracle \(V\) on this trajectory.* Not “WebArena published score.” Unused on STOP families.
