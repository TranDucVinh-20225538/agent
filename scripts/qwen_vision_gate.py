#!/usr/bin/env python3
"""Gate: hosted Qwen must accept a 1280×800 screenshot and speak CUA XML.

A text smoke that returns "OK" is not this gate.
Exit 0 = continue to f001. Exit 2 = STOP, blocked_no_vision / no XML.
"""
from __future__ import annotations

import base64
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PNG = ROOT / "results/stage4-retrieval-f001/base/retrieval-f001/step_1_20260826@061248736656.png"


def main() -> int:
    url = os.environ.get("OPENAI_BASE_URL", "").rstrip("/") + "/chat/completions"
    key = os.environ.get("OPENAI_API_KEY", "")
    model = os.environ.get("MYPCBENCH_QWEN_MODEL", "qwen/qwen3.5-35b-a3b")
    if not os.environ.get("OPENAI_BASE_URL"):
        print("FAIL: OPENAI_BASE_URL unset", file=sys.stderr)
        return 2
    if not key or key.startswith("sk-proj-"):
        print("FAIL: OpenRouter key missing; GPT sk-proj- is still in OPENAI_API_KEY", file=sys.stderr)
        return 2
    if not PNG.is_file():
        print(f"FAIL: screenshot missing: {PNG}", file=sys.stderr)
        return 2

    b64 = base64.b64encode(PNG.read_bytes()).decode("ascii")
    payload = {
        "model": model,
        "max_tokens": 512,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "This is a 1280x800 desktop screenshot. "
                            "Reply with one OSWorld XML tool call only, either "
                            "<tool_call><function=computer_use>... or "
                            "<tool_call><function=bash><parameter=command>echo ok"
                            "</parameter></function></tool_call>. No prose."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64}"},
                    },
                ],
            }
        ],
        "extra_body": {"enable_thinking": True},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/TranDucVinh-20225538/agent",
            "X-Title": "MyPCBench Stage 4 Qwen vision gate",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            code = resp.status
    except Exception as e:
        print(f"FAIL: vision request: {e}", file=sys.stderr)
        return 2

    choice = (body.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    text = msg.get("content") or ""
    if not text:
        # some thinking models put text in reasoning / content=None first
        text = json.dumps(msg)[:4000]
    low = text.lower()
    print(f"vision_gate HTTP {code} model={model}")
    print(f"vision_gate_preview={text[:500]!r}")
    if code != 200:
        print("FAIL: not HTTP 200", file=sys.stderr)
        return 2
    if "i'm sorry" in low and "image" in low:
        print("FAIL: image rejected", file=sys.stderr)
        return 2
    xml = (
        "<tool_call>" in text
        or "<function=computer_use>" in text
        or "<function=bash>" in text
        or "computer_use" in low
    )
    if not xml:
        print(
            "FAIL: no CUA XML (computer_use/bash). Text-only OK is not this gate.",
            file=sys.stderr,
        )
        return 2
    print("vision_gate_rc=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
