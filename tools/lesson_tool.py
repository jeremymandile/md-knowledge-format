#!/usr/bin/env python3
"""
LESSON.md / LESSONS.md Authoring & Memory Tool
----------------------------------------------
Unified CLI for the LESSON.md lesson format and the LESSONS.md agent-memory file.
"""

import argparse
import os
import re
import sys
from datetime import datetime

# Optional dependencies
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    import markdown
    HAS_MD = True
except ImportError:
    HAS_MD = False


# ----------------------------------------------------------------------
# Better fallback YAML parser (warns on unsupported nested dicts)
# ----------------------------------------------------------------------
def _simple_yaml_load(text):
    """Parse a flat YAML mapping. Returns a dict. Warns if nested structures are dropped."""
    lines = text.split('\n')
    data = {}
    current_key = None
    current_list = []
    warned_nested = False

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        if ':' in stripped and not stripped.startswith('-'):
            if current_key and current_list:
                data[current_key] = current_list
                current_list = []

            key, _, val = stripped.partition(':')
            key = key.strip()
            val = val.strip().strip('"').strip("'")

            if val == '':
                current_key = key
            else:
                data[key] = val
                current_key = None
            continue

        elif stripped.startswith('- ') and current_key:
            item = stripped[2:].strip().strip('"').strip("'")
            current_list.append(item)
        else:
            if current_key and ':' in stripped and not warned_nested:
                print(
                    "WARNING: nested dicts not supported by fallback YAML parser; "
                    "install PyYAML for full support.",
                    file=sys.stderr,
                )
                warned_nested = True

    if current_key and current_list:
        data[current_key] = current_list
    return data


