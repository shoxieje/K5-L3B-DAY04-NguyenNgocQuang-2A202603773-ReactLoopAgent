# Quy định làm bài · Day 04

## Hình thức

**Bài cá nhân.** Mỗi cá nhân tự làm và tự nộp repo riêng, đặt tên theo [SUBMISSION.md](SUBMISSION.md).

## Sử dụng AI

- Được dùng công cụ AI để hỏi khái niệm, giải thích lỗi và gợi ý.
- Mục tiêu của bài là tự viết agent loop, nên không dùng LangChain, LangGraph hay framework agent khác.
- Bạn phải giải thích được toàn bộ code mình nộp. Nếu trợ giảng hỏi mà không giải thích được, phần đó có thể không được tính điểm.
- `NOTES.md` phải dựa trên trace thật của bạn.

## Hợp tác và sao chép

- Được trao đổi ý tưởng và cùng gỡ lỗi với bạn học, không sao chép code, file eval hay `NOTES.md` của người khác.
- Không sửa `fixtures/`, `evals/cases.json`, `evals/scenarios.py`, `evals/grading.py` hay rubric để làm case pass, không sửa tay kết quả eval.

## Deadline và nộp muộn

Hạn nộp theo giờ Việt Nam (GMT+7):

- Ca 9:00–13:00 và ca 14:00–18:00: trước 23:59 cùng ngày.
- Ca 16:30–20:00: trước 12:00 trưa hôm sau.

Nếu key coach thông báo hạn khác trong vòng 48 giờ sau buổi lab thì theo thông báo đó. Nộp muộn bị trừ điểm.

## Sửa bài sau deadline

Bài được chấm theo commit cuối cùng trước hạn. Commit sau hạn được tính là nộp muộn.

## Bonus

Bonus là điểm cộng cho chất lượng bài lab, không phải điểm giơ tay, phát biểu hay pitching. Mức điểm xem ở [RUBRIC.md](RUBRIC.md).

## Bảo mật API key và dữ liệu

- Chỉ để key trong biến môi trường hoặc file `.env`. File `.env` đã nằm trong `.gitignore`, không commit, không gửi lên chat hay ảnh chụp màn hình.
- Lỡ đẩy key lên GitHub: thu hồi key ngay trên trang của provider rồi tạo key mới. Xoá file thôi là chưa đủ vì key còn trong lịch sử git.
- Eval gọi model thật cho cả agent và judge nên tốn token. Khi đang sửa lỗi, dùng `--case` để chạy một case.
- Xóa thông tin nhạy cảm khỏi trace và file eval trước khi nộp.
