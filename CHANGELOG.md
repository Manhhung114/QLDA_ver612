# CHANGELOG

## V6.21 WebOpt — Railway Web Performance Final
- Trợ lý AI bổ sung **Fast Context** để giảm thời gian chờ trước token đầu tiên: câu hỏi tiến độ chỉ gửi top công việc rủi ro; RFI/NCR chỉ nạp hồ sơ liên quan; bản vẽ, chi phí, vật tư và pháp lý chỉ nạp khi câu hỏi cần.
- Lịch sử chat gửi AI giảm từ 8 xuống 4 message gần nhất để giảm input token và tăng tốc phản hồi.
- Gemini `auto` ưu tiên đường model nhanh trực tiếp (`gemini-2.5-flash-lite` → `gemini-2.5-flash`) và chỉ gọi discovery `models.list()` khi các model nhanh không dùng được.
- Streaming Gemini giảm retry mặc định xuống 2 lần với backoff ngắn hơn để tránh đứng lâu ở trạng thái “AI đang phân tích...”. Có thể override bằng `GEMINI_STREAM_RETRY_ATTEMPTS`, `GEMINI_STREAM_RETRY_BASE_SECONDS`, `GEMINI_FAST_MODEL`.
- Chat dự án luôn dùng `use_web=False`; nhãn trạng thái AI trên giao diện đổi thành `Fast Context` để không gây hiểu nhầm rằng Web Search đang làm chậm chat nội bộ.
- Trợ lý AI Chat chuyển sang streaming: OpenAI dùng Responses streaming delta, Gemini dùng `generate_content_stream`; Streamlit hiển thị dần bằng `st.write_stream()` thay vì chờ xong toàn bộ câu trả lời.
- Nếu SDK OpenAI cũ không có streaming API, giao diện vẫn phát dần theo từng cụm từ thay vì đổ cả khối một lần.
- Bỏ các chú thích/hướng dẫn tĩnh trong các sheet để giao diện gọn hơn: không còn dòng `Workflow engine...`, mô tả luồng trả hồ sơ, nhãn `Approval UI / Workflow engine`, hướng dẫn `Nhập đúng Mã...`, nhắc quay lại bấm Làm mới file và chú thích kỹ thuật V6.9.
- Vẫn giữ các thông báo nghiệp vụ cần thiết: trạng thái đang chờ duyệt, cảnh báo thiếu file, hồ sơ bị trả về, người duyệt, lịch sử và kết quả phê duyệt.
- Giữ nguyên phiên bản nghiệp vụ V6.21 và toàn bộ luồng phê duyệt online RFA/RFI/Shopdrawing/Hoàn công.
- Railway dùng multi-stage Docker: source WebOpt cuối được giải nén/kiểm tra/compile ở build stage; runtime image chạy trực tiếp `streamlit_app.py` đã sinh sẵn.
- Runtime image không còn 12 source bundle và không chạy chuỗi patch V6.16→V6.21 khi Streamlit rerun.
- Chỉ render module/sheet đang mở; `st.fragment` cho vùng file và phê duyệt online.
- Plotly và module Văn bản chỉ import khi thực sự dùng; Gantt tắt mặc định.
- Workflow được đọc theo batch để tránh N+1 query; giữ tương thích hồ sơ legacy qua V6.15 deterministic resubmit.
- SQLite: WAL, statement cache, memory temp/cache, mmap và index cho các truy vấn chính.
- Google Apps Script/Drive dùng HTTP connection pool; `/me` cache 15 giây; file list/file-count cache 5 giây; nút Làm mới file xóa cache ngay.
- Bảng lớn phân trang: hồ sơ/bản vẽ 50 dòng/trang; tiến độ 100 dòng/trang.
- Excel chỉ tạo khi người dùng bấm `Tạo Excel`, không chạy openpyxl ở mọi rerun.
- Cookie đăng nhập chỉ ghi khi token thay đổi, giảm component HTML thừa.
- Streamlit production tắt file watcher, bật fast rerun; Docker giới hạn thread BLAS/OMP để giảm CPU/RAM trên Railway.
- Build context Railway được whitelist chỉ còn các file cần cho build/runtime WebOpt.

## V6.21 — Partial Rerun / Lazy Load
- Chỉ render module và sheet đang chọn.
- Dùng `st.fragment` cho vùng file và phê duyệt online.

## V6.20 — Runtime Fast Path
- HTTP pool/cache Drive và SQLite index ban đầu.

## V6.19 — Lean Railway
- Dọn build context và tài liệu cũ.
