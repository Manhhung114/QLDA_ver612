# QLDA V6.15 - Workflow resubmit compatibility fix

V6.15 sửa lỗi hồ sơ đã bị trả về Nhà thầu, Nhà thầu cập nhật file mới và bấm Lưu nhưng workflow vẫn giữ trạng thái `Chờ Nhà thầu chỉnh sửa`.

Điểm sửa chính:
- Tìm workflow theo `project_id + record_kind + record_id`, không phụ thuộc tuyệt đối vào `subtype`.
- Tương thích mã bước legacy/current: `SITE_MANAGEMENT`, `CONSULTANT`, `PROJECT_MANAGEMENT` và các alias TVGS/BQLDA.
- Khi Nhà thầu bấm Lưu trong trạng thái trả về, Save và Resubmit được thực hiện ngay trong cùng transaction.
- Sau Save có kiểm tra hậu điều kiện; nếu vẫn còn `CONTRACTOR`, app báo lỗi thay vì hiển thị đã lưu thành công.
- Áp dụng cho RFA, RFI, Shopdrawing và Bản vẽ hoàn công (AS_BUILT).
- Trình lại đúng cấp đã trả: Ban điều hành / TVGS / Ban QLDA.
