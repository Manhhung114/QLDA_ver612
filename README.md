# QLDA Xây dựng V6.21

Bản Partial Rerun / Lazy Load dành cho Railway.

Tối ưu chính:
- chỉ render 01 module chính đang chọn thay vì thực thi toàn bộ nội dung của `st.tabs`;
- Hồ sơ và Bản vẽ chỉ tải đúng sheet đang chọn;
- File Google Drive và Phê duyệt online dùng `st.fragment` để giảm full rerun khi lọc file/nhập ý kiến;
- giữ HTTP connection pool, cache Drive ngắn hạn và SQLite index của V6.20;
- giữ nguyên RBAC, persistent login, Google Drive và workflow Nhà thầu → Ban điều hành → TVGS → Ban QLDA.

Railway chạy bằng `Dockerfile`; SQLite nên đặt trên persistent volume với `QLDA_DB_PATH=/var/data/qlda_cloud.db`.
