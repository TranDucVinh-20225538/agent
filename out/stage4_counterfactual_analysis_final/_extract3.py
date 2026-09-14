#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(".").resolve()
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

def trunc(x, n=700):
    s = str(x)
    return s[:n] + ("...<trunc>" if len(s) > n else "")

lines = []
by_task = {}
for c in cells:
    b, cf = c["base"], c["cf"]
    if not (b["done"] and cf["done"]):
        continue
    by_task.setdefault(b["task"], []).append(c)

for task in sorted(by_task):
    lines.append(f"\n\n########## TASK: {task} ##########")
    for c in by_task[task]:
        b, cf = c["base"], c["cf"]
        model = b["model"]
        lines.append(f"\n----- {model} -----")
        lines.append(f"BASE score={b['score_raw']}  CF score={cf['score_raw']}  delta={None if b['score_raw'] is None or cf['score_raw'] is None else (cf['score_raw']-b['score_raw'])}")
        cfg = cf.get("guest") or {}
        lines.append(f"gold_moved={cfg.get('gold_moved')} ok={cfg.get('ok')} fails={cfg.get('fails')}")
        lines.append(f"probe_before: {trunc(cfg.get('probe_before'), 500)}")
        lines.append(f"probe_after:  {trunc(cfg.get('probe_after'), 500)}")
        if cfg.get("extra_probes_before"):
            lines.append(f"extra_before: {trunc(cfg.get('extra_probes_before'), 500)}")
        if cfg.get("extra_probes_after"):
            lines.append(f"extra_after:  {trunc(cfg.get('extra_probes_after'), 500)}")
        if cfg.get("files_before"):
            lines.append(f"files_before: {trunc(cfg.get('files_before'), 300)}")
        if cfg.get("files_after"):
            lines.append(f"files_after:  {trunc(cfg.get('files_after'), 300)}")
        bmsg = final_text(ROOT / b["dir"] / task / "messages.json")
        cfmsg = final_text(ROOT / cf["dir"] / task / "messages.json")
        lines.append(f"BASE final answer: {trunc(bmsg, 900)}")
        lines.append(f"CF final answer:   {trunc(cfmsg, 900)}")

(OUT / "_semantic_dump.txt").write_text("\n".join(lines))
print("written", len(lines), "lines, size bytes:", (OUT/"_semantic_dump.txt").stat().st_size)
