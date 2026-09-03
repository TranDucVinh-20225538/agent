# Script present — Research arc & Paper 2 (anh Khải)

**Thời lượng gợi ý:** ~25–30 phút (Part 1 ~10 phút, Part 2 ~15 phút, Q&A)  
**Giả định:** Anh Khải đã đọc / nghe phần Paper 1 tối qua. Không giải thích lại toàn bộ experiment.

---

## PART 1 — Câu chuyện tiếp theo sau Paper 1

### Slide 1 — Title

**Trên slide:** *Sau Paper 1: từ measurement gap đến decision consequence*  
Vin Duc Tran · [ngày present]

**Nói:**

> Anh ơi, em xin phép nối tiếp phần Paper 1 tối qua. Hôm nay em không pitch metric hay benchmark mới. Em muốn trình bày research direction em đang hình dung — gồm Paper 2 và chỗ Paper 3 có thể đứng — và xin ý kiến anh xem hướng này có đủ lớn và đúng câu hỏi “for what?” không.

---

### Slide 2 — Paper 1 recap (30 giây)

**Trên slide:** Benchmark thường đo một episode → completion / score. Một episode không trực tiếp test: *nếu determining state đổi, agent có reflect state mới không?*

**Nói:**

> Paper 1 giữ instruction, interface, judge; chỉ perturb determining set D trong environment. Từ đó em tách ba property thường bị gộp chung: **completion**, **state tracking**, và **score sensitivity / score attachment**. Kết quả: ba thứ này **không đồng nhất** — có track đúng mà score không đổi, có score đổi khi track, có score cao dù miss D.

---

### Slide 3 — Kết luận Paper 1 (hẹp)

**Trên slide:**  
Không phải: “Benchmark này broken.”  
Mà: *High score không certify agent đã grounded vào determining state hiện tại.*

**Nói:**

> Em cố giữ claim hẹp. Paper 1 không nói mọi CUA benchmark đều hỏng. Nó nói: **một scalar score, dù cao, không tự chứng minh agent đang bám state hiện tại**. Completion, tracking, và score attachment là các property **có thể tách**.

---

### Slide 4 — Câu hỏi tiếp theo

**Trên slide:**  
Không phải: “Em sẽ đề xuất metric mới.”  
Mà: *Gap này có ảnh hưởng quyết định chọn agent để deploy không?*

**Nói:**

> Sau Paper 1, câu hỏi tự nhiên — cũng là câu anh hỏi — là **“for what?”**. Em không muốn trả lời bằng cách lập tức invent metric. Trước hết phải test: **measurement gap có consequence thực tế không**, cụ thể là khi lab **chọn một agent** từ leaderboard.

---

### Slide 5 — Arc 3 bước

**Trên slide:**

```
Paper 1: Is there a problem?     → Discovery
Paper 2: Does it affect decisions? → Consequence  
Paper 3: How should we evaluate?   → Solution (nếu P2 đứng)
```

**Nói:**

> Em hình dung arc ba bước. Paper 1: **có gap không**. Paper 2: **gap có làm chọn sai agent không**. Paper 3 — chỉ justified nếu Paper 2 đứng — **đánh giá thế nào trước khi chọn/deploy**. Mỗi paper trả lời một câu bắt buộc phải xuất hiện sau paper trước, không phải “Paper 1 hay → làm thêm benchmark”.

---

### Slide 6 — Paper 2 preview

**Trên slide:**  
Quyết định: chọn agent nào trong {A, B, C, …}  
Theo benchmark score → Winner\_Score  
Theo state tracking trên paired interventions → Winner\_Tracking  
**Hai winner có cùng một agent không?**

**Nói:**

> Benchmark được dùng để **so sánh, chọn model, claim capability, quyết định deploy**. Paper 2 hỏi: nếu môi trường **stateful** — finance, health record, CRM, personal desktop — thì **agent score cao nhất có phải agent đáng chọn nhất về state-grounded reliability không?** Đó là decision experiment, không phải audit thêm phenomenon.

