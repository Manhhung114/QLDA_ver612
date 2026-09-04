# QLDA Xây Dựng V6.19

Bản Railway tinh gọn, giữ nguyên chức năng nghiệp vụ của V6.18/V6.17.

## Runtime Railway
- `streamlit_app.py`: entrypoint Streamlit.
- `cloud_db.py`: dữ liệu SQLite + workflow phê duyệt.
- `drive_gateway.py`: Google Drive Apps Script gateway.
- `ai_service.py`: AI.
- `legal_documents.py`: văn bản pháp luật.
- `mpp_cloud_reader.py`: đọc Microsoft Project bằng MPXJ/Java.
- `settings_store.py`: cấu hình.
- `v615_runtime_patch.py` → `v619_runtime_patch.py`: lớp tương thích dữ liệu/workflow cũ.
- `v612_source/`: source bundle nền đang được loader sử dụng.

## Tối ưu V6.19
- Xóa khỏi branch hiện tại các changelog/deploy/test/cache cũ gây rối root repo; lịch sử vẫn còn trong Git history.
- Gom thay đổi vào `CHANGELOG.md` và hướng dẫn deploy vào `DEPLOY_RAILWAY.md`.
- `.dockerignore` dùng whitelist nên Railway chỉ gửi các file runtime cần thiết vào Docker build context.
- Docker bỏ `build-essential`, dùng `--prefer-binary` để giảm thời gian cài package và kích thước image.
- Giữ phiên đăng nhập qua Refresh/F5 và tự trình lại workflow khi có file cập nhật sau lần trả hồ sơ.

## Deploy
Xem `DEPLOY_RAILWAY.md`.
