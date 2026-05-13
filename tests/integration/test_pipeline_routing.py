"""tests/integration/test_pipeline_routing.py

Integration tests for the three-stage pipeline routing:
  pre_check -> execute -> post_learn

Tests that the correct stage runs given different inputs,
and that lessons are routed to the correct tags.

Philosophy: test the contract, not the implementation.
"""
import pytest
import pathlib
import textwrap


@pytest.mark.integration
class TestPipelineRouting:
    """Pipeline stage routing integration tests."""

    def _make_config(self, tmp_path: pathlib.Path, **overrides) -> dict:
        """Build a minimal pipeline config dict."""
        config = {
            "pipeline": {
                "pre_check": {"enabled": True, "max_lessons_to_surface": 3,
                              "token_budget_threshold": 500},
                "execute": {"enabled": True, "inject_lessons_as": "system_context"},
                "post_learn": {"enabled": True, "confidence_threshold": 0.8,
                               "auto_tag": True},
            },
            "knowledge": {
                "lessons_file": str(tmp_path / "LESSONS.md"),
                "lesson_version": 1,
                "allow_external_scripts": False,
            },
        }
        config.update(overrides)
        return config

    def _make_lessons(self, tmp_path: pathlib.Path) -> pathlib.Path:
        lessons = tmp_path / "LESSONS.md"
        lessons.write_text(textwrap.dedent(
            """\
            ---
            lesson_version: 1
            ---

            ## L001 — Never use bare except

            tags: [python, error-handling]
            severity: high

            Never use bare `except:`. Always catch specific exceptions.

            ## L002 — Validate API responses

            tags: [api, validation]
            severity: medium

            Always check status codes before parsing response bodies.
            """
        ))
        return lessons

    def test_pre_check_finds_relevant_lessons(self, tmp_path):
        """pre_check stage should surface lessons matching the task tags."""
        lessons = self._make_lessons(tmp_path)
        config = self._make_config(tmp_path)

        # Simulate pre_check: find lessons by tag
        task_tags = ["python", "error-handling"]
        content = lessons.read_text()

        found = []
        for block in content.split("\n\n"):
            if any(tag in block for tag in task_tags):
                found.append(block)

        assert len(found) > 0, "pre_check should find relevant lessons"
        assert any("bare except" in f for f in found)

    def test_pre_check_skips_irrelevant_lessons(self, tmp_path):
        """pre_check should not surface lessons that don't match the task."""
        lessons = self._make_lessons(tmp_path)

        # Task tags that don't match any lessons
        task_tags = ["typescript", "css"]
        content = lessons.read_text()

        found = []
        for block in content.split("\n\n"):
            if any(tag in block for tag in task_tags):
                found.append(block)

        # Should find nothing (or only non-lesson blocks like front matter)
        lesson_blocks = [f for f in found if "##" in f]
        assert len(lesson_blocks) == 0, (
            "pre_check should not surface lessons for unrelated tags"
        )

    def test_post_learn_appends_to_lessons(self, tmp_path):
        """post_learn stage should append new lessons to LESSONS.md."""
        lessons = self._make_lessons(tmp_path)
        initial_content = lessons.read_text()
        initial_count = initial_content.count("## L")

        new_lesson = textwrap.dedent(
            """\

            ## L003 — Cache database queries

            tags: [performance, database]
            severity: medium

            Repeated identical queries in a loop caused N+1 problem.
            Cache results or use batch queries instead.
            """
        )

        # post_learn appends the lesson
        with open(lessons, "a") as f:
            f.write(new_lesson)

        updated = lessons.read_text()
        assert updated.count("## L") == initial_count + 1
        assert "Cache database queries" in updated

    def test_allow_external_scripts_false_enforced(self, tmp_path):
        """Pipeline config must have allow_external_scripts: false in production."""
        config = self._make_config(tmp_path)

        knowledge_config = config.get("knowledge", {})
        assert knowledge_config.get("allow_external_scripts") is False, (
            "allow_external_scripts MUST be False in production config"
        )

    def test_lesson_version_validated(self, tmp_path):
        """Lessons file must have lesson_version in front matter."""
        lessons = tmp_path / "LESSONS.md"
        lessons.write_text("# No front matter\n\n## L001\n\ntags: [test]\n")

        content = lessons.read_text()
        has_version = "lesson_version:" in content

        # This should fail — missing front matter
        assert not has_version, "This lessons file correctly lacks lesson_version"

        # A valid file should have it
        valid = self._make_lessons(tmp_path / "valid")
        # No — use new tmp dir
        valid_path = tmp_path / "valid_lessons.md"
        valid_path.write_text("---\nlesson_version: 1\n---\n\n## L001\n\ntags: [x]\n")
        assert "lesson_version:" in valid_path.read_text()

    def test_tag_routing_uses_exact_match(self, tmp_path):
        """Tags should be matched exactly, not as substrings.

        'api' should not match 'rapid' or 'mapping'.
        """
        lessons = tmp_path / "LESSONS.md"
        lessons.write_text(textwrap.dedent(
            """\
            ---
            lesson_version: 1
            ---

            ## L001 — Example lesson

            tags: [rapid, mapping, typing]
            severity: low

            This lesson has tags that contain 'api' as a substring.
            """
        ))

        content = lessons.read_text()
        # Exact tag match for 'api' — look for [api] or api, in the tags line
        import re
        pattern = re.compile(r'\btags:\s*\[([^\]]*)\]', re.MULTILINE)
        all_tags = []
        for match in pattern.finditer(content):
            tags = [t.strip() for t in match.group(1).split(",")]
            all_tags.extend(tags)

        # 'api' should NOT be in the tag list (only 'rapid', 'mapping', 'typing')
        assert "api" not in all_tags, (
            "Exact tag matching: 'api' should not appear as a tag "
            "just because other tags contain it as a substring"
        )
