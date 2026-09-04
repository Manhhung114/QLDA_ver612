# CHANGELOG

## V6.21 WebOpt — Railway Web Performance Final
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
