"""
csp_sanitizer.py -- Secure HTML rendering middleware for agent outputs.

md-knowledge-format :: Renderer Specification v1.0
https://github.com/jeremymandile/md-knowledge-format/blob/master/docs/renderer_spec.md

Usage (Flask):
    from tools.csp_sanitizer import apply_security_hardening

    @app.post("/agent/output")
    def agent_output():
        raw_html = render_html(request.data)
        return apply_security_hardening(raw_html)

Usage (FastAPI):
    from tools.csp_sanitizer import apply_security_hardening
    from fastapi.responses import HTMLResponse

    @app.post("/agent/output")
    async def agent_output(request: Request):
        raw_html = await render_html(request.body())
        resp = apply_security_hardening(raw_html)
        return HTMLResponse(content=resp.get_data(as_text=True),
                            headers=dict(resp.headers))

Install optional dependency:
    pip install beautifulsoup4
"""

import secrets
from typing import Dict, List

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    from flask import Response
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# ---------------------------------------------------------------------------
# Allowlists
# ---------------------------------------------------------------------------

ALLOWED_TAGS: set = {
    "div", "details", "summary", "svg", "table", "thead", "tbody", "tr",
    "th", "td", "p", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li",
    "a", "code", "pre", "span", "strong", "em", "img", "br", "hr", "input",
}

ALLOWED_ATTRS: Dict[str, List[str]] = {
    "a":       ["href", "title"],
    "input":   ["type", "value", "min", "max", "step", "disabled"],
    "img":     ["src", "alt"],
    "svg":     ["viewBox", "width", "height", "xmlns"],
    "details": ["open"],
    "*":       ["class", "id"],
}

# Attribute prefixes that are stripped unconditionally (event handlers + inline style).
DISALLOWED_ATTR_PREFIXES: tuple = ("on", "style")

# URL schemes that are blocked in href / src attributes.
BLOCKED_URL_SCHEMES: tuple = ("javascript:", "data:", "vbscript:")

# ---------------------------------------------------------------------------
# CSP helpers
# ---------------------------------------------------------------------------

def generate_nonce() -> str:
    """Return a cryptographically random nonce suitable for a CSP style-src."""
    return secrets.token_urlsafe(16)


def build_csp_header(nonce: str) -> str:
    """Return a strict Content-Security-Policy header value."""
    return (
        f"default-src 'self'; "
        f"script-src 'none'; "
        f"style-src 'self' 'nonce-{nonce}'; "
        f"img-src 'self' data:; "
        f"frame-ancestors 'none'; "
        f"base-uri 'self'; "
        f"form-action 'none'"
    )

# ---------------------------------------------------------------------------
# URL escaping
# ---------------------------------------------------------------------------

def _safe_url(value: str) -> str:
    """Return an empty string if the URL uses a blocked scheme."""
    stripped = value.strip().lower()
    for scheme in BLOCKED_URL_SCHEMES:
        if stripped.startswith(scheme):
            return ""
    return value

# ---------------------------------------------------------------------------
# HTML sanitisation
# ---------------------------------------------------------------------------

def sanitize_html(raw_html: str, nonce: str) -> str:
    """
    Strip disallowed tags/attributes from *raw_html* and inject *nonce* into
    any remaining <style> blocks.

    Requires beautifulsoup4:  pip install beautifulsoup4
    """
    if not BS4_AVAILABLE:
        raise ImportError(
            "beautifulsoup4 is required for HTML sanitisation. "
            "Install it with:  pip install beautifulsoup4"
        )

    soup = BeautifulSoup(raw_html, "html.parser")

    # 1. Decompose entirely dangerous elements.
    for tag_name in ("script", "iframe", "object", "embed", "base", "link", "meta"):
        for tag in soup.find_all(tag_name):
            tag.decompose()

    # 2. Process remaining tags.
    for tag in soup.find_all(True):
        if tag.name == "style":
            # Keep <style> blocks but inject the nonce so the browser
            # only applies styles issued by our renderer.
            tag["nonce"] = nonce
            continue

        if tag.name not in ALLOWED_TAGS:
            tag.unwrap()  # Remove the tag but preserve its text content.
            continue

        # Build the per-tag attribute allowlist.
        allowed_here = (
            ALLOWED_ATTRS.get(tag.name, []) + ALLOWED_ATTRS.get("*", [])
        )

        # Collect attributes to remove.
        attrs_to_remove = []
        for attr in list(tag.attrs):
            if any(attr.startswith(prefix) for prefix in DISALLOWED_ATTR_PREFIXES):
                attrs_to_remove.append(attr)
            elif attr not in allowed_here:
                attrs_to_remove.append(attr)

        for attr in attrs_to_remove:
            del tag.attrs[attr]

        # Sanitise URL-bearing attributes.
        for url_attr in ("href", "src", "action"):
            if url_attr in tag.attrs:
                tag.attrs[url_attr] = _safe_url(str(tag.attrs[url_attr]))

    return str(soup)


# ---------------------------------------------------------------------------
# Full response hardening (Flask)
# ---------------------------------------------------------------------------

def apply_security_hardening(agent_html: str) -> "Response":
    """
    Sanitise *agent_html* and wrap it in a Flask Response with strict
    security headers.

    Returns a Flask Response object.  Requires flask: pip install flask
    """
    if not FLASK_AVAILABLE:
        raise ImportError(
            "flask is required for apply_security_hardening(). "
            "Install it with:  pip install flask"
        )

    nonce = generate_nonce()
    safe_html = sanitize_html(agent_html, nonce)

    resp = Response(safe_html, mimetype="text/html")
    resp.headers["Content-Security-Policy"] = build_csp_header(nonce)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return resp


# ---------------------------------------------------------------------------
# Standalone sanitisation (no Flask dependency)
# ---------------------------------------------------------------------------

def sanitize(agent_html: str) -> Dict[str, str]:
    """
    Framework-agnostic alternative.  Returns a dict with keys:
      - "html"  : the sanitised HTML string
      - "csp"   : the Content-Security-Policy header value
      - "nonce" : the nonce used (in case you need to embed it)
    """
    nonce = generate_nonce()
    safe_html = sanitize_html(agent_html, nonce)
    return {
        "html":  safe_html,
        "csp":   build_csp_header(nonce),
        "nonce": nonce,
    }


# ---------------------------------------------------------------------------
# CLI smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    malicious = (
        '<div onclick="alert(1)">'
        '<script>evil()</script>'
        '<a href="javascript:bad()">click</a>'
        '<img src="data:text/html,<h1>xss</h1>" onerror="evil()">'
        '<style>body{color:red}</style>'
        '</div>'
    )

    result = sanitize(malicious)
    html = result["html"]

    assert "onclick" not in html, "onclick not stripped"
    assert "<script" not in html, "<script> not stripped"
    assert "javascript:" not in html, "javascript: URL not blocked"
    assert "data:text" not in html, "data: URL not blocked"
    assert "onerror" not in html, "onerror not stripped"
    assert "nonce-" in result["csp"], "nonce missing from CSP"

    print("All assertions passed.")
    print("Sanitised HTML:")
    print(html)
    print()
    print("CSP header:")
    print(result["csp"])

    sys.exit(0)
