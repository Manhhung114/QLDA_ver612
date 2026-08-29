# Deploy QLDA V6.14 trên Railway

1. Đảm bảo Railway đang kết nối repo `Manhhung114/QLDA_ver612`, branch `main`.
2. Railway > Deployments > Redeploy (hoặc chờ deploy tự động từ commit mới).
3. Không xóa SQLite DB / volume.
4. Không cần cập nhật Google Apps Script cho bản sửa V6.14 này.
5. Sau deploy, kiểm tra màn hình Phê duyệt online phải hiển thị `Workflow engine: V6.14`.

## Kiểm tra nghiệp vụ
1. Cấp duyệt chọn `Yêu cầu chỉnh sửa`.
2. Nhà thầu mở hồ sơ, tải file mới, bấm `Lưu hồ sơ` / `Lưu bản vẽ`.
3. Danh sách phải đổi ngay sang `Trình lại - Đang duyệt - <cấp đã trả>`.
4. `Lần chỉnh sửa` tăng lên 1 (hoặc tăng thêm 1 ở vòng tiếp theo).
5. Tài khoản đúng cấp duyệt tick hồ sơ > `Mở / xử lý hồ sơ` sẽ thấy nút `Phê duyệt` và `Yêu cầu chỉnh sửa`.
