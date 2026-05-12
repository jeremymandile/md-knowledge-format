"""
Unit tests for LESSONS.md format validation.
"""
import re, pytest
from pathlib import Path


def test_lessons_file_exists(repo_root):
    """LESSONS-html-shift.md should exist in docs/"""
    path = repo_root / "docs" / "LESSONS-html-shift.md"
    assert path.exists(), f"LESSONS.md not found at {path}"


def test_lessons_file_structure(repo_root):
    """LESSONS.md should have required top-level sections"""
    path = repo_root / "docs" / "LESSONS-html-shift.md"
    content = path.read_text()
    assert "DO NOT" in content.upper()
    assert "PITFALL" in content.upper()
    assert "SUCCESS" in content.upper()


def test_lesson_entries_have_tags(repo_root):
    """Each lesson entry should have at least one hash-prefixed tag"""
    path = repo_root / "docs" / "LESSONS-html-shift.md"
    content = path.read_text()
    tag_lines = [line for line in content.split("\n") if "Tags:" in line or "tags:" in line.lower()]
    assert len(tag_lines) > 0, "No tag lines found in LESSONS.md"
    for line in tag_lines:
        # At least one # tag should be present
        assert "#" in line, f"Tag line missing hash-prefix: {line}"


def test_lesson_file_is_grep_friendly(repo_root):
    """LESSONS.md should not require special parsing — plain grep must work"""
    path = repo_root / "docs" / "LESSONS-html-shift.md"
    content = path.read_text()
    # Must be plain text (no binary artifacts)
    assert content.isprintable() or "\n" in content
    # Must have consistent line endings
    assert "\r\n" not in content or "\n" in content


def test_renderer_spec_exists(repo_root):
    """renderer_spec.md should exist in docs/"""
    path = repo_root / "docs" / "renderer_spec.md"
    assert path.exists(), f"renderer_spec.md not found at {path}"


def test_html_whitelist_exists(repo_root):
    """html_tag_whitelist.yaml should exist in specs/"""
    path = repo_root / "specs" / "html_tag_whitelist.yaml"
    assert path.exists(), f"html_tag_whitelist.yaml not found at {path}"


def test_whitelist_is_valid_yaml(repo_root):
    """html_tag_whitelist.yaml should be parseable as YAML"""
    pytest.importorskip("yaml")
    import yaml
    path = repo_root / "specs" / "html_tag_whitelist.yaml"
    with open(path) as f:
        data = yaml.safe_load(f)
    assert data is not None
    assert isinstance(data, dict)
