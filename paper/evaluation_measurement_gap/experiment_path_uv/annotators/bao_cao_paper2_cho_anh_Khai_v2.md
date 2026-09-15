# BÁO CÁO CHUẨN BỊ TRÌNH BÀY VỚI ANH KHẢI

*Đề tài: "From Trajectories to Evidence: Auditing Observation Loss and Identifiability in Computer-Use Agent Evaluation" — Paper 2/3, đang nhắm nộp AAMAS 2027 (hạn abstract 1/10)*

Người trình bày: Vinh | Tháng 9/2026 | Bản đọc để nói, viết cho người chưa biết gì về bài cũng đọc hiểu được, càng đầy đủ càng tốt.

Em xin phép trình bày lại toàn bộ bài báo hiện đang chuẩn bị nộp AAMAS 2027 — từ nền tảng khái niệm, quá trình đi tới kết quả hiện tại, rà soát tài liệu liên quan, tới từng kết quả cụ thể trong bản draft đã khoá (`main.tex` v0.5) — để anh tiện theo dõi và cho ý kiến ở những chỗ em còn phân vân.

---

## Phần 1 — Kiến thức nền tảng, để anh dễ theo dõi phần sau

### 1.1. Bài này giải quyết vấn đề gì (nói bằng ngôn ngữ đời thường)

Có những AI agent biết tự thao tác máy tính — click chuột, gõ phím, mở trình duyệt, làm việc thay người — gọi chung là "computer-use agent" (CUA). Để biết agent nào giỏi, người ta cho nó làm một loạt nhiệm vụ trên một benchmark (bộ đề kiểm tra chuẩn hoá, ví dụ OSWorld, WebArena, VisualWebArena, MyPCBench), rồi có một "bộ chấm điểm" (evaluator) xem agent làm đúng hay sai, ra một con số gọi là reliability score (điểm tin cậy).

Các bài trước đây (Dong và cộng sự, Xue và cộng sự, Rosset và cộng sự — em nói kỹ ở Phần 3) đã chỉ ra: bộ chấm điểm đó có thể tự nó sai — chấm nhầm FAIL cho một trường hợp thực ra là đúng, hoặc chỉ nhìn frame cuối cùng nên bỏ lỡ bằng chứng.

Bài này hỏi một câu hẹp hơn và mới hơn: **khi bộ chấm điểm đã bị "đóng băng" (frozen) — tức không sửa gì thêm trong lúc audit — thì chuyện gì xảy ra *bên trong* nó, sau khi bằng chứng đã được thu thập và trước khi ra phán quyết cuối cùng?**

Câu trả lời chính, và cũng là phát hiện trọng tâm của cả bài: có một cơ chế gọi là **"discard sau khi đã thu thập"** (post-collection discard) — bằng chứng đúng đã từng được hệ thống nhìn thấy, đã được ghi vào một tập tạm gọi là `found` (đã tìm thấy), nhưng một bước xử lý phía sau (aggregation — bước tổng hợp nhiều ứng viên câu trả lời thành một kết quả cuối, chạy theo nguyên tắc "an toàn thì loại" — fail-closed) lại **loại bỏ nó** trước khi ra kết luận. Kết quả: agent bị chấm MISS (trượt), dù bằng chứng đúng đã từng nằm trong tay hệ thống.

> ***Lưu ý khi trình bày:** Đây không phải là "agent làm sai" — bằng chứng đúng đã có trong câu trả lời của agent. Cũng không phải lỗi dữ liệu thiếu (bằng chứng có tồn tại ở một trạng thái trung gian của hệ thống). Đây là lỗi ở tầng đo lường (measurement), nằm giữa lúc thu thập và lúc ra phán quyết — một vị trí mà nếu chỉ nhìn kết quả PASS/FAIL cuối cùng thì không thể phát hiện ra.*

### 1.2. Cách bài báo đóng khung bài toán — pipeline 5 bước

Để nói cho rõ "chỗ nào trong hệ thống" bị mất bằng chứng, bài dùng một khung 5 bước mà bài toán chấm điểm agent nào cũng có thể quy về:

$$\tau \rightarrow I \rightarrow P \rightarrow E \rightarrow Y \rightarrow S$$

- **τ (trajectory)** — toàn bộ log/vết agent để lại khi làm nhiệm vụ (mọi hành động, mọi câu trả lời, mọi ảnh chụp màn hình).
- **I (observation)** — kênh quan sát được khai báo trước: hệ thống chấm điểm *thực sự* nhìn vào phần nào của τ? (Ví dụ: chỉ nhìn dòng chữ trả lời cuối cùng, không nhìn ảnh, không nhìn các bước trung gian.)
- **P (parser)** — bộ phân tích cú pháp, cố rút ra từ I một đoạn ứng viên câu trả lời duy nhất (hoặc không rút ra được gì).
- **E (evidence)** — phân loại bằng chứng: đoạn rút ra đó có phải là DETERMINING (đủ tư cách làm bằng chứng, vì nó khớp đúng dạng cần tìm) hay không.
- **Y (correspondence)** — quyết định HIT/MISS: chỉ được gán khi E là DETERMINING *và* nhãn đúng (gold label, ký hiệu L) độc lập với chính đáp án của episode đó (tức không tự "rò rỉ" đáp án vào phép so sánh). Nếu không đủ điều kiện, hệ thống phải trả về **ABSTAIN** (không đủ bằng chứng để phán quyết) — ABSTAIN nghĩa là *thiếu phép đo tương ứng*, không phải "nhiệm vụ thất bại".
- **S (score)** — con số hoặc lựa chọn cuối cùng được tính ra từ Y, hoặc từ một rubric thô hơn (ví dụ chấm bằng ảnh) mà thậm chí không bao giờ lộ ra Y.

Bài dùng ba nhãn phân tích (không phải lý thuyết đo lường mới, chỉ là cách gọi tên cho đúng vị trí lỗi) — trùng lặp một phần với cách Dong và cộng sự chia giai đoạn construction/observation/scoring/reporting:

| Khoảng hở | Ý nghĩa |
|---|---|
| **Outcome gap** | Điểm S không nhất thiết khớp với việc theo dõi đúng trạng thái thế giới đã được đo độc lập |
| **Observation gap** | Bằng chứng có trong τ không nhất thiết vào được I, hoặc không sống sót qua P |
| **Justification gap** | Bằng chứng thu được không nhất thiết đủ để xác định (identify) đúng cái claim mình muốn đo — kể cả correspondence hai chiều (two-sided: vừa đúng vừa sai đều nhận biết được) |

Bài lấy trọng tâm ở **observation gap**, cụ thể là "P3" (Phần 5 dưới đây) — mất bằng chứng *ngay bên trong* bước P, sau khi đã vào I.

### 1.3. Bảng tra cứu các mã hiệu sẽ dùng lại nhiều lần

Đề tài có nhiều nhánh con, đặt tên tắt P1–P4, Path A, Path UV, Study 1–3. Em liệt kê ngắn gọn để anh tiện tra khi đọc phần sau:

