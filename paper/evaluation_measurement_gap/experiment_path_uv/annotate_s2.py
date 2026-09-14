#!/usr/bin/env python3
"""Local Stage-2 UI. Target + gallery. Writes CSV after each click."""

from __future__ import annotations

import csv
import json
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
PACK = ROOT / "annotators"
PORT = 8766
LOCK = threading.Lock()
FIELDS = ["item_id", "equivalence", "ts"]


def load_items() -> list[dict]:
    rows = []
    for r in csv.DictReader((PACK / "stage2.csv").open()):
        gal = [x for x in (r.get("gallery_png") or "").split() if x]
        rows.append(
            {
                "item_id": r["item_id"],
                "task": r["task"],
                "task_vi": r.get("task_vi") or "",
                "target_png": r["target_png"],
                "gallery": gal,
            }
        )
    return rows


def labels_path(rater: str) -> Path:
    safe = "".join(c for c in rater if c.isalnum() or c in "-_") or "anon"
    return PACK / f"labels_{safe}_s2.csv"


def load_done(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    out = {}
    for r in csv.DictReader(path.open()):
        if r.get("item_id") and r.get("equivalence"):
            out[r["item_id"]] = r["equivalence"]
    return out


def upsert(path: Path, item_id: str, equivalence: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with LOCK:
        rows = list(csv.DictReader(path.open())) if path.exists() else []
        found = False
        for r in rows:
            if r.get("item_id") == item_id:
                r["equivalence"] = equivalence
                r["ts"] = ts
                found = True
                break
        if not found:
            rows.append({"item_id": item_id, "equivalence": equivalence, "ts": ts})
        tmp = path.with_suffix(".csv.tmp")
        with tmp.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, "") for k in FIELDS})
        tmp.replace(path)


