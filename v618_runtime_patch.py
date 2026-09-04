from __future__ import annotations

from v617_runtime_patch import install_db_patch as _db17, patch_streamlit_source as _ui17


def install_db_patch():
    _db17()


def _one(source: str, old: str, new: str, name: str) -> str:
    if old not in source:
        raise RuntimeError(f"V6.18 patch anchor missing: {name}")
    return source.replace(old, new, 1)


def patch_streamlit_source(source: str) -> str:
    s = _ui17(source)
    s = s.replace('Approval UI / Workflow engine: V6.17', 'Approval UI / Workflow engine: V6.18')
    s = s.replace('Workflow engine: **V6.17**', 'Workflow engine: **V6.18**')

    old_helpers = '''def _gateway_session_token() -> str:\n    return str(st.session_state.get("qlda_drive_session_token", "") or "")\n\n\ndef _gateway_logout() -> None:\n    for key in ("qlda_drive_session_token", "qlda_drive_identity", "qlda_drive_error"):\n        st.session_state.pop(key, None)\n'''
    new_helpers = '''# V6.18 - Phiên đăng nhập bền qua F5/Refresh.
# Session token do Apps Script ký HMAC và tự hết hạn (mặc định 12 giờ).
# Cookie chỉ giữ lại chính token đã ký; mỗi lần phục hồi app vẫn gọi /me để
# kiểm tra tài khoản còn hoạt động và quyền hiện tại trước khi cho truy cập.
_QLDA_AUTH_COOKIE = "qlda_auth_session_v618"
_QLDA_AUTH_COOKIE_MAX_AGE = 12 * 60 * 60


def _browser_session_cookie() -> str:
    try:
        cookies = st.context.cookies
        return str(cookies.get(_QLDA_AUTH_COOKIE, "") or "").strip()
    except Exception:
        return ""


def _auth_cookie_js(value: str, max_age: int) -> None:
    js_value = json.dumps(str(value or ""))
    secure = "; Secure" if (IS_RAILWAY or IS_RENDER) else ""
    cookie_text = f"{_QLDA_AUTH_COOKIE}=" + "__VALUE__" + f"; Path=/; Max-Age={int(max_age)}; SameSite=Lax{secure}"
    js_cookie = json.dumps(cookie_text)
    components.html(
        f"""<script>
        (function() {{
          const v = {js_value};
          const c = {js_cookie}.replace('__VALUE__', v);
          try {{ window.parent.document.cookie = c; }} catch (e) {{ document.cookie = c; }}
        }})();
        </script>""",
        height=0,
    )


def _write_browser_session_cookie(token: str) -> None:
    if str(token or "").strip():
        _auth_cookie_js(str(token).strip(), _QLDA_AUTH_COOKIE_MAX_AGE)


def _clear_browser_session_cookie() -> None:
    _auth_cookie_js("", 0)


def _gateway_session_token() -> str:
    token = str(st.session_state.get("qlda_drive_session_token", "") or "").strip()
    if token:
        return token
    if bool(st.session_state.get("qlda_ignore_persistent_auth", False)):
        return ""
    token = _browser_session_cookie()
    if token:
        st.session_state["qlda_drive_session_token"] = token
        st.session_state["qlda_auth_restored_from_cookie"] = True
    return token


def _gateway_logout() -> None:
    for key in ("qlda_drive_session_token", "qlda_drive_identity", "qlda_drive_error", "qlda_auth_restored_from_cookie"):
        st.session_state.pop(key, None)
    st.session_state["qlda_ignore_persistent_auth"] = True
    _clear_browser_session_cookie()
'''
    s = _one(s, old_helpers, new_helpers, 'auth helpers')

    old_login = '''                st.session_state["qlda_drive_session_token"] = token\n                st.session_state.pop("qlda_drive_identity", None)\n                st.rerun()'''
    new_login = '''                st.session_state["qlda_drive_session_token"] = token\n                st.session_state.pop("qlda_drive_identity", None)\n                st.session_state.pop("qlda_ignore_persistent_auth", None)\n                _write_browser_session_cookie(token)\n                st.rerun()'''
    s = _one(s, old_login, new_login, 'login persistence')

    old_valid = '''    with st.sidebar:\n        _ui_note(f"Người dùng: {identity.get('name') or identity.get('email')}")'''
    new_valid = '''    # Gia hạn cookie phía trình duyệt trong thời gian token backend còn hiệu lực.\n    # Nếu tab bị F5/Refresh và Streamlit tạo session mới, token này được phục hồi\n    # trước khi render màn hình login.\n    live_token = _gateway_session_token()\n    if live_token:\n        _write_browser_session_cookie(live_token)\n        if st.session_state.pop("qlda_auth_restored_from_cookie", False):\n            st.toast("Đã khôi phục phiên đăng nhập sau khi refresh.", icon="🔐")\n\n    with st.sidebar:\n        _ui_note(f"Người dùng: {identity.get('name') or identity.get('email')}")'''
    s = _one(s, old_valid, new_valid, 'authenticated cookie refresh')

    return s
