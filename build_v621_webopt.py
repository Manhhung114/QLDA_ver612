from __future__ import annotations

import base64
import gzip
from pathlib import Path


REQUIRED_MARKERS = (
    "QLDA Xây dựng V6.21 WebOpt",
    "from v621_webopt_runtime import install_runtime",
    "approval_workflows_for_records",
    "@st.fragment\ndef _render_online_approval",
    "@st.fragment\ndef _render_inline_drive_attachments",
    "Hiển thị biểu đồ Gantt",
    "def _paged_df",
    "def _render_excel_export",
    "class _LazyPlotlyExpress",
    "Tạo Excel tiến độ",
    "st.write_stream(",
    "ask_project_stream(",
    "install_ai_streaming()",
)

# Chỉ ẩn các chú thích/hướng dẫn tĩnh trên giao diện. Không đụng tới trạng thái,
# cảnh báo nghiệp vụ, workflow, quyền, database hoặc Google Drive.
HIDDEN_UI_NOTE_MARKERS = (
    "Sau khi tải file lớn xong, quay lại app",
    "Sau khi tải xong, quay lại app và bấm Làm mới file / File DB",
    "File lớn hơn giới hạn trên: dùng 'Mở trình tải file ở tab riêng'",
    "Workflow engine: **V6.21 WebOpt** • Nhà thầu trình",
    "Nếu một cấp yêu cầu chỉnh sửa: hồ sơ quay về Nhà thầu",
    "V6.9 không dùng nút Trình lại riêng",
    "Approval UI / Workflow engine: V6.21",
    "Nhập đúng Mã hồ sơ và Nội dung trình duyệt trước khi đính kèm file",
    "Nhập đúng Mã bản vẽ và Nội dung/Tên bản vẽ trước khi đính kèm file",
)

FORBIDDEN_UI_NOTE_MARKERS = (
    "Workflow engine: **V6.21 WebOpt** • Nhà thầu trình",
    "Nếu một cấp yêu cầu chỉnh sửa: hồ sơ quay về Nhà thầu",
    "Approval UI / Workflow engine: V6.21 WebOpt",
    "V6.9 không dùng nút Trình lại riêng",
    "Nhập đúng Mã hồ sơ và Nội dung trình duyệt trước khi đính kèm file",
    "Nhập đúng Mã bản vẽ và Nội dung/Tên bản vẽ trước khi đính kèm file",
    "Sau khi tải xong, quay lại app và bấm Làm mới file / File DB",
    "Sau khi tải file lớn xong, quay lại app",
    "File lớn hơn giới hạn trên: dùng 'Mở trình tải file ở tab riêng'",
)


def _finalize_source(source: str) -> str:
    """Apply final production-only WebOpt normalization at Docker build time."""
    source = source.replace("QLDA Xây dựng V6.0", "QLDA Xây dựng V6.21 WebOpt")
    source = source.replace("Workflow engine: **V6.21**", "Workflow engine: **V6.21 WebOpt**")
    source = source.replace("Approval UI / Workflow engine: V6.21", "Approval UI / Workflow engine: V6.21 WebOpt")

    ai_import = "from ai_service import (AIServiceError, AISettings, OpenAIProjectAssistant, GeminiSettings, GeminiProjectAssistant, ProjectContextBuilder)\n"
    if ai_import not in source:
        raise RuntimeError("V6.21 AI import anchor missing")
    source = source.replace(
        ai_import,
        ai_import + "from ai_streaming_patch import install_ai_streaming\ninstall_ai_streaming()\n",
        1,
    )

    # Giữ nguyên cách trả lời AI ban đầu. Chỉ thay cơ chế render sang streaming để
    # nội dung xuất hiện dần khi model gửi token về.
    old_chat = '''            try:\n                with st.chat_message("assistant"):\n                    with st.spinner("AI đang phân tích dữ liệu dự án..."):\n                        answer = ai.ask_project(pid, q, previous, date.today(), use_web=False)\n                    st.markdown(answer)\n                st.session_state[hkey].append({"role": "assistant", "content": answer})\n            except Exception as exc:\n                st.error(str(exc))\n'''
    new_chat = '''            try:\n                with st.chat_message("assistant"):\n                    _ai_status = st.empty()\n                    _ai_status.caption("AI đang phân tích dữ liệu dự án...")\n                    answer = st.write_stream(\n                        ai.ask_project_stream(pid, q, previous, date.today(), use_web=False)\n                    )\n                    _ai_status.empty()\n                answer = str(answer or "").strip()\n                if answer:\n                    st.session_state[hkey].append({"role": "assistant", "content": answer})\n            except Exception as exc:\n                st.error(str(exc))\n'''
    if old_chat not in source:
        raise RuntimeError("V6.21 AI streaming chat anchor missing")
    source = source.replace(old_chat, new_chat, 1)

    # Loại các dòng chú thích tĩnh để sheet gọn hơn, đặc biệt trên điện thoại.
    source = "\n".join(
        line for line in source.splitlines()
        if not any(marker in line for marker in HIDDEN_UI_NOTE_MARKERS)
    ) + "\n"

    # Hai caption "Nhập đúng Mã..." là body duy nhất của if not attach_ready.
    # Sau khi bỏ caption phải bỏ luôn if rỗng để source vẫn hợp lệ.
    source = source.replace(
        "        if not attach_ready:\n        is_revision_return =",
        "        is_revision_return =",
    )

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

    leaked_notes = [x for x in FORBIDDEN_UI_NOTE_MARKERS if x in source]
    if leaked_notes:
        raise RuntimeError(f"UI note cleanup incomplete: {leaked_notes}")
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