# ----------------------------------------------------------------------
# Front matter parsing
# ----------------------------------------------------------------------
def parse_frontmatter(filepath):
    """Return (meta_dict, body_markdown) from a LESSON.md or LESSONS.md file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    parts = content.split('---', 2)
    if len(parts) < 3:
        raise ValueError("Missing YAML front matter (enclose between --- lines).")

    front = parts[1].strip()
    body = parts[2].strip()

    if HAS_YAML:
        meta = yaml.safe_load(front)
    else:
        meta = _simple_yaml_load(front)

    if not isinstance(meta, dict):
        raise ValueError("Front matter must be a YAML dictionary.")
    return meta, body


# ----------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------
REQUIRED_LESSON_FIELDS = ['title', 'language', 'difficulty', 'topics', 'prerequisites', 'objectives']
VALID_DIFFICULTIES = {'beginner', 'intermediate', 'advanced'}
LESSON_SECTIONS = ['Learning Objectives', 'Prerequisites', 'Content', 'Exercises', 'Further Reading']
CODE_BLOCK_PATTERN = re.compile(r'```(\w*)\n')
KNOWN_LANGUAGES = {
    'python', 'javascript', 'typescript', 'java', 'c', 'cpp', 'c++',
    'go', 'rust', 'ruby', 'php', 'swift', 'kotlin', 'scala', 'shell', 'bash',
}


def validate_lesson(filepath):
    """Thoroughly check a LESSON.md file."""
    try:
        meta, body = parse_frontmatter(filepath)
    except Exception as e:
        print(f"ERROR: {e}")
        return False

    version = meta.get('lessond_version', '1.0')
    if version != '1.0':
        print(f"WARNING: LESSON.md version '{version}' (expected '1.0')")

    missing = [f for f in REQUIRED_LESSON_FIELDS if f not in meta]
    if missing:
        print(f"ERROR: Missing required fields: {', '.join(missing)}")
        return False

    for field in ['topics', 'prerequisites', 'objectives']:
        if not isinstance(meta[field], list) or len(meta[field]) == 0:
            print(f"ERROR: '{field}' must be a non-empty list.")
            return False

    if meta['difficulty'] not in VALID_DIFFICULTIES:
        print(f"WARNING: difficulty '{meta['difficulty']}' not one of {sorted(VALID_DIFFICULTIES)}")

    if meta['language'].lower() not in KNOWN_LANGUAGES:
        print(f"WARNING: '{meta['language']}' not in known language list — verify spelling.")

    section_pattern = re.compile(
        r'^##\s+(' + '|'.join(re.escape(s) for s in LESSON_SECTIONS) + r')',
        re.MULTILINE,
    )
    if not section_pattern.search(body):
        print("WARNING: No standard sections found (## Learning Objectives, ## Content, etc.)")

    unlabelled = [cb for cb in CODE_BLOCK_PATTERN.findall(body) if cb == '']
    if unlabelled:
        print(f"WARNING: {len(unlabelled)} code block(s) without a language identifier.")

    print(f"\n✅  '{filepath}' is a valid LESSON.md")
    print(f"    Title      : {meta['title']}")
    print(f"    Language   : {meta['language']}  |  Difficulty: {meta['difficulty']}")
    print(f"    Topics     : {', '.join(meta['topics'])}")
    return True


# ----------------------------------------------------------------------
# Scaffold LESSON.md
# ----------------------------------------------------------------------
def scaffold_lesson(filepath, cli_args=None):
    """Create a new LESSON.md interactively, with optional CLI overrides."""
    if cli_args is None:
        cli_args = {}

    if os.path.exists(filepath):
        overwrite = input(f"File '{filepath}' already exists. Overwrite? [y/N]: ").strip().lower()
        if overwrite != 'y':
            print("Aborted.")
            return

    print("Building a new LESSON.md\n")
    title = cli_args.get('title') or input("Title: ").strip()
    language = cli_args.get('language') or input("Language (e.g. Python, JavaScript): ").strip()
    difficulty = (cli_args.get('difficulty') or input("Difficulty [beginner/intermediate/advanced]: ")).strip().lower()
    if difficulty not in VALID_DIFFICULTIES:
        print("Invalid difficulty; defaulting to 'beginner'.")
        difficulty = 'beginner'

    topics_raw = cli_args.get('topics') or input("Topics (comma-separated): ").strip()
    topics = [t.strip() for t in topics_raw.split(',') if t.strip()] if topics_raw else ['general']

    prereq_raw = cli_args.get('prerequisites') or input("Prerequisites (comma-separated): ").strip()
    prereqs = [p.strip() for p in prereq_raw.split(',') if p.strip()] if prereq_raw else ['None']

    obj_raw = cli_args.get('objectives') or input("Learning objectives (comma-separated): ").strip()
    objectives = [o.strip() for o in obj_raw.split(',') if o.strip()] if obj_raw else ['Understand the topic']

    fm = (
        f'---\n'
        f'lessond_version: "1.0"\n'
        f'title: "{title}"\n'
        f'language: "{language}"\n'
        f'difficulty: "{difficulty}"\n'
        f'topics: {topics}\n'
        f'prerequisites: {prereqs}\n'
        f'objectives: {objectives}\n'
        f'created: "{datetime.now().strftime("%Y-%m-%d")}"\n'
        f'---\n'
    )
    body = (
        "## Learning Objectives\n"
        "<!-- List what the learner will be able to do -->\n\n"
        "## Prerequisites\n"
        "<!-- Required knowledge -->\n\n"
        "## Content\n"
        "<!-- Lesson content; use fenced code blocks with a language identifier -->\n\n"
        "## Exercises\n"
        "<!-- Practical tasks for the learner -->\n\n"
        "## Further Reading\n"
        "<!-- Links to docs, articles, etc. -->\n"
    )
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(fm + '\n' + body)
    print(f"\n✅  Created '{filepath}'")


# ----------------------------------------------------------------------
# Scaffold LESSONS.md (agent memory)
# ----------------------------------------------------------------------
def scaffold_memory(filepath):
    """Create a LESSONS.md agent-memory file with the three canonical sections."""
    if os.path.exists(filepath):
        overwrite = input(f"File '{filepath}' already exists. Overwrite? [y/N]: ").strip().lower()
        if overwrite != 'y':
            print("Aborted.")
            return

    today = datetime.now().strftime('%Y-%m-%d')
    content = f"""\
---
lessons_version: "1.0"
created: "{today}"
project: "your-project-name"
---

# Lessons Learned

## DO NOT
<!-- Hard blocks. If you see a matching situation, stop immediately and apply the alternative. -->

<!-- Example:
### DO NOT use `pandas.DataFrame.append`
- **Why:** Deprecated in pandas 1.4.0, removed in 2.0.
- **Use instead:** `pd.concat()`
- **First seen:** YYYY-MM-DD (agent: name)
- **Tags:** #pandas #deprecation
-->

