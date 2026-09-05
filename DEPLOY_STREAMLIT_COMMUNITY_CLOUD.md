# Deploy QLDA V6.22 PostgreSQL Cloud lên Streamlit Community Cloud

## Cấu hình deploy
- Repository: `Manhhung114/QLDA_ver612`
- Branch: `main`
- Main file path: `streamlit_app.py`
- Python: **3.12**

Streamlit Community Cloud sẽ tự đọc:
- `requirements.txt` để cài Python package;
- `packages.txt` để cài `default-jre-headless` cho MPXJ/JPype;
- `.streamlit/config.toml` để lấy cấu hình Streamlit.

`streamlit_app.py` giải nén, finalize và compile source ứng dụng trực tiếp trong bộ nhớ, không ghi `dist/` khi chạy.

## Secrets
Trong **Advanced settings → Secrets**, khai báo các khóa đang dùng trên hệ thống hiện tại.

PostgreSQL:

```toml
DATABASE_URL = "postgresql://..."
```

Google Drive Gateway:

```toml
QLDA_DRIVE_WEBAPP_URL = "https://script.google.com/macros/s/.../exec"
QLDA_DRIVE_API_TOKEN = "..."
```

Nếu dùng Gemini:

```toml
GEMINI_API_KEY = "..."
GEMINI_MODEL = "auto"
AI_WEB_SEARCH = "1"
```

Nếu dùng OpenAI thì thêm `OPENAI_API_KEY` và các cấu hình model tương ứng.

## Lưu ý database
Filesystem cục bộ của Streamlit Community Cloud không phải nơi lưu dữ liệu nghiệp vụ lâu dài. Với hệ thống hiện tại, dữ liệu cần bền vững nên lưu trong PostgreSQL; file đính kèm tiếp tục lưu trên Google Drive qua Gateway.
