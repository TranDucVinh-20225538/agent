#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(".").resolve()
RESULTS = ROOT / "results"
OUT = ROOT / "out" / "stage4_counterfactual_analysis_final"

cells = json.loads((OUT / "_raw_cells.json").read_text())

def final_text(messages_path):
    if not messages_path.is_file():
        return None
    try:
        d = json.loads(messages_path.read_text())
    except Exception as e:
        return f"<parse error {e}>"
    msgs = d if isinstance(d, list) else d.get("messages", d)
    for m in reversed(msgs):
        if m.get("role") == "assistant":
            texts = [c.get("text","") for c in m.get("content",[]) if isinstance(c,dict) and c.get("type")=="text"]
            if texts:
                return "\n".join(texts).strip()
    return None

lines = []
for c in cells:
    b, cf = c["base"], c["cf"]
    if not (b["done"] and cf["done"]):
        continue
    model, task = b["model"], b["task"]
    b_msg = final_text(RESULTS / b["dir"].split("results/")[-1] / task / "messages.json") if False else final_text(ROOT / b["dir"] / task / "messages.json")
    cf_msg = final_text(ROOT / cf["dir"] / task / "messages.json")
    lines.append(f"\n===== {model} | {task} =====")
    lines.append(f"-- BASE (score={b['score_raw']}) --")
    lines.append((b_msg or "<no text found>")[:2000])
    lines.append(f"-- CF (score={cf['score_raw']}) --")
    lines.append((cf_msg or "<no text found>")[:2000])
    # guest gold summary (raw, truncated)
    bg = b.get("guest")
    cfg = cf.get("guest")
    lines.append(f"-- GUEST base keys: {list(bg.keys()) if isinstance(bg,dict) else bg} --")
    lines.append(f"-- GUEST cf keys: {list(cfg.keys()) if isinstance(cfg,dict) else cfg} --")

(OUT / "_valid_pairs_dump.txt").write_text("\n".join(lines))
print("valid pairs written:", sum(1 for c in cells if c["base"]["done"] and c["cf"]["done"]))
print(len(lines), "lines")
