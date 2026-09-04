from pathlib import Path

from v621_runtime_patch import compiled_streamlit_app, install_db_patch

# QLDA V6.21 Railway loader.
# Bundle được decode/patch/compile một lần mỗi Railway process; V6.21 bổ sung
# lazy navigation và st.fragment để giảm rerun toàn bộ ứng dụng.
_BUNDLE_DIR = Path(__file__).resolve().parent / "v612_source" / "streamlit_app_bundle"

install_db_patch()
exec(
    compiled_streamlit_app(str(_BUNDLE_DIR), str(Path(__file__).resolve())),
    globals(),
    globals(),
)
