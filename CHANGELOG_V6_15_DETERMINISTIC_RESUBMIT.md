# QLDA V6.15 - Deterministic Revision Resubmit

Sửa lỗi hồ sơ đã bị trả về Nhà thầu, Nhà thầu tải file mới và bấm Lưu nhưng workflow vẫn giữ `Chờ Nhà thầu chỉnh sửa`.

Nguyên nhân được xác nhận trên source Railway thực tế:
- `cloud_db.py` nền vẫn là V6.12 và workflow dùng mã bước `CONSULTANT` / `PROJECT_MANAGEMENT`.
- Một số bản vá trước giả định mã `TVGS` / `BQLDA`.
- Việc tìm workflow khi Save còn phụ thuộc `subtype` khớp tuyệt đối, gây lỗi với dữ liệu legacy khác kiểu chữ/mã.

V6.15:
- Save tìm workflow theo `project_id + record_kind + record_id`, không phụ thuộc subtype legacy.
- Chuẩn hóa các alias Ban điều hành / TVGS / Ban QLDA về mã bước thật của V6.12.
- Nếu `return_stage` cũ/hỏng, suy ra cấp trả từ `approval_history`, sau đó từ `overall_status`.
- Save hồ sơ/bản vẽ và Resubmit xảy ra trong cùng transaction.
- Sau Save có kiểm tra hậu điều kiện; nếu workflow vẫn CONTRACTOR thì chặn và báo lỗi, không báo lưu thành công giả.
- Áp dụng RFA, RFI, SHOPDRAWING và AS_BUILT.
- Đã test 12 tình huống: 4 nhóm hồ sơ x 3 cấp trả (Ban điều hành, TVGS, Ban QLDA), kể cả subtype legacy và return_stage hỏng. Tất cả đạt.
