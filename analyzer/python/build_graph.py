"""Build a typed constraint graph from parsed constraints."""
from typing import List, Tuple
from analyzer.python.classify_nodes import classify_constraint, ConstraintClass


def build_graph(constraints: List[dict], source_file: str = "") -> Tuple[List[dict], List[str]]:
    """
    Convert raw constraints into a list of typed nodes.
    Returns (nodes, warnings).
    """
    nodes = []
    warnings = []

    for i, c in enumerate(constraints):
        cls = classify_constraint(c, source_file)
        if cls is None:
            warnings.append(f"Line {c.get('line', '?')}: could not classify constraint; assigned Class D")
            cls = ConstraintClass.D

        node = {
            'id': f"node_{i}_{source_file.replace('/', '_').replace('\\', '_')}",
            'text': c['text'],
            'class': cls.name,
            'class_value': cls.value,
            'source_file': source_file,
            'line': c.get('line', 0)
        }
        nodes.append(node)

    return nodes, warnings
