# Dataset selection funnel

Pre-registered before confirmatory Claude runs. Pilot runs
(retrieval-f001, hard_app-f033, preference_inference-f009, situated_action-f028)
are reported separately and are not used to choose this sample.

Under A–E, `hard_app-f033` is ineligible (HuggingFace category is
`situated_action`, attributable weight 0 in the screen file, rubric not
channel-invariant, `cua_required`). `preference_inference-f009` is
ineligible (not channel-invariant; LibreOffice Writer in the instruction).
Those remain in the pilot log. They are not re-inserted into the
confirmatory sample to keep a favorite result.

- Tasks in release: **184**
- Eligible under A–E: **10**
- Confirmatory sample (k≤3 per type, seed=20260826): **8**

Exclusions are not mutually exclusive; a task may fail several checks.
- not channel-invariant: 142
- no mapped sqlite: 23
- cua_required: 128
- GUI artifact in instruction/rubric/apps: 71
- instruction pins a dollar gold: 1

## Primary exclude reason (first-listed conjunction)

| reason | n |
| --- | ---: |
| `not_channel_invariant|cua_required|gui_artifact|evidence_type_other` | 34 |
| `not_channel_invariant|cua_required|evidence_type_other` | 33 |
| `not_channel_invariant` | 26 |
| `not_channel_invariant|cua_required` | 15 |
| `not_channel_invariant|gui_artifact` | 12 |
| `cua_required|gui_artifact|evidence_type_other` | 11 |
| `cua_required|evidence_type_other` | 7 |
| `not_channel_invariant|no_mapped_sqlite|cua_required|evidence_type_other` | 5 |
| `not_channel_invariant|cua_required|gui_artifact` | 4 |
| `cua_required` | 4 |
| `no_mapped_sqlite|cua_required` | 4 |
| `not_channel_invariant|no_mapped_sqlite|cua_required` | 4 |
| `gui_artifact` | 3 |
| `not_channel_invariant|no_mapped_sqlite|gui_artifact` | 2 |
| `not_channel_invariant|no_mapped_sqlite|cua_required|gui_artifact|evidence_type_other` | 2 |
| `no_mapped_sqlite|cua_required|gui_artifact|evidence_type_other` | 2 |
| `not_channel_invariant|no_mapped_sqlite` | 2 |
| `not_channel_invariant|no_mapped_sqlite|cua_required|gui_artifact` | 1 |
| `no_mapped_sqlite|cua_required|evidence_type_other` | 1 |
| `not_channel_invariant|cua_required|instruction_pins_gold|evidence_type_other` | 1 |
| `not_channel_invariant|evidence_type_other` | 1 |

## Eligible by evidence type

| evidence_type | eligible | in sample |
| --- | ---: | ---: |
| point_field | 5 | 3 |
| aggregation | 2 | 2 |
| multi_record | 2 | 2 |
| contradiction_cross_source | 1 | 1 |

## Selection rule

For each evidence type, sort eligible task ids lexicographically. If n≤3, take all. If n>3, `random.Random(20260826).sample(ids, 3)`.

Do not replace a sampled task that later fails dummy-probe identifiability. Record it as `rejected_not_identifiable` in the sample outcomes.

Do not select on hypothesized support for attribution.

