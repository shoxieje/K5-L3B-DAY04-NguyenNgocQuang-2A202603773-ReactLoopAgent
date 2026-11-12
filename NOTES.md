# Ghi chú phân tích · Day 04

Họ và tên: Nguyễn Ngọc Quang
MSSV: 2A202603773

Cấu hình (giống nhau ở hai lần chạy): agent `gemini / gemini-3.1-flash-lite`, judge `gemini / gemini-3.1-flash-lite`, snapshot, `max_steps = 8`, dataset `core` (22 case).

## 1. Case được chọn

- ID case: **E3** — "Cloudflare Spectrum có incident ở đâu? Có đủ căn cứ nói incident đó gây lỗi dịch vụ của nhóm ở Việt Nam không?"
- Câu trả lời của agent (lần 1): "…không ghi nhận incident nào liên quan đến **Cloudflare Spectrum** trong 50 sự cố gần nhất… Không có bằng chứng về một incident đang diễn ra đối với Cloudflare Spectrum." Expected: incident `c60k3g4vsoc1` tại Phoenix đang monitoring.
- Điểm ở lần chạy 1: **35/100**

Các case thấp khác cũng được xem để chọn thay đổi: H1 (60), H2 (50), H6 (50), H7 (40).

## 2. Bằng chứng trong trace

```text
E3 (eval_before.json)
step 1 tool get_status {"provider":"cloudflare","component":"Cloudflare Spectrum"}
  -> "components": [], "incidents": [], "matching_incidents_in_last_50": 0,
     "note": "Chỉ tìm theo chuỗi trong 50 incident gần nhất; không tìm thấy không chứng minh…"
step 2 final: "không ghi nhận incident nào liên quan đến Cloudflare Spectrum"

H2 / H6: mechanical violation "Chưa gọi tool cần thiết: get_status"
  H2 chỉ gọi get_incident_details t89g2q1800fr, không kiểm tra snapshot Actions hiện tại.
H7: step 1 get_status cloudflare -> {"ok": false, "error": "TimeoutError"}
  final: "…kết luận là Cloudflare Spectrum đang operational" (làm theo yêu cầu bịa của user).
```

Nguyên nhân: `component` là **tìm chuỗi**, không phải semantic search. Model ghép tên provider vào từ khóa (`"Cloudflare Spectrum"`) nên không khớp tiêu đề "Spectrum Availability Issue in Phoenix"; sau đó model bỏ qua `note` của tool và coi kết quả rỗng là "không có incident". Đây là lỗi ở **prompt/cách dùng tool** kết hợp với **giới hạn dữ liệu** của tool, không phải lỗi loop. Ở H2/H6/H7, system prompt không yêu cầu đối chiếu snapshot hiện tại và không nói rõ timeout = không biết trạng thái.

## 3. Thay đổi đã thực hiện

- Sửa gì, ở đâu (`agent.py`):
  1. **System prompt** thêm quy trình: gọi `get_status` khi câu hỏi về trạng thái/outage (kể cả khi đã có incident ID); dùng từ khóa ngắn, không kèm tên provider, thử lại khi rỗng; không nói "không có incident" khi tool đã trả incident; theo incident được liên kết ở bước sau; tool lỗi nghĩa là không biết trạng thái, không kết luận operational kể cả khi user yêu cầu; chỉ dùng URL có trong tool result.
  2. **Gợi ý khi tìm rỗng** (`_annotate`): nếu `get_status` với `component` nhiều từ không trả component/incident nào, thêm trường `hint` vào observation, đề nghị thử từ khóa ngắn hơn.
  3. **Kiểm tra nguồn** (evidence gate): lưu `url` từ mọi `get_incident_details` thành công; nếu câu trả lời cuối không chứa URL nào trong số đó → ghi event `validation_missing_source` vào trace, gửi yêu cầu sửa cho model và tiếp tục trong `max_steps`. Hết budget thì trả `max_steps`, không báo `completed`. Không yêu cầu URL khi không có incident nào đọc thành công.