| Mã | Tên gọi khác | Vai trò trong bài hiện tại |
|---|---|---|
| **P3** | Study 3 | **Core (trọng tâm duy nhất)** — audit "discard sau khi thu thập" trên bộ trích xuất đã đóng băng (MyPCBench). Phần 5 của báo cáo này. |
| **P4** | — | **Secondary** — chuỗi thí nghiệm xây dựng (constructive) để kiểm tra: nếu khai báo tường minh kênh quan sát I, thì correspondence hai chiều có định danh được không. Phần 6. |
| **P1** | Study 1 | **Supporting, chỉ nằm trong phụ lục** — một demo tồn tại/phân ly (existence/dissociation): điểm số và việc theo dõi đúng trạng thái thế giới có thể tách rời nhau. Phần 7.1. |
| **P2** | Study 2 | **Supporting, chỉ nằm trong phụ lục** — việc đánh giá/lựa chọn có thể làm thay đổi "cơ sở bằng chứng" của một so sánh. Phần 7.2. |
| **Path A** | — | **Supporting** — audit 299 phán quyết FAIL công khai trên WebArena/VisualWebArena, chia theo lý do trống bằng chứng vs có bằng chứng nhưng sai. Phần 7.3. |
| **Path UV** | — | **Chưa đưa vào bài chính** — thử mở rộng phát hiện M1a sang một bộ dữ liệu công khai khác (CUAVerifierBench). Đang làm dở, chỉ ghi 1 câu trong Limitations. Phần 8. |
| **M1a–M4** | — | Năm mã nguyên nhân khiến bộ trích xuất bỏ lỡ một câu trả lời đúng (Bảng ở Phần 5.2). M1a là trọng tâm. |
| **R-AGG, R-SCOPE, R-CMP, R-CHAN, ALL** | — | Các cấu hình "sửa thoáng hơn" (permissive repair) được thử trên bộ trích xuất, xem có cứu được các case miss không. Phần 5.5. |

> ***Lưu ý khi trình bày:** Bốn khái niệm P3, P4, P1/P2, Path A này sẽ quay lại liên tục ở các phần sau — anh chỉ cần nhớ: P3 là trọng tâm duy nhất của bài (CORE), P4 phụ thuộc P3 (không phải metric thay thế), P1/P2/Path A chỉ là phần hỗ trợ nằm trong phụ lục, không phải đóng góp chính.*

### 1.4. Vài khái niệm kỹ thuật sẽ nhắc lại nhiều lần

**MyPCBench** — bộ benchmark cho computer-use agent mà toàn bộ phân tích trong bài này dựa trên đó. Bài không tự thu dữ liệu mới ở tầng "agent làm nhiệm vụ" cho phần P3 — mà lấy log đã có sẵn, đóng băng bộ trích xuất câu trả lời (extractor), rồi audit chính bộ trích xuất đó.

**Frozen (đóng băng)** — nghĩa là trong lúc audit, code của bộ chấm điểm không được sửa. Đây là điều kiện bắt buộc để có thể nói "lỗi nằm ở đâu trong hệ thống", vì nếu vừa audit vừa sửa thì không còn biết lỗi gốc là gì.

**DETERMINING** — một đoạn văn bản được coi là bằng chứng hợp lệ (DETERMINING) nếu nó khớp đúng *dạng* cần tìm (kind-parse), không phải chỉ vì nó tình cờ bằng đúng giá trị đáp án. Đây là điểm quan trọng để tránh "rò rỉ" — tránh việc bộ so khớp nhìn thấy trước đáp án rồi tự bịa ra là "khớp".

**HIT / MISS / ABSTAIN** — ba trạng thái kết quả correspondence: HIT (khớp đúng), MISS (không khớp dù đủ điều kiện so sánh), ABSTAIN (không đủ bằng chứng để so sánh — khác hẳn MISS, và khác hẳn "nhiệm vụ thất bại").

**DONE** — trạng thái agent tự báo đã hoàn thành nhiệm vụ (khác với có bằng chứng đúng hay không — một agent có thể DONE mà vẫn bị MISS hoặc ABSTAIN).

**Valid pair (cặp hợp lệ)** — trong các thí nghiệm có so sánh trước/sau can thiệp (counterfactual), một cặp được tính là "hợp lệ" chỉ khi cả hai lượt chạy (trước và sau) đều DONE.

**n_min = 3** — ngưỡng tối thiểu số cặp hợp lệ để một agent được đưa vào xếp hạng so sánh (ranking). Ngưỡng này được khoá (pre-registered — cam kết trước, không đổi sau khi thấy dữ liệu) trước khi biết kết quả.

**S (score)** và **STS (state-tracking score)** — S là điểm rubric thô (có thể tính từ ảnh chụp màn hình qua nhiều bước). STS là một chỉ số riêng đo việc agent có theo dõi đúng trạng thái thế giới hay không — hai con số này có thể lệch nhau, đó chính là "outcome gap" nói ở mục 1.2.

**Type A / Type B** — trong Study 1: Type A là trường hợp điểm số S thay đổi cùng chiều với việc theo dõi trạng thái (nhất quán); Type B là trường hợp điểm số S *không đổi* (ví dụ vẫn 100/100) dù việc theo dõi trạng thái trên thực tế đã sai — tức là điểm số "không nhìn thấy" được cái sai.

---

## Phần 2 — Quá trình đi tới bản draft hiện tại (tóm tắt các mốc lớn)

Đề tài này đã trải qua rất nhiều vòng kiểm tra chéo nội bộ (hơn 60 "round" audit riêng, lưu trong tài liệu theo dõi quyết định của nhóm) — em không liệt kê hết vì không cần thiết cho buổi trình bày này, chỉ nêu các mốc lớn để anh hiểu vì sao bài có hình dạng như hiện tại:

