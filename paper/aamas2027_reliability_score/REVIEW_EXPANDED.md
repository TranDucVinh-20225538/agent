# Đánh giá tổng quan mở rộng — "What Does a Computer-Use Agent Reliability Score Actually Measure?"

*Bản AAMAS 2027 main-track draft, area GAAI, `paper/aamas2027_reliability_score/main.tex` (5 trang body + supplement 1 trang). Tài liệu này mở rộng chi tiết cho 3 study, dựa trên đọc trực tiếp `main.tex` và `supplement.tex`.*

## 1. Bối cảnh và luận điểm chính

Leaderboard cho computer-use agent (CUA) thường báo cáo một con số hoàn thành (completion-conditioned score): episode kết thúc, rubric gán một điểm. Cách dùng phổ biến — chọn agent dựa trên con số đó — ngầm coi con số là một *quan sát* về độ tin cậy (reliability) của agent. Bài báo lập luận: cách hiểu đó không có cơ sở. Điểm số là một **constructed measurement** (đo lường được kiến tạo, theo nghĩa Cronbach 1955 / Messick 1995): một chuỗi phép biến đổi biến trajectory thành candidate evidence, thành decision, thành giá trị báo cáo. Validity là thuộc tính của *chuỗi biến đổi đó*, không phải của con số cuối.

Câu hỏi trung tâm: **điểm reliability của một CUA thực sự đo cái gì?** Trả lời bằng cách audit **một instrument đã đóng băng (frozen)**, qua **3 study bổ sung cho nhau** (không phải 3 thí nghiệm độc lập) — cùng soi vào một pipeline đo lường ở 3 độ phân giải khác nhau:

```
Trajectory/world → Candidate evidence → Decision/aggregation → Reliability score → Ranking/triage
      ↑ Study 1: score có track outcome?
                    ↑ Study 3: evidence có được thu thập đầy đủ?
                                    ↑ Study 3: có bị bỏ/scope sai/so sánh mất?
                                                      ↑ Study 2: số có select đúng ý định?
```

Ba study **chia sẻ** benchmark family, protocol counterfactual có cặp (paired), và model roster — bài chủ động nói rõ: **không cộng dồn sample size giữa các study**.

**Protocol chung cho cả 3 study:** dùng MyPCBench (Jang 2026) — desktop ảo có seed. Với mỗi task *t*, có world gốc E⁰ₜ và world can thiệp E¹ₜ = Iₜ(E⁰ₜ) — một patch đã khoá, ghi đè lên một tập "determining set" Dₜ đã đăng ký trước. Instruction, giao diện, kích thước screenshot, và judge giữ nguyên; guest probe xác nhận gold value đã thực sự đổi. Một cặp chỉ **valid** nếu cả 2 leg đều kết thúc theo đúng nghĩa canonical (đọc từ hành động cuối cùng, qua một classifier fail-closed **không** tham khảo judge — tức kênh "đã xong chưa" và kênh "điểm bao nhiêu" tách biệt nhau hoàn toàn). Lỗi thực thi (execution failure) được tính là **quan sát vắng mặt**, không phải là một "miss" về tracking.

---

## 2. Study 1 — Score–Outcome Dissociation (điểm số có track thế giới thật không)

**Câu hỏi:** một điểm reliability có nhất thiết track sự thay đổi trong outcome thật hay không?

**Cách đo, trên mỗi valid pair, đọc 3 sự kiện tách biệt:**
- **Tracking**: so khớp kiểu (typed match) câu trả lời cuối với gold thật trên tập D — hoàn toàn không có judge tham gia.
- **Score sensitivity**: bằng nhau tuyệt đối (S_CF = S_Base) so với bất kỳ delta khác 0 nào.
- Phân loại pair:
  - **Type A**: tracking đúng (giữ được) **và** score không đổi — đây là kết quả "khoẻ mạnh" mong đợi.
  - **Score-sensitive**: tracking đúng nhưng score lại đổi — score "nhạy" hơn mức cần thiết.
  - **Type B**: tracking không đầy đủ/sai, nhưng score vẫn cao và không đổi — đây là ca nguy hiểm nhất: agent thực ra sai nhưng điểm vẫn "đẹp".

