# CHANGELOG

## V6.20 — Runtime Fast Path
- Bundle Streamlit chỉ decode/gzip/patch/compile **một lần cho mỗi Railway process**; các `st.rerun()` sau tái sử dụng code object đã compile.
- Drive Gateway dùng `requests.Session` + HTTP connection pool theo phiên người dùng.
- Cache đọc ngắn hạn: danh sách file 3 giây, số lượng file 5 giây, danh sách người duyệt 30 giây, thông tin root 60 giây.
- Nút `Làm mới file / File DB` xóa cache file ngay lập tức.
- Bổ sung index SQLite cho tasks, documents, drawings, attachments và approval workflow.
- Giữ nguyên RBAC, persistent login và toàn bộ logic phê duyệt online V6.17–V6.19.

## V6.19 — Lean Railway
- Dọn build context và tài liệu cũ khỏi Railway image.
