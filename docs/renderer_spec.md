# Renderer Specification v1.0

**Purpose:** Deterministic routing and secure rendering of agent outputs into human-facing HTML or machine-facing Markdown.
**Status:** Production-ready for OpenClaw / NemoClaw pipelines.
**Maintainer:** Jeremy Mandile (md-knowledge-format)

---

## 1. Overview

The Renderer Specification defines:

- **When** an agent should emit HTML instead of Markdown (based on audience and complexity).
- **How** to structure the decision logic in a deterministic, validatable way.
- **How** to secure HTML output so that rich presentation never becomes an attack surface.
- **How** to retain versioned, grep-friendly sources of truth while delivering polished human experiences.

This spec directly implements the lesson taught in [LESSONS.md](#lessonsmd) regarding HTML as a "presentation plane artifact" and Markdown as "control plane."

---

## 2. Output Format Decision Schema

The router decision is encoded in `renderer_decision_schema.json`. This JSON Schema is used to **validate** an agent's output format intent before rendering begins.

### 2.1 Full Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://md-knowledge-format.io/renderer_decision_schema.json",
  "title": "Agent Output Format Decision",
  "schemaVersion": "1.0",
  "type": "object",
  "properties": {
    "recipient": {
      "description": "Intended consumer of the output.",
      "enum": ["human", "agent", "system"]
    },
    "complexity_score": {
      "type": "integer",
      "minimum": 1,
      "maximum": 10,
      "description": "1 = trivial answer; 10 = multi-phase plan with interactive comparisons."
    },
    "requires_interactivity": {
      "type": "boolean",
      "description": "Does the output benefit from expand/collapse, tabs, or in-browser exploration?"
    },
    "rendering_constraints": {
      "type": "object",
      "properties": {
        "max_token_budget": {
          "type": "integer",
          "minimum": 100,
          "description": "Maximum number of tokens allowed for the rendered output."
        },
        "allow_external_scripts": {
          "type": "boolean",
          "default": false,
          "description": "Must always be false in production; included for completeness."
        }
      },
      "required": ["max_token_budget"]
    },
    "recommended_format": {
      "enum": ["markdown", "html", "json"]
    }
  },
  "required": ["recipient", "complexity_score", "recommended_format", "rendering_constraints"],
  "allOf": [
    {
      "if": {
        "properties": {
          "recipient": { "const": "human" },
          "complexity_score": { "minimum": 6 }
        }
      },
      "then": {
        "properties": {
          "recommended_format": { "const": "html" }
        }
      }
    },
    {
      "if": {
        "properties": {
          "recipient": { "const": "agent" }
        }
      },
      "then": {
        "properties": {
          "recommended_format": { "const": "markdown" }
        }
      }
    },
    {
      "if": {
        "properties": {
          "requires_interactivity": { "const": true }
        }
      },
      "then": {
        "properties": {
          "recommended_format": { "const": "html" }
        }
      },
      "else": {
        "properties": {
          "recommended_format": { "const": "markdown" }
        }
      }
    }
  ]
}
```

### 2.2 Deterministic Fallback

The `else` clause guarantees that if no explicit condition triggers `html`, the output silently falls back to `markdown`. This ensures no undefined format is ever passed to the renderer.

### 2.3 Token Budget Enforcement

The `max_token_budget` is declared inside `rendering_constraints`. When the agent's estimated output tokens exceed this value **and** the recommended format is HTML, the rendering pipeline must **fall back to Markdown** (or trigger progressive rendering — see Section 5).

---

## 3. Secure HTML Rendering

All agent-generated HTML must be passed through a **sanitization + CSP middleware** before being served to a browser.

### 3.1 Tag and Attribute Allowlist

**Allowed tags:**
`div`, `details`, `summary`, `svg`, `table`, `thead`, `tbody`, `tr`, `th`, `td`, `p`, `h1`-`h6`, `ul`, `ol`, `li`, `a`, `code`, `pre`, `span`, `strong`, `em`, `img`, `br`, `hr`, `input` (type=range only)

**Allowed attributes per tag:**

- `a`: `href`, `title`
- `input`: `type`, `value`, `min`, `max`, `step`, `disabled`
- `img`: `src`, `alt`
- `svg`: `viewBox`, `width`, `height`, `xmlns`
- `details`: `open`
- Global: `class`, `id`

**Stripped completely:** `<script>`, `<style>`, `<iframe>`, `<object>`, `<embed>`, event handlers (`on*`).

### 3.2 Content Security Policy (CSP) with Nonce

Inline styles are necessary for basic visual formatting (colour-coded diffs, layout). To allow them safely without `'unsafe-inline'`, we use a **cryptographic nonce**.

```python
import secrets
from flask import Response