**Thiết kế:** lịch thí nghiệm 5×10 đã khoá trước (50 cell dự định; 4 cell chưa bao giờ được lên lịch; 46 cell thực thi; 92 leg tổng; 35 execution failure; **24 valid pairs** sống sót). 3 lane chính: Claude, GPT-5.5, Qwen3.5-35B-A3B. Có thêm một size-ablation và một exploratory Flash lane nhưng **không được gộp** vào rate chính.

| Lane | Valid | Track-valid | Type A | Score-sensitive | Type B | Invariance (95% CI Clopper–Pearson) |
|---|---|---|---|---|---|---|
| Claude | 9 | 7 | 6 | 1 | 2 | 6/7 = 0.857, CI [0.421, 0.996] |
| GPT-5.5 | 8 | 7 | 3 | 4 | 1 | 3/7 = 0.429, CI [0.099, 0.816] |
| Qwen3.5-35B-A3B | 1 | 1 | 1 | 0 | 0 | 1/1, CI [0.025, 1.000] |

Vài điểm quan trọng về cách đọc bảng này:
- Tracking luôn được code từ câu trả lời cuối, **không bao giờ** từ chính S — tránh vòng lặp tự xác nhận.
- Run chưa hoàn thành = execution failure, bị loại khỏi mẫu, không tính là "miss tracking".
- CI rất rộng ở cả 3 lane (đặc biệt Qwen chỉ có 1 pair) — bài **chủ động không** đưa ra một con số invariance gộp chung, và **không** cộng 24 pair này vào 18 valid pair của Study 2.
- Một "trap" được thiết kế để agent dễ mắc — nhưng **không quyết định trước** kết quả: cùng một intervention có thể ra Type A sạch trên agent này, và ra split trên agent khác. Tức hiện tượng dissociation không phải do một loại can thiệp cố định gây ra, nó phụ thuộc cả vào hành vi thực của từng agent.

**Kết luận của Study 1 (đúng mức, không quá tay):** điểm số báo cáo *có thể giữ nguyên* dù outcome khác biệt về chất, và *có thể thay đổi* mà không có thay đổi tương ứng trong tracking. Một điểm ổn định **không** chứng minh tracking đúng; một điểm biến động **không** chứng minh tracking sai. Đây là lý do vì sao điểm số cần được audit — Study 1 mới chỉ *phát hiện hiện tượng*, chưa nói *correspondence gãy ở đâu* (đó là việc của Study 3).

---

## 3. Study 2 — Measurement and Selection Audit (điểm số có làm đúng việc chọn agent không)

**Câu hỏi:** nếu điểm số không phản ánh đầy đủ trajectory, thì ít nhất nó có làm tốt công việc người ta vẫn dùng nó để làm — chọn agent tốt nhất — hay không?

**Thiết kế:** 3 agent, mỗi agent chạy đúng 57 leg đã đăng ký trước, cùng một instrument: GPT-5.5, Qwen3.8-Flash, Claude Opus 4.6. Toàn bộ những thứ sau được khoá **trước khi có bất kỳ outcome nào**: task, intervention, seed, step budget, ngưỡng nhận vào `n_min = 3` valid pair mới được xếp hạng, và luật "nếu có ít hơn 3 agent được xếp hạng thì confirmatory selection test **không được đánh giá**". Một lane thứ 4 đã bị loại **trước khi chạy** vì lệch instrument/transport, không xuất hiện trong bảng coverage. Cả 3 lane còn lại dùng chung một generic XML tool protocol — **không phải** stack computer-use gốc của từng vendor, nên so sánh chỉ có ý nghĩa trong nội bộ roster + instrument này, không suy rộng ra "Claude tốt hơn GPT nói chung".

| Agent | DONE/57 | \|A\| (valid pairs) | mean S⁰ | mean STS |
|---|---|---|---|---|
| GPT-5.5 | 32 | 9 | 69.3 | 0.130 |
| Qwen3.8-Flash | 29 | 8 | 95.8 | 0.229 |
| Claude Opus 4.6 | 4 | 1 | 100 | 0 |

