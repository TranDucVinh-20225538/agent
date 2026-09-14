# Path B2 sample (frozen before labels)

Seed `20260913`. Primary T=3. `MAX_IMAGE=50`.
Does not use `human_label.json`, `Score`, or `final_eval` for sampling roles
except the mechanical T=3 qualification already in B1.

Episodes: 30 (cap_hit=10, operator_nearmiss=10, other_control=10).
Hidden key frames: 1065. Annotation items: 1065.
Discarded frames in sample: 536.

Annotators receive `b2_annotation_sheet.csv` only (no `in_discard`).
Screenshots are not in the released judge JSON. B2 remains blocked until
v2 `trajectory/*.png` exist for every sampled `(agent_file, task_id)`.
