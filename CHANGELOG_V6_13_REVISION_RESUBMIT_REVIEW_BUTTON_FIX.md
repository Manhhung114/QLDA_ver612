# V6.13 - Revision Resubmit / Reviewer Button Fix

- Sửa lỗi Nhà thầu đã cập nhật + Lưu hồ sơ nhưng workflow vẫn ở `CONTRACTOR`, làm Ban điều hành/TVGS/Ban QLDA không thấy nút Phê duyệt.
- Thêm fail-safe dựa trên `record.updated_at > workflow.updated_at`: chỉ khi Nhà thầu thực sự bấm Lưu sau lần bị trả mới tự trình lại đúng `return_stage`.
- Xác minh hậu điều kiện ngay sau nút Lưu/Trình lại.
- Khi người duyệt mở hồ sơ legacy bị kẹt, hệ thống tự phục hồi và rerun để hiện nút `Phê duyệt / Yêu cầu chỉnh sửa`.
- Áp dụng chung cho RFA, RFI, SHOPDRAWING và AS_BUILT.
- Giữ nguyên lịch sử duyệt và tăng `revision_no` khi resubmit thành công.

Đã kiểm tra bộ test phê duyệt V6.1 -> V6.13: 45/45 test đạt.
