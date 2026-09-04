from __future__ import annotations

from pathlib import Path

import streamlit as st

from build_v621_webopt import build as _build_webopt


# Local/dev entrypoint. Railway does not execute this loader: the Docker builder
# generates the final app once and copies dist/streamlit_app.py directly into the
# runtime image. This keeps production reruns free of bundle decode/patch work.
_DIST = Path(__file__).resolve().parent / "dist" / "streamlit_app.py"
if not _DIST.exists():
    _build_webopt()


@st.cache_resource(show_spinner=False)
def _compiled_webopt(path: str, mtime_ns: int):
    source = Path(path).read_text(encoding="utf-8")
    return compile(source, path, "exec")


exec(
    _compiled_webopt(str(_DIST), _DIST.stat().st_mtime_ns),
    globals(),
    globals(),
)