**Coverage chính là kết quả đầu tiên, và là kết quả gây sốc nhất.** Claude chỉ kết thúc (terminate) 4 leg trên 3 task → |A| = 1 trong số 19 pair khả dĩ. Theo đúng `n_min=3`, Claude được **báo cáo nhưng không được xếp hạng**. Roster được xếp hạng chỉ còn 2 agent — ít hơn 3 — nên **confirmatory selection test không được đánh giá**, đây là **một outcome đã được định trước trong kế hoạch**, không phải một thí nghiệm thất bại giữa chừng. Bài nhấn mạnh: **không so sánh model trên 57 task** — sau luật coverage-first, chỉ còn 4 task cluster hỗ trợ được so sánh cặp còn lại. Mean S⁰=100 của Claude trên |A| của nó là **coverage artefact** — chỉ vì đó là task duy nhất agent giải và đóng đúng cách, không phải bằng chứng năng lực.

**Cấu trúc tracking dự định là degenerate.** Binary track Y=1 đòi hỏi *mọi* component trọng số dương trong D khớp trên cả 2 leg. Kết quả: **Y=0 trên toàn bộ 18 valid pair** — không có positive class nào cả, nên S⁰ **không thể được hiệu chỉnh (calibrate)** thành P(Y=1). Lớp đo graded STS (trích xuất kiểu từ câu trả lời cuối so với gold thật, khoá trước khi có aggregate, không có judge) nằm gần sàn (floor) — GPT 0.130, Flash 0.229, Claude 0. Một khoảng cách vài phần trăm sau đó là khoảng cách giữa hai residual, không phải giữa "agent đáng tin" và "agent không đáng tin".

**So sánh khám phá (exploratory) trên 4-task common support (A∩):** Bootstrap có cặp qua task (seed 20260904, B=5000), Δ = Flash − GPT-5.5:
- Δ S⁰ = +46.5, 95% CI [21.0, 72.0] → argmax theo S⁰ là **Flash**.
- Δ STS = −0.042, 95% CI [−0.125, 0.000] → argmax theo STS là **GPT-5.5**.

| Task | S⁰ GPT/Flash | STS GPT/Flash | ΔS⁰ | ΔSTS |
|---|---|---|---|---|
| counterfactual-f010 | 83/100 | 0/0 | +17 | 0 |
| preference_inference-f014 | 0/84 | 0/0 | +84 | 0 |
| retrieval-f002 | 75/100 | 0.50/0.50 | +25 | 0 |
| retrieval-f009 | 40/100 | 0.50/0.33 | +60 | −0.167 |

Sự đảo ngược (reversal) giữa 2 layer đo là **strict trên đúng 1 task** (`retrieval-f009`), **hoà trên 3 task còn lại**. Bỏ đúng task đó ra khỏi mẫu thì so sánh STS trở thành hoà — bài tự làm phép leave-one-pair-out để chứng minh điều này, và tự nói rõ đây **không phải là một xác nhận thứ hai độc lập**, chỉ là kiểm tra tính nhạy cảm với 1 điểm dữ liệu. Trên các pair này, STS chỉ nhận 3 giá trị khả dĩ {0, 1/3, 1/2} — tức bất đồng giữa 2 layer đo nằm ngay ở giới hạn độ phân giải của chính công cụ đo, không phải một tín hiệu mạnh.

**Một phát hiện phụ đáng chú ý:** giới hạn về A∩ làm mean S⁰ của GPT-5.5 tụt từ 69.3 (trên 9 pair riêng của nó) xuống 49.5, trong khi Flash không đổi (95.8 → 96.0). Trên chính |A| của từng agent, Flash cao hơn ở cả 2 layer. "Ai thắng" phụ thuộc vào bạn chọn layer nào và agent nào hoàn thành được task nào — không có denominator nào được chọn *sau khi* thấy cái nào đẹp hơn.

