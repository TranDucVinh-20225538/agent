"""Map a found-then-filter extractor onto core discard_set.

Keep-set = items that survived aggregation. Discard-set = items that
entered ``found`` and are absent from the survivor list. Indices are
local to the caller (span ids, screenshot ids, …).
"""

from __future__ import annotations

from typing import Iterable, List, Sequence

from evidence_loss_audit.discard import discard_set


def from_found_and_survivors(
    n_items: int,
    found: Sequence[int],
    survivors: Sequence[int],
) -> List[int]:
    """Discard = found minus survivors, restricted to ``range(n_items)``.

    Items never in ``found`` are not discards (they were not collected).
    """
    grouped = {"survivors": [int(i) for i in survivors]}
    union_discard = discard_set(n_items, grouped)
    collected = {int(i) for i in found}
    return [i for i in union_discard if i in collected]


def last_observation_keep(
    n_items: int, last_indices: Iterable[int]
) -> dict[str, list[int]]:
    """Treat the last scored observation as the sole keep-list."""
    return {"last": sorted({int(i) for i in last_indices if 0 <= int(i) < n_items})}
