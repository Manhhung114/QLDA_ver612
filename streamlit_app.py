from pathlib import Path
import base64
import gzip

from v615_runtime_patch import install_db_patch, patch_streamlit_source

# QLDA V6.15 loader.
# Base application source remains stored as the validated V6.12 gzip+base64 bundle.
# V6.15 applies the deterministic revision-resubmit patch for all online-approval types.
_BUNDLE_DIR = Path(__file__).resolve().parent / "v612_source" / "streamlit_app_bundle"
_parts = sorted(_BUNDLE_DIR.glob("bundle_*.b64"))

if len(_parts) != 12:
    raise RuntimeError(
        f"QLDA source bundle is incomplete: expected 12 parts, found {len(_parts)}."
    )

_b64 = "".join(p.read_text(encoding="ascii").strip() for p in _parts)
try:
    _source = gzip.decompress(base64.b64decode(_b64)).decode("utf-8")
except Exception as exc:
    raise RuntimeError(f"QLDA source bundle is invalid: {exc}") from exc

install_db_patch()
_source = patch_streamlit_source(_source)
exec(compile(_source, str(Path(__file__).resolve()), "exec"), globals(), globals())
