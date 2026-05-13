"""Tests for coherence scoring function."""
import json
from pathlib import Path
from analyzer.python.compute_rho import compute_coherence


def load_sample_graph():
    path = Path(__file__).parent / "sample_constraint_graph.json"
    with open(path) as f:
        return json.load(f)["nodes"]


def test_coherence_clean_graph():
    nodes = load_sample_graph()
    rho, details = compute_coherence(nodes)
    assert rho > 0.8, f"Expected rho > 0.8 for clean graph, got {rho}"
    assert details['contradictions_found'] == 0


def test_coherence_decreases_with_contradiction():
    nodes = load_sample_graph()
    rho_before, _ = compute_coherence(nodes)
    nodes.append({
        "id": "node_conflict",
        "text": "Be verbose and detailed. Always give step-by-step reasoning and be concise.",
        "class": "C",
        "source_file": "SOUL.md",
        "line": 20
    })
    rho_after, details = compute_coherence(nodes)
    assert rho_after < rho_before, "Contradiction should reduce rho"
    assert details['contradictions_found'] > 0


def test_coherence_decreases_with_duplicate():
    nodes = load_sample_graph()
    rho_before, _ = compute_coherence(nodes)
    nodes.append(dict(nodes[1], id="node_dup"))  # exact duplicate
    rho_after, details = compute_coherence(nodes)
    assert rho_after <= rho_before
    assert details['duplicates_found'] > 0


def test_coherence_bounded():
    rho, _ = compute_coherence([])
    assert rho == 1.0

    nodes = load_sample_graph()
    rho, _ = compute_coherence(nodes)
    assert 0.0 <= rho <= 1.0
