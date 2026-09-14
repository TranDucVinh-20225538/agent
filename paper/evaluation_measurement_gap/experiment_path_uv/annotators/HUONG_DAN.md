# Hướng dẫn gán nhãn (Stage 1)

Cảm ơn bạn đã giúp. Việc này **không** cần biết AI hay paper. Mỗi dòng = **một việc cần làm** + **một ảnh**.

## Câu hỏi

Giả sử đây là **ảnh duy nhất** bạn được xem. Ảnh này có đủ để một người chấm bài quyết định agent **đã làm xong việc đó hay chưa**?

Chọn **đúng một** ô `isolation`:

| Nhãn | Khi nào |
|---|---|
| `DECISIVE` | Có. Ảnh cho thấy trạng thái/kết quả quyết định (xác nhận xong, món cần tìm hiện rõ, bộ lọc đã bật, form đã gửi, lỗi chặn việc…). Thiếu ảnh này thì không biết xong chưa. |
| `NOT_DECISIVE` | Không. Đang load, menu, click giữa đường, trang không liên quan, hoặc không thấy kết quả việc. |
| `UNCLEAR` | Ảnh vỡ / mờ, hoặc mô tả việc không nói rõ cái gì mới tính là xong. |

Không cần đoán agent “thật ra” đúng hay sai. Không cần nghĩ ảnh “quan trọng với máy.”

## Làm sao (nhanh: UI local)

Trong thư mục `experiment_path_uv`:

```
python3 annotate_ui.py
```

Mở http://127.0.0.1:8765 → nhập tên → chọn **Pilot** trước → Bắt đầu.

- Ảnh lớn bên trái. Việc **tiếng Việt** + English bên phải.
- Bấm 1 trong 3 nút, hoặc phím `1` / `2` / `3`. Backspace = câu trước.
- Mỗi lần bấm ghi ngay vào `annotators/labels_TÊN_pilot.csv` (hoặc `_all.csv`). Đóng tab rồi mở lại sẽ tiếp chỗ dở.

Làm **một mình**. Đừng hỏi người khác hay người nhờ bạn “câu này chọn gì.” Gửi lại file `labels_...csv`.

(Nếu không mở được UI: điền tay `stage1_pilot.csv` cột `isolation` như trước.)

## Không làm

Không dùng ChatGPT/Claude để chọn nhãn. Không tìm xem task đó trên mạng “đáp án đúng.” Không sửa cột `task`.