1. **Study 3 (P3) — khởi nguồn:** phát hiện gốc "discard sau khi thu thập" (M1a) được tìm ra khi audit thủ công bộ trích xuất của MyPCBench. Đây luôn là phát hiện mạnh nhất và cuối cùng trở thành CORE của bài.
2. **Hạ tầng thực thi được viết lại từ đầu (generic agent loop):** ban đầu nhóm định chạy agent thật trên 4 mô hình khác nhau (Qwen 9B, Qwen Flash, GPT, Claude) bằng công cụ "computer-use" riêng của từng hãng, nhưng gặp hai vấn đề — (a) một số hãng không tương thích với hạ tầng OpenRouter đang dùng (lỗi schema kỹ thuật), (b) ngân sách hạn chế lúc đầu. Nhóm quyết định xây một "vòng lặp agent chung" (generic loop), dùng chung một giao thức gọi công cụ bằng văn bản (không dùng API "computer-use" riêng của từng hãng), để cả 3 dòng mô hình (GPT, Qwen, Claude) đều chạy qua đúng một hạ tầng — tránh việc so sánh giữa các mô hình bị nhiễu bởi sự khác biệt hạ tầng.
3. **Nhiều lỗi hạ tầng được bắt và sửa trước khi tin vào số liệu:** ví dụ một cờ trạng thái `has_done_action` từng bị gán sai (một lượt chạy bị lỗi hệ thống hoặc bị timeout vẫn bị gắn nhãn "hoàn thành"), hoặc parser không nhận ra một số dạng gọi hàm gần đúng nhưng sai cú pháp. Mỗi lỗi này đều được kiểm chứng bằng cách đọc trực tiếp log thô, sửa, rồi chạy lại — không "vá" cho vừa với kết quả mong muốn.
4. **Study 2 (P2) — chạy ma trận 3 mô hình × 57 lượt/mô hình:** kết quả cuối: GPT-5.5 có 9 cặp hợp lệ, Qwen Flash có 8, Claude chỉ có 1 (dưới ngưỡng n_min=3). Vì chỉ có 2/3 mô hình đạt ngưỡng, quy tắc đã khoá trước (Phase 4 preregistration) tự động kích hoạt: **không đánh giá xếp hạng chính thức (Layer B)**, chỉ báo cáo kết quả thăm dò (exploratory) trên 4 nhiệm vụ có dữ liệu chung.
5. **Path A** — mở rộng sang audit phán quyết FAIL công khai trên hai benchmark WebArena/VisualWebArena (dùng lại dữ liệu của Lù và cộng sự — AgentRewardBench) để xem một hiện tượng tương tự (trống bằng chứng vs bằng chứng sai) có xuất hiện ở nơi khác không.
6. **Path UV** — thử mở rộng M1a sang một bộ dữ liệu công khai khác nữa (Microsoft CUAVerifierBench), nhưng bước kiểm chứng cuối (con người xác nhận bằng chứng bị mất có thực sự mất hẳn hay không) chưa đạt chuẩn trong thời gian cho phép — quyết định không đưa số liệu vào bài, chỉ ghi 1 câu trong Limitations.
7. **Tái cấu trúc bài viết (structural revision, "hostile review"):** vì bài ban đầu có tới hơn 10 đóng góp/tuyên bố độc lập chạy song song (P1–P4, Path A, formalization...) — một bản tự-phản biện nội bộ nghiêm khắc (đóng vai reviewer cố tình "giết" bài) đã chỉ ra đây là điểm yếu lớn nhất (quá nhiều mảnh ghép, dễ bị reviewer thật đánh vì tản mạn, không có 1 đóng góp rõ ràng). Từ đó nhóm quyết định: chỉ giữ **đúng 1 CORE** (P3), mọi thứ khác giáng cấp xuống Secondary/Supporting/phụ lục, và khoá lại toàn bộ cách diễn đạt (claim ledger — một "sổ khoá câu chữ", quy định từng câu được nói thế nào, cấm nói thế nào) để tránh overclaim (nói quá những gì dữ liệu thực sự cho phép).

Bản `main.tex` v0.5 hiện tại (đã chuyển hẳn sang khuôn mẫu chính thức của AAMAS — `aamas.cls`, 2 cột, ẩn danh vì blind review) chính là kết quả của bước tái cấu trúc đó, và đã được rà lại toàn bộ (689 dòng, đọc kỹ từng dòng) để xác nhận nó tuân thủ đúng những gì bản tự-phản biện yêu cầu — không còn overclaim nào lọt lưới.

---

## Phần 3 — Rà soát tài liệu liên quan (Related Work)

### 3.1. Công trình gần nhất, phải đối chiếu trực tiếp: Dong và cộng sự

Dong và cộng sự coi điểm số CUA là đầu ra của một pipeline (không phải quan sát trực tiếp episode), và audit ngược 150 trajectory công khai đã bị chấm FAIL trên 5 benchmark — phát hiện 15.3% phán quyết FAIL là sai (10.7% do evaluator chấm nhầm âm tính giả, 4.7% do nhiệm vụ tự nó bị lỗi/lỗi thời), thêm 3.3% không rõ ràng từ bằng chứng được công bố.

Đây là một **audit phán quyết** (verdict audit): phán quyết FAIL đã công bố có đúng không?

Bài của mình khác ở chỗ: không audit phán quyết cuối cùng, mà audit **chính phép biến đổi** I→P→E bên trong hệ thống, trên những trajectory mình đang giữ sẵn — rồi từ đó xây dựng thêm một phép đo có căn cứ quan sát tường minh (observation-grounded) và ghi lại nơi việc xây dựng đó dừng lại (không định danh được nữa).

### 3.2. Xue và cộng sự, Rosset và cộng sự — mất quan sát ở "frame cuối cùng"

Hai công trình này (Online-Mind2Web/WebJudge của Xue, và một verifier khác của Rosset) chỉ ra: các judge dùng LLM để chấm agent qua ảnh chụp màn hình thường chỉ nhìn frame cuối cùng (last-frame), hoặc bị quá tải khi nhìn toàn bộ trajectory — cả hai đều làm mất bằng chứng thị giác quan trọng. Rosset còn đề xuất một verifier biết tự chọn ảnh chẩn đoán theo từng tiêu chí chấm.

Đây là mất quan sát đã biết ở phía **thị giác** (visual). Bài của mình khác: đóng băng một bộ trích xuất **văn bản** (last-text), và đo mất bằng chứng *sau khi* bằng chứng đã vào một tập tích luỹ (accumulator) — một vị trí lỗi khác hẳn "chưa từng nhìn thấy ảnh".

### 3.3. Shao và cộng sự — tính hợp lệ của giao thức (protocol validity)

Shao và cộng sự audit 2.385 trace trên 15 benchmark, tìm các đường tắt (shortcut), khai thác lỗ hổng (exploitation), và tình trạng điểm bị thổi phồng. Trục phân tích của họ là exposure → exploitation → shortcut gây hiểu nhầm.

Trục của bài mình là observation → evidence → correspondence, kể cả mất bằng chứng *sau khi* bằng chứng đã sẵn có. Hai trục không thay thế nhau.

### 3.4. Nền tảng lý thuyết đo lường (validity)

Bài không phát minh lý thuyết đo lường mới, mà dựa trên các công trình nền tảng:

- **Messick** — coi validity (tính hợp lệ của phép đo) là một quá trình nghiên cứu khoa học về ý nghĩa và cách dùng điểm số, không phải một thuộc tính cố định của bài test.
- **Cronbach và Meehl** — đặt construct validity (tính hợp lệ của khái niệm được đo) trong mạng lưới các suy luận xung quanh một bài kiểm tra.
- **Kane** — nguyên tắc mà bài dựa vào nhiều nhất: cái được kiểm chứng (validate) là *cách diễn giải và cách dùng* điểm số, không phải bản thân điểm số.
- **Jacobs và Wallach** — đưa mô hình hoá đo lường (measurement modeling) vào các hệ thống tính toán.
- **Raji và cộng sự, Bowman và Dahl, Bean và cộng sự** — chỉ ra các lỗi construct-validity khi một bài test hữu hạn bị coi là thước đo năng lực tổng quát; Bean còn cho một checklist thực hành để kiểm tra construct validity của benchmark LLM.

Đóng góp của bài không phải là một khung lý thuyết validity mới, mà là **một cuộc audit ở đúng tầng trajectory–observation–evidence**, dưới một giao thức đã đóng băng, cô lập được cơ chế discard-sau-khi-thu-thập và có thí nghiệm sửa chữa có dấu (signed repair experiment) để kiểm tra.

### 3.5. Các công trình audit evaluator/observation khác

- **WeaveBench** — chỉ ra chấm điểm chỉ theo kết quả cuối (outcome-only) thổi phồng tỷ lệ pass so với một judge biết nhìn cả trajectory.
- **Lù và cộng sự (AgentRewardBench)** — biến chính các judge tự động thành đối tượng được đánh giá (không phải agent).
- **Cao và cộng sự** — ghi nhận hiện tượng "corrupt success" (thành công bị hỏng theo quy trình); **Advani** — ghi nhận "false success" (đóng nhiệm vụ tự tin nhưng không đúng kết quả thực).
- **Zhang và cộng sự** — một hướng khác (không phải trọng tâm bài này): định vị lỗi về đúng bước/thành phần chịu trách nhiệm trong chính agent, chứ không phải audit kênh quan sát của bộ chấm điểm.

