---
lesson_version: 1
agent_id: test-fleet
format: lessons-collection
---

## L001 — Never use bare except in tool calls

tags: [python, error-handling, tool-calls]
severity: high
session: 2024-01-15T09:30:00Z
agent: agent-alpha

Used `except:` without specifying exception type. Swallowed a
`KeyboardInterrupt` and caused the process to hang indefinitely.

Rule: Always use `except Exception as e:` or a specific exception type.
Never use bare `except:` in production tool code.

## L002 — Check API rate limits before bulk operations

tags: [api, rate-limiting, reliability]
severity: medium
session: 2024-01-16T14:00:00Z
agent: agent-alpha

Called external API 1000x in a loop without rate limiting.
Hit 429 errors after ~100 calls. Entire batch failed.

Rule: Implement exponential backoff and respect Retry-After headers.
Check rate limit headers before starting bulk operations.

## L003 — Validate YAML front matter before processing

tags: [yaml, validation, lessons-format]
severity: low
session: 2024-01-17T10:15:00Z
agent: agent-beta

Attempted to read `lesson_version` from a LESSONS.md file that had
a typo: `lessond_version` (extra 'd'). Silently used default version.

Rule: Always validate required front matter fields explicitly.
Do not silently fall back to defaults for required schema fields.

## L004 — Use allow_external_scripts: false in production

tags: [security, configuration, yaml]
severity: high
session: 2024-01-18T09:00:00Z
agent: agent-gamma

Pipeline config had `allow_external_scripts: true` in a production
environment. This created an arbitrary code execution risk.

Rule: `allow_external_scripts` MUST be `false` in production.
Only set `true` in sandboxed development environments with explicit approval.

## L005 — Token budget: grep first, full load second

tags: [performance, token-budget, lessons-format]
severity: medium
session: 2024-01-19T11:30:00Z
agent: agent-delta

Loaded entire LESSONS.md into context window on every call.
For a 500-lesson file, this consumed ~8,000 tokens before any task work.

Rule: When token budget < 1000, use grep to find relevant lessons by tag.
Only load full LESSONS.md if the grep returns 0 results.
