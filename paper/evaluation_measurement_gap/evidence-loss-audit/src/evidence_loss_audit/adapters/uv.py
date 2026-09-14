"""Plug-in for one published top-K-per-criterion screenshot verifier.

Copied from the live recovery tree so that tree can keep running.
Default keep-cap K=5. Prompts are this adapter's, not core.

This module does not call an API and does not rewrite a running job.
"""

from __future__ import annotations

from string import Template
from typing import Dict, List

K = 5

# Official screenshot×criterion relevance prompt used by that verifier.
MM_SCREENSHOT_CRITERION_RELEVANCE_PROMPT = Template(
    """Task: $task_definition$init_url_context

You are analyzing a screenshot from an agent's trajectory to determine which rubric criteria this screenshot is most relevant to.

**Rubric Criteria:**
$rubric_criteria

**Your Task:**
For EACH criterion listed above, assign a relevance score from 0-10 indicating how much this screenshot helps evaluate that specific criterion.

**Scoring Guidelines:**
- **10**: Screenshot directly shows critical evidence for this criterion (e.g., shows the exact item being searched, cart contents, confirmation page)
- **7-9**: Screenshot shows important contextual information for this criterion (e.g., search results, filters applied, navigation state)
- **4-6**: Screenshot shows somewhat relevant information for this criterion (e.g., related page, partial information)
- **1-3**: Screenshot shows minimal relevance to this criterion (e.g., wrong page, unrelated content)
- **0**: Screenshot is completely irrelevant to this criterion

**Important:**
- A screenshot can be highly relevant to multiple criteria
- Focus on what is VISIBLE in the screenshot, not what the agent claimed to do
- Consider whether the screenshot confirms or contradicts criterion requirements

Please output a JSON object with scores for ALL criteria:

{
 "criterion_0": <score_0_to_10>,
 "criterion_1": <score_0_to_10>,
 ...
 "criterion_N": <score_0_to_10>
}

DO NOT OUTPUT ANYTHING OTHER THAN JSON.
"""
)

# Short rubric extraction. Not the vendor's full multi-step rubric agent.
RUBRIC_PROMPT = Template(
    """Task: $task
Start URL: $init_url

Extract 4-8 evaluation criteria EXPLICITLY stated in the task. No inferred extras.
JSON only:
{"items": [{"criterion": "...", "description": "..."}, ...]}
"""
)


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
