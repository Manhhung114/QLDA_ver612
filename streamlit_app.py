from pathlib import Path

from v620_runtime_patch import compiled_streamlit_app, install_db_patch

# QLDA V6.20 small Railway loader.
# The source bundle is decoded/patched/compiled ONCE per Railway process by
# v620_runtime_patch.compiled_streamlit_app(). Subsequent Streamlit reruns reuse
# the cached code object instead of repeating Base64 + gzip + patch + compile.
_BUNDLE_DIR = Path(__file__).resolve().parent / "v612_source" / "streamlit_app_bundle"

install_db_patch()
exec(
    compiled_streamlit_app(str(_BUNDLE_DIR), str(Path(__file__).resolve())),
    globals(),
    globals(),
)
