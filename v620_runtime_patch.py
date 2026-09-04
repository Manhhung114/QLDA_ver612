from __future__ import annotations

import base64
import copy
import gzip
import json
import threading
import time
from functools import lru_cache
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter

from v619_runtime_patch import install_db_patch as _db19, patch_streamlit_source as _ui19


_FILE_ACTIONS = {"list_record_files", "record_file_counts", "file_info"}
_USER_ACTIONS = {"approval_users", "list_users", "root_info"}
_TTLS = {
    "list_record_files": 3.0,
    "record_file_counts": 5.0,
    "file_info": 30.0,
    "approval_users": 30.0,
    "list_users": 20.0,
    "root_info": 60.0,
}


def _install_drive_gateway_fast_path() -> None:
    """Reuse HTTP/TLS connections and short-cache read-only Drive calls."""
    from drive_gateway import DriveGateway, DriveGatewayError

    if getattr(DriveGateway, "_v620_runtime_fast_path", False):
        return

    original_init = DriveGateway.__init__

    def fast_init(self, config):
        original_init(self, config)
        self._v620_http = requests.Session()
        adapter = HTTPAdapter(pool_connections=20, pool_maxsize=20, max_retries=0)
        self._v620_http.mount("https://", adapter)
        self._v620_http.mount("http://", adapter)
        self._v620_http.headers.update({"User-Agent": "QLDA-XayDung-V6.20-Railway/1.0"})
        self._v620_cache = {}
        self._v620_cache_lock = threading.RLock()

    def clear_cache(self, scope: str = "all") -> None:
        scope = str(scope or "all").strip().lower()
        wanted = _FILE_ACTIONS if scope == "files" else _USER_ACTIONS if scope == "users" else None
        with self._v620_cache_lock:
            if wanted is None:
                self._v620_cache.clear()
                return
            for key in list(self._v620_cache):
                if key[0] in wanted:
                    self._v620_cache.pop(key, None)

    def close(self) -> None:
        try:
            self._v620_http.close()
        except Exception:
            pass

    def fast_post(self, action: str, payload=None, session_token: str = ""):
        if not self.config.configured:
            raise DriveGatewayError(
                "Chưa cấu hình QLDA_DRIVE_WEBAPP_URL / QLDA_DRIVE_API_TOKEN."
            )

        payload = dict(payload or {})
        ttl = float(_TTLS.get(str(action), 0.0))
        cache_key = None
        now = time.monotonic()
        if ttl > 0:
            payload_key = json.dumps(
                payload, ensure_ascii=False, sort_keys=True,
                separators=(",", ":"), default=str,
            )
            cache_key = (str(action), str(session_token or ""), payload_key)
            with self._v620_cache_lock:
                hit = self._v620_cache.get(cache_key)
                if hit and hit[0] > now:
                    return copy.deepcopy(hit[1])

        body = {"action": action, "api_token": self.config.api_token}
        if payload:
            body.update(payload)
        if session_token:
            body["session_token"] = session_token

        try:
            resp = self._v620_http.post(
                self.config.webapp_url,
                json=body,
                timeout=self.config.timeout,
                allow_redirects=True,
            )
        except requests.RequestException as exc:
            raise DriveGatewayError(f"Không kết nối được Google Drive Gateway: {exc}") from exc

        if resp.status_code >= 400:
            raise DriveGatewayError(
                f"Google Drive Gateway HTTP {resp.status_code}: {resp.text[:500]}"
            )
        try:
            data = resp.json()
        except Exception as exc:
            raise DriveGatewayError(
                "Google Drive Gateway trả về dữ liệu không phải JSON. Kiểm tra URL Web App /exec."
            ) from exc
        if not isinstance(data, dict):
            raise DriveGatewayError("Google Drive Gateway trả về dữ liệu không hợp lệ.")
        if not data.get("ok", False):
            raise DriveGatewayError(str(data.get("error") or "Google Drive Gateway báo lỗi không xác định."))

        if cache_key is not None:
            with self._v620_cache_lock:
                self._v620_cache[cache_key] = (now + ttl, copy.deepcopy(data))
                if len(self._v620_cache) > 256:
                    expired = [k for k, v in self._v620_cache.items() if v[0] <= now]
                    for k in expired:
                        self._v620_cache.pop(k, None)
                    while len(self._v620_cache) > 256:
                        self._v620_cache.pop(next(iter(self._v620_cache)), None)

        if action in {"trash_file", "upload_legacy"}:
            clear_cache(self, "files")
        elif action in {"set_user", "delete_user"}:
            clear_cache(self, "users")
        return data

    DriveGateway.__init__ = fast_init
    DriveGateway._post = fast_post
    DriveGateway.clear_cache = clear_cache
    DriveGateway.close = close
    DriveGateway._v620_runtime_fast_path = True