### 3.6. Vị trí của bài trong bức tranh chung

Nói ngắn gọn nhất có thể để anh dễ nhớ:

> **Dong**: audit *phán quyết* hồi cứu trên trace công khai — tập trung xem FAIL công bố có đúng không.
> **Bài này**: coi chính công cụ đánh giá là đối tượng thí nghiệm, đóng băng phép biến đổi observation/evidence, audit mất bằng chứng *bên trong* phép biến đổi đó (kể cả bằng chứng đã thu thập rồi bị vứt), thử nghiệm sửa chữa thoáng hơn, và ghi lại ranh giới định danh được khi xây dựng một phép đo có căn cứ quan sát tường minh.

---

## Phần 4 — Cấu trúc hiện tại của bài báo

Bảng dưới đây (gọi là "evidence map" trong bài) chốt lại vai trò của từng phần — đây là kết quả trực tiếp của vòng tái cấu trúc nói ở Phần 2, mục 7:

| Vai trò | Nguồn | Cách đọc được cho phép |
|---|---|---|
| **Core** | P3 | Discard-sau-khi-thu-thập (M1a) và việc sửa chữa có dấu không chiếm ưu thế, trên một bộ trích xuất đã đóng băng |
| **Secondary** | P4 | Ranh giới xây dựng được của quan sát/định danh, đặc biệt: tuân thủ giao diện ≠ định danh hai chiều, và một mẫu toàn-HIT |
| **Supporting** | P1, P2 | Chỉ trong phụ lục: điểm số không nhất thiết theo dõi đúng thế giới; đánh giá có thể thay đổi cơ sở bằng chứng của một so sánh |
| **Supporting** | Path A | FAIL công bố trộn lẫn I rỗng (126) và bằng chứng-sai (173) trên một lát cắt string/URL đã thừa nhận; không phải tỷ lệ FAIL-sai |
| **Formal** | 𝓜(τ,𝓘) | Sổ sách hình thức cho các tuyên bố được biện minh dưới một I đã khai báo |
| **Consequence** | Bảng 8 câu hỏi | Tám câu hỏi báo cáo thực hành; không phải chuẩn mực đã kiểm định |

Vì sao phải giáng cấp mạnh như vậy? Bản tự-phản biện nội bộ ("hostile review") chỉ ra bản gốc có tới hơn 10 tuyên bố độc lập chạy song song — đây chính xác là kiểu bài dễ bị reviewer thật đánh giá là "tản mạn, không rõ một đóng góp trung tâm". Sau khi giáng cấp, bài chỉ còn đúng 1 CORE, và mọi câu chữ đều được đối chiếu với một "claim ledger" (sổ khoá câu chữ) để đảm bảo không có câu nào nói quá những gì dữ liệu cho phép. Em đã tự đọc lại toàn bộ 689 dòng của `main.tex` để xác nhận việc này — không tìm thấy chỗ nào vi phạm.

---

## Phần 5 — Kết quả chính (CORE): Mất bằng chứng bên trong một bộ trích xuất đã đóng băng

### 5.1. Thiết lập thí nghiệm

Đơn vị phân tích là một "row" — một thành phần trong tập xác định (determining set) trên một lượt chạy (leg). Tổng cộng có **134 row trên 57 leg**.

Một row được gọi là **R1-positive** nếu giá trị đúng (gold) xuất hiện nguyên văn trong câu trả lời của agent. Trong 134 row: **59 row là R1-positive** (20 MATCH + 39 RECALL_MISS), 75 row còn lại là ABSENT (đáp án không hề xuất hiện trong câu trả lời — không phải lỗi hệ thống trích xuất, không tính vào audit này).

> Các tỷ lệ dưới đây là *có điều kiện* trên tập đã audit (59 row R1-positive). Đây **không phải** tỷ lệ "agent trả lời sai", không phải tỷ lệ evaluator bất đồng với nhau, và không phải tỷ lệ ảnh chụp màn hình bị thiếu.

Bộ trích xuất đã đóng băng bắt đúng **20/59 row R1-positive** (độ nhạy — sensitivity — 0.339) và bỏ lỡ **39 row**.

### 5.2. Vì sao 39 row đó bị bỏ lỡ — 5 nguyên nhân, đếm thủ công

| Mã | n | Ý nghĩa |
|---|---|---|
| **M1a** | **13** | **Gold đã vào tập `found` (đã tìm thấy) và bị loại bỏ** |
| M1b | 7 | Các ứng viên "cãi nhau"; gold không nằm trong số được chọn |
| M2 | 9 | Không có nhãn/từ khoá nào khớp ở bất kỳ đâu trong câu trả lời |
| M3 | 5 | Có khớp nhãn, nhưng gold nằm ngoài mọi cửa sổ ±window quanh nó |
| M4 | 5 | Hệ thống báo ra một giá trị khác, không phải gold |

**M1a (13 row) là trọng tâm của cả bài** — đây là trường hợp duy nhất mà "máy đã cầm đúng đáp án trong tay rồi mới đánh rơi". Bốn loại còn lại là các kiểu lỗi bình thường hơn (không tìm thấy gì, tìm sai vị trí, v.v.) — không phải điểm mới của bài.

### 5.3. Post-collection discard — vì sao đây là một vị trí lỗi mới, chưa ai chỉ ra

Trong 13 row M1a: **7/13 row, gold là đa số tuyệt đối (strict majority) trong các ứng viên đã tích luỹ** — tức không phải trường hợp mơ hồ cận biên, mà gold rõ ràng chiếm ưu thế trong chính tập mà hệ thống đã thu thập, vậy mà vẫn bị loại.

Bốn câu khẳng định phủ định (để làm rõ đây không phải bốn loại lỗi đã biết trước đó):

- Không phải agent làm sai — chuỗi gold có trong câu trả lời *và* trong bộ tích luỹ.
- Không phải dữ liệu bị thiếu thông thường — quan sát này tồn tại ở một trạng thái trung gian của hệ thống.
- Không phải mất frame cuối kiểu Xue/Rosset — kênh này là văn bản, không phải ảnh.
- Không phải lỗi judge kiểu thông thường — không có LLM judge nào ngồi trong bộ trích xuất này.

### 5.4. Đối chiếu độc lập bằng chấm điểm qua ảnh — vì sao 13 row này "đáng sợ" hơn con số cho thấy

Đây là phần em muốn nhấn mạnh riêng với anh, vì nó là bằng chứng thuyết phục nhất cho việc "hai cách quan sát khác nhau có thể kết luận trái ngược nhau trên cùng một episode". Đối chiếu 13 row M1a với một rubric chấm bằng ảnh chụp màn hình (screenshot rubric) đã khoá sẵn từ trước, độc lập hoàn toàn với kênh văn bản:

| Đại lượng | n |
|---|---|
| Có thể đối chiếu được với S đã khoá | 10/13 |
| S = 100 (hoàn hảo) trong số đối chiếu được | **7/10** |
| Nằm trong tập Â (có cặp hợp lệ) với Y=0 (theo dõi trạng thái sai ở mức cặp) | **9/9** |
| Gold xuất hiện sớm hơn trong log (trước dòng trả lời cuối) | 8/13 |

