"""Compute the coherence metric ρ_t for a set of constraint nodes."""
from typing import List, Tuple
from analyzer.python.detect_cycles import detect_cycles

CONTRADICTION_WEIGHTS = {'A': 1.0, 'Bs': 1.0, 'Bp': 0.8, 'C': 0.5, 'D': 0.2}
REDUNDANCY_WEIGHTS    = {'A': 0.0, 'Bs': 0.6, 'Bp': 0.6, 'C': 0.4, 'D': 0.1}
LEAKAGE_WEIGHTS       = {'A': 0.0, 'Bs': 0.9, 'Bp': 0.9, 'C': 0.7, 'D': 0.0}

CONTRADICTION_KEYWORDS = {
    'C':  [('concise', 'detailed'), ('blunt', 'soft'), ('hedg', 'certain')],
    'Bp': [('before', 'after'), ('validate', 'skip')],
    'Bs': [('json', 'yaml'), ('bullet', 'paragraph')],
}

STRUCTURAL_LEAKAGE_WORDS = ['json', 'output format', 'schema', 'structure', 'yaml']
TONE_LEAKAGE_WORDS       = ['tone', 'be polite', 'be assertive', 'style']
HARD_LEAKAGE_WORDS       = ['safety', 'non-overridable', 'hard constraint']


def compute_coherence(nodes: List[dict]) -> Tuple[float, dict]:
    """
    Compute ρ_t = 1 - normalized(L_c + L_r + L_l)
    Returns (rho, details_dict)
    """
    total = len(nodes)
    if total == 0:
        return 1.0, {'rho': 1.0, 'contradiction_loss': 0, 'redundancy_loss': 0, 'leakage_loss': 0}

    contradiction_count = 0.0
    for node in nodes:
        cls = node['class']
        text = node['text'].lower()
        for pair in CONTRADICTION_KEYWORDS.get(cls, []):
            if pair[0] in text and pair[1] in text:
                contradiction_count += CONTRADICTION_WEIGHTS.get(cls, 0.5)
        if cls == 'C' and any(w in text for w in STRUCTURAL_LEAKAGE_WORDS):
            contradiction_count += LEAKAGE_WEIGHTS['C']
        if cls == 'Bp' and any(w in text for w in TONE_LEAKAGE_WORDS):
            contradiction_count += LEAKAGE_WEIGHTS['Bp']

    normalized_Lc = contradiction_count / max(total * 1.0, 1)

    text_set: set = set()
    duplicate_count = 0.0
    for node in nodes:
        norm_text = ' '.join(node['text'].lower().split())
        if norm_text in text_set:
            duplicate_count += REDUNDANCY_WEIGHTS.get(node['class'], 0.4)
        else:
            text_set.add(norm_text)
    normalized_Lr = duplicate_count / max(total * 0.6, 1)

    leakage_count = 0.0
    for node in nodes:
        cls = node['class']
        text = node['text'].lower()
        if cls != 'A' and any(w in text for w in HARD_LEAKAGE_WORDS):
            leakage_count += LEAKAGE_WEIGHTS.get(cls, 0.0)
        if cls not in ('Bs', 'Bp') and any(w in text for w in ['structure', 'format']):
            leakage_count += LEAKAGE_WEIGHTS.get(cls, 0.0)
    normalized_Ll = leakage_count / max(total * 0.7, 1)

    cycle_penalty = 0.1 * len(detect_cycles(nodes))

    rho = max(0.0, min(1.0, 1.0 - (normalized_Lc + normalized_Lr + normalized_Ll + cycle_penalty)))

    details = {
        'rho': rho,
        'contradiction_loss': normalized_Lc,
        'redundancy_loss': normalized_Lr,
        'leakage_loss': normalized_Ll,
        'cycle_penalty': cycle_penalty,
        'total_nodes': total,
        'contradictions_found': contradiction_count,
        'duplicates_found': duplicate_count,
        'leakage_count': leakage_count,
    }
    return rho, details
