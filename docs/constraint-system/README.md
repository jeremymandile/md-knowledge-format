# Constraint System Specification

A formal model for concurrent instruction fields in stochastic policy-conditioned agent systems.

## What This Is

This directory contains the complete specification for understanding, modeling, and stabilizing the interaction between:

- **SOUL.md** — behavioral priors (tone, stance, verbosity)
- **LESSON.md** — structural and procedural constraints
- **System Policy** — hard inviolable constraints
- **Runtime Context** — local, ephemeral conditioning

These constraint sources do not execute in sequence. They act **concurrently** on a shared decoding process. This specification defines how they interact, how they conflict, how they degrade, and how to keep them stable.

## Document Map

| Document | Purpose |
|----------|---------|
| `LESSONS.md` | Entry point: index of all modules |
| `lesson-soul-md.md` | What SOUL.md is mechanically—a concurrent probabilistic prior, not a style guide |
| `constraint-precedence-algebra.md` | Formal precedence rules: H > Lₛ > Lₚ > S > R, with substance/expression boundary |
| `constraint-operational-semantics.md` | How constraints survive attention window partitioning during decoding |
| `failure-mode-taxonomy-multi-agent-interference.md` | Fleet-level failure classes when SOUL diverges under shared LESSON |
| `constraint-authoring-stability.md` | Why human-authored constraints accumulate contradictions over time |
| `constraint-sanitization-and-pruning-algorithm.md` | Operational algorithm for detecting and removing constraint rot |
| `constraint-coherence-optimization-theory.md` | The coherence metric ρ_t as objective function for system stability |

## Reading Order

Start with `LESSONS.md` for the index, then `lesson-soul-md.md` for the core insight, then `constraint-precedence-algebra.md` for the formal rules. The remaining documents build outward from that foundation.

## Scope Boundary

This is a **specification layer only**. It defines:

- Constraint decomposition and classification
- Conflict resolution rules
- Failure mode taxonomy
- Stability conditions and pruning algorithms

It does **not** include:

- Runtime implementations (Rust, Python, CI)
- Distributed consensus protocols
- Hardware execution models
- Formal proof systems

Those are separate concerns, built on top of this specification, not part of it.

## Status

All eight documents are complete and internally consistent. The Lₛ/Lₚ split resolves the only structural ambiguity present in earlier drafts. No pipeline language remains. All documents use the concurrent constraint field model.