Nói dễ hiểu: **7 trong 10 trường hợp đối chiếu được, rubric chấm bằng ảnh cho điểm tuyệt đối (S=100) — "nhìn qua ảnh thì thấy agent làm đúng hoàn toàn" — ngay trong lúc kênh văn bản đã đánh rơi mất đáp án đúng.** Và cả 9/9 trường hợp có thể theo dõi ở mức cặp thì việc theo dõi trạng thái (Y) đều cho kết quả sai (0). 8/13 row, gold còn xuất hiện *sớm hơn* trong log — tức nó không biến mất ngẫu nhiên, nó *có ở đó*, chỉ là bước tổng hợp không giữ lại.

> ***Lưu ý khi trình bày:** Điều này không chứng minh "ảnh có chứa gold" (bài không đọc file PNG cho phần này), và không phải một audit trên 171 trajectory. Đây là cái "vì sao cần quan tâm" cục bộ trên chính instrument này: một rubric thị giác toàn trajectory có thể trông như thành công trên cùng episode mà bằng chứng văn bản đã không sống sót qua bộ trích xuất.*

M1a không loại trừ lẫn nhau với các row bị miss khác (25/75 row ABSENT cũng mang đặc điểm M1); M1a là cái tên chỉ đúng loại "bằng chứng có thể phục hồi nhưng bị vứt bỏ". Không có câu chuyện một-nguyên-nhân-duy-nhất nào được cho phép khẳng định ở đây. Một dự đoán phụ đã đăng ký trước (miss sẽ tập trung ở các nhiệm vụ có can thiệp thế giới bị *fail*) — khoảng tin cậy chồng lấn nhau, bài không thay bằng một kết luận đảo ngược.

### 5.5. Thử "sửa" hệ thống — và vì sao sửa thoáng hơn không phải lời giải

Bốn kiểu can thiệp tầng (layer intervention) được xác định *trước khi* chạy: R-AGG (plurality — lấy đa số) nhắm vào M1a; R-SCOPE, R-CMP, R-CHAN nhắm vào các loại miss khác; ALL gộp tất cả. Không có cấu hình nào được đề xuất làm bộ trích xuất thay thế.

| Cấu hình | Bắt đúng /59 | Thay đổi có dấu so với ban đầu | Số câu ĐÚNG bị phá /20 |
|---|---|---|---|
| FROZEN (ban đầu) | 20 | --- | 0 |
| **R-AGG** | 28 | **+8 đúng thêm, nhưng cũng +18 sai thêm** | 0 |
| **ALL** (gộp hết) | 10 | **tệ hơn cả ban đầu** | 16 |

(Bảng đầy đủ 6 cấu hình, gồm cả R-SCOPE và R-CHAN, nằm ở Phụ lục C của tài liệu supplementary — không đưa vào thân bài vì không phải trọng tâm.)

Dưới cấu hình sửa thoáng hơn đã định trước, **8 câu đúng thêm được giải phóng, nhưng đi kèm 18 câu sai thêm.** R-AGG là can thiệp duy nhất làm tăng độ nhạy (20→28), nhưng làm vậy bằng cách giải phóng 26 lượt ABSTAIN — tức là "tìm được thêm bằng chứng" không đồng nghĩa "phục hồi đúng phép đo mong muốn". Gộp hết mọi cách sửa lại (ALL) thì **tệ hơn cả để nguyên bộ trích xuất đóng băng** (10 so với 20). Một can thiệp sửa ở tầng so sánh sau (R-CMP) hoàn toàn không thể cứu được một lượt miss đã xảy ra ở tầng trước đó (R-CMP giống hệt từng bit với FROZEN).

**Kết luận được cho phép nói (licensed claim) mang tính cục bộ theo instrument**: bài **không** ước lượng M1a xảy ra bao nhiêu lần ở các evaluator CUA khác, và **không** đề xuất R-AGG như một phương pháp để dùng.

> ***Lưu ý khi trình bày:** Đây chính là đóng góp thứ hai của bài, sau bản thân phát hiện M1a — không chỉ chỉ ra lỗi, mà còn chứng minh bằng thực nghiệm rằng "nới lỏng cho thoáng hơn" không tự động là cải thiện, kể cả khi nới đúng chỗ.*

---

## Phần 6 — Kết quả bổ trợ (Secondary): Ranh giới xây dựng được của đánh giá có căn cứ quan sát

Phần 5 cho thấy một bộ trích xuất *có sẵn* có thể mất bằng chứng *sau khi* đã thu thập. Phần này hỏi tiếp: nếu tự tay xây dựng tường minh một giao thức quan sát (observation-grounded), thay vì audit một bộ trích xuất kế thừa, thì có tránh được vấn đề không?

P4 **không phải** bốn metric thất bại, không phải bảng xếp hạng, không phải metric tin cậy thay thế, và **không phải** một đánh giá độ tin cậy của Flash (mô hình Qwen dùng trong các thí nghiệm này). Đây là **một chuỗi xây dựng** cho thấy các ranh giới liên tiếp: quan sát rỗng → tuân thủ giao diện nhưng không định danh được → mẫu HIT dày đặc nhưng không có biến thiên hai chiều.

Kênh quan sát trong suốt P4 luôn là **văn bản trả lời cuối cùng của agent, không có ảnh hay tool-trace làm phương án dự phòng ngầm**. Trạng thái hoàn thành nhiệm vụ (execution status) không bao giờ được tính là HIT/MISS. ABSTAIN luôn là "thiếu phép đo tương ứng", không phải "nhiệm vụ thất bại".

| Ranh giới | Quan sát đã khoá | Cách đọc được cho phép |
|---|---|---|
| Bằng chứng E xác định vắng mặt khỏi I đã khai báo | 40/40 DONE; 30 ABSTAIN; Flash coverage 0.1667 | Hoàn thành ≠ bằng chứng trong I |
| Tuân thủ giao diện ≠ định danh hai chiều | Form 0.9333; H3 không đánh giá được | Tuân thủ giao diện ≠ ước lượng được hai chiều |
| Mẫu chỉ toàn HIT, quy tắc đã khoá | 30 HIT / 0 MISS; I_CC=0; G2 10/10 | Correspondence hai chiều không định danh được ở đây |

### 6.1. Bằng chứng có thể vắng mặt khỏi kênh đã khai báo (P4-B/C)

P4-B chấm HIT/MISS/ABSTAIN dựa trên văn bản trả lời cuối, trên 40 episode xác nhận (20 cụm × 2 mô hình). Cả 40 lượt đều kết thúc DONE. Kết quả: HIT 5, MISS 5, **ABSTAIN 30**. Mọi lượt ABSTAIN đều vì lý do `no_anchor` — không có chuỗi neo (anchor) khớp với chỉ dẫn nằm trên một dòng kết thúc bằng xuống dòng trong văn bản cuối cùng. Hệ thống **không** sau đó đi mò thêm ảnh, tool-trace, hay các lượt trung gian.

P4-C chấm văn bản cuối (không có cấu trúc) đối chiếu với gold độc lập. Trên 30 episode xác nhận của Flash: HIT 3, MISS 2, **ABSTAIN 25**; coverage (độ phủ) chỉ 0.1667 — trượt ngưỡng đã đăng ký trước (≥0.5).

