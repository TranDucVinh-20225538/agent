# Lab lead — tìm 2 người + chạy U2 Stage 1

Bạn là annotator **1/3**. Cần **2 người thật** nữa. Agent không tính.

Mục tiêu: Stage 1 xong ~20/9, Stage 2 trước 28/9, abstract AAMAS 1/10.

## Tìm ai

Người đọc được tiếng Anh ngắn (cột `task`), nhìn screenshot web được. Không cần biết AI.

Nơi hỏi: labmate, bạn cùng lab CMU, người đã làm HIT/annotation. Tránh: người sẽ bảo “để mình hỏi GPT,” người bạn sẽ ngồi cạnh bàn đáp án.

Nói khi rủ (đúng 30 giây):

> Mình nhờ xem ảnh chụp lúc một chương trình tự lướt web. Mỗi dòng một ảnh + một câu việc. Hỏi ảnh đó, nếu là ảnh duy nhất, có đủ để biết việc xong chưa không. Ba lựa chọn. Làm một mình. Pilot ~300 dòng (~2 giờ). Full ~1230 dòng (~6–8 giờ). Có thể chia buổi.

Trả công: tiền / gift card / bữa ăn — nói rõ trước. 6–8 giờ không phải “nhờ 15 phút.”

**Screen 5 phút:** gửi 10 dòng đầu `stage1_pilot.csv`. Nếu họ nhãn hết `DECISIVE` hoặc hết `NOT_DECISIVE`, hoặc bảo “để GPT làm,” đổi người.

## Bạn nói / không nói

Nói: nội dung `annotators/HUONG_DAN.md`.

Không nói: discard, keep, máy cắt 73%, gold, `found`, U2-irr, A0, `u2_stage1_key.csv`, “ảnh này bị vứt.” Họ không được biết máy thích ảnh nào.

Bạn cũng **không mở key.csv lúc tự chấm.**

## Gửi họ gì

Thư mục `experiment_path_uv/annotators/` (sau khi chạy pack):

- `HUONG_DAN.md`
- `stage1_pilot.csv` rồi mới `stage1_all.csv`
- folder `png/` (file `U2S1-xxxx.png`)

Không zip `out/u2_stage1_key.csv`, `u2_sample.md`, `r_results.jsonl`.

Ba file nhãn độc lập: `stage1_pilot_A.csv`, `_B.csv`, `_C.csv` (A = bạn).

## Lịch gợi ý

| Khi | Việc |
|---|---|
| Hôm nay–15/9 | Chốt 2 người. OpenReview account (17/9). |
| 15–17/9 | Cả 3 làm **pilot** (~297 dòng). So Fleiss thô. Chỉ sửa *chữ* codebook nếu 3 người hiểu DECISIVE khác nhau — không sửa sau full. |
| 17–20/9 | Nốt `stage1_all.csv`. |
| Sau S1 | Mình (lab) dựng Stage 2 từ DECISIVE. Họ làm S2 (ít dòng hơn). |
| Trước 1/10 | Join irr. Abstract AAMAS. |

P3-H (39 dòng, folder khác) làm **sau U2 S1**, cùng 3 người, cùng 3 nhãn, **sheet khác** — đừng trộn.

## Sau khi nhận CSV

Đừng xem đáp án với họ. Đưa raw CSV cho người join (hoặc bảo Cursor join). Majority 2/3; UNCLEAR loại khỏi mẫu irr.
