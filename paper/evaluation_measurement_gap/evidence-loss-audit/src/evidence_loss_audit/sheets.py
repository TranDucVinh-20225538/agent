"""Two-stage annotation packets: blind Stage 1 + foil gallery Stage 2.

Annotator columns never include keep/discard/verdict. Lab keys are
written separately.
"""

from __future__ import annotations

import random
from typing import Iterable, Mapping, Sequence


def build_stage1(
    *,
    event: Sequence[Mapping],
    control: Sequence[Mapping] | None = None,
    seed: int = 20260913,
    control_frame_cap: int = 10,
    item_prefix: str = "S1",
) -> tuple[list[dict], list[dict]]:
    """Return ``(lab_key_rows, annotator_rows)``.

    Each event mapping needs ``episode_id``, ``n_items``, ``discard``
    (iterable of indices). Keep foils: ``min(n_discard, n_keep)`` keep
    indices, RNG without replacement.
    """
    rng = random.Random(seed)
    st1: list[dict] = []
    control = control or []

    def _append(row: dict, frame: int, in_discard: int, reason: str) -> None:
        st1.append(
            {
                "role": row["role"],
                "episode_id": row["episode_id"],
                "n_items": row["n_items"],
                "n_discard": row["n_discard"],
                "n_keep": row["n_keep"],
                "pilot": row.get("pilot", 0),
                "frame_index": int(frame),
                "in_discard": int(in_discard),
                "reason": reason,
            }
        )

    for raw in event:
        disc = sorted(int(i) for i in (raw.get("discard") or []))
        disc_set = set(disc)
        n = int(raw["n_items"])
        keep = [i for i in range(n) if i not in disc_set]
        row = {
            "role": "event",
            "episode_id": raw["episode_id"],
            "n_items": n,
            "n_discard": len(disc),
            "n_keep": len(keep),
            "pilot": int(raw.get("pilot") or 0),
        }
        keep_s = keep[:]
        rng.shuffle(keep_s)
        keep_s = keep_s[: min(len(disc), len(keep_s))]
        for i in disc:
            _append(row, i, 1, "all_discard")
        for i in keep_s:
            _append(row, i, 0, "matched_keep")

    for raw in control:
        n = int(raw["n_items"])
        disc = sorted(int(i) for i in (raw.get("discard") or []))
        row = {
            "role": "control",
            "episode_id": raw["episode_id"],
            "n_items": n,
            "n_discard": len(disc),
            "n_keep": n - len(disc),
            "pilot": 0,
        }
        pool = list(range(n))
        rng.shuffle(pool)
        for i in pool[: min(control_frame_cap, n)]:
            _append(row, i, 0, "control_frame")

    sheet = st1[:]
    rng.shuffle(sheet)
    ann = []
    for n, row in enumerate(sheet, start=1):
        ann.append(
            {
                "item_id": f"{item_prefix}-{n:04d}",
                "episode_id": row["episode_id"],
                "frame_index": row["frame_index"],
            }
        )
    return st1, ann


def build_stage2(
    *,
    decisive_targets: Sequence[Mapping],
    keep_by_episode: Mapping[str, Sequence[int]],
    seed: int = 20260913,
    item_prefix: str = "S2",
) -> tuple[list[dict], list[dict]]:
    """Stage-2 packets for isolation-DECISIVE targets.

    ``decisive_targets`` lab rows need ``episode_id``, ``frame_index``,
    ``in_discard``. Gallery for a discard target = keep-set. Gallery for
    a keep target (foil) = other keep frames. Annotators do not see the
    rule.
    """
    rng = random.Random(seed)
    lab: list[dict] = []
    for raw in decisive_targets:
        eid = raw["episode_id"]
        target = int(raw["frame_index"])
        in_discard = int(raw.get("in_discard") or 0)
        keep = [int(i) for i in keep_by_episode.get(eid, [])]
        if in_discard:
            gallery = [i for i in keep]
            kind = "discard_vs_keep"
        else:
            gallery = [i for i in keep if i != target]
            kind = "keep_foil"
        g = gallery[:]
        rng.shuffle(g)
        lab.append(
            {
                "episode_id": eid,
                "target_frame": target,
                "in_discard": in_discard,
                "gallery_kind": kind,
                "gallery": g,
            }
        )
    rng.shuffle(lab)
    ann = []
    for n, row in enumerate(lab, start=1):
        ann.append(
            {
                "item_id": f"{item_prefix}-{n:04d}",
                "episode_id": row["episode_id"],
                "target_frame": row["target_frame"],
                "gallery": list(row["gallery"]),
            }
        )
    return lab, ann


def majority_label(labels: Iterable[str], *, hold: str = "UNCLEAR") -> str | None:
    """Majority of non-hold labels. None if no majority or <2 votes."""
    votes = [x for x in labels if x and x != hold]
    if len(votes) < 2:
        return None
    counts: dict[str, int] = {}
    for v in votes:
        counts[v] = counts.get(v, 0) + 1
    top = max(counts.values())
    winners = [k for k, c in counts.items() if c == top]
    if len(winners) != 1 or top < 2:
        return None
    return winners[0]
