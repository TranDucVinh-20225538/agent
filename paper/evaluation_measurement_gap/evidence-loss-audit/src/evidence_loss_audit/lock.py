"""SAMPLE_LOCK-style episode draw and lock-file renderer.

Sort identifiers before any RNG. Census if |E| ≤ 40, else sample 40
events + min(20, |C|) nearest-median controls. Control ties: stable
(abs(n − median), id) — no extra RNG.
"""

from __future__ import annotations

import random
import statistics
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence


DEFAULT_SEED = 20260913
CENSUS_MAX = 40
CONTROL_MAX = 20


@dataclass(frozen=True)
class Episode:
    episode_id: str
    n_items: int
    n_discard: int


@dataclass
class Draw:
    seed: int
    event: list[Episode]
    control: list[Episode]
    census: bool
    pilot_ids: list[str] = field(default_factory=list)

    @property
    def n_event(self) -> int:
        return len(self.event)

    @property
    def n_control(self) -> int:
        return len(self.control)


def by_id(rows: Iterable[Episode]) -> list[Episode]:
    return sorted(rows, key=lambda r: r.episode_id)


def pick_controls(
    C: Sequence[Episode], event: Sequence[Episode], n_ctrl: int
) -> list[Episode]:
    """Nearest |n_items − median(E)|; ties broken by episode_id."""
    if n_ctrl <= 0 or not C:
        return []
    med = statistics.median(int(r.n_items) for r in event)
    ranked = sorted(C, key=lambda r: (abs(int(r.n_items) - med), r.episode_id))
    return list(ranked[:n_ctrl])


def draw_episodes(
    rows: Sequence[Episode],
    *,
    seed: int = DEFAULT_SEED,
    keep_cap: int = 5,
    census_max: int = CENSUS_MAX,
    control_max: int = CONTROL_MAX,
    pilot_n: int = 6,
) -> Draw:
    rows = by_id(rows)
    E = by_id([r for r in rows if int(r.n_discard) >= 1])
    C = by_id(
        [r for r in rows if int(r.n_discard) == 0 and int(r.n_items) > keep_cap]
    )
    rng = random.Random(seed)
    census = len(E) <= census_max
    if census:
        event = list(E)
    else:
        event = by_id(rng.sample(list(E), census_max))
    n_ctrl = min(control_max, len(C))
    control = by_id(pick_controls(C, event, n_ctrl))
    event = by_id(event)
    pilot = [r.episode_id for r in event[:pilot_n]]
    return Draw(
        seed=seed,
        event=event,
        control=control,
        census=census,
        pilot_ids=pilot,
    )


def render_lock_md(
    *,
    seed: int = DEFAULT_SEED,
    keep_cap: int = 5,
    annotators: int = 3,
    extra: dict[str, Any] | None = None,
) -> str:
    extra = extra or {}
    lines = [
        "# Sample lock — freeze before seeing discard rates",
        "",
        f"**Status:** LOCKED. Seed `{seed}`.",
        f"**Annotators:** {annotators} (Fleiss' κ + majority).",
        "Do not rewrite after rates exist.",
        "",
        "## After the intermediate state exists — episode draw",
        "",
        "Let `E` = episodes with `n_discard >= 1`.",
        f"Let `C` = episodes with `n_discard == 0` and `n_items > {keep_cap}`.",
        "",
        "| If | Draw |",
        "|---|---|",
        f"| \\|E\\| ≤ {CENSUS_MAX} | Census all of `E`. Controls: `min({CONTROL_MAX}, \\|C\\|)` from `C`, nearest `n_items` to median(`E`); ties broken by stable id order (no extra RNG). |",
        f"| \\|E\\| > {CENSUS_MAX} | `Random({seed}).sample(E, {CENSUS_MAX})`. Controls: {CONTROL_MAX} from `C` by the same nearest-median + id tie-break. |",
        "",
        "Sort ids **before** building `E`/`C` or consuming the RNG.",
        "Census / 40+20 stays when `|E|` is known; record `|E|` as a check,",
        "not a new draw.",
        "",
        "## Primary number",
        "",
        "P(IRRECOVERABLE | sampled discard). Isolation-DECISIVE is secondary.",
        "This lock does not conclude that evidence was lost.",
        "",
    ]
    for k, v in extra.items():
        lines.append(f"- {k}: {v}")
    if extra:
        lines.append("")
    return "\n".join(lines)
