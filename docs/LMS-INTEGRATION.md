# LMS Integration Guide for LESSON.md

How to ingest, validate, and serve LESSON.md files inside any Learning Management System.

---

## Overview

LESSON.md files are plain Markdown with YAML front matter. Any LMS can consume them with three steps:

1. **Parse** the front matter for metadata (title, language, difficulty, topics, objectives).
2. **Render** the Markdown body to HTML (with syntax highlighting for code blocks).
3. **Validate** lessons on upload to catch errors before learners see them.

---

## Backend Ingestion

### Python (FastAPI / Django / Flask)

```python
import sys
sys.path.append("path/to/md-knowledge-format/tools")
from lesson_tool import parse_frontmatter, validate_lesson

def ingest_lesson(filepath: str) -> dict:
    if not validate_lesson(filepath):
        raise ValueError(f"Invalid LESSON.md: {filepath}")
    meta, body = parse_frontmatter(filepath)
    return {
        "title": meta["title"],
        "language": meta["language"],
        "difficulty": meta["difficulty"],
        "topics": meta["topics"],
        "prerequisites": meta["prerequisites"],
        "objectives": meta["objectives"],
        "body_markdown": body,
        "created": meta.get("created"),
        "version": meta.get("lessond_version", "1.0"),
    }
```

### JavaScript / Node.js

```javascript
import { readFileSync } from "fs";
import matter from "gray-matter"; // npm install gray-matter

function parseLesson(filepath) {
  const { data, content } = matter(readFileSync(filepath, "utf-8"));
  const required = ["title", "language", "difficulty", "topics", "prerequisites", "objectives"];
  for (const field of required) {
    if (!data[field]) throw new Error(`Missing required field: ${field}`);
  }
  return { meta: data, body: content };
}
```

---

## Frontend Rendering

### Option A: Client-side Markdown

```html
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script>
  fetch("/api/lessons/python-loops")
    .then(r => r.json())
    .then(lesson => {
      document.getElementById("title").innerText = lesson.title;
      document.getElementById("body").innerHTML = marked.parse(lesson.body_markdown);
    });
</script>
```

### Option B: Server-side with syntax highlighting

```python
import markdown

md = markdown.Markdown(extensions=["fenced_code", "codehilite"])
html_body = md.convert(body)
```

---

## Upload Validation

Run the CLI validator on every uploaded file:

```bash
python tools/lesson_tool.py validate uploaded-file.lesson.md
# Exit 0 = valid, non-zero = invalid
```

Or embed it:

```python
from lesson_tool import validate_lesson

if not validate_lesson("new_lesson.lesson.md"):
    reject_upload("Lesson failed validation. Check required fields and code blocks.")
```

---

## Catalogue & Discovery

Index the front matter in your database and expose filters by language, difficulty, and topic:

```sql
INSERT INTO lessons (title, language, difficulty, topics, objectives, filepath)
VALUES (:title, :language, :difficulty, ARRAY[:topics], ARRAY[:objectives], :filepath);
```

---

## SCORM / xAPI Compatibility

**SCORM:** Render the lesson to a standalone HTML page, then bundle it with an `imsmanifest.xml`:

```bash
python tools/lesson_tool.py html lesson.lesson.md > scorm-package/index.html
```

**xAPI:** Use front matter fields as context extensions in your statement:

```json
{
  "verb": {"id": "http://adlnet.gov/expapi/verbs/completed"},
  "object": {
    "id": "https://your-lms/lessons/python-loops",
    "definition": {
      "name": {"en-US": "Python Loops: for and while"},
      "extensions": {
        "https://md-knowledge-format/spec/v1.0/language": "Python",
        "https://md-knowledge-format/spec/v1.0/difficulty": "beginner",
        "https://md-knowledge-format/spec/v1.0/topics": ["loops", "iteration"]
      }
    }
  }
}
```

---

## LLM Ingestion

Feed a LESSON.md directly into an LLM prompt:

```python
def lesson_to_prompt(filepath: str) -> str:
    meta, body = parse_frontmatter(filepath)
    return (
        f"You are teaching a {meta['difficulty']} {meta['language']} lesson.\n\n"
        f"Title: {meta['title']}\n"
        f"Topics: {', '.join(meta['topics'])}\n"
        f"Objectives: {', '.join(meta['objectives'])}\n\n"
        f"Lesson content:\n{body}\n\n"
        "Based on this lesson, generate three practice exercises."
    )
```

---

## Summary

| LMS Capability | How LESSON.md Enables It |
|---|---|
| Structured metadata | YAML front matter — parse once, index forever |
| Rich content | Standard Markdown with fenced code blocks |
| Syntax highlighting | Language identifiers on every code block |
| Upload validation | `validate_lesson()` catches errors pre-publish |
| Course catalogue | Filter by language, difficulty, topics |
| SCORM / xAPI export | Render to HTML, bundle with manifest |
| LLM integration | Feed directly into prompt context |

No conversion scripts, no vendor lock-in. Just a file.
