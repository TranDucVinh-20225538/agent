#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "out" / "stage4_counterfactual_analysis_final"
cells = json.loads((OUT / "_raw_cells.json").read_text())

def final_text_messages(messages_path):
    if not messages_path.is_file():
        return None
    try:
        d = json.loads(messages_path.read_text())
    except Exception as e:
        return None
    msgs = d if isinstance(d, list) else d.get("messages", d)
    for m in reversed(msgs):
        if m.get("role") == "assistant":
            texts = [c.get("text","") for c in m.get("content",[]) if isinstance(c,dict) and c.get("type")=="text"]
            if texts:
                return "\n".join(texts).strip()
    return None

def trunc(x, n=900):
    s = str(x)
    return s[:n] + ("...<trunc>" if len(s) > n else "")

lines = []
by_task = {}
for c in cells:
    b, cf = c["base"], c["cf"]
    if not (b["done"] and cf["done"]):
        continue
    by_task.setdefault(b["task"], []).append(c)

only_gpt_qwen = ["GPT"]  # just regenerate GPT sections
for task in sorted(by_task):
    for c in by_task[task]:
        b, cf = c["base"], c["cf"]
        model = b["model"]
        if model not in only_gpt_qwen:
            continue
        bmsg = final_text_messages(ROOT / b["dir"] / b["task"] / "messages.json") or b.get("final_response")
        cfmsg = final_text_messages(ROOT / cf["dir"] / cf["task"] / "messages.json") or cf.get("final_response")
        lines.append(f"\n----- TASK {task} | {model} -----")
        lines.append(f"BASE score={b['score_raw']}  CF score={cf['score_raw']}")
        lines.append(f"BASE final: {trunc(bmsg,1200)}")
        lines.append(f"CF final:   {trunc(cfmsg,1200)}")

(OUT / "_gpt_fix_dump.txt").write_text("\n".join(lines))
print("done", len(lines))
