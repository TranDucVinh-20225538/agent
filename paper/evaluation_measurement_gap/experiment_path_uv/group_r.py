"""Official UV Step-3 grouping. Copied from MMRubricAgent (K=5 default)."""

from __future__ import annotations

from typing import Dict, List

K = 5


def group_screenshots_by_criterion(
    relevance_scores: Dict[int, Dict], num_criteria: int, max_k: int = K
) -> Dict[int, List[int]]:
    grouped: Dict[int, List[int]] = {c: [] for c in range(num_criteria)}
    for screenshot_idx, scores_dict in relevance_scores.items():
        for key, score in scores_dict.items():
            if key == "screenshot_idx":
                continue
            grouped[int(key)].append((int(screenshot_idx), int(score)))
    for c in grouped:
        grouped[c].sort(key=lambda x: (x[1], x[0]), reverse=True)
        grouped[c] = [s for s, _ in grouped[c][:max_k]]
    return grouped


def filter_irrelevant_screenshots(
    grouped: Dict[int, List[int]], relevance_scores: Dict[int, Dict]
) -> Dict[int, List[int]]:
    filtered: Dict[int, List[int]] = {}
    for c_idx, s_indices in grouped.items():
        scored = [
            (s, int(relevance_scores.get(s, {}).get(c_idx, 0))) for s in s_indices
        ]
        high_scores = [s for _, s in scored if s >= 6]
        if not high_scores:
            filtered[c_idx] = s_indices
            continue
        min_high = min(high_scores)
        kept = [
            s for s, score in scored if not (score < 5 and (min_high - score) > 2)
        ]
        filtered[c_idx] = kept if kept else s_indices
    return filtered


def discard_set(n_frames: int, grouped: Dict[int, List[int]]) -> list[int]:
    keep = set()
    for idxs in grouped.values():
        keep.update(idxs)
    return [i for i in range(n_frames) if i not in keep]
