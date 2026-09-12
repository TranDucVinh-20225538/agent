"""P4-B mechanical transforms. No task_id branch. Applied to natural τ later.

Templates are hashed at Phase 2. They do not author last-responses.
"""
from __future__ import annotations


def c3_del(tau: str, gold: str) -> str:
    """Delete the first gold span; leave remaining text (anchors) intact."""
    if gold not in tau:
        return tau
    return tau.replace(gold, "", 1)


def c4_stale(tau: str, gold: str) -> str:
    """Gold appears only inside well-formed markup, not as a channel remainder."""
    body = tau.replace(gold, "") if gold in tau else tau
    return body.rstrip("\n") + f'\n<function=lookup>{{"q": "{gold}"}}</function>'


def c5_irr(tau: str, distractor_line: str) -> str:
    """Append a same-kind distractor on a separate unanchored line."""
    return tau.rstrip("\n") + "\n" + distractor_line.strip("\n")


def c6_pair(tau: str, distractor_a: str, distractor_b: str) -> tuple[str, str]:
    """Two C5 variants; caller must keep the anchored line identical."""
    return c5_irr(tau, distractor_a), c5_irr(tau, distractor_b)


def chan_unterminated(tau: str) -> str:
    """Unterminated function opener → channel_indeterminate under frozen V1."""
    return tau.rstrip("\n") + "\n<function=lookup"
