#!/usr/bin/env python3
"""Download released WebJudge o4-mini judge products + source + task-level human labels."""

from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEST = ROOT / "data"
BASE = (
    "https://raw.githubusercontent.com/OSU-NLP-Group/Online-Mind2Web/main/"
)

FILES = {
    "src/webjudge_online_mind2web.py": (
        "src/methods/webjudge_online_mind2web.py"
    ),
    "human_label.json": (
        "data/evaluation_results/online_mind2web_evaluation_results/"
        "human_label.json"
    ),
    "agente_results.json": (
        "data/evaluation_results/online_mind2web_evaluation_results/"
        "webjudge_o4-mini/agente_results.json"
    ),
    "browser_use_results.json": (
        "data/evaluation_results/online_mind2web_evaluation_results/"
        "webjudge_o4-mini/browser_use_results.json"
    ),
    "claude_computer_use_3.5_results.json": (
        "data/evaluation_results/online_mind2web_evaluation_results/"
        "webjudge_o4-mini/claude_computer_use_3.5_results.json"
    ),
    "claude_computer_use_3.7_results.json": (
        "data/evaluation_results/online_mind2web_evaluation_results/"
        "webjudge_o4-mini/claude_computer_use_3.7_results.json"
    ),
    "operator_results.json": (
        "data/evaluation_results/online_mind2web_evaluation_results/"
        "webjudge_o4-mini/operator_results.json"
    ),
    "seeact_results.json": (
        "data/evaluation_results/online_mind2web_evaluation_results/"
        "webjudge_o4-mini/seeact_results.json"
    ),
}


def main() -> None:
    DEST.mkdir(exist_ok=True)
    (DEST / "src").mkdir(exist_ok=True)
    for name, rel in FILES.items():
        dest = DEST / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        url = BASE + rel
        print("GET", url)
        raw = urllib.request.urlopen(url, timeout=180).read()
        dest.write_bytes(raw)
        print(f"  {name} {len(raw)} {hashlib.sha256(raw).hexdigest()}")


if __name__ == "__main__":
    main()
