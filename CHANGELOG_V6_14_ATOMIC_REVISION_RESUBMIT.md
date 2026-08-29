# QLDA V6.14 - Atomic Revision Resubmit

V6.14 sửa lỗi hồ sơ đã bị trả về Nhà thầu, Nhà thầu tải file mới và bấm Lưu nhưng workflow vẫn giữ trạng thái `Chờ Nhà thầu chỉnh sửa`, làm cấp duyệt không thấy nút Phê duyệt.

Cơ chế mới: khi bản ghi đang có workflow `current_stage=CONTRACTOR`, thao tác `Lưu hồ sơ/Lưu bản vẽ` thực hiện cập nhật dữ liệu và trình lại đúng `return_stage` trong cùng transaction SQLite. Upload file riêng không tự trình lại; chỉ Save thành công mới chuyển bước. `revision_no` tăng ngay và cấp đã trả hồ sơ được mở lại với trạng thái `Đang chờ duyệt`.

Áp dụng cho RFA, RFI, SHOPDRAWING và AS_BUILT/Bản vẽ hoàn công, bao gồm trường hợp bị trả tại Ban điều hành, TVGS hoặc Ban QLDA.

Bộ kiểm thử workflow liên quan: 62/62 đạt.
