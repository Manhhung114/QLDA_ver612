# QLDA Xây dựng V6.21 WebOpt

Bản web tối ưu cho Railway, giữ nguyên toàn bộ nghiệp vụ V6.21.

Tối ưu chính:
- Docker multi-stage tạo sẵn source WebOpt; Railway runtime chạy trực tiếp `streamlit_app.py` cuối;
- lazy navigation + `st.fragment`, chỉ tải module/sheet đang dùng;
- lazy import Plotly và Văn bản; Gantt tắt mặc định;
- SQLite WAL/index/cache + batch workflow query để giảm N+1 query;
- HTTP connection pool + cache đọc ngắn hạn Google Apps Script/Drive;
- phân trang bảng lớn và chỉ tạo Excel khi người dùng yêu cầu;
- persistent login giữ qua Refresh/F5;
- Streamlit production tắt file watcher và giới hạn thread CPU không cần thiết;
- giữ tương thích workflow Nhà thầu → Ban điều hành → TVGS → Ban QLDA và dữ liệu workflow legacy.

Railway nên dùng 1 replica khi còn SQLite trên persistent volume tại `/var/data/qlda_cloud.db`. Khi cần scale nhiều replica, nên chuyển database sang PostgreSQL trước.
