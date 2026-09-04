from __future__ import annotations

import base64
import gzip
from pathlib import Path


REQUIRED_MARKERS = (
    "Workflow engine: **V6.21 WebOpt**",
    "from v621_webopt_runtime import install_runtime",
    "approval_workflows_for_records",
    "@st.fragment\ndef _render_online_approval",
    "@st.fragment\ndef _render_inline_drive_attachments",
    "Hiển thị biểu đồ Gantt",
    "def _paged_df",
    "def _render_excel_export",
    "class _LazyPlotlyExpress",
    "Tạo Excel tiến độ",
)


def _finalize_source(source: str) -> str:
    """Apply final production-only WebOpt normalization at Docker build time."""
    # Keep one clear build/version label everywhere the user can see it.
    source = source.replace("QLDA Xây dựng V6.0", "QLDA Xây dựng V6.21 WebOpt")
    source = source.replace("Workflow engine: **V6.21**", "Workflow engine: **V6.21 WebOpt**")
    source = source.replace("Approval UI / Workflow engine: V6.21", "Approval UI / Workflow engine: V6.21 WebOpt")

    # Historical bundle/runtime loader must never leak into the Railway runtime app.
    forbidden = (
        "from v621_runtime_patch import",
        "compiled_streamlit_app(",
        "bundle_01.b64",
        "v612_source/streamlit_app_bundle",
    )
    leaked = [x for x in forbidden if x in source]
    if leaked:
        raise RuntimeError(f"Historical runtime loader leaked into final WebOpt app: {leaked}")
    return source


def build() -> Path:
    root = Path(__file__).resolve().parent
    parts_dir = root / "v621_webopt_source"
    parts = sorted(parts_dir.glob("part_*.b64"))
    if len(parts) != 9:
        raise RuntimeError(f"Incomplete V6.21 WebOpt source: expected 9 parts, found {len(parts)}")

    try:
        encoded = "".join(p.read_text(encoding="ascii").strip() for p in parts)
        source = gzip.decompress(base64.b64decode(encoded)).decode("utf-8")
    except Exception as exc:
        raise RuntimeError(f"Invalid V6.21 WebOpt multipart source: {exc}") from exc

    source = _finalize_source(source)
    missing = [marker for marker in REQUIRED_MARKERS if marker not in source]
    if missing:
        raise RuntimeError(f"V6.21 WebOpt markers missing: {missing}")

    out = root / "dist" / "streamlit_app.py"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(source, encoding="utf-8")
    compile(source, str(out), "exec")
    print(f"V6.21 WebOpt production build OK: {len(source)} chars -> {out}")
    return out


def main() -> None:
    build()


if __name__ == "__main__":
    main()
