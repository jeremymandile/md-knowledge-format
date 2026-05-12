"""
Minimal AI agent implementing md-knowledge-format contracts.

Emits structured metadata, respects LESSONS.md, and routes output
format deterministically — no prompt engineering required.
"""
import re
from pathlib import Path
from typing import Optional, Literal


class KnowledgeAwareAgent:
    """
    An agent that:
    1. Loads lessons from LESSONS.md via grep (no embeddings)
    2. Emits structured metadata for schema validation
    3. Respects routing decisions (HTML vs Markdown)
    4. Avoids mistakes documented in lessons
    """

    def __init__(self, lessons_file: Optional[Path] = None, schema_file: Optional[Path] = None):
        self.lessons_file = lessons_file
        self.schema_file = schema_file
        self.lessons = self._load_lessons()
        self.schema = self._load_schema()

    def _load_lessons(self) -> dict:
        """Load lessons via grep-friendly parsing — no embeddings, no vector DB."""
        lessons = {"do_not": [], "pitfalls": [], "success": []}

        if not self.lessons_file or not self.lessons_file.exists():
            return lessons

        content = self.lessons_file.read_text()
        current_section = None

        for line in content.split("\n"):
            if "## DO NOT" in line:
                current_section = "do_not"
            elif "## PITFALL" in line:
                current_section = "pitfalls"
            elif "## SUCCESS" in line:
                current_section = "success"
            elif current_section and line.strip().startswith("###"):
                title = line.strip().lstrip("#").strip()
                lessons[current_section].append({"title": title, "raw": line})

        return lessons

    def _load_schema(self) -> Optional[dict]:
        """Load the renderer decision schema for validation."""
        if not self.schema_file or not self.schema_file.exists():
            return None
        import json
        with open(self.schema_file) as f:
            return json.load(f)

    def _check_lessons(self, prompt: str, proposed_output: str) -> list:
        """
        Check proposed output against loaded DO NOT rules.
        Returns list of violation strings (empty if all clear).
        """
        violations = []
        for rule in self.lessons["do_not"]:
            title = rule["title"].lower()
            if "script" in title and "<script>" in proposed_output.lower():
                violations.append(f"Violates: {rule['title']}")
            if "event handler" in title and re.search(r'on\w+="', proposed_output):
                violations.append(f"Violates: {rule['title']}")
            if "javascript:" in title and "javascript:" in proposed_output.lower():
                violations.append(f"Violates: {rule['title']}")
        return violations

    def _revise_output(self, output: str, violations: list) -> str:
        """Revise output to address lesson violations."""
        revised = output
        for violation in violations:
            if "<script>" in violation.lower():
                revised = re.sub(r'<script[^>]*>.*?</script>', '', revised, flags=re.DOTALL | re.I)
            if "event handler" in violation.lower():
                revised = re.sub(r'\s+on\w+="[^"]*"', '', revised)
            if "javascript:" in violation.lower():
                revised = re.sub(r'href=["\']javascript:[^"\']*["\']', 'href="#"', revised, flags=re.I)
        return revised

    def emit_metadata(self,
                      recipient: str,
                      complexity_score: int,
                      requires_interactivity: bool,
                      estimated_tokens: int,
                      max_token_budget: int = 1000) -> dict:
        """
        Emit structured metadata for schema validation.
        Control-plane output: machine-readable, grep-friendly.
        """
        return {
            "recipient": recipient,
            "complexity_score": complexity_score,
            "requires_interactivity": requires_interactivity,
            "rendering_constraints": {"max_token_budget": max_token_budget},
            "estimated_tokens": estimated_tokens,
            "recommended_format": "html" if (
                recipient == "human" and
                (complexity_score >= 6 or requires_interactivity)
            ) else "markdown"
        }

    def generate(self, prompt: str, metadata: dict, structured_data: dict) -> dict:
        """
        Generate output respecting lessons and routing decisions.
        Returns dict with 'format', 'content', 'warnings'.
        """
        if metadata["recommended_format"] == "html":
            raw_output = self._render_html(structured_data)
        else:
            raw_output = self._render_markdown(structured_data)

        violations = self._check_lessons(prompt, raw_output)
        if violations:
            raw_output = self._revise_output(raw_output, violations)
            warnings = violations
        else:
            warnings = []

        return {
            "format": metadata["recommended_format"],
            "content": raw_output,
            "warnings": warnings,
            "metadata": metadata,
        }

    def _render_html(self, data: dict) -> str:
        """Simple HTML renderer — production systems should use Jinja2."""
        title = data.get("title", "Untitled")
        items = data.get("items", [])
        rows = "".join(f"        <li>{item}</li>\n" for item in items)
        return (
            f"<!DOCTYPE html>\n<html>\n<head>\n"
            f"    <title>{title}</title>\n"
            f"    <style>body{{font-family:system-ui;margin:2rem;}}</style>\n"
            f"</head>\n<body>\n    <h1>{title}</h1>\n    <ul>\n"
            f"{rows}"
            f"    </ul>\n</body>\n</html>"
        )

    def _render_markdown(self, data: dict) -> str:
        """Simple Markdown renderer."""
        title = data.get("title", "Untitled")
        items = data.get("items", [])
        return f"# {title}\n\n" + "".join(f"- {item}\n" for item in items)
