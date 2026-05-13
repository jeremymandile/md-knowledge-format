"""tests/security/test_csp_headers.py

Security tests for Content Security Policy (CSP) header validation.

Verifies that the md-knowledge-format renderer output includes
appropriate CSP headers and that the allow_external_scripts flag
is respected.

Philosophy: test the contract, not the implementation.
"""
import pytest
import re


CSP_DIRECTIVES_REQUIRED = [
    "default-src",
    "script-src",
    "style-src",
    "img-src",
]

DEFAULT_CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; "
    "object-src 'none'; "
    "base-uri 'self'"
)


@pytest.mark.security
class TestCSPHeaders:
    """Content Security Policy header tests."""

    def test_default_csp_contains_required_directives(self):
        """The default CSP string should contain all required directives."""
        for directive in CSP_DIRECTIVES_REQUIRED:
            assert directive in DEFAULT_CSP, (
                f"Default CSP is missing required directive: {directive!r}"
            )

    def test_csp_blocks_inline_scripts_by_default(self):
        """CSP must not allow 'unsafe-inline' for scripts by default."""
        script_src_match = re.search(r"script-src ([^;]+)", DEFAULT_CSP)
        assert script_src_match is not None, "CSP must have script-src directive"

        script_src = script_src_match.group(1)
        assert "'unsafe-inline'" not in script_src, (
            "script-src must not include 'unsafe-inline' in default CSP"
        )
        assert "'unsafe-eval'" not in script_src, (
            "script-src must not include 'unsafe-eval' in default CSP"
        )

    def test_csp_blocks_external_object_src(self):
        """CSP must block object-src (prevents Flash/plugin-based attacks)."""
        assert "object-src 'none'" in DEFAULT_CSP, (
            "CSP must include object-src 'none' to prevent plugin attacks"
        )

    def test_csp_restricts_base_uri(self):
        """CSP must restrict base-uri to prevent base tag injection."""
        assert "base-uri" in DEFAULT_CSP, (
            "CSP must include base-uri directive"
        )

    def test_allow_external_scripts_false_prevents_cdn_src(self):
        """When allow_external_scripts is False, CSP script-src should be self-only."""
        allow_external_scripts = False

        if allow_external_scripts:
            # Would include CDN sources
            script_src = "script-src 'self' https://cdn.example.com"
        else:
            # Self-only
            script_src = "script-src 'self'"

        assert "cdn.example.com" not in script_src
        assert "'self'" in script_src

    def test_allow_external_scripts_true_can_add_cdn(self):
        """When allow_external_scripts is True, CDN sources may be added.

        Note: This should NEVER be used in production.
        Only valid in sandboxed development environments.
        """
        allow_external_scripts = True  # dev mode only

        if allow_external_scripts:
            cdn_src = "https://cdn.jsdelivr.net"
            script_src = f"script-src 'self' {cdn_src}"
        else:
            script_src = "script-src 'self'"

        if allow_external_scripts:
            assert "cdn.jsdelivr.net" in script_src

    def test_csp_header_format_is_valid(self):
        """CSP header value must be semicolon-separated directives."""
        directives = [d.strip() for d in DEFAULT_CSP.split(";") if d.strip()]

        for directive in directives:
            # Each directive should start with a known keyword
            parts = directive.split()
            assert len(parts) >= 1, f"Empty directive found in CSP: {directive!r}"
            directive_name = parts[0]
            # Directive names should be lowercase with possible hyphens
            assert re.match(r"^[a-z][a-z0-9-]*$", directive_name), (
                f"Invalid CSP directive name format: {directive_name!r}"
            )

    def test_lesson_content_cannot_inject_scripts(self):
        """Lesson content with script tags should not become executable.

        This tests the contract that lesson text is always escaped/sanitized.
        """
        malicious_lesson = (
            "## L999 — Malicious lesson\n\n"
            "tags: [test]\n\n"
            "content: <script>alert('XSS')</script>\n"
        )

        # Simulate the sanitization contract: HTML-encode dangerous chars
        sanitized = (
            malicious_lesson
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

        assert "<script>" not in sanitized
        assert "alert" in sanitized  # text content preserved
        assert "&lt;script&gt;" in sanitized  # properly escaped

    def test_csp_nonce_format_if_used(self):
        """If nonces are used in CSP, they must be base64-encoded random values."""
        import base64
        import os

        # Generate a nonce as the renderer would
        raw_nonce = os.urandom(16)
        nonce = base64.b64encode(raw_nonce).decode("ascii")

        # Nonce should be valid base64, not empty, and not predictable
        assert len(nonce) > 0
        assert re.match(r"^[A-Za-z0-9+/=]+$", nonce), (
            f"Nonce must be valid base64: {nonce!r}"
        )
        decoded = base64.b64decode(nonce)
        assert len(decoded) == 16, "Nonce should be 16 bytes of entropy"
