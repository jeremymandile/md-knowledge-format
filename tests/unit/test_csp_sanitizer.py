"""
Unit tests for csp_sanitizer.py middleware.
"""
import pytest

try:
    from tools.csp_sanitizer import apply_security_hardening, generate_nonce
    HAS_SANITIZER = True
except ImportError:
    HAS_SANITIZER = False

pytestmark = pytest.mark.skipif(not HAS_SANITIZER, reason="csp_sanitizer not importable without Flask")


def test_script_tag_stripped():
    """<script> tags must be completely removed"""
    raw = "<div><script>alert('xss')</script>Safe text</div>"
    resp = apply_security_hardening(raw)
    assert "Safe text" in resp.text
    assert "<script>" not in resp.text.lower()
    assert "alert" not in resp.text.lower()


def test_event_handlers_stripped():
    """Inline event handlers must be removed"""
    raw = "<a href='#' onclick='steal()' onmouseover='bad()'>click</a>"
    resp = apply_security_hardening(raw)
    assert "click" in resp.text
    assert "onclick" not in resp.text.lower()
    assert "onmouseover" not in resp.text.lower()


def test_javascript_url_blocked():
    """javascript: URLs in href/src must be blocked"""
    raw = "<a href='javascript:void(document.cookie)'>link</a>"
    resp = apply_security_hardening(raw)
    assert "link" in resp.text
    assert "javascript:" not in resp.text.lower()


def test_iframe_stripped():
    """<iframe>, <object>, <embed> must be removed"""
    raw = "<div><iframe src='evil.com'></iframe>content</div>"
    resp = apply_security_hardening(raw)
    assert "content" in resp.text
    assert "<iframe" not in resp.text.lower()


def test_csp_headers_present():
    """All required security headers must be present"""
    raw = "<p>test</p>"
    resp = apply_security_hardening(raw)
    csp = resp.headers["Content-Security-Policy"]
    assert "default-src 'self'" in csp
    assert "script-src 'none'" in csp
    assert "nonce-" in csp
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-Frame-Options"] == "DENY"


def test_nonce_is_unique():
    """Generated nonces should be cryptographically unique"""
    nonce1 = generate_nonce()
    nonce2 = generate_nonce()
    assert nonce1 != nonce2
    assert len(nonce1) >= 16


def test_disallowed_tag_unwrapped():
    """Disallowed tags should be unwrapped but text preserved"""
    raw = "<marquee><b>scrolling</b></marquee>"
    resp = apply_security_hardening(raw)
    assert "scrolling" in resp.text
    assert "<marquee>" not in resp.text.lower()


def test_safe_html_passes():
    """Safe HTML should pass through with CSP headers"""
    raw = "<div class='info'><p>Hello world</p></div>"
    resp = apply_security_hardening(raw)
    assert "Hello world" in resp.text
    assert resp.headers["Content-Security-Policy"]
