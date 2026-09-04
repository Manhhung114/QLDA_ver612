# CHANGELOG

## V6.21 — Partial Rerun / Lazy Load
- Thay top-level `st.tabs` bằng điều hướng lazy: mỗi lần chỉ render đúng 01 module đang chọn thay vì chạy toàn bộ 11 module.
- Quản lý hồ sơ chỉ render 01 sheet đang chọn trong NCR/RFA/RFI/BBHT/NTCV/NTVL/KDVT.
- Quản lý bản vẽ chỉ render 01 sheet đang chọn trong Shopdrawing/Issued Design/Updated/As-built.
- Tách vùng File Google Drive và Phê duyệt online bằng `st.fragment`; thao tác lọc file/nhập ý kiến không còn bắt buộc rerun toàn app.
- Các thao tác thay đổi dữ liệu thật như upload, phê duyệt, yêu cầu chỉnh sửa vẫn full rerun để đồng bộ số liệu và workflow.
- Cache `/me` 15 giây để giảm gọi Apps Script khi fragment rerun nhưng vẫn nhận thay đổi quyền sớm.
- Giữ nguyên toàn bộ Runtime Fast Path V6.20, RBAC, persistent login và workflow phê duyệt online.

## V6.20 — Runtime Fast Path
- Bundle Streamlit chỉ decode/gzip/patch/compile một lần mỗi Railway process.
- Drive Gateway dùng HTTP connection pool và cache đọc ngắn hạn.
- Bổ sung index SQLite cho các truy vấn chính.

## V6.19 — Lean Railway
- Dọn build context và tài liệu cũ khỏi Railway image.
