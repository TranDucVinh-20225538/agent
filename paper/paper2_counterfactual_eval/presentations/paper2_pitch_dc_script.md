# Script — Paper 2 Pitch (`.dc.html`)

**File:** `/Users/cubo/Downloads/Paper 2 Pitch.dc.html`  
**Slides:** 17 · **Thời lượng:** ~25 phút + Q&A  
**Giả định:** Anh Khải đã nghe Paper 1; không kể lại experiment.

---

## Đánh giá deck (ngắn)

**Ổn để present.** Arc rõ, claim hẹp, Layer A/B đúng spec, null scenarios publishable, freeze-before-run đúng chỗ sợ nhất của Paper 2.

| Điểm mạnh | Cần chú ý khi nói |
|---|---|
| Title → for what? → 3-paper arc đúng nhịp | Slide 9: nhấn **illustration only** — đừng để anh tưởng đã có result |
| `argmax S̄ =? argmax STS` là câu hỏi trung tâm đúng | Slide 12: `S̄⁰` = base leg only — nói rõ nếu anh hỏi “có average S0/S1 không?” |
| Scenario 1–4 đều publishable (không chỉ chase inversion) | Slide 16: primitive là thesis-level — chỉ ~20–30s, đừng lecture |
| Slide 17 hỏi đúng: decision utility vs deploy consequence | Tên trên title: `Vin` → nên `Vinh` |

**Không thiếu nội dung cốt lõi.** Phụ lục Q&A đã nằm trong speaker notes slide 17 — không cần thêm slide.

---

## Timing gợi ý

| Block | Slides | Phút |
|---|---|---|
| Mở + Paper 1 | 01–03 | ~3 |
| For what? + arc | 04–06 | ~4 |
| Paper 2 framing | 07–09 | ~4 |
| Design | 10–14 | ~8 |
| Spec + ask | 15–17 | ~6 |
| **Tổng** | | **~25** |

---

## Script từng slide

### 01 · Title

**Trên slide:** From measurement gap to decision consequence

**Nói (~40s):**

> Anh ơi, em xin phép nối tiếp phần Paper 1 tối qua. Hôm nay em không pitch metric hay benchmark mới — em trình bày research direction đang hình dung (Paper 2, và chỗ Paper 3 có thể đứng) và xin ý kiến anh xem hướng này có đủ lớn và đúng câu hỏi “for what?” không.

---

### 02 · Paper 1 recap

**Trên slide:** Completion / State tracking / Score attachment

**Nói (~45s):**

> Paper 1 giữ instruction, interface, judge; chỉ perturb determining set D trong environment. Từ đó tách ba property thường bị gộp: **completion**, **state tracking**, **score sensitivity**. Ba thứ này không đồng nhất — có track đúng mà score không đổi, có score đổi khi track, có score cao dù miss D. Em cố giữ claim hẹp: không nói mọi CUA benchmark đều hỏng.

---

### 03 · Narrow claim

**Trên slide:** High score does not certify grounding in current determining state

**Nói (~25s):**

> Paper 1 không nói “benchmark này broken”. Nó nói: một scalar score, dù cao, không tự chứng minh agent đang bám state hiện tại. Completion, tracking và score attachment là các property có thể tách.

---

### 04 · Next question

**Trên slide:** Not invent a metric → test whether the gap changes which agent is picked

**Nói (~40s):**

> Sau Paper 1, câu hỏi tự nhiên — cũng là câu anh hỏi — là “for what?”. Em không muốn trả lời bằng cách lập tức invent metric. Trước hết phải test: measurement gap có consequence thực tế không, cụ thể là khi lab chọn một agent từ leaderboard.

---

### 05 · Three-paper arc

**Trên slide:** Discovery → Consequence → Solution

**Nói (~50s):**

> Arc ba bước. Paper 1: có gap không — đã xong. Paper 2: gap có làm chọn sai agent không — hôm nay. Paper 3 — chỉ justified nếu Paper 2 đứng — đánh giá thế nào trước khi chọn hoặc deploy. Mỗi paper trả lời một câu bắt buộc sau paper trước, không phải “Paper 1 hay thì làm thêm benchmark”.

---

### 06 · P2 and P3 outline

**Trên slide:** Decision experiment vs conditional protocol

**Nói (~55s):**

> Benchmark được dùng để so sánh, chọn model, claim capability, quyết định deploy. Paper 2 hỏi: trong môi trường stateful — finance, health record, CRM, desktop — agent score cao nhất có phải agent đáng chọn nhất về state-grounded reliability? Paper 3 chỉ có lý do tồn tại nếu Paper 2 cho thấy chọn theo score alone có thể sai: registry D, freeze intervention, paired replay, reliability profile. Là infrastructure cho người khác dùng, không phải leaderboard mới.

---

### 07 · Central question

**Trên slide:** `argmax S̄ =? argmax STS`

**Nói (~40s):**

> Paper 2 không chứng minh lại Paper 1. Paper 2 test phản biện: “score imperfect nhưng agent score cao vẫn thường là agent đáng deploy”. Nếu đúng, phenomenon chỉ là measurement artifact. Nếu sai — ranking đảo — thì có decision consequence.

---

### 08 · Audit vs decision

**Trên slide:** Type A / sensitive / Type B → top-1 selection disagreement

**Nói (~45s):**

> Paper 1 audit instrument. Paper 2 là decision experiment: Rule 1 chọn theo conventional benchmark trên world gốc G₀; Rule 2 chọn theo state tracking trên cùng universe paired interventions. Primary outcome không phải correlation thấp — correlation thấp chưa chắc đổi quyết định. Primary là **top-1 disagreement**.

---

