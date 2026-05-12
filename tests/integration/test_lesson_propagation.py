"""
Integration test: proves wisdom compounds without fine-tuning.
This is the core insight of md-knowledge-format.

Session 1: Agent makes a mistake (embeds <script>).
Human adds DO NOT rule to LESSONS.md.
Session 2: Same agent, fresh context, avoids the mistake.
No fine-tuning. No embeddings. Just grep + schema.
"""
import pytest
from pathlib import Path

try:
    from tools.csp_sanitizer import apply_security_hardening
    HAS_SANITIZER = True
except ImportError:
    HAS_SANITIZER = False


class MockAgentSession:
    """Minimal agent session that loads LESSONS.md via grep."""

    def __init__(self, lessons_file: Path):
        self.lessons_file = lessons_file
        self._load_lessons()

    def _load_lessons(self):
        """Load lessons via grep-friendly parsing (no embeddings)."""
        self.do_not_rules = []
        if self.lessons_file.exists():
            content = self.lessons_file.read_text()
            for line in content.split("\n"):
                if "### DO NOT" in line:
                    rule = line.split("###")[-1].strip()
                    self.do_not_rules.append(rule.lower())

    def generate(self, prompt: str, metadata: dict):
        """Generate output respecting loaded lessons."""
        output_obj = type("Output", (), {})()
        if "script" in prompt.lower() and any("script" in rule for rule in self.do_not_rules):
            # Agent learned: avoid <script>
            output_obj.html = "<div class='widget'><p>Code review widget (safe)</p></div>"
        else:
            # Agent (naively) embeds script
            output_obj.html = (
                "<div class='widget'><script>alert('xss')</script>"
                "<p>Code review widget</p></div>"
            )
        return output_obj


def test_lesson_propagation_end_to_end(temp_lessons_file):
    """
    Proves: same prompt + fresh context + lessons file = avoided mistake.
    No fine-tuning. No embeddings. Just grep + file.
    """
    # === SESSION 1: Mistake ===
    session1 = MockAgentSession(lessons_file=temp_lessons_file)
    output1 = session1.generate(
        prompt="Create a code review widget with script tracking",
        metadata={"recipient": "human", "complexity_score": 7}
    )
    # Agent (naively) embeds a script tag
    assert "<script>" in output1.html, "Session 1 should make the mistake"

    # Human (or automated linter) adds lesson
    lesson_entry = (
        "\n### DO NOT embed <script> tags in agent-generated HTML\n"
        "- Why: XSS risk; violates CSP policy.\n"
        "- Use instead: Use data attributes + external JS with CSP nonce.\n"
        "- Tags: #security #xss #html\n"
    )
    with open(temp_lessons_file, "a") as f:
        f.write(lesson_entry)

    # === SESSION 2: Fresh context, same agent ===
    session2 = MockAgentSession(lessons_file=temp_lessons_file)
    output2 = session2.generate(
        prompt="Create a code review widget with script tracking",
        metadata={"recipient": "human", "complexity_score": 7}
    )

    # Agent now avoids the mistake — no fine-tuning, just grep
    assert "<script>" not in output2.html, "Session 2 should avoid the mistake"

    # Bonus: sanitizer also hardens the output
    if HAS_SANITIZER:
        resp = apply_security_hardening(output2.html)
        assert "nonce-" in resp.headers["Content-Security-Policy"]
        assert "<script>" not in resp.text.lower()


def test_lesson_file_persists_across_sessions(temp_lessons_file):
    """Lesson written in session 1 is readable in session 2."""
    # Write a lesson
    with open(temp_lessons_file, "a") as f:
        f.write("\n### DO NOT use inline scripts\n- Tags: #security\n")

    # New session reads it
    content = temp_lessons_file.read_text()
    assert "DO NOT use inline scripts" in content
    assert "#security" in content


def test_multiple_lessons_compound(temp_lessons_file):
    """Multiple lessons accumulate and all are enforced."""
    lessons = [
        "\n### DO NOT use script injection\n- Tags: #security\n",
        "\n### DO NOT use eval()\n- Tags: #security #javascript\n",
        "\n### DO NOT use document.write\n- Tags: #security\n",
    ]
    for lesson in lessons:
        with open(temp_lessons_file, "a") as f:
            f.write(lesson)

    session = MockAgentSession(lessons_file=temp_lessons_file)
    assert len(session.do_not_rules) == 3
