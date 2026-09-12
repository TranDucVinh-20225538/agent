"""P4-C2 mechanical transforms. No task_id branch. Applied to natural τ later.

Working-span vs CLAIM-span are distinct. Does not author last-responses.
Does not copy P4-C or P4-B τ. Does not read traces.
"""
from __future__ import annotations

import re

CLAIM_LINE = re.compile(r"^\s*CLAIM\s*:", re.I)
CLAIM_VALUE = re.compile(r"^(\s*CLAIM\s*:\s*)(.+?)(\s*)$", re.I)


def drop_claim_lines(tau: str) -> str:
    """Remove declared CLAIM lines; leave working text."""
    kept = []
    for raw in tau.split("\n"):
        line = raw.rstrip("\r")
        if not CLAIM_LINE.match(line):
            kept.append(line)
    return "\n".join(kept)


def working_irr(tau: str, distractor_line: str) -> str:
    """Append a non-CLAIM working distractor. Must not change the CLAIM line."""
    return tau.rstrip("\n") + "\n" + distractor_line.strip("\n")


def c6_working_pair(tau: str, distractor_a: str, distractor_b: str) -> tuple[str, str]:
    """Two working-span C5 variants; CLAIM line stays identical."""
    return working_irr(tau, distractor_a), working_irr(tau, distractor_b)


def replace_claim(tau: str, new_value: str) -> str:
    """Rewrite CLAIM remainders. Working lines unchanged."""
    out = []
    for raw in tau.split("\n"):
        line = raw.rstrip("\r")
        m = CLAIM_VALUE.match(line)
        if m:
            out.append(m.group(1) + new_value)
        else:
            out.append(line)
    return "\n".join(out)


def c3_drop_claim(tau: str) -> str:
    """Gold-absent claim channel: no CLAIM line."""
    return drop_claim_lines(tau)


def c4_markup(tau: str, gold: str) -> str:
    """Gold only inside well-formed markup, not as a CLAIM remainder."""
    body = drop_claim_lines(tau)
    if gold:
        body = body.replace(gold, "")
    return body.rstrip("\n") + f'\n<function=lookup>{{"q": "{gold}"}}</function>'


def chan_unterminated(tau: str) -> str:
    """Unterminated function opener → channel_indeterminate under V1*."""
    return tau.rstrip("\n") + "\n<function=lookup"