---

### Slide 7 — Paper 3 preview (conditional)

**Trên slide:**  
Primitive: *State-grounded reliability cannot be established from one realized episode.*  
Cần **controlled perturbation** của determining state D.  
Paper 3 = protocol chuẩn để lab/benchmark maintainer áp dụng — **không** rank mọi CUA.

**Nói:**

> Paper 3 chỉ có lý do tồn tại nếu Paper 2 cho thấy **chọn theo score alone có thể sai**. Lúc đó mới xây evaluation layer: registry D, freeze intervention, paired replay, **reliability profile** — giống robustness cần perturb input, không chỉ clean accuracy. Paper 3 là **infrastructure cho người khác dùng**, không phải OSWorld-scale leaderboard mới.

---

### Slide 8 — One-liner (English, để nhớ arc)

**Trên slide:**  
Paper 1 asks whether a score tells us what the agent tracked.  
Paper 2 asks whether getting that wrong **changes which agent we choose**.  
Paper 3 asks **how to evaluate** once one episode is insufficient.

**Nói:**

> Em tóm arc bằng ba câu này. Giờ em đi sâu Part 2 — thiết kế Paper 2 như decision experiment.

---

## PART 2 — Paper 2: decision experiment

### Slide 9 — Central question

**Trên slide (boxed):**  
*Does benchmark success identify the agent that tracks changing state best?*  
Hay: chọn theo \(\arg\max \overline{S}\) có trùng \(\arg\max \overline{STS}\) không?

**Nói:**

> Paper 2 không chứng minh lại Paper 1. Paper 1 đã nói score không certify tracking. Paper 2 test phản biện: **“Score imperfect nhưng agent score cao vẫn thường là agent đáng deploy.”** Nếu đúng, phenomenon chỉ là measurement artifact. Nếu sai — **ranking đảo** — thì có **decision consequence**.

---

### Slide 10 — Decision experiment vs audit

**Trên slide:**

| | Paper 1 | Paper 2 |
|---|---|---|
| Mục tiêu | Tách completion / tracking / score attachment | Hai **decision rule** có chọn cùng agent không |
| Outcome | Type A, sensitive, Type B | Top-1 **selection disagreement** |

**Nói:**

> Paper 1 audit **instrument**. Paper 2 là **decision experiment**: Rule 1 — chọn theo conventional benchmark trên world gốc \(G_0\). Rule 2 — chọn theo **state tracking** trên cùng universe paired interventions. Primary outcome không phải correlation thấp — vì correlation thấp chưa chắc đổi quyết định. Primary là **top-1 disagreement**.

---

### Slide 11 — Ví dụ trực giác

**Trên slide:**

| Agent | Benchmark score | STS |
|-------|----------------:|----:|
| A | 92 | 70 |
| B | 89 | 90 |
| C | 85 | 78 |

Score chọn **A**. STS chọn **B**.

**Nói:**

> Ví dụ minh họa — **chưa phải kết quả**. Leaderboard chọn A. Nếu deploy cần agent **bám state khi state đổi**, B có thể hợp lý hơn. Nếu pattern này xuất hiện trên protocol **freeze trước khi chạy**, Paper 1 không còn là curiosity — mà là **model-selection problem**.

---

### Slide 12 — Không giả định inversion

**Trên slide:**  
Paper 1 = exploratory signal, **không** confirmatory ranking.  
Paper 2 cần **fresh, pre-specified** task universe \(\mathcal{T}\).  
Paper 1’s 10 tasks → replay pilot Layer A only.

**Nói:**

> Em **không** giả định inversion sẽ xảy ra. Paper 1 có ít pair, task chọn để **discover phenomenon**, không để rank model. Lấy luôn 10 task đó rank sẽ bị accusation **post-hoc**. Paper 2 cần universe mới, eligibility và agent list **đóng trước outcome**. Paper 1 data chỉ là **motivation + Layer A pilot**.

---

### Slide 13 — Layer A: Calibration

