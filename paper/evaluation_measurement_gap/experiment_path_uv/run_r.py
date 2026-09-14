#!/usr/bin/env python3
"""Recover UV-shaped R (rubric + per-frame relevance + top-K discard).

Our OpenRouter instance. Not Rosset's unpublished matrix.
Steps 4–10 (outcome judge) are not run. This agent does not annotate U2.

Key: OPENROUTER_API_KEY_LARGE from /Users/cubo/CMU/agent/.env (no .venv).
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import time
import urllib.error
import urllib.request
from io import BytesIO
from pathlib import Path
from string import Template

from PIL import Image

from group_r import K, discard_set, filter_irrelevant_screenshots, group_screenshots_by_criterion
from keys import NAME, load_key

ROOT = Path(__file__).resolve().parent
SHOTS = ROOT / "data" / "screenshots" / "fara7b_om2w_browserbase"
EXPORT = ROOT / "out" / "export_om2w.jsonl"
CACHE = ROOT / "out" / "r_cache"
OUT = ROOT / "out"

RUBRIC_MODEL = "openai/gpt-5.5"
VISION_MODEL = "openai/o4-mini"
CAP_USD = 40.0

RELEVANCE_PROMPT = Template(
    """Task: $task_definition$init_url_context

You are analyzing a screenshot from an agent's trajectory to determine which rubric criteria this screenshot is most relevant to.

**Rubric Criteria:**
$rubric_criteria

**Your Task:**
For EACH criterion listed above, assign a relevance score from 0-10 indicating how much this screenshot helps evaluate that specific criterion.

**Scoring Guidelines:**
- **10**: Screenshot directly shows critical evidence for this criterion (e.g., shows the exact item being searched, cart contents, confirmation page)
- **7-9**: Screenshot shows important contextual information for this criterion (e.g., search results, filters applied, navigation state)
- **4-6**: Screenshot shows somewhat relevant information for this criterion (e.g., related page, partial information)
- **1-3**: Screenshot shows minimal relevance to this criterion (e.g., wrong page, unrelated content)
- **0**: Screenshot is completely irrelevant to this criterion

**Important:**
- A screenshot can be highly relevant to multiple criteria
- Focus on what is VISIBLE in the screenshot, not what the agent claimed to do
- Consider whether the screenshot confirms or contradicts criterion requirements

Please output a JSON object with scores for ALL criteria:

{
 "criterion_0": <score_0_to_10>,
 "criterion_1": <score_0_to_10>,
 ...
 "criterion_N": <score_0_to_10>
}

DO NOT OUTPUT ANYTHING OTHER THAN JSON.
"""
)

RUBRIC_PROMPT = Template(
    """Task: $task
Start URL: $init_url

