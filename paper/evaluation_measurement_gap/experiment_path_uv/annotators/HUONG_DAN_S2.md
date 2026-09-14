# Stage 2 — cùng 3 người (Vinh, Toàn, Hùng)

Câu hỏi **khác** Stage 1.

Bạn thấy: **một việc** + **một ảnh mục tiêu** (trái) + **một gallery** ảnh khác cùng lần làm việc (phải).

Trong gallery **có ít nhất một ảnh chứa cùng evidence quyết định** với ảnh mục tiêu không?

Cùng evidence = cùng kết quả việc (cùng số phí, cùng trang ID, cùng list đã lọc đúng…). **Không** đủ nếu chỉ cùng website / cùng trang chủ.

| Nhãn | Khi nào |
|---|---|
| `EQUIVALENT` | Có. Bỏ ảnh mục tiêu vẫn chấm được nhờ một tấm trong gallery. |
| `NOT_EQUIVALENT` | Không tấm nào trong gallery mang cùng evidence đó. Gallery trống cũng là NOT_EQUIVALENT. |
| `UNCLEAR` | Ảnh vỡ / không chắc. |

Không hỏi ảnh nào máy vứt. Làm một mình. Không GPT.

```
python3 annotate_s2.py
```

Mở http://127.0.0.1:8766 — tên `VINH-1` / `TOAN-1` / `HUNG-1`. Phím `1` / `2` / `3`. Click ảnh gallery để phóng to.

~360 dòng. File: `annotators/labels_TÊN_s2.csv`.
