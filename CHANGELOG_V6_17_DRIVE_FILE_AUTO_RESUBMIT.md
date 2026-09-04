# QLDA V6.17 - Drive file auto resubmit

Sửa lỗi hồ sơ đã bị trả về, Nhà thầu đã tải file phiên bản mới nhưng workflow vẫn giữ `Chờ Nhà thầu chỉnh sửa`.

V6.17 dùng bằng chứng file Google Drive: nếu workflow đang ở `CONTRACTOR` và có file hiện hành có `modified_time` sau thời điểm `REQUEST_REVISION`, hệ thống tự gọi `force_revision_resubmit()` và chuyển về đúng cấp đã trả. `revision_no` tăng ngay.

Áp dụng chung cho RFA, RFI, SHOPDRAWING và AS_BUILT/Hoàn công. Cơ chế chạy cả khi Nhà thầu hoặc người duyệt mở hồ sơ, nên có thể tự phục hồi các hồ sơ đang kẹt từ V6.16 trở về trước.
