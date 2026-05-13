# Real-World Multimodal Agent Workflows: A Practical Guide

A framework for designing workflows that combine deep reasoning, creative media, voice, APIs, and coding agents—with concrete examples, prompt patterns, and integration tips.

## The Workflow Design Framework

Every robust multimodal workflow follows this pattern:

```
[Trigger] → [Reasoning] → [Tool Selection] → [Execution] → [Output Assembly] → [Delivery]
```

| Stage | Purpose | Key Questions |
|-------|---------|--------------|
| **Trigger** | What starts the workflow? | User message? Scheduled job? API webhook? Voice command? |
| **Reasoning** | What does the agent need to figure out? | Intent? Context? Constraints? Required tools? |
| **Tool Selection** | Which capabilities are needed? | Image gen? Voice synthesis? API call? Code exec? Database query? |
| **Execution** | Run tools in parallel/sequence | Order dependencies? Error handling? Timeout limits? |
| **Output Assembly** | Combine results into coherent response | Format (HTML/Markdown)? Personalization? Safety checks? |
| **Delivery** | Get result to user | Channel (chat, email, voice, webhook)? Tracking? Feedback loop? |

## Real-World Examples

### Example 1: Sales Demo Generator (OpenClaw)

Goal: Turn a prospect's website URL into a personalized, multimodal sales demo.

```
[Trigger: Prospect URL + company name]
  → [Reasoning: Extract pain points from site]
  → [Tool Selection: Web scraper + LLM for insights + Image gen + Voice synthesis]
  → [Execution: 1. Scrape site 2. Generate value props 3. Create mockup images 4. Synthesize voiceover]
  → [Output Assembly: HTML with tabs — Insights / Mockups / Voice Demo]
  → [Delivery: Email + Slack notification to AE]
```

**Prompt Pattern for Reasoning Stage:**

```markdown
You are a sales strategist. Analyze this company's website and identify:
1. Their top 3 stated priorities (from homepage, about, blog)
2. Likely pain points our product solves
3. One personalized hook for an AE to use

Output format (strict JSON):
{
  "priorities": ["...", "...", "..."],
  "pain_points": ["...", "..."],
  "hook": "One-sentence personalized opener"
}
```

> **Integration Tip:** Use `renderer_spec.md` to route complex output to HTML (`recipient=human, complexity=8`), with CSP-hardened mockup embeds.

### Example 2: Marketing Content Engine

Goal: Turn a product brief into a full campaign: blog post, social graphics, video script, and voiceover.

```
[Trigger: Product brief + target audience]
  → [Reasoning: Map brief to content pillars]
  → [Tool Selection: LLM for blog + Image gen + Video script + Voice synthesis + Canva API]
  → [Execution: 1. Blog draft 2. 3 social image variants 3. 60-sec video script 4. Voiceover audio]
  → [Output Assembly: HTML campaign dashboard with tabs, download links, A/B test variant toggles]
  → [Delivery: Shared link + Slack bot notification]
```

> **Integration Tip:** Store each asset's generation prompt + parameters in `LESSONS.md` for reproducibility.

**Example lesson entry:**

```markdown
### SUCCESS: DALL-E prompt engineering for B2B tech
- **Why:** Vague prompts produce generic images; specific prompts produce on-brand assets.
- **Use instead:** Include brand colors, UI style, and audience context in image_prompt.
- **Tags:** #creative #image-gen #marketing #prompt-engineering
```

### Example 3: Voice-First Customer Support Agent

Goal: Handle a spoken support request end-to-end: transcribe → reason → act → respond in voice.

```
[Trigger: User speaks "My order hasn't arrived"]
  → [Reasoning: Classify intent + extract entities]
  → [Tool Selection: Whisper STT + LLM + Order API + Policy KB + Voice synthesis]
  → [Execution: 1. Transcribe 2. Classify intent 3. Query order API 4. Apply resolution policy 5. Generate response]
  → [Output Assembly: Voice response + Fallback text transcript + Agent handoff trigger]
  → [Delivery: Stream audio back to user + Log interaction]
```

> **Integration Tip:** Use `csp_sanitizer.py` to sanitize user-generated content rendered in follow-up HTML summaries for human agents.

### Example 4: Developer Copilot

Goal: Turn a feature request into working code, a live demo, and documentation.

```
[Trigger: "Add dark mode toggle to settings page"]
  → [Reasoning: Break down into subtasks]
  → [Tool Selection: Code LLM + Sandbox + Screenshot tool + Docs LLM + HTML renderer]
  → [Execution: 1. Generate component 2. Verify in sandbox 3. Capture screenshot 4. Write changelog]
  → [Output Assembly: Tabbed HTML — Code / Demo / Docs, colour-coded diff, "Copy code" button]
  → [Delivery: PR comment + Slack notification]
```

## Prompt Patterns

### Chain-of-Thought for Tool Selection

```markdown
Before selecting tools, reason step-by-step:
1. What is the user's core intent?
2. What information is missing?
3. Which tools can fill those gaps?
4. What's the optimal execution order?
5. What could go wrong, and how to handle it?
```

### Structured Output for Reliability

```markdown
Output format (strict JSON):
{
  "tool_calls": [
    { "tool": "name", "args": { ... }, "depends_on": ["previous_step_id"] }
  ],
  "fallback_plan": "What to do if a tool fails",
  "success_criteria": "How we'll know this worked"
}
```

### Personalization Without PII Leakage

```markdown
When personalizing output:
- Use first name only if explicitly provided
- Never echo back sensitive data (emails, IDs) in logs
- Mask PII in any rendered HTML with [REDACTED]
- Store full traces in secure vault, not in LESSONS.md
```

## Integration Patterns That Scale

### Pattern 1: The Renderer Gateway

Use `renderer_spec.md` as a central routing layer for all output:

```python
def route_output(metadata: dict, content: str) -> Response:
    if metadata["recommended_format"] == "html":
        html = compile_to_html(content)
        return apply_security_hardening(html)
    return compile_to_markdown(content)
```

### Pattern 2: Lesson-Driven Tool Selection

Store tool usage patterns in `LESSONS.md`. Agents load via grep to improve decisions over time—no embeddings, no fine-tuning.

### Pattern 3: Fallback Chains for Reliability

```yaml
tool_execution:
  primary: "dalle-3"
  fallbacks: ["midjourney-api", "placeholder-image"]
  timeout_seconds: 30
  retry_count: 2
```

### Pattern 4: Audit Logging Without PII

```python
# Good: log actions, not data
log_event({
    "action": "image_generated",
    "tool": "dalle-3",
    "prompt_hash": sha256(prompt),
    "user_id_hash": sha256(user_id)
})
```

## md-knowledge-format Contracts

| Artifact | Purpose |
|----------|---------|
| `LESSON.md` | Human-readable patterns |
| `LESSONS.md` | Agent-loadable rules |
| `renderer_spec.md` | Deterministic output routing |
| `csp_sanitizer.py` | Secure delivery |

Start small. Chain two tools. Log one lesson. Iterate.