HTML = r"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>U2 Stage 2</title>
<style>
  :root { --bg:#0f1115; --card:#1a1e27; --txt:#e8eaed; --mut:#9aa0a6; --line:#2a3140; }
  * { box-sizing: border-box; }
  body { margin:0; font-family: ui-sans-serif, system-ui, sans-serif; background:var(--bg); color:var(--txt); }
  header { padding:12px 18px; border-bottom:1px solid var(--line); display:flex; gap:16px; align-items:center; flex-wrap:wrap; }
  header label { color:var(--mut); font-size:13px; }
  input { background:#0b0d12; color:var(--txt); border:1px solid var(--line); border-radius:6px; padding:6px 8px; }
  .task { padding:12px 18px; border-bottom:1px solid var(--line); }
  .task .vi { font-size:16px; }
  .task .en { color:var(--mut); font-size:13px; margin-top:4px; }
  .cols { display:grid; grid-template-columns: 42% 1fr; min-height: 55vh; }
  .pane { padding:12px; }
  h2 { margin:0 0 8px; font-size:12px; color:var(--mut); letter-spacing:.04em; text-transform:uppercase; }
  .target { background:#000; display:flex; align-items:center; justify-content:center; min-height:48vh; }
  .target img { max-width:100%; max-height:70vh; object-fit:contain; }
  .grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap:8px; max-height:70vh; overflow:auto; }
  .grid img { width:100%; height:120px; object-fit:cover; background:#000; border:1px solid var(--line); cursor:zoom-in; }
  .grid img:hover { outline:2px solid #3b6cff; }
  .btns { display:flex; gap:8px; padding:12px 18px; border-top:1px solid var(--line); flex-wrap:wrap; }
  button { font:inherit; cursor:pointer; border:0; border-radius:8px; padding:12px 14px; font-weight:600; }
  .eq { background:#1e6b3a; color:#fff; }
  .ne { background:#8b2e2e; color:#fff; }
  .u { background:#5c4a1f; color:#fff; }
  .back { background:#2a3140; color:var(--txt); }
  kbd { background:#0b0d12; border:1px solid var(--line); border-radius:4px; padding:0 5px; font-size:12px; }
  .prog { color:var(--mut); font-size:13px; }
  .done { color:#7dcea0; padding:24px; }
  #zoom { display:none; position:fixed; inset:0; background:rgba(0,0,0,.92); z-index:9; align-items:center; justify-content:center; }
  #zoom.show { display:flex; }
  #zoom img { max-width:96vw; max-height:96vh; }
</style>
</head>
<body>
<header>
  <label>Tên bạn <input id="rater" placeholder="vd. VINH-1" size="12"/></label>
  <button type="button" id="go" style="background:#3b6cff;color:#fff;padding:7px 12px;border-radius:6px;border:0;">Bắt đầu / tiếp</button>
  <span class="prog" id="prog"></span>
</header>
<div class="task">
  <div class="vi" id="vi"></div>
  <div class="en" id="en"></div>
</div>
<div class="cols">
  <div class="pane">
    <h2>Ảnh mục tiêu</h2>
    <div class="target"><img id="tgt" alt="target"/></div>
  </div>
  <div class="pane">
    <h2>Gallery — có tấm nào <em>cùng evidence</em> với ảnh mục tiêu không? (cùng kết quả việc, không chỉ cùng website)</h2>
    <div class="grid" id="gal"></div>
  </div>
</div>
<div class="btns">
  <button class="eq" data-v="EQUIVALENT">EQUIVALENT — có, gallery còn cùng evidence <kbd>1</kbd></button>
  <button class="ne" data-v="NOT_EQUIVALENT">NOT_EQUIVALENT — không tấm nào cùng <kbd>2</kbd></button>
  <button class="u" data-v="UNCLEAR">UNCLEAR <kbd>3</kbd></button>
  <button class="back" id="back">← Trước</button>
</div>
<div id="zoom"><img id="zimg" alt="zoom"/></div>
<script>
let items=[], i=0, hist=[], done={}, busy=false;
const $ = id => document.getElementById(id);
$("rater").value = localStorage.getItem("u2s2_rater") || "";
function state(){ return {rater: $("rater").value.trim() || "anon"}; }
async function start(){
  const s = state();
  if(!s.rater || s.rater==="anon"){ if(!confirm("Chưa nhập tên. Lưu thành anon?")) return; }
  localStorage.setItem("u2s2_rater", s.rater);
  const r = await fetch("/api/next?" + new URLSearchParams(s));
  const j = await r.json();
  items = j.items; i = j.index; hist=[]; done = j.done || {};
  render();
}
function render(){
  $("prog").textContent = items.length ? ("#" + (i+1) + " / " + items.length + " · đã lưu " + Object.keys(done).length) : "";
  if(i>=items.length){ $("vi").innerHTML = "<div class='done'>Xong Stage 2.</div>"; $("en").textContent=""; $("tgt").src=""; $("gal").innerHTML=""; return; }
  const it = items[i];
  $("vi").textContent = it.task_vi || "";
  $("en").textContent = it.task;
  $("tgt").src = "/" + it.target_png;
  $("gal").innerHTML = "";
  (it.gallery||[]).forEach(p => {
    const img = document.createElement("img");
    img.src = "/" + p;
    img.onclick = () => { $("zimg").src = img.src; $("zoom").classList.add("show"); };
    $("gal").appendChild(img);
  });
  if(!(it.gallery||[]).length){
    $("gal").innerHTML = "<div class='prog'>Gallery trống — không có ảnh khác để so.</div>";
  }
}
async function label(v){
  if(busy || i>=items.length || !items.length) return;
  busy = true;
  try {
    const it = items[i];
    const r = await fetch("/api/label", {method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({...state(), item_id: it.item_id, equivalence: v})});
    if(!r.ok) throw new Error("save fail");
    done[it.item_id] = v;
    hist.push(i); i += 1; render();
  } finally { busy = false; }
}
$("go").onclick = start;
$("back").onclick = () => { if(hist.length){ i = hist.pop(); render(); } };
document.querySelectorAll(".btns button[data-v]").forEach(b => b.onclick = () => label(b.dataset.v));
$("zoom").onclick = () => $("zoom").classList.remove("show");
document.addEventListener("keydown", e => {
  if(e.target.tagName==="INPUT") return;
  if(e.key==="1") label("EQUIVALENT");
  if(e.key==="2") label("NOT_EQUIVALENT");
  if(e.key==="3") label("UNCLEAR");
  if(e.key==="Escape") $("zoom").classList.remove("show");
});
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        print(fmt % args, flush=True)

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        u = urlparse(self.path)
        if u.path in ("/", "/index.html"):
            self._send(200, HTML.encode(), "text/html; charset=utf-8")
            return
        if u.path.startswith("/s2_png/") and ".." not in u.path:
            fp = PACK / u.path.lstrip("/")
            if fp.is_file():
                self._send(200, fp.read_bytes(), "image/png")
                return
            self._send(404, b"no png", "text/plain")
            return
        if u.path == "/api/next":
            q = parse_qs(u.query)
            rater = (q.get("rater") or ["anon"])[0]
            items = load_items()
            done = load_done(labels_path(rater))
            idx = 0
            for n, it in enumerate(items):
                if it["item_id"] not in done:
                    idx = n
                    break
            else:
                idx = len(items)
            payload = json.dumps({"index": idx, "done": done, "items": items}).encode()
            self._send(200, payload, "application/json")
            return
        self._send(404, b"no", "text/plain")

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/label":
            self._send(404, b"no", "text/plain")
            return
        n = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(n).decode())
        eq = str(body.get("equivalence") or "")
        item_id = str(body.get("item_id") or "")
        rater = str(body.get("rater") or "anon")
        if eq not in {"EQUIVALENT", "NOT_EQUIVALENT", "UNCLEAR"} or not item_id:
            self._send(400, b"bad", "text/plain")
            return
        upsert(labels_path(rater), item_id, eq)
        self._send(200, b'{"ok":true}', "application/json")


def main() -> None:
    if not (PACK / "stage2.csv").exists():
        raise SystemExit("run join_u2_stage2.py first")
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Stage 2 UI: http://127.0.0.1:{PORT}", flush=True)
    print("CSV: annotators/labels_<ten>_s2.csv", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
