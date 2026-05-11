# md-knowledge-format

**A family of Markdown-based standards for portable, machine-readable knowledge files.**

Two formats. One philosophy: *just a file.*

| Format | Teaches | Audience |
|---|---|---|
| **LESSON.md** | A programming-language lesson | Humans (learners, LMSs, IDEs) |
| **LESSONS.md** | Hard-won operational experience | AI agents and the teams that run them |

Both use YAML front matter + Markdown body. Both are human-readable, version-controlled, and require zero infrastructure beyond a text editor.

---

## LESSON.md — Portable Programming Lessons

LESSON.md is a spec for encoding a single programming-language lesson in a way that any tutorial platform, IDE, or LMS can consume without conversion.

**Required front matter:**

```yaml
---
lessond_version: "1.0"
title: "Python Loops: for and while"
language: "Python"
difficulty: "beginner"
topics: ["loops", "iteration", "control-flow"]
prerequisites: ["Python variables", "Python conditions"]
objectives:
  - Write a for loop to iterate over a list
  - Use while loops with a condition
created: "2025-01-01"
---
```

**Recommended body sections:** Learning Objectives · Prerequisites · Content · Exercises · Further Reading

Full spec: [`spec/LESSON.md-spec.md`](spec/LESSON.md-spec.md)  
Example: [`examples/python-loops.lesson.md`](examples/python-loops.lesson.md)

---

## LESSONS.md — Agent Institutional Memory

LESSONS.md is a living, file-based memory for autonomous AI agents. It answers one question: *how do we stop independent agents from repeating the same mistakes?*

The answer: give them a file they already know how to read.

```markdown
## DO NOT
### DO NOT use `pandas.DataFrame.append`
- **Why:** Deprecated in pandas 1.4.0, removed in 2.0.
- **Use instead:** `pd.concat()`
- **Tags:** #pandas #deprecation

## PITFALLS
### `datetime.now()` is not timezone-aware in containers
- **Fix:** Use `datetime.now(timezone.utc)`
- **Tags:** #python #timezone

## SUCCESS PATTERNS
### Chain-of-draft reasoning before writing >50 lines of code
- **Result:** Reduced review cycles by ~30 %.
- **Tags:** #process #code-gen
```

**How it works in practice:**

1. **Pre-action guard** — before executing a non-trivial task, the agent reads LESSONS.md. A matching `DO NOT` entry causes an immediate stop and substitution of the safe alternative.
2. **Post-failure write-back** — when a mistake occurs, the agent (or a human) appends a new entry. A PR is opened; after auto-merge, every agent in the fleet learns the lesson.
3. **Retrieval is just grep** — tag matching via ripgrep. No vector DB, no embeddings, near-zero latency.

Real-world result: after six months of use, a fleet of OpenClaw agents went from ~12 recurring mistake classes per month to zero of those same classes repeating.

Full spec: [`spec/LESSONS.md-spec.md`](spec/LESSONS.md-spec.md)  
Starter template: [`examples/starter.lessons.md`](examples/starter.lessons.md)

---

## Tooling

### CLI — `lesson_tool.py`

[`tools/lesson_tool.py`](tools/lesson_tool.py) is a single-file Python 3.6+ CLI for both formats. Zero mandatory dependencies.

```bash
# Create a new LESSON.md interactively
python tools/lesson_tool.py scaffold my-lesson.lesson.md

# Or with flags for automation
python tools/lesson_tool.py scaffold my-lesson.lesson.md \
  --title "Python Loops" --language Python --difficulty beginner \
  --topics "loops,iteration" --objectives "Write a for loop,Use while loops"

# Validate a LESSON.md
python tools/lesson_tool.py validate my-lesson.lesson.md

# Export to HTML
python tools/lesson_tool.py html my-lesson.lesson.md > lesson.html

# Create a LESSONS.md agent-memory file
python tools/lesson_tool.py init-memory LESSONS.md
```

### Docker

No Python on the host? Run the CLI in a container:

```bash
docker build -t md-knowledge-format tools/
docker run --rm -v $(pwd):/workspace md-knowledge-format validate my-lesson.lesson.md
docker run --rm -v $(pwd):/workspace md-knowledge-format html my-lesson.lesson.md > lesson.html
docker run --rm -v $(pwd):/workspace md-knowledge-format init-memory LESSONS.md
```

### OpenClaw Plugins — One-Click Install

Give your OpenClaw agent swarm shared institutional memory in one command:

```bash
npm install @md-knowledge-format/openclaw-lessons
```

Then add to `openclaw.yaml`:

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

**What you get:** agents auto-abort dangerous actions, mistakes are captured and shared fleet-wide, and weekly cleanup keeps the memory file lean. [Plugin docs →](plugins/openclaw-lessons/README.md)

**Optional Python dependencies for enhanced output:**

```bash
pip install pyyaml markdown
```

---

## Repository layout

```
/README.md                       ← you are here
/spec/
  LESSON.md-spec.md              ← LESSON.md format specification v1.0
  LESSONS.md-spec.md             ← LESSONS.md format specification v1.0
/tools/
  lesson_tool.py                 ← unified CLI for both formats
/examples/
  python-loops.lesson.md         ← sample LESSON.md file
  starter.lessons.md             ← starter LESSONS.md template
```

---

## Why "just a file" wins

- **Zero latency.** No API round-trip to retrieve a lesson or a memory entry.
- **Human-auditable.** Open the file and immediately understand what your agents are avoiding and why.
- **Version-controlled.** Git blame shows who added a lesson and when. Rollback is a revert.
- **Framework-agnostic.** LESSONS.md works with any agent framework that can read a file.
- **No prompt rot.** Your main system prompt stays clean. Urgant, context-specific rules live in LESSONS.md and age out naturally.

---

## Contributing

Suggestions for the spec, new tool commands, or additional examples are welcome via issues and pull requests.

## License

MIT