## PITFALLS
<!-- Context-dependent mistakes to watch for. -->

<!-- Example:
### `datetime.now()` is not timezone-aware in containers
- **What happens:** Container UTC gets treated as local time.
- **Fix:** Use `datetime.now(timezone.utc)`
- **Context:** Any cron-based agent.
- **Tags:** #python #timezone
-->

## SUCCESS PATTERNS
<!-- Techniques that worked exceptionally well. -->

<!-- Example:
### Chain-of-draft reasoning before writing >50 lines of code
- **Result:** Reduced review cycles by 30 %.
- **How:** Agent writes a numbered plain-language draft first.
- **Tags:** #process #code-gen
-->
"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n✅  Created '{filepath}'")


# ----------------------------------------------------------------------
# HTML export (with plain-text fallback)
# ----------------------------------------------------------------------
def export_html(filepath):
    """Convert a .md file to a styled HTML page (stdout)."""
    meta, body = parse_frontmatter(filepath)

    if HAS_MD:
        md = markdown.Markdown(extensions=['fenced_code', 'codehilite'])
        html_body = md.convert(body)
    else:
        import html as _html
        html_body = f"<pre>{_html.escape(body)}</pre>"

    title = meta.get('title', 'Lesson')
    styles = """\
    <style>
      body  { font-family: system-ui, sans-serif; max-width: 800px; margin: auto; padding: 2em; background: #fafafa; }
      pre   { background: #1e1e1e; color: #d4d4d4; padding: 1em; border-radius: 5px; overflow-x: auto; }
      code  { font-family: 'Fira Code', monospace; }
      .meta { background: #eee; padding: 1em; border-radius: 5px; margin-bottom: 2em; }
    </style>"""

    meta_html = (
        "<div class='meta'>"
        f"<h1>{title}</h1>"
        f"<p><strong>Language:</strong> {meta.get('language', '')} | "
        f"<strong>Difficulty:</strong> {meta.get('difficulty', '')}</p>"
        f"<p><strong>Topics:</strong> {', '.join(meta.get('topics', []))}</p>"
        "</div>"
    )

    print(f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title}</title>
{styles}
</head>
<body>
{meta_html}
{html_body}
</body>
</html>""")


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description='Unified LESSON.md / LESSONS.md authoring & memory tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
commands:
  scaffold   Create a new LESSON.md (interactive, with optional --flags)
  validate   Validate an existing LESSON.md
  html       Export a LESSON.md to HTML on stdout
  init-memory  Create a LESSONS.md agent-memory file
""",
    )
    sub = parser.add_subparsers(dest='command', required=True)

    sp_s = sub.add_parser('scaffold', help='Create a new LESSON.md')
    sp_s.add_argument('file')
    sp_s.add_argument('--title')
    sp_s.add_argument('--language')
    sp_s.add_argument('--difficulty', choices=list(VALID_DIFFICULTIES))
    sp_s.add_argument('--topics', help='Comma-separated list')
    sp_s.add_argument('--prerequisites', '--prereqs', dest='prerequisites', help='Comma-separated list')
    sp_s.add_argument('--objectives', help='Comma-separated list')

    sp_v = sub.add_parser('validate', help='Validate a LESSON.md file')
    sp_v.add_argument('file')

    sp_h = sub.add_parser('html', help='Export LESSON.md to HTML (stdout)')
    sp_h.add_argument('file')

    sp_m = sub.add_parser('init-memory', help='Create a LESSONS.md agent-memory file')
    sp_m.add_argument('file', nargs='?', default='LESSONS.md')

    args = parser.parse_args()

    if args.command == 'scaffold':
        scaffold_lesson(args.file, {
            'title': args.title,
            'language': args.language,
            'difficulty': args.difficulty,
            'topics': args.topics,
            'prerequisites': args.prerequisites,
            'objectives': args.objectives,
        })
    elif args.command == 'validate':
        validate_lesson(args.file)
    elif args.command == 'html':
        export_html(args.file)
    elif args.command == 'init-memory':
        scaffold_memory(args.file)


if __name__ == '__main__':
    main()
