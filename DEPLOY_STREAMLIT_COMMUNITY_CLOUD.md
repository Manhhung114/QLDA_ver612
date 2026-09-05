# Deploy QLDA V6.21 WebOpt lên Streamlit Community Cloud

## Cấu hình deploy
- Repository: `Manhhung114/QLDA_ver612`
- Branch: `main`
- Main file path: `streamlit_app.py`
- Python: **3.12**

Streamlit Community Cloud sẽ tự đọc:
- `requirements.txt` để cài Python package;
- `packages.txt` để cài `default-jre-headless` cho MPXJ/JPype;
- `.streamlit/config.toml` để lấy cấu hình Streamlit.

Không cần Dockerfile, Railway volume hoặc lệnh start riêng. `streamlit_app.py` hiện giải nén và compile V6.21 WebOpt trực tiếp trong bộ nhớ, không ghi `dist/` khi chạy.

## Secrets
Trong **Advanced settings → Secrets**, khai báo các khóa đang dùng trên hệ thống hiện tại. Tối thiểu với Google Drive Gateway:

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
Streamlit Community Cloud không cung cấp persistent disk kiểu Railway. SQLite cục bộ có thể mất khi app reboot/redeploy. Vì vậy cần duy trì cơ chế backup/restore DB hoặc chuyển database sang dịch vụ lưu trữ bền vững nếu dữ liệu nghiệp vụ phải giữ lâu dài.
