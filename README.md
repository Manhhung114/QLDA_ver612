# QLDA Xây dựng V6.21 WebOpt

Bản hiện tại đã chuyển lại để chạy trực tiếp trên **Streamlit Community Cloud**, giữ nguyên nghiệp vụ V6.21 và các tối ưu WebOpt.

## Deploy chính
- Repository: `Manhhung114/QLDA_ver612`
- Branch: `main`
- Main file: `streamlit_app.py`
- Python: **3.12**

`streamlit_app.py` hiện giải nén và compile source V6.21 WebOpt trực tiếp trong bộ nhớ. Vì vậy Community Cloud không cần Docker build stage, Railway volume hay thư mục `dist/` ghi lúc chạy.

Streamlit Community Cloud tự dùng:
- `requirements.txt` cho Python dependencies;
- `packages.txt` cho `default-jre-headless` phục vụ MPXJ/JPype;
- `.streamlit/config.toml` cho cấu hình giao diện/server.

## Tính năng/tối ưu vẫn giữ
- lazy navigation + `st.fragment`, chỉ tải module/sheet đang dùng;
- lazy import Plotly và Văn bản; Gantt tắt mặc định;
- SQLite WAL/index/cache + batch workflow query;
- HTTP connection pool + cache ngắn hạn Google Apps Script/Drive;
- phân trang bảng lớn và chỉ tạo Excel khi người dùng yêu cầu;
- persistent login qua Refresh/F5;
- AI Gemini/OpenAI streaming và typewriter stream;
- workflow Nhà thầu → Ban điều hành → TVGS → Ban QLDA;
- tương thích dữ liệu/workflow legacy.

## Secrets
Khi tạo app trên Streamlit Community Cloud, vào **Advanced settings → Secrets** và nhập lại các khóa hiện đang dùng, đặc biệt `QLDA_DRIVE_WEBAPP_URL`, `QLDA_DRIVE_API_TOKEN`, `GEMINI_API_KEY` hoặc `OPENAI_API_KEY`.

Xem hướng dẫn chi tiết tại `DEPLOY_STREAMLIT_COMMUNITY_CLOUD.md`.

> Lưu ý: Streamlit Community Cloud không có persistent disk như Railway. SQLite cục bộ có thể mất khi app reboot/redeploy; với dữ liệu nghiệp vụ cần lưu lâu dài nên duy trì backup/restore hoặc chuyển database sang kho lưu trữ bền vững.

`Dockerfile` và tài liệu Railway chỉ còn để tham chiếu triển khai cũ; Community Cloud không cần dùng chúng.
