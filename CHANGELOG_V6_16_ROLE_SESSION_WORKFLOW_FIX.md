# QLDA V6.16 - Role Session & Workflow Fix

Sửa lỗi hồ sơ đã bị trả về Nhà thầu, Nhà thầu tải file mới nhưng giao diện vẫn rơi vào nhánh `Tải file lên lưu` và không chạy `Lưu hồ sơ -> Trình lại` do session chưa nhận đúng `approval_role`.

- Trang RFA/RFI/Shopdrawing/Hoàn công luôn refresh identity từ Apps Script khi mở.
- Nếu workflow đang `CONTRACTOR` và email đăng nhập đúng `submitted_by`, người dùng được coi là Nhà thầu hợp lệ cho chính hồ sơ đó, kể cả session role cũ/trống.
- Hồ sơ trả về hiển thị đúng form chỉnh sửa + đính kèm + nút Lưu; không rơi sang nhánh upload lưu trữ chung.
- Người duyệt được thấy nút `Phê duyệt / Yêu cầu chỉnh sửa` nếu role đúng bước hoặc email đúng người được gán ở bước duyệt.
- Giữ cơ chế DB V6.15: Save của hồ sơ trả về cưỡng bức resubmit đúng cấp trong cùng transaction.

Áp dụng: RFA, RFI, SHOPDRAWING và AS_BUILT/Bản vẽ hoàn công.
