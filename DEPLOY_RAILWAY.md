# Deploy V6.20 lên Railway

1. Railway → Deployments → Redeploy branch `main`.
2. Giữ persistent volume và `QLDA_DB_PATH=/var/data/qlda_cloud.db`.
3. Không cần cập nhật lại Google Apps Script cho thay đổi hiệu năng này.
4. Sau deploy kiểm tra giao diện hiển thị `Workflow engine: V6.20`.
5. Thử: đăng nhập → mở RFA/RFI/Shopdrawing/Hoàn công → chuyển qua lại sheet → Refresh; phiên đăng nhập vẫn phải được giữ.
6. Khi vừa tải file ở tab Apps Script, có thể bấm `Làm mới file / File DB` để bỏ cache 3–5 giây ngay lập tức.