def generate_nonce() -> str:
    return secrets.token_urlsafe(16)

def csp_header(nonce: str) -> str:
    return (
        f"default-src 'self'; "
        f"script-src 'none'; "
        f"style-src 'self' 'nonce-{nonce}'; "
        f"img-src 'self' data:; "
        f"frame-ancestors 'none'; "
        f"base-uri 'self'; "
        f"form-action 'none'"
    )

def apply_security_hardening(agent_html: str) -> Response:
    nonce = generate_nonce()
    sanitized = sanitize_html(agent_html, nonce)
    resp = Response(sanitized, mimetype='text/html')
    resp.headers['Content-Security-Policy'] = csp_header(nonce)
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['X-Frame-Options'] = 'DENY'
    return resp
```

**Rationale:** Even if an attacker injects a `<style>` tag, the browser only applies styles carrying the correct nonce — blocking any injected CSS.

---

## 4. Integration Guide

### 4.1 OpenClaw / NemoClaw Pipeline

```yaml
pipeline:
  stages:
    - name: output_format_routing
      schema: specs/renderer_decision_schema.json
      logic: |
        IF recipient == "human" AND (complexity_score >= 6 OR requires_interactivity == true):
          SET recommended_format = "html"
        ELSE:
          SET recommended_format = "markdown"

    - name: token_budget_fallback
      condition: recommended_format == "html" AND estimated_tokens > rendering_constraints.max_token_budget
      action: set recommended_format = "markdown"
      log: "Token budget exceeded, falling back to Markdown."

    - name: rendering
      if: recommended_format == "html"
      action: compile_to_html(template="v2_dynamic")
      guardrails: [sanitize_html, apply_security_hardening]

    - fallback:
      action: compile_to_markdown(template="v1_linear")
```

### 4.2 Middleware Registration (Python / FastAPI)

```python
from middleware.csp_sanitizer import apply_security_hardening

@app.post("/agent/output")
async def agent_output(request: AgentOutputRequest):
    raw_html = await render_html(request.data)
    safe_response = apply_security_hardening(raw_html)
    return safe_response
```

### 4.3 Testing Checklist

- [ ] Schema validation: `recipient=human`, `complexity_score=6` → `recommended_format=html`
- [ ] Fallback: `recipient=agent`, `complexity_score=9` → `markdown`
- [ ] Token budget override: `max_token_budget=500` with estimated tokens 600 → format switches to `markdown`
- [ ] CSP header present with nonce
- [ ] `<script>alert(1)</script>` stripped from malicious input
- [ ] `onerror` handlers removed from allowed tags
- [ ] Nonce attribute added to `<style>` blocks

---

## 5. Progressive Rendering (Future Enhancement)

When token budgets are tight but interactivity is still desirable, the pipeline may employ progressive rendering:

1. Stream the semantic skeleton in plain Markdown.
2. On user interaction (click to expand), dynamically fetch and render the relevant HTML fragment.
3. Each fragment is individually sanitized with its own nonce.

This is documented separately in `progressive_rendering_spec.md` (available upon request).

---

## 6. Companion Artifacts

| Artifact | Description |
|----------|-------------|
| `renderer_decision_schema.json` | Formal JSON Schema (this spec, Section 2) |
| `renderer_test_suite.json` | Edge-case test vectors for schema + sanitizer |
| `html_tag_whitelist.yaml` | Standalone allowlist, easy to audit and extend |
| `csp_sanitizer.py` | Production-ready middleware (Section 3) |

---

## 7. Feedback & Updates

This specification is versioned and open to refinement. Contact Jeremy Mandile via GitHub issues on the md-knowledge-format repository.

**Current Version:** 1.0 (2026-05-12) — Initial release aligned with Claude Code HTML shift lessons.