**Trên slide:**  
*Score cao có predict tracking tốt hơn không?*  
Across cells: \(S \rightarrow P(Y=1)\).  
Null mạnh nếu align tốt → gap tồn tại nhưng aggregate vẫn informative.

**Nói:**

> **Layer A** — identifiability / calibration: trên từng paired cell, agent score cao có xu hướng track đúng hơn không? Có thể làm calibration curve, rank correlation, mixed-effects model. Nếu align rất tốt, Paper 1 vẫn đúng ở episode level nhưng **benchmark aggregate vẫn đủ chọn agent** — đó là null **quan trọng**, không phải failure.

---

### Slide 14 — Layer B: Selection (primary)

**Trên slide:**  
\(M_{\text{score}} = \arg\max_M \overline{S^0}(M)\)  
\(M_{\text{STS}} = \arg\max_M \overline{STS}(M)\)  
Primary: \(M_{\text{score}} \stackrel{?}{=} M_{\text{STS}}\)

**Nói:**

> **Layer B** là primary practical test. \(\overline{S}\) lấy **base leg only** — score trên world gốc, đúng như leaderboard. **Không** average \(S^0\) và \(S^1\). \(\overline{STS}\) trên **cùng analysis set** valid pairs. Nếu top-1 khác nhau → **decision consequence**. Nếu giống nhau dù calibration yếu → middle case: measurement issue chưa đổi selection.

---

### Slide 15 — Ba scenario (+ middle)

**Trên slide:**

1. **Align:** top-1 giống → gap chưa có decision harm rõ  
2. **Calibration yếu, top-1 giống** → measurement ≠ decision (middle)  
3. **Top-1 khác** → có thể chọn sai agent (jackpot)  
4. *(exploratory)* Family-wise rank khác nhau → profile cần thiết

**Nói:**

> Em thiết kế Paper 2 để **mọi scenario đều publishable**. Scenario 1–2 không làm Paper 3 bắt buộc — vẫn là scientific answer. Scenario 3 justify arc sang Paper 3. Scenario 4 — ví dụ retrieval align nhưng aggregation invert — cho thấy cần **profile theo state family**, không một scalar universal.

---

### Slide 16 — Đơn vị (M, T, I)

**Trên slide:**  
Cell: model M, task T, intervention I  
\(G_0 \rightarrow G_1 = I(G_0)\)  
Đo: completion, **STS** (typed D, guest gold), \(S^0, S^1\)  
\(\Delta S\) = score attachment audit — **không** phải reliability metric

**Nói:**

> Đơn vị là \((M,T,I)\). Intervention chỉ đổi D; instruction, UI, judge giữ. Paper 2 coi **state tracking** là quantity riêng — STS với gold-matching protocol đã freeze trong design note. Score sensitivity vẫn report như Paper 1 nhưng **không** biến \(\Delta S\) thành “agent reliable”.

---

### Slide 17 — Cross-agent

**Trên slide:**  
≥4 agents, sealed IDs **trước** run  
Không: chạy 10 model → publish 2 model invert  
Zero valid pair = **execution coverage**, không silent drop khỏi rank  
\(n_{\min}=3\) valid pairs mới vào \(\arg\max\)

**Nói:**

> Cross-agent cần **đủ candidate** để selection problem có nghĩa, không phải càng nhiều càng tốt. Model list **freeze trước**. Không drop model sau khi thấy STS xấu. Agent không đủ valid pairs vẫn report coverage — **không** vào ranking để làm bảng đẹp.

---

### Slide 18 — Cross-task & eligibility

**Trên slide:**  
Task universe \(\mathcal{T}\) mới — **không** Paper 1 ten  
Stratify: numeric, categorical, aggregation, temporal, joint/state, entity  
N = suy ra từ **selection rule**, không KPI “30 task”  
Primary: 1 CF/task; subset ~25% thêm \(G_2\)

**Nói:**

