"""
Post-failure reporter plugin for OpenClaw agents.

When an action fails (or a human flags output as incorrect), this plugin
formats a new DO NOT entry and appends it to LESSONS.md.
"""

import os
import re
from datetime import datetime


_ENTRY_TEMPLATE = """\
### DO NOT {description}
- **Why:** {why}
- **Use instead:** {alternative}
- **First seen:** {date} (agent: {agent_name})
- **Tags:** {tags}

"""


def format_entry(description, why, alternative, agent_name="unknown", tags=None, date=None):
    """Format a new DO NOT entry string."""
    return _ENTRY_TEMPLATE.format(
        description=description,
        why=why,
        alternative=alternative,
        date=date or datetime.now().strftime("%Y-%m-%d"),
        agent_name=agent_name,
        tags=" ".join(f"#{t.strip('#')}" for t in (tags or [])),
    )


def append_entry(entry, workspace_root="."):
    """Insert a new entry into the DO NOT section of LESSONS.md.

    Creates the file if it does not exist. Returns the file path.
    """
    filepath = os.path.join(workspace_root, "LESSONS.md")

    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(
                f'---\nlessons_version: "1.0"\ncreated: "{datetime.now().strftime("%Y-%m-%d")}"\n---\n\n'
                f"# Lessons Learned\n\n## DO NOT\n{entry}\n## PITFALLS\n\n## SUCCESS PATTERNS\n"
            )
        return filepath

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    insertion = content.find("## PITFALLS")
    if insertion == -1:
        content += "\n" + entry
    else:
        content = content[:insertion] + entry + content[insertion:]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath


# OpenClaw hook interface
def post_failure(failure_context):
    """Called by OpenClaw when an agent action fails.

    Args:
        failure_context: dict with keys —
            agent_name, action_description, error_message,
            suggested_fix (optional), workspace_root (optional)

    Returns a dict describing the action taken.
    """
    action = failure_context.get("action_description", "")
    error = failure_context.get("error_message", "")
    workspace = failure_context.get("workspace_root", ".")

    tags = set(re.findall(r"`([a-zA-Z_][a-zA-Z0-9_.]*)`", action))
    for kw in ("sql", "pdf", "font", "unicode", "api", "container"):
        if kw in action.lower():
            tags.add(kw)

    entry = format_entry(
        description=action[:100],
        why=error[:200],
        alternative=failure_context.get("suggested_fix") or "Investigate and apply the correct approach",
        agent_name=failure_context.get("agent_name", "unknown"),
        tags=list(tags),
    )

    filepath = append_entry(entry, workspace)
    return {"entry_added": True, "file": filepath, "entry": entry}
