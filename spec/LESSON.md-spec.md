# LESSON.md Specification — v1.0

A LESSON.md file is a Markdown document with a YAML front matter block that encodes a single programming-language lesson in a portable, machine-readable format.

## File naming

`<slug>.lesson.md` or simply `LESSON.md` at a project root.

## Structure

```
---
<YAML front matter>
---

<Markdown body>
```

## Required front matter fields

| Field | Type | Description |
|---|---|---|
| `lessond_version` | string | Spec version — currently `"1.0"` |
| `title` | string | Human-readable lesson title |
| `language` | string | Programming language (e.g. `"Python"`) |
| `difficulty` | string | One of `beginner`, `intermediate`, `advanced` |
| `topics` | list of strings | Tags describing lesson content |
| `prerequisites` | list of strings | Required prior knowledge |
| `objectives` | list of strings | What the learner can do after completing the lesson |

### Optional front matter fields

| Field | Type | Description |
|---|---|---|
| `created` | string | ISO 8601 date (`YYYY-MM-DD`) |
| `author` | string | Author name or handle |
| `license` | string | Content license (e.g. `"CC BY 4.0"`) |

## Recommended body sections

All sections are optional but encouraged for interoperability:

- `## Learning Objectives`
- `## Prerequisites`
- `## Content`
- `## Exercises`
- `## Further Reading`

## Code blocks

Always use fenced code blocks with a language identifier:

````markdown
```python
print("hello")
```
````

Blocks without a language identifier will trigger a warning from `lesson_tool.py validate`.

## Validation

Use the bundled tool:

```bash
python tools/lesson_tool.py validate path/to/file.lesson.md
```
