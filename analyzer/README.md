# Constraint Coherence Analyzer

Static analysis linter for SOUL/LESSON constraint systems.

## What it does

- Parses Markdown constraint files into a typed graph
- Classifies every node into precedence class A, Bₛ, Bₚ, C, or D
- Detects contradictions, redundancy, and axis leakage
- Computes the coherence metric **ρ_t** ∈ [0, 1]
- Exits non-zero if ρ_t < threshold (default 0.85)

## Usage

```bash
# From repo root
python -m analyzer.python.main \
  --soul docs/constraint-system/lesson-soul-md.md \
  --lessons docs/constraint-system/LESSONS.md \
  --threshold 0.85

# JSON output for CI consumption
python -m analyzer.python.main \
  --soul docs/constraint-system/lesson-soul-md.md \
  --lessons docs/constraint-system/LESSONS.md \
  --json > coherence_report.json
```

## Exit codes

- `0` — ρ_t ≥ threshold (pass)
- `1` — ρ_t < threshold (fail) or file not found

## Dependencies

Python 3.10+ stdlib only. No external packages required.

## Running tests

```bash
pip install pytest
pytest analyzer/tests/ -v
```

## Threshold calibration

| ρ_t range | Status |
|-----------|--------|
| ≥ 0.85 | Deploy |
| 0.70–0.84 | Warning — pruning recommended |
| < 0.70 | Critical — deploy blocked |
