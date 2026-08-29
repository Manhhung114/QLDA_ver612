# Deploy V6.14 trên Railway

1. Railway dùng repo `Manhhung114/QLDA_ver612`, branch `main`.
2. Vào Deployments > Redeploy hoặc chờ Railway tự deploy commit mới.
3. Không xóa SQLite DB/volume.
4. Không cần cập nhật Google Apps Script cho V6.14.
5. Sau deploy, màn hình Phê duyệt online phải hiển thị `Workflow engine: V6.14`.

Kiểm tra: cấp duyệt yêu cầu chỉnh sửa -> Nhà thầu tải file mới -> bấm Lưu -> trạng thái phải đổi ngay thành `Trình lại - Đang duyệt - <cấp đã trả>` và Lần chỉnh sửa tăng 1. Tài khoản đúng cấp duyệt mở hồ sơ phải thấy nút `Phê duyệt` và `Yêu cầu chỉnh sửa`.
