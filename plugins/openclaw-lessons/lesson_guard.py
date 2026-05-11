"""
Pre-action guard plugin for OpenClaw agents.

Reads LESSONS.md before every non-trivial tool call. If a DO NOT entry
matches the planned action (via tag overlap), the action is blocked and
the safe alternative is substituted.
"""

import os
import re


def _find_lessons_file(workspace_root="."):
    path = os.path.join(workspace_root, "LESSONS.md")
    return path if os.path.exists(path) else None


def _parse_do_not_entries(filepath):
    """Return a list of DO NOT entries as dicts (description, alternative, tags)."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    section_match = re.search(
        r"^## DO NOT\n(.*?)(?=^## |\Z)", content, re.MULTILINE | re.DOTALL
    )
    if not section_match:
        return []

    entries = []
    for m in re.finditer(
        r"### DO NOT (.+?)\n(.*?)(?=### DO NOT |\Z)",
        section_match.group(1),
        re.MULTILINE | re.DOTALL,
    ):
        details = m.group(2)
        alt = re.search(r"\*\*Use instead:\*\*\s+(.+)", details)
        tags_match = re.search(r"\*\*Tags:\*\*\s+(.+)", details)
        entries.append(
            {
                "description": m.group(1).strip(),
                "alternative": alt.group(1).strip() if alt else None,
                "tags": tags_match.group(1).split() if tags_match else [],
            }
        )
    return entries


def _tags_from_action(action_description):
    """Extract candidate tags from an action description string."""
    tags = set()
    tags.update(re.findall(r"`([a-zA-Z_][a-zA-Z0-9_.]*)`", action_description))
    tags.update(re.findall(r"#(\w+)", action_description))
    for keyword in ("sql", "pdf", "http", "api", "database", "container", "font", "unicode"):
        if keyword in action_description.lower():
            tags.add(keyword)
    return tags


def guard(action_description, workspace_root="."):
    """Check an action description against LESSONS.md DO NOT entries.

    Returns a dict:
        blocked (bool), reason (str), alternative (str | None)
    """
    path = _find_lessons_file(workspace_root)
    if not path:
        return {"blocked": False, "reason": "No LESSONS.md found.", "alternative": None}

    action_tags = _tags_from_action(action_description)
    for entry in _parse_do_not_entries(path):
        entry_tags = {t.strip("#") for t in entry["tags"]}
        overlap = action_tags & entry_tags
        if overlap:
            return {
                "blocked": True,
                "reason": f"DO NOT matched: {entry['description']} (overlap: {overlap})",
                "alternative": entry["alternative"],
            }

    return {"blocked": False, "reason": "No matching DO NOT entries.", "alternative": None}


# OpenClaw hook interface
def pre_tool_call(action):
    """Called by OpenClaw before the agent executes a tool.

    Mutates the action dict in-place: sets blocked=True and rewrites
    the description to the safe alternative when a DO NOT entry fires.
    """
    result = guard(action.get("description", ""))
    if result["blocked"]:
        action["blocked"] = True
        action["block_reason"] = result["reason"]
        if result["alternative"]:
            action["description"] = result["alternative"]
            action["rewritten"] = True
    return action
