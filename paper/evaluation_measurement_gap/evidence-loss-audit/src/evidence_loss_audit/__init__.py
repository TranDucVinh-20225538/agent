"""Locate collect-then-filter sites that need human confirmation.

This package does not conclude that evidence was lost.
"""

from .chain import LinkRow, classify_links
from .discard import discard_set, keep_union

__all__ = [
    "LinkRow",
    "classify_links",
    "discard_set",
    "keep_union",
]
