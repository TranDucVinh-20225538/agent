"""Union-based discard: an item is discarded iff it is in no keep-list."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence


def keep_union(grouped: Mapping[object, Iterable[int]]) -> set[int]:
    keep: set[int] = set()
    for idxs in grouped.values():
        keep.update(int(i) for i in idxs)
    return keep


def discard_set(
    n_items: int, grouped: Mapping[object, Sequence[int]]
) -> List[int]:
    """Return sorted indices in ``range(n_items)`` that no keep-list retained.

    ``grouped`` is any mapping of criterion/key → kept item indices.
    The keep-set is the union of those lists. This function does not
    interpret scores, prompts, or a keep-cap — those belong in an adapter.
    """
    if n_items < 0:
        raise ValueError("n_items must be >= 0")
    keep = keep_union(grouped)
    return [i for i in range(n_items) if i not in keep]
