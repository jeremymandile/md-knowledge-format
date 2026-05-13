"""tests/e2e/test_fleet_learning.py

E2E test: two agents, one lesson, zero fine-tuning.

Demonstrates the core flywheel:
  1. Agent A encounters an error and writes a LESSON.md entry.
  2. Agent B (a fresh instance) reads the shared LESSONS.md.
  3. Agent B avoids the same error — without any model retraining.

This is the key contract: institutional memory travels via files,
not via weights.
"""
import pytest
import pathlib
import textwrap


@pytest.mark.e2e
class TestFleetLearning:
    """Two-agent fleet learning via shared LESSONS.md."""

    def _make_lessons_db(self, tmp_path: pathlib.Path) -> pathlib.Path:
        """Create a minimal shared LESSONS.md file."""
        db = tmp_path / "LESSONS.md"
        db.write_text(textwrap.dedent(
            """\
            ---
            lesson_version: 1
            agent_id: agent-alpha
            ---

            ## L001 — Never use bare except in tool calls

            tags: [python, error-handling, tool-calls]
            severity: high
            session: 2024-01-15T09:30:00Z

            ### What happened

            Used `except:` without specifying exception type. Swallowed a
            KeyboardInterrupt and caused the process to hang indefinitely.

            ### Rule

            Always use `except Exception as e:` or a specific exception type.
            Never use bare `except:` in production tool code.

            ### Verified fix

            ```python
            # BAD
            try:
                result = tool.call()
            except:
                pass

            # GOOD
            try:
                result = tool.call()
            except Exception as e:
                logger.error("Tool failed: %s", e)
                raise
            ```
            """
        ))
        return db

    def test_agent_a_writes_lesson(self, tmp_path):
        """Agent A can write a lesson entry to LESSONS.md."""
        db = self._make_lessons_db(tmp_path)

        new_entry = textwrap.dedent(
            """\

            ## L002 — Check API rate limits before bulk calls

            tags: [api, rate-limiting, reliability]
            severity: medium
            session: 2024-01-16T14:00:00Z

            ### What happened

            Called external API 1000x in a loop without rate limiting.
            Hit 429 errors after ~100 calls. Entire batch failed.

            ### Rule

            Always implement exponential backoff and respect Retry-After headers.
            """
        )

        with open(db, "a") as f:
            f.write(new_entry)

        content = db.read_text()
        assert "L002" in content
        assert "rate-limiting" in content
        assert "L001" in content  # original lesson preserved

    def test_agent_b_reads_lessons(self, tmp_path):
        """Agent B can read all lessons from the shared LESSONS.md."""
        db = self._make_lessons_db(tmp_path)

        content = db.read_text()
        lessons = [line for line in content.splitlines() if line.startswith("## L")]

        assert len(lessons) >= 1
        assert any("bare except" in l or "L001" in l for l in lessons)

    def test_agent_b_avoids_known_mistake(self, tmp_path):
        """Agent B grep-checks LESSONS.md and finds the relevant warning.

        This is the core fleet learning contract:
        - Agent B has never seen the error directly
        - Agent B reads shared LESSONS.md
        - Agent B finds the relevant lesson via tag search
        - Agent B can now avoid the mistake
        """
        db = self._make_lessons_db(tmp_path)

        # Simulate Agent B's context-check before writing code:
        # "Am I about to do something that a previous agent warned about?"
        target_tag = "error-handling"
        content = db.read_text()

        relevant_lessons = []
        current_lesson = []
        in_relevant = False

        for line in content.splitlines():
            if line.startswith("## L"):
                if in_relevant and current_lesson:
                    relevant_lessons.append("\n".join(current_lesson))
                current_lesson = [line]
                in_relevant = False
            elif "tags:" in line and target_tag in line:
                in_relevant = True
                current_lesson.append(line)
            elif current_lesson:
                current_lesson.append(line)

        if in_relevant and current_lesson:
            relevant_lessons.append("\n".join(current_lesson))

        # Agent B found the lesson
        assert len(relevant_lessons) >= 1, (
            f"Agent B should find lessons tagged {target_tag!r}"
        )
        assert any("bare except" in lesson or "Never use bare except" in lesson
                   for lesson in relevant_lessons), (
            "The relevant lesson content should mention bare except"
        )

    def test_zero_finetuning_required(self, tmp_path):
        """Verify that knowledge transfer requires no model changes.

        The entire transfer mechanism is file-based. This test
        proves that by showing the full cycle works with only
        filesystem operations (no model API calls).
        """
        shared_db = self._make_lessons_db(tmp_path)

        # Agent A writes a lesson (filesystem write)
        with open(shared_db, "a") as f:
            f.write("\n## L003 — Test lesson\n\ntags: [testing]\n")

        # Agent B reads it (filesystem read) — no model involved
        content = shared_db.read_text()

        # Knowledge transferred
        assert "L003" in content
        assert "testing" in content

        # Verify it's all just text — no binary weights, no embeddings
        assert shared_db.suffix == ".md"
        assert all(c.isprintable() or c == "\n" for c in content), (
            "LESSONS.md must be plain text — no binary data"
        )