### 09 · Illustrative ranking

**Trên slide:** Score picks A · Tracking picks B *(illustration only)*

**Nói (~40s):**

> Đây chỉ là ví dụ minh họa — chưa phải kết quả. Leaderboard chọn A. Nếu deploy cần agent bám state khi state đổi, B có thể hợp lý hơn. Nếu pattern này xuất hiện trên protocol freeze trước khi chạy, Paper 1 không còn là curiosity — mà là model-selection problem.

---

### 10 · Fresh universe

**Trên slide:** New 𝒯 · sealed agents · gold-moving interventions

**Nói (~70s):**

> Em không giả định inversion sẽ xảy ra. Paper 1 ít pair, task chọn để discover phenomenon, không để rank model — lấy luôn 10 task đó rank sẽ bị accusation post-hoc. Paper 2 cần universe mới, eligibility và agent list đóng trước outcome; Paper 1 data chỉ là motivation và Layer A pilot.
>
> Eligibility đã viết trong spec: sqlite, dv_from_answer, không pin gold, không LibreOffice artifact, không cua_required, loại Paper 1 IDs. Stratify theo state family; N suy ra từ selection rule, không phải KPI “30 task”. Intervention chỉ cần gold-moving và identifiable — không design trap; Claude aggregation-f018 designed Type B mà thành Type A là bài học.

---

### 11 · Layer A

**Trên slide:** Calibration S → P(Y=1)

**Nói (~45s):**

> Layer A — calibration: trên từng paired cell, agent score cao có xu hướng track đúng hơn không? Calibration curve, rank correlation, mixed-effects. Nếu align rất tốt, Paper 1 vẫn đúng ở episode level nhưng benchmark aggregate vẫn đủ để chọn agent — đó là **null quan trọng**, không phải failure.

---

### 12 · Layer B (primary)

**Trên slide:** `M_score = argmax S̄⁰` · `M_STS = argmax STS`

**Nói (~50s):**

> Layer B là primary practical test. S̄⁰ lấy **base leg only** — score trên world gốc, đúng như leaderboard; **không** average S⁰ và S¹. STS trên cùng analysis set valid pairs. Nếu top-1 khác nhau thì có decision consequence. Nếu giống nhau dù calibration yếu thì là middle case: measurement issue chưa đổi selection.

---

### 13 · Scenarios

**Trên slide:** Align / Middle / Disagreement / Exploratory

**Nói (~55s):**

> Em thiết kế Paper 2 để mọi scenario đều publishable. Scenario 1–2 không làm Paper 3 bắt buộc — vẫn là scientific answer. Scenario 3 justify arc sang Paper 3. Scenario 4 — ví dụ retrieval align nhưng aggregation invert — cho thấy cần profile theo state family, không một scalar universal.

---

### 14 · Unit of analysis

**Trên slide:** (M, T, I) · STS trên typed D · ΔS không phải reliability

**Nói (~45s):**

> Đơn vị là (M, T, I). Intervention chỉ đổi D; instruction, UI, judge giữ nguyên. Paper 2 coi state tracking là quantity riêng — STS với gold-matching protocol đã freeze. Score sensitivity vẫn report như Paper 1 nhưng **không** biến ΔS thành “agent reliable”. STS graded trên typed D; Paper 1 Type B là special case STS < 1.

---

### 15 · Frozen spec

**Trên slide:** Six decisions · no new cells run

**Nói (~50s):**

> Em đã đóng sáu quyết định trong `PAPER2_SPEC.md` — chưa chạy agent nào. Khác Paper 1, Paper 2 dễ chết nhất ở accusation “nhìn kết quả rồi mới tạo inversion”. Protocol phải đóng trước. Bước tiếp: sealed list model IDs và task IDs, rồi mới đếm cost legs.

---

### 16 · Primitive

**Trên slide:** Controlled perturbation of determining state

**Nói (~30s):**

> Contribution sâu hơn metric: nếu Paper 2 đứng, community có thể chấp nhận primitive — giống robustness không chỉ đo trên một distribution. STS là quantity **sau** khi chấp nhận primitive, không phải “metric vì nghe hay”.

---

### 17 · Questions (dừng xin ý)

**Trên slide:** Decision utility? Or stronger deployment consequence?

**Nói (~60s):**

> Em dừng ở đây và xin ý kiến anh:
>
> 1. Arc discover → consequence → solution có đủ lớn không?
> 2. Bước Paper 2 — top-1 disagreement trên frozen universe — có đúng chỗ “for what?” không?
> 3. Anh có thấy thiếu loại evidence nào trước khi em freeze \(\mathcal{M}\) và \(\mathcal{T}\) rồi chạy?
>
> Em sẵn sàng nhận null nếu score vẫn đủ chọn agent — nhưng muốn test fair trước khi commit compute.

---

## Phụ lục Q&A (chỉ khi anh hỏi)

**“Paper 1 đã có Claude vs GPT, sao không rank luôn?”**  
→ Paper 1 không pre-register ranking; n nhỏ; task cho audit phenomenon. Confirmatory ranking cần universe mới.

**“STS khác gì binary track Paper 1?”**  
→ STS graded trên typed D (partial credit); ranking dùng aggregate STS; Type B là special case STS < 1.

**“30 task × 5 model?”**  
→ Không phải target. N suy ra từ frozen rule và coverage floor \(n_{\min}\).

**“Paper 3 khi nào?”**  
→ Chỉ khi Paper 2 có selection disagreement hoặc family-level pattern mạnh. Không song song.

**“Deploy consequence thật?”**  
→ Level 3 (STS predict stale errors in production) là paper sau. Paper 2 chỉ cần: wrong agent selected on benchmark.