Hai bước này là một bài học: agent tự nhiên không nhất thiết truyền tải bằng chứng quyết định qua một kênh văn bản cuối chưa được khai báo trước, và việc hoàn thành nhiệm vụ (terminal completion) **không** đồng nghĩa với thành công của phép đo có căn cứ quan sát. Kết luận **không phải** "văn bản cuối là kênh đúng cho CUA", và **không phải** "agent kém năng lực". Bài học đúng là: nếu kênh đã khai báo không chứa bằng chứng quyết định, hệ thống phải ABSTAIN chứ không được âm thầm quay sang tìm nguồn khác.

### 6.2. Tuân thủ giao diện không đồng nghĩa định danh được hai chiều (C2)

Metric v2 yêu cầu một dòng `CLAIM:` khai báo tường minh — đây là ràng buộc về giao diện (interface constraint), bản thân nó không phải là bằng chứng. Trên Flash, N=30: HIT 26, MISS 2, ABSTAIN 1, không chấm được 1; **Form (tỷ lệ tuân thủ giao diện) = 0.9333** (đạt ngưỡng). MISS thông thường vẫn tồn tại (2 cụm). Nhưng sàn phân biệt định danh dự kiến (C2-intended discrimination floor) là **NOT_EVALUABLE** — chỉ có 8 trường hợp đủ điều kiện, dưới ngưỡng 10 cần thiết, tỷ lệ miss trên lát này bằng 0.

Nói dễ hiểu: agent tuân thủ đúng format yêu cầu (Form cao) không có nghĩa là hệ thống có thể đo được correspondence hai chiều (vừa nhận ra đúng, vừa nhận ra sai). **Tuân thủ giao diện không phải là tính hợp lệ (validity).**

### 6.3. Một mẫu năng lực cao vẫn có thể thiếu biến thiên âm (P4-D)

Câu hỏi ở bước này: nếu không ép một hạn ngạch MISS (MISS quota), thì correspondence hai chiều có quan sát được không? Trên Flash, N=30: **HIT 30, MISS 0, ABSTAIN 0**; Form = 1.0000 (hoàn hảo); nhưng **I_CC = 0** dưới quy tắc đã khoá (I_CC = 1 chỉ khi có ít nhất 8 HIT *và* 8 MISS). Năng lực dương (plus-competence) vẫn giữ vững: G2 đạt 10/10 HIT. Các lát minus và plus-minus cũng đều 10/10 HIT.

Phân loại: **W1 — thử thách yếu / correspondence vẫn không quan sát được.** Cổng thất bại chính xác là G3 (cổng yêu cầu biến thiên hai chiều).

Dưới quy tắc đã khoá trước, mẫu này **không chứa đủ quan sát âm** để định danh được estimand hai chiều. I_CC = 0 là một kết quả về *khả năng quan sát của giao thức và mẫu* — **không phải** một phát hiện rằng năng lực cao gây ra tình trạng không định danh được, **không phải** phát hiện agent không đáng tin, và **không phải** tuyên bố Flash hoàn toàn đáng tin cậy. Nhánh công việc này đã đóng lại: không tăng thêm distractor (yếu tố gây nhiễu) để ép ra MISS, không chỉnh lại parser, không tạo ra một "nhà máy sản xuất MISS" nhân tạo để né tránh kết quả này.

> ***Lưu ý khi trình bày:** P4 phụ thuộc vào P3 — nó chỉ ra ranh giới của việc xây dựng, chứ không đưa ra một điểm số thay thế. Ba bước 6.1–6.3 đọc liền mạch là một câu chuyện: (1) hoàn thành nhiệm vụ không đảm bảo có bằng chứng, (2) đúng format không đảm bảo định danh được, (3) ngay cả khi có bằng chứng và đúng format, thiếu quan sát âm vẫn khiến correspondence hai chiều không định danh được.*

---

## Phần 7 — Kết quả hỗ trợ khác (chỉ nằm trong phụ lục, không phải trọng tâm)

### 7.1. Study 1 (P1) — điểm số có thể tách rời khỏi việc theo dõi đúng thế giới

Đây là một demo tồn tại/phân ly (existence/dissociation demonstration), **không phải** ước lượng tỷ lệ phổ biến (prevalence). Lịch trình đã đóng băng thực thi 46/50 cell dự kiến (92 leg); 35 leg lỗi thực thi; 24 cặp hợp lệ.

| Lane | Hợp lệ | Track-valid | Type A | Sens. | Type B |
|---|---|---|---|---|---|
| Claude | 9 | 7 | 6 | 1 | 2 |
| GPT-5.5 | 8 | 7 | 3 | 4 | 1 |
| Qwen3.5-35B-A3B | 1 | 1 | 1 | 0 | 0 |

Claude: tỷ lệ bất biến (invariance) 6/7 = 0.857 (khoảng tin cậy [0.421, 0.996]). GPT-5.5: 3/7 = 0.429 ([0.099, 0.816]). Các khoảng tin cậy này khá rộng — vì cỡ mẫu nhỏ — nên bài không headline một tỷ lệ bất biến gộp chung.

### 7.2. Study 2 (P2) — đánh giá/lựa chọn có thể thay đổi cơ sở bằng chứng của một so sánh

Tiêu đề đã khoá của phần này: "việc đánh giá và lựa chọn có thể thay đổi cơ sở bằng chứng của một so sánh độ tin cậy" — **không phải** tuyên bố "evaluator thay đổi sự thật".

Ba agent, mỗi agent chạy lịch trình đã đăng ký trước 57 leg: GPT-5.5, Qwen3.8-Flash, Claude Opus 4.6. Ngưỡng đưa vào xếp hạng n_min=3 cặp hợp lệ, và quy tắc "dưới 3 agent được xếp hạng thì không đánh giá phép kiểm định lựa chọn xác nhận (confirmatory selection test)" — cả hai đều được cam kết *trước khi* có bất kỳ kết quả nào.

| Agent | DONE/57 | \|Â\| | mean S⁰ | mean STS |
|---|---|---|---|---|
| GPT-5.5 | 32 | 9 | 69.3 | 0.130 |
| Qwen3.8-Flash | 29 | 8 | 95.8 | 0.229 |
| Claude Opus 4.6 | 4 | 1 | 100 | 0 |

Claude chỉ kết thúc DONE trên 4 leg thuộc 3 task, nên |Â|=1 — dưới ngưỡng n_min. Chỉ 2/3 agent đạt ngưỡng xếp hạng, nên theo đúng quy tắc đã khoá, **phép kiểm định lựa chọn xác nhận không được đánh giá**.

Trên 4 nhiệm vụ có dữ liệu chung (common support), gán nhãn thăm dò (exploratory), một bootstrap có ghép cặp (seed 20260904, B=5000): Flash trừ GPT cho ΔS⁰ = +46.5 (KTC 95% [21.0, 72.0]) và ΔSTS = −0.042 ([−0.125, 0.000]). Việc đảo dấu này chỉ chặt chẽ trên đúng **1 trong 4 nhiệm vụ** (`retrieval-f009`) và hoà ở 3 nhiệm vụ còn lại — bỏ nhiệm vụ đó ra thì so sánh STS trở thành hoà. Bài **không** tuyên bố về mức độ phổ biến của sự bất ổn định trong xếp hạng.

