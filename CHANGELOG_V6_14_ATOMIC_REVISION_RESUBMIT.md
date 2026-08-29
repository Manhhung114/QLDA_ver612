# QLDA V6.14 - Atomic Revision Resubmit

## Lỗi được sửa
Hồ sơ đã bị trả về Nhà thầu, Nhà thầu tải file mới và bấm Lưu nhưng workflow vẫn giữ trạng thái `CONTRACTOR` / `Chờ Nhà thầu chỉnh sửa`, làm cấp duyệt không thấy nút Phê duyệt.

## Nguyên nhân
Các bản trước dựa một phần vào UI/rerun và so sánh `updated_at` để phục hồi lần trình lại. Timestamp SQLite chỉ tới giây nên có trường hợp lưu và trả hồ sơ cùng thời điểm, hoặc UI bị ngắt giữa Save và resubmit.

## Cơ chế V6.14
- Khi cập nhật một hồ sơ/bản vẽ đang có workflow ở `current_stage=CONTRACTOR`, `save_document()` / `save_drawing()` thực hiện resubmit ngay trong CÙNG transaction SQLite.
- Chỉ hành động Lưu mới resubmit; upload file riêng không tự gửi hồ sơ.
- Workflow quay chính xác về `return_stage` đã trả hồ sơ.
- Tăng `revision_no` ngay khi Lưu.
- Mở lại bước duyệt với trạng thái `Đang chờ duyệt`.
- Giữ lịch sử các bước đã duyệt trước đó.

## Áp dụng
- RFA
- RFI
- SHOPDRAWING
- AS_BUILT / Bản vẽ hoàn công

## Kết quả kiểm thử
62/62 test liên quan workflow đạt, gồm cả trả hồ sơ tại Ban điều hành, TVGS và Ban QLDA.