Extract 4-8 evaluation criteria EXPLICITLY stated in the task. No inferred extras.
JSON only:
{"items": [{"criterion": "...", "description": "..."}, ...]}
"""
)


def chat(key: str, model: str, messages: list, spend: float) -> tuple[str, float]:
    if spend >= CAP_USD:
        raise RuntimeError("spend_cap")
    body = json.dumps(
        {"model": model, "messages": messages, "temperature": 0, "max_tokens": 2048}
    ).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://local.path-uv-r",
            "X-Title": "Path UV R recovery",
        },
        method="POST",
    )
    last_err: Exception | None = None
    payload = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                payload = json.loads(resp.read().decode())
            break
        except urllib.error.HTTPError as exc:
            err = exc.read().decode("utf-8", errors="replace")[:400]
            raise RuntimeError(f"http_{exc.code}:{err}") from exc
        except (TimeoutError, urllib.error.URLError, OSError) as exc:
            last_err = exc
            print(f"  retry {attempt}/3 after {type(exc).__name__}", flush=True)
            time.sleep(5 * attempt)
    if payload is None:
        raise RuntimeError(f"chat_timeout:{last_err!r}") from last_err
    msg = payload["choices"][0]["message"]
    content = msg.get("content")
    if isinstance(content, list):
        text = "".join(
            b.get("text") or "" for b in content if isinstance(b, dict)
        )
    else:
        text = content or ""
    usage = payload.get("usage") or {}
    cost = usage.get("cost")
    if cost is None:
        cost = (
            float(usage.get("prompt_tokens") or 0) * 2e-6
            + float(usage.get("completion_tokens") or 0) * 8e-6
        )
    return text, spend + float(cost)


def parse_json(text: str) -> dict:
    text = text.strip()
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        raise ValueError(f"no json: {text[:200]}")
    return json.loads(m.group(0))


def jpeg_b64(path: Path) -> str:
    im = Image.open(path).convert("RGB")
    buf = BytesIO()
    im.save(buf, format="JPEG", quality=95)
    return base64.b64encode(buf.getvalue()).decode()


def load_export() -> dict[str, dict]:
    rows = {}
    for line in EXPORT.read_text().splitlines():
        r = json.loads(line)
        rows[r["task_id"]] = r
    return rows


def load_cached_results() -> list[dict]:
    rows = []
    for p in CACHE.glob("*.result.json"):
        rows.append(json.loads(p.read_text()))
    rows.sort(key=lambda r: r["task_id"])
    return rows


def write_aggregate(rows: list[dict], spend: float) -> None:
    rows = sorted(rows, key=lambda r: r["task_id"])
    OUT.mkdir(exist_ok=True)
    (OUT / "r_results.jsonl").write_text(
        "\n".join(json.dumps(r) for r in rows) + ("\n" if rows else "")
    )
    n_hit = sum(1 for r in rows if r["n_discard"] > 0)
    (OUT / "r_result.md").write_text(
        f"# Path UV R recovery\n\n"
        f"Instance: OpenRouter `{RUBRIC_MODEL}` + `{VISION_MODEL}` via `{NAME}`.\n"
        f"Not authors' unpublished matrix. K={K}. Steps 4–10 not run.\n\n"
        f"Episodes: {len(rows)}. Any discard: {n_hit}/{len(rows)}.\n"
        f"Spend (reported): ${spend:.3f} (cap ${CAP_USD}).\n"
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--task-id", default=None)
    ap.add_argument(
        "--summarize-only",
        action="store_true",
        help="Rebuild r_results.jsonl / r_result.md from cache; no API.",
    )
    args = ap.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)

    if args.summarize_only:
        rows = load_cached_results()
        spend = max((float(r.get("spend_usd_running") or 0) for r in rows), default=0.0)
        write_aggregate(rows, spend)
        print((OUT / "r_result.md").read_text())
        print(f"jsonl_rows={len(rows)}")
        return

    key = load_key()
    print(f"key_source={NAME} (value hidden)", flush=True)
    meta = load_export()
    tasks = sorted(p.name for p in SHOTS.iterdir() if p.is_dir())
    if args.task_id:
        tasks = [args.task_id]
    if args.limit:
        tasks = tasks[: args.limit]

    spend = 0.0
    cached = load_cached_results()
    if cached:
        spend = max(float(r.get("spend_usd_running") or 0) for r in cached)
        write_aggregate(cached, spend)
    for tid in tasks:
        tdir = SHOTS / tid
        pngs = sorted(tdir.glob("*.png"))
        info = meta.get(tid) or {"instruction": "", "init_url": "", "n_screenshots": len(pngs)}
        done = CACHE / f"{tid}.result.json"
        if done.exists():
            rec = json.loads(done.read_text())
            write_aggregate(load_cached_results(), spend)
            print(f"CACHED {tid} discard={rec.get('n_discard')}", flush=True)
            continue
        print(f"TASK {tid} n={len(pngs)} spend={spend:.3f}", flush=True)
        rub_path = CACHE / f"{tid}.rubric.json"
        if rub_path.exists():
            rubric = json.loads(rub_path.read_text())
        else:
            text, spend = chat(
                key,
                RUBRIC_MODEL,
                [{"role": "user", "content": RUBRIC_PROMPT.substitute(
                    task=info.get("instruction") or tid,
                    init_url=info.get("init_url") or "",
                )}],
                spend,
            )
            rubric = parse_json(text)
            rub_path.write_text(json.dumps(rubric, indent=2))
        items = rubric.get("items") or []
        n_c = len(items)
        crit_txt = ""
        for i, c in enumerate(items):
            crit_txt += f"\n{i}. **{c.get('criterion','')}**\n Description: {c.get('description','')}\n"
        rel: dict[int, dict] = {}
        for png in pngs:
            idx = int(png.stem)
            rel_path = CACHE / f"{tid}.rel.{idx:04d}.json"
            if rel_path.exists():
                rel[idx] = {int(k) if str(k).isdigit() else k: v for k, v in json.loads(rel_path.read_text()).items()}
                continue
            prompt = RELEVANCE_PROMPT.substitute(
                task_definition=info.get("instruction") or tid,
                init_url_context=f"\nStart URL: {info.get('init_url') or ''}",
                rubric_criteria=crit_txt,
            )
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{jpeg_b64(png)}",
                                "detail": "high",
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ]
            text, spend = chat(key, VISION_MODEL, messages, spend)
            raw = parse_json(text)
            scores = {}
            for i in range(n_c):
                v = raw.get(f"criterion_{i}", raw.get(str(i), 0))
                try:
                    scores[i] = int(v)
                except (TypeError, ValueError):
                    scores[i] = 0
            rel_path.write_text(json.dumps(scores))
            rel[idx] = scores
            time.sleep(0.15)
        grouped = filter_irrelevant_screenshots(
            group_screenshots_by_criterion(rel, n_c, K), rel
        )
        disc = discard_set(len(pngs), grouped)
        rec = {
            "task_id": tid,
            "n_frames": len(pngs),
            "n_criteria": n_c,
            "K": K,
            "n_discard": len(disc),
            "discard": disc,
            "grouped": {str(k): v for k, v in grouped.items()},
            "spend_usd_running": round(spend, 4),
            "rubric_model": RUBRIC_MODEL,
            "vision_model": VISION_MODEL,
            "key_source": NAME,
            "note": "our OpenRouter instance; not authors' R",
        }
        (CACHE / f"{tid}.result.json").write_text(json.dumps(rec, indent=2))
        write_aggregate(load_cached_results(), spend)
        print(f"  discard {len(disc)}/{len(pngs)}", flush=True)

    write_aggregate(load_cached_results(), spend)
    print((OUT / "r_result.md").read_text())


if __name__ == "__main__":
    main()
