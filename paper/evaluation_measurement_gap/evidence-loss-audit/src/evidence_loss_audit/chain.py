"""Four links: opportunity / discard / isolation-DECISIVE / IRRECOVERABLE.

Do not collapse the chain. The last two links are human labels. This
module only joins them; it does not invent DECISIVE or EQUIVALENT.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


ISOLATION_OK = frozenset({"DECISIVE", "NOT_DECISIVE", "UNCLEAR", None})
EQUIV_OK = frozenset({"EQUIVALENT", "NOT_EQUIVALENT", "UNCLEAR", None})


@dataclass(frozen=True)
class LinkRow:
    opportunity: bool
    discard: bool
    isolation_decisive: Optional[bool]
    irrecoverable: Optional[bool]
    redundant: Optional[bool]
    hold_out: bool
    note: str


def classify_links(
    *,
    n_items: int,
    keep_cap: int,
    in_discard: bool,
    isolation: Optional[str] = None,
    equivalence: Optional[str] = None,
) -> LinkRow:
    """Join machine links to optional human labels.

    ``isolation`` / ``equivalence`` must be codebook tokens or None.
    IRRECOVERABLE is True only for discard + DECISIVE + NOT_EQUIVALENT.
    None on a human field means that link has not been labeled yet —
    not a machine claim of loss.
    """
    if isolation not in ISOLATION_OK:
        raise ValueError(f"bad isolation label: {isolation!r}")
    if equivalence not in EQUIV_OK:
        raise ValueError(f"bad equivalence label: {equivalence!r}")

    opportunity = int(n_items) > int(keep_cap)
    iso = True if isolation == "DECISIVE" else (
        False if isolation == "NOT_DECISIVE" else None
    )
    hold_iso = isolation == "UNCLEAR"
    hold_eq = equivalence == "UNCLEAR"

    irrecoverable: Optional[bool] = None
    redundant: Optional[bool] = None
    hold_out = False
    note = "machine_only"

    if isolation is None:
        note = "await_stage1"
    elif hold_iso:
        hold_out = True
        note = "stage1_unclear"
    elif not in_discard:
        note = "not_a_discard"
    elif iso is False:
        note = "not_determining"
    elif equivalence is None:
        note = "await_stage2"
    elif hold_eq:
        hold_out = True
        note = "stage2_unclear"
    elif equivalence == "NOT_EQUIVALENT":
        irrecoverable = True
        redundant = False
        note = "irrecoverable"
    else:
        irrecoverable = False
        redundant = True
        note = "redundant"

    return LinkRow(
        opportunity=opportunity,
        discard=bool(in_discard),
        isolation_decisive=iso,
        irrecoverable=irrecoverable,
        redundant=redundant,
        hold_out=hold_out,
        note=note,
    )
