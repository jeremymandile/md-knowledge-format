#!/usr/bin/env python3
"""examples/agent_demo/run_demo.py

Entry point for the md-knowledge-format agent demo.

Runs three scenarios that demonstrate the core flywheel:
  1. Basic lesson lookup
  2. Cross-session learning (Agent A teaches Agent B)
  3. Token-budget mode (grep instead of full load)

Usage:
    cd examples/agent_demo
    python run_demo.py

Requires:
    pip install pyyaml
"""
import pathlib
import sys
import time

# Add repo root to path so we can import from the demo package
REPO_ROOT = pathlib.Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from agent import KnowledgeAwareAgent


SEPARATOR = "=" * 60


def demo_basic_lookup(lessons_path: pathlib.Path) -> None:
    """Demo 1: Basic lesson lookup by tag."""
    print(f"\n{SEPARATOR}")
    print("DEMO 1: Basic Lesson Lookup")
    print(SEPARATOR)

    agent = KnowledgeAwareAgent(
        agent_id="demo-agent-alpha",
        lessons_path=lessons_path,
    )

    print(f"Agent: {agent.agent_id}")
    print(f"Lessons file: {lessons_path}")
    print()

    tags_to_check = ["python", "error-handling", "api"]
    for tag in tags_to_check:
        lessons = agent.grep_lessons(tag)
        print(f"  Tag [{tag!r}]: {len(lessons)} lesson(s) found")
        for lesson in lessons[:2]:  # show first 2
            title = next((l for l in lesson.splitlines() if l.startswith("## ")), "?")
            print(f"    - {title}")

    print("\n[OK] Basic lookup complete")


def demo_cross_session_learning(lessons_path: pathlib.Path) -> None:
    """Demo 2: Agent A writes a lesson; Agent B reads it immediately."""
    print(f"\n{SEPARATOR}")
    print("DEMO 2: Cross-Session Learning")
    print(SEPARATOR)

    agent_a = KnowledgeAwareAgent(
        agent_id="agent-alpha",
        lessons_path=lessons_path,
    )
    agent_b = KnowledgeAwareAgent(
        agent_id="agent-beta",
        lessons_path=lessons_path,  # shared file!
    )

    # Agent A encounters something new and writes a lesson
    print("Agent A: Writing new lesson about retry logic...")
    new_lesson = """
## L999 — Always use exponential backoff for retries

tags: [reliability, api, retry]
severity: medium
session: demo

### Rule

Never use fixed sleep() for retries. Use exponential backoff
with jitter to avoid thundering herd problems.
"""
    agent_a.append_lesson(new_lesson)
    print("Agent A: Lesson written.")
    print()

    # Agent B (fresh) can now access it
    print("Agent B: Checking for reliability lessons...")
    results = agent_b.grep_lessons("reliability")
    print(f"Agent B: Found {len(results)} lesson(s) tagged 'reliability'")
    for r in results:
        title = next((l for l in r.splitlines() if l.startswith("## ")), "?")
        print(f"  - {title}")

    print("\n[OK] Cross-session learning complete — Agent B learned without fine-tuning")


def demo_token_budget_mode(lessons_path: pathlib.Path) -> None:
    """Demo 3: Token-budget mode — grep first, full load only if needed."""
    print(f"\n{SEPARATOR}")
    print("DEMO 3: Token-Budget Mode")
    print(SEPARATOR)

    agent = KnowledgeAwareAgent(
        agent_id="budget-agent",
        lessons_path=lessons_path,
        token_budget=500,  # tight context window
    )

    print(f"Agent: {agent.agent_id} (budget: {agent.token_budget} tokens)")
    print()

    # In budget mode, agent greps first
    start = time.perf_counter()
    results = agent.smart_lookup("python")
    elapsed = time.perf_counter() - start

    print(f"  Smart lookup for [python]: {len(results)} result(s) in {elapsed*1000:.1f}ms")
    print(f"  Mode used: {agent.last_lookup_mode}")
    print()
    print("[OK] Token-budget mode complete — targeted grep avoids context overflow")


def main() -> None:
    """Run all three demos."""
    print("md-knowledge-format Agent Demo")
    print("Demonstrating: institutional memory via shared LESSONS.md")

    # Use the sample lessons file from fixtures if available,
    # otherwise create a minimal one in /tmp
    fixtures = REPO_ROOT / "tests" / "fixtures" / "sample_lessons.md"
    if fixtures.exists():
        lessons_path = fixtures
        print(f"\nUsing fixture: {fixtures.relative_to(REPO_ROOT)}")
    else:
        import tempfile
        tmp = pathlib.Path(tempfile.mktemp(suffix=".md"))
        tmp.write_text(
            "---\nlesson_version: 1\n---\n\n"
            "## L001 — Use explicit exception types\n\n"
            "tags: [python, error-handling]\nseverity: high\n\n"
            "Never use bare `except:`. Always catch specific exceptions.\n"
        )
        lessons_path = tmp
        print(f"\nCreated temp lessons file: {tmp}")

    try:
        demo_basic_lookup(lessons_path)
        demo_cross_session_learning(lessons_path)
        demo_token_budget_mode(lessons_path)
    finally:
        # Clean up temp file if we created one
        if not fixtures.exists() and lessons_path.exists():
            lessons_path.unlink()

    print(f"\n{SEPARATOR}")
    print("All demos complete!")
    print("The flywheel spins. No fine-tuning required.")
    print(SEPARATOR)


if __name__ == "__main__":
    main()
