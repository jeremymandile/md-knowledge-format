#!/usr/bin/env python3
"""
Constraint coherence analyzer — CLI entry point.

Usage:
  python -m analyzer.python.main \\
    --soul docs/constraint-system/lesson-soul-md.md \\
    --lessons docs/constraint-system/LESSONS.md \\
    --threshold 0.85
"""
import argparse
import json
import sys
from pathlib import Path

from analyzer.python.parse_constraints import parse_markdown_constraints
from analyzer.python.build_graph import build_graph
from analyzer.python.compute_rho import compute_coherence


def main() -> None:
    parser = argparse.ArgumentParser(description='Constraint Coherence Analyzer')
    parser.add_argument('--soul',      required=True, help='Path to SOUL.md / lesson-soul-md.md')
    parser.add_argument('--lessons',   required=True, help='Path to LESSONS.md')
    parser.add_argument('--policy',                   help='Path to system policy file (optional)')
    parser.add_argument('--threshold', type=float, default=0.85)
    parser.add_argument('--json',      action='store_true', help='Emit JSON report to stdout')
    args = parser.parse_args()

    all_constraints = []
    for path_str in filter(None, [args.soul, args.lessons, args.policy]):
        p = Path(path_str)
        if p.exists():
            all_constraints.extend(parse_markdown_constraints(p))

    nodes, warnings = build_graph(all_constraints, source_file=args.soul)
    rho, details = compute_coherence(nodes)

    report = {
        'rho': rho,
        'threshold': args.threshold,
        'pass': rho >= args.threshold,
        'nodes_count': len(nodes),
        'warnings': warnings,
        'details': details,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        status = "PASS" if report['pass'] else "FAIL"
        print(f"{status} rho_t={rho:.3f} (threshold {args.threshold})")
        for w in warnings:
            print(f"  WARNING: {w}")
        print(f"  contradictions={details['contradictions_found']:.2f}"
              f"  duplicates={details['duplicates_found']:.2f}"
              f"  leakage={details['leakage_count']:.2f}")

    sys.exit(0 if report['pass'] else 1)


if __name__ == '__main__':
    main()
