# Contributing to md-knowledge-format

Thanks for helping make portable knowledge files better. This guide covers how to propose changes to the LESSON.md and LESSONS.md specs, submit examples, and improve the tooling.

## Getting Started

1. **Fork the repo** and clone it locally.
2. **Create a branch** for your change:
   ```bash
   git checkout -b my-change
   ```
3. **Run the validator** on any `.lesson.md` files you touch:
   ```bash
   python tools/lesson_tool.py validate path/to/file.lesson.md
   ```
4. **Push your branch** and open a pull request.

## Proposing Spec Changes

The specs live in `spec/`. We follow semantic versioning:

- **Patch (1.0.x):** Clarifications, typo fixes, non-breaking wording improvements.
- **Minor (1.x.0):** New optional front-matter fields, new recommended body sections.
- **Major (x.0.0):** Changes to required fields or file structure.

For anything beyond a patch:

1. Open an issue first describing the problem and your proposed solution.
2. Gather feedback from the community.
3. Once there's rough consensus, submit a PR with the spec change **and** an update to `lesson_tool.py` if the change affects validation or scaffolding.

## Submitting Examples

Examples live in `examples/`. A good example:

- Validates cleanly: `python tools/lesson_tool.py validate examples/your-file.lesson.md`
- Uses all five recommended body sections.
- Has language identifiers on every code block.
- Demonstrates a realistic, self-contained lesson.

For `.lessons.md` examples, seed them with realistic entries that showcase all three sections (DO NOT, PITFALLS, SUCCESS PATTERNS).

## Improving the Tool

`tools/lesson_tool.py` is a single-file Python 3.6+ CLI with zero mandatory dependencies. When contributing:

- Keep the fallback YAML parser working for users without PyYAML.
- Maintain backward compatibility — the tool should handle v1.0 and any future spec versions gracefully.
- Run `python tools/lesson_tool.py validate examples/python-loops.lesson.md` before submitting to confirm the tool still works end-to-end.

## Code of Conduct

Be kind. Be constructive. This is a small spec — let's keep it that way.

## Questions?

Open an issue or start a discussion. We're building the simplest possible knowledge format family. Your ideas are welcome.
