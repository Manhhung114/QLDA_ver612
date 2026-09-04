# Deploy Railway V6.19

1. Railway → service QLDA → Deployments.
2. Redeploy commit V6.19.
3. Kiểm tra build log: Docker dùng `python:3.12-slim`, cài `requirements.txt`, không cài `build-essential`.
4. Mở app và xác nhận `Workflow engine: V6.19`.
5. Thử Refresh/F5: không bị thoát đăng nhập khi token còn hạn.
6. Kiểm tra một hồ sơ phê duyệt online để xác nhận workflow RFA/RFI/Shopdrawing/Hoàn công vẫn hoạt động.

Không cần deploy lại Google Apps Script cho thay đổi tinh gọn V6.19.
