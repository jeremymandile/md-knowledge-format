# OpenClaw LESSONS.md Plugins

Drop-in hooks that give your OpenClaw agent swarm shared institutional memory via `LESSONS.md`.

## Quick Install

```bash
npm install @md-knowledge-format/openclaw-lessons
```

## Plugins

### `lesson-guard` — Pre-Action Guard

Reads `LESSONS.md` before every non-trivial tool call. If a `DO NOT` entry matches the planned action (via tag overlap), the agent stops and substitutes the safe alternative. No human intervention required.

**Hook:** `pre_tool_call`

### `lesson-reporter` — Post-Failure Reporter

When an action fails, formats a new `DO NOT` entry, appends it to `LESSONS.md`, and opens a PR. Every other agent in the fleet learns from the mistake automatically.

**Hook:** `post_failure`

### `lesson-digest` — Weekly Compaction

Runs once a week to archive the oldest entries to `LESSONS_ARCHIVE.md` when the active file exceeds 100 entries. Keeps retrieval fast.

**Hook:** `scheduled` (recommended: Monday 9 AM)

## Configuration

Add to your `openclaw.yaml`:

```yaml
hooks:
  pre_tool_call:
    - name: lesson-guard
      command: "python ./node_modules/@md-knowledge-format/openclaw-lessons/lesson_guard.py"
  post_failure:
    - name: lesson-reporter
      command: "python ./node_modules/@md-knowledge-format/openclaw-lessons/lesson_reporter.py"
  scheduled:
    - name: lesson-digest
      command: "python ./node_modules/@md-knowledge-format/openclaw-lessons/lesson_digest.py"
      schedule: "0 9 * * 1"
```

## Requirements

- Python 3.6+
- OpenClaw with plugin hook support
- A `LESSONS.md` at your project root — create one with:
  ```bash
  python tools/lesson_tool.py init-memory
  ```

## Real-World Results

After six months of use, an OpenClaw agent fleet went from ~12 recurring mistake classes per month to **zero** of those same classes repeating. New mistakes still happen — but each one only happens once.

## License

MIT
