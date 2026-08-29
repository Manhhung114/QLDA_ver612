# QLDA Xây dựng V6.12 — Source Manifest

Bản lưu GitHub đầy đủ cho Railway, branch `main`.

## Entry point

- `streamlit_app.py`: loader của ứng dụng V6.12.
- Source Streamlit đầy đủ được lưu nguyên vẹn dưới dạng gzip + base64 tại `v612_source/streamlit_app_bundle/bundle_01.b64` đến `bundle_12.b64`.
- Loader yêu cầu đủ đúng 12 phần, ghép lại, giải nén và chạy source V6.12.
- SHA-256 source `streamlit_app.py` gốc sau giải nén: `8e1f5a7deb9d227c219f2bb7222f0b08f21c5de36fa41c59534bbe8ba581d24c`.
- Kích thước source gốc: `265605` bytes.

## Runtime modules

- `cloud_db.py`
- `drive_gateway.py`
- `ai_service.py`
- `legal_documents.py`
- `mpp_cloud_reader.py`
- `settings_store.py`

## Railway / Docker

- `Dockerfile`
- `requirements.txt`
- `.dockerignore`
- `.streamlit/config.toml`
- `VERSION.txt` = `6.12`

Dockerfile khởi chạy:

```text
streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=${PORT:-10000} --server.headless=true --browser.gatherUsageStats=false
```

## Google Drive Gateway

- `google_drive_appscript/Code.gs`
- `google_drive_appscript/appsscript.json`

## Kiểm tra khi lưu

- 12/12 bundle source đã được đối chiếu Git blob SHA với file V6.12 cục bộ.
- Source ghép lại giống byte-for-byte với `streamlit_app.py` V6.12 gốc.
- Python compile của source ghép lại: OK.