**Điều kiện hoá theo việc kết thúc (termination) cũng thay đổi những gì điểm số "nhìn thấy" được:** các cell bị loại (không valid pair) có điểm **thấp hơn** trung bình so với cell trong A (46.4/44.9/26.1 so với 69.3/95.8/100) — nghĩa là bộ lọc coverage-first *bảo thủ* (conservative) cho việc hiệu chỉnh, chứ không thiên vị agent. Nhưng vẫn có 2, 2, và 1 cell (lần lượt GPT/Flash/Claude) bị loại dù điểm ≥90 mà **không có** DONE canonical — vì terminal-classifier không bao giờ tham khảo judge, đây là "tiến độ nhìn thấy được qua rubric nhưng chưa đóng episode", một protocol chỉ dựa vào completion **không thể** biểu diễn được hiện tượng này.

**Một robustness check khác cũng được báo cáo thẳng ra dù làm phức tạp câu chuyện:** một bộ canonicalization parser được liệt kê từ dialect của 1 agent (Flash) thì "khoan dung" hơn với chính agent đó — nếu coi những rescue đó là reject thì |A| của Flash tụt từ 8 xuống 7, các lane khác không đổi. Vì lý do này, mọi |A| báo cáo trong bài được coi là **cận dưới** (lower bound), không phải con số chính xác.

---

## 4. Study 3 — Diagnosing Evidence Loss (evaluator bị mất bằng chứng ở đâu)

Study 1 và 2 cho thấy correspondence *có thể* gãy. Chúng không nói *gãy ở đâu*. Study 3 đóng băng evaluator và mổ xẻ các map biến trajectory thành giá trị báo cáo.

**Đơn vị phân tích:** một *row* = một component của D, trên một leg. Kho lưu trữ phát triển (development archive) có **134 row** trên 57 leg.
- Row là **R1-positive** nếu giá trị gold nằm *đúng nguyên văn* trong câu trả lời của agent (n=59: 20 MATCH + 39 RECALL_MISS).
- 61 row còn lại là **ABSENT**: gold không hề có trong text.
- Mọi tỷ lệ dưới đây **chỉ tính trên tập đã audit này** — đây **không phải** false-negative rate của agent, cũng không phải của benchmark nói chung.

### 4.1 Recall loss — headline của study

Instrument đã đóng băng chỉ khôi phục được **20/59** row R1-positive (sensitivity = 0.339). **Miss 39 row.** Đây là headline: thông tin *có thể khôi phục được* (agent đã viết đúng nó ra) vẫn có thể bị mất trước khi tới bước chấm điểm.

| Nguyên nhân | n | Ý nghĩa |
|---|---|---|
| M1a | 13 | gold đã đi vào `found` rồi **bị discard** |
| M1b | 7 | các candidate mâu thuẫn nhau; gold không nằm trong số đó |
| M2 | 9 | không có label nào khớp ở bất kỳ đâu trong câu trả lời |
| M3 | 5 | label khớp; nhưng gold nằm ngoài mọi cửa sổ (window) ± |
| M4 | 5 | instrument báo cáo một giá trị **không phải** gold |

39 miss **không phải một cơ chế duy nhất** — đây là điểm quan trọng để tránh việc quy hết về "bug đơn giản". Phát hiện mạnh nhất, cụ thể nhất là **M1a**: trong 13/39 miss, extractor **đã tích luỹ đúng giá trị gold rồi**, và bước fail-closed aggregation **tự bỏ nó đi**. Trong 7/13 trường hợp đó, gold còn chiếm *đa số* (majority) trong các candidate đã tích luỹ — tức không phải trường hợp cận biên, mà là trường hợp "đáng lẽ phải thắng nhưng bị luật fail-closed loại". (Lưu ý: M1 không loại trừ lẫn với nhóm ABSENT — 25/61 row ABSENT cũng mang đặc điểm M1; M1a là tên riêng cho đúng loại "bằng chứng có thể khôi phục nhưng bị discard".)

### 4.2 Repair như can thiệp chẩn đoán, không phải một phương pháp thay thế

