# QLDA V6.18 - Persistent Refresh Login

## Sửa lỗi
V6.17 lưu token đăng nhập chỉ trong `st.session_state`. F5/Refresh có thể tạo Streamlit session mới, làm mất token phía app và quay về màn hình đăng nhập mặc dù token Apps Script vẫn còn hạn.

## Cơ chế mới
- Sau đăng nhập, token HMAC do Apps Script cấp được lưu thêm trong cookie trình duyệt `qlda_auth_session_v618`.
- Cookie tối đa 12 giờ, tương ứng TTL token hiện tại của Apps Script.
- Sau F5/Refresh, app đọc cookie và phục hồi `qlda_drive_session_token`.
- App luôn gọi `me()` sau phục hồi, nên tài khoản bị khóa/xóa, quyền thay đổi, token sai chữ ký hoặc hết hạn vẫn bị từ chối.
- Nút Đăng xuất xóa cả session Streamlit và cookie.
- Không lưu mật khẩu trong cookie hoặc trình duyệt.

Không cần cập nhật Code.gs nếu V6.17 Gateway hiện đang hoạt động.
