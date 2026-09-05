from __future__ import annotations


PATCH_MARKER = "# V6.22 AUTH REFRESH V4"


def patch_auth_refresh_v4(source: str) -> str:
    """Persist the existing signed QLDA token across F5 without blocking UI.

    The generated V6.22 source already restores ``qlda_auth_session_v618`` from
    ``st.context.cookies`` and validates the restored signed token through the
    existing Drive Gateway ``me`` call. Only the browser writer is unreliable:
    ``components.html`` writes ``document.cookie`` inside its iframe rather than
    reliably on the Streamlit app origin.

    V4 changes only cookie write/remove. It never adds an auth readiness gate or
    ``st.stop()``, so a cookie-component problem cannot blank the application.
    The historical iframe writer is retained as a fail-open fallback.
    """
    if PATCH_MARKER in source:
        return source

    required = (
        '_QLDA_AUTH_COOKIE = "qlda_auth_session_v618"',
        "def _browser_session_cookie() -> str:",
        "def _write_browser_session_cookie(token: str) -> None:",
        "def _clear_browser_session_cookie() -> None:",
        "def _gateway_session_token() -> str:",
        "_write_browser_session_cookie(token)\n                st.rerun()",
        "_gateway_logout()\n            st.rerun()",
        "_qlda_cookie_written_for_token",
    )
    missing = [item for item in required if item not in source]
    if missing:
        raise RuntimeError(f"V6.22 auth refresh V4 anchors missing: {missing}")

    start = source.index("def _write_browser_session_cookie(token: str) -> None:")
    end = source.index("\ndef _gateway_session_token() -> str:", start)

    replacement = r'''# V6.22 AUTH REFRESH V4

def _qlda_cookie_controller_v4():
    """Create the browser cookie component only when a write/remove is needed."""
    from streamlit_cookies_controller import CookieController as _QLDACookieController
    return _QLDACookieController(key="qlda_auth_cookie_v622_v4")


def _qlda_cookie_secure_v4() -> bool:
    try:
        return str(st.context.url or "").strip().lower().startswith("https://")
    except Exception:
        return bool(IS_RAILWAY or IS_RENDER)


def _write_browser_session_cookie(token: str) -> None:
    value = str(token or "").strip()
    if not value:
        return

    # st.context.cookies is the cookie snapshot from the initial browser request.
    # On a true F5 it contains the persisted cookie, so no component is created.
    if _browser_session_cookie() == value:
        return

    try:
        controller = _qlda_cookie_controller_v4()
        controller.set(
            _QLDA_AUTH_COOKIE,
            value,
            path="/",
            max_age=float(_QLDA_AUTH_COOKIE_MAX_AGE),
            secure=_qlda_cookie_secure_v4(),
            same_site="lax",
        )
        return
    except Exception:
        # Fail open: preserve the historical behavior instead of blocking UI.
        pass

    js_value = json.dumps(value)
    secure = "; Secure" if _qlda_cookie_secure_v4() else ""
    components.html(
        f"""<script>
        (function() {{
          const value = {js_value};
          document.cookie = "{_QLDA_AUTH_COOKIE}=" + value + "; Path=/; Max-Age={_QLDA_AUTH_COOKIE_MAX_AGE}; SameSite=Lax{secure}";
        }})();
        </script>""",
        height=0,
    )


def _clear_browser_session_cookie() -> None:
    try:
        controller = _qlda_cookie_controller_v4()
        controller.remove(
            _QLDA_AUTH_COOKIE,
            path="/",
            secure=_qlda_cookie_secure_v4(),
            same_site="lax",
        )
        return
    except Exception:
        # Fail open and keep the old clear path as a compatibility fallback.
        pass

    secure = "; Secure" if _qlda_cookie_secure_v4() else ""
    components.html(
        f"""<script>
        document.cookie = "{_QLDA_AUTH_COOKIE}=; Path=/; Max-Age=0; SameSite=Lax{secure}";
        </script>""",
        height=0,
    )
'''
    source = source[:start] + replacement + source[end:]

    # Give the browser component time to receive the set/remove command before
    # Streamlit tears down the current run. This happens only on login/logout.
    source = source.replace(
        "_write_browser_session_cookie(token)\n                st.rerun()",
        "_write_browser_session_cookie(token)\n                time.sleep(0.50)\n                st.rerun()",
        1,
    )
    source = source.replace(
        "_gateway_logout()\n            st.rerun()",
        "_gateway_logout()\n            time.sleep(0.35)\n            st.rerun()",
        1,
    )

    return source
