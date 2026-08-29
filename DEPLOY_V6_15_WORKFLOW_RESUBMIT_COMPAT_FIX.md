# Deploy V6.15

1. Đẩy toàn bộ source V6.15 lên repository Railway đang sử dụng.
2. Kiểm tra `requirements.txt`, `Dockerfile`, `streamlit_app.py`, `v615_runtime_patch.py` và `VERSION.txt` cùng nằm trong root.
3. Railway > Deployments > Redeploy.
4. Sau deploy, giao diện phải hiển thị `Workflow engine: V6.15`.
5. Không cần xóa SQLite DB và không cần cập nhật Apps Script chỉ cho bản sửa workflow này.

Với hồ sơ đã kẹt từ phiên bản cũ: Nhà thầu mở hồ sơ và bấm Lưu lại một lần; workflow sẽ trình lại đúng cấp đã trả.
