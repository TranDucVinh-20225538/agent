"""Load OpenRouter LARGE from the agent .env. Never print the value."""

from __future__ import annotations

import os
from pathlib import Path

AGENT_ENV = Path("/Users/cubo/CMU/agent/.env")
NAME = "OPENROUTER_API_KEY_LARGE"


def load_key() -> str:
    if AGENT_ENV.is_file():
        for line in AGENT_ENV.read_text().splitlines():
            s = line.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, v = s.split("=", 1)
            if k.strip() != NAME:
                continue
            val = v.strip().strip("'").strip('"')
            if val and NAME not in os.environ:
                os.environ[NAME] = val
    val = (os.environ.get(NAME) or "").strip()
    if not val:
        raise SystemExit(f"FAIL: {NAME} unset (looked in {AGENT_ENV}; no .venv)")
    if val.startswith("sk-proj-"):
        raise SystemExit("FAIL: GPT key bound; need OpenRouter LARGE")
    return val
