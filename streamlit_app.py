from pathlib import Path
import base64
import gzip

# QLDA V6.12 source loader.
# The complete Streamlit application is stored as gzip+base64 parts in
# v612_source/streamlit_app_bundle/ to preserve the exact V6.12 source in GitHub.
_BUNDLE_DIR = Path(__file__).resolve().parent / "v612_source" / "streamlit_app_bundle"
_parts = sorted(_BUNDLE_DIR.glob("bundle_*.b64"))

if len(_parts) != 12:
    raise RuntimeError(
        f"QLDA V6.12 source bundle is incomplete: expected 12 parts, found {len(_parts)}."
    )

_b64 = "".join(p.read_text(encoding="ascii").strip() for p in _parts)
try:
    _source = gzip.decompress(base64.b64decode(_b64)).decode("utf-8")
except Exception as exc:
    raise RuntimeError(f"QLDA V6.12 source bundle is invalid: {exc}") from exc

exec(compile(_source, str(Path(__file__).resolve()), "exec"), globals(), globals())
