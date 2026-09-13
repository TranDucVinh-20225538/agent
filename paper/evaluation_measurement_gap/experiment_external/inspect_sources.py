#!/usr/bin/env python3
"""Read-only schema/hash inspection for the cross-instrument eligibility audit.

Does not classify E2. Does not run agents. Does not modify evaluators.
Does not import P3 extractors.
"""
from __future__ import annotations

import hashlib
import json
import urllib.request

SOURCES = {
    "webjudge_src": "https://raw.githubusercontent.com/OSU-NLP-Group/Online-Mind2Web/main/src/methods/webjudge_online_mind2web.py",
    "webjudge_agente_results": "https://raw.githubusercontent.com/OSU-NLP-Group/Online-Mind2Web/main/data/evaluation_results/online_mind2web_evaluation_results/webjudge_o4-mini/agente_results.json",
    "webarena_evaluators": "https://raw.githubusercontent.com/web-arena-x/webarena/main/evaluation_harness/evaluators.py",
    "wav_agent_response_evaluator": "https://raw.githubusercontent.com/ServiceNow/webarena-verified/main/src/webarena_verified/core/evaluation/evaluators/agent_response_evaluator.py",
    "tau_env_base": "https://raw.githubusercontent.com/sierra-research/tau-bench/main/tau_bench/envs/base.py",
}


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> None:
    for name, url in SOURCES.items():
        raw = urllib.request.urlopen(url, timeout=60).read()
        print(f"{name}\t{len(raw)}\t{sha256_bytes(raw)}")
        if name == "webjudge_agente_results":
            line = raw.splitlines()[0]
            obj = json.loads(line)
            print("  webjudge_record_keys", sorted(obj.keys()))
            rec = obj.get("image_judge_record")
            print("  n_image_judge_record", len(rec) if isinstance(rec, list) else None)
            if isinstance(rec, list) and rec:
                print("  image_judge_record0_keys", sorted(rec[0].keys()))


if __name__ == "__main__":
    main()
