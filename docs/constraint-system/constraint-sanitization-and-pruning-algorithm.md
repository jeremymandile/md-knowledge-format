# constraint-sanitization-and-pruning-algorithm.md

## Constraint Sanitization and Pruning Algorithm
### Stabilizing SOUL/LESSON Systems in Production Fleets

---

## 1. Purpose

This document defines an operational algorithm for actively maintaining the
stability of concurrent constraint systems (H, Lₛ, Lₚ, S, R) over time.

It addresses the inevitable degradation described in the constraint authoring
stability model: additive patching, class boundary erosion, and silent
contradiction accumulation.

The algorithm is intended to be run periodically (e.g., as a CI check,
pre-commit hook, or fleet health check). It does not require model inference;
it operates purely on the static constraint files (SOUL.md, LESSON.md, policy
configs).

---

## 2. Core Problem

Over time:

- SOUL.md drifts → contradictory behavioral priors
- LESSON.md accumulates → overlapping structural/procedural rules
- Humans add local patches → S leaks into L, L leaks into S
- Edge cases multiply → constraint entropy increases monotonically

The result:

```
lim t→∞ E(t) → 0
```

where E(t) = effective coherence of the constraint system.

Without active pruning, the system becomes unstable by default.

---

## 3. Algorithm Overview

The algorithm operates in five phases:

1. **Parse & Classify** — Extract all constraints and assign them to one of the five precedence classes (A, Bₛ, Bₚ, C, D).
2. **Contradiction Detection** — Identify same-class conflicts and cross-class boundary violations.
3. **Redundancy Analysis** — Flag constraints that are fully subsumed by higher-precedence rules.
4. **Pruning & Resolution** — Remove or rewrite problematic constraints according to deterministic rules.
5. **Stability Verification** — Re-evaluate the system against formal invariants and threshold conditions.

---

## 4. Phase 1 — Parse & Classify

### Input

- SOUL.md (Class C candidates)
- LESSON.md (Class Bₛ and Bₚ candidates)
- System policy file (Class A candidates)
- Runtime configuration (Class D candidates)

### Classification Rules

| If a constraint… | Assign to Class |
|------------------|-----------------|
| Is a safety, legal, or hard-refusal policy | A |
| Defines output format, schema, structure | Bₛ |
| Defines step order, dependencies, procedures | Bₚ |
| Defines tone, stance, verbosity, personality | C |
| Defines preferences, fallbacks, defaults | D |

### Automatic Checks

- If a constraint cannot be unambiguously assigned to exactly one class → flag for manual decomposition.
- If a constraint appears to belong to multiple classes → split into atomic components before proceeding.

---

## 5. Phase 2 — Contradiction Detection

### 5.1 Same-Class Contradictions

- **Class A conflicts**: Should never occur. If detected, re-classify the softer constraint as Bₛ or Bₚ.
- **Class Bₛ conflicts**: Two structural rules that demand incompatible output formats. The one appearing earlier in the file takes precedence unless explicitly overridden.
- **Class Bₚ conflicts**: Two procedural rules with contradictory ordering. The dependency-prerequisite rule wins. If no dependency relationship exists, the earlier rule wins.
- **Class C conflicts**: Two SOUL priors in direct opposition. These cannot be resolved deterministically. Flag for author resolution.
- **Class D conflicts**: Resolved by recency, specificity, and source authority.

### 5.2 Cross-Class Boundary Violations

Detect when a constraint from a lower-precedence class attempts to control an axis that belongs to a higher-precedence class.

Axis-to-class mapping:

| Axis | Valid Classes |
|------|--------------|
| Validity (binary) | A |
| Structure (categorical) | Bₛ |
| Procedure (ordinal) | Bₚ |
| Probability (continuous) | C |
| Locality (temporal) | D |

---

## 6. Phase 3 — Redundancy Analysis

### 6.1 Subsumption Detection

A constraint c₁ is redundant if c₁ is fully implied by a higher-precedence constraint c₂ that is unambiguous and present in the system.

### 6.2 Dead Rule Detection

A constraint is dead if it has never been triggered in recent fleet operation logs and is not a Class A invariant. Dead rules are candidates for removal or archival.

### 6.3 Over-specification Score

For Class C (SOUL.md) constraints: score(C) = |C| / max_C, where max_C is the recommended maximum (~10 rules). If score(C) > 1, flag for reduction.

---

## 7. Phase 4 — Pruning & Resolution

### 7.1 Automatic Pruning (Safe)

- Remove exact duplicate constraints (same text, same class).
- Remove constraints fully subsumed by a higher-precedence constraint.
- Delete dead rules that are not Class A.
- Strip any constraint fragment that attempts to control an axis belonging to a higher-precedence class.

### 7.2 Suggested Pruning (Requires Approval)

- Resolve same-class Bₛ or Bₚ conflicts by selecting the earlier or dependency-prerequisite rule.
- Reduce over-specified SOUL.md by merging similar priors.
- Remove exception-heavy procedural rules that have become as complex as the base rule they modify.

### 7.3 Manual Resolution Required

- Class C conflicts (contradictory SOUL priors).
- Class A conflicts (immediate human review mandatory).

---

## 8. Phase 5 — Stability Verification

After pruning, verify against formal invariants:

1. No Class A violation
2. Class Bₛ substance preserved
3. Class Bₚ substance preserved
4. Class C bounded
5. Class D bounded
6. No cross-class cycling
7. Dimensional separation
8. Attention bandwidth thresholds: |A| ≤ 7, |Bₛ| ≤ 15, |Bₚ| ≤ 15, |C| ≤ 10

If any invariant fails, block deployment and request manual resolution.

---

## 9. Integration with Production Fleet

### 9.1 Pre-Commit / CI Hook

Run as a required check before any SOUL.md or LESSON.md change is merged. A failing check prevents the PR from landing.

### 9.2 Periodic Fleet Health Check

Run weekly across all active agents. Report contradiction count, boundary violation count, redundancy score, and over-specification score. If the fleet-wide instability metric crosses threshold τ, trigger a mandatory pruning cycle.

### 9.3 Post-Incident Reconciliation

After any fleet-level incident, run the algorithm on the affected agent set. Apply automatic pruning and flag the root cause for human review.

---

## 10. Formal Stability Guarantee

If the algorithm is applied with frequency f and pruning is completed on every cycle, then:

```
lim t→∞ E(t) ≥ ε > 0
```

where ε is a tunable minimum coherence threshold.

Without periodic pruning, E(t) → 0. With pruning, the system remains within stable operating bounds.

---

## 11. Summary

The constraint sanitization and pruning algorithm provides the missing operational layer for SOUL/LESSON systems: detect contradictions, boundary violations, and redundancy; prune safely where deterministic rules allow; flag subjective conflicts for human resolution; verify that the pruned system satisfies all formal invariants.

It converts the theoretical models into a repeatable, automated stabilization process for production agent fleets.
