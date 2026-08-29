# Deploy V6.13 - Revision Resubmit / Reviewer Button Fix

## Railway / GitHub
Repo: `Manhhung114/QLDA_ver612`
Branch: `main`

1. Railway > Deployments.
2. Redeploy commit mới nhất.
3. Sau khi chạy, vào RFA/RFI/Shopdrawing/Hoàn công và kiểm tra dòng `Approval UI / Workflow engine: V6.13`.

## Cách kiểm tra lỗi đã sửa
1. Ban điều hành/TVGS/Ban QLDA chọn `Yêu cầu chỉnh sửa`.
2. Nhà thầu mở hồ sơ, tải file mới và bấm `Lưu hồ sơ`/`Lưu bản vẽ`.
3. Hồ sơ phải chuyển khỏi `Chờ Nhà thầu chỉnh sửa` sang `Trình lại - Đang duyệt - <cấp đã trả>`.
4. Đăng nhập đúng cấp duyệt, chọn hồ sơ > `Mở / xử lý hồ sơ`.
5. Phải thấy hai nút `✅ Phê duyệt` và `↩️ Yêu cầu chỉnh sửa`.

V6.13 có fail-safe: nếu lần Lưu trước đã cập nhật bản ghi nhưng workflow bị kẹt ở CONTRACTOR, khi người duyệt mở hồ sơ hệ thống tự phục hồi về đúng `return_stage`.
