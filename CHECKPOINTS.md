# Checkpoints · Day 04

**Bài cá nhân.** Có 7 checkpoint và 1 giờ nghỉ. 15 phút đầu mỗi ca dành để ổn định lớp, nội dung lab bắt đầu sau đó. Lịch dưới đây chia theo tỉ lệ timeline trong [GUIDE.md](GUIDE.md).

| Checkpoint | Nội dung | Ca 9:00–13:00 | Ca 14:00–18:00 | Ca 16:30–20:00 |
|---|---|---|---|---|
| CP1 | Setup và khám phá tools | 09:15–09:30 | 14:15–14:30 | 16:45–16:55 |
| CP2 | Bài 1: agent loop | 09:30–10:20 | 14:30–15:20 | 16:55–17:40 |
| CP3 | Bài 2: xử lý lỗi và trace | 10:20–10:45 | 15:20–15:45 | 17:40–18:00 |
| Nghỉ | Nghỉ giải lao | 10:45–10:55 | 15:45–15:55 | 18:00–18:10 |
| CP4 | Bài 3: eval lần 1 | 10:55–11:25 | 15:55–16:25 | 18:10–18:40 |
| CP5 | Bài 4: phân tích và cải tiến | 11:25–12:20 | 16:25–17:20 | 18:40–19:25 |
| CP6 | Bài 5: eval lần 2 | 12:20–12:45 | 17:20–17:45 | 19:25–19:50 |
| CP7 | Demo, chốt bài và nộp | 12:45–13:00 | 17:45–18:00 | 19:50–20:00 |

## CP1 · Setup và khám phá tools

- **Cần làm:** fork repo đề, đổi tên theo mẫu, clone về máy, đặt `PROVIDER`, `MODEL` và API key của một provider; chạy thử 2 tool trong [GUIDE.md](GUIDE.md).
- **Sản phẩm:** repo riêng đúng tên, máy đã có key chạy được.
- **Cần hiểu:** hai tool trả gì, vì sao tìm không thấy không chứng minh incident không tồn tại.
- **Tự kiểm tra:** lệnh `get_status` in ra JSON; push thử được vào repo của bạn.

## CP2 · Bài 1: agent loop

- **Cần làm:** hoàn thiện `run_agent` trong `agent.py` theo contract trong [GUIDE.md](GUIDE.md).
- **Sản phẩm:** agent gọi được tool và trả lời được một câu hỏi thật.
- **Cần hiểu:** vì sao phải giữ nguyên assistant message và trả đúng `tool_call_id` cho mọi call.
- **Tự kiểm tra:** `python3 run.py 'GitHub Actions hiện có sự cố không? Hãy kiểm tra incident gần đây.'` trả `status` là `completed`.

## CP3 · Bài 2: xử lý lỗi và trace

- **Cần làm:** thêm `max_steps`, xử lý JSON lỗi, tool lỗi, `finish == 'length'`, lỗi provider, và ghi trace đúng format.
- **Sản phẩm:** agent không crash khi gặp lỗi, trace đủ để debug.
- **Cần hiểu:** lỗi nào trả lại cho model, lỗi nào kết thúc run.
- **Tự kiểm tra:** `python3 -m unittest discover -s tests -v`; chỉ còn lại các test của phần kiểm tra nguồn ở Bài 4.

## CP4 · Bài 3: eval lần 1

- **Cần làm:** chạy `python3 evals/run_evals.py --output eval_before.json`, đọc `summary`, `grade.reason`, `grade.mechanical`, answer và trace.
- **Sản phẩm:** `eval_before.json` đủ 22 case, danh sách lỗi.
- **Cần hiểu:** điểm judge chỉ là ước lượng; `completed` chỉ nói agent dừng bình thường.
- **Tự kiểm tra:** `summary.score_0_100` khác `null`.

## CP5 · Bài 4: phân tích và cải tiến

- **Cần làm:** chọn một lỗi, ghi bằng chứng và nguyên nhân vào `NOTES.md`, implement một thay đổi và kiểm tra nguồn.
- **Sản phẩm:** `agent.py` đã cải tiến, `NOTES.md` mục 1 đến 3.
- **Cần hiểu:** lỗi nằm ở prompt, loop hay giới hạn của dữ liệu.
- **Tự kiểm tra:** `python3 -m unittest discover -s tests -v` không còn test lỗi.

## CP6 · Bài 5: eval lần 2

- **Cần làm:** chạy lại với cùng cấu hình bằng `python3 evals/run_evals.py --output eval_after.json`, so sánh điểm, lỗi và chi phí.
- **Sản phẩm:** `eval_after.json`, `NOTES.md` mục 4 và 5.
- **Cần hiểu:** một lần chạy mỗi phiên bản không chứng minh độ ổn định.
- **Tự kiểm tra:** khối `config` trong hai file eval giống nhau.

## CP7 · Demo, chốt bài và nộp

- **Cần làm:** demo một trace nhiều bước và một lỗi agent, push repo, nộp link LMS.
- **Sản phẩm:** repo đúng tên, link đã nộp trên LMS.
- **Cần hiểu:** kết quả cải tiến của bạn và giới hạn của nó.
- **Tự kiểm tra:** đi hết checklist trong [SUBMISSION.md](SUBMISSION.md).
