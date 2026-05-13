"""Parse Markdown constraint files into a raw list of constraint text items."""
from pathlib import Path
from typing import List, Dict


def parse_markdown_constraints(file_path: Path) -> List[Dict[str, str]]:
    """
    Extract constraints from a markdown file.
    Returns list of dicts with keys: 'text', 'line', 'section'
    """
    constraints = []
    if not file_path.exists():
        return constraints

    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    current_section = "unknown"
    in_constraint = False
    constraint_lines = []
    start_line = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped.startswith('## ') or stripped.startswith('# '):
            current_section = stripped.lstrip('#').strip()

        if stripped.startswith('- **') or stripped.startswith('* **'):
            in_constraint = True
            constraint_lines = [stripped]
            start_line = i + 1
        elif stripped.startswith('### '):
            in_constraint = True
            constraint_lines = [stripped]
            start_line = i + 1
        elif in_constraint and stripped == '':
            constraints.append({
                'text': '\n'.join(constraint_lines),
                'line': start_line,
                'section': current_section
            })
            in_constraint = False
            constraint_lines = []
        elif in_constraint and (stripped.startswith('#') or stripped.startswith('---')):
            constraints.append({
                'text': '\n'.join(constraint_lines),
                'line': start_line,
                'section': current_section
            })
            in_constraint = False
            constraint_lines = []
        elif in_constraint:
            constraint_lines.append(stripped)

    if in_constraint and constraint_lines:
        constraints.append({
            'text': '\n'.join(constraint_lines),
            'line': start_line,
            'section': current_section
        })

    return constraints