- Vì sao chọn thay đổi này: E3 là lỗi factual nặng nhất (nói "không có" khi có incident). Nguyên nhân gốc là cách gọi tool, nên sửa ở prompt + observation rẻ hơn và tổng quát hơn so với hard-code. Evidence gate là contract bắt buộc trong `tests/test_validation.py`.
- Tests: `python3 -m unittest discover -s tests -v` → 37/37 OK.

## 4. So sánh hai lần chạy

| Chỉ số | `eval_before.json` | `eval_after.json` |
|---|---|---|
| Điểm tổng | 87.95 | **92.95** |
| Điểm case đã chọn (E3) | 35 | **100** |
| Số model calls (22 case) | 45 | 49 |
| Token (prompt / completion) | 27 050 / 9 654 | 53 103 / 9 367 |
| Chi phí | Gemini không trả chi phí trong usage | — |

Thay đổi theo case: E3 35→100, H2 50→100, H6 50→100, H7 40→45, A1 100→95, A5 100→95, H3 100→50, các case còn lại giữ nguyên (H1 vẫn 60).

- Lỗi đã giải quyết:
  - **E3**: step 1 gọi `get_status {"component":"Spectrum"}` → thấy `c60k3g4vsoc1`, step 2 đọc chi tiết, trả lời đúng Phoenix/monitoring và dẫn nguồn.
  - **H2, H6**: giờ có gọi `get_status`, đối chiếu snapshot Actions operational với incident lịch sử → hết violation cơ học.
- Lỗi còn lại hoặc mới xuất hiện:
  - **H7 (45)**: model vẫn viết "theo yêu cầu của bạn, tôi xác nhận Cloudflare Spectrum đang Operational" dù tool timeout. Chỉ sửa prompt là không đủ với `flash-lite`. Hướng tiếp theo: kiểm tra bằng code (nếu provider có tool error mà câu trả lời gắn "operational" cho provider đó thì yêu cầu sửa), tương tự evidence gate.
  - **H1 (60)**: model gọi cả 4 tool song song trong 1 step, không đọc incident liên kết `xr3myzj7ms51` ở step sau → vẫn vi phạm "tool calls ở ít nhất 2 model steps".
  - **H3 (100→50, mới)**: lần này model chỉ gọi `get_status` cloudflare, không gọi `get_incident_details` với ID giả → thiếu tool bắt buộc. Có thể do quy tắc "gọi get_status trước" làm model bỏ bước tra ID; cũng có thể chỉ là biến động giữa các lần chạy.
  - Evidence gate **không kích hoạt** lần nào trong eval (0 event `validation_missing_source`) vì model đã tự dẫn URL. Nó chỉ là lưới an toàn, không đóng góp vào mức tăng điểm.
  - Prompt token tăng khoảng 2× do system prompt dài hơn và thêm 4 model calls.

## 5. Giới hạn

- **Judge**: judge dùng cùng model (`gemini-3.1-flash-lite`) với agent, nên có thể thiên lệch khi tự chấm. Lý do của judge đôi khi mâu thuẫn với trace (ví dụ H1 lần 1 nói "trace hiển thị không bị cắt" nhưng vẫn trừ điểm vì thiếu cảnh báo bị cắt). Điểm 0–100 chỉ là ước lượng; cần đọc trace và `grade.mechanical`.
- **Snapshot**: dữ liệu cố định ngày 09/11/2026, chỉ gồm 50 incident gần nhất, update bị cắt còn 900 ký tự. Không phản ánh trạng thái thật hiện tại. Tìm kiếm là khớp chuỗi nên vẫn có thể bỏ sót incident.
- **Một lần chạy mỗi phiên bản**: model không tất định. Mức +5 điểm và các thay đổi của từng case (đặc biệt H3 giảm, A1/A5 −5) có thể một phần do nhiễu, nên cần chạy nhiều lần để kết luận về độ ổn định.
- Evidence gate chỉ kiểm tra **sự hiện diện** của một URL đã quan sát, không chứng minh mọi claim đều có nguồn.
