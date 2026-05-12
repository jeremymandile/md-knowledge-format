# md-knowledge-format Agent Demo

A runnable example showing an AI agent using the md-knowledge-format system end-to-end.

## What This Demonstrates

1. **Deterministic routing** — agent emits metadata → schema validates HTML vs Markdown decision
2. **Lesson-aware generation** — agent checks LESSONS.md via grep and avoids documented mistakes
3. **Security hardening** — HTML outputs pass through `csp_sanitizer.py` for CSP + sanitization
4. **Lesson propagation** — mistake → lesson added → next session avoids repeat (no fine-tuning)
5. **Token budget fallback** — when HTML would exceed budget, pipeline falls back to Markdown

## Prerequisites

```bash
# Python 3.10+
python --version

# Install dependencies (from repo root)
pip install -r requirements-test.txt
```

## Run the Demo

```bash
# From repo root:
python examples/agent_demo/run_demo.py
```

### Expected Output

```
md-knowledge-format Agent Demo
==================================================
Loaded 3 DO NOT rules from LESSONS.md

Demo 1: Human recipient, high complexity -> HTML
--------------------------------------------------
Schema validated: format = html
Generated html output (412 chars)
Sanitized: CSP nonce present = True
Saved to examples/agent_demo/output/sample_output.html

Demo 2: Lesson propagation -- mistake -> lesson -> avoidance
--------------------------------------------------
Session 1: Violations found = 0 (no lessons loaded yet)
Human added lesson: 'DO NOT embed <script> tags'
Session 2: Violations found = 1 (lesson loaded via grep)
Output revised: <script> removed = True

Demo 3: Token budget enforcement -> fallback to Markdown
--------------------------------------------------
Budget exceeded (1500 > 1000)
Fallback: format = markdown

==================================================
Demo complete. Key takeaways:
  * Schema enforces deterministic routing
  * Lessons propagate via grep, not embeddings
  * Sanitizer hardens every HTML response
  * Token budget fallback controls costs
```

## Files

```
examples/agent_demo/
├── agent.py              # KnowledgeAwareAgent — the reference implementation
├── run_demo.py           # Entry point: runs the full workflow
├── config/
│   └── pipeline.yaml     # Stage configuration for OpenClaw/NemoClaw
├── output/               # Generated artifacts (created on first run)
│   └── sample_output.html
└── README.md             # This file
```

## Integrate Into Your Pipeline

See `config/pipeline.yaml` for the full stage configuration. To drop into OpenClaw/NemoClaw:

```yaml
include:
  - path: examples/agent_demo/config/pipeline.yaml
    stages: [metadata_emission, schema_validation, lesson_check, rendering, security_hardening]
```

## Extend the Example

### Add a New Lesson

Edit `docs/LESSONS-html-shift.md`:

```markdown
### DO NOT use inline <style> without CSP nonce
- Why: CSS injection risk; violates content security policy.
- Use instead: Inject nonce via middleware; allow only nonce-bearing styles.
- Tags: #security #csp #html
```

The agent will automatically respect this on the next run — no code changes required.

### Add a New XSS Test Vector

Edit `tests/security/test_xss_vectors.json`, then run:

```bash
pytest tests/security/ -v
```

## Learn More

- [Renderer Specification](../../docs/renderer_spec.md)
- [LESSONS.md Format](../../docs/LESSONS-html-shift.md)
- [CSP Sanitizer Source](../../tools/csp_sanitizer.py)
- [Test Suite](../../tests/)

---

> The power isn't in the code — it's in the contract.
> md-knowledge-format turns agent wisdom into versioned, grep-friendly files that compound over time.
