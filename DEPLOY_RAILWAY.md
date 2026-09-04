# Deploy V6.21 WebOpt lên Railway

1. Railway → service QLDA → Deployments → Redeploy branch `main`.
2. Giữ Volume mount tại `/var/data` và biến `QLDA_DB_PATH=/var/data/qlda_cloud.db`.
3. Không cần thay Google Apps Script / `Code.gs`.
4. Trong build log phải có dòng `V6.21 WebOpt build OK`.
5. Sau deploy, RFA/RFI/Shopdrawing/Hoàn công phải hiện `Workflow engine: V6.21 WebOpt`.
6. F5/Refresh phải giữ đăng nhập.
7. Mở Tiến độ: Gantt chỉ được tải khi bật `Hiển thị biểu đồ Gantt`.
8. Sau upload file, cache file tối đa khoảng 5 giây; bấm `Làm mới file / File DB` để đồng bộ ngay.

## Cấu hình Railway khuyến nghị
- Dùng 1 replica khi còn SQLite trên persistent volume.
- Không chạy nhiều replica cùng ghi vào một file SQLite.
- Không đổi hoặc xóa persistent volume khi Redeploy.
- Nếu số người dùng đồng thời tăng mạnh, chuyển database sang PostgreSQL trước khi scale ngang.

V6.21 WebOpt dùng multi-stage Docker: build stage giải nén và compile source cuối; runtime image chỉ chứa app đã sinh sẵn cùng các module cần thiết, nên các Streamlit rerun không phải xử lý bundle/patch lịch sử.