Một điểm đáng chú ý khác: các cell bị loại (không DONE) có điểm trung bình thấp hơn hẳn (46.4, 44.9, 26.1 so với 69.3, 95.8, 100 trên Â) — nhưng vẫn có 2, 2, và 1 cell bị loại đạt điểm ≥90 dù không có DONE chuẩn. Một giao thức chỉ tính điểm khi hoàn thành thì không thể diễn tả được tiến độ rubric-visible mà không đóng nhiệm vụ.

### 7.3. Path A — FAIL công khai trộn lẫn hai trạng thái quan sát khác nhau

Trên 299 phán quyết FAIL đã công bố (lát cắt string/URL đã thừa nhận của WebArena/VisualWebArena, dùng lại trajectory của Lù và cộng sự — AgentRewardBench): oracle ghi nhận cùng một nhãn FAIL cho hai trạng thái quan sát hoàn toàn khác nhau — **126 trajectory không có ứng viên nào để kiểm tra** trong kênh I đã khai báo (last-answer/last-URL), và **173 trajectory có ứng viên nhưng ứng viên đó không khớp gold**.

ABSTAIN ≠ MISS. V=0 (FAIL) không nói được là loại nào trong hai loại đó. FAIL vì I rỗng chính là hành vi *đúng theo đặc tả* của `string_match`/`url_match` — **không phải** bằng chứng cho rằng 126 phán quyết FAIL đó là vô căn cứ từ I, và **không phải** kiểu rà soát của con người như Dong đã làm. Bài **không** báo cáo một tỷ lệ áp dụng cho toàn bộ AgentRewardBench.

---

## Phần 8 — Path UV: nỗ lực mở rộng sang dữ liệu công khai khác (chưa đưa vào bài chính)

Sau khi có M1a trên MyPCBench, nhóm thử kiểm tra xem hiện tượng "discard sau khi thu thập" có xuất hiện ở một bộ đánh giá công khai khác không — dùng kiến trúc Universal Verifier của Microsoft trên bộ dữ liệu công khai CUAVerifierBench (verifier này chấm trajectory bằng ảnh chụp màn hình, dùng rubric × giới hạn top-K ảnh mỗi tiêu chí trước khi chấm).

Thiết kế gồm 3 bước: U1 (kiểm tra điều kiện cần bằng máy — có bao nhiêu episode có số ảnh vượt quá K), R-recovery (tự chạy lại đúng thuật toán của UV trên một instance riêng để tái tạo lại ảnh nào bị loại, vì Hugging Face không công bố ma trận điểm liên quan thật), và U2 (con người gán nhãn xem ảnh bị loại có phải là bằng chứng quyết định hay không).

Kết quả tới thời điểm hiện tại: bước U1 đã đạt (93/106 episode thoả điều kiện cơ hội mất bằng chứng), bước R-recovery cũng đã dựng được cơ chế tái tạo (đã tự sửa một lỗi thiết kế quan trọng: phân biệt rõ "bị loại nhưng vẫn còn bằng chứng tương đương ở ảnh khác được giữ lại" — REDUNDANT — với "bị loại và mất hẳn, không còn ở đâu" — IRRECOVERABLE — chỉ loại sau mới được phép coi là tương tự M1a). Nhưng bước kiểm chứng cuối cùng bằng con người (U2, xác nhận IRRECOVERABLE) **chưa đạt chuẩn tin cậy đủ vững trong thời gian cho phép**.

**Quyết định:** không đưa số liệu Path UV vào bài, chỉ ghi một câu ngắn gọn, trung thực trong phần Limitations: đã thử một nỗ lực có mục tiêu hơn trên một corpus screenshot công khai (CUAVerifierBench), thoả được điều kiện cơ hội và tái tạo discard, nhưng bước kiểm chứng cuối về khả năng phục hồi chưa đạt chuẩn — **không rút ra kết luận nào về việc M1a có "vận chuyển" (transport) được sang nơi khác hay không**, từ cả nỗ lực này lẫn nỗ lực trước đó (audit các công cụ CUA công khai khác, không tìm được corpus nào thoả điều kiện hợp lệ đã đóng băng mà không phải sửa giao thức quan sát hoặc evaluator).

> ***Lưu ý khi trình bày:** Đây là một quyết định có chủ đích, không phải bỏ quên — giống cách một nỗ lực trước đó (không tìm được bộ dữ liệu nào đủ điều kiện) cũng được ghi nhận minh bạch trong Limitations thay vì giấu đi hoặc thổi phồng bằng số liệu chưa đủ tin cậy.*

---

## Phần 9 — Hệ quả thực hành: tám câu hỏi báo cáo

Từ toàn bộ phân tích trên, bài rút ra một bảng 8 câu hỏi mà bất kỳ ai công bố một con số reliability cho CUA (trong bối cảnh giao thức đã đóng băng) nên tự trả lời trước khi con số đó được đọc như một tuyên bố tin cậy. Đây **không phải** một chuẩn mực đã kiểm định, **không phải** metric mới, **không phải** một định lý — chỉ là hệ quả thực hành của phân tích.

| # | Câu hỏi |
|---|---|
| 1. Đối tượng | Độ tin cậy của hệ thống nào, trên họ nhiệm vụ nào, dùng để làm gì? |
| 2. Đại lượng đo | Trạng thái/kết quả nào được định nghĩa độc lập là "đúng"? Ai khoá gold (L)? |
| 3. Quan sát | Phần nào của τ thực sự được quan sát (I)? Điều gì bị cấm làm phương án dự phòng ngầm? |
| 4. Bằng chứng | Điều gì khiến một quan sát trở thành DETERMINING? Thế nào là NONDETERMINING? |
| 5. Correspondence | Bằng chứng được khớp với đại lượng đo như thế nào? Bộ so khớp có được phép nhìn thấy value(L) không? |
| 6. Abstention | Chuyện gì xảy ra khi bằng chứng không đủ? ABSTAIN có được phân biệt rõ với MISS và với lỗi thực thi không? |
| 7. Không rò rỉ | Quy trình có thể nhìn thấy trước đáp án mà nó đang định chấm không? |
| 8. Định danh được | Mẫu có đủ biến thiên dương *và* âm để hỗ trợ đúng tuyên bố mong muốn (một chiều hay hai chiều) không? |

---

## Phần 10 — Giới hạn của bài (Limitations)

Em liệt kê đầy đủ vì đây là phần quan trọng để tránh bị hỏi bất ngờ khi trình bày:

