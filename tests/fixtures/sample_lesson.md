---
lesson_version: 1
agent_id: test-agent
session_id: 2024-01-15T09:30:00Z
topic: Python error handling
related_lessons: []
---

# LESSON: Never Use Bare Except in Tool Calls

## What happened

During a tool-calling loop, used `except:` without specifying the exception
type. This swallowed a `KeyboardInterrupt` during a long-running operation,
causing the process to hang indefinitely and require a forced kill.

The bare except caught *everything*, including system signals that should
have propagated up.

## Root cause

Copied a code pattern from a quick example without considering the
implications of catching all exceptions indiscriminately.

## Fix

Always use `except Exception as e:` at minimum. For tool calls that
may receive signals, use even more specific exception types.

```python
# BAD — never do this
try:
    result = tool.call(payload)
except:
    logger.error("Tool failed")
    return None

# GOOD — catch what you expect
try:
    result = tool.call(payload)
except ToolTimeoutError as e:
    logger.warning("Tool timed out: %s", e)
    return None
except Exception as e:
    logger.error("Unexpected tool failure: %s", e)
    raise
```

## Tags

`python`, `error-handling`, `tool-calls`, `reliability`

## Severity

high — bare except can mask critical system errors and cause hangs

## Verified fix

yes — confirmed in session 2024-01-16 that explicit exception types
prevent signal swallowing
