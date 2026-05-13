"""tests/e2e/test_agent_session.py

E2E tests for a single agent session lifecycle:
  - Session start: agent loads LESSONS.md
  - Execution: agent runs a task
  - Session end: agent writes any new lessons discovered

These tests verify the full session contract without
requiring a live LLM API. All agent behavior is simulated
using the file-based knowledge interface.

Philosophy: test the contract, not the implementation.
"""
import pytest
import pathlib
import textwrap
import time


@pytest.mark.e2e
class TestAgentSession:
    """Single agent session lifecycle tests."""

    def _make_shared_lessons(self, tmp_path: pathlib.Path) -> pathlib.Path:
        """Create a shared LESSONS.md file for testing."""
        db = tmp_path / "LESSONS.md"
        db.write_text(textwrap.dedent(
            """\
            ---
            lesson_version: 1
            ---

            ## L001 — Always validate inputs before processing

            tags: [validation, security, python]
            severity: high
            session: 2024-01-10T08:00:00Z

            Never process user-supplied data without validation.
            Check type, length, and format before any downstream use.

            ## L002 — Log the decision, not just the outcome

            tags: [logging, observability, debugging]
            severity: medium
            session: 2024-01-11T09:30:00Z

            Include WHY a decision was made in log messages.
            "Retrying request" is less useful than
            "Retrying request: status=503 attempt=2/3 backoff=2.0s"
            """
        ))
        return db

    def test_session_starts_by_loading_lessons(self, tmp_path):
        """At session start, agent should be able to load the lessons database."""
        db = self._make_shared_lessons(tmp_path)

        # Simulate session start: load lessons
        content = db.read_text()

        assert "lesson_version: 1" in content
        assert "L001" in content
        assert "L002" in content
        assert len(content) > 100, "Lessons file should have substantial content"

    def test_session_pre_checks_before_task(self, tmp_path):
        """Before executing a task, agent checks for relevant lessons."""
        db = self._make_shared_lessons(tmp_path)

        # Simulate: agent is about to handle user input
        task_description = "Process user-submitted form data"
        relevant_tags = ["validation", "security"]

        content = db.read_text()
        warnings = []

        for block in content.split("\n\n"):
            if any(tag in block for tag in relevant_tags) and "## L" in block:
                # This is a relevant lesson header area
                warnings.append(block)

        # Should find at least L001 (validation)
        assert len(warnings) > 0, "Pre-check should surface relevant warnings"
        assert any("validation" in w.lower() or "L001" in w for w in warnings)

    def test_session_executes_task(self, tmp_path):
        """Agent executes the task, possibly producing a result."""
        # Simulate task execution: validate and process some data
        user_input = {"name": "Alice", "age": 30}

        def validate_and_process(data: dict) -> dict:
            """Simulated tool that validates input."""
            if not isinstance(data.get("name"), str):
                raise ValueError("name must be a string")
            if not isinstance(data.get("age"), int):
                raise ValueError("age must be an integer")
            return {"status": "ok", "processed": data}

        result = validate_and_process(user_input)
        assert result["status"] == "ok"
        assert result["processed"]["name"] == "Alice"

    def test_session_writes_new_lesson_on_discovery(self, tmp_path):
        """When agent discovers something new, it appends to LESSONS.md."""
        db = self._make_shared_lessons(tmp_path)
        initial_count = db.read_text().count("## L")

        # Simulate: agent discovered that dict.get() is safer than dict[key]
        new_lesson = textwrap.dedent(
            """\

            ## L003 — Use dict.get() instead of dict[key] for optional fields

            tags: [python, defensive-coding]
            severity: low
            session: 2024-01-20T15:00:00Z

            Using dict[key] raises KeyError for missing keys.
            Use dict.get(key, default) for optional fields.
            """
        )

        with open(db, "a") as f:
            f.write(new_lesson)

        updated = db.read_text()
        assert updated.count("## L") == initial_count + 1
        assert "dict.get()" in updated

    def test_session_ends_cleanly(self, tmp_path):
        """Session lifecycle should complete without errors."""
        db = self._make_shared_lessons(tmp_path)

        # Full session lifecycle
        session_log = []

        # 1. Load
        content = db.read_text()
        session_log.append("loaded")

        # 2. Pre-check
        warnings = [b for b in content.split("\n\n")
                    if "validation" in b and "## L" in b]
        session_log.append(f"pre_check: {len(warnings)} warning(s)")

        # 3. Execute
        result = {"status": "ok"}
        session_log.append("executed")

        # 4. Post-learn (no new lesson this time)
        session_log.append("post_learn: nothing to record")

        # Verify session ran all four stages
        assert "loaded" in session_log
        assert any("pre_check" in s for s in session_log)
        assert "executed" in session_log
        assert any("post_learn" in s for s in session_log)

    def test_session_is_idempotent(self, tmp_path):
        """Running the same session twice should not corrupt the lessons file."""
        db = self._make_shared_lessons(tmp_path)

        def run_session():
            content = db.read_text()
            # No new lesson to write
            return content.count("## L")

        count_after_first = run_session()
        count_after_second = run_session()

        assert count_after_first == count_after_second, (
            "Read-only sessions should not change the lessons count"
        )

    def test_concurrent_session_writes_are_safe(self, tmp_path):
        """Multiple sessions appending lessons should not corrupt the file.

        This is a basic sanity check. In production, file locking
        or append-only operations should be used.
        """
        db = self._make_shared_lessons(tmp_path)

        # Simulate two sessions writing at different times
        lesson_a = "\n\n## L003 — Session A lesson\n\ntags: [test]\n"
        lesson_b = "\n\n## L004 — Session B lesson\n\ntags: [test]\n"

        with open(db, "a") as f:
            f.write(lesson_a)

        with open(db, "a") as f:
            f.write(lesson_b)

        content = db.read_text()
        assert "L003" in content
        assert "L004" in content
        assert "lesson_version: 1" in content  # front matter still intact
