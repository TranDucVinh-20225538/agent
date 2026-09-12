#!/usr/bin/env python3
"""P3-2 label-derivation rule R. Implements spec §13. Nothing else.

A deterministic function of task-side text and a component identifier. No answer
text, no task identifier, no kind, no per-identifier branch. Labels are literals;
callers escape them before the frozen extractor sees them.

Values are locked in the spec. This file does not search.
"""
from __future__ import annotations

import json
import re
from typing import Any

MIN_TOKEN = 2


def norm(s: str) -> str:
    return " ".join(s.casefold().split())


def task_text(instruction: str | None, grading: Any) -> str:
    g = grading if isinstance(grading, str) else json.dumps(grading, ensure_ascii=False)
    return f"{instruction or ''} {g}"


def grounded(label: str, text: str) -> bool:
    return norm(label) in norm(text)


def derive_labels(instruction: str | None, grading: Any, component_id: str) -> list[str]:
    text = task_text(instruction, grading)
    tokens = [t for t in component_id.split("_") if len(t) >= MIN_TOKEN]
    out, seen = [], set()
    for length in range(1, len(tokens) + 1):
        for i in range(len(tokens) - length + 1):
            phrase = " ".join(tokens[i : i + length])
            key = phrase.casefold()
            if key in seen or not grounded(phrase, text):
                continue
            seen.add(key)
            out.append(phrase)
    return out


def escaped_labels(instruction: str | None, grading: Any, component_id: str) -> list[str]:
    """R's labels as the frozen extractor expects them: literals, escaped."""
    return [re.escape(s) for s in derive_labels(instruction, grading, component_id)]
