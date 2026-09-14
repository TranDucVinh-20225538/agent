# Path U2 codebook — two-stage human labels

This agent is not an annotator. Do not start labels until R exists for
the sampled OM2W episodes and PNGs are exported.

Isolation DECISIVE is **not** the M1a analogue.
The licensed U2 object is **irrecoverable loss** (stage 2).

## Stage 1 — isolation (task text + one image)

Unit: `(task_id, frame_index)` in released `screenshots[]` order.
Primary split only: `fara7b_om2w_browserbase`.

Does this screenshot contain **decisive visual evidence** that a competent
evaluator would need in order to decide whether the agent completed the task,
*if this were the only screenshot they saw*?

- **DECISIVE:** the frame shows a state or result that, by itself, would
  under-determine the verdict if it were missing and nothing else were shown
  (checkout complete, filter applied, target item visible, form submitted,
  blocking error).
- **NOT_DECISIVE:** navigation chrome, intermediate click, duplicate-looking
  mid-nav, or no task-relevant state.
- **UNCLEAR:** image unreadable or task text does not specify what would count.

Annotators do **not** see `uv_*`, human outcome/process, keep/discard,
relevance scores, or other frames.

This answers **decisive-in-isolation**. It does **not** answer whether the
kept set still contains equivalent evidence.

## Stage 2 — equivalence vs an unlabeled gallery (kept-set check)

Run **after** stage 1. Same annotators. Still no keep/discard tags.

Unit: `(task_id, target_frame, gallery_id)`.

Shown: task text + the **target** image + a **gallery** of other screenshots
from the same episode (order shuffled). Ask:

Does **at least one** gallery image contain the **same determining evidence**
as the target (same task-relevant end-state or fact, not merely the same site)?

- **EQUIVALENT:** yes — a competent evaluator could recover that evidence
  from the gallery without the target.
- **NOT_EQUIVALENT:** no gallery image carries that evidence.
- **UNCLEAR:** cannot tell.

### What the gallery is (lab construction; annotators do not see the rule)

| Target (unblinded, lab only) | Gallery |
|---|---|
| Discard frame with stage-1 DECISIVE | Union of per-criterion keep lists (`group_r.discard_set` complement) |
| Keep frame with stage-1 DECISIVE (foil, same UI) | Other keep frames, excluding the target |

Foils exist so stage 2 is not “only discarded images get a gallery.”
Annotators are not told which row is a foil.

### Lab join (not shown to annotators)

Among **discard** frames only:

| Isolation | Stage 2 vs keep-gallery | Class |
|---|---|---|
| DECISIVE | NOT_EQUIVALENT | **IRRECOVERABLE** — licensed M1a-shape analogue |
| DECISIVE | EQUIVALENT | **REDUNDANT** — evidence also in the kept set |
| DECISIVE | UNCLEAR | hold out of the primary rate |
| not DECISIVE | — | not a loss of determining evidence |

M1a in this paper is gold collected then **removed from the final decision**.
A discarded frame whose twin remains in the keep-set is redundant loss,
not that analogue. Report **both** rates. Do not headline isolation
DECISIVE as U2.

## Sampling

Locked in `SAMPLE_LOCK.md` **before** full 106-R rates. Do not retune
after seeing discard fractions.

## Annotators (locked before full 106-R)

**N = 3** independent humans. Not 2. Not this agent.

Stage-1 / stage-2 labels: majority vote (2 of 3) after UNCLEAR held
out per rater. Primary IRR: **Fleiss' κ** on DECISIVE vs not (stage 1)
and EQUIVALENT vs not (stage 2). Pairwise Cohen's κ is secondary.

Pilot: 6 event episodes (rule in `SAMPLE_LOCK.md`), both stages, all
three annotators, then full sample. Do not change these definitions
after seeing U2 rates except to fix ambiguity found in the pilot.

## Forbidden

LLM-as-annotator. Using `uv_*` or task-level human as DECISIVE.
Calling isolation DECISIVE “M1a transported.” Showing keep/discard tags.
Changing the sample rule after R completes.

## Same codebook on P3-CORE (13 M1a rows)

Apply these Stage-1 / Stage-2 labels, 3 annotators, and Fleiss' κ to
the 13 locked M1a rows in `tab:m1a-s100` / `tab:m1a-join`. Mapping and
frame draw: `experiment_m1a_location/P3_HUMAN.md`. Do not start those
labels until the HPC screenshot bundle exists. This does not change
DECISIVE / EQUIVALENT / IRRECOVERABLE definitions.
