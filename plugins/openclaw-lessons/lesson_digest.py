"""
Weekly digest plugin for OpenClaw agents.

Counts entries in LESSONS.md and, when the active file exceeds
`max_entries`, moves the oldest entries (FIFO per section) to
LESSONS_ARCHIVE.md to keep the active file lean.
"""

import os
import re
from datetime import datetime


def _parse_sections(filepath):
    """Return {section_name: raw_content_str} for the three standard sections."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    sections = {}
    for name in ("DO NOT", "PITFALLS", "SUCCESS PATTERNS"):
        m = re.search(rf"^## {name}\n(.*?)(?=^## |\Z)", content, re.MULTILINE | re.DOTALL)
        sections[name] = m.group(1) if m else ""
    return sections


def _count_entries(section_content):
    return len(re.findall(r"^### ", section_content, re.MULTILINE))


def _split_entries(section_content):
    """Split section content into individual entry strings."""
    parts = re.split(r"\n(?=### )", section_content.strip())
    return [p for p in parts if p.strip()]


def compact(filepath, archive_path=None, max_entries=100):
    """Move oldest entries to archive when total exceeds max_entries.

    Args:
        filepath: Path to LESSONS.md.
        archive_path: Path to LESSONS_ARCHIVE.md (defaults to same directory).
        max_entries: Keep no more than this many entries total across all sections.

    Returns a dict with counts of archived entries per section.
    """
    if archive_path is None:
        archive_path = os.path.join(os.path.dirname(os.path.abspath(filepath)), "LESSONS_ARCHIVE.md")

    sections = _parse_sections(filepath)
    total = sum(_count_entries(v) for v in sections.values())

    if total <= max_entries:
        return {"status": "no compaction needed", "total_entries": total}

    budget_per_section = max_entries // 3
    archived_counts = {}
    archived_content = {}

    for name, content in sections.items():
        entries = _split_entries(content)
        if len(entries) > budget_per_section:
            overflow = entries[: len(entries) - budget_per_section]
            sections[name] = "\n".join(entries[len(entries) - budget_per_section :])
            archived_counts[name] = len(overflow)
            archived_content[name] = "\n".join(overflow)
        else:
            archived_counts[name] = 0

    # Write slimmed active file
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    for name, new_body in sections.items():
        if archived_counts.get(name, 0) > 0:
            raw = re.sub(
                rf"(## {name}\n).*?(?=^## |\Z)",
                lambda m, nb=new_body: m.group(1) + nb + "\n",
                raw,
                flags=re.MULTILINE | re.DOTALL,
            )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(raw)

    # Append to archive
    if any(v > 0 for v in archived_counts.values()):
        today = datetime.now().strftime("%Y-%m-%d")
        archive_block = f"\n<!-- Archived {today} -->\n"
        for name, content in archived_content.items():
            if content:
                archive_block += f"\n## {name}\n{content}\n"

        if os.path.exists(archive_path):
            with open(archive_path, "a", encoding="utf-8") as f:
                f.write(archive_block)
        else:
            with open(archive_path, "w", encoding="utf-8") as f:
                f.write(f"# Lessons Archive\n{archive_block}")

    return {
        "status": "compacted",
        "entries_before": total,
        "archived_by_section": archived_counts,
        "archive_file": archive_path,
    }


# OpenClaw hook interface
def weekly_digest(workspace_root="."):
    """Called by OpenClaw on a weekly schedule to compact LESSONS.md."""
    filepath = os.path.join(workspace_root, "LESSONS.md")
    if not os.path.exists(filepath):
        return {"status": "no LESSONS.md found"}
    return compact(filepath)