- M1a mang tính đặc thù theo instrument cho tới khi được "vận chuyển" (transport) sang nơi khác — bài **chưa** làm việc vận chuyển đó.
- Study 1–3 đều thuộc cùng họ MyPCBench; các tập dữ liệu **không được cộng dồn**, kết quả **không phải** ước lượng tỷ lệ phổ biến đa-benchmark.
- P4 là một "slate" (bộ nhiệm vụ) được dựng riêng, **không phải** một benchmark công khai.
- Kênh văn bản cuối (last-text) là một kênh quan sát nghiêm ngặt đã khai báo, **không phải** giao thức chuẩn cho CUA — Xue và Rosset đã chỉ ra chấm bằng ảnh frame cuối cũng mất bằng chứng tương tự.
- P4-D là kết quả về khả năng định danh của giao thức-và-mẫu (I_CC=0 vì mẫu có 0 MISS dưới một quy tắc đòi cả hai phía), **không phải** ước lượng độ tin cậy của Flash.
- 𝓜(τ,𝓘) là sổ sách hình thức, **chưa có triển khai thực nghiệm**.
- Bài **không** đo độ tin cậy hay an toàn của CUA khi triển khai thực tế.
- Path A **không** dùng thành công của con người làm gold cho correspondence, và **không** khẳng định FAIL-vì-rỗng là phán quyết oracle sai.
- Đã thử audit các công cụ CUA công khai khác để tìm một evaluator độc lập lộ ra trạng thái bằng chứng trung gian ở đúng độ chi tiết cần để kiểm tra post-collection discard — **không corpus nào thoả điều kiện hợp lệ đã đóng băng** mà không phải sửa giao thức quan sát hoặc evaluator. Một nỗ lực thứ hai, có mục tiêu hơn, trên CUAVerifierBench (Path UV, Phần 8) thoả được điều kiện cơ hội và tái tạo discard, nhưng bước kiểm chứng con người cuối cùng về khả năng phục hồi chưa đạt chuẩn tin cậy trong thời gian cho phép — bài **không** rút kết luận vận chuyển từ cả hai nỗ lực.

---

## Phần 11 — Tình trạng nộp bài hiện tại

- Đang nhắm **AAMAS 2027** (Hà Nội, 3–7/5/2027), giới hạn 8 trang nội dung ở track Research Paper (references không giới hạn).
- Đã migrate hoàn toàn sang khuôn mẫu chính thức `aamas.cls` (2 cột, bản ẩn danh vì blind review, đúng copyright block CC-BY yêu cầu).
- Toàn bộ phần phụ lục chi tiết (Study 1, Study 2, bảng sửa chữa đầy đủ 6 cấu hình, bảng M1a nối với S/Y, bảng thành phần FAIL công khai) đã tách thành một file `supplementary.tex` riêng, nộp kèm dạng zip theo đúng quy định của AAMAS 2027 (supplementary material là tuỳ chọn, không tính vào 8 trang, reviewer xem tuỳ ý).
- Bài đã qua một vòng "hostile review" nội bộ nghiêm khắc (tự đóng vai reviewer cố tình tìm cách bác bỏ đóng góp) và một "claim ledger" khoá câu chữ — em đã tự đọc lại toàn bộ bản draft hiện tại để xác nhận nó tuân thủ đúng các yêu cầu đó, không tìm thấy vi phạm nào.
- Vì bài chủ đích giữ phạm vi hẹp (một instrument, một họ benchmark, đúng 1 CORE, không claim rộng) nên có khả năng rơi vào diện **AAMAS Findings** thay vì Proceedings chính — nhưng Findings vẫn là **publication thật: có peer review, lưu trữ chính thức (archival), trích dẫn được**, không phải "giải an ủi".
- Hai điểm kỹ thuật còn tồn đọng, chưa ảnh hưởng nội dung khoa học nhưng cần dọn trước khi nộp: (1) tình trạng git của repo đang lệch cả hai chiều so với remote (một số commit chưa push, một số commit trên remote chưa kéo về) — cần ai đó có quyền push xử lý trước khi lệch thêm; (2) một mục README còn ghi nhầm số phiên bản draft (v0.4 thay vì v0.5).

---

## Phần 12 — Những điều em cần xin ý kiến anh Khải

### 12.1. Có nên chạy tiếp Path UV không?

Path UV gần đạt được mục tiêu (2/3 điều kiện đã thoả), chỉ còn bước kiểm chứng con người cuối cùng chưa đạt chuẩn. Nếu hoàn thành được, đây sẽ là bằng chứng đầu tiên cho thấy M1a "vận chuyển" được sang một bộ dữ liệu công khai khác — một đóng góp có thể đáng để thêm vào, hoặc để dành cho một bài riêng. Em xin ý kiến anh: có đáng đầu tư thêm thời gian để hoàn thiện bước kiểm chứng con người đó không, hay nên giữ nguyên như hiện tại (chỉ 1 câu trong Limitations) và tập trung hoàn thiện bài đang có?

### 12.2. Mức độ chi tiết của phần P1/P2/Path A trong thân bài

Hiện tại P1, P2, Path A chỉ còn 1 dòng mỗi phần trong bảng evidence map ở thân bài, chi tiết đẩy hết ra phụ lục. Đây là quyết định có chủ đích sau vòng "hostile review" để giữ bài tập trung vào đúng 1 CORE. Em xin ý kiến anh: mức độ tối giản này có ổn không, hay nên giữ lại thêm một chút chi tiết trong thân bài (ví dụ bảng Study 2 coverage) để reviewer dễ đánh giá độ vững của toàn bộ chuỗi kết quả?

### 12.3. Việc chỉ có 2/3 agent đạt ngưỡng xếp hạng ở Study 2 (P2, phụ lục) có cần giải thích thêm không?

Vì Claude chỉ đạt |Â|=1 (dưới n_min=3), phép kiểm định lựa chọn xác nhận không được đánh giá — bài xử lý đúng theo quy tắc đã khoá trước, nhưng đây có thể là điểm reviewer sẽ hỏi ("tại sao không tăng N cho Claude để đủ ngưỡng?"). Em xin ý kiến anh về cách trả lời câu hỏi này nếu gặp phải — hiện bài chỉ nói "chúng tôi không chạy thêm N sau khi thấy kết quả", có cần bổ sung thêm lý do kỹ thuật (ví dụ Claude tốn chi phí/hay bị lỗi thực thi hơn) không?

---

## Phần 13 — Đề xuất bước tiếp theo

- **Việc 1 — dọn kỹ thuật trước khi nộp** (không cần ý kiến anh, em tự làm): đồng bộ git giữa local và remote, sửa số phiên bản trong README, rà lại một lượt cuối bảng số liệu giữa `main.tex` và `EVIDENCE_MAP.md`/`CLAIM_LEDGER.md` để chắc chắn không có con số nào lệch.
- **Việc 2 — hoàn thiện Path UV (nếu anh đồng ý ở mục 12.1):** hoàn thành bước kiểm chứng con người (U2) trên mẫu đã khoá trước (seed 20260913), theo đúng quy trình hai giai đoạn đã thiết kế (Stage 1 mù, Stage 2 có gallery kiểm tra dư thừa với mồi nhử chống rò rỉ).
- **Việc 3 — rà lại một lượt cuối trước khi nộp abstract (hạn 1/10):** đọc lại toàn bộ `supplementary.tex` với cùng mức độ kỹ càng đã làm với `main.tex`, để chắc chắn phụ lục cũng không có overclaim nào lọt lưới.
- **Việc 4 — chuẩn bị các câu trả lời dự kiến cho reviewer** dựa trên 3 điểm ở Phần 12, đặc biệt là câu hỏi "vì sao không mở rộng N cho Claude" và "vì sao không transport M1a sang corpus khác" — cả hai đều nên có một câu trả lời ngắn, trung thực, đã chuẩn bị sẵn.

**Trên đây là toàn bộ những gì em đã tìm hiểu và tổng hợp lại về bài báo. Em xin phép dừng ở đây để nghe ý kiến của anh, đặc biệt ở ba điểm nêu tại Phần 12.**