def _install_sqlite_indexes() -> None:
    """Add read-path indexes without changing existing data or workflow rules."""
    from cloud_db import CloudDatabase

    if getattr(CloudDatabase, "_v620_runtime_indexes", False):
        return

    original_create_tables = CloudDatabase.create_tables

    def create_tables_with_fast_indexes(self):
        original_create_tables(self)
        with self.connect() as c:
            c.executescript(
                """
                CREATE INDEX IF NOT EXISTS idx_tasks_project_source_order
                    ON tasks(project_id, source_type, source_task_id, start_date, id);
                CREATE INDEX IF NOT EXISTS idx_documents_project_type_date
                    ON documents(project_id, doc_type, issue_date, id);
                CREATE INDEX IF NOT EXISTS idx_document_attachments_document
                    ON document_attachments(document_id, id);
                CREATE INDEX IF NOT EXISTS idx_drawings_project_type_date
                    ON drawings(project_id, drawing_type, received_date, id);
                CREATE INDEX IF NOT EXISTS idx_drawing_attachments_drawing
                    ON drawing_attachments(drawing_id, id);
                CREATE INDEX IF NOT EXISTS idx_approval_workflows_lookup
                    ON approval_workflows(project_id, record_kind, subtype, record_id);
                CREATE INDEX IF NOT EXISTS idx_approval_workflows_record_fast
                    ON approval_workflows(project_id, record_kind, record_id, current_stage, id);
                CREATE INDEX IF NOT EXISTS idx_approval_steps_workflow_order
                    ON approval_steps(workflow_id, stage_order, stage_code);
                """
            )

    CloudDatabase.create_tables = create_tables_with_fast_indexes
    CloudDatabase._v620_runtime_indexes = True


def install_db_patch() -> None:
    """Compatibility entrypoint used by the small Railway loader."""
    _db19()
    _install_drive_gateway_fast_path()
    _install_sqlite_indexes()


def _one(source: str, old: str, new: str, name: str) -> str:
    if old not in source:
        raise RuntimeError(f"V6.20 patch anchor missing: {name}")
    return source.replace(old, new, 1)


def _patch_v620_final_source(source: str) -> str:
    s = source
    s = s.replace("Approval UI / Workflow engine: V6.19", "Approval UI / Workflow engine: V6.20")
    s = s.replace("Workflow engine: **V6.19**", "Workflow engine: **V6.20**")
    s = s.replace("Workflow engine: **V6.17**", "Workflow engine: **V6.20**")
    s = s.replace("QLDA Xây dựng V6.0 • Render • Drive 2GB", "QLDA Xây dựng V6.20 • Railway • Drive 2GB")

    old_gateway = '''def _drive_gateway() -> DriveGateway:\n    return DriveGateway(config_from_streamlit(st))\n'''
    new_gateway = '''def _drive_gateway() -> DriveGateway:\n    # V6.20: giữ một Gateway trong session để tái sử dụng HTTP connection pool\n    # và cache đọc ngắn hạn xuyên qua các lần st.rerun().\n    cfg = config_from_streamlit(st)\n    signature = (cfg.webapp_url, cfg.api_token, int(cfg.timeout), int(cfg.legacy_max_upload_mb), int(cfg.direct_max_upload_mb))\n    holder = st.session_state.get("_qlda_drive_gateway_instance")\n    if isinstance(holder, tuple) and len(holder) == 2 and holder[0] == signature:\n        return holder[1]\n    if isinstance(holder, tuple) and len(holder) == 2:\n        try:\n            holder[1].close()\n        except Exception:\n            pass\n    gw = DriveGateway(cfg)\n    st.session_state["_qlda_drive_gateway_instance"] = (signature, gw)\n    return gw\n'''
    s = _one(s, old_gateway, new_gateway, "persistent DriveGateway")

    old_refresh = '''    if h1.button("🔄 Làm mới file / File DB", key=panel_key + "_refresh_files", width="stretch"):\n        st.rerun()\n'''
    new_refresh = '''    if h1.button("🔄 Làm mới file / File DB", key=panel_key + "_refresh_files", width="stretch"):\n        try:\n            _drive_gateway().clear_cache("files")\n        except Exception:\n            pass\n        st.rerun()\n'''
    s = _one(s, old_refresh, new_refresh, "Drive refresh cache clear")

    old_logout = '''def _gateway_logout() -> None:\n    for key in ("qlda_drive_session_token", "qlda_drive_identity", "qlda_drive_error", "qlda_auth_restored_from_cookie"):\n        st.session_state.pop(key, None)\n    st.session_state["qlda_ignore_persistent_auth"] = True\n    _clear_browser_session_cookie()\n'''
    new_logout = '''def _gateway_logout() -> None:\n    holder = st.session_state.pop("_qlda_drive_gateway_instance", None)\n    if isinstance(holder, tuple) and len(holder) == 2:\n        try:\n            holder[1].close()\n        except Exception:\n            pass\n    for key in ("qlda_drive_session_token", "qlda_drive_identity", "qlda_drive_error", "qlda_auth_restored_from_cookie"):\n        st.session_state.pop(key, None)\n    st.session_state["qlda_ignore_persistent_auth"] = True\n    _clear_browser_session_cookie()\n'''
    s = _one(s, old_logout, new_logout, "gateway cleanup on logout")
    return s


def patch_streamlit_source(source: str) -> str:
    return _patch_v620_final_source(_ui19(source))


@lru_cache(maxsize=1)
def compiled_streamlit_app(bundle_dir: str, entry_path: str):
    """Decode/patch/compile the legacy bundle once per Railway process."""
    parts = sorted(Path(bundle_dir).glob("bundle_*.b64"))
    if len(parts) != 12:
        raise RuntimeError(
            f"QLDA source bundle is incomplete: expected 12 parts, found {len(parts)}."
        )
    raw_b64 = "".join(p.read_text(encoding="ascii").strip() for p in parts)
    try:
        source = gzip.decompress(base64.b64decode(raw_b64)).decode("utf-8")
    except Exception as exc:
        raise RuntimeError(f"QLDA source bundle is invalid: {exc}") from exc
    source = patch_streamlit_source(source)
    return compile(source, str(entry_path), "exec")
