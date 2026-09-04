# Deploy V6.21 lên Railway

1. Railway → Deployments → Redeploy branch `main`.
2. Giữ persistent volume và `QLDA_DB_PATH=/var/data/qlda_cloud.db`.
3. Không cần cập nhật Google Apps Script cho thay đổi V6.21.
4. Sau deploy kiểm tra giao diện hiển thị `Workflow engine: V6.21`.
5. Menu chính đổi sang bộ chọn `📌 Chức năng`; chỉ module được chọn mới được render.
6. Trong Hồ sơ/Bản vẽ, chỉ sheet đang chọn được tải dữ liệu.
7. Thử RFA/RFI/Shopdrawing/Hoàn công: lọc file và nhập ý kiến phê duyệt phải phản hồi nhanh hơn, còn khi bấm Phê duyệt/Yêu cầu chỉnh sửa hệ thống vẫn full rerun để đồng bộ trạng thái.
8. Refresh/F5 vẫn phải giữ phiên đăng nhập như V6.18+.