4 layer-intervention được **đặc tả trước khi chạy**:
- **R-AGG**: plurality vote trên các candidate đã tích luỹ (nhắm vào M1a).
- **R-SCOPE**: mở rộng cửa sổ ra toàn bộ câu trả lời (nhắm vào M3).
- **R-CMP**: so sánh kiểu containment thay vì exact (nhắm vào M1b, lỗi entity).
- **R-CHAN**: xoá các đoạn markup/scaffolding (nhắm vào nhiễu do định dạng).
- **ALL**: gộp cả 4.

Không repair nào **thay thế** instrument — đây là các can thiệp chẩn đoán từng lớp một.

| Config | Sensitivity/59 | Abstention/134 | M4/reported | MATCH → dest./20 |
|---|---|---|---|---|
| FROZEN | 20 | 89 | 25/45 | 0 |
| R-AGG | 28 | 63 | 43/71 | 0 |
| R-SCOPE | 13 | 56 | 65/78 | 14 |
| R-CMP | 20 | 89 | 25/45 | 0 |
| R-CHAN | 15 | 104 | 15/30 | 7 |
| ALL | 10 | 79 | 45/55 | 16 |

**Không repair nào thắng toàn diện.**
- **R-AGG** là intervention *duy nhất* nâng sensitivity (20→28), nhưng nó giải phóng 26 abstention thành **+8 đúng / +18 sai** — phần lớn lỗi mới nằm trên các row **ABSENT** (gold không hề có trong text) — tức instrument giờ "dám" đưa ra quyết định ở những chỗ trước đây nó im lặng, và phần lớn quyết định mới đó là sai. **Khôi phục thêm evidence không đồng nghĩa với khôi phục đúng phép đo.**
- **R-SCOPE** biến 14/20 row *vốn đã đúng* thành thứ khác — mở rộng recall của observation lại **làm giảm** độ đúng của phép đo (confident-wrong = 0.833).
- **R-CHAN** phá 7 row MATCH, chủ yếu bằng cách xoá nhầm markup chưa đóng thẻ tới hết văn bản — đúng như hướng gây hại mà fixture đã đặt tên trước.
- **ALL** tệ hơn *từng thành phần riêng lẻ* về sensitivity — 4 can thiệp **không "vote" cùng hướng**, chúng chẩn đoán các map khác nhau, và các map đó không di chuyển phép đo theo cùng một hướng.
- **R-CMP bit-identical với FROZEN** trên mọi chỉ số — lớp so sánh (comparison layer) không thể tự tạo ra một abstention, và lỗi entity trong archive này vốn dĩ đã là abstention rồi. Kết luận: **một repair ở layer sau không thể cứu một miss đã xảy ra ở layer trước.**

### 4.3 Hiệu ứng có dấu (signed) trên một thống kê so sánh

Trên cùng 4-task support với Study 2, Δ STS (Flash trừ GPT) dưới FROZEN là **−0.0417**. R-AGG thu hẹp gap trung bình về −0.0208 nhưng bất đồng theo từng task lại **tăng** (2 task khác 0 di chuyển ngược hướng nhau, triệt tiêu một phần). Đáng chú ý nhất: **R-CHAN đảo dấu hoàn toàn: Δ STS = +0.1667**, argmax chuyển sang Flash. Dưới R-CHAN, Flash **bit-identical với FROZEN trên mọi task**; GPT sụp từ 0.250 xuống 0.042. Thứ tự đổi **vì channel intervention phá huỷ evidence của một lane**, không phải vì lane kia đo tốt hơn. ALL = phá huỷ đó cộng thêm phần Flash được lợi từ các repair khác (Δ = +0.2292).

Đây là **một existence demonstration**, được đặt tên thẳng: số cluster task độc lập hiệu quả cho Δ STS đã khoá này là **n_eff = 1** (chỉ `retrieval-f009`). Bài **không** đưa ra tuyên bố về tần suất ranking instability nói chung. Và một điểm rất tinh: **sự đồng thuận giữa kết quả sau repair với S⁰ không phải là bằng chứng của validity** — R-CHAN "đồng ý" với S⁰ chính bằng cách phá huỷ GPT, chứ không phải vì nó đo đúng hơn.

