"""Assign precedence class to each constraint node."""
from enum import Enum
from typing import Optional


class ConstraintClass(Enum):
    A = "Hard Invariants"
    Bs = "Structural Constraints"
    Bp = "Procedural Constraints"
    C = "Behavioral Priors"
    D = "Contextual Heuristics"


def classify_constraint(constraint: dict, source_file: str = "") -> Optional[ConstraintClass]:
    """
    Classify a constraint text into one of the five classes.
    Returns None if ambiguous (caller defaults to D).
    """
    text = constraint.get('text', '')
    section = constraint.get('section', '').lower()
    combined = (text + ' ' + section).lower()

    hard_signals = [
        "do not output", "must always", "security policy", "safety constraint",
        "non-overridable", "inviolable", "never output", "must never",
        "hard constraint", "system policy"
    ]
    if any(s in combined for s in hard_signals):
        return ConstraintClass.A

    structural_signals = [
        "output format", "schema", "json", "yaml front matter", "must include",
        "structure", "format must", "valid json", "valid yaml",
        "code block must", "output must be", "front matter"
    ]
    if any(s in combined for s in structural_signals):
        return ConstraintClass.Bs

    procedural_signals = [
        "before calling", "after", "step", "validate before",
        "then", "procedure", "workflow", "ordering", "first", "sequence",
        "use pd.concat", "instead of", "always validate",
        "cite sources", "step-by-step"
    ]
    if any(s in combined for s in procedural_signals):
        return ConstraintClass.Bp

    tone_signals = [
        "be blunt", "be concise", "skip filler", "tone", "voice",
        "personality", "never open with", "great question",
        "epistemic", "stance", "verbosity", "humor", "swearing",
        "hedging", "confident", "direct", "assertive"
    ]
    if any(s in combined for s in tone_signals):
        return ConstraintClass.C

    return ConstraintClass.D
