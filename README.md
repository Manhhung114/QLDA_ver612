# QLDA Xây dựng V6.20

Bản Runtime Fast Path dành cho Railway.

Tối ưu chính:
- mã Streamlit bundle chỉ giải nén/patch/compile một lần mỗi Railway process;
- tái sử dụng HTTP connection tới Google Apps Script/Drive;
- cache ngắn hạn các lệnh đọc Drive và có nút refresh cưỡng bức;
- bổ sung index SQLite cho các truy vấn hồ sơ, bản vẽ, tiến độ và workflow;
- giữ nguyên RBAC, persistent login, Google Drive và phê duyệt online.

Railway chạy bằng `Dockerfile`; SQLite nên đặt trên persistent volume với `QLDA_DB_PATH=/var/data/qlda_cloud.db`.
