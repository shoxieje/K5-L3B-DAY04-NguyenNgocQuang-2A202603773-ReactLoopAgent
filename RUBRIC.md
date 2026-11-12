# Rubric

## Điểm của eval: 0–100

Mỗi case được chấm bằng LLM judge theo bốn tiêu chí: **factuality 40**, **completeness 25**, **evidence 20** và **boundaries 15**. Chương trình cộng bốn điểm, sau đó áp trần nếu vi phạm kiểm tra code của case (ví dụ thiếu tool bắt buộc hoặc lặp lại injection marker). Xem `grade.dimensions`, `grade.reason` và `grade.mechanical` trong kết quả.

Điểm tổng là trung bình cộng điểm **tất cả** case. Nếu có case `unscored` do lỗi agent/provider/judge chưa phân biệt được, điểm tổng là `null`; `partial_mean_0_100` chỉ mang tính tham khảo. `max_steps` được tính 0 vì run không hoàn thành. Chạy một case bằng `--case H1` chỉ tạo điểm của case đó, không phải điểm cả bộ.

LLM judge là một phép đánh giá xấp xỉ, có thể nhầm hoặc thiên lệch; mặc định judge dùng cùng model với agent. Hãy đọc `expected`, trace và câu trả lời để kiểm tra lại, nhất là case điểm thấp hoặc cao bất thường. Một lần chạy không chứng minh độ ổn định.

## Chấm bài chính: 85 điểm

**Bài cá nhân**, chấm trên repo của từng học viên.

### Phần bắt buộc

| Nội dung | Điểm | Tiêu chí | Bằng chứng | Điều kiện mất điểm |
|---|---:|---|---|---|
| Agent loop | 30 | Gọi model và tool; lưu assistant message, trả đúng tool-call IDs; xử lý nhiều calls và dừng đúng. | `agent.py`, unit tests | Dùng framework; thiếu `tool_call_id`; bỏ sót tool call |
| Robustness và trace | 15 | `max_steps`, invalid JSON, tool error, model dừng bất thường; trace đủ để debug. | `agent.py`, trace trong file eval | Crash khi tool lỗi; báo `completed` khi output bị cắt; trace thiếu `event` |
| Eval và phân tích | 20 | Chạy hai lần, đọc case và trace, xác định lỗi, giải thích bằng evidence và nêu giới hạn của điểm judge. | `eval_before.json`, `eval_after.json`, `NOTES.md` | Điểm tổng `null`; không dẫn trace; hai lần chạy khác cấu hình |
| Cải tiến và trình bày | 20 | Có cải tiến phù hợp, validation nguồn, tests, so sánh kết quả và giải thích lỗi còn lại. | `agent.py`, `NOTES.md`, buổi demo | Sửa dataset, fixtures hay grading để case pass; không có so sánh trước sau |

### Trừ điểm chung

- Nộp muộn: bị trừ điểm theo [RULES.md](RULES.md).
- Sai tên repo hoặc nộp sai link: bị trừ điểm.
- Để lộ API key trong repo: bị trừ điểm, và phải thu hồi key ngay.

Điểm eval và điểm bài lab là **hai thang đo khác nhau**; không tự động dùng điểm eval thay cho điểm lab.

## Bonus tùy chọn: tối đa 15 điểm

Bộ bonus gồm 10 case, chấm riêng theo cùng thang 0–100 và quy đổi `điểm bonus = điểm bộ bonus × 0,15`. Chỉ quy đổi khi cả 10 case đã được chấm; nếu có case lỗi hoặc chỉ chạy một case thì chưa có điểm bonus tổng. Giảng viên đối chiếu trace, nhất là retry 429, lỗi định dạng, pagination và sources; điểm judge chỉ là tham khảo.

Bài chính tối đa 85 điểm, bonus cộng thêm tối đa 15 điểm; tổng tối đa **100 điểm**. Bonus không thay thế các yêu cầu của bài chính.
