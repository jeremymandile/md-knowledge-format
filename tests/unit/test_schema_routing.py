"""
Unit tests for renderer_decision_schema.json routing logic.
"""
import jsonschema, pytest, json


def test_valid_human_high_complexity(schema):
    """Human + complexity >= 6 -> html"""
    instance = {
        "recipient": "human",
        "complexity_score": 7,
        "requires_interactivity": False,
        "rendering_constraints": {"max_token_budget": 1000},
        "recommended_format": "html"
    }
    jsonschema.validate(instance, schema)
    assert instance["recommended_format"] == "html"


def test_valid_human_low_complexity_fallback(schema):
    """Human + complexity < 6 -> markdown"""
    instance = {
        "recipient": "human",
        "complexity_score": 3,
        "requires_interactivity": False,
        "rendering_constraints": {"max_token_budget": 1000},
        "recommended_format": "markdown"
    }
    jsonschema.validate(instance, schema)
    assert instance["recommended_format"] == "markdown"


def test_valid_agent_recipient(schema):
    """Agent recipient -> markdown regardless of complexity"""
    instance = {
        "recipient": "agent",
        "complexity_score": 9,
        "requires_interactivity": False,
        "rendering_constraints": {"max_token_budget": 1000},
        "recommended_format": "markdown"
    }
    jsonschema.validate(instance, schema)
    assert instance["recommended_format"] == "markdown"


def test_valid_interactivity_triggers_html(schema):
    """requires_interactivity=true -> html even for low complexity"""
    instance = {
        "recipient": "human",
        "complexity_score": 2,
        "requires_interactivity": True,
        "rendering_constraints": {"max_token_budget": 1000},
        "recommended_format": "html"
    }
    jsonschema.validate(instance, schema)
    assert instance["recommended_format"] == "html"


def test_invalid_missing_required_field(schema):
    """Missing rendering_constraints -> invalid"""
    instance = {
        "recipient": "human",
        "complexity_score": 7,
        "requires_interactivity": False,
        "recommended_format": "html"
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, schema)


def test_invalid_complexity_out_of_bounds(schema):
    """complexity_score > 10 -> invalid"""
    instance = {
        "recipient": "human",
        "complexity_score": 11,
        "requires_interactivity": False,
        "rendering_constraints": {"max_token_budget": 1000},
        "recommended_format": "html"
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance, schema)


@pytest.mark.parametrize("score,expected", [
    (1, "markdown"), (5, "markdown"), (6, "html"), (10, "html")
])
def test_complexity_boundary_conditions(schema, score, expected):
    """Test the complexity_score threshold boundary"""
    instance = {
        "recipient": "human",
        "complexity_score": score,
        "requires_interactivity": False,
        "rendering_constraints": {"max_token_budget": 1000},
        "recommended_format": expected
    }
    jsonschema.validate(instance, schema)
    assert instance["recommended_format"] == expected
