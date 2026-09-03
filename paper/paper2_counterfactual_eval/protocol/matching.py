"""Paper 2 measurement object: typed match, STS, Paper 1 2×2.

Extracted gold/reported values in. No agent I/O. No writer track.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Any, Mapping


class Kind(str, Enum):
    MONEY_USD = "money_usd"
    INTEGER = "integer"
    CATEGORICAL = "categorical"
    ENTITY = "entity"
    STATE = "state"


class Role(str, Enum):
    DETERMINING = "determining"
    HELD = "held"
    DISTRACTOR = "distractor"


class AlignmentCell(str, Enum):
    TYPE_A = "type_a"
    SCORE_SENSITIVE = "score_sensitive"
    TYPE_B = "type_b"
    LOW_SCORE_MISS_INVARIANT = "low_score_miss_invariant"
    SCORE_MOVED_MISS = "score_moved_miss"


MONEY_ABS_TOL = Decimal("1")
HIGH_SCORE_CUTOFF = 80


def _dec(x: Any) -> Decimal:
    return Decimal(str(x))


def match_money_usd(gold: Any, reported: Any) -> bool:
    """$4,872 matches $4,871.70; $91,200 does not match $90,000."""
    g, r = _dec(gold), _dec(reported)
    if abs(g - r) <= MONEY_ABS_TOL:
        return True
    return round(g) == round(r)


def match_integer(gold: Any, reported: Any) -> bool:
    return int(gold) == int(reported)


def match_categorical(gold: Any, reported: Any) -> bool:
    return str(gold).strip().casefold() == str(reported).strip().casefold()


def match_entity(gold: Any, reported: Any) -> bool:
    return match_categorical(gold, reported)


def match_state(gold: Mapping[str, Any], reported: Mapping[str, Any], key_kinds: Mapping[str, Kind]) -> bool:
    if set(key_kinds) - set(gold):
        raise ValueError("gold missing required state keys")
    if set(key_kinds) - set(reported):
        return False
    for key, kind in key_kinds.items():
        if not match_value(kind, gold[key], reported[key]):
            return False
    return True


def match_value(kind: Kind, gold: Any, reported: Any, *, key_kinds: Mapping[str, Kind] | None = None) -> bool:
    if kind is Kind.MONEY_USD:
        return match_money_usd(gold, reported)
    if kind is Kind.INTEGER:
        return match_integer(gold, reported)
    if kind is Kind.CATEGORICAL:
        return match_categorical(gold, reported)
    if kind is Kind.ENTITY:
        return match_entity(gold, reported)
    if kind is Kind.STATE:
        if key_kinds is None:
            raise ValueError("state match requires key_kinds")
        return match_state(gold, reported, key_kinds)
    raise ValueError(kind)


@dataclass(frozen=True)
class Component:
    id: str
    kind: Kind
    role: Role
    weight: Decimal = Decimal("1")
    key_kinds: tuple[tuple[str, Kind], ...] = ()

    def w(self) -> Decimal:
        if self.role is Role.DISTRACTOR:
            return Decimal("0")
        return self.weight


def sts_leg(components: list[Component], matches: Mapping[str, bool]) -> Decimal:
    num = Decimal("0")
    den = Decimal("0")
    for c in components:
        w = c.w()
        if w == 0:
            continue
        den += w
        if matches[c.id]:
            num += w
    if den == 0:
        raise ValueError("no positive-weight components")
    return num / den


def binary_track(components: list[Component], matches0: Mapping[str, bool], matches1: Mapping[str, bool]) -> bool:
    for c in components:
        if c.w() == 0:
            continue
        if not (matches0[c.id] and matches1[c.id]):
            return False
    return True


def alignment_cell(*, track: bool, s0: int, s1: int) -> AlignmentCell:
    ds = s1 - s0
    if track and ds == 0:
        return AlignmentCell.TYPE_A
    if track and ds != 0:
        return AlignmentCell.SCORE_SENSITIVE
    if (not track) and ds != 0:
        return AlignmentCell.SCORE_MOVED_MISS
    if s0 >= HIGH_SCORE_CUTOFF and s1 >= HIGH_SCORE_CUTOFF:
        return AlignmentCell.TYPE_B
    return AlignmentCell.LOW_SCORE_MISS_INVARIANT
