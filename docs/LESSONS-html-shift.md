---
lessons_version: "1.0"
created: "2026-05-12"
project: "any-agent-system-with-human-facing-outputs"
---

# Lessons Learned

## DO NOT

### DO NOT use Markdown for complex human-facing outputs when visual structure or interactivity is needed

- **Why:** Markdown produces a "wall of text" for outputs longer than ~200 lines or containing multiple data facets. Human comprehension degrades; decisions slow down.
- **Use instead:** Generate an HTML artifact that uses colour-coded diffs, tabs, inline SVGs, or expandable sections to present the same information compactly and interactively.
- **First seen:** 2025 (Anthropic Claude Code shift), documented 2026-05-12
- **Tags:** #html #human-facing #readability #interactive

### DO NOT hardcode interactive HTML without a Content Security Policy (CSP)

- **Why:** Agent-generated HTML can introduce XSS vectors if it ever includes unsanitised user input. A single injection can compromise the user's browser.
- **Use instead:** Serve agent HTML inside a sandboxed `<iframe>` with a strict CSP (`sandbox="allow-scripts allow-same-origin"`) and no `unsafe-inline` unless absolutely necessary. Sanitise all dynamic content.
- **First seen:** 2025 (Claude Code launch discussions), documented 2026-05-12
- **Tags:** #html #security #xss #csp

### DO NOT store generated HTML as the primary artifact for agent output history

- **Why:** HTML is verbose and structurally noisy, making line-by-line diffs nearly unreadable in version control.
- **Use instead:** Store the **source data** (Markdown, JSON, or structured dict) that describes the output. Generate the HTML on demand.
- **First seen:** 2026-05-12 (agent fleet infrastructure)
- **Tags:** #html #version-control #diffs #storage

## PITFALLS

### Token usage explodes when every reply is HTML

- **What happens:** A 500-line Markdown report becomes 1,200 lines of HTML. Cost and latency increase by 2-3x.
- **Fix:** Adopt **progressive rendering** — stream the semantic skeleton first, then enhance with interactivity only as the user interacts. Use compact semantic elements (`<details>`, `<summary>`) instead of heavy `<div>` wrappers.
- **Context:** Any agent that generates HTML for human consumption in real-time.
- **Tags:** #html #tokens #performance #streaming

### "Rich HTML" encourages scope creep — agents try to build full apps

- **What happens:** An agent told "use HTML for better output" starts embedding complex JavaScript, external fonts, or third-party libraries. Output becomes unpredictable.
- **Fix:** Constrain the agent's HTML palette to a predefined allowlist of tags. Validate outputs against this whitelist before rendering.
- **Context:** Autonomous coding agents that generate human-facing reports.
- **Tags:** #html #scope-creep #constraints #validation

### HTML output breaks the "diffable" property that makes agent progress reviewable

- **What happens:** A human reviewer compares two HTML versions and sees hundreds of changed CSS class names — not the actual content changes.
- **Fix:** Always maintain a canonical, diff-friendly intermediate representation alongside the final HTML. The reviewer compares the intermediate representation, not the rendered HTML.
- **Context:** Code-review workflows, audit trails, and team collaboration.
- **Tags:** #html #diffs #audit #review

## SUCCESS PATTERNS

### Treat HTML as a compiled "presentation plane" artifact, not the source of truth

- **Result:** Clean separation of concerns: agents learn from Markdown (LESSONS.md), produce data in structured formats, and render to HTML only for human display.
- **How:** Define a "render" step that takes a structured output object and converts it to HTML using a fixed, version-controlled template.
- **Tags:** #architecture #separation-of-concerns #html #markdown

### Use HTML's interactivity to keep humans "in the loop" on complex decisions

- **Result:** Humans understand agent plans faster, catch errors earlier, and trust the system more.
- **How:** When an agent proposes a multi-step plan, render it as an HTML page with **tabs** for each phase, an **SVG flowchart**, and colour-coded risk indicators. Let the human click to approve each phase.
- **Tags:** #interactivity #trust #human-in-the-loop

### Apply the "grep test" to agent memory, not to generated HTML

- **Result:** Agent lessons remain instantly searchable with ripgrep, while the rich HTML output remains a disposable, on-the-fly rendering.
- **How:** Store all lessons, rules, and patterns in LESSONS.md (plain Markdown). Never store them inside HTML templates. The agent reads LESSONS.md before generating any user-facing artifact.
- **Tags:** #retrieval #grep #memory #lessons

### Block javascript: and data: URLs in all href and src attributes

- **Result:** Eliminates a common XSS vector in agent-generated HTML even after tag/attr allowlisting.
- **How:** In the sanitizer, strip any attribute value that starts with `javascript:` or `data:` (unless data URIs are explicitly required for images).
- **Tags:** #security #xss #sanitizer #url-escaping
