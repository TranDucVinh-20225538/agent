# Paper 2 — Tier 3 inject-probe gate

Written 2026-09-04T04:41:05.400973+00:00.
Live apply via `cf_inject.py` (not `--probe-only`). Snapshot restore between units.
No agent. No judge. Sealed registry / D untouched.

Group 1 (non-`-I2`): **3** `aggregation-f037` … `preference_inference-f010`
Group 2 (`-I2`): **0**

**Total: 3 PASS / 0 REJECT (identifiability) / 0 REJECT (held-leak) / 0 technical-failure / 1 needs_hand_D_design** (of 4).

### By group

| group | PASS | REJECT_id | REJECT_held | tech |
| --- | ---: | ---: | ---: | ---: |
| group1 non-I2 | 3 | 0 | 0 | 0 |
| group2 -I2 | 0 | 0 | 0 | 0 |

### Skipped — needs hand `D` design (not run)

Inventing `D` under gate time pressure is forbidden (DESIGN.md §2 / frozen review_decision).

- `situated_action-f029`: **needs_hand_D_design** — No invented D. Keep in seal for stratification. After probe may be rejected_not_identifiable. Action/style only.

### Notes (not reclassifications)

- `contradiction-f024` PASS is on a **relative vaultbank** Chili's charge (`2026-03-22`, amount −34.75→−52.125). The frozen component `chilis_receipt_amount` lives on `~/Downloads/Chilis_Receipt_March_2026.txt` (TOTAL $94.28), which current inject cannot patch relatively without an absolute string replace. SpeedTax held. No D rewrite; no forced file absolute patch.
- `aggregation-f037` / `preference_inference-f010` review text allowed REJECT for unstable mail gold; both still PASSed this guest (count 794→714; Jim timestamps shifted; Toby held). REJECT was allowed; it did not occur.

| task_id | group | verdict | gold_moved | fails |
| --- | --- | --- | --- | --- |
| `aggregation-f037` | 1 | PASS | True |  |
| `contradiction-f024` | 1 | PASS | True |  |
| `preference_inference-f010` | 1 | PASS | True |  |
| `situated_action-f029` | 1 | needs_hand_D_design | None | needs_hand_D_design |

