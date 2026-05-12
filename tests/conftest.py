"""
Shared pytest fixtures for md-knowledge-format test suite.
"""
import json, pytest, tempfile
from pathlib import Path

@pytest.fixture(scope="session")
def repo_root():
    """Return the repository root path."""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def schema_path(repo_root):
    """Path to the renderer decision schema."""
    return repo_root / "specs" / "renderer_decision_schema.json"

@pytest.fixture(scope="session")
def schema(schema_path):
    """Load the JSON schema."""
    if not schema_path.exists():
        pytest.skip(f"Schema not found at {schema_path}")
    with open(schema_path) as f:
        return json.load(f)

@pytest.fixture(scope="session")
def whitelist_path(repo_root):
    """Path to the HTML tag whitelist."""
    return repo_root / "specs" / "html_tag_whitelist.yaml"

@pytest.fixture
def temp_lessons_file():
    """Create a temporary LESSONS.md file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Lessons Learned\n\n## DO NOT\n\n")
        path = Path(f.name)
    yield path
    path.unlink(missing_ok=True)

@pytest.fixture
def sample_lesson(repo_root):
    """Load a sample LESSON.md for parsing tests."""
    path = repo_root / "tests" / "fixtures" / "sample_lesson.md"
    return path.read_text() if path.exists() else None
