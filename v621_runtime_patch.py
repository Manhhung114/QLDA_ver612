from __future__ import annotations

import base64
import gzip
from functools import lru_cache
from pathlib import Path

from v620_runtime_patch import install_db_patch as _db20, patch_streamlit_source as _ui20


def install_db_patch():
    _db20()
    # V6.21: /me vẫn được refresh thường xuyên để quyền thay đổi sớm, nhưng
    # giữ cache ngắn để fragment rerun không gọi Apps Script liên tục.
    try:
        import v620_runtime_patch as _v620
        _v620._TTLS["me"] = 15.0
    except Exception:
        pass


def _one(source: str, old: str, new: str, name: str) -> str:
    if old not in source:
        raise RuntimeError(f"V6.21 patch anchor missing: {name}")
    return source.replace(old, new, 1)


def patch_streamlit_source(source: str) -> str:
    s = _ui20(source)
    s = s.replace("Approval UI / Workflow engine: V6.20", "Approval UI / Workflow engine: V6.21")
    s = s.replace("Workflow engine: **V6.20**", "Workflow engine: **V6.21**")
    s = s.replace("QLDA Xây dựng V6.20 • Railway • Drive 2GB", "QLDA Xây dựng V6.21 • Railway • Drive 2GB")

    # Partial rerun: interactions inside file list and approval comment area do not
    # rerun the whole QLDA application. Explicit st.rerun() after a real DB/Drive
    # mutation still performs a full rerun so counters/workflow state remain exact.
    s = _one(
        s,
        "def _render_inline_drive_attachments(pid: int, *, kind: str, subtype: str, record_code: str, record_id: int, panel_key: str, show_contractor_upload: bool = True) -> int:\n",
        "@st.fragment\ndef _render_inline_drive_attachments(pid: int, *, kind: str, subtype: str, record_code: str, record_id: int, panel_key: str, show_contractor_upload: bool = True) -> int:\n",
        "Drive attachment fragment",
    )
    s = _one(
        s,
        "def _render_online_approval(pid: int, record_kind: str, subtype: str, record_id: int, record_code: str, record_title: str, attachment_count: int | None = None, submitted_name_hint: str = \"\") -> None:\n",
        "@st.fragment\ndef _render_online_approval(pid: int, record_kind: str, subtype: str, record_id: int, record_code: str, record_title: str, attachment_count: int | None = None, submitted_name_hint: str = \"\") -> None:\n",
        "online approval fragment",
    )

    # Lazy-load one document sheet instead of executing all seven st.tabs bodies.
    old_docs = '''def render_documents(pid: int):\n    st.subheader("📁 Quản lý hồ sơ")\n    doc_types = ["NCR", "RFA", "RFI", "BBHT", "NTCV", "NTVL", "KDVT"]\n    tab_names = ["NCR", "RFA", "RFI", "Biên bản hiện trường", "NT công việc", "NT vật liệu đầu vào", "Kiểm định vật tư"]\n    tabs = st.tabs(tab_names)\n    for tab, doc_type in zip(tabs, doc_types):\n        with tab:\n            st.markdown(f"### {DOC_CONFIG[doc_type]['title']}")\n            render_document_type(pid, doc_type)\n'''
    new_docs = '''def render_documents(pid: int):\n    st.subheader("📁 Quản lý hồ sơ")\n    doc_types = ["NCR", "RFA", "RFI", "BBHT", "NTCV", "NTVL", "KDVT"]\n    doc_labels = {\n        "NCR": "NCR", "RFA": "RFA", "RFI": "RFI",\n        "BBHT": "Biên bản hiện trường", "NTCV": "NT công việc",\n        "NTVL": "NT vật liệu đầu vào", "KDVT": "Kiểm định vật tư",\n    }\n    doc_type = st.segmented_control(\n        "Loại hồ sơ", doc_types, default=doc_types[0],\n        format_func=lambda x: doc_labels.get(x, x),\n        key=f"qlda_doc_section_{pid}", label_visibility="collapsed",\n    ) or doc_types[0]\n    st.markdown(f"### {DOC_CONFIG[doc_type]['title']}")\n    render_document_type(pid, doc_type)\n'''
    s = _one(s, old_docs, new_docs, "lazy document sheets")

    # Lazy-load one drawing sheet instead of all four tab bodies.
    old_drawings = '''def render_drawings(pid: int):\n    st.subheader("📐 Quản lý bản vẽ")\n    keys = ["SHOPDRAWING", "ISSUED_DESIGN", "UPDATED", "AS_BUILT"]\n    tabs = st.tabs([DRAWING_TYPES[k] for k in keys])\n    for tab, key in zip(tabs, keys):\n        with tab:\n            render_drawing_type(pid, key)\n'''
    new_drawings = '''def render_drawings(pid: int):\n    st.subheader("📐 Quản lý bản vẽ")\n    keys = ["SHOPDRAWING", "ISSUED_DESIGN", "UPDATED", "AS_BUILT"]\n    drawing_type = st.segmented_control(\n        "Loại bản vẽ", keys, default=keys[0],\n        format_func=lambda x: DRAWING_TYPES.get(x, x),\n        key=f"qlda_drawing_section_{pid}", label_visibility="collapsed",\n    ) or keys[0]\n    render_drawing_type(pid, drawing_type)\n'''
    s = _one(s, old_drawings, new_drawings, "lazy drawing sheets")

    # Main navigation: st.tabs executes every tab body on every rerun. V6.21 uses
    # a compact mobile-friendly selector and calls exactly one module.
    old_main = '''main_tabs = st.tabs(["📅 Quản lý tiến độ", "📁 Quản lý hồ sơ", "📐 Quản lý bản vẽ", "💰 Quản lý chi phí", "📦 Vật tư & thiết bị", "📷 Nhật ký công trường", "📊 Báo cáo trực quan", "📚 Văn bản QLDA XD", "🤖 Trợ lý AI", "⚙️ Cài đặt", "🏗️ Dự án"])\nwith main_tabs[0]:\n    render_schedule(pid)\nwith main_tabs[1]:\n    render_documents(pid)\nwith main_tabs[2]:\n    render_drawings(pid)\nwith main_tabs[3]:\n    render_cost_management(pid)\nwith main_tabs[4]:\n    render_material_management(pid)\nwith main_tabs[5]:\n    render_site_diary(pid)\nwith main_tabs[6]:\n    render_reports(pid)\nwith main_tabs[7]:\n    render_legal_documents()\nwith main_tabs[8]:\n    render_ai_assistant(pid)\nwith main_tabs[9]:\n    render_settings()\nwith main_tabs[10]:\n    render_project_info(pid)\n'''
    new_main = '''_main_sections = [\n    ("📅 Tiến độ", lambda: render_schedule(pid)),\n    ("📁 Hồ sơ", lambda: render_documents(pid)),\n    ("📐 Bản vẽ", lambda: render_drawings(pid)),\n    ("💰 Chi phí", lambda: render_cost_management(pid)),\n    ("📦 Vật tư", lambda: render_material_management(pid)),\n    ("📷 Nhật ký", lambda: render_site_diary(pid)),\n    ("📊 Báo cáo", lambda: render_reports(pid)),\n    ("📚 Văn bản", lambda: render_legal_documents()),\n    ("🤖 AI", lambda: render_ai_assistant(pid)),\n    ("⚙️ Cài đặt", lambda: render_settings()),\n    ("🏗️ Dự án", lambda: render_project_info(pid)),\n]\n_main_labels = [x[0] for x in _main_sections]\n_main_choice = st.selectbox(\n    "📌 Chức năng", _main_labels, key=f"qlda_main_section_{pid}",\n    help="V6.21 chỉ tải module đang chọn để giảm truy vấn và tăng tốc Railway.",\n)\n_main_actions = dict(_main_sections)\n_main_actions[_main_choice]()\n'''
    s = _one(s, old_main, new_main, "lazy top-level navigation")

    return s


@lru_cache(maxsize=1)
def compiled_streamlit_app(bundle_dir: str, entry_path: str):
    """Decode/patch/compile V6.21 once per Railway process."""
    parts = sorted(Path(bundle_dir).glob("bundle_*.b64"))
    if len(parts) != 12:
        raise RuntimeError(f"QLDA source bundle is incomplete: expected 12 parts, found {len(parts)}.")
    b64_text = "".join(p.read_text(encoding="ascii").strip() for p in parts)
    try:
        source = gzip.decompress(base64.b64decode(b64_text)).decode("utf-8")
    except Exception as exc:
        raise RuntimeError(f"QLDA source bundle is invalid: {exc}") from exc
    source = patch_streamlit_source(source)
    return compile(source, entry_path, "exec")
