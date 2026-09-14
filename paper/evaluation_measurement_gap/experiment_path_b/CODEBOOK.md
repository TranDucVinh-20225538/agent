# Path B2 codebook — human decisive-frame labels

**Do not start labels until screenshots exist for a sampled episode.**
This agent is not an annotator.

## Unit

One screenshot in one WebJudge-scored trajectory, identified by
`(agent_file, task_id, frame_index)` in released `image_judge_record` order.

## Question to the annotator (shown with task text + image only)

Does this screenshot contain **decisive visual evidence** that a competent
evaluator would need in order to decide whether the agent completed the task?

- **DECISIVE:** the frame shows a state or result that, if missing, would
  make the success/failure judgment under-determined (checkout complete,
  filter applied, target item visible, form submitted, error that blocks).
- **NOT_DECISIVE:** navigation chrome, intermediate click, duplicate of
  a later frame, or no task-relevant state.
- **UNCLEAR:** image unreadable or task text does not specify what would
  count.

Annotators do **not** see `Score`, `final_eval`, or keep/discard status.

## Sample (locked before B2 labels; after B1)

B1 found only 10 T=3 cap-hits, so the 80–150 episode target is not a
census of the event. Frozen draw (`sample_b2.py`, seed `20260913`):

- all 10 `hit_cap=1` episodes (Operator);
- 10 Operator `hit_cap=0` nearest `n_qualified` to 50;
- 10 other-agent `hit_cap=0` with ≥1 QUALIFIED frame.

Within cap-hits: **all** discarded frames plus an equal number of kept
qualified frames. Annotators see `b2_annotation_sheet.csv` only.

## IRR

Cohen's κ on DECISIVE vs not (UNCLEAR held out). Pilot 20 episodes before
the main sample. Do not change the codebook after seeing B1 discard rates
except to fix ambiguity found in the pilot.

## Forbidden

LLM-as-annotator. Using `Score≥T` as DECISIVE. Using task-level human
success to label frames.