### 4.4 Specification portability (tái tạo bảng nhãn viết tay)

Hỏi riêng: liệu bảng nhãn viết tay (hand-written label table) của instrument đã đóng băng có thể được tái tạo bởi một luật *grounded* trên task, độc lập với corpus, **khoá trước khi validate** hay không?
- **Groundedness (G1)** so với định nghĩa task: 100% (30/30 theo supplement).
- **Calibration fidelity (G2)** so với bảng đã đóng băng: **9/30 — FAIL**. MATCH tụt 20→13, ABSENT không đổi.

Bài nói rõ: **không hỏi liệu R có "tốt hơn" hay không** — chỉ hỏi liệu một luật grounded định sẵn có tái tạo được instrument hiện có hay không. Không tái tạo được. 9/30 (G2) và 39/59 (recall miss) là **hai estimand khác nhau, không được gộp**.

### 4.5 Comparative cohort gate — cánh cửa đóng lại

Một pre-specified gate yêu cầu ≥20 task cluster độc lập, cùng construct, cùng frozen evaluator, quyết định **trước khi thấy trajectory đầu tiên**. Slate gồm 28 task họ mới. Probe chỉ kiểm tra khả năng inject/guest (không agent, không STS): Wave A 9/12, Wave B 7/16 → **n=16 < 20 → FAIL**. Nhánh so sánh comparative bị đóng lại — supplement tự viết thẳng: **"Not a scientific headline."**

---

## 5. Bảng hợp nhất (chính bài tự gọi đây là "the paper")

| Giai đoạn (map) | Correspondence kỳ vọng | Thất bại quan sát được |
|---|---|---|
| Trajectory → score | Score track outcome | Study 1: dissociation Type A/B |
| Evidence → selection | Score hỗ trợ đúng việc chọn | Study 2: coverage sập; Y=0 trên 18/18 |
| Trajectory → evidence | Evidence khôi phục được thì sống sót | Study 3: 39/59 miss |
| Evidence → score | Sửa 1 layer vẫn giữ nguyên ý nghĩa | Study 3: +8 đúng/+18 sai; không repair nào thắng |
| Specification → instrument | Nhãn viết tay tái tạo được | Study 3: G2 chỉ 9/30 |

Hàm ý vận hành (operational implication) mà bài đưa ra: leaderboard chỉ báo cáo S thì **không thể** phân biệt agent trung thực với thế giới và agent chỉ "ghi điểm đẹp" (Study 1); **không thể** nói agent nào thậm chí đủ điều kiện để so sánh (Study 2); **không thể** nói con số có được tạo ra bằng cách bỏ đi bằng chứng mà agent đã viết ra hay không (Study 3). Instrument tiếp theo nên phơi bày rõ các map: kênh kết thúc fail-closed tách khỏi judge; tracking construct không tham khảo judge; extractor đóng băng trước khi có aggregate; và một test tái tạo cho bất kỳ bảng nhãn viết tay nào.

---

## 6. Điểm mạnh (đánh giá mở rộng)

1. **Kỷ luật pre-registration xuyên suốt, không có ngoại lệ.** N, keep_cap, `n_min=3`, comparative gate `n≥20`, seed cho bootstrap — tất cả khoá trước khi thấy outcome. Khi một gate fail, bài báo cáo thẳng là fail thay vì lách hoặc âm thầm bỏ qua ("not evaluated", "FAIL. Comparative branch closed."). Đây là điểm khó công kích nhất của bài với một reviewer hostile.
2. **Tách kênh triệt để để tránh vòng lặp tự-xác-nhận.** Terminal/completion classifier không tham khảo judge; tracking construct không tham khảo judge. Nếu không tách, mọi kết luận "score sai" đều có thể bị nghi là circular.
3. **Mọi existence-demo được gắn đúng nhãn quy mô của nó** — n_eff=1 được nói thẳng ra ngay tại chỗ phát hiện, không để người đọc suy diễn thành effect tổng quát.
4. **Có rất nhiều câu "we do not claim..." chủ động** rải khắp bài — chặn trước gần hết các hướng overclaim thường bị reviewer bắt lỗi ở dạng bài audit/critique.
5. **Robustness check được báo cáo dù làm phức tạp câu chuyện có lợi** — ví dụ near-miss parser sensitivity khiến |A| của Flash có thể tụt 8→7, vẫn được nêu ra thay vì giấu.
6. **Súc tích, đúng khuôn khổ** — 5 trang, còn dư chỗ, không bị nhồi nhét để vừa giới hạn.
7. **Mục "AI use" đã có sẵn**, đúng format chính sách AAMAS 2027.

