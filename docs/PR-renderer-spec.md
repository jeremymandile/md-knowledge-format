## feat: Deterministic HTML/Markdown Routing + Secure Rendering (Renderer Spec v1.0)

> **Use this file as a template when opening a PR for these changes on a fork or feature branch.**
> Copy the body below into the GitHub PR description.

---

### Summary

This PR implements the "Markdown for control plane, HTML for presentation plane" rule as automated, auditable guardrails. Inspired by Anthropic's Claude Code shift to rich HTML for human-facing outputs, it adds a formal routing schema, a hardened sanitization middleware, and agent institutional memory that prevents rendering mistakes fleet-wide.

### Motivation

As AI agents generate longer, more complex outputs (code reviews, multi-step plans, research summaries), Markdown's linear format becomes a liability:

- Wall-of-text cognitive overload for humans reviewing agent plans
- No interactivity: no tabs, expand/collapse, inline diagrams, or colour-coded diffs
- Poor visual signalling of risk, relationships, or structural hierarchy

HTML unlocks rich presentation — but introduces token cost, XSS risk, and version-control noise if uncontrolled. This PR encodes the trade-offs as deterministic policy enforced at the pipeline layer, not via prompt engineering.

### What's Included

| File | Role |
|------|------|
| `docs/renderer_spec.md` | Renderer Specification v1.0: JSON Schema, CSP/nonce, pipeline integration |
| `docs/LESSON-html-shift.md` | Human-facing lesson: why Claude Code shifted to HTML |
| `docs/LESSONS-html-shift.md` | Agent institutional memory: DO NOT / PITFALLS / SUCCESS PATTERNS |
| `tools/csp_sanitizer.py` | Production middleware: allowlist sanitization + nonce-based CSP |
| `specs/renderer_test_suite.json` | 10 schema + 14 sanitizer test vectors (pytest-compatible) |
| `specs/html_tag_whitelist.yaml` | Standalone, auditable tag/attr allowlist for security reviews |

### Architecture Impact

Maps cleanly to the OpenClaw / NemoClaw 4-layer prevention architecture:

| Layer | Policy Hook |
|-------|------------|
| **State Detection** | Emit `recipient`, `complexity_score`, `requires_interactivity` on every response candidate |
| **Turn Policy** | Route to HTML iff `recipient=human` AND (`complexity_score >= 6` OR `requires_interactivity=true`) |
| **Friction Policy** | Fall back to Markdown if `estimated_tokens > max_token_budget` |
| **Guardrail Policy** | Sanitize all HTML via `csp_sanitizer.py`: allowlist tags/attrs, nonce-based CSP, `javascript:` blocking |

### Migration Guide

**Step 1 — Add routing stage to `openclaw.yaml`:**

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
```

**Step 2 — Register middleware in your API layer:**

```python
from tools.csp_sanitizer import apply_security_hardening

@app.post("/agent/output")
async def handler(request):
    raw_html = await render_html(request.data)
    return apply_security_hardening(raw_html)
```

**Step 3 — Update agent prompts to emit required routing fields:**

```
Always include in your response metadata:
{
  "recipient": "human" | "agent" | "system",
  "complexity_score": 1-10,
  "requires_interactivity": true | false,
  "rendering_constraints": { "max_token_budget": <int> }
}
```

### Testing

```bash
# Install dependencies
pip install pytest jsonschema beautifulsoup4 flask

# Run schema validation tests
python -m pytest tests/test_renderer.py::test_schema_cases -v

# Run sanitizer XSS tests
python -m pytest tests/test_renderer.py::test_sanitizer_cases -v

# Quick smoke test (schema)
echo '{"recipient":"human","complexity_score":7,"requires_interactivity":true,"rendering_constraints":{"max_token_budget":1000},"recommended_format":"html"}' | \
  python -m jsonschema -i - specs/renderer_decision_schema.json && echo "Schema valid"

# Quick smoke test (sanitizer)
python -c "
from tools.csp_sanitizer import sanitize
result = sanitize('<script>evil()</script><p>safe</p>')
assert '<script>' not in result['html']
assert 'nonce-' in result['csp']
print('Sanitizer OK')
"
```

### Security Notes

- All agent-generated HTML passes through `csp_sanitizer.py` before serving
- CSP header uses cryptographic nonce per response; `'unsafe-inline'` never enabled
- `<script>`, `<iframe>`, event handlers (`on*`), `javascript:`, `vbscript:`, and `data:text/html` URLs stripped unconditionally
- Allowlist is explicit: only tags/attrs defined in `specs/html_tag_whitelist.yaml` survive
- `X-Content-Type-Options: nosniff` and `X-Frame-Options: DENY` set on every response

### Breaking Changes

None. This is an additive layer; existing Markdown-only agents continue to work unchanged.

### Review Checklist

- [ ] Schema validation tests pass (`SCH-001` through `SCH-010`)
- [ ] Sanitizer blocks all XSS test vectors (`SAN-001` through `SAN-014`)
- [ ] CSP header present with nonce in all HTML responses
- [ ] Token budget fallback triggers when estimated tokens exceed `max_token_budget`
- [ ] Lesson files render correctly in GitHub preview
- [ ] `html_tag_whitelist.yaml` matches constants in `csp_sanitizer.py`

### Related

- [Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code)
- [I Gave My AI Agents a Single Markdown File — It Cut Recurring Mistakes to Zero](https://dev.to/jeremy_mandile_/i-gave-my-ai-agents-a-single-markdown-file-it-cut-recurring-mistakes-to-zero-2n47)
- [Renderer Specification v1.0](./renderer_spec.md)
- [Agent Institutional Memory for HTML outputs](./LESSONS-html-shift.md)

---

Ready for review. Once merged, the agent fleet automatically enforces:

> **Markdown for control. HTML for human eyes.**