> Cross-task quan trọng hơn chỉ tăng N. Eligibility đã viết trong `PAPER2_SPEC`: sqlite, dv_from_answer, không pin gold, không LibreOffice artifact, không cua_required, loại Paper 1 IDs. Chọn task theo **state family**, seed mới. **Không** pitch “30×5×2=300” làm mục tiêu — số episode suy ra sau khi list \(\mathcal{M}\) và \(\mathcal{T}\). Hybrid: mỗi task ít nhất một intervention; subset thêm leg thứ hai để check không phải artifact một hướng perturb.

---

### Slide 19 — Intervention discipline

**Trên slide:**  
Paper 1 lesson: designed Type B ≠ observed class  
Paper 2: intervention **gold-moving + identifiable** — outcome để experiment quyết định  
Không “trap benchmark”

**Nói:**

> Intervention chỉ cần gold-moving, typed D, validate trước — **không** design để ép Type B. Claude aggregation-f018 designed trap mà thành Type A là bài học. Paper 2 không lặp lại kiểu đó cho confirmatory universe.

---

### Slide 20 — Frozen spec (6 quyết định)

**Trên slide:**  
1. Primary hypothesis (top-1 disagreement)  
2. Deployment decision (chọn 1 CUA stateful)  
3. Agent inclusion rule  
4. Task / family inclusion rule  
5. STS + \(\overline{S^0}\) definition  
6. Selection disagreement criterion + nulls  

→ `PAPER2_SPEC.md` — **chưa chạy cell mới**

**Nói:**

> Em đã đóng sáu quyết định trong spec repo — chưa chạy agent. Khác Paper 1, Paper 2 dễ chết nhất ở accusation **nhìn kết quả rồi mới tạo inversion**. Protocol phải đóng trước. Bước tiếp: sealed list model IDs + task IDs, rồi mới đếm cost legs.

---

### Slide 21 — Primitive (thesis)

**Trên slide:**  
*You cannot establish state-grounded reliability from a single realized episode.*  
Need: **controlled perturbation of determining state D.**  
Analog: clean accuracy vs robustness (perturb input)

**Nói:**

> Contribution sâu hơn metric: nếu Paper 2 đứng, community có thể chấp nhận **primitive** — giống robustness không chỉ đo trên một distribution. STS là quantity **sau** khi chấp nhận primitive, không phải “metric vì nghe hay”.

---

### Slide 22 — Câu hỏi cho anh Khải

**Trên slide:**  
Anh thấy bước Paper 1 → Paper 2 có đủ biến measurement gap thành vấn đề **decision utility** không?  
Hay em cần **deployment consequence** mạnh hơn (Paper 3 territory)?

**Nói:**

> Em dừng ở đây và xin ý kiến anh. Cụ thể: arc **discover → consequence → solution** có đủ lớn không; bước Paper 2 — test top-1 disagreement trên frozen universe — có đúng chỗ “for what?” không; anh có thấy thiếu một loại evidence nào trước khi em freeze \(\mathcal{M}\) và \(\mathcal{T}\) rồi chạy. Em sẵn sàng nhận null nếu score vẫn đủ chọn agent — nhưng muốn test fair trước khi commit compute.

---

## Phụ lục — Câu trả lời ngắn nếu anh hỏi

**“Paper 1 đã có Claude vs GPT — sao không rank luôn?”**  
→ Paper 1 không pre-register ranking; n nhỏ; task cho audit phenomenon. Confirmatory ranking cần universe mới.

**“STS khác gì binary track Paper 1?”**  
→ STS graded trên typed D (partial credit); ranking dùng aggregate STS; Paper 1 Type B là special case STS < 1.

**“30 task 5 model?”**  
→ Không phải target; N suy ra từ frozen rule và coverage floor \(n_{\min}\).

**“Paper 3 khi nào?”**  
→ Chỉ khi Paper 2 có selection disagreement (hoặc family-level pattern mạnh). Không song song.

**“Deploy consequence thật?”**  
→ Level 3 (STS predict stale errors in production) là paper sau; Paper 2 chỉ cần **wrong agent selected on benchmark**.