## 7. Điểm yếu (đánh giá mở rộng, những chỗ reviewer thật sẽ nhắm vào)

1. **N nhỏ, CI rộng ở khắp nơi.** Study 1: 9/8/1 pair mỗi lane. Study 2: roster xếp hạng chỉ còn 2 agent (dưới ngưỡng), nên phần "confirmatory" coi như trống trong bài này. Study 3: headline effect (đảo dấu Δ STS) cũng chỉ là n_eff=1. Một reviewer không thiện cảm với null/negative result có thể hỏi thẳng: rốt cuộc cái gì được *establish* một cách chắc chắn?
2. **External validity giới hạn nghiêm trọng** — chỉ 1 benchmark (MyPCBench), 1 frozen instrument, dùng generic tool protocol thay vì stack native từng vendor. Bài tự thừa nhận trong Limitations, nhưng vẫn là lỗ hổng thật khi review.
3. **Comparative cohort gate đã FAIL** — phần so sánh ranking quy mô lớn hơn (điều đáng lẽ mới thực sự trả lời câu hỏi "agent nào tốt hơn") **chưa từng xảy ra** trong bài này; những gì còn lại chỉ là audit từng agent riêng lẻ cộng với 1 so sánh exploratory 4-task.
4. **Không có population-level rate nào được ước lượng** — bài chỉ chứng minh sự tồn tại (existence) của các failure mode, không nói tần suất ở quy mô lớn. Có reviewer sẽ tiếc.
5. **3 study cố tình chia sẻ benchmark/model/protocol** — dù được giải thích rõ là thiết kế có chủ đích ("one measurement system, three resolutions"), vẫn có khả năng một reviewer hỏi "tại sao không trình bày như một nghiên cứu tích hợp duy nhất thay vì 3 lens tách biệt" — cách đóng khung này vừa là điểm mạnh (rõ ràng, có chủ đích) vừa là điểm dễ bị chất vấn (có phải đang bù đắp cho việc thiếu một effect mạnh duy nhất không).
6. **Mục "AI use" hiện khá ngắn gọn** ("dùng để draft/copy-edit prose... không tool nào chọn hypothesis/gate/repair/số liệu") — nên đối chiếu lại với mức độ tham gia thực tế trong quá trình làm nghiên cứu (review thiết kế sampling, bắt bug trong script phân tích, verify công thức N, v.v.) trước khi nộp, để đảm bảo khai đúng theo đúng nghĩa chính sách AAMAS về "tham gia vào methodology/experimental design".

## 8. Tổng kết

Đây là một bài thuộc dạng **measurement-validity / methodology audit** — sức mạnh nằm ở kỷ luật pre-registration và sự trung thực trong báo cáo (mọi null/negative result đều được nêu thẳng), không nằm ở effect size lớn hay N lớn. Đó là một dạng đóng góp hợp lệ và được nhiều venue coi trọng (đặc biệt các track về evaluation/measurement), nhưng sẽ có nhóm reviewer đòi hỏi "actionable takeaway" rõ ràng hơn những gì bài hiện có. Bài đã phần nào trả lời trước bằng đoạn Unified Findings (4 điều kiện thiết kế cho instrument tiếp theo) — đây là điểm nên nhấn mạnh nếu bị hỏi trong quá trình rebuttal.
