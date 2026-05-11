# LESSONS.md Specification — v1.0

A LESSONS.md file is an agent-readable Markdown document that stores a project's institutional memory: hard blocks, context-dependent pitfalls, and proven success patterns. Any AI agent that can read a file can use it.

## File naming

`LESSONS.md` at the root of a project repository.

## Structure

```
---
<YAML front matter>
---

# Lessons Learned

## DO NOT
...

## PITFALLS
...

## SUCCESS PATTERNS
...
```

## Front matter fields

| Field | Type | Description |
|---|---|---|
| `lessons_version` | string | Spec version — currently `"1.0"` |
| `created` | string | ISO 8601 date |
| `project` | string | Project or repository name |

## Sections

### DO NOT

Hard blocks. If an agent's planned action matches an entry here, it must **stop and apply the alternative**.

Entry format:

```markdown
### DO NOT <short description of the forbidden action>
- **Why:** <reason>
- **Use instead:** <safe alternative>
- **First seen:** YYYY-MM-DD (agent: <name>)
- **Tags:** #tag1 #tag2
```

### PITFALLS

Context-dependent mistakes. The agent should note the risk and explicitly justify any deviation.

Entry format:

```markdown
### <short description of the pitfall>
- **What happens:** <consequence>
- **Fix:** <correction>
- **Context:** <when this applies>
- **Tags:** #tag1 #tag2
```

### SUCCESS PATTERNS

Techniques that have worked well. Agents are encouraged to apply these proactively.

Entry format:

```markdown
### <short description of the pattern>
- **Result:** <observed outcome>
- **How:** <how to apply it>
- **Tags:** #tag1 #tag2
```

## Retrieval

Agents do not need semantic search. Tag matching and section scanning with standard tools (grep/ripgrep) is sufficient:

```bash
grep "#pandas" LESSONS.md
```

## Maintenance

When the active file exceeds ~100 entries, move rarely-triggered entries to `LESSONS_ARCHIVE.md` and keep the active file lean.

## Scaffold

```bash
python tools/lesson_tool.py init-memory LESSONS.md
```
