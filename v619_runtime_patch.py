from __future__ import annotations

from v618_runtime_patch import install_db_patch as _db18, patch_streamlit_source as _ui18


def install_db_patch():
    _db18()


def patch_streamlit_source(source: str) -> str:
    s = _ui18(source)
    s = s.replace('Approval UI / Workflow engine: V6.18', 'Approval UI / Workflow engine: V6.19')
    s = s.replace('Workflow engine: **V6.18**', 'Workflow engine: **V6.19**')
    return s
