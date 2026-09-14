#!/usr/bin/env python3
"""Local annotator UI. Stdlib only. Writes CSV after each click."""

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
PNG = PACK / "png"
PORT = 8765

VI = json.loads((PACK / "task_vi.json").read_text())
LOCK = threading.Lock()
FIELDS = ["item_id", "isolation", "ts"]


def load_items(pack: str) -> list[dict]:
    name = "stage1_pilot.csv" if pack == "pilot" else "stage1_all.csv"
    rows = list(csv.DictReader((PACK / name).open()))
    for r in rows:
        r["task_vi"] = VI.get(r["task"], "")
    return rows


def labels_path(rater: str, pack: str) -> Path:
    safe = "".join(c for c in rater if c.isalnum() or c in "-_") or "anon"
    return PACK / f"labels_{safe}_{pack}.csv"


def load_done(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    out = {}
    for r in csv.DictReader(path.open()):
        if r.get("item_id") and r.get("isolation"):
            out[r["item_id"]] = r["isolation"]
    return out


def upsert_label(path: Path, item_id: str, isolation: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with LOCK:
        rows = list(csv.DictReader(path.open())) if path.exists() else []
        found = False
        for r in rows:
            if r.get("item_id") == item_id:
                r["isolation"] = isolation
                r["ts"] = ts
                found = True
                break
        if not found:
            rows.append({"item_id": item_id, "isolation": isolation, "ts": ts})
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
<title>U2 Stage 1</title>
<style>
  :root { --bg:#0f1115; --card:#1a1e27; --txt:#e8eaed; --mut:#9aa0a6; --line:#2a3140; }
  * { box-sizing: border-box; }
  body { margin:0; font-family: ui-sans-serif, system-ui, sans-serif; background:var(--bg); color:var(--txt); }
  header { padding:12px 18px; border-bottom:1px solid var(--line); display:flex; gap:16px; align-items:center; flex-wrap:wrap; }
  header label { color:var(--mut); font-size:13px; }
  input, select { background:#0b0d12; color:var(--txt); border:1px solid var(--line); border-radius:6px; padding:6px 8px; }
  main { display:grid; grid-template-columns: 1fr 340px; min-height: calc(100vh - 54px); }
  .imgwrap { background:#000; display:flex; align-items:center; justify-content:center; overflow:auto; }
  .imgwrap img { max-width:100%; max-height: calc(100vh - 54px); object-fit:contain; }
  aside { padding:16px; border-left:1px solid var(--line); background:var(--card); display:flex; flex-direction:column; gap:12px; }
  h2 { margin:0; font-size:13px; color:var(--mut); font-weight:600; text-transform:uppercase; letter-spacing:.04em; }
  .task { font-size:15px; line-height:1.45; }
  .task.vi { font-size:16px; }
  .task.en { color:var(--mut); font-size:13px; }
  .btns { display:flex; flex-direction:column; gap:8px; margin-top:8px; }
  button { font: inherit; cursor:pointer; border:0; border-radius:8px; padding:12px 14px; text-align:left; font-weight:600; }
  .d { background:#1e6b3a; color:#fff; }
  .n { background:#3d4454; color:#fff; }
  .u { background:#5c4a1f; color:#fff; }
  button:hover { filter:brightness(1.08); }
  button.picked { outline: 2px solid #fff; outline-offset: 2px; }
  .row { display:flex; gap:8px; }
  .row button { flex:1; background:#2a3140; color:var(--txt); font-weight:500; }
  .prog { font-size:13px; color:var(--mut); }
  kbd { background:#0b0d12; border:1px solid var(--line); border-radius:4px; padding:0 5px; font-size:12px; }
  .done { color:#7dcea0; font-size:18px; padding:24px; }
</style>
</head>
<body>
<header>
  <label>Tên bạn <input id="rater" placeholder="vd. an" size="12"/></label>
  <label>Gói
    <select id="pack">
      <option value="pilot">Pilot (~300)</option>
      <option value="all">Tất cả (~1232)</option>
    </select>
  </label>
  <button type="button" id="go" style="background:#3b6cff;color:#fff;padding:7px 12px;border-radius:6px;border:0;">Bắt đầu / tiếp</button>
  <span class="prog" id="prog"></span>
</header>
<main>
  <div class="imgwrap"><img id="img" alt="screenshot"/></div>
  <aside>
    <h2>Việc (tiếng Việt)</h2>
    <div class="task vi" id="vi"></div>
    <h2>English</h2>
    <div class="task en" id="en"></div>
    <div class="btns">
      <button class="d" data-v="DECISIVE">DECISIVE — đủ để biết xong chưa <kbd>1</kbd></button>
      <button class="n" data-v="NOT_DECISIVE">NOT_DECISIVE — chưa đủ / đang giữa đường <kbd>2</kbd></button>
      <button class="u" data-v="UNCLEAR">UNCLEAR — ảnh vỡ / việc mơ hồ <kbd>3</kbd></button>
    </div>
    <div class="row">
      <button type="button" id="back">← Trước <kbd>Backspace</kbd></button>
    </div>
    <div class="prog">File lưu: annotators/labels_TÊN_gói.csv — mỗi lần bấm là ghi ngay.</div>
  </aside>
</main>
<script>
let items=[], i=0, hist=[], done={}, busy=false;
const $ = id => document.getElementById(id);
$("rater").value = localStorage.getItem("u2_rater") || "";
$("pack").value = localStorage.getItem("u2_pack") || "pilot";
function state(){ return {rater: $("rater").value.trim() || "anon", pack: $("pack").value}; }
async function start(){
  const s = state();
  if(!s.rater || s.rater==="anon"){ if(!confirm("Chưa nhập tên. Lưu thành anon?")) return; }
  localStorage.setItem("u2_rater", s.rater);
  localStorage.setItem("u2_pack", s.pack);
  const r = await fetch("/api/next?" + new URLSearchParams(s));
  const j = await r.json();
  items = j.items; i = j.index; hist=[]; done = j.done || {};
  render();
}
function nDone(){ return Object.keys(done).length; }
function render(){
  $("prog").textContent = items.length ? ("#" + (i+1) + " / " + items.length + " · đã lưu " + nDone()) : "";
  document.querySelectorAll(".btns button").forEach(b => b.classList.remove("picked"));
  if(!items.length){ $("vi").innerHTML = "<div class='done'>Hết. Cảm ơn.</div>"; $("en").textContent=""; $("img").src=""; return; }
  if(i>=items.length){ $("vi").innerHTML = "<div class='done'>Xong hết gói này.</div>"; $("en").textContent=""; $("img").src=""; $("prog").textContent = items.length+" / "+items.length + " · đã lưu " + nDone(); return; }
  const it = items[i];
  $("vi").textContent = it.task_vi || "(chưa dịch)";
  $("en").textContent = it.task;
  $("img").src = "/" + it.png;
  const cur = done[it.item_id];
  if(cur) document.querySelectorAll(".btns button").forEach(b => { if(b.dataset.v===cur) b.classList.add("picked"); });
}
async function label(v){
  if(busy || i>=items.length || !items.length) return;
  busy = true;
  try {
    const s = state();
    const it = items[i];
    const r = await fetch("/api/label", {method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({...s, item_id: it.item_id, isolation: v})});
    if(!r.ok) throw new Error("save fail");
    done[it.item_id] = v;
    hist.push(i);
    i += 1;
    render();
  } finally { busy = false; }
}
$("go").onclick = start;
$("back").onclick = () => { if(hist.length){ i = hist.pop(); render(); } };
document.querySelectorAll(".btns button").forEach(b => b.onclick = () => label(b.dataset.v));
document.addEventListener("keydown", e => {
  if(e.target.tagName==="INPUT" || e.target.tagName==="SELECT") return;
  if(e.key==="1") label("DECISIVE");
  if(e.key==="2") label("NOT_DECISIVE");
  if(e.key==="3") label("UNCLEAR");
  if(e.key==="Backspace"){ e.preventDefault(); $("back").click(); }
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
        if u.path.startswith("/png/") and ".." not in u.path:
            fp = PACK / u.path.lstrip("/")
            if fp.is_file():
                self._send(200, fp.read_bytes(), "image/png")
                return
            self._send(404, b"no png", "text/plain")
            return
        if u.path == "/api/next":
            q = parse_qs(u.query)
            rater = (q.get("rater") or ["anon"])[0]
            pack = (q.get("pack") or ["pilot"])[0]
            items = load_items(pack)
            done = load_done(labels_path(rater, pack))
            idx = 0
            for n, it in enumerate(items):
                if it["item_id"] not in done:
                    idx = n
                    break
            else:
                idx = len(items)
            payload = json.dumps(
                {
                    "index": idx,
                    "done": done,
                    "items": [
                        {
                            "item_id": r["item_id"],
                            "task": r["task"],
                            "task_vi": r["task_vi"],
                            "png": r["png"],
                        }
                        for r in items
                    ],
                }
            ).encode()
            self._send(200, payload, "application/json")
            return
        self._send(404, b"no", "text/plain")

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/label":
            self._send(404, b"no", "text/plain")
            return
        n = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(n).decode())
        rater = str(body.get("rater") or "anon")
        pack = str(body.get("pack") or "pilot")
        item_id = str(body.get("item_id") or "")
        isolation = str(body.get("isolation") or "")
        if isolation not in {"DECISIVE", "NOT_DECISIVE", "UNCLEAR"} or not item_id:
            self._send(400, b"bad", "text/plain")
            return
        upsert_label(labels_path(rater, pack), item_id, isolation)
        self._send(200, b'{"ok":true}', "application/json")


def main() -> None:
    if not (PACK / "stage1_pilot.csv").exists():
        raise SystemExit("run make_annotator_pack.py first")
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Annotator UI: http://127.0.0.1:{PORT}", flush=True)
    print("CSV ghi vào annotators/labels_<ten>_<pilot|all>.csv", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
